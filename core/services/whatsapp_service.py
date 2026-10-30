# whatsapp_service.py | AI-Control SDD v0.6.0 | 03-10-2026 00:15(GMT-04:00)
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from core.models import AuditLog, Organization
from omnichannel.models import ContactPhoneNumber, Conversation, Message, Contact, ContactOrganizationMembership
from omnichannel.services import DefaultOrganizationService
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
        elif event_type == "messages.update":
            self.process_message_update(payload, org_slug)
        elif event_type == "connection.update":
            self.process_connection_update(payload, org_slug)
        elif event_type == "qrcode.updated":
            self.process_qrcode_updated(payload, org_slug)
        else:
            logger.info(f"Ignoring unknown event: {event_type}")

    def process_message_update(self, payload: dict, org_slug: str):
        """
        Atualiza o delivery_status da mensagem (Sent ➔ Delivered ➔ Read / Ticks azuis)
        e notifica via WebSocket em tempo real.
        """
        from django.utils import timezone
        data = payload.get("data", {})
        updates_list = data if isinstance(data, list) else [data]

        STATUS_MAP = {
            1: Message.DeliveryStatus.SENT,
            "1": Message.DeliveryStatus.SENT,
            "SERVER_ACK": Message.DeliveryStatus.SENT,
            "SENT": Message.DeliveryStatus.SENT,
            2: Message.DeliveryStatus.DELIVERED,
            "2": Message.DeliveryStatus.DELIVERED,
            "DELIVERY_ACK": Message.DeliveryStatus.DELIVERED,
            "DELIVERED": Message.DeliveryStatus.DELIVERED,
            3: Message.DeliveryStatus.READ,
            "3": Message.DeliveryStatus.READ,
            "READ": Message.DeliveryStatus.READ,
            "PLAYED": Message.DeliveryStatus.READ,
            4: Message.DeliveryStatus.FAILED,
            "4": Message.DeliveryStatus.FAILED,
            "ERROR": Message.DeliveryStatus.FAILED,
            "FAILED": Message.DeliveryStatus.FAILED,
        }

        channel_layer = get_channel_layer()

        for item in updates_list:
            if not isinstance(item, dict):
                continue

            key = item.get("key", {}) if isinstance(item.get("key"), dict) else {}
            external_id = key.get("id") or item.get("id") or item.get("keyId")
            if not external_id:
                continue

            update_info = item.get("update", {}) if isinstance(item.get("update"), dict) else {}
            raw_status = update_info.get("status") or item.get("status")
            if raw_status is None:
                continue

            target_status = STATUS_MAP.get(raw_status)
            if not target_status:
                continue

            msg = Message.objects.filter(external_id=external_id).select_related("conversation").first()
            if not msg:
                continue

            updated_fields = []
            if target_status == Message.DeliveryStatus.READ:
                msg.delivery_status = Message.DeliveryStatus.READ
                msg.is_read = True
                if not msg.read_at:
                    msg.read_at = timezone.now()
                    updated_fields.append("read_at")
                updated_fields.extend(["delivery_status", "is_read"])
            elif target_status == Message.DeliveryStatus.DELIVERED:
                if msg.delivery_status != Message.DeliveryStatus.READ:
                    msg.delivery_status = Message.DeliveryStatus.DELIVERED
                    updated_fields.append("delivery_status")
            elif target_status == Message.DeliveryStatus.FAILED:
                msg.delivery_status = Message.DeliveryStatus.FAILED
                updated_fields.append("delivery_status")

            if updated_fields:
                msg.save(update_fields=updated_fields)

            if channel_layer and msg.conversation:
                org_id = msg.conversation.organization_id
                async_to_sync(channel_layer.group_send)(
                    f'private-org-{org_id}',
                    {
                        'type': 'conversation_message_status_updated',
                        'data': {
                            'conversation_id': str(msg.conversation_id),
                            'message_id': str(msg.id),
                            'external_id': msg.external_id,
                            'delivery_status': msg.delivery_status,
                            'is_read': msg.is_read,
                            'read_at': msg.read_at.isoformat() if msg.read_at else None,
                        }
                    }
                )

    def process_qrcode_updated(self, payload: dict, org_slug: str):
        data = payload.get("data", {})
        qrcode_info = data.get("qrcode", {}) if isinstance(data.get("qrcode"), dict) else {}
        base64_str = qrcode_info.get("base64") or data.get("base64")
        if not base64_str:
            return

        instance_name = payload.get("instance") or f"ai_control_{org_slug}"
        cache.set(f"whats_gt:qrcode:{instance_name}", base64_str, timeout=60)

        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                if org_slug and org_slug not in ('default', 'none', ''):
                    org = Organization.objects.filter(slug=org_slug, is_active=True).first()
                else:
                    org = DefaultOrganizationService.get_default_organization()

                if org:
                    async_to_sync(channel_layer.group_send)(
                        f'private-org-{org.id}',
                        {
                            'type': 'forward_event',
                            'event_type': 'whatsapp.qrcode.updated',
                            'data': {
                                'instance_name': instance_name,
                                'qrcode_base64': base64_str,
                            }
                        }
                    )
            except Exception as e:
                logger.warning(f"Erro ao emitir qrcode.updated: {e}")

    def process_message_upsert(self, payload: dict, org_slug: str):
        parsed_list = EvolutionWebhookAdapter.parse_messages(payload)
        if not parsed_list:
            return
            
        for parsed in parsed_list:
            if parsed.from_me:
                continue
                
            try:
                # Resolução robusta de organização (P01 & P07)
                if org_slug and org_slug not in ('default', 'none', ''):
                    org = Organization.objects.filter(slug=org_slug, is_active=True).first()
                    if not org:
                        org, _ = Organization.objects.get_or_create(slug=org_slug, defaults={'name': org_slug, 'is_active': True})
                else:
                    org = DefaultOrganizationService.get_default_organization()

                if not org:
                    org = DefaultOrganizationService.get_default_organization()
                
                remote_jid = parsed.sender_jid
                cpn = ContactPhoneNumber.objects.filter(whatsapp_jid=remote_jid).first()
                if not cpn:
                    contact = Contact.objects.create(
                        status=Contact.Status.PLATFORM_LEAD,
                        whatsapp_push_name=parsed.push_name or None
                    )
                    cpn = ContactPhoneNumber.objects.create(contact=contact, whatsapp_jid=remote_jid)
                    ContactOrganizationMembership.objects.get_or_create(
                        contact=contact,
                        organization_id=org.id
                    )
                else:
                    contact = cpn.contact
                    ContactOrganizationMembership.objects.get_or_create(
                        contact=contact,
                        organization_id=org.id
                    )
                    if parsed.push_name and contact.whatsapp_push_name != parsed.push_name:
                        contact.whatsapp_push_name = parsed.push_name
                        contact.save(update_fields=['whatsapp_push_name', 'updated_at'])
                    
                conv, _ = Conversation.objects.get_or_create(
                    contact=cpn.contact, 
                    organization_id=org.id,
                    defaults={"status": Conversation.Status.ACTIVE_AI}
                )
                
                from django.utils import timezone
                import datetime
                dt = timezone.make_aware(datetime.datetime.fromtimestamp(parsed.timestamp)) if parsed.timestamp else timezone.now()
                
                # Sincronização de preview e contador não lido para performance O(1)
                conv.last_message_preview = parsed.content[:250] if parsed.content else ""
                conv.last_message_timestamp = dt
                conv.unread_count = (conv.unread_count or 0) + 1
                conv.save(update_fields=['last_message_preview', 'last_message_timestamp', 'unread_count', 'updated_at'])

                msg = Message.objects.create(
                    conversation=conv,
                    external_id=parsed.message_id or None,
                    sender_whatsapp=remote_jid,
                    direction=Message.Direction.INBOUND,
                    content=parsed.content,
                    delivery_status=Message.DeliveryStatus.DELIVERED,
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
                    
                    # Notificação em tempo real para o frontend Omnichannel (Blindagem de PII)
                    display_name = contact.whatsapp_push_name or (str(contact.full_name) if contact.full_name else f"Lead #{str(contact.id)[:4]}")
                    safe_omnichannel_payload = {
                        "conversation_id": str(conv.id),
                        "message": {
                            "id": str(msg.id),
                            "external_id": msg.external_id,
                            "direction": "INBOUND",
                            "content": parsed.content,
                            "delivery_status": msg.delivery_status,
                            "is_read": False,
                            "media_type": msg.media_type,
                            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                        },
                        "contact": {
                            "id": str(contact.id),
                            "display_name": display_name,
                            "avatar_url": contact.avatar_url,
                            "status": contact.status,
                        },
                        "unread_count": conv.unread_count,
                    }
                    async_to_sync(channel_layer.group_send)(
                        f'private-org-{org.id}',
                        {
                            'type': 'conversation_message_new',
                            'data': safe_omnichannel_payload
                        }
                    )
                
                if conv.status == Conversation.Status.ACTIVE_AI:
                    AIIngestionDelegator.delay(payload)
                    # FR-006: Emitir typing se o Celery demorar (countdown de 5 segundos)
                    send_typing_signal.apply_async(args=[org_slug, remote_jid], countdown=5)
                elif conv.status == Conversation.Status.ACTIVE_HUMAN:
                    # FR-006 / T020: Disparar geração preditiva assíncrona do Copiloto de IA
                    try:
                        from omnichannel.tasks.copilot_tasks import generate_copilot_draft_task
                        generate_copilot_draft_task.delay(str(conv.id), str(msg.id))
                    except Exception as copilot_err:
                        logger.warning(f"Erro ao agendar task do Copilot: {copilot_err}")
                
            except Exception as e:
                logger.error(f"Error handling message upsert: {e}", exc_info=True)

    def process_connection_update(self, payload: dict, org_slug: str):
        state = payload.get("data", {}).get("state", "unknown")
        cache.set(f'whats_gt:state:{org_slug}', state, 86400)
        if state in ("open", "close"):
            instance_name = payload.get("instance") or f"ai_control_{org_slug}"
            cache.delete(f"whats_gt:qrcode:{instance_name}")
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'debug_messages_{org_slug}',
                {'type': 'connection_update', 'state': state}
            )

            try:
                if org_slug and org_slug not in ('default', 'none', ''):
                    org = Organization.objects.filter(slug=org_slug, is_active=True).first()
                else:
                    org = DefaultOrganizationService.get_default_organization()
                if not org:
                    org = DefaultOrganizationService.get_default_organization()

                if org:
                    async_to_sync(channel_layer.group_send)(
                        f'private-org-{org.id}',
                        {
                            'type': 'forward_event',
                            'event_type': 'whatsapp.connection.updated',
                            'data': {
                                'state': state,
                                'connected': state == 'open',
                                'org_id': str(org.id),
                            }
                        }
                    )
            except Exception as e:
                logger.warning(f"Erro ao emitir connection.update para omnichannel: {e}")
            
        # Debounce com Redis (TTL 10s) para evitar flapping no AuditLog (T017)
        debounce_key = f"whats_gt:connection_debounce:{org_slug}:{state}"
        if not cache.get(debounce_key):
            cache.set(debounce_key, True, timeout=10)
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
