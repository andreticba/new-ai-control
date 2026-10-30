import json
import time
from unittest.mock import patch, MagicMock
import pytest
from core.api.v1.views.webhook_whatsapp import SILENT_DROP_EVENTS, ACTIONABLE_EVENTS


@pytest.fixture
def webhook_url():
    return "/api/v1/webhook/whatsapp/"


@pytest.mark.django_db
class TestWebhookWhatsAppGateway:

    @patch("core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay")
    def test_silent_drop_events_return_200_without_enqueuing_celery(self, mock_delay, client, webhook_url, settings):
        """Garante que presence.update e outros eventos de descarte silencioso não vão para o Celery."""
        settings.WHATS_GT_API_KEY = "valid_api_key_123"

        # Warm-up do client de testes do Django
        client.post(
            webhook_url,
            data=json.dumps({"event": "presence.update", "data": {}}),
            content_type="application/json",
            HTTP_APIKEY="valid_api_key_123",
        )

        test_events = ["presence.update", "chats.set", "chats.update", "contacts.set", "labels.association"]
        for evt in test_events:
            mock_delay.reset_mock()
            start = time.perf_counter()
            response = client.post(
                webhook_url,
                data=json.dumps({"event": evt, "data": {"status": "recording"}}),
                content_type="application/json",
                HTTP_APIKEY="valid_api_key_123",
            )
            elapsed_ms = (time.perf_counter() - start) * 1000

            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            mock_delay.assert_not_called(), f"Evento {evt} não deveria ter enfileirado tarefa no Celery!"
            assert elapsed_ms < 50.0  # Latência mínima O(1) após warm-up

    @patch("core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay")
    def test_actionable_events_enqueue_celery_task(self, mock_delay, client, webhook_url, settings):
        """Garante que eventos acionáveis (incluindo qrcode.updated e messages.edited) vão para o Celery."""
        settings.WHATS_GT_API_KEY = "valid_api_key_123"

        actionable = [
            "messages.upsert",
            "messages.update",
            "messages.edited",
            "messages.delete",
            "qrcode.updated",
            "connection.update",
        ]
        for evt in actionable:
            mock_delay.reset_mock()
            response = client.post(
                webhook_url,
                data=json.dumps({"event": evt, "data": {"id": "test_id"}}),
                content_type="application/json",
                HTTP_APIKEY="valid_api_key_123",
            )
            assert response.status_code == 200
            mock_delay.assert_called_once()

    @patch("core.api.v1.views.webhook_whatsapp.logger.warning")
    @patch("core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay")
    def test_unsupported_event_sanitizes_log_and_drops(self, mock_delay, mock_warn, client, webhook_url, settings):
        """Garante que evento desconhecido não vaze destination, apikey ou sender nos logs."""
        settings.WHATS_GT_API_KEY = "valid_api_key_123"

        payload = {
            "event": "unsupported.random.event",
            "destination": "http://localhost:8000/api/v1/webhook/whatsapp/?apikey=super_secret_leak",
            "apikey": "instance_token_leak",
            "sender": "5511999999999@s.whatsapp.net",
            "instance": "instancia_teste",
            "data": {"some": "secret"}
        }

        response = client.post(
            webhook_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_APIKEY="valid_api_key_123",
        )
        assert response.status_code == 200
        mock_delay.assert_not_called()

        # Verifica que o log de warning foi sanitizado
        mock_warn.assert_called()
        log_message = str(mock_warn.call_args)
        assert "super_secret_leak" not in log_message
        assert "instance_token_leak" not in log_message
        assert "5511999999999" not in log_message
        assert "instancia_teste" in log_message

    @patch("core.services.whatsapp_service.get_channel_layer")
    def test_process_message_update_delivery_and_read_ticks(self, mock_get_channel_layer):
        """Valida a progressão SENT ➔ DELIVERED ➔ READ (ticks azuis) e notificação WebSocket."""
        from core.services.whatsapp_service import WhatsAppService
        from omnichannel.models import Contact, ContactPhoneNumber, Conversation, Message
        from core.models import Organization

        from unittest.mock import AsyncMock
        mock_layer = MagicMock()
        mock_layer.group_send = AsyncMock()
        mock_get_channel_layer.return_value = mock_layer

        org = Organization.objects.create(name="Tick Test Org", slug="tick-org")
        contact = Contact.objects.create(full_name="Lead Ticks")
        cpn = ContactPhoneNumber.objects.create(contact=contact, whatsapp_jid="5511988887777@s.whatsapp.net")
        conv = Conversation.objects.create(contact=contact, organization_id=org.id)

        from django.utils import timezone

        msg = Message.objects.create(
            conversation=conv,
            external_id="EVO_MSG_12345",
            sender_whatsapp="5511988887777@s.whatsapp.net",
            direction=Message.Direction.OUTBOUND,
            content="Mensagem de teste de ticks",
            delivery_status=Message.DeliveryStatus.SENT,
            is_read=False,
            timestamp=timezone.now(),
        )

        service = WhatsAppService()

        # 1. Simula messages.update com DELIVERY_ACK
        payload_delivered = {
            "event": "messages.update",
            "instance": "ai_control_tick-org",
            "data": {
                "key": {
                    "id": "EVO_MSG_12345",
                    "fromMe": True,
                    "remoteJid": "5511988887777@s.whatsapp.net"
                },
                "update": {
                    "status": "DELIVERY_ACK"
                }
            }
        }
        service.process_event("messages.update", payload_delivered, "tick-org")
        msg.refresh_from_db()
        assert msg.delivery_status == Message.DeliveryStatus.DELIVERED
        assert not msg.is_read

        # 2. Simula messages.update com READ
        payload_read = {
            "event": "messages.update",
            "instance": "ai_control_tick-org",
            "data": [
                {
                    "key": {
                        "id": "EVO_MSG_12345",
                        "fromMe": True
                    },
                    "update": {
                        "status": "READ"
                    }
                }
            ]
        }
        service.process_event("messages.update", payload_read, "tick-org")
        msg.refresh_from_db()
        assert msg.delivery_status == Message.DeliveryStatus.READ
        assert msg.is_read is True
        assert msg.read_at is not None

