# whatsgt_views.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
import json
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from core.models import AuditLog
from omnichannel.models import Message
from core.services.evolution_gateway import EvolutionGatewayService

logger = logging.getLogger(__name__)

def _mask_sender_jid(jid):
    if not jid or '@' not in jid:
        return '***@unknown'
    phone_part, domain = jid.split('@', 1)
    if len(phone_part) >= 8:
        return f"{phone_part[:5]}***{phone_part[-4:]}@{domain}"
    return f"***@{domain}"

def _truncate_content(content, max_length=200):
    if not content:
        return ''
    if len(content) <= max_length:
        return content
    return content[:max_length] + ' [...]'

def _get_user_organization(user):
    if hasattr(user, 'profile') and user.profile and user.profile.primary_organization:
        return user.profile.primary_organization
    return None

def _rate_limit(request, action, limit=10, timeout=60):
    ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    key = f"rate_limit_{action}_{ip}_{request.user.id}"
    count = cache.get(key, 0)
    if count >= limit:
        return False
    cache.set(key, count + 1, timeout)
    return True


@method_decorator(staff_member_required, name='dispatch')
class WhatsGtInstanceQrView(View):
    def get(self, request, *args, **kwargs):
        if not _rate_limit(request, 'qr_code', limit=5, timeout=10):
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)

        org = _get_user_organization(request.user)
        org_slug = org.slug if org else 'default'
        
        state = cache.get(f'whats_gt:state:{org_slug}', 'unknown')
        gw = EvolutionGatewayService()
        instance_name = gw._instance_name(org_slug)

        if state in ('unknown', 'close'):
            gw.get_or_create_instance(org_slug, request=request)
            
        qr_data = gw.get_qr_code(instance_name)
        if qr_data:
            if "connected" in qr_data:
                cache.set(f'whats_gt:state:{org_slug}', 'open', 86400)
            return JsonResponse(qr_data)
            
        return JsonResponse({"error": "QR Code not ready yet"}, status=202)


@method_decorator(staff_member_required, name='dispatch')
class WhatsGtInstanceDeleteView(View):
    def delete(self, request, *args, **kwargs):
        if not _rate_limit(request, 'delete_instance', limit=5, timeout=10):
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)
            
        org = _get_user_organization(request.user)
        org_slug = org.slug if org else 'default'
        
        gw = EvolutionGatewayService()
        instance_name = gw._instance_name(org_slug)
        
        gw.delete_instance(instance_name, actor=request.user)
        cache.set(f'whats_gt:state:{org_slug}', 'close', 86400)
        
        return JsonResponse({"status": "deleted"})


@method_decorator(staff_member_required, name='dispatch')
class WhatsGtMessageSendView(View):
    def post(self, request, *args, **kwargs):
        if not _rate_limit(request, 'send', limit=10, timeout=60):
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON"}))

        jid = body.get("jid")
        text = body.get("text")

        if not jid or not isinstance(jid, str) or '@' not in jid:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid or missing 'jid'"}))
        if not text or not isinstance(text, str):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid or missing 'text'"}))

        AuditLog.objects.create(
            actor=request.user,
            action=AuditLog.ActionType.HUMAN_REVIEW,
            details={
                "action": "whatsgt_message_send",
                "jid": jid,
                "text": text,
                "ip_address": request.META.get('REMOTE_ADDR')
            },
            ip_address=request.META.get('REMOTE_ADDR')
        )

        org = _get_user_organization(request.user)
        org_slug = org.slug if org else 'default'
        
        gw = EvolutionGatewayService()
        instance_name = gw._instance_name(org_slug)
        
        result = gw.send_text_message(instance_name, jid, text)
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=502)
            
        return JsonResponse({"status": "sent", "evolution_response": result})


@method_decorator(staff_member_required, name='dispatch')
class WhatsGtMessagesListView(View):
    def get(self, request, *args, **kwargs):
        if not _rate_limit(request, 'message_list', limit=60, timeout=60):
            return JsonResponse({"error": "Rate limit exceeded"}, status=429)

        org = _get_user_organization(request.user)

        if org:
            messages = Message.objects.filter(
                conversation__organization=org
            ).order_by('-timestamp')[:50]
        else:
            messages = Message.objects.order_by('-timestamp')[:50]

        data = []
        for msg in messages:
            data.append({
                "id": str(msg.id),
                "direction": msg.direction,
                "content": _truncate_content(msg.content),
                "sender_whatsapp": _mask_sender_jid(msg.sender_whatsapp),
                "timestamp": msg.timestamp.isoformat(),
            })

        return JsonResponse({"messages": data})
