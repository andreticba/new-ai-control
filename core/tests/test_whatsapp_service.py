# test_whatsapp_service.py | AI-Control SDD v0.6.0 | 03-10-2026 00:15(GMT-04:00)
from django.test import TestCase
from unittest.mock import patch
from core.models import Organization
from omnichannel.models import Contact, ContactPhoneNumber, Conversation, Message
from core.services.whatsapp_service import WhatsAppService

class WhatsAppServiceTests(TestCase):
    def test_whatsapp_service_instantiation(self):
        service = WhatsAppService()
        self.assertTrue(hasattr(service, 'process_event'))

    @patch('core.services.whatsapp_service.send_typing_signal.apply_async')
    @patch('core.services.whatsapp_service.async_to_sync')
    @patch('core.services.whatsapp_service.get_channel_layer')
    @patch('core.services.whatsapp_service.AIIngestionDelegator.delay')
    def test_process_message_upsert(self, mock_delegator, mock_get_channel_layer, mock_async_to_sync, mock_send_typing):
        payload = {
            "event": "messages.upsert",
            "data": {
                "key": {
                    "fromMe": False, 
                    "remoteJid": "551199999999@s.whatsapp.net",
                    "id": "MSG_ID_123"
                },
                "message": {
                    "conversation": "Hello from testing"
                },
                "pushName": "Test User",
                "messageTimestamp": 1690000000
            }
        }
        
        service = WhatsAppService()
        service.process_message_upsert(payload, "ai-control-01")
        
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.first()
        self.assertEqual(msg.content, "Hello from testing")
        self.assertEqual(msg.sender_whatsapp, "551199999999@s.whatsapp.net")
        
        # Test if WebSocket was called
        mock_get_channel_layer.assert_called()
        mock_async_to_sync.assert_called()
        
        # Test if AI Ingestion was called (T009)
        mock_delegator.assert_called_once_with(payload)
        
        # Test if typing signal was scheduled (T011)
        mock_send_typing.assert_called_once()
        args, kwargs = mock_send_typing.call_args
        self.assertEqual(kwargs['countdown'], 5)
        self.assertEqual(kwargs['args'], ["ai-control-01", "551199999999@s.whatsapp.net"])
