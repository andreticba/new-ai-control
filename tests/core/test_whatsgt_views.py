# test_whatsgt_views.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
import pytest
import json
from unittest.mock import patch
from django.contrib.auth.models import User
from core.models import Organization, Contact, Conversation, Message, AuditLog

@pytest.fixture
def org_1():
    return Organization.objects.create(name="Org 1")

@pytest.fixture
def org_2():
    return Organization.objects.create(name="Org 2")

@pytest.fixture
def non_staff_user(org_1):
    user = User.objects.create_user(username="normal", password="123")
    user.is_staff = False
    user.save()
    return user

@pytest.fixture
def staff_user_org_1(org_1):
    user = User.objects.create_user(username="staff1", password="123")
    user.is_staff = True
    user.save()
    return user

@pytest.mark.django_db
def test_qr_debug_view_requires_staff(client, non_staff_user):
    client.force_login(non_staff_user)
    response = client.get('/admin/core/debug/qr/')
    assert response.status_code in [302, 403]

@pytest.mark.django_db
def test_qr_debug_view_success(client, staff_user_org_1):
    client.force_login(staff_user_org_1)
    response = client.get('/admin/core/debug/qr/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_whatsgt_instance_qr_requires_staff(client, non_staff_user):
    client.force_login(non_staff_user)
    response = client.get('/api/v1/whats-gt/qr/')
    assert response.status_code in [302, 403]

@pytest.mark.django_db
def test_whatsgt_message_list_filters_and_masks(client, staff_user_org_1, org_1, org_2):
    from django.utils import timezone
    contact1 = Contact.objects.create()
    conv1 = Conversation.objects.create(contact=contact1, organization=org_1)
    Message.objects.create(
        conversation=conv1, 
        content="Secret1", 
        direction=Message.Direction.INBOUND, 
        sender_whatsapp="5511911111111@s.whatsapp.net",
        timestamp=timezone.now()
    )

    contact2 = Contact.objects.create()
    conv2 = Conversation.objects.create(contact=contact2, organization=org_2)
    Message.objects.create(
        conversation=conv2, 
        content="Secret2", 
        direction=Message.Direction.INBOUND, 
        sender_whatsapp="5511922222222@s.whatsapp.net",
        timestamp=timezone.now()
    )

    client.force_login(staff_user_org_1)
    
    with patch('core.views.whatsgt_views._get_user_organization', return_value=org_1):
        response = client.get('/api/v1/whats-gt/messages/')
        
    assert response.status_code == 200
    data = response.json()
    assert 'messages' in data
    
    assert len(data['messages']) == 1
    
    msg = data['messages'][0]
    assert "11111" not in msg['sender_whatsapp']

@pytest.mark.django_db
def test_whatsgt_message_send_invalid_schema(client, staff_user_org_1):
    client.force_login(staff_user_org_1)
    response = client.post('/api/v1/whats-gt/messages/send/', json.dumps({"text": "Hello"}), content_type="application/json")
    assert response.status_code == 400

@pytest.mark.django_db
@patch('core.services.evolution_gateway.EvolutionGatewayService.send_text_message')
def test_whatsgt_message_send_creates_audit_log(mock_send, client, staff_user_org_1, org_1):
    client.force_login(staff_user_org_1)
    mock_send.return_value = {"status": "success"}

    payload = {"jid": "5511999999999@s.whatsapp.net", "text": "Test Staff Message"}
    
    with patch('core.views.whatsgt_views._get_user_organization', return_value=org_1):
        response = client.post('/api/v1/whats-gt/messages/send/', json.dumps(payload), content_type="application/json")
    
    assert response.status_code == 200
    
    audit = AuditLog.objects.last()
    assert audit is not None
    assert audit.actor == staff_user_org_1
    assert audit.details["text"] == "Test Staff Message"
