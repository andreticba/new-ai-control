# core/api/v1/views/webhook_whatsapp.py | AI-Control SDD v0.6.0 | 03-10-2026 14:09(GMT-04:00)
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from core.tasks.whatsapp_tasks import process_whatsapp_webhook_task
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)

ACTIONABLE_EVENTS = {
    'messages.upsert',
    'messages.update',
    'messages.edited',
    'messages.delete',
    'message.delete',
    'qrcode.updated',
    'connection.update',
}

SILENT_DROP_EVENTS = {
    'contacts.upsert',
    'contacts.update',
    'contacts.set',
    'chats.upsert',
    'chats.update',
    'chats.delete',
    'chats.set',
    'presence.update',
    'send.message',
    'application.startup',
    'labels.association',
    'labels.edit',
    'call',
}

FORBIDDEN_LOG_KEYS = {'destination', 'apikey', 'sender', 'data', 'token', 'secret', 'key'}

class WebhookGatewayView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        summary="WhatsApp Webhook Receiver",
        description="Recebe eventos de webhook da API do WhatsApp via SaaS Gateway.",
        request=dict,
        responses={200: dict}
    )
    def post(self, request, *args, **kwargs):
        # T009: Validação do header/payload contra WHATS_GT_API_KEY
        api_key = request.headers.get('apikey') or request.META.get('HTTP_APIKEY')
        
        if not api_key:
            api_key = request.query_params.get('apikey')
            
        if not api_key and isinstance(request.data, dict):
            api_key = request.data.get('apikey')
            
        if not api_key or api_key != getattr(settings, 'WHATS_GT_API_KEY', None):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        import time
        start_time = time.perf_counter()

        # T012: Iteração primária
        payload = request.data
        events = payload if isinstance(payload, list) else [payload]

        for event_item in events:
            event_name = event_item.get('event')

            # FR-001: Silent Drop O(1) para presence.update e sync inicial
            if event_name in SILENT_DROP_EVENTS:
                continue

            # FR-002: Roteamento para Celery apenas de eventos acionáveis
            if event_name in ACTIONABLE_EVENTS:
                process_whatsapp_webhook_task.delay(event_item)
                continue

            # FR-007 / SC-001: Sanitização estrita de log para eventos desconhecidos
            safe_item = {k: v for k, v in event_item.items() if k.lower() not in FORBIDDEN_LOG_KEYS}
            logger.warning(f"Ignorando evento não suportado: {event_name} | Payload: {safe_item}")

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"[WebhookGateway] event_count={len(events)} latency_ms={duration_ms:.2f} status=200"
        )

        return Response({"status": "success"}, status=status.HTTP_200_OK)
