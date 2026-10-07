# whatsapp_tasks.py | AI-Control SDD v0.6.0 | 03-10-2026 00:15(GMT-04:00)
from celery import shared_task

@shared_task
def AIIngestionDelegator(payload: dict):
    pass

@shared_task
def send_typing_signal(org_slug: str, remote_jid: str):
    from core.services.evolution_gateway import EvolutionGatewayService
    gw = EvolutionGatewayService()
    instance_name = gw._instance_name(org_slug)
    gw.send_presence(instance_name, remote_jid, "composing")

@shared_task
def process_whatsapp_webhook_task(event_item: dict):
    from core.services.whatsapp_service import WhatsAppService
    
    event_type = event_item.get("event")
    
    # Resolve isolation by extracting org_slug from instance name
    instance_name = event_item.get("instance", "")
    if instance_name.startswith("ai_control_"):
        org_slug = instance_name.replace("ai_control_", "", 1)
    else:
        org_slug = "default"
        
    service = WhatsAppService()
    service.process_event(event_type, event_item, org_slug)
