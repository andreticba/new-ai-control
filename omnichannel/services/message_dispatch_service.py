# omnichannel/services/message_dispatch_service.py | AI-Control Omnichannel v0.6.0 | 22-10-2026
import logging
import uuid
from typing import Optional
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
from core.models import Organization
from core.services.evolution_gateway import EvolutionGatewayService
from omnichannel.models import Conversation, Message
from omnichannel.api.serializers.read import MessageReadSerializer

logger = logging.getLogger(__name__)


class EvolutionAPIException(Exception):
    """
    Exceção de infraestrutura levantada quando o despacho outbound para a Evolution API v2
    falha, sofre timeout (> 5.0s) ou retorna status sem confirmação inequívoca (key.id).
    Garante o princípio de Falha Atômica (D2 / SC-003).
    """
    pass


# Alias semântico para compatibilidade canônica
MessageDispatchError = EvolutionAPIException


class MessageDispatchService:
    """
    Serviço de domínio responsável pelo despacho de mensagens manuais pelo operador humano
    e aprovações do Copiloto, integrando a Evolution API, persistência segura e eventos WebSocket.
    """

    @classmethod
    def send_operator_message(
        cls,
        conversation: Conversation,
        sender_user,
        content: str,
        quoted_message_id: Optional[uuid.UUID] = None,
        media_type: str = Message.MediaType.TEXT,
        media_url: Optional[str] = None,
        sent_by_ai: bool = False,
    ) -> Message:
        """
        1. Resolve WhatsApp JID do contato e mensagem citada (Reply To).
        2. Dispara a mensagem outbound para a Evolution API de forma estritamente síncrona.
        3. Valida confirmação inequívoca contendo key.id (falha atômica).
        4. Persiste a entidade Message no banco de dados como SENT.
        5. Atualiza os campos desnormalizados da Conversation para consulta O(1).
        6. Notifica o WebSocket dos operadores.
        """
        contact = conversation.contact
        phone = contact.phone_numbers.first()
        whatsapp_jid = phone.whatsapp_jid if phone else None

        if not whatsapp_jid:
            raise ValueError("Contato não possui número de WhatsApp válido cadastrado.")

        quoted_msg = None
        quoted_payload = None
        if quoted_message_id:
            quoted_msg = Message.objects.filter(id=quoted_message_id, conversation=conversation).first()
            if quoted_msg and quoted_msg.external_id:
                quoted_payload = {
                    "key": {
                        "id": quoted_msg.external_id,
                        "remoteJid": whatsapp_jid,
                        "fromMe": quoted_msg.direction == Message.Direction.OUTBOUND,
                    },
                    "message": {
                        "conversation": quoted_msg.content or "Mensagem"
                    }
                }

        # D2 / FR-003: Envio síncrono para a Evolution API v2 com verificação estrita
        org = Organization.objects.filter(id=conversation.organization_id).first()
        org_slug = org.slug if org and org.slug else "default"
        gw = EvolutionGatewayService()
        instance_name = conversation.instance_name or gw._instance_name(org_slug)

        send_fn = getattr(gw, 'send_text_message', None) or getattr(gw, 'send_text', None)
        if not send_fn:
            raise EvolutionAPIException("Driver de envio da Evolution API não está disponível.")

        try:
            evo_res = send_fn(
                instance_name,
                whatsapp_jid,
                content,
                quoted=quoted_payload,
            )
        except Exception as e:
            logger.error(f"[MessageDispatchService] Exceção de rede ao despachar para Evolution API: {e}")
            raise EvolutionAPIException(f"Falha de comunicação ou timeout ao despachar mensagem para a Evolution API: {e}") from e

        if not isinstance(evo_res, dict):
            raise EvolutionAPIException(f"Resposta inválida da Evolution API: {evo_res}")

        if "error" in evo_res:
            err_msg = evo_res.get("error")
            logger.error(f"[MessageDispatchService] Erro retornado pela Evolution API: {err_msg}")
            raise EvolutionAPIException(f"Falha na entrega da mensagem pela Evolution API: {err_msg}")

        external_id = evo_res.get("key", {}).get("id") or evo_res.get("messageId")
        if not external_id:
            logger.error(f"[MessageDispatchService] Resposta da Evolution API sem key.id: {evo_res}")
            raise EvolutionAPIException("Evolution API não confirmou a mensagem com identificador inequívoco (key.id ausente).")

        now = timezone.now()
        with transaction.atomic():
            msg = Message.objects.create(
                conversation=conversation,
                external_id=external_id,
                direction=Message.Direction.OUTBOUND,
                content=content,
                sent_by_ai=sent_by_ai,
                delivery_status=Message.DeliveryStatus.SENT,
                is_read=True,
                read_at=now,
                media_type=media_type,
                media_url=media_url,
                sender_user_id=sender_user.id if sender_user else None,
                quoted_message=quoted_msg,
                timestamp=now,
            )

            # Atualização dos campos desnormalizados da Conversation (Anti N+1)
            conversation.last_message_preview = content[:255]
            conversation.last_message_timestamp = now
            conversation.updated_at = now
            conversation.save(update_fields=['last_message_preview', 'last_message_timestamp', 'updated_at'])

        cls._broadcast_new_message(conversation, msg)
        return msg

    @classmethod
    def _broadcast_new_message(cls, conversation: Conversation, message: Message):
        """
        Emite notificação WebSocket da nova mensagem para a timeline dos operadores.
        """
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"private-org-{conversation.organization_id}",
                {
                    "type": "conversation_message_new",
                    "data": {
                        "conversation_id": str(conversation.id),
                        "message": MessageReadSerializer(message).data,
                    }
                }
            )
