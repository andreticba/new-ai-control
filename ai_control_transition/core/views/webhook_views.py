# webhook_views.py | AI-Control SDD v0.6.0 | 02-10-2026 23:59(GMT-04:00)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.utils import sanitize_phi_pii
from core.services.whatsapp_service import WhatsAppService
import logging

logger = logging.getLogger(__name__)

class WebhookSinkholeView(APIView):
    """
    Catch-all view para eventos de webhook não suportados.
    Recebe o request, sanitiza PII/PHI, loga e retorna 200 OK.
    """
    def post(self, request, event_type=None, *args, **kwargs):
        payload = request.data
        sanitized_payload = sanitize_phi_pii(payload)
        
        logger.info(f"Ignorando evento não suportado: {event_type} | Payload: {sanitized_payload}")
        
        return Response({"status": "ignored"}, status=status.HTTP_200_OK)

def _extract_org_slug(request):
    org_slug = request.query_params.get('org')
    if not org_slug:
        instance_name = request.data.get('instance', '')
        if instance_name.startswith('ai_control_'):
            org_slug = instance_name.replace('ai_control_', '', 1)
        else:
            org_slug = 'default'
    return org_slug

class MessagesUpsertWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.data
        org_slug = _extract_org_slug(request)
        WhatsAppService().process_event("messages.upsert", payload, org_slug)
        return Response({"status": "received"}, status=status.HTTP_200_OK)

class ConnectionUpdateWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.data
        org_slug = _extract_org_slug(request)
        WhatsAppService().process_event("connection.update", payload, org_slug)
        return Response({"status": "received"}, status=status.HTTP_200_OK)

class MessagesUpdateWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"status": "received"}, status=status.HTTP_200_OK)

class ContactsUpsertWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"status": "received"}, status=status.HTTP_200_OK)

class SendMessageWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({"status": "received"}, status=status.HTTP_200_OK)
