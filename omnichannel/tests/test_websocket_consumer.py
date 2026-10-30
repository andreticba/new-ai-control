# test_websocket_consumer.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:31:00(GMT-04:00)
import json
import uuid
import pytest
from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from core.models import Organization, OrganizationMembership, Role
from omnichannel.consumers.omnichannel_consumer import OmnichannelConsumer

User = get_user_model()


def _get_or_create_org_role():
    role = Role.objects.filter(scope=Role.Scope.ORGANIZATION).first()
    if not role:
        role = Role.objects.create(
            name="Org Agent",
            slug="org_agent_test",
            scope=Role.Scope.ORGANIZATION
        )
    return role


@pytest.mark.django_db(transaction=True)
class TestOmnichannelWebSocketConsumer:

    def test_unauthenticated_connection_rejected(self):
        async def _run():
            communicator = WebsocketCommunicator(
                OmnichannelConsumer.as_asgi(),
                "/ws/omnichannel/"
            )
            connected, close_code = await communicator.connect()
            assert connected is False
            assert close_code == 4401
            await communicator.disconnect()

        async_to_sync(_run)()

    def test_authenticated_connection_and_ping_pong(self):
        # Cria usuário e organização
        user = User.objects.create(username="atendente_ws_1", is_active=True)
        org = Organization.objects.create(name="Clínica Central", slug="clinica-central")
        role = _get_or_create_org_role()
        OrganizationMembership.objects.create(user=user, organization=org, role=role)

        token = str(AccessToken.for_user(user))
        path = f"/ws/omnichannel/?token={token}&org_id={org.id}"

        async def _run():
            communicator = WebsocketCommunicator(
                OmnichannelConsumer.as_asgi(),
                path
            )
            connected, _ = await communicator.connect()
            assert connected is True

            # Teste de Ping / Pong
            await communicator.send_json_to({"action": "ping"})
            response = await communicator.receive_json_from()
            assert response == {"event": "pong"}

            await communicator.disconnect()

        async_to_sync(_run)()

    def test_unauthorized_organization_rejected(self):
        user = User.objects.create(username="atendente_ws_unauth", is_active=True)
        other_org = Organization.objects.create(name="Outra Clínica", slug="outra-clinica")
        # Sem membership associado

        token = str(AccessToken.for_user(user))
        path = f"/ws/omnichannel/?token={token}&org_id={other_org.id}"

        async def _run():
            communicator = WebsocketCommunicator(
                OmnichannelConsumer.as_asgi(),
                path
            )
            connected, close_code = await communicator.connect()
            assert connected is False
            assert close_code == 4403
            await communicator.disconnect()

        async_to_sync(_run)()

    def test_channel_layer_broadcast_events(self):
        user = User.objects.create(username="atendente_ws_broadcast", is_active=True)
        org = Organization.objects.create(name="Clínica Broadcast", slug="clinica-broadcast")
        role = _get_or_create_org_role()
        OrganizationMembership.objects.create(user=user, organization=org, role=role)

        token = str(AccessToken.for_user(user))
        path = f"/ws/omnichannel/?token={token}&org_id={org.id}"

        async def _run():
            communicator = WebsocketCommunicator(
                OmnichannelConsumer.as_asgi(),
                path
            )
            connected, _ = await communicator.connect()
            assert connected is True

            channel_layer = get_channel_layer()
            group_name = f"private-org-{org.id}"

            # 1. Evento: conversation.message.new
            await channel_layer.group_send(
                group_name,
                {
                    "type": "conversation_message_new",
                    "data": {
                        "conversation_id": str(uuid.uuid4()),
                        "message": {"id": "msg_001", "content": "Olá via WebSocket"},
                    }
                }
            )
            msg_event = await communicator.receive_json_from()
            assert msg_event["event"] == "conversation.message.new"
            assert msg_event["data"]["message"]["content"] == "Olá via WebSocket"

            # 2. Evento: copilot.draft.generated
            await channel_layer.group_send(
                group_name,
                {
                    "type": "copilot_draft_generated",
                    "data": {
                        "draft_id": "draft_001",
                        "suggested_content": "Sugestão gerada pela IA local",
                    }
                }
            )
            copilot_event = await communicator.receive_json_from()
            assert copilot_event["event"] == "copilot.draft.generated"
            assert copilot_event["data"]["suggested_content"] == "Sugestão gerada pela IA local"

            # 3. Evento: conversation.status.updated
            await channel_layer.group_send(
                group_name,
                {
                    "type": "conversation_status_updated",
                    "data": {
                        "conversation_id": "conv_123",
                        "new_status": "ACTIVE_HUMAN",
                    }
                }
            )
            status_event = await communicator.receive_json_from()
            assert status_event["event"] == "conversation.status.updated"
            assert status_event["data"]["new_status"] == "ACTIVE_HUMAN"

            await communicator.disconnect()

        async_to_sync(_run)()
