<!-- decoupling_contracts.md | Vitalia SDD v0.6.0 | 20-10-2026 23:10:00(GMT-04:00) -->
> **decoupling_contracts.md | Vitalia SDD v0.6.0 | 20-10-2026 23:10:00(GMT-04:00)**

# Contratos de Interface & Tipagem Estrita: 006-omnichannel-decoupling

Este documento define as especificações formais de tipagem, assinaturas e contratos de dados para a refatoração de desacoplamento do módulo Omnichannel, tanto no ecossistema Frontend (TypeScript / React 19) quanto no Backend (Python 3.14 / Django REST Framework), blindando o sistema contra alucinações e ambiguidades de implementação.

---

## 1. Contratos do Frontend (TypeScript)

### 1.1 Hook: `useColumnResize` (`frontend/src/hooks/use-column-resize.ts`)

```typescript
export interface UseColumnResizeOptions {
  /** Chave única para persistência no localStorage */
  storageKey: string;
  /** Largura padrão inicial em pixels se não houver valor em cache */
  defaultWidth: number;
  /** Limite inferior de segurança em pixels */
  minWidth: number;
  /** Limite superior de segurança em pixels */
  maxWidth: number;
  /**
   * Direção de arraste:
   * - 'left': O cálculo da largura é (clientX - offset). Indicado para colunas alinhadas à esquerda (ex: Sidebar).
   * - 'right': O cálculo da largura é (window.innerWidth - clientX). Indicado para drawers ancorados à direita.
   */
  direction?: 'left' | 'right';
  /** Offset horizontal da barra de navegação/dock (ex: 56px para a dock lateral) */
  offset?: number;
}

export interface UseColumnResizeReturn {
  /** Largura corrente da coluna em pixels */
  width: number;
  /** Flag booleana indicando se o usuário está arrastando a divisória ativamente */
  isDragging: boolean;
  /** Handler para o evento onMouseDown da divisória */
  startDragging: (e: React.MouseEvent) => void;
  /** Redefine a largura para o valor padrão de fábrica */
  resetWidth: () => void;
}

export function useColumnResize(options: UseColumnResizeOptions): UseColumnResizeReturn;
```

### 1.2 Hook: `useWhatsAppInstance` (`frontend/src/hooks/use-whatsapp-instance.ts`)

```typescript
export interface WhatsAppInstanceStatus {
  instanceName: string;
  state: 'open' | 'connecting' | 'close' | 'unknown';
  connected: boolean;
  qrCodeBase64: string | null;
}

export interface UseWhatsAppInstanceReturn {
  status: WhatsAppInstanceStatus;
  isLoading: boolean;
  isDisconnecting: boolean;
  /** Consulta o status atual da instância e atualiza o estado */
  refreshStatus: () => Promise<void>;
  /** Gera um novo QR Code para pareamento */
  generateQrCode: () => Promise<void>;
  /** Desconecta (logout) a instância da Evolution API */
  disconnectInstance: () => Promise<boolean>;
}

export function useWhatsAppInstance(orgId?: string): UseWhatsAppInstanceReturn;
```

### 1.3 Componente: `NavRail` (`frontend/src/components/omnichannel/nav-rail.tsx`)

```typescript
export interface NavRailProps {
  user: {
    email?: string;
    username?: string;
    full_name?: string;
  } | null;
  isWhatsAppConnected: boolean;
  onOpenWhatsAppModal: () => void;
  activeTab?: 'conversations' | 'settings';
}
```

### 1.4 Componente: `OmnichannelHeader` (`frontend/src/components/omnichannel/omnichannel-header.tsx`)

```typescript
export interface OmnichannelHeaderProps {
  organizationName: string;
  isConnected: boolean; // WebSocket state
  isWhatsAppConnected: boolean;
  onOpenWhatsAppModal: () => void;
}
```

### 1.5 Componente: `ColumnSplitter` (`frontend/src/components/omnichannel/column-splitter.tsx`)

```typescript
export interface ColumnSplitterProps {
  isDragging: boolean;
  onMouseDown: (e: React.MouseEvent) => void;
  variant?: 'cyan' | 'emerald';
  title?: string;
}
```

---

## 2. Contratos do Backend (Python & DRF)

### 2.1 Service Layer: `InstanceService` (`omnichannel/services/instance_service.py`)

