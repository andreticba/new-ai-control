# whatsapp_tasks.py | AI-Control SDD v0.6.0 | 20-10-2026 19:33:00(GMT-04:00)
import logging
from celery import shared_task

logger = logging.getLogger(__name__)

def should_delegate_to_ai(conversation) -> bool:
    if not conversation:
        return True
    from omnichannel.models import Conversation
    return conversation.status != Conversation.Status.ACTIVE_HUMAN


@shared_task
def AIIngestionDelegator(payload: dict):
    """
    Despachante assíncrono para ingestão e geração de respostas autônomas da IA.
    Trava de Segurança Inviolável (FR-004 / T015):
    Se a conversa estiver sob controle humano (ACTIVE_HUMAN), nenhuma resposta autônoma
    da IA será gerada ou despachada.
    """
    from core.adapters.evolution import EvolutionWebhookAdapter
    from omnichannel.models import ContactPhoneNumber, Conversation
    
    parsed_list = EvolutionWebhookAdapter.parse_messages(payload)
    if not parsed_list:
        return
        
    for parsed in parsed_list:
        if parsed.from_me:
            continue
        cpn = ContactPhoneNumber.objects.filter(whatsapp_jid=parsed.sender_jid).first()
        if cpn:
            conv = Conversation.objects.filter(contact=cpn.contact).order_by('-updated_at').first()
            if not should_delegate_to_ai(conv):
                logger.info(f"[AIIngestionDelegator] Supressão de IA: Conversa {conv.id} está em ACTIVE_HUMAN (Takeover por {conv.assigned_user_id}).")
                return


AIIngestionDelegator.should_delegate_to_ai = staticmethod(should_delegate_to_ai)

@shared_task
def send_typing_signal(org_slug: str, remote_jid: str):
    """
    Emite sinal visual de 'digitando...' caso o processamento demore.
    Trava de Takeover: Suprime se a conversa estiver sob atendimento humano ativo.
    """
    from omnichannel.models import ContactPhoneNumber, Conversation
    cpn = ContactPhoneNumber.objects.filter(whatsapp_jid=remote_jid).first()
    if cpn:
        conv = Conversation.objects.filter(contact=cpn.contact).order_by('-updated_at').first()
        if conv and conv.status == Conversation.Status.ACTIVE_HUMAN:
            logger.info(f"[send_typing_signal] Supressão de typing: Conversa {conv.id} está sob atendimento humano.")
            return

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
