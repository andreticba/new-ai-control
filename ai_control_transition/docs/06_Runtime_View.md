<!-- 06_Runtime_View.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 6. Runtime View

## Cenário 1: Ingestão de Dados via Webhook

1. **Ator Externo** (Ex: Gateway de Mensagens) faz um HTTP POST para `/api/v1/webhook/`.
2. **`WebhookGatewayView`** intercepta a requisição.
   - Verifica cabeçalho `apikey`. Se inválido: Retorna `401 Unauthorized`.
   - Se evento for silencioso (ex: `chats.set`), aplica *Silent Drop* e retorna `200 OK`.
3. A View embala o payload e aciona `process_whatsapp_webhook_task.delay(payload)`.
4. A View retorna `200 OK` imediatamente ao parceiro (SLA garantido).
5. **Celery Worker** (Assíncrono) captura a task.
   - Descriptografa dados do Vault.
   - Realiza inserções vetoriais ou chamadas de LLM.
   - Atualiza a base de dados via ORM de forma transacional.

## Cenário 2: Streaming de Atualizações de Privacidade

1. Cliente B2B conecta-se via **WebSocket** em `/ws/tenant/updates/`.
2. O servidor `Daphne` promove a conexão HTTP para WS e autentica.
3. Quando um usuário final revoga um consentimento, o backend altera o banco de dados.
4. Um sinal (Signal) no Django aciona o `channels_redis`.
5. O grupo de WebSocket recebe o evento de push em tempo real avisando da restrição, removendo os dados imediatamente da tela.

