# test_evolution_events_task.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from core.models import AuditLog, Message
from core.tasks.evolution_events import process_evolution_event

@pytest.mark.django_db
class TestEvolutionEventsTask:
    
    @patch("core.tasks.evolution_events._handle_message_upsert")
    def test_routes_messages_upsert(self, mock_upsert):
        payload = {"event": "messages.upsert", "data": {}}
        process_evolution_event(payload, "test_org")
        mock_upsert.assert_called_once_with(payload, "test_org")

    @patch("core.tasks.evolution_events._handle_connection_update")
    def test_routes_connection_update(self, mock_conn):
        payload = {"event": "connection.update", "data": {}}
        process_evolution_event(payload, "test_org")
        mock_conn.assert_called_once_with(payload, "test_org")

    def test_unknown_event_is_ignored(self):
        payload = {"event": "unknown.event"}
        assert process_evolution_event(payload, "test_org") is None

    @patch("core.tasks.evolution_events.cache.set")
    def test_connection_update_open_sets_cache(self, mock_cache_set):
        payload = {"event": "connection.update", "data": {"state": "open"}}
        process_evolution_event(payload, "test_org")
        mock_cache_set.assert_called_once_with('whats_gt:state:test_org', 'open', 86400)

    @patch("core.tasks.evolution_events.async_to_sync")
    @patch("core.tasks.evolution_events.get_channel_layer")
    def test_connection_update_broadcasts_ws(self, mock_get_channel_layer, mock_async_to_sync):
        mock_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_layer
        
        dummy = MagicMock()
        mock_async_to_sync.return_value = dummy
        
        payload = {"event": "connection.update", "data": {"state": "open"}}
        process_evolution_event(payload, "test_org")
        
        dummy.assert_called_once_with(
            'debug_messages_test_org',
            {'type': 'connection_update', 'state': 'open'}
        )

    def test_connection_update_open_writes_auditlog(self):
        payload = {"event": "connection.update", "data": {"state": "open"}}
        process_evolution_event(payload, "test_org")
        
        log = AuditLog.objects.filter(action=AuditLog.ActionType.WHATSAPP_CONNECTED).first()
        assert log is not None
        assert log.details.get("org_slug") == "test_org"

    @patch("core.tasks.evolution_events.EvolutionWebhookAdapter")
    def test_message_upsert_saves_message(self, mock_adapter_class):
        mock_dto = MagicMock()
        mock_dto.from_me = False
        mock_dto.sender_jid = "5511999999999@s.whatsapp.net"
        mock_dto.content = "Hello"
        mock_dto.timestamp = 1600000000
        
        mock_adapter_class.parse_messages.return_value = [mock_dto]
        
        with patch("core.tasks.evolution_events.Organization.objects.get_or_create") as mock_org, \
             patch("core.tasks.evolution_events.ContactPhoneNumber.objects.filter") as mock_cpn, \
             patch("core.tasks.evolution_events.Conversation.objects.get_or_create") as mock_conv, \
             patch("core.tasks.evolution_events.Message.objects.create") as mock_msg_create, \
             patch("core.tasks.evolution_events.get_channel_layer") as mock_channel, \
             patch("core.tasks.evolution_events.async_to_sync") as mock_async_to_sync:
            
            mock_org.return_value = (MagicMock(), False)
            mock_cpn.return_value.first.return_value = MagicMock(contact=MagicMock())
            mock_conv.return_value = (MagicMock(), False)
            mock_async_to_sync.return_value = MagicMock()
            
            payload = {"event": "messages.upsert", "data": {}}
            process_evolution_event(payload, "test_org")
            
            mock_msg_create.assert_called_once()
