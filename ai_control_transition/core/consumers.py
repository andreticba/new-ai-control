# consumers.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
# core/consumers.py | AI-Control SDD v0.6.0 | 01-10-2026 20:12(GMT-04:00)
#
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  WebSocket Consumer para a Interface de Debug                      ║
# ║                                                                    ║
# ║  PAPEL:                                                            ║
# ║  Mantém uma conexão persistente entre o navegador do admin e o     ║
# ║  Django. Quando uma mensagem nova chega via webhook, o webhook     ║
# ║  view faz um "broadcast" para este consumer via Redis Channel      ║
# ║  Layer, e o consumer empurra a mensagem para o navegador           ║
# ║  instantaneamente — sem polling.                                   ║
# ║                                                                    ║
# ║  FLUXO:                                                            ║
# ║  1. Admin abre /admin/core/debug/qr/ → JS abre WebSocket          ║
# ║  2. Consumer aceita e adiciona o canal ao grupo da organização     ║
# ║  3. Webhook recebe POST da Evolution API → salva no DB             ║
# ║  4. Webhook chama channel_layer.group_send(grupo_org, ...)         ║
# ║  5. Consumer recebe o evento e envia via ws para o navegador       ║
# ║  6. JS renderiza a mensagem na tela sem recarregar                 ║
# ║                                                                    ║
# ║  SEGURANÇA:                                                        ║
# ║  - Somente usuários autenticados como staff podem conectar (P02).  ║
# ║  - Grupo isolado por organização para multi-tenancy (P02).         ║
# ║  - PII é mascarada antes de enviar ao frontend (P07).              ║
# ╚══════════════════════════════════════════════════════════════════════╝

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


def _get_debug_group_name(org_id):
    """
    Gera o nome do grupo Channels isolado por organização.

    Cada organização (tenant) tem seu próprio grupo no Redis.
    Isso garante que admins de clínicas diferentes não vejam
    mensagens cruzadas (isolamento multi-tenant — P02).

    Args:
        org_id: ID ou slug da organização. Fallback para "default".

    Returns:
        Nome do grupo no formato "debug_messages_{org_id}".
    """
    return f"debug_messages_{org_id or 'default'}"


@database_sync_to_async
def _get_user_org_id(user):
    """
    Busca o ID da organização primária do usuário autenticado.

    Este método roda em thread separada (database_sync_to_async)
    porque estamos num consumer async e o ORM do Django é síncrono.

    Fallback para 'default' se o usuário não tiver perfil ou organização.
    """
    if hasattr(user, 'profile') and user.profile and user.profile.primary_organization:
        return str(user.profile.primary_organization.slug)
    return 'default'


class DebugConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket para a interface de debug do WhatsApp.

    Ciclo de vida:
      connect()      → chamado quando o JS abre new WebSocket(...)
      disconnect()   → chamado quando o JS fecha a conexão ou a aba
      receive()      → chamado quando o JS envia uma mensagem (reservado)
      new_message()  → handler do evento "new_message" enviado pelo webhook
    """

    async def connect(self):
        """
        Aceita a conexão WebSocket se o usuário for staff.
        Adiciona o canal do usuário ao grupo da sua organização.
        """
        user = self.scope.get("user")

        # ── Gate de Segurança (P02 — RBAC) ──
        # Apenas administradores (is_staff) podem abrir este WebSocket.
        # Usuários anônimos ou sem permissão recebem close() imediato.
        if not user or user.is_anonymous or not user.is_staff:
            await self.close()
            return

        # Determina a organização do usuário para isolamento multi-tenant
        org_id = await _get_user_org_id(user)
        self.group_name = _get_debug_group_name(org_id)

        # Adiciona este canal específico ao grupo de broadcast da organização.
        # Quando o webhook chamar group_send(self.group_name, {...}),
        # TODOS os canais neste grupo receberão o evento.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name  # ID único deste WebSocket específico
        )

        await self.accept()
        logger.info(
            f"[DebugConsumer] Admin '{user.username}' conectou ao WebSocket "
            f"de debug (grupo: {self.group_name})."
        )

    async def disconnect(self, close_code):
        """
        Remove o canal do grupo ao desconectar (admin fecha a aba).
        """
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Recebe mensagens do frontend via WebSocket.

        No momento, não processamos mensagens vindas do JS (o envio
        de mensagens continua via HTTP POST para manter o AuditLog).
        Reservado para uso futuro (ex: comandos de controle).
        """
        pass

    async def new_message(self, event):
        await self.send(text_data=json.dumps({'type': 'new_message', 'message': event['message']}))

    async def connection_update(self, event):
        await self.send(text_data=json.dumps({'type': 'connection_update', 'state': event['state']}))
