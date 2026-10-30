# omnichannel/tests/test_pii_sanitization.py | AI-Control Omnichannel v0.6.0
import re
import pytest
import uuid
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Organization, OrganizationMembership, Role
from omnichannel.models import (
    Contact,
    ContactPhoneNumber,
    ContactOrganizationMembership,
    Conversation,
    Message,
)
from omnichannel.api.serializers import (
    ContactSerializer,
    ConversationListSerializer,
    MessageSerializer,
)

User = get_user_model()

# Regex adversarial para capturar padrões de números de telefone e JIDs do WhatsApp
# Desconsidera dígitos que façam parte de hashes ou UUIDs hexadecimais
PHONE_REGEX = re.compile(r'(?<![0-9a-fA-F-])(\+?\d{10,15}|[0-9]{10,}@s\.whatsapp\.net)(?![0-9a-fA-F-])')


@pytest.fixture
def pii_test_environment(db):
    org = Organization.objects.create(name="Hospital Geral", slug="hospital-geral")
    user = User.objects.create_user(
        username="operador_pii",
        email="operador_pii@hospital.org",
        password="password123",
    )
    role = Role.objects.filter(scope=Role.Scope.ORGANIZATION).first()
    if not role:
        role = Role.objects.create(name="Org Agent", slug="org_agent_pii", scope=Role.Scope.ORGANIZATION)

    OrganizationMembership.objects.create(
        user=user,
        organization=org,
        role=role,
        is_active=True,
    )

    contact = Contact.objects.create(
        full_name="Dra. Roberta Valadares",
        avatar_url="https://hospital.org/avatars/roberta.png",
        status=Contact.Status.CLIENT,
    )
    phone = ContactPhoneNumber.objects.create(
        contact=contact,
        whatsapp_jid="5511999998888@s.whatsapp.net",
        phone_number="+5511999998888",
    )
    ContactOrganizationMembership.objects.create(
        contact=contact,
        organization_id=org.id,
        notes="Paciente com prontuário restrito.",
    )

    conv = Conversation.objects.create(
        contact=contact,
        organization_id=org.id,
        status=Conversation.Status.ACTIVE_AI,
        channel_type=Conversation.ChannelType.WHATSAPP,
        instance_name=f"ai_control_{org.slug}",
    )

    msg = Message.objects.create(
        conversation=conv,
        external_id="msg_pii_001",
        direction=Message.Direction.INBOUND,
        content="Olá, meu retorno está agendado para amanhã?",
        sent_by_ai=False,
        delivery_status=Message.DeliveryStatus.READ,
        is_read=True,
        media_type=Message.MediaType.TEXT,
        timestamp=conv.created_at,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    return {
        "org": org,
        "user": user,
        "contact": contact,
        "phone": phone,
        "conv": conv,
        "msg": msg,
        "client": client,
    }


@pytest.mark.django_db
def test_contact_serializer_never_exposes_phone(pii_test_environment):
    """
    Valida que o ContactSerializer não contém chaves de telefone ou JID.
    """
    contact = pii_test_environment["contact"]
    serializer = ContactSerializer(contact)
    data = serializer.data

    assert "phone_number" not in data
    assert "whatsapp_jid" not in data
    assert "phone_numbers" not in data
    assert "phone_hash" not in data
    assert data["display_name"] == "Dra. Roberta Valadares"
    assert data["avatar_url"] == "https://hospital.org/avatars/roberta.png"


@pytest.mark.django_db
def test_conversation_list_api_response_adversarial_pii_check(pii_test_environment):
    """
    Auditoria adversarial em todo o payload da API de listagem de conversas.
    Garante que nem o telefone (+5511999998888) nem o JID vazam no JSON serializado.
    """
    client = pii_test_environment["client"]
    org = pii_test_environment["org"]

    response = client.get("/api/v1/omnichannel/conversations/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == status.HTTP_200_OK

    raw_json_str = response.content.decode("utf-8")

    # Busca estrita de padrões de telefone ou JID no JSON de resposta
    leaks = PHONE_REGEX.findall(raw_json_str)
    assert len(leaks) == 0, f"Vazamento de PII detectado no JSON da API: {leaks}"
    assert "5511999998888" not in raw_json_str
    assert "@s.whatsapp.net" not in raw_json_str


@pytest.mark.django_db
def test_message_serializer_adversarial_pii_check(pii_test_environment):
    """
    Garante que mensagens não expõem metadados de telefone.
    """
    msg = pii_test_environment["msg"]
    serializer = MessageSerializer(msg)
    raw_serialized = str(serializer.data)

    assert "5511999998888" not in raw_serialized
    assert "@s.whatsapp.net" not in raw_serialized
    assert "phone_number" not in serializer.data
