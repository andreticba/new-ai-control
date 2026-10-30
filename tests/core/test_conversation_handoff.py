# tests/core/test_conversation_handoff.py | AI-Control SDD v0.6.0
import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from core.models import Organization, AuditLog
from omnichannel.models import Contact, ContactPhoneNumber, ContactOrganizationMembership, Conversation, Message
from core.services.conversation_service import ConversationService
from core.tasks.whatsapp_tasks import AIIngestionDelegator
import json

User = get_user_model()


@pytest.fixture
def test_user():
    return User.objects.create_user(username="atendente_handoff", password="123")


@pytest.fixture
def webhook_payload():
    return {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "MSG_HANDOFF_1",
            },
            "pushName": "Teste",
            "messageTimestamp": 1695900000,
            "message": {
                "conversation": "Humano, por favor",
            },
        },
    }


@pytest.mark.django_db
@patch('core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay')
def test_handoff_stops_ai_processing(mock_webhook_task, client, test_user, webhook_payload, settings):
    settings.WHATS_GT_API_KEY = 'test-key'

    # 1. Envia a primeira mensagem via Webhook Gateway
    response = client.post(
        '/api/v1/webhook/whatsapp/',
        json.dumps(webhook_payload),
        content_type='application/json',
        HTTP_APIKEY='test-key',
    )
    assert response.status_code == 200
    assert mock_webhook_task.called
    mock_webhook_task.reset_mock()

    # 2. Cria conversa simulando a persistência no banco
    contact = Contact.objects.create(full_name="Teste")
    conversation = Conversation.objects.create(
        contact=contact,
        organization_id=test_user.id,
        status=Conversation.Status.ACTIVE_AI,
    )

    # Verifica que em ACTIVE_AI a IA processa normalmente
    assert AIIngestionDelegator.should_delegate_to_ai(conversation) is True

    # 3. Atendente assume o atendimento (Handoff humano)
    ConversationService.assume_conversation(str(conversation.id), test_user)

    conversation.refresh_from_db()
    assert conversation.status == Conversation.Status.ACTIVE_HUMAN
    assert conversation.assigned_user == test_user

    # 4. Trava de segurança: a IA deve ser estritamente bloqueada (FR-004)
    assert AIIngestionDelegator.should_delegate_to_ai(conversation) is False

    # 5. Envia segunda mensagem do usuário
    webhook_payload['data']['key']['id'] = "MSG_HANDOFF_2"
    response2 = client.post(
        '/api/v1/webhook/whatsapp/',
        json.dumps(webhook_payload),
        content_type='application/json',
        HTTP_APIKEY='test-key',
    )
    assert response2.status_code == 200
