<!-- omnichannel_api_contracts.md | Vitalia SDD v0.6.0 | 20-10-2026 18:02:00(GMT-04:00) -->
> **omnichannel_api_contracts.md | Vitalia SDD v0.6.0 | 20-10-2026 18:02:00(GMT-04:00)**

# API Contracts & Integration Interfaces: 005-omnichannel-integration

Este documento padroniza os contratos de interface do módulo Omnichannel, integrando o gateway ativo da Evolution API v2 com os endpoints REST de frontend, eventos WebSockets e tasks Celery, em rigorosa conformidade com o **Princípio de Não-Exibição de PII**: **telefones não são expostos na interface de conversas**, sendo substituídos pelo `display_name` e `avatar_url`.

---

## 1. Webhook Evolution API v2 (Em Produção)

Endpoint canônico já configurado no [docker-compose.yml](file:///home/andre/projetos/assistidos/ai-control/docker-compose.yml) e atendido por [core/api/v1/views/webhook_whatsapp.py](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/webhook_whatsapp.py):

- **Path:** `POST /api/v1/webhook/whatsapp/`
- **Autenticação:** Header `apikey`, Query param `?apikey=...` ou campo `apikey` no payload validado contra `settings.WHATS_GT_API_KEY`.
- **Payload Exemplo (`messages.upsert`):**
  ```json
  {
    "event": "messages.upsert",
    "instance": "ai_control_minha-empresa",
    "data": {
      "key": {
        "remoteJid": "5565999887766@s.whatsapp.net",
        "fromMe": false,
        "id": "EVL-MSG-998877"
      },
      "pushName": "João Silva",
      "message": {
        "conversation": "Olá, gostaria de saber os serviços disponíveis."
      },
      "messageTimestamp": 1729459200
    }
  }
  ```
- **Comportamento:**
  - Silent drop imediato para eventos de sincronização: `chats.set`, `chats.update`.
  - Captura do `pushName` e persistência no `Contact.whatsapp_push_name`.
  - Despacho assíncrono para o Celery: `process_whatsapp_webhook_task.delay(event_item)`.
  - Resposta síncrona: `200 OK` (`{"status": "success"}`) em $P95 \le 200\text{ms}$.

---

## 2. Endpoints REST para o Frontend de Atendimento (DRF)

### 2.1 Listar Conversas
- **Path:** `GET /api/v1/omnichannel/conversations/`
- **Headers:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Query Params:**
  - `status`: `ACTIVE_AI` | `ACTIVE_HUMAN` | `CLOSED`
  - `filter`: `all` | `unread` | `ai` | `mine` | `pinned`
  - `search`: busca textual por nome de contato ou assunto
  - `page`, `page_size`: Paginação padrão DRF
- **Response `200 OK` (Zero PII - Sem telefones expostos):**
  ```json
  {
    "count": 42,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "contact": {
          "id": "7ca64731-...",
          "display_name": "João Silva",
          "avatar_url": "https://pps.whatsapp.net/v/t61.24694-24/...",
          "status": "CLIENT"
        },
        "status": "ACTIVE_AI",
        "unread_count": 2,
        "is_pinned": false,
        "last_message": {
          "content": "Olá, gostaria de saber os serviços...",
          "direction": "INBOUND",
          "timestamp": "2026-10-20T17:20:00Z"
        },
        "tags": ["Financeiro", "VIP"],
        "assigned_user_id": null
      }
    ]
  }
  ```

### 2.2 Timeline de Mensagens da Conversa
- **Path:** `GET /api/v1/omnichannel/conversations/{id}/messages/`
- **Headers:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Response `200 OK`:**
  ```json
  {
    "results": [
      {
        "id": "8b9c...",
        "external_id": "EVL-MSG-998877",
        "direction": "INBOUND",
        "content": "Olá, gostaria de saber os serviços disponíveis.",
        "sent_by_ai": false,
        "delivery_status": "READ",
        "is_read": true,
        "media_type": "text",
        "media_url": null,
        "media_duration": null,
        "quoted_message": null,
        "timestamp": "2026-10-20T17:20:00Z"
      },
      {
        "id": "9c1d...",
        "external_id": "EVL-MSG-998878",
        "direction": "OUTBOUND",
        "content": "Olá João! Segue a apresentação de nossos serviços em anexo.",
        "sent_by_ai": false,
        "sender_user_id": "4d5e...",
        "sender_name": "Pedro Santos",
        "delivery_status": "DELIVERED",
        "is_read": true,
        "media_type": "document",
        "media_url": "https://storage.ai-control.com/docs/apresentacao.pdf",
        "media_duration": null,
        "quoted_message": {
          "id": "8b9c...",
          "content": "Olá, gostaria de saber os serviços disponíveis."
        },
        "timestamp": "2026-10-20T17:21:00Z"
      }
    ]
  }
  ```

### 2.3 Takeover Humano (Assumir Atendimento)
- **Path:** `POST /api/v1/omnichannel/conversations/{id}/takeover/`
- **Headers:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Comportamento:** Altera `status` para `ACTIVE_HUMAN`, atribui `assigned_user_id = request.user.id`, bloqueia auto-respostas da IA e emite evento WebSocket `conversation.status.updated`.

### 2.4 Devolver para IA
- **Path:** `POST /api/v1/omnichannel/conversations/{id}/return-to-ai/`
- **Comportamento:** Altera `status` para `ACTIVE_AI`, limpa `assigned_user_id` e reativa a IA.

### 2.5 Ações do Copiloto (Aprovar / Descartar Draft)
- **Path:** `POST /api/v1/omnichannel/copilot-drafts/{id}/approve/`
- **Payload Opcional (se editado pelo operador):**
  ```json
  {
    "edited_content": "Texto ajustado pelo atendente antes do envio."
  }
  ```
- **Comportamento:** Grava `final_sent_content`, marca draft como `APPROVED`, despacha mensagem outbound para a Evolution API e cria `Message(direction='OUTBOUND', sent_by_ai=True)`.
- **Path:** `POST /api/v1/omnichannel/copilot-drafts/{id}/discard/`

---

## 3. Contratos de WebSockets (Django Channels)

- **Conexão:** `ws://localhost:8000/ws/omnichannel/?token=<JWT>`
- **Channel Layer Group:** `private-org-{organization_id}`
- **Eventos:**
  1. `conversation.message.new`: Nova mensagem (inbound ou outbound) com delivery status e mídias
  2. `conversation.message.status_updated`: Atualização dos ticks (Sent ➔ Delivered ➔ Read)
  3. `copilot.draft.generated`: Sugestão preditiva para o atendente com `suggested_content`
  4. `conversation.status.updated`: Transição de status da fila ou takeover
