<!-- quickstart.md | Vitalia SDD v0.6.0 | 22-10-2026 06:13:00(GMT-04:00) -->
> **quickstart.md | Vitalia SDD v0.6.0 | 22-10-2026 06:13:00(GMT-04:00)**

# Quickstart & Verification Guide: 007-omnichannel-hardening

Este guia estabelece os procedimentos passo a passo para validar as correções de hardening do módulo Omnichannel e sua integração com a Evolution API v2.

---

## 1. Pré-requisitos do Ambiente

Certifique-se de que os serviços essenciais estão em execução:

```bash
# Verificar status dos containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Esperado:
# ai-control_evolution_api   Up ...   0.0.0.0:8081->8080/tcp
# ai-control_redis           Up ...   0.0.0.0:6379->6379/tcp
# ai-control_db              Up ...   0.0.0.0:5432->5432/tcp
```

---

## 2. Cenário 1: Validação de Mascaramento de Chaves em Logs (P12)

**Objetivo:** Garantir que requisições contendo parâmetros sensíveis não imprimam chaves em texto plano.

1. Envie uma requisição de teste simulando a query string com apikey:
   ```bash
   curl -s -X POST "http://localhost:8000/api/v1/webhook/whatsapp/?apikey=sua_apikey_global_secreta" \
     -H "Content-Type: application/json" \
     -d '{"event":"presence.update","data":{"id":"556599999999@s.whatsapp.net","presences":{}}}'
   ```
2. Inspecione a saída do servidor Django/Daphne:
   - **Resultado Esperado:** A URL registrada nos logs deve conter `?apikey=[REDACTED]` e a resposta HTTP deve ser `200 OK` em $\le 15\text{ms}$.

---

## 3. Cenário 2: Descarte Silencioso de Telemetria no Celery (P04)

**Objetivo:** Confirmar que eventos de presença não inundam a fila do Celery.

1. Dispare evento `presence.update` e observe os workers do Celery:
   ```bash
   # Em outro terminal:
   celery -A config worker -l INFO
   ```
2. **Resultado Esperado:** 
   - O worker do Celery **NÃO** deve receber tarefas para `presence.update`.
   - O console permanece silencioso e sem flood de mensagens.

---

## 4. Cenário 3: Despacho Outbound com Falha Atômica (D2)

**Objetivo:** Garantir que nenhuma mensagem falsa seja criada no banco se a Evolution API falhar.

1. Tente enviar uma mensagem para uma conversa com a instância desconectada ou forçando um erro de rede.
2. Inspecione o banco de dados e a interface do chat:
   - **Resultado Esperado:**
     - A API responde com `HTTP 502 Bad Gateway` com payload descritivo.
     - Nenhuma linha é inserida na tabela `omnichannel_message` como `SENT`.
     - O frontend exibe toast de erro e preserva o texto digitado na caixa de entrada sem criar balão falso.

---

## 5. Cenário 4: Pareamento Reativo com Auto-fechamento (P02)

**Objetivo:** Confirmar que o modal fecha sozinho após autenticação do WhatsApp.

1. Abra a tela de Omnichannel (`http://localhost:3000/omnichannel`) e clique em "Conectar WhatsApp".
2. Leia o QR Code com o aplicativo WhatsApp no smartphone.
3. **Resultado Esperado:**
   - O badge atualiza imediatamente para "Conectado" em verde.
   - O modal se fecha automaticamente em 1.5 segundos sem necessidade de recarregar a página.

---

## 6. Cenário 5: Associação de Novo Contato à Organização Padrão (P07)

**Objetivo:** Confirmar que novos números espontâneos não violam a restrição multitenant.

1. Envie uma mensagem pelo WhatsApp a partir de um número nunca antes cadastrado no sistema.
2. Inspecione a tabela `omnichannel_conversation`:
   ```bash
   python manage.py shell -c "
   from omnichannel.models import Conversation
   latest = Conversation.objects.order_by('-created_at').first()
   print('Conversation ID:', latest.id, '| Organization ID:', latest.organization_id)
   assert latest.organization_id is not None, 'Falha: organization_id não pode ser nulo!'
   print('✅ Sucesso: Organização associada corretamente.')
   "
   ```
3. **Resultado Esperado:** `organization_id` preenchido com a Organização Padrão da plataforma e operador de suporte visualiza o chat sem erro 401 ou 404.