```python
import uuid
from typing import Optional, TypedDict
from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()


class InstanceStatusPayload(TypedDict):
    instance_name: str
    state: str  # "open" | "connecting" | "close" | "unknown"
    connected: bool
    qrcode_base64: Optional[str]


class InstanceService:
    @classmethod
    def get_status(cls, organization: Organization) -> InstanceStatusPayload:
        """
        Consulta o status da conexão da instância da organização junto à Evolution API.
        Se state != 'open', tenta obter o QR code em base64.
        """

    @classmethod
    def generate_qr(cls, organization: Organization, request=None) -> InstanceStatusPayload:
        """
        Garante que a instância foi criada e configurada com webhook, e gera novo QR Code.
        """

    @classmethod
    def disconnect(cls, organization: Organization, actor: User) -> bool:
        """
        Desconecta (logout) a instância da Evolution API e registra entrada no AuditLog.
        """
```

### 2.2 Service Layer: `TakeoverService` (`omnichannel/services/takeover_service.py`)

```python
import uuid
from django.contrib.auth import get_user_model
from omnichannel.models import Conversation

User = get_user_model()


class TakeoverService:
    @classmethod
    def assign_to_human(cls, conversation: Conversation, operator: User) -> Conversation:
        """
        Executa trava atômica. Atualiza status para ACTIVE_HUMAN e assigned_user_id para operator.id.
        Emite evento 'conversation_status_updated' no channel_layer da organização.
        """

    @classmethod
    def return_to_ai(cls, conversation: Conversation, actor: User) -> Conversation:
        """
        Executa trava atômica. Atualiza status para ACTIVE_AI e assigned_user_id para None.
        Emite evento 'conversation_status_updated' no channel_layer da organização.
        """

    @classmethod
    def mark_as_read(cls, conversation: Conversation) -> int:
        """
        Atualiza todas as mensagens pendentes para is_read=True com timestamp atual.
        Zera o unread_count e emite evento WebSocket de atualização.
        Retorna a contagem de mensagens marcadas.
        """
```

### 2.3 Service Layer: `MessageDispatchService` (`omnichannel/services/message_dispatch_service.py`)

```python
import uuid
from typing import Optional
from django.contrib.auth import get_user_model
from omnichannel.models import Conversation, Message

User = get_user_model()


class MessageDispatchService:
    @classmethod
    def send_operator_message(
        cls,
        conversation: Conversation,
        sender_user: User,
        content: str,
        quoted_message_id: Optional[uuid.UUID] = None,
        media_type: str = Message.MediaType.TEXT,
        media_url: Optional[str] = None
    ) -> Message:
        """
        1. Valida se o contato possui JID do WhatsApp registrado.
        2. Resolve mensagem citada (se quoted_message_id for informado).
        3. Envia o payload para a Evolution API via EvolutionGatewayService.
        4. Cria a entidade Message (OUTBOUND, sent_by_ai=False, sender_user_id=sender_user.id).
        5. Atualiza last_message_preview e last_message_timestamp na Conversation.
        6. Emite evento WebSocket 'conversation_message_new'.
        Retorna a instância persistida de Message.
        """
```

---

## 3. Contratos de Serializers (Princípio P17: Read vs. Write)

### 3.1 Write Serializers (`omnichannel/api/serializers/write.py`)

```python
from rest_framework import serializers
from omnichannel.models import Message


class MessageCreateSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=True)
    content = serializers.CharField(required=True, allow_blank=False, max_length=10000)
    quoted_message_id = serializers.UUIDField(required=False, allow_null=True)
    media_type = serializers.ChoiceField(choices=Message.MediaType.choices, default=Message.MediaType.TEXT)
    media_url = serializers.URLField(required=False, allow_null=True)


class TakeoverActionSerializer(serializers.Serializer):
    """Payload de entrada para transbordo humano (opcionalmente recebe notas ou tags)."""
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)


class InstanceActionSerializer(serializers.Serializer):
    """Payload para ações sobre instâncias (suporta passar org_id explícito)."""
    org_id = serializers.UUIDField(required=False)
```

### 3.2 Read Serializers (`omnichannel/api/serializers/read.py`)

Preservam a estrutura JSON consumida pelo frontend, otimizados para evitar qualquer query adicional durante a serialização (Princípio P15).
```python
# Exportam:
# - ContactReadSerializer
# - QuotedMessageReadSerializer
# - MessageReadSerializer
# - ConversationReadSerializer
# - CopilotDraftReadSerializer
```
