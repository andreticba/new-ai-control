# __init__.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
import logging
import requests
import os
from celery import shared_task
from core.models import DocumentChunk
from omnichannel.models import Message

logger = logging.getLogger(__name__)

@shared_task
def process_whatsapp_message_task(message_id: str):
    """
    Roteia a mensagem para a IA e dispara a resposta para o Evolution API.
    """
    try:
        msg = Message.objects.select_related('conversation', 'conversation__organization').get(id=message_id)
    except Message.DoesNotExist:
        logger.error(f"Mensagem {message_id} não encontrada.")
        return

    org = msg.conversation.organization
    
    logger.info(f"Processando IA para {msg.sender_whatsapp} (Org: {org.name})")
    
    # Exemplo: Isolamento estrito de Tenant no PgVector (FR-007)
    # Suponha que já geramos o embedding do 'msg.content' -> query_embedding
    # dummy_embedding = [...]
    # results = DocumentChunk.objects.filter(
    #     document__organization=org
    # ).order_by(L2Distance('embedding', dummy_embedding))[:5]
    
    # Mocking da resposta da IA
    ai_response_text = f"Resposta automática da IA para: {msg.content}"
    
    from django.utils import timezone
    # Criar mensagem de saída (Outbound)
    outbound_msg = Message.objects.create(
        conversation=msg.conversation,
        sender_whatsapp="AI-Bot",
        direction=Message.Direction.OUTBOUND,
        content=ai_response_text,
        sent_by_ai=True,
        timestamp=timezone.now()
    )
    
    from core.services.evolution_gateway import EvolutionGatewayService
    gw = EvolutionGatewayService()
    instance_name = gw._instance_name(org.slug)
    
    result = gw.send_text_message(instance_name, msg.sender_whatsapp, ai_response_text)
    
    if "error" in result:
        logger.error(f"Erro ao enviar resposta via Evolution API: {result['error']}")
    else:
        logger.info(f"Resposta enviada com sucesso para {msg.sender_whatsapp}")
