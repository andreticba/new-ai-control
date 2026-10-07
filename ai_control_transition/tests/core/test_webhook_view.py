# test_webhook_view.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
import pytest
from django.urls import reverse
from unittest.mock import patch
import json

@pytest.fixture
def webhook_url():
    return "/api/v1/webhook/whatsapp/?org=test_org"

@pytest.mark.django_db
class TestWebhookView:
    @patch("core.views.webhook.process_evolution_event.delay")
    def test_webhook_returns_200_immediately(self, mock_delay, client, webhook_url):
        response = client.post(
            webhook_url,
            data=json.dumps({"event": "test", "data": {}}),
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json() == {"status": "queued"}

    @patch("core.views.webhook.process_evolution_event.delay")
    def test_webhook_enqueues_celery_task(self, mock_delay, client, webhook_url):
        payload = {"event": "test"}
        client.post(
            webhook_url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        mock_delay.assert_called_once_with(payload, "test_org")

    def test_webhook_invalid_json_returns_400(self, client, webhook_url):
        response = client.post(
            webhook_url,
            data="invalid-json",
            content_type="application/json"
        )
        assert response.status_code == 400

    def test_webhook_no_csrf_required(self, client, webhook_url):
        response = client.post(
            webhook_url,
            data=json.dumps({"event": "test"}),
            content_type="application/json"
        )
        assert response.status_code == 200
