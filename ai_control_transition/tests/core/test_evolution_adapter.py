# tests/core/test_evolution_adapter.py | AI-Control SDD v0.6.0 | 29-09-2026 15:15(GMT-04:00)

import pytest
from core.adapters.evolution import EvolutionWebhookAdapter
from core.services.contact_service import ContactService
from core.models import Organization, Contact, ContactPhoneNumber, ContactOrganizationMembership
from core.utils import generate_phone_hash

@pytest.fixture
def evolution_webhook_payload():
    return {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "BAE5A123456789"
            },
            "pushName": "John Doe",
            "messageTimestamp": 1695900000,
            "message": {
                "conversation": "Olá, preciso de ajuda!"
            }
        }
    }

def test_evolution_adapter_parse_valid_message(evolution_webhook_payload):
    dtos = EvolutionWebhookAdapter.parse_messages(evolution_webhook_payload)
    
    assert len(dtos) == 1
    dto = dtos[0]
    assert dto.message_id == "BAE5A123456789"
    assert dto.sender_jid == "5511999999999@s.whatsapp.net"
    assert dto.sender_phone == "5511999999999"
    assert dto.push_name == "John Doe"
    assert dto.content == "Olá, preciso de ajuda!"
    assert dto.from_me is False
    assert dto.is_group is False

def test_evolution_adapter_parse_ignore_non_message_event():
    payload = {"event": "connection.update", "data": {}}
    dtos = EvolutionWebhookAdapter.parse_messages(payload)
    assert len(dtos) == 0

@pytest.mark.django_db
def test_contact_service_creates_contact_and_membership():
    sender_phone = "5511888888888"
    sender_jid = f"{sender_phone}@s.whatsapp.net"
    push_name = "Maria Silva"
    
    contact, org = ContactService.get_or_create_contact_for_webhook(
        sender_phone=sender_phone,
        sender_jid=sender_jid,
        push_name=push_name,
        organization_slug="test-org"
    )
    
    # Valida Organização
    assert org.slug == "test-org"
    
    # Valida Contato
    assert contact.full_name == push_name
    
    # Valida Telefone com Hash (Blind Index)
    phone_obj = ContactPhoneNumber.objects.get(contact=contact)
    assert phone_obj.whatsapp_jid == sender_jid
    # O hash salvo deve bater com a utilidade isolada
    assert phone_obj.phone_hash == generate_phone_hash(sender_phone)
    
    # Valida Membership
    assert ContactOrganizationMembership.objects.filter(contact=contact, organization=org).exists()

@pytest.mark.django_db
def test_contact_service_finds_existing_contact_by_hash():
    # Cria primeiro acesso
    sender_phone = "5511777777777"
    sender_jid = f"{sender_phone}@s.whatsapp.net"
    push_name = "Carlos Souza"
    
    contact1, org1 = ContactService.get_or_create_contact_for_webhook(
        sender_phone=sender_phone,
        sender_jid=sender_jid,
        push_name=push_name
    )
    
    # Simula um segundo webhook chegando com o mesmo telefone, mesmo que o nome mude
    contact2, org2 = ContactService.get_or_create_contact_for_webhook(
        sender_phone=sender_phone,
        sender_jid=sender_jid,
        push_name="Carlos S."
    )
    
    # Deve ser o MESMO contato e MESMA organização
    assert contact1.id == contact2.id
    assert org1.id == org2.id
    # E não deve ter duplicado telefones
    assert ContactPhoneNumber.objects.filter(contact=contact1).count() == 1
