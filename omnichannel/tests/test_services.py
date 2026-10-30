# omnichannel/tests/test_services.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:58:00(GMT-04:00)
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Organization
from omnichannel.models import (
    Contact,
    ContactPhoneNumber,
    Conversation,
    Message,
)
from omnichannel.services.instance_service import InstanceService
from omnichannel.services.takeover_service import TakeoverService
from omnichannel.services.message_dispatch_service import MessageDispatchService

User = get_user_model()


@pytest.fixture
def service_test_setup(db):
    org = Organization.objects.create(name="Hospital Clinico", slug="hospital-clinico")
    user = User.objects.create_user(
        username="medico_atendente",
        email="medico@hospital.org",
        password="password123"
    )
    contact = Contact.objects.create(
        full_name="Paciente Carlos Silva",
        status=Contact.Status.CLIENT
    )
    phone = ContactPhoneNumber.objects.create(
        contact=contact,
        whatsapp_jid="5511988887777@s.whatsapp.net",
        phone_number="+5511988887777"
    )
    conv = Conversation.objects.create(
        contact=contact,
        organization_id=org.id,
        status=Conversation.Status.ACTIVE_AI,
        channel_type=Conversation.ChannelType.WHATSAPP,
        instance_name=f"ai_control_{org.slug}",
        unread_count=3
    )
    now = timezone.now()
    msg1 = Message.objects.create(
        conversation=conv,
        external_id="msg_srv_001",
        direction=Message.Direction.INBOUND,
        content="Preciso de ajuda urgente",
        is_read=False,
        media_type=Message.MediaType.TEXT,
        timestamp=now
    )
    msg2 = Message.objects.create(
        conversation=conv,
        external_id="msg_srv_002",
        direction=Message.Direction.INBOUND,
        content="Alguém aí?",
        is_read=False,
        media_type=Message.MediaType.TEXT,
        timestamp=now
    )
    return {
        "org": org,
        "user": user,
        "contact": contact,
        "phone": phone,
        "conv": conv,
        "messages": [msg1, msg2],
    }


@pytest.mark.django_db
class TestTakeoverService:
    def test_assign_to_human(self, service_test_setup):
        conv = service_test_setup["conv"]
        user = service_test_setup["user"]

        with patch("omnichannel.services.takeover_service.get_channel_layer") as mock_layer:
            mock_channel = MagicMock()
            mock_channel.group_send = AsyncMock()
            mock_layer.return_value = mock_channel

            updated = TakeoverService.assign_to_human(conv, user)

            import uuid
            expected_uuid = uuid.UUID(int=user.id)
            assert updated.status == Conversation.Status.ACTIVE_HUMAN
            assert updated.assigned_user_id == expected_uuid

            conv.refresh_from_db()
            assert conv.status == Conversation.Status.ACTIVE_HUMAN
            assert conv.assigned_user_id == expected_uuid

    def test_return_to_ai(self, service_test_setup):
        conv = service_test_setup["conv"]
        user = service_test_setup["user"]
        conv.status = Conversation.Status.ACTIVE_HUMAN
        conv.assigned_user_id = user.id
        conv.save()

        with patch("omnichannel.services.takeover_service.get_channel_layer") as mock_layer:
            mock_channel = MagicMock()
            mock_channel.group_send = AsyncMock()
            mock_layer.return_value = mock_channel

            updated = TakeoverService.return_to_ai(conv, user)

            assert updated.status == Conversation.Status.ACTIVE_AI
            assert updated.assigned_user_id is None

            conv.refresh_from_db()
            assert conv.status == Conversation.Status.ACTIVE_AI
            assert conv.assigned_user_id is None

    def test_mark_as_read(self, service_test_setup):
        conv = service_test_setup["conv"]

        with patch("omnichannel.services.takeover_service.get_channel_layer") as mock_layer:
            mock_channel = MagicMock()
            mock_channel.group_send = AsyncMock()
            mock_layer.return_value = mock_channel

            count = TakeoverService.mark_as_read(conv)
            assert count == 2

            conv.refresh_from_db()
            assert conv.unread_count == 0
            for msg in conv.messages.all():
                assert msg.is_read is True


@pytest.mark.django_db
class TestMessageDispatchService:
    def test_send_operator_message_success(self, service_test_setup):
        conv = service_test_setup["conv"]
        user = service_test_setup["user"]

        with patch("omnichannel.services.message_dispatch_service.EvolutionGatewayService") as mock_gateway, \
             patch("omnichannel.services.message_dispatch_service.get_channel_layer") as mock_layer:
            mock_channel = MagicMock()
            mock_channel.group_send = AsyncMock()
            mock_layer.return_value = mock_channel

            mock_inst = MagicMock()
            mock_inst._instance_name.return_value = f"ai_control_{service_test_setup['org'].slug}"
            mock_inst.send_text.return_value = {"key": {"id": "evo_outbound_123"}}
            mock_inst.send_text_message.return_value = {"key": {"id": "evo_outbound_123"}}
            mock_gateway.return_value = mock_inst

            msg = MessageDispatchService.send_operator_message(
                conversation=conv,
                sender_user=user,
                content="Olá Carlos, sou o Dr. Medico, vou atendê-lo agora."
            )

            assert msg.id is not None
            assert msg.direction == Message.Direction.OUTBOUND
            assert msg.sent_by_ai is False
            assert msg.sender_user_id == user.id
            assert msg.content == "Olá Carlos, sou o Dr. Medico, vou atendê-lo agora."

            conv.refresh_from_db()
            assert conv.last_message_preview == "Olá Carlos, sou o Dr. Medico, vou atendê-lo agora."
            assert conv.last_message_timestamp is not None


@pytest.mark.django_db
class TestInstanceService:
    def test_get_status(self, service_test_setup):
        org = service_test_setup["org"]

        with patch("omnichannel.services.instance_service.EvolutionGatewayService") as mock_gateway:
            mock_inst = MagicMock()
            mock_inst._instance_name.return_value = f"ai_control_{org.slug}"
            mock_inst.get_connection_state.return_value = {"state": "open"}
            mock_gateway.return_value = mock_inst

            status_res = InstanceService.get_status(org_id=org.id)
            assert status_res["connected"] is True
            assert status_res["state"] == "open"
            assert f"ai_control_{org.slug}" in status_res["instance_name"]

    def test_disconnect(self, service_test_setup):
        org = service_test_setup["org"]

        with patch("omnichannel.services.instance_service.EvolutionGatewayService") as mock_gateway:
            mock_inst = MagicMock()
            mock_inst._instance_name.return_value = f"ai_control_{org.slug}"
            mock_inst.logout_instance.return_value = True
            mock_gateway.return_value = mock_inst

            res = InstanceService.disconnect(org_id=org.id)
            assert res["success"] is True
