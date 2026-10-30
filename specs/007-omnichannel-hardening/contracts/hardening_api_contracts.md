<!-- hardening_api_contracts.md | Vitalia SDD v0.6.0 | 21-10-2026 20:37:00(GMT-04:00) -->
> **hardening_api_contracts.md | Vitalia SDD v0.6.0 | 21-10-2026 20:37:00(GMT-04:00)**

# API Contracts & Integration Interfaces: 007-omnichannel-hardening

Este documento padroniza os contratos de interface do módulo Omnichannel após as medidas de hardening, cobrindo o webhook seguro da Evolution API v2, endpoints REST para despacho outbound com confirmação estrita, suporte a contatos novos sem organização versus contatos com usuário vinculado, CORS expandido e eventos de WebSocket.

---

## 1. Webhook Evolution API v2 Sanitizado

- **Endpoint:** `POST /api/v1/webhook/whatsapp/`
- **Autenticação:** Cabeçalho HTTP `apikey: <WHATS_GT_API_KEY>` (Recomendado) ou parâmetro na query string `?apikey=...` (higienizado por middleware).
- **Lista de Eventos Acionáveis (`ACTIONABLE_EVENTS`):**
  - `messages.upsert`: Criação de mensagem inbound (despachada ao Celery).
  - `messages.update`: Atualização de ticks de entrega/leitura (despachada ao Celery).
  - `messages.edited`: Atualização de texto de mensagem editada (despachada ao Celery).
  - `messages.delete`: Revogação de mensagem (despachada ao Celery).
  - `connection.update`: Atualização de status da conexão WhatsApp (despachada com debounce ao Celery).
  - `qrcode.updated`: Emissão de novo QR Code para pareamento (despachada ao Celery para broadcast via WebSocket).
- **Lista de Descarte Silencioso (`SILENT_DROP_EVENTS` em $O(1)$):**
  - `presence.update`: Status digitando/online de contatos.
  - `contacts.set` / `contacts.update` / `contacts.upsert`: Sincronização de contatos da agenda.
  - `chats.set` / `chats.update` / `chats.upsert` / `chats.delete`: Sincronização de metadados de chat.
  - `application.startup`: Inicialização da Evolution.
  - `call`: Chamadas de voz/vídeo.
- **Resposta Síncrona:**
  ```json
  {
    "status": "success",
    "received_events": 1
  }
  ```
- **Código HTTP:** `200 OK` (Latência média $\le 15\text{ms}$).

---

## 2. Endpoints REST do Frontend de Atendimento (DRF)

### 2.1 Despacho de Mensagem Outbound com Confirmação Estrita (Decisão D2: A)

- **Path:** `POST /api/v1/omnichannel/messages/`
- **Headers:** 
  - `Authorization: Bearer <JWT_ACCESS_TOKEN>`
  - `Content-Type: application/json`
- **Request Body (`MessageCreateSerializer`):**
  ```json
  {
    "conversation_id": "805d409a-54df-4791-bd1b-dbd1c6574a61",
    "content": "Olá! Sou o atendente humano, como posso te ajudar hoje?",
    "quoted_message_id": null,
    "media_type": "TEXT",
    "media_url": null
  }
  ```
- **Regra de Autorização (P07):**
  - Se `conversation.contact` tiver um `User` do sistema associado: O operador logado **DEVE** pertencer a uma das organizações desse usuário (`organization_id__in=authorized_orgs`).
  - Se `conversation.contact` for um `Contact` novo sem usuário: O contato e a conversa são associados automaticamente à Organização Padrão da plataforma (`organization_id = default_org.id`). Operadores membros da organização padrão (ou administradores/suporte) possuem acesso com filtro mandatório `organization_id`, satisfazendo 100% o Princípio P07.
- **Response `201 Created` (Confirmação da Evolution API recebida com sucesso):**
  ```json
  {
    "id": "1b4f6082-af6b-4e0a-aecd-86795e72695a",
    "conversation_id": "805d409a-54df-4791-bd1b-dbd1c6574a61",
    "external_id": "3EB0C421B07D5BFF6D9E34",
    "direction": "OUTBOUND",
    "content": "Olá! Sou o atendente humano, como posso te ajudar hoje?",
    "delivery_status": "SENT",
    "media_type": "TEXT",
    "media_url": null,
    "quoted_message": null,
    "sent_by_ai": false,
    "sender_user_id": "df96046c-13c6-45a5-b815-e05547ce6616",
    "timestamp": "2026-10-21T18:19:25.268000-04:00"
  }
  ```
