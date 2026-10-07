# whatsapp_service.py | AI-Control SDD v0.6.0 | 03-10-2026 00:15(GMT-04:00)
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from core.models import AuditLog, ContactPhoneNumber, Organization, Conversation, Message, Contact
from core.adapters.evolution import EvolutionWebhookAdapter
from core.tasks.whatsapp_tasks import AIIngestionDelegator, send_typing_signal

logger = logging.getLogger(__name__)

def _mask_pii(text):
    if not text:
        return text
    if '@' not in text:
        return '***@unknown'
    phone_part, domain = text.split('@', 1)
    if len(phone_part) >= 8:
        return f"{phone_part[:5]}***{phone_part[-4:]}@{domain}"
    return f"***@{domain}"

class WhatsAppService:
    
    def process_event(self, event_type: str, payload: dict, org_slug: str):
        if event_type == "messages.upsert":
            self.process_message_upsert(payload, org_slug)
        elif event_type == "connection.update":
            self.process_connection_update(payload, org_slug)
        else:
            logger.info(f"Ignoring unknown event: {event_type}")

    def process_message_upsert(self, payload: dict, org_slug: str):
        parsed_list = EvolutionWebhookAdapter.parse_messages(payload)
        if not parsed_list:
            return
            
        for parsed in parsed_list:
            if parsed.from_me:
                continue
                
            try:
                org, _ = Organization.objects.get_or_create(slug=org_slug, defaults={'name': org_slug})
                
                remote_jid = parsed.sender_jid
                cpn = ContactPhoneNumber.objects.filter(whatsapp_jid=remote_jid).first()
                if not cpn:
                    contact = Contact.objects.create(status=Contact.Status.PLATFORM_LEAD)
                    cpn = ContactPhoneNumber.objects.create(contact=contact, whatsapp_jid=remote_jid)
                    
                conv, _ = Conversation.objects.get_or_create(
                    contact=cpn.contact, 
                    organization=org,
                    defaults={"status": Conversation.Status.ACTIVE_AI}
                )
                
                from django.utils import timezone
                import datetime
                dt = timezone.make_aware(datetime.datetime.fromtimestamp(parsed.timestamp)) if parsed.timestamp else timezone.now()
                
                msg = Message.objects.create(
                    conversation=conv,
                    sender_whatsapp=remote_jid,
                    direction=Message.Direction.INBOUND,
                    content=parsed.content,
                    timestamp=dt
                )
                
                channel_layer = get_channel_layer()
                if channel_layer:
                    text = parsed.content
                    if len(text) > 200:
                        text = text[:197] + "..."
                        
                    safe_payload = {
                        "id": str(msg.id),
                        "direction": "INBOUND",
                        "content": text,
                        "sender_whatsapp": _mask_pii(remote_jid),
                        "timestamp": msg.created_at.isoformat()
                    }
                    async_to_sync(channel_layer.group_send)(
                        f'debug_messages_{org_slug}',
                        {'type': 'new_message', 'message': safe_payload}
                    )
                
                if conv.status == Conversation.Status.ACTIVE_AI:
                    AIIngestionDelegator.delay(payload)
                    # FR-006: Emitir typing se o Celery demorar (countdown de 5 segundos)
                    send_typing_signal.apply_async(args=[org_slug, remote_jid], countdown=5)
                
            except Exception as e:
                logger.error(f"Error handling message upsert: {e}", exc_info=True)

    def process_connection_update(self, payload: dict, org_slug: str):
        state = payload.get("data", {}).get("state", "unknown")
        cache.set(f'whats_gt:state:{org_slug}', state, 86400)
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'debug_messages_{org_slug}',
                {'type': 'connection_update', 'state': state}
            )
            
        if state == "open":
            AuditLog.objects.create(
                action=AuditLog.ActionType.WHATSAPP_CONNECTED,
                details={"org_slug": org_slug, "state": state}
            )
        elif state == "close":
            AuditLog.objects.create(
                action=AuditLog.ActionType.WHATSAPP_DISCONNECTED,
                details={"org_slug": org_slug, "state": state}
            )
