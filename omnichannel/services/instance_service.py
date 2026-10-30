# omnichannel/services/instance_service.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:58:00(GMT-04:00)
import logging
from typing import Optional, Dict, Any
from core.models import Organization
from core.services.evolution_gateway import EvolutionGatewayService

logger = logging.getLogger(__name__)


class InstanceService:
    """
    Serviço de domínio para gestão do ciclo de vida das instâncias WhatsApp na Evolution API.
    Isola a comunicação REST, geração de QR Code e processo de logout.
    """

    @classmethod
    def get_status(cls, org_id: Any) -> Dict[str, Any]:
        """
        Consulta o status atual da instância de forma estritamente idempotente (read-only).
        Não gera novo QR Code automaticamente para evitar invalidar sockets do Baileys.
        """
        org = Organization.objects.filter(id=org_id).first()
        org_slug = org.slug if org and org.slug else "default"

        gw = EvolutionGatewayService()
        instance_name = gw._instance_name(org_slug)
        raw_state = gw.get_connection_state(instance_name)

        state = raw_state.get("state") if isinstance(raw_state, dict) else raw_state
        if state in ("refused", None, "unknown"):
            state = "close"

        from django.core.cache import cache
        cached_qr = cache.get(f'whats_gt:qrcode:{instance_name}') if state != "open" else None

        return {
            "instance_name": instance_name,
            "state": state,
            "connected": state == "open",
            "qrcode_base64": cached_qr,
        }

    @classmethod
    def generate_qr(cls, org_id: Any, request: Optional[Any] = None) -> Dict[str, Any]:
        """
        Gera uma nova instância ou reinicia o pareamento gerando um novo QR Code sob demanda.
        """
        org = Organization.objects.filter(id=org_id).first()
        org_slug = org.slug if org and org.slug else "default"

        gw = EvolutionGatewayService()
        instance_name = gw._instance_name(org_slug)

        gw.get_or_create_instance(org_slug, request=request)
        qr_res = gw.get_qr_code(instance_name)

        qr_data = None
        state = "connecting"
        if isinstance(qr_res, dict):
            if qr_res.get("connected"):
                state = "open"
            else:
                qr_data = qr_res.get("base64")
                if qr_data:
                    from django.core.cache import cache
                    cache.set(f'whats_gt:qrcode:{instance_name}', qr_data, timeout=60)

        if qr_data and org:
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f'private-org-{org.id}',
                        {
                            'type': 'forward_event',
                            'event_type': 'whatsapp.qrcode.updated',
                            'data': {
                                'instance_name': instance_name,
                                'qrcode_base64': qr_data,
                            }
                        }
                    )
            except Exception as e:
                logger.warning(f"Erro ao emitir evento de qrcode.updated no channel_layer: {e}")

        return {
            "instance_name": instance_name,
            "state": state,
            "connected": state == "open",
            "qrcode_base64": qr_data,
        }

    @classmethod
    def disconnect(cls, org_id: Any, actor: Optional[Any] = None) -> Dict[str, Any]:
        """
        Desconecta (logout) a instância da Evolution API com segurança.
        """
        org = Organization.objects.filter(id=org_id).first()
        org_slug = org.slug if org and org.slug else "default"

        gw = EvolutionGatewayService()
        instance_name = gw._instance_name(org_slug)

        success = gw.logout_instance(instance_name, actor=actor)

        from django.core.cache import cache
        cache.set(f'whats_gt:state:{org_slug}', 'close', 86400)
        cache.delete(f'whats_gt:qrcode:{instance_name}')

        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            if channel_layer and org:
                async_to_sync(channel_layer.group_send)(
                    f'private-org-{org.id}',
                    {
                        'type': 'forward_event',
                        'event_type': 'whatsapp.connection.updated',
                        'data': {
                            'instance_name': instance_name,
                            'state': 'close',
                            'connected': False,
                        }
                    }
                )
        except Exception as e:
            logger.warning(f"Erro ao emitir evento de desconexão no channel_layer: {e}")

        return {
            "instance_name": instance_name,
            "state": "close",
            "connected": False,
            "disconnected": bool(success),
            "success": bool(success),
        }
