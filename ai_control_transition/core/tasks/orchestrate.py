from celery import shared_task
from core.models import WhatsAppSession, ConversationTurn

@shared_task
def run_orchestrator(session_id: str, turn_id: str, wa_id_raw: str = None):
    """
    Main orchestration task.
    In MVP, wa_id_raw should be provided to send messages back.
    """
    session = WhatsAppSession.objects.get(id=session_id)
    turn = ConversationTurn.objects.get(id=turn_id)
    
    # If wa_id_raw is not provided, we might not be able to reply, but we'll try processing anyway.
    if not wa_id_raw:
        # Fallback for old tests / tasks
        wa_id_raw = "unknown"
        
    from core.orchestrator.agent import process_turn
    process_turn(session, turn, wa_id_raw)
