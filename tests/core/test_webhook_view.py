# tests/core/test_webhook_view.py
import pytest
from unittest.mock import patch
import json


@pytest.fixture
def webhook_url():
    return "/api/v1/webhook/whatsapp/"


@pytest.mark.django_db
class TestWebhookView:
    @patch("core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay")
    def test_webhook_returns_200_immediately(self, mock_delay, client, webhook_url, settings):
        settings.WHATS_GT_API_KEY = "test_key"
        response = client.post(
            webhook_url,
            data=json.dumps({"event": "messages.upsert", "data": {}}),
            content_type="application/json",
            HTTP_APIKEY="test_key",
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    @patch("core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay")
    def test_webhook_enqueues_celery_task(self, mock_delay, client, webhook_url, settings):
        settings.WHATS_GT_API_KEY = "test_key"
        payload = {"event": "messages.upsert", "data": {"id": "1"}}
        client.post(
            webhook_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_APIKEY="test_key",
        )
        mock_delay.assert_called_once()

    def test_webhook_unauthorized_without_key(self, client, webhook_url, settings):
        settings.WHATS_GT_API_KEY = "test_key"
        response = client.post(
            webhook_url,
            data=json.dumps({"event": "messages.upsert"}),
            content_type="application/json",
        )
        assert response.status_code == 401
