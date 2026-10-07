from celery import shared_task
from core.models import WhatsAppSession

@shared_task
def checkpoint_sessions():
    """Dummy task para efetuar checkpoints do Redis pro BD."""
    pass
