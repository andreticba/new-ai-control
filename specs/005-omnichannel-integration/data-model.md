<!-- data-model.md | Vitalia SDD v0.6.0 | 20-10-2026 18:02:00(GMT-04:00) -->
> **data-model.md | Vitalia SDD v0.6.0 | 20-10-2026 18:02:00(GMT-04:00)**

# Data Model: 005-omnichannel-integration (Arquitetura Completa e Blindagem de PII)

Este documento especifica o modelo de dados completo do módulo Omnichannel, preservando a retrocompatibilidade com as tabelas existentes em [omnichannel/models.py](file:///home/andre/projetos/assistidos/ai-control/omnichannel/models.py), adicionando as extensões necessárias para atender 100% dos requisitos da interface do WhatsApp Web e consolidando a **Diretriz Máxima de Proteção de PII**: **o telefone (mesmo mascarado) NUNCA é exibido na lista ou no chat**, sendo substituído exclusivamente pelo **Nome de Exibição (`whatsapp_push_name` / `full_name`)** e **Foto de Perfil (`avatar_url`)**.

---

## 1. Diagrama Entidade-Relacionamento Completo (ERD)

```mermaid
erDiagram
    Contact {
        UUID id PK
        text full_name "EncryptedTextField (AES)"
        string whatsapp_push_name "Nome no WhatsApp (ex: Carlos Silva)"
        string avatar_url "Foto do perfil do WhatsApp"
        string_array search_tokens "GinIndex para busca"
        string status "PLATFORM_LEAD | CUSTOMER_LEAD | PROSPECT | CLIENT | ARCHIVED"
        datetime created_at
        datetime updated_at
    }

    ContactPhoneNumber {
        UUID id PK
        UUID contact_id FK
        string whatsapp_jid "UK (ex: 5565...@s.whatsapp.net)"
        string phone_number "EncryptedCharField (RSA/AES)"
        string phone_hash "HMAC-SHA256 Blind Index (db_index)"
        string description
        datetime created_at
        datetime updated_at
    }

    ContactOrganizationMembership {
        UUID contact_id FK
        UUID organization_id "Soft FK (db_index)"
        string validated_email "EncryptedCharField"
        text notes "EncryptedTextField"
        datetime created_at
        datetime updated_at
    }

    Conversation {
        UUID id PK
        UUID contact_id FK "PROTECT"
        UUID organization_id "Soft FK, db_index"
        string status "ACTIVE_AI | ACTIVE_HUMAN | CLOSED"
        string access_level "PUBLIC | SUPERVISOR_ONLY | MUTED"
        UUID assigned_user_id "Nullable, db_index (Operador alocado)"
        datetime last_message_timestamp
        text last_message_preview "Prévia de texto O(1)"
        int unread_count "Contador de não lidas O(1)"
        boolean is_pinned "Fixar conversa no topo"
        string channel_type "WHATSAPP | INSTAGRAM | WEBCHAT"
        string instance_name "ai_control_{org_slug}"
        string_array tags "Tags de CRM (ex: VIP, Suporte)"
        boolean context_locked
        datetime locked_at
        string current_intent
        int consecutive_rag_failures
        datetime created_at
        datetime updated_at
    }

    Message {
        UUID id PK
        UUID conversation_id FK "CASCADE"
        string external_id "ID Evolution (data.key.id, db_index)"
        string sender_whatsapp "JID técnico para roteamento"
        UUID sender_user_id "Nullable, db_index (Atendente humano que enviou)"
        string direction "INBOUND | OUTBOUND"
        text content "Texto da mensagem ou legenda"
        boolean sent_by_ai "True se gerado/enviado pela IA"
        string delivery_status "PENDING | SENT | DELIVERED | READ | FAILED"
        boolean is_read "True se lida pelo atendente"
        datetime read_at "Data/hora de leitura"
        string visibility_level "PUBLIC | INTERNAL_TEAM | ARCHIVED"
        string sentiment "NEUTRAL | POSITIVE | URGENT | FRUSTRATED"
        string media_type "text | image | audio | video | document | sticker"
        text media_url "URL da mídia/anexo"
        string media_mimetype "MIME type (ex: audio/ogg, image/jpeg)"
        int media_duration "Duração em segundos para áudio"
        UUID quoted_message_id "FK self (Mensagem citada / Reply to)"
        datetime timestamp "Timestamp do WhatsApp"
        datetime created_at
    }

    CopilotDraft {
        UUID id PK
        UUID conversation_id FK "CASCADE"
        UUID trigger_message_id "FK Message (Mensagem que motivou a sugestão)"
        text suggested_content "Texto sugerido pela IA"
        text final_sent_content "Texto editado/enviado pelo operador"
        string status "PENDING | APPROVED | DISCARDED"
        string generated_by_model "ex: phi4-mini:latest"
        float latency_ms
        datetime created_at
        datetime updated_at
    }

    Contact ||--o{ ContactPhoneNumber : "has phone numbers"
    Contact ||--o{ ContactOrganizationMembership : "belongs to orgs"
    Contact ||--o{ Conversation : "initiates conversations"
    Conversation ||--o{ Message : "contains messages"
    Message ||--o{ Message : "replies to (quoted)"
    Conversation ||--o{ CopilotDraft : "receives AI suggestions"
    Message ||--o{ CopilotDraft : "triggers suggestion"
```

---

## 2. Protocolo de Blindagem e Não-Exibição de PII (LGPD Art. 13 e 46)

Para proteger a privacidade dos clientes finais e blindar o sistema contra vazamento de dados em trânsito e na interface:

1. **Proibição de Telefone na Interface Operacional:**
   - O número de telefone (seja em formato E.164 ou mascarado como `***-7766`) **NÃO** deve ser renderizado:
     - Na lista de conversas (cards à esquerda);
     - No cabeçalho do chat ativo;
     - Nos balões de mensagem.
2. **Hierarquia de Exibição de Identidade (`display_name`):**
   - **Prioridade 1:** `full_name` qualificado no CRM (descriptografado sob permissão);
   - **Prioridade 2:** `whatsapp_push_name` (nome configurado pelo cliente no WhatsApp, ex: "Carlos Silva");
   - **Prioridade 3:** Fallback elegante (`"Lead #<UUID[:4]>"` ou `"Contato Anônimo"`).
3. **Foto de Perfil (`avatar_url`):**
   - Carregada dinamicamente via Evolution API (`/chat/fetchProfilePictureUrl/{instance}`) e salva no `Contact`.
   - Caso não exista foto, a interface exibe as iniciais do `display_name` sobre gradiente suave.
4. **Armazenamento e Busca:**
   - O telefone real existe apenas cifrado em repouso (`phone_number`).
   - A busca relacional rápida ocorre exclusivamente pelo índice cego `phone_hash` (HMAC-SHA256).

---

## 3. Detalhamento dos Modelos e Extensões Não-Destrutivas

### 3.1 `Contact` (Extensão Não-Destrutiva)
- `avatar_url`: TextField (null=True, blank=True) — URL do avatar do WhatsApp.
- `whatsapp_push_name`: CharField(max_length=255, null=True, blank=True) — Nome de exibição vindo do webhook.
- *Campos vigentes mantidos:* `id`, `full_name`, `search_tokens`, `status`, `created_at`, `updated_at`.

### 3.2 `Conversation` (Extensão Não-Destrutiva)
- `unread_count`: PositiveIntegerField(default=0) — Otimização O(1) para badges de não lidas na lista.
- `last_message_preview`: TextField(null=True, blank=True) — Prévia da última mensagem para renderização instantânea da lista.
- `is_pinned`: BooleanField(default=False) — Fixar conversas prioritárias no topo.
- `channel_type`: CharField(max_length=20, default='WHATSAPP') — Suporte a múltiplos canais omnichannel.
- `instance_name`: CharField(max_length=100, null=True, blank=True) — Nome da instância conectada.
- `tags`: ArrayField(models.CharField(max_length=50), blank=True, default=list) — Categorização e tags de CRM.
- *Campos vigentes mantidos:* `id`, `contact`, `organization_id`, `status`, `access_level`, `assigned_user_id`, `last_message_timestamp`, `context_locked`, `locked_at`, `current_intent`, `consecutive_rag_failures`, `created_at`, `updated_at`.

### 3.3 `Message` (Extensão Não-Destrutiva)
- `external_id`: CharField(max_length=255, db_index=True, null=True, blank=True) — ID único da Evolution API (`key.id`) para idempotência e atualização de ticks.
- `delivery_status`: CharField(choices=['PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED'], default='DELIVERED') — Estado de entrega no WhatsApp (ticks cinzas e azuis).
- `is_read`: BooleanField(default=False) — Leitura da mensagem pelo operador humano.
- `read_at`: DateTimeField(null=True, blank=True) — Timestamp em que o operador visualizou a mensagem.
- `sender_user_id`: UUIDField(null=True, blank=True, db_index=True) — Identificador do atendente humano quando a mensagem for `OUTBOUND` e não for gerada por IA.
- `media_type`: CharField(max_length=20, default='text') — text, image, audio, video, document, sticker.
- `media_url`: TextField(null=True, blank=True) — URL segura da mídia para download/reprodução.
- `media_mimetype`: CharField(max_length=100, null=True, blank=True) — Tipo MIME da mídia.
- `media_duration`: PositiveIntegerField(null=True, blank=True) — Duração em segundos (essencial para player de áudio PTT).
- `quoted_message`: ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies') — Citação / resposta contextual a mensagem anterior.
- *Campos vigentes mantidos:* `id`, `conversation`, `sender_whatsapp`, `direction`, `content`, `sent_by_ai`, `visibility_level`, `sentiment`, `timestamp`, `created_at`.

### 3.4 `CopilotDraft` (Nova Entidade Não-Destrutiva)
- `id`: UUID (PK)
- `conversation`: ForeignKey (`Conversation`, on_delete=models.CASCADE, related_name='copilot_drafts')
- `trigger_message`: ForeignKey (`Message`, on_delete=models.SET_NULL, null=True, blank=True) — Mensagem inbound que gerou a sugestão
- `suggested_content`: TextField — Texto proposto pelo LLM local
- `final_sent_content`: TextField (null=True, blank=True) — Texto final aprovado e enviado pelo atendente (métrica de acurácia)
- `status`: Enum (`PENDING`, `APPROVED`, `DISCARDED`)
- `generated_by_model`: CharField (default="phi4-mini:latest")
- `latency_ms`: FloatField (latência de inferência)
- `created_at`, `updated_at`: DateTimeField
