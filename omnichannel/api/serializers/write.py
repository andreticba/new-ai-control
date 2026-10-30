# write.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:55:00(GMT-04:00)
from rest_framework import serializers
from omnichannel.models import Message


class MessageCreateSerializer(serializers.Serializer):
    """
    Validação estrita de entrada para despacho de mensagens manuais pelo operador humano.
    """
    conversation_id = serializers.UUIDField(required=True)
    content = serializers.CharField(required=True, allow_blank=False, max_length=10000)
    quoted_message_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    media_type = serializers.ChoiceField(
        choices=Message.MediaType.choices,
        default=Message.MediaType.TEXT
    )
    media_url = serializers.URLField(required=False, allow_null=True, default=None)


class TakeoverActionSerializer(serializers.Serializer):
    """
    Payload de entrada para transbordo ou devolução de atendimento.
    """
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500, default="")


class InstanceActionSerializer(serializers.Serializer):
    """
    Payload de entrada para ações na instância WhatsApp (suporta org_id explícito).
    """
    org_id = serializers.UUIDField(required=False, default=None)
