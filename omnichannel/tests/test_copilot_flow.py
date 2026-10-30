# test_copilot_flow.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:42:00(GMT-04:00)
import json
import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Organization, OrganizationMembership, Role
from omnichannel.models import Contact, ContactPhoneNumber, Conversation, Message, CopilotDraft
from omnichannel.services.copilot_service import CopilotService
from omnichannel.tasks.copilot_tasks import generate_copilot_draft_task
from core.services.whatsapp_service import WhatsAppService

User = get_user_model()


def _get_or_create_org_role():
    role = Role.objects.filter(scope=Role.Scope.ORGANIZATION).first()
    if not role:
        role = Role.objects.create(
            name="Org Agent",
            slug="org_agent_copilot",
            scope=Role.Scope.ORGANIZATION
        )
    return role


@pytest.fixture
def copilot_setup():
    user = User.objects.create_user(username="operador_copilot", password="password123")
    org = Organization.objects.create(name="Clínica Copilot", slug="clinica-copilot")
    role = _get_or_create_org_role()
    OrganizationMembership.objects.create(user=user, organization=org, role=role, is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    contact = Contact.objects.create(
        full_name="Lucas Pereira",
        whatsapp_push_name="Lucas WhatsApp",
        status=Contact.Status.CLIENT
    )
    cpn = ContactPhoneNumber.objects.create(
        contact=contact,
        whatsapp_jid="5511988887777@s.whatsapp.net",
        phone_number="+5511988887777"
    )

    conv = Conversation.objects.create(
        contact=contact,
        organization_id=org.id,
        status=Conversation.Status.ACTIVE_HUMAN,
        assigned_user_id=uuid.UUID(int=user.id),
        unread_count=1,
    )

    now = timezone.now()
    msg = Message.objects.create(
        conversation=conv,
        sender_whatsapp="5511988887777@s.whatsapp.net",
        direction=Message.Direction.INBOUND,
        content="Qual o endereço da clínica para a consulta?",
        external_id="EVL-COPILOT-001",
        timestamp=now
    )

    return {
        "user": user,
        "org": org,
        "client": client,
        "contact": contact,
        "cpn": cpn,
        "conversation": conv,
        "message": msg,
    }


@pytest.mark.django_db
class TestCopilotFlow:

    @patch("omnichannel.services.copilot_service.requests.post")
    def test_copilot_service_generation(self, mock_post, copilot_setup):
        """
        T018: Testa o serviço CopilotService chamando o Ollama mockado
        e persistindo o CopilotDraft.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Nosso endereço é Av. Paulista, 1000 - Bela Vista."
        }
        mock_post.return_value = mock_response

        conv = copilot_setup["conversation"]
        msg = copilot_setup["message"]

        service = CopilotService()
        draft = service.generate_suggestion(conv.id, msg.id)

        assert draft is not None
        assert draft.conversation == conv
        assert draft.trigger_message == msg
        assert draft.status == CopilotDraft.Status.PENDING
        assert "Av. Paulista" in draft.suggested_content
        assert draft.latency_ms > 0
        assert mock_post.called

    @patch("omnichannel.tasks.copilot_tasks.get_channel_layer")
    @patch("omnichannel.tasks.copilot_tasks.CopilotService.generate_suggestion")
    def test_copilot_celery_task_and_websocket_broadcast(self, mock_generate, mock_get_channel_layer, copilot_setup):
        """
        T019: Testa a task Celery disparando a geração e emitindo no WebSocket.
        """
        conv = copilot_setup["conversation"]
        msg = copilot_setup["message"]

        mock_draft = CopilotDraft.objects.create(
            conversation=conv,
            trigger_message=msg,
            suggested_content="Temos horários disponíveis amanhã.",
            status=CopilotDraft.Status.PENDING,
            generated_by_model="phi4-mini:latest",
            latency_ms=120.0
        )
        mock_generate.return_value = mock_draft

        mock_channel_layer = MagicMock()
        mock_channel_layer.group_send = AsyncMock()
        mock_get_channel_layer.return_value = mock_channel_layer

        draft_id = generate_copilot_draft_task(conv.id, msg.id)

        assert draft_id == str(mock_draft.id)
        mock_generate.assert_called_once_with(conv.id, msg.id)
        mock_channel_layer.group_send.assert_called()

    @patch("omnichannel.tasks.copilot_tasks.generate_copilot_draft_task.delay")
    def test_whatsapp_service_triggers_copilot_on_active_human(self, mock_delay, copilot_setup):
        """
        T020: Mensagem inbound com conversa em ACTIVE_HUMAN aciona generate_copilot_draft_task.
        """
        conv = copilot_setup["conversation"]
        assert conv.status == Conversation.Status.ACTIVE_HUMAN

        payload = {
            "event": "messages.upsert",
            "data": {
                "key": {
                    "fromMe": False,
                    "remoteJid": "5511988887777@s.whatsapp.net",
                    "id": "MSG_HUMAN_INBOUND"
                },
                "pushName": "Lucas WhatsApp",
                "message": {
                    "conversation": "Tem estacionamento no local?"
                },
                "messageTimestamp": 1729459200
            }
        }

        service = WhatsAppService()
        service.process_message_upsert(payload, copilot_setup["org"].slug)

        mock_delay.assert_called_once()
        args, _ = mock_delay.call_args
        assert args[0] == str(conv.id)

    @patch("core.services.evolution_gateway.requests.post")
    def test_approve_copilot_draft_with_edit(self, mock_post, copilot_setup):
        """
        T021: Operador aprova sugestão do Copiloto (com edição de texto opcional).
        O draft é marcado como APPROVED e a mensagem OUTBOUND é enviada.
        """
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {"key": {"id": "EVO-OUT-001"}})

        client = copilot_setup["client"]
        conv = copilot_setup["conversation"]
        msg = copilot_setup["message"]

        draft = CopilotDraft.objects.create(
            conversation=conv,
            trigger_message=msg,
            suggested_content="O endereço é Rua Augusta, 500.",
            status=CopilotDraft.Status.PENDING,
        )

        res = client.post(
            f"/api/v1/omnichannel/copilot-drafts/{draft.id}/approve/",
            data={"edited_content": "O endereço é Rua Augusta, 500 - 3º andar."},
            format="json"
        )
        assert res.status_code == 200

        draft.refresh_from_db()
        assert draft.status == CopilotDraft.Status.APPROVED
        assert draft.final_sent_content == "O endereço é Rua Augusta, 500 - 3º andar."

        # Verifica que a mensagem OUTBOUND foi salva no banco
        outbound_msg = Message.objects.filter(
            conversation=conv,
            direction=Message.Direction.OUTBOUND,
            sent_by_ai=True
        ).first()
        assert outbound_msg is not None
        assert outbound_msg.content == "O endereço é Rua Augusta, 500 - 3º andar."
        assert outbound_msg.external_id == "EVO-OUT-001"

    def test_discard_copilot_draft(self, copilot_setup):
        """
        T021: Operador descarta a sugestão do Copiloto.
        O status muda para DISCARDED e nenhuma mensagem OUTBOUND é gerada.
        """
        client = copilot_setup["client"]
        conv = copilot_setup["conversation"]
        msg = copilot_setup["message"]

        draft = CopilotDraft.objects.create(
            conversation=conv,
            trigger_message=msg,
            suggested_content="Texto que o operador não quer enviar.",
            status=CopilotDraft.Status.PENDING,
        )

        res = client.post(f"/api/v1/omnichannel/copilot-drafts/{draft.id}/discard/")
        assert res.status_code == 200

        draft.refresh_from_db()
        assert draft.status == CopilotDraft.Status.DISCARDED

        # Garante que nenhuma mensagem nova foi disparada
        outbound_count = Message.objects.filter(
            conversation=conv,
            direction=Message.Direction.OUTBOUND
        ).count()
        assert outbound_count == 0
