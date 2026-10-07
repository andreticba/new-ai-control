# test_sanitization.py | AI-Control SDD v0.6.0 | 02-10-2026 23:44(GMT-04:00)
from django.test import TestCase
from core.utils import sanitize_phi_pii

class SanitizationTests(TestCase):
    def test_sanitize_phi_pii_removes_sensitive_data(self):
        payload = {
            "pushName": "John Doe",
            "message": {
                "conversation": "My phone is +55 11 99999-9999",
                "participant": "123456789@s.whatsapp.net"
            },
            "status": "connected"
        }
        sanitized = sanitize_phi_pii(payload)
        
        self.assertEqual(sanitized["pushName"], "[PII/PHI]")
        self.assertEqual(sanitized["message"]["conversation"], "[PII/PHI]")
        self.assertEqual(sanitized["message"]["participant"], "[PII/PHI]")
        self.assertEqual(sanitized["status"], "connected")
        
    def test_sanitize_phi_pii_handles_lists(self):
        payload = {
            "contacts": [
                {"pushName": "Alice", "id": "111"},
                {"pushName": "Bob", "id": "222"}
            ]
        }
        sanitized = sanitize_phi_pii(payload)
        self.assertEqual(sanitized["contacts"][0]["pushName"], "[PII/PHI]")
        self.assertEqual(sanitized["contacts"][1]["pushName"], "[PII/PHI]")

    def test_sanitize_phi_pii_safe_keys_untouched(self):
        payload = {
            "event": "messages.upsert",
            "instance": "ai-control-01",
            "data": {
                "key": "value"
            }
        }
        sanitized = sanitize_phi_pii(payload)
        self.assertEqual(sanitized["event"], "messages.upsert")
        self.assertEqual(sanitized["data"]["key"], "value")
