# omnichannel/services/takeover_service.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:58:00(GMT-04:00)
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone
from omnichannel.models import Conversation

logger = logging.getLogger(__name__)


class TakeoverService:
    """
    Serviço de domínio responsável pela alternância de controle entre Operador Humano e IA,
    com travas atômicas transacionais (select_for_update) e emissão de telemetria em tempo real.
    """

    @classmethod
    def assign_to_human(cls, conversation: Conversation, operator) -> Conversation:
        """
        Transbordo: Atribui o atendimento exclusivamente a um operador humano,
        silenciando intervenções automáticas da IA na conversa.
        """
        import uuid
        operator_uuid = uuid.UUID(int=operator.id) if isinstance(operator.id, int) else operator.id
        with transaction.atomic():
            locked_conv = Conversation.objects.select_for_update().get(id=conversation.id)
            locked_conv.status = Conversation.Status.ACTIVE_HUMAN
            locked_conv.assigned_user_id = operator_uuid
            locked_conv.updated_at = timezone.now()
            locked_conv.save(update_fields=['status', 'assigned_user_id', 'updated_at'])

        cls._broadcast_status_change(locked_conv)
        return locked_conv

    @classmethod
    def return_to_ai(cls, conversation: Conversation, actor) -> Conversation:
        """
        Devolve o atendimento à IA autônoma e limpa a atribuição do operador.
        """
        with transaction.atomic():
            locked_conv = Conversation.objects.select_for_update().get(id=conversation.id)
            locked_conv.status = Conversation.Status.ACTIVE_AI
            locked_conv.assigned_user_id = None
            locked_conv.updated_at = timezone.now()
            locked_conv.save(update_fields=['status', 'assigned_user_id', 'updated_at'])

        cls._broadcast_status_change(locked_conv)
        return locked_conv

    @classmethod
    def mark_as_read(cls, conversation: Conversation) -> int:
        """
        Marca todas as mensagens não lidas como lidas e zera a contagem unread_count.
        """
        with transaction.atomic():
            locked_conv = Conversation.objects.select_for_update().get(id=conversation.id)
            updated_count = locked_conv.messages.filter(is_read=False).update(
                is_read=True,
                read_at=timezone.now()
            )
            locked_conv.unread_count = 0
            locked_conv.save(update_fields=['unread_count', 'updated_at'])

        cls._broadcast_status_change(locked_conv)
        return updated_count

    @classmethod
    def _broadcast_status_change(cls, conversation: Conversation):
        """
        Emite notificação WebSocket para os atendentes conectados na organização.
        """
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"private-org-{conversation.organization_id}",
                {
                    "type": "conversation_status_updated",
                    "data": {
                        "conversation_id": str(conversation.id),
                        "status": conversation.status,
                        "assigned_user_id": str(conversation.assigned_user_id) if conversation.assigned_user_id else None,
                        "unread_count": conversation.unread_count,
                    }
                }
            )
