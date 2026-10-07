<!-- 03_System_Scope_and_Context.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 3. System Scope and Context

## 3.1 Contexto de Negócio
O sistema age como um núcleo centralizador (Vault). Ele fica posicionado entre os **Canais de Interação** (WhatsApp, APIs parceiras, Web Apps) e os **Serviços de Terceiros** (Motores de LLM, Gateways de Pagamento).

Sua principal fronteira de responsabilidade é atuar como "guardião" das mensagens e perfis: tudo o que entra é higienizado, validado criptograficamente e processado assincronamente.

## 3.2 Contexto Técnico (Interfaces Externas)
A plataforma possui as seguintes fronteiras de comunicação:

1. **SaaS Message Gateways (Evolution API):**
   - Recebe requisições via `WebhookGatewayView` (Webhooks).
   - O payload original é roteado e armazenado em segurança.
2. **LLM Providers (OpenAI, Gemini, Ollama):**
   - Comunicação via API abstraída pelo `AIIngestionDelegator`.
   - **Regra de Escopo:** Dados de PII (Personally Identifiable Information) *não* devem ser transmitidos aos provedores de LLM. Os dados devem ser ofuscados no Vault antes da requisição.
3. **Clients (WebSockets / Frontend):**
   - Canais WebSocket baseados em `daphne` e `channels-redis` para streaming de eventos em tempo real aos clientes (painéis de controle).

