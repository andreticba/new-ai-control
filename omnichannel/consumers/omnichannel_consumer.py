# omnichannel_consumer.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:26:00(GMT-04:00)
import json
import logging
import uuid
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def _get_user_from_jwt(token_str):
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(token_str)
        user_id = token.get("user_id")
        if user_id:
            return User.objects.filter(id=user_id, is_active=True).first()
    except Exception as e:
        logger.warning(f"[OmnichannelConsumer] Falha na validação de token JWT: {e}")
    return None


@database_sync_to_async
def _verify_user_organization_access(user, org_id_str):
    """
    Verifica se o usuário pertence à organização solicitada.
    Se org_id_str for None, tenta recuperar a organização primária do usuário.
    """
    try:
        from core.models import Organization, OrganizationMembership
        if org_id_str:
            try:
                org_uuid = uuid.UUID(str(org_id_str))
            except (ValueError, TypeError):
                # Tenta por slug se não for UUID
                org = Organization.objects.filter(slug=str(org_id_str)).first()
                if org:
                    org_uuid = org.id
                else:
                    return None
            
            # Superusers e staff têm acesso global ou verifica membership
            if user.is_superuser or user.is_staff:
                org = Organization.objects.filter(id=org_uuid).first()
                return str(org.id) if org else None

            has_membership = OrganizationMembership.objects.filter(
                user=user,
                organization_id=org_uuid
            ).exists()
            if has_membership:
                return str(org_uuid)
            return None

        # Fallback para a organização primária do perfil
        if hasattr(user, 'profile') and user.profile and user.profile.primary_organization:
            return str(user.profile.primary_organization.id)
            
        first_membership = OrganizationMembership.objects.filter(user=user).first()
        if first_membership:
            return str(first_membership.organization_id)

    except Exception as e:
        logger.error(f"[OmnichannelConsumer] Erro ao validar acesso organizacional: {e}", exc_info=True)
    return None


class OmnichannelConsumer(AsyncWebsocketConsumer):
    """
    WebSocket Consumer para a interface Omnichannel (WhatsApp Web Clone).
    Contrato: ws://localhost:8000/ws/omnichannel/?token=<JWT>&org_id=<UUID>
    Grupo de Broadcast: private-org-{organization_id}
    """

    async def connect(self):
        query_string = self.scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)

        token = query_params.get("token", [None])[0]
        requested_org = query_params.get("org_id", query_params.get("organization_id", [None]))[0]

        user = self.scope.get("user")
        if not user or user.is_anonymous:
            if token:
                user = await _get_user_from_jwt(token)
            
        if not user or user.is_anonymous:
            logger.warning("[OmnichannelConsumer] Conexão rejeitada: Usuário não autenticado.")
            await self.close(code=4401)
            return

        self.user = user
        self.organization_id = await _verify_user_organization_access(self.user, requested_org)

        if not self.organization_id:
            logger.warning(f"[OmnichannelConsumer] Conexão rejeitada: Acesso não autorizado para o usuário {self.user.id}.")
            await self.close(code=4403)
            return

        self.group_name = f"private-org-{self.organization_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"[OmnichannelConsumer] Conexão aceita: User {self.user.id} no grupo {self.group_name}")

    async def disconnect(self, close_code):
        if hasattr(self, "group_name") and self.group_name:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"[OmnichannelConsumer] Desconectado do grupo {self.group_name} (code: {close_code})")

    async def receive(self, text_data=None, bytes_data=None):
        """
        Recebe mensagens do cliente (ex: ping / keepalive / typing).
        """
        if not text_data:
            return
        try:
            data = json.loads(text_data)
            action = data.get("action")
            if action == "ping":
                await self.send(text_data=json.dumps({"event": "pong"}))
        except Exception as e:
            logger.warning(f"[OmnichannelConsumer] Erro ao processar frame de entrada: {e}")

    # ── Handlers de Eventos do Channel Layer (Broadcast) ──

    async def conversation_message_new(self, event):
        """
        Evento: conversation.message.new
        Disparado quando uma mensagem inbound ou outbound é criada.
        """
        await self.send(text_data=json.dumps({
            "event": "conversation.message.new",
            "data": event.get("data", {})
        }))

    async def conversation_message_status_updated(self, event):
        """
        Evento: conversation.message.status_updated
        Disparado na atualização de ticks de entrega/leitura (Sent ➔ Delivered ➔ Read).
        """
        await self.send(text_data=json.dumps({
            "event": "conversation.message.status_updated",
            "data": event.get("data", {})
        }))

    async def copilot_draft_generated(self, event):
        """
        Evento: copilot.draft.generated
        Disparado quando a IA local gera uma sugestão de resposta para a conversa ativa.
        """
        await self.send(text_data=json.dumps({
            "event": "copilot.draft.generated",
            "data": event.get("data", {})
        }))

    async def conversation_status_updated(self, event):
        """
        Evento: conversation.status.updated
        Disparado na mudança de status (ex: Takeover Humano, Encerramento ou Devolução para IA).
        """
        await self.send(text_data=json.dumps({
            "event": "conversation.status.updated",
            "data": event.get("data", {})
        }))

    async def forward_event(self, event):
        """
        Fallback genérico para encaminhar outros eventos do módulo.
        """
        await self.send(text_data=json.dumps({
            "event": event.get("event_type", "omnichannel.event"),
            "data": event.get("data", {})
        }))
