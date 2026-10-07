# core/tests/test_webhook_gateway.py | AI-Control SDD v0.6.0 | 03-10-2026 14:02(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def valid_headers():
    return {'HTTP_APIKEY': 'test-secret-key'}

@pytest.fixture
def gateway_url():
    # Usaremos o path hardcoded enquanto a rota n\u00e3o est\u00e1 nomeada/registrada
    return '/api/v1/webhook/whatsapp/'

@pytest.mark.django_db
class TestWebhookGateway:

    @patch('core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay')
    def test_object_payload_calls_celery_once(self, mock_delay, client, gateway_url, valid_headers, settings):
        settings.WHATS_GT_API_KEY = 'test-secret-key'
        payload = {"event": "messages.upsert", "data": {"id": "123"}}
        
        response = client.post(gateway_url, data=payload, format='json', **valid_headers)
        
        assert response.status_code == 200
        mock_delay.assert_called_once()

    @patch('core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay')
    def test_array_payload_calls_celery_n_times(self, mock_delay, client, gateway_url, valid_headers, settings):
        settings.WHATS_GT_API_KEY = 'test-secret-key'
        payload = [
            {"event": "messages.upsert", "data": {"id": "1"}},
            {"event": "messages.upsert", "data": {"id": "2"}}
        ]
        
        response = client.post(gateway_url, data=payload, format='json', **valid_headers)
        
        assert response.status_code == 200
        assert mock_delay.call_count == 2

    @patch('core.api.v1.views.webhook_whatsapp.process_whatsapp_webhook_task.delay')
    def test_silent_drop_for_chats_set(self, mock_delay, client, gateway_url, valid_headers, settings):
        settings.WHATS_GT_API_KEY = 'test-secret-key'
        payload = {"event": "chats.set", "data": {"huge_history": "..."}}
        
        response = client.post(gateway_url, data=payload, format='json', **valid_headers)
        
        assert response.status_code == 200
        mock_delay.assert_not_called()

    def test_authentication_401_no_key(self, client, gateway_url):
        payload = {"event": "messages.upsert", "data": {}}
        response = client.post(gateway_url, data=payload, format='json')
        assert response.status_code == 401

    @patch('core.api.v1.views.webhook_whatsapp.logger')
    def test_sanitization_for_unsupported_event(self, mock_logger, client, gateway_url, valid_headers, settings):
        settings.WHATS_GT_API_KEY = 'test-secret-key'
        payload = {"event": "unknown.event", "data": {"sensitive_pii": "John Doe"}}
        
        response = client.post(gateway_url, data=payload, format='json', **valid_headers)
        
        assert response.status_code == 200
        mock_logger.warning.assert_called()
        log_call_args = mock_logger.warning.call_args[0][0]
        assert "unknown.event" in log_call_args
        assert "John Doe" not in log_call_args
        assert "sensitive_pii" not in log_call_args
