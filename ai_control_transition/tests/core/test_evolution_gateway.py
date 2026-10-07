# test_evolution_gateway.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings
from core.models import AuditLog
from core.services.evolution_gateway import EvolutionGatewayService
import requests

@pytest.fixture
def mock_settings(settings):
    settings.WHATS_GT_API_URL = "http://fake-api"
    settings.WHATS_GT_API_KEY = "fake-key"
    settings.WHATS_GT_WEBHOOK_BASE_URL = "http://fake-webhook"
    return settings

@pytest.mark.django_db
class TestEvolutionGatewayService:
    
    def test_instance_name_format(self, mock_settings):
        service = EvolutionGatewayService()
        assert service._instance_name("test_org") == "ai_control_test_org"

    @patch("core.services.evolution_gateway.requests.get")
    @patch("core.services.evolution_gateway.requests.post")
    def test_get_or_create_creates_when_404(self, mock_post, mock_get, mock_settings):
        mock_get.return_value = MagicMock(status_code=404)
        mock_post.side_effect = [
            MagicMock(status_code=201, json=lambda: {"status": "created"}),
            MagicMock(status_code=200, json=lambda: {"status": "success"})
        ]
        
        service = EvolutionGatewayService()
        result = service.get_or_create_instance("test_org")
        
        mock_get.assert_called_once_with("http://fake-api/instance/connectionState/ai_control_test_org", headers={"apikey": "fake-key"}, timeout=5)
        assert mock_post.call_count == 2
        
        create_call = mock_post.call_args_list[0]
        webhook_call = mock_post.call_args_list[1]
        
        assert create_call[0][0] == "http://fake-api/instance/create"
        assert create_call[1]["json"]["instanceName"] == "ai_control_test_org"
        assert create_call[1]["json"]["qrcode"] is True
        
        assert webhook_call[0][0] == "http://fake-api/webhook/set/ai_control_test_org"
        assert webhook_call[1]["json"]["webhook"]["url"] == "http://fake-webhook/api/v1/webhook/whatsapp/?org=test_org"
        
        assert result == {"status": "created"}

    @patch("core.services.evolution_gateway.requests.get")
    @patch("core.services.evolution_gateway.requests.post")
    def test_get_or_create_returns_existing_when_200(self, mock_post, mock_get, mock_settings):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"instance": {"state": "open"}})
        
        service = EvolutionGatewayService()
        result = service.get_or_create_instance("test_org")
        
        mock_get.assert_called_once()
        mock_post.assert_not_called()
        assert result == {"instance": {"state": "open"}}

    @patch("core.services.evolution_gateway.requests.delete")
    def test_delete_instance_calls_api(self, mock_delete, mock_settings):
        mock_delete.return_value = MagicMock(status_code=200)
        
        service = EvolutionGatewayService()
        service.delete_instance("ai_control_test")
        
        mock_delete.assert_called_once_with("http://fake-api/instance/delete/ai_control_test", headers={"apikey": "fake-key"}, timeout=5)

    @patch("core.services.evolution_gateway.requests.delete")
    def test_delete_instance_writes_auditlog(self, mock_delete, mock_settings):
        mock_delete.return_value = MagicMock(status_code=200)
        
        service = EvolutionGatewayService()
        service.delete_instance("ai_control_test")
        
        log = AuditLog.objects.filter(action=AuditLog.ActionType.WHATSAPP_INSTANCE_DELETE).first()
        assert log is not None
        assert log.details.get("instance_name") == "ai_control_test"

    @patch("core.services.evolution_gateway.requests.get")
    def test_get_qr_returns_base64(self, mock_get, mock_settings):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"base64": "data:image/png;base64,123"})
        
        service = EvolutionGatewayService()
        result = service.get_qr_code("ai_control_test")
        
        assert result == {"base64": "data:image/png;base64,123"}

    @patch("core.services.evolution_gateway.requests.get")
    def test_get_qr_returns_connected_when_open(self, mock_get, mock_settings):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"instance": {"state": "open"}})
        
        service = EvolutionGatewayService()
        result = service.get_qr_code("ai_control_test")
        
        assert result == {"connected": True}

    @patch("core.services.evolution_gateway.requests.post")
    def test_send_text_message(self, mock_post, mock_settings):
        mock_post.return_value = MagicMock(status_code=201)
        
        service = EvolutionGatewayService()
        service.send_text_message("ai_control_test", "123@s.whatsapp.net", "hello")
        
        mock_post.assert_called_once_with(
            "http://fake-api/message/sendText/ai_control_test",
            json={
                "number": "123@s.whatsapp.net",
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "textMessage": {
                    "text": "hello"
                }
            },
            headers={"apikey": "fake-key"},
            timeout=5
        )

    @patch("core.services.evolution_gateway.os.environ.get")
    def test_service_reads_credentials_from_settings(self, mock_env_get, mock_settings):
        EvolutionGatewayService()
        mock_env_get.assert_not_called()
