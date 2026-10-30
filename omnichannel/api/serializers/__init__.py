# __init__.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:55:00(GMT-04:00)
"""
Serializers do módulo Omnichannel com segregação formal de Leitura vs. Escrita (Princípio P17)
e aliases canônicos retrocompatíveis para garantir zero regressão na suíte de testes existente.
"""

from omnichannel.api.serializers.read import (
    ContactReadSerializer,
    QuotedMessageReadSerializer,
    MessageReadSerializer,
    ConversationReadSerializer,
    CopilotDraftReadSerializer,
)

from omnichannel.api.serializers.write import (
    MessageCreateSerializer,
    TakeoverActionSerializer,
    InstanceActionSerializer,
)

# Aliases de compatibilidade para suítes de teste e integrações existentes
ContactSerializer = ContactReadSerializer
QuotedMessageSerializer = QuotedMessageReadSerializer
MessageSerializer = MessageReadSerializer
ConversationListSerializer = ConversationReadSerializer
CopilotDraftSerializer = CopilotDraftReadSerializer

__all__ = [
    # Read Serializers
    'ContactReadSerializer',
    'QuotedMessageReadSerializer',
    'MessageReadSerializer',
    'ConversationReadSerializer',
    'CopilotDraftReadSerializer',
    # Write Serializers
    'MessageCreateSerializer',
    'TakeoverActionSerializer',
    'InstanceActionSerializer',
    # Retrocompatible Aliases
    'ContactSerializer',
    'QuotedMessageSerializer',
    'MessageSerializer',
    'ConversationListSerializer',
    'CopilotDraftSerializer',
]
