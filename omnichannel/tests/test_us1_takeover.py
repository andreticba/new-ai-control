# test_us1_takeover.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:36:00(GMT-04:00)
import json
import uuid
import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Organization, OrganizationMembership, Role
from omnichannel.models import Contact, ContactPhoneNumber, Conversation, Message
from core.tasks.whatsapp_tasks import AIIngestionDelegator

User = get_user_model()


def _get_or_create_org_role():
    role = Role.objects.filter(scope=Role.Scope.ORGANIZATION).first()
    if not role:
        role = Role.objects.create(
            name="Org Agent",
            slug="org_agent_us1",
            scope=Role.Scope.ORGANIZATION
        )
    return role


@pytest.fixture
def auth_setup():
    user = User.objects.create_user(username="operador_us1", password="password123")
    org = Organization.objects.create(name="Clínica Triagem", slug="clinica-triagem")
    role = _get_or_create_org_role()
    OrganizationMembership.objects.create(user=user, organization=org, role=role, is_active=True)

    client = APIClient()
    client.force_authenticate(user=user)

    contact = Contact.objects.create(
        full_name="Maria Antônia Souza",
        whatsapp_push_name="Maria WhatsApp",
        avatar_url="https://pps.whatsapp.net/v/avatar.jpg",
        status=Contact.Status.CLIENT
    )
    cpn = ContactPhoneNumber.objects.create(
        contact=contact,
        whatsapp_jid="5565999887766@s.whatsapp.net",
        phone_number="+5565999887766"
    )

    conv = Conversation.objects.create(
        contact=contact,
        organization_id=org.id,
        status=Conversation.Status.ACTIVE_AI,
        unread_count=2,
        last_message_preview="Gostaria de marcar uma consulta médica",
        is_pinned=True,
    )

    now = timezone.now()
    msg1 = Message.objects.create(
        conversation=conv,
        sender_whatsapp="5565999887766@s.whatsapp.net",
        direction=Message.Direction.INBOUND,
        content="Gostaria de marcar uma consulta médica",
        external_id="EVL-US1-001",
        timestamp=now
    )

    return {
        "user": user,
        "org": org,
        "client": client,
        "contact": contact,
        "cpn": cpn,
        "conversation": conv,
        "message": msg1,
    }


