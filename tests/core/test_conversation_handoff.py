# tests/core/test_conversation_handoff.py | AI-Control SDD v0.6.0 | 29-09-2026 15:18(GMT-04:00)

import pytest
from unittest.mock import patch
from django.contrib.auth.models import User
from core.models import Organization, AuditLog, ConsentLog
from omnichannel.models import Contact, ContactPhoneNumber, ContactOrganizationMembership, Conversation, Message
from core.services.conversation_service import ConversationService
import json

@pytest.fixture
def test_user():
    return User.objects.create_user(username="atendente", password="123")

@pytest.fixture
def webhook_payload():
    return {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "MSG_HANDOFF_1"
            },
            "pushName": "Teste",
            "messageTimestamp": 1695900000,
            "message": {
                "conversation": "Humano, por favor"
            }
        }
    }

@pytest.mark.django_db
@patch('core.tasks.process_whatsapp_message_task')
def test_handoff_stops_ai_processing(mock_task, client, test_user, webhook_payload):
    # 1. Envia a primeira mensagem para criar o Contato e a Conversa (ACTIVE_AI default)
    response = client.post(
        '/api/v1/webhook/whatsapp/', 
        json.dumps(webhook_payload), 
        content_type='application/json'
    )
    assert response.status_code == 200
    
    # A IA deve ser acionada na primeira vez
    assert mock_task.delay.called
    mock_task.reset_mock()
    
    # Valida que a conversa foi criada
    contact = Contact.objects.first()
    conversation = Conversation.objects.filter(contact=contact).first()
    assert conversation.status == Conversation.Status.ACTIVE_AI
    
    # 2. Atendente assume a conversa
    ConversationService.assume_conversation(str(conversation.id), test_user)
    
    # Verifica o AuditLog
    audit = AuditLog.objects.filter(action=AuditLog.ActionType.HANDOFF_ASSUMED).first()
    assert audit is not None
    assert audit.actor == test_user
    assert audit.target_contact == contact
    
    # 3. Envia segunda mensagem do usuário (agora no modo ACTIVE_HUMAN)
    webhook_payload['data']['key']['id'] = "MSG_HANDOFF_2"
    response2 = client.post(
        '/api/v1/webhook/whatsapp/', 
        json.dumps(webhook_payload), 
        content_type='application/json'
    )
    assert response2.status_code == 200
    
    # A IA **NÃO** deve ser acionada desta vez
    assert not mock_task.delay.called
    
    # Mas a mensagem ainda deve ser salva no banco
    assert Message.objects.count() == 2
