import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from core.models import Organization
from omnichannel.models import Contact, ContactPhoneNumber, Conversation, Message
from omnichannel.services.message_dispatch_service import MessageDispatchService, EvolutionAPIException

User = get_user_model()


@pytest.fixture
def org_and_user(db):
    org = Organization.objects.create(name="Org Teste", slug="org-teste", is_active=True)
    user = User.objects.create_user(username="operador_teste", password="password123")
    return org, user


@pytest.fixture
def conversation_with_contact(org_and_user):
    org, user = org_and_user
    contact = Contact.objects.create(
        status=Contact.Status.PLATFORM_LEAD,
        whatsapp_push_name="Cliente Teste"
    )
    ContactPhoneNumber.objects.create(
        contact=contact,
        whatsapp_jid="5511988887777@s.whatsapp.net"
    )
    conv = Conversation.objects.create(
        contact=contact,
        organization_id=org.id,
        status=Conversation.Status.ACTIVE_HUMAN
    )
    return conv, user


@pytest.mark.django_db
class TestMessageDispatchAtomicFailure:

    @patch("omnichannel.services.message_dispatch_service.EvolutionGatewayService.send_text_message")
    def test_send_operator_message_success_persists_and_returns(self, mock_send, conversation_with_contact):
        """Quando a Evolution API confirma com key.id, persiste a mensagem como SENT."""
        conv, user = conversation_with_contact
        mock_send.return_value = {
            "key": {
                "id": "EVOLUTION_MSG_KEY_12345",
                "remoteJid": "5511988887777@s.whatsapp.net",
                "fromMe": True
            },
            "status": "PENDING"
        }

        msg = MessageDispatchService.send_operator_message(
            conversation=conv,
            sender_user=user,
            content="Olá, tudo bem?"
        )

        assert msg.id is not None
        assert msg.external_id == "EVOLUTION_MSG_KEY_12345"
        assert msg.delivery_status == Message.DeliveryStatus.SENT
        assert msg.content == "Olá, tudo bem?"
        assert Message.objects.filter(id=msg.id).exists()
        mock_send.assert_called_once()

    @patch("omnichannel.services.message_dispatch_service.EvolutionGatewayService.send_text_message")
    def test_send_operator_message_failure_raises_exception_and_no_db_record(self, mock_send, conversation_with_contact):
        """Quando a Evolution API falha (erro retornado), levanta EvolutionAPIException e NADA é gravado no banco."""
        conv, user = conversation_with_contact
        mock_send.return_value = {"error": "Connection closed with WhatsApp server"}

        initial_count = Message.objects.count()

        with pytest.raises(EvolutionAPIException) as exc_info:
            MessageDispatchService.send_operator_message(
                conversation=conv,
                sender_user=user,
                content="Mensagem que vai falhar"
            )

        assert "Falha na entrega" in str(exc_info.value) or "Evolution API" in str(exc_info.value)
        # Nenhuma mensagem fantasma criada
        assert Message.objects.count() == initial_count

    @patch("omnichannel.services.message_dispatch_service.EvolutionGatewayService.send_text_message")
    def test_send_operator_message_timeout_raises_exception_and_no_db_record(self, mock_send, conversation_with_contact):
        """Quando a chamada da Evolution API sofre timeout de rede, não grava no banco."""
        conv, user = conversation_with_contact
        mock_send.side_effect = TimeoutError("Connection to Evolution API timed out after 5.0s")

        initial_count = Message.objects.count()

        with pytest.raises(EvolutionAPIException) as exc_info:
            MessageDispatchService.send_operator_message(
                conversation=conv,
                sender_user=user,
                content="Mensagem com timeout"
            )

        assert Message.objects.count() == initial_count

    def test_send_operator_message_without_whatsapp_jid_raises_error(self, org_and_user):
        """Se o contato não tiver telefone cadastrado, falha atômica antes de qualquer chamada."""
        org, user = org_and_user
        contact = Contact.objects.create(status=Contact.Status.PLATFORM_LEAD)
        conv = Conversation.objects.create(contact=contact, organization_id=org.id)

        initial_count = Message.objects.count()

        with pytest.raises(ValueError):
            MessageDispatchService.send_operator_message(
                conversation=conv,
                sender_user=user,
                content="Tentativa sem telefone"
            )

        assert Message.objects.count() == initial_count

    @patch("omnichannel.services.message_dispatch_service.EvolutionGatewayService.send_text_message")
    def test_message_api_view_returns_502_on_dispatch_failure(self, mock_send, client, conversation_with_contact):
        """Garante que a View DRF retorna HTTP 502 quando a Evolution API falhar."""
        from core.models import OrganizationMembership
        from rest_framework_simplejwt.tokens import RefreshToken

        conv, user = conversation_with_contact
        user.is_staff = True
        user.save()

        token = str(RefreshToken.for_user(user).access_token)
        mock_send.return_value = {"error": "Device not connected"}

        response = client.post(
            "/api/v1/omnichannel/messages/",
            data={
                "conversation_id": str(conv.id),
                "content": "Tentando enviar com WhatsApp fora do ar"
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        assert response.status_code == 502
        assert "error" in response.json()
        assert "Não foi possível enviar a mensagem no WhatsApp" in response.json()["error"]
        assert not Message.objects.filter(content="Tentando enviar com WhatsApp fora do ar").exists()

