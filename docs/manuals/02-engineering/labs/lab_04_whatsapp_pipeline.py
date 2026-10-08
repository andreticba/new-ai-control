from _lab_base import run_lab, load_mock_personas
from core.models import Contact, ContactPhoneNumber, Conversation, Message
from core.services.whatsapp_service import WhatsAppService
import time

def lab_whatsapp():
    org_uf, _ = load_mock_personas()
    
    # 1. Payload simulado recebido do Evolution API via Webhook (já despachado ao Celery)
    payload_mock = {
        "event": "messages.upsert",
        "instance": f"ai_control_{org_uf.slug}",
        "data": {
            "message": {
                "conversation": "Olá, preciso de ajuda com o RAG."
            },
            "key": {
                "remoteJid": "5511999998888@s.whatsapp.net",
                "fromMe": False
            },
            "messageTimestamp": int(time.time())
        }
    }
    
    print("--- 1. Recebendo Payload do Webhook ---")
    print(f"Instância (Isolamento): {payload_mock['instance']}")
    
    # 2. Processamento via WhatsAppService (como o Celery faria)
    service = WhatsAppService()
    # O process_event mascara os PIIs no logger e cria entidades
    service.process_event(payload_mock['event'], payload_mock, org_uf.slug)
    
    # 3. Verificação do Estado no Banco
    print("\n--- 2. Entidades Criadas no Banco ---")
    contact_phone = ContactPhoneNumber.objects.get(whatsapp_jid="5511999998888@s.whatsapp.net")
    print(f"Contato: {contact_phone.contact.id} | Telefone: {contact_phone.whatsapp_jid}")
    
    conv = Conversation.objects.get(contact=contact_phone.contact, organization=org_uf)
    print(f"Conversa Status: {conv.status} | Tenant: {conv.organization.slug}")
    
    msg = Message.objects.filter(conversation=conv).first()
    print(f"Mensagem Registrada: '{msg.content}' | Direção: {msg.direction}")

if __name__ == '__main__':
    run_lab(lab_whatsapp)