@pytest.mark.django_db
class TestUS1TakeoverAndTriage:

    def test_list_conversations_strict_pii_shield(self, auth_setup):
        """
        FR-003 / FR-007: Validar que a lista de conversas retorna display_name e avatar_url,
        mas PROÍBE rigorosamente a exposição de telefones em tela.
        """
        client = auth_setup["client"]
        res = client.get("/api/v1/omnichannel/conversations/")
        assert res.status_code == 200

        data = res.json()
        results = data if isinstance(data, list) else data.get("results", [])
        assert len(results) >= 1

        conv_data = results[0]
        contact_data = conv_data["contact"]

        # Identidade visual conforme
        assert contact_data["display_name"] == "Maria Antônia Souza"
        assert contact_data["avatar_url"] == "https://pps.whatsapp.net/v/avatar.jpg"
        assert conv_data["unread_count"] == 2
        assert conv_data["is_pinned"] is True

        # Validação estrita de Não-Exibição de PII: Telefone NÃO pode existir no payload
        json_dump = json.dumps(conv_data)
        assert "5565999887766" not in json_dump
        assert "phone_number" not in contact_data
        assert "whatsapp_jid" not in contact_data

    def test_conversation_filters_and_search(self, auth_setup):
        client = auth_setup["client"]
        conv = auth_setup["conversation"]
        user = auth_setup["user"]

        # Filtro por unread
        res_unread = client.get("/api/v1/omnichannel/conversations/?filter=unread")
        assert res_unread.status_code == 200
        unread_results = res_unread.json() if isinstance(res_unread.json(), list) else res_unread.json().get("results", [])
        assert len(unread_results) == 1

        # Filtro por mine (atualmente conv.assigned_user_id é None)
        res_mine = client.get("/api/v1/omnichannel/conversations/?filter=mine")
        assert res_mine.status_code == 200
        mine_results = res_mine.json() if isinstance(res_mine.json(), list) else res_mine.json().get("results", [])
        assert len(mine_results) == 0

        # Filtro por busca
        res_search = client.get("/api/v1/omnichannel/conversations/?search=Maria")
        assert res_search.status_code == 200
        search_results = res_search.json() if isinstance(res_search.json(), list) else res_search.json().get("results", [])
        assert len(search_results) == 1

    def test_takeover_human_transition(self, auth_setup):
        """
        FR-004: Operador assume o atendimento (takeover), alterando para ACTIVE_HUMAN
        e atribuindo assigned_user_id ao operador logado.
        """
        client = auth_setup["client"]
        conv = auth_setup["conversation"]
        user = auth_setup["user"]

        assert conv.status == Conversation.Status.ACTIVE_AI
        assert conv.assigned_user_id is None

        res = client.post(f"/api/v1/omnichannel/conversations/{conv.id}/takeover/")
        assert res.status_code == 200

        conv.refresh_from_db()
        assert conv.status == Conversation.Status.ACTIVE_HUMAN
        assert conv.assigned_user_id == uuid.UUID(int=user.id)

    def test_ai_suppression_under_human_takeover(self, auth_setup):
        """
        FR-004 / T015: Ingestão e geração de respostas da IA devem ser suprimidas
        quando a conversa estiver sob Takeover Humano (ACTIVE_HUMAN).
        """
        conv = auth_setup["conversation"]
        conv.status = Conversation.Status.ACTIVE_HUMAN
        conv.assigned_user_id = uuid.UUID(int=auth_setup["user"].id)
        conv.save()

        inbound_payload = {
            "event": "messages.upsert",
            "data": {
                "key": {
                    "remoteJid": "5565999887766@s.whatsapp.net",
                    "fromMe": False,
                    "id": "MSG_UNDER_TAKEOVER"
                },
                "pushName": "Maria WhatsApp",
                "message": {
                    "conversation": "Alguém pode me ajudar?"
                },
                "messageTimestamp": 1729459200
            }
        }

        # Executa a task Celery - deve ser suprimida silenciosamente sem erros
        AIIngestionDelegator(inbound_payload)
        conv.refresh_from_db()
        assert conv.status == Conversation.Status.ACTIVE_HUMAN

    def test_return_to_ai_transition(self, auth_setup):
        """
        FR-005: Operador devolve a conversa para a IA (return-to-ai),
        restaurando ACTIVE_AI e limpando assigned_user_id.
        """
        client = auth_setup["client"]
        conv = auth_setup["conversation"]
        conv.status = Conversation.Status.ACTIVE_HUMAN
        conv.assigned_user_id = uuid.UUID(int=auth_setup["user"].id)
        conv.save()

        res = client.post(f"/api/v1/omnichannel/conversations/{conv.id}/return-to-ai/")
        assert res.status_code == 200

        conv.refresh_from_db()
        assert conv.status == Conversation.Status.ACTIVE_AI
        assert conv.assigned_user_id is None

    def test_conversation_messages_timeline(self, auth_setup):
        client = auth_setup["client"]
        conv = auth_setup["conversation"]
        msg1 = auth_setup["message"]

        # Cria segunda mensagem com quoted_message
        msg2 = Message.objects.create(
            conversation=conv,
            sender_whatsapp="ai_control_instance",
            direction=Message.Direction.OUTBOUND,
            content="Olá Maria! Temos vaga para amanhã às 14h.",
            quoted_message=msg1,
            timestamp=timezone.now()
        )

        res = client.get(f"/api/v1/omnichannel/conversations/{conv.id}/messages/")
        assert res.status_code == 200

        data = res.json()
        messages_list = data if isinstance(data, list) else data.get("results", [])
        assert len(messages_list) == 2

        # Valida que quoted_message é serializado adequadamente
        outbound_data = [m for m in messages_list if m["direction"] == "OUTBOUND"][0]
        assert outbound_data["quoted_message"] is not None
        assert outbound_data["quoted_message"]["id"] == str(msg1.id)
        assert outbound_data["quoted_message"]["content"] == msg1.content
