# read.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:55:00(GMT-04:00)
import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from omnichannel.models import Contact, Conversation, Message, CopilotDraft

logger = logging.getLogger(__name__)
User = get_user_model()


class ContactReadSerializer(serializers.ModelSerializer):
    """
    Serializer de Contato para leitura com blindagem rigorosa de PII (LGPD Art. 13 e 46).
    O número de telefone jamais é serializado ou exposto.
    A identidade é resolvida deterministicamente no campo `display_name`.
    """
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['id', 'display_name', 'avatar_url', 'status']
        read_only_fields = ['id', 'display_name', 'status']

    def get_display_name(self, obj):
        # Prioridade 1: full_name (se cadastrado e preenchido)
        if obj.full_name and str(obj.full_name).strip():
            return str(obj.full_name).strip()
        # Prioridade 2: whatsapp_push_name (configurado pelo cliente no WhatsApp)
        if obj.whatsapp_push_name and str(obj.whatsapp_push_name).strip():
            return str(obj.whatsapp_push_name).strip()
        # Prioridade 3: Fallback elegante e anônimo
        contact_id_str = str(obj.id)
        return f"Lead #{contact_id_str[:4]}"


class QuotedMessageReadSerializer(serializers.ModelSerializer):
    """
    Representação resumida da mensagem citada (Reply To) para leitura na timeline.
    """
    class Meta:
        model = Message
        fields = ['id', 'content', 'media_type', 'timestamp']
        read_only_fields = fields


class MessageReadSerializer(serializers.ModelSerializer):
    """
    Serializer de Leitura de Mensagem para a timeline do chat.
    Zero exposição de telefones no payload do chat.
    """
    sender_name = serializers.SerializerMethodField()
    quoted_message = QuotedMessageReadSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'external_id',
            'direction',
            'content',
            'sent_by_ai',
            'delivery_status',
            'is_read',
            'read_at',
            'media_type',
            'media_url',
            'media_mimetype',
            'media_duration',
            'sender_user_id',
            'sender_name',
            'quoted_message',
            'timestamp',
            'created_at',
        ]
        read_only_fields = fields

    def get_sender_name(self, obj):
        if obj.direction == Message.Direction.OUTBOUND:
            if obj.sent_by_ai:
                return "Assistente IA"
            if obj.sender_user_id:
                try:
                    user = User.objects.filter(id=obj.sender_user_id).first()
                    if user:
                        return user.get_full_name() or user.username
                except Exception:
                    pass
                return "Atendente"
            return "Atendente"
        # Para INBOUND, o nome vem do Contact
        return None


class ConversationReadSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para o painel de listagem de conversas.
    Em conformidade com o Princípio P15 (Anti N+1): prioriza os campos desnormalizados
    last_message_preview e last_message_timestamp da Conversation para evitar queries em loop.
    """
    contact = ContactReadSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'contact',
            'status',
            'access_level',
            'unread_count',
            'is_pinned',
            'channel_type',
            'instance_name',
            'last_message',
            'tags',
            'assigned_user_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_last_message(self, obj):
        # 1. Verifica cache prefetched em memória se disponível (Anti N+1)
        if hasattr(obj, '_prefetched_objects_cache') and 'messages' in obj._prefetched_objects_cache:
            messages = obj._prefetched_objects_cache['messages']
            if messages:
                last_msg = messages[0] if isinstance(messages, list) else messages.first()
                if last_msg:
                    return {
                        "id": str(last_msg.id),
                        "content": last_msg.content,
                        "direction": last_msg.direction,
                        "timestamp": last_msg.timestamp.isoformat() if last_msg.timestamp else None,
                        "delivery_status": last_msg.delivery_status,
                        "media_type": last_msg.media_type,
                    }

        # 2. Resolução instantânea O(1) via campos desnormalizados
        if obj.last_message_preview:
            return {
                "id": None,
                "content": obj.last_message_preview,
                "direction": Message.Direction.INBOUND,
                "timestamp": obj.last_message_timestamp.isoformat() if obj.last_message_timestamp else None,
                "delivery_status": Message.DeliveryStatus.DELIVERED,
                "media_type": Message.MediaType.TEXT,
            }

        # 3. Fallback de segurança para testes que não utilizam o service layer
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return {
                "id": str(last_msg.id),
                "content": last_msg.content,
                "direction": last_msg.direction,
                "timestamp": last_msg.timestamp.isoformat() if last_msg.timestamp else None,
                "delivery_status": last_msg.delivery_status,
                "media_type": last_msg.media_type,
            }

        return None


class CopilotDraftReadSerializer(serializers.ModelSerializer):
    """
    Serializer para as sugestões preditivas do Copiloto de IA em modo de leitura.
    """
    class Meta:
        model = CopilotDraft
        fields = [
            'id',
            'conversation_id',
            'trigger_message_id',
            'suggested_content',
            'final_sent_content',
            'status',
            'generated_by_model',
            'latency_ms',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
