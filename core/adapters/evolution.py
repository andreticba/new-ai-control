# core/adapters/evolution.py | AI-Control SDD v0.6.0 | 29-09-2026 15:14(GMT-04:00)

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class UnifiedMessageDTO:
    """
    Representação unificada de uma mensagem que entra no sistema,
    desacoplada do formato específico do gateway (Evolution API).
    """
    message_id: str
    sender_jid: str  # JID bruto do remetente (ex: 551199999999@s.whatsapp.net)
    sender_phone: str  # Telefone limpo (ex: 551199999999)
    receiver_jid: str # A organização/número que recebeu
    push_name: str # Nome enviado pelo WhatsApp
    content: str
    timestamp: int
    is_group: bool = False
    from_me: bool = False

class EvolutionWebhookAdapter:
    """
    Adapter para transformar o payload bruto do Evolution API v2 em UnifiedMessageDTO.
    """
    
    @classmethod
    def parse_messages(cls, payload: Dict[str, Any]) -> List[UnifiedMessageDTO]:
        """
        No Evolution API v2, o payload de evento 'MESSAGES_UPSERT' contém o campo 'data'.
        'data' pode vir as chaves principais como 'key', 'message', 'pushName'.
        """
        event = payload.get('event')
        if event != 'messages.upsert':
            return []
            
        data = payload.get('data', {})
        
        # Pode vir como dicionário único ou lista dependendo da versão exata, mas no webhook
        # geralmente o 'data' contém 'message', 'key', 'pushName', etc., ou é uma lista deles.
        messages_data = [data] if isinstance(data, dict) else data
        parsed_messages = []
        
        for msg_data in messages_data:
            key = msg_data.get('key', {})
            message_info = msg_data.get('message', {})
            
            message_id = key.get('id', '')
            remote_jid = key.get('remoteJid', '')
            from_me = key.get('fromMe', False)
            
            # Se for do próprio bot (fromMe), ignoramos (ou registramos como outbound se necessário)
            # Para recebimento do usuário, from_me é False.
            
            is_group = '@g.us' in remote_jid
            push_name = msg_data.get('pushName', '')
            timestamp = msg_data.get('messageTimestamp', 0)
            
            # Extrair texto
            # O texto pode estar em message.conversation ou message.extendedTextMessage.text
            content = ''
            if 'conversation' in message_info:
                content = message_info['conversation']
            elif 'extendedTextMessage' in message_info:
                content = message_info['extendedTextMessage'].get('text', '')
            elif 'imageMessage' in message_info:
                content = message_info['imageMessage'].get('caption', '[Imagem]')
            elif 'videoMessage' in message_info:
                content = message_info['videoMessage'].get('caption', '[Vídeo]')
            elif 'audioMessage' in message_info:
                content = '[Áudio]'
            elif 'documentMessage' in message_info:
                content = '[Documento]'
            
            if not content:
                content = '[Mensagem não suportada/vazia]'
                
            sender_phone = remote_jid.split('@')[0]
            
            dto = UnifiedMessageDTO(
                message_id=message_id,
                sender_jid=remote_jid,
                sender_phone=sender_phone,
                receiver_jid=msg_data.get('owner', ''), # No webhook o owner/instance costuma vir na query ou payload global
                push_name=push_name,
                content=content,
                timestamp=timestamp,
                is_group=is_group,
                from_me=from_me
            )
            parsed_messages.append(dto)
            
        return parsed_messages
