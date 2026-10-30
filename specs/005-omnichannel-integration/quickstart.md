<!-- quickstart.md | Vitalia SDD v0.6.0 | 20-10-2026 17:30:40(GMT-04:00) -->
> **quickstart.md | Vitalia SDD v0.6.0 | 20-10-2026 17:30:40(GMT-04:00)**

# Quickstart & End-to-End Validation Guide: 005-omnichannel-integration

Este guia fornece passos determinísticos para validar localmente a ingestão de webhooks da Evolution API v2 no endpoint canônico em execução, a triagem com transição de estados e a assistência pelo Copiloto de IA.

---

## 1. Pré-Requisitos do Ambiente Local

Certifique-se de que os containers Docker da stack (`ai-control_db`, `ai-control_redis`, `ai-control_evolution`, `ai-control_ollama`) estão saudáveis:
```bash
docker compose ps
```

---

## 2. Cenário 1: Ingestão de Webhook Inbound no Endpoint Canônico

Dispara evento `messages.upsert` na rota oficial de webhook `/api/v1/webhook/whatsapp/`:

```bash
curl -X POST "http://localhost:8000/api/v1/webhook/whatsapp/?apikey=sua_apikey_global_secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "ai_control_default",
    "data": {
      "key": {
        "remoteJid": "5565999887766@s.whatsapp.net",
        "fromMe": false,
        "id": "EVL-MSG-TEST-001"
      },
      "pushName": "Carlos Silva",
      "message": {
        "conversation": "Olá, gostaria de saber os horários de atendimento."
      },
      "messageTimestamp": 1729459200
    }
  }'
```

**Resultado Esperado:**
- Resposta HTTP `200 OK` (`{"status": "success"}`) em $P95 \le 200\text{ms}$.
- Processamento assíncrono via `process_whatsapp_webhook_task` no Celery.
- Criação/recuperação do `Contact` e `ContactPhoneNumber` em `omnichannel/models.py`.
- Criação da `Conversation` no estado `ACTIVE_AI` e persistência de `Message(direction='INBOUND')`.

---

## 3. Cenário 2: Takeover do Atendente Humano (Operador Assume o Chat)

O operador na interface assume a conversa, alterando o status para `ACTIVE_HUMAN`:

```bash
curl -X POST http://localhost:8000/api/v1/omnichannel/conversations/<CONVERSATION_ID>/takeover/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SEU_JWT_TOKEN>"
```

**Resultado Esperado:**
- Status atualizado para `ACTIVE_HUMAN` com `assigned_user_id` preenchido.
- O bot de resposta automática direta é pausado para essa conversa.
- Evento WebSocket emitido no Channel Layer para atualização dinâmica na lista de chats.

---

## 4. Cenário 3: Geração de Copilot Draft e Aprovação de 1-Clique

Com a conversa em `ACTIVE_HUMAN`, uma nova mensagem do cliente gera uma sugestão do copiloto:

```bash
# Ingestão de nova mensagem inbound do cliente
curl -X POST "http://localhost:8000/api/v1/webhook/whatsapp/?apikey=sua_apikey_global_secreta" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "ai_control_default",
    "data": {
      "key": {
        "remoteJid": "5565999887766@s.whatsapp.net",
        "fromMe": false,
        "id": "EVL-MSG-TEST-002"
      },
      "pushName": "Carlos Silva",
      "message": {
        "conversation": "Qual o endereço da unidade central?"
      },
      "messageTimestamp": 1729459260
    }
  }'
```

**Resultado Esperado:**
- Nenhuma resposta enviada ao WhatsApp sem aprovação humana.
- A tarefa Celery `generate_copilot_draft_task` gera o draft via Ollama (`phi4-mini:latest`) em $P90 \le 3.5\text{s}$.
- Evento WebSocket `copilot.draft.generated` recebido na tela do atendente.
- Operador aprova a sugestão:
  ```bash
  curl -X POST http://localhost:8000/api/v1/omnichannel/copilot-drafts/<DRAFT_ID>/approve/ \
    -H "Authorization: Bearer <SEU_JWT_TOKEN>"
  ```
- Mensagem despachada para o WhatsApp do cliente através de `EvolutionGatewayService.send_message(...)`.

---

## 5. Cenário 4: Execução da Suíte de Testes Automatizados (TDD)

Executa a suíte de testes de mensageria preservando todos os testes já existentes:

```bash
pytest tests/core/test_evolution_gateway.py core/tests/test_webhook_gateway.py apps/omnichannel/tests/ -v
```