- **Response `502 Bad Gateway` (Falha na Evolution API - Sem falso positivo no chat):**
  ```json
  {
    "error": "Falha no envio da mensagem pelo WhatsApp: Instância ai_control_ai-control desconectada na Evolution API.",
    "code": "EVOLUTION_DISCONNECTED"
  }
  ```

---

### 2.2 Listagem de Conversas com Suporte a Leads Globais vs. Usuários Restritos

- **Path:** `GET /api/v1/omnichannel/conversations/`
- **Headers:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Query Params:**
  - `status`: `ACTIVE_AI` | `ACTIVE_HUMAN` | `CLOSED` | `ARCHIVED`
  - `filter`: `all` | `unread` | `ai` | `mine` | `pinned` | `unassigned`
  - `search`: busca textual por nome do contato ou texto da mensagem
- **Response `200 OK` (Zero PII - Nome de exibição protegido):**
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "805d409a-54df-4791-bd1b-dbd1c6574a61",
        "organization_id": null,
        "contact": {
          "id": "3b4e7b42-f900-4fe5-acd7-b3919e5cda6d",
          "display_name": "André Silva",
          "avatar_url": null,
          "status": "PLATFORM_LEAD"
        },
        "status": "ACTIVE_AI",
        "assigned_user_id": null,
        "last_message_preview": "Olá, gostaria de saber informações sobre o curso",
        "last_message_timestamp": "2026-10-21T17:36:18Z",
        "unread_count": 1,
        "is_pinned": false,
        "channel_type": "WHATSAPP",
        "tags": []
      }
    ]
  }
  ```

---

## 3. Contratos de Conexão WebSocket e Canais em Tempo Real

- **Endpoint:** `ws://localhost:8000/ws/omnichannel/`
- **Autenticação Segura:**
  - Subprotocolo WebSocket: `Sec-WebSocket-Protocol: Bearer, <JWT_TOKEN>` (imune a vazamentos em logs de query string)
  - Fallback por Query Param: `?token=<JWT_TOKEN>&org_id=<UUID>` (com sanitização obrigatória no logger ASGI).
- **Grupos de Broadcast:**
  - Conversas de Organização: `private-org-{organization_id}`
  - Conversas Globais / Sem Organização: `private-global-leads` (consumido por operadores autorizados)
- **Evento: Nova Mensagem (`conversation.message.new`):**
  ```json
  {
    "event": "conversation.message.new",
    "data": {
      "conversation_id": "805d409a-54df-4791-bd1b-dbd1c6574a61",
      "message": {
        "id": "1b4f6082-af6b-4e0a-aecd-86795e72695a",
        "external_id": "3EB0C421B07D5BFF6D9E34",
        "direction": "OUTBOUND",
        "content": "Olá! Sou o atendente humano, como posso te ajudar hoje?",
        "delivery_status": "SENT",
        "timestamp": "2026-10-21T18:19:25Z"
      }
    }
  }
  ```
- **Evento: QR Code Atualizado (`whatsapp.qrcode.updated`):**
  ```json
  {
    "event": "whatsapp.qrcode.updated",
    "data": {
      "instance_name": "ai_control_ai-control",
      "qrcode_base64": "data:image/png;base64,iVBORw0KGgo..."
    }
  }
  ```

---

## 4. Contrato de Segurança de Rede (CORS e Logging - Decisão D3: A)

- **CORS Allowed Origins:**
  - `http://localhost:3000` (Frontend desenvolvimento padrão)
  - `http://127.0.0.1:3000` (Frontend IP loopback)
  - Expansão dinâmica via `CORS_ALLOWED_ORIGINS_ENV` configurável no `.env`.
- **Filtro de Logging ASGI / Daphne:**
  - Padrão de mascaramento regex: `(?i)(apikey|token|password|secret)=([^&\s]+)` $\rightarrow$ `\1=[REDACTED]`.
