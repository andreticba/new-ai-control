# test_whatsapp_tasks.py | AI-Control SDD v0.6.0 | 02-10-2026 23:59(GMT-04:00)
from django.test import TestCase
from core.tasks.whatsapp_tasks import AIIngestionDelegator

class WhatsAppTasksTests(TestCase):
    def test_delegator_task_exists(self):
        self.assertTrue(callable(AIIngestionDelegator))
