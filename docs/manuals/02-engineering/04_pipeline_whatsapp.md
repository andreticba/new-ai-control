<!-- 04_pipeline_whatsapp.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# 04. Pipeline WhatsApp e Channels
**Público-alvo:** Desenvolvedores Backend / Integrações
**Tempo de Leitura:** 6 min

O processo de envio e recebimento via WhatsApp Evolution Gateway é o coração do CRM da Plataforma. Ele mescla Webhooks síncronos da internet com processamento em filas assíncronas do Celery.

## 1. Fluxo de Recebimento de Mensagem (Inbound) ✅

1. **`core.api.v1.views.webhook_whatsapp`**: A classe `WebhookGatewayView` escuta eventos do Gateway e valida a API Key e silenciosamente descarta eventos `chats.set` em $O(1)$ sem encher log.
2. Roteia os dados atômicos brutos (`payload`) chamando de forma assíncrona o `process_whatsapp_webhook_task.delay(event_item)` (Celery).
3. **`core.tasks.whatsapp_tasks.process_whatsapp_webhook_task`**: Ocorre o isolamento do tenant. O Gateway foi forçado a usar um prefixo de instância (ex: `ai_control_ufdemo`). Este Celery worker quebra a string da instância, descobre que o slug da organização é `ufdemo` e injeta este parâmetro.
4. **`core.services.whatsapp_service`**:
   - Cria-se a `Organization` local, se não existir.
   - Cria o `Contact` e amarra o número `ContactPhoneNumber`.
   - Localiza/Inicia uma `Conversation` na Organização com o status "Atendida pela IA".
   - Grava a `Message` no Postgres.
   - Dispara uma transmissão assíncrona (Broadcast) via Websockets com `django-channels` (com PIIs truncados) para que a interface de Inbox no front-end exiba o balão de mensagem imediatamente para todos os atendentes.

## 2. A Ingestão da IA e Limitações do Squad 🟡 / 🧭

Após salvar a mensagem, o fluxo do WhatsApp Service faz um `AIIngestionDelegator.delay(payload)`.
- **Status (Design de Referência):** A task `AIIngestionDelegator` (do Celery) é apenas um mock vazio `pass`. A inteligência artificial ainda não toma conta do chat ativamente.
- **Limitação de Contexto SQUAD:** Atualmente, a conversa pertence a uma `Organization` e tem a visibilidade baseada nela. O roteamento imediato de uma conversa para uma SQUAD fechada com filtro restritivo de leitura **ainda não existe em código real**, as lógicas deverão evoluir para que uma `Conversation` pertença a um `Project` ou `Squad` permitindo um RBAC ainda mais forte.

## Laboratório Recomendado
Acesse o laboratório de inicialização para visualizar esta criação no terminal e verificar a simulação do Evento, da Fila e a persistência final sem poluir a Web:
`python manage.py shell < docs/manuals/02-engineering/labs/lab_04_whatsapp_pipeline.py`
