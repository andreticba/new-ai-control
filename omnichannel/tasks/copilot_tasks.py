# copilot_tasks.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:41:00(GMT-04:00)
import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from omnichannel.services.copilot_service import CopilotService

logger = logging.getLogger(__name__)


@shared_task
def generate_copilot_draft_task(conversation_id, trigger_message_id=None):
    """
    Task Celery assíncrona (FR-006 / T019):
    Invoca o Ollama em segundo plano e emite o draft via WebSocket para o atendente humano.
    """
    try:
        service = CopilotService()
        draft = service.generate_suggestion(conversation_id, trigger_message_id)
        if not draft:
            return None

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"private-org-{draft.conversation.organization_id}",
                {
                    "type": "copilot_draft_generated",
                    "data": {
                        "draft_id": str(draft.id),
                        "conversation_id": str(draft.conversation_id),
                        "trigger_message_id": str(draft.trigger_message_id) if draft.trigger_message_id else None,
                        "suggested_content": draft.suggested_content,
                        "model": draft.generated_by_model,
                        "latency_ms": draft.latency_ms,
                        "created_at": draft.created_at.isoformat(),
                    }
                }
            )

        logger.info(
            f"[CopilotDraft] draft_id={draft.id} conversation_id={draft.conversation_id} "
            f"model={draft.generated_by_model} latency_ms={draft.latency_ms}"
        )

        return str(draft.id)
    except Exception as e:
        logger.error(f"[generate_copilot_draft_task] Erro na geração de sugestão do Copiloto: {e}", exc_info=True)
        return None
