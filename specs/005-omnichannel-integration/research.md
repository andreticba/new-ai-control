<!-- research.md | Vitalia SDD v0.6.0 | 20-10-2026 17:31:00(GMT-04:00) -->
> **research.md | Vitalia SDD v0.6.0 | 20-10-2026 17:31:00(GMT-04:00)**

# Technical Research & Architecture Decisions: 005-omnichannel-integration

Este documento detalha o embasamento técnico e as decisões arquiteturais da integração Omnichannel, orientadas pela preservação estrita da infraestrutura operacional já em execução no projeto (`EvolutionGatewayService`, `WebhookGatewayView`, `WhatsAppService`, `omnichannel/models.py`), em total conformidade com o **Protocolo de Verificação Externa (P03)**, **Segurança de Dados e Segredos (P06)**, **Isolamento de Hardware (P11)** e **Observabilidade (P15)**.

---

## Decisão 1: Preservação Integral do Endpoint Canônico de Webhook `/api/v1/webhook/whatsapp/`

- **Escolhido**: Manter e estender o receptor existente em `core/api/v1/views/webhook_whatsapp.py`, sem alterar a URL de webhook configurada no `docker-compose.yml` (`WEBHOOK_GLOBAL_URL=${WHATS_GT_WEBHOOK_BASE_URL}/api/v1/webhook/whatsapp/?apikey=...`).
- **Verificado em**:
  - `https://doc.evolution-api.com/v2/pt-BR/` em 20-10-2026
  - `https://docs.celeryq.dev/en/stable/userguide/tasks.html` em 20-10-2026
- **Justificativa**: A infraestrutura atual já processa webhooks com validação de `WHATS_GT_API_KEY`, *silent drop* de `chats.set`/`chats.update` e despacho para `process_whatsapp_webhook_task.delay(event_item)` no Celery. Alterar a rota ou recriar o receptor do zero causaria regressão imediata no container `ai-control_evolution` que já está operando e quebrando 53 testes existentes.
- **Alternativas**:
  - *Criar nova rota paralela `/api/v1/omnichannel/webhook/evolution/`*: rejeitado porque duplicaria endpoints, causaria conflito de instâncias e exigiria reconfiguração arriscada do container em produção.

---

## Decisão 2: Aproveitamento dos Modelos Existentes em `omnichannel/models.py` com Blind Indexing

- **Escolhido**: Reutilizar as tabelas vigentes `omnichannel_contact`, `omnichannel_contactphonenumber`, `omnichannel_conversation`, `omnichannel_message` e adicionar apenas a entidade não-destrutiva `CopilotDraft`. O blind index com `phone_hash` gerado por `core.utils.generate_phone_hash` já está presente e ativo em `ContactPhoneNumber`.
- **Verificado em**:
  - `https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm` (LGPD Art. 13 e 46) em 20-10-2026
  - `https://owasp.org/www-project-top-10/` (Cryptographic Failures) em 20-10-2026
- **Justificativa**: Respeita a integridade do banco de dados relacional e as migrações já aplicadas, preservando o histórico de contatos e conversas sem executar migrações destrutivas.
- **Alternativas**:
  - *Refatorar ou recriar a estrutura de tabelas*: rejeitado por violar o princípio de estabilidade e arriscar perda de dados pré-existentes.

---

## Decisão 3: Notificação em Tempo Real via Django Channels e Cache TanStack Query v5

- **Escolhido**: Conectar o frontend React 19 ao Django Channels (`channels_redis` no Redis DB 1 via `WHATS_GT_CHANNELS_REDIS_URL`) utilizando o Channel Layer já acionado por `WhatsAppService.process_message_upsert` (`group_send`), complementando com eventos de status de conversa e drafts de copiloto.
- **Verificado em**:
  - `https://channels.readthedocs.io/en/latest/` em 20-10-2026
  - `https://tanstack.com/query/v5/docs/framework/react/guides/optimistic-updates` em 20-10-2026
- **Justificativa**: O Channel Layer já existe no backend (`WHATS_GT_CHANNELS_REDIS_URL`), bastando prover o consumer autenticado e conectar os hooks do TanStack Query v5 para sincronização otimista de tela.
- **Alternativas**:
  - *Polling via requisições HTTP*: rejeitado por sobrecarregar o banco com consultas desnecessárias.

---

## Decisão 4: Modelo de Atendimento Híbrido com Trava Anti-Colisão (Takeover)

- **Escolhido**: Utilizar a máquina de estados existente em `Conversation.Status` (`ACTIVE_AI`, `ACTIVE_HUMAN`, `CLOSED`). Ao acionar o endpoint de Takeover, a conversa transiciona para `ACTIVE_HUMAN` com `assigned_user_id = user.id`. Em `ACTIVE_HUMAN`, o pipeline de auto-resposta da IA é desativado para essa conversa, ativando a geração preditiva assíncrona de `CopilotDraft`.
- **Verificado em**:
  - `https://owasp.org/www-project-top-10-for-large-language-model-applications/` (LLM08: Excessive Agency) em 20-10-2026
- **Justificativa**: Evita colisão entre operador humano e robô de auto-atendimento, conferindo soberania total ao atendente conforme os princípios P00 e P02.
- **Alternativas**:
  - *Intervenção sem trava de estado*: rejeitado porque o bot continuaria respondendo em paralelo ao operador.

---

## Decisão 5: Layout WhatsApp Web Clone com Viewport Fixo `h-dvh` e Adaptação Cross-Device

- **Escolhido**: Interface no frontend React 19 em viewport fixo `h-dvh` com 3 colunas articuladas (Lista, Timeline, Drawer CRM) no desktop, e transição para navegação em pilha (drill-down) no tablet/mobile, consumindo as novas views DRF de conversas e mensagens.
- **Verificado em**:
  - `https://www.w3.org/TR/css-values-4/#viewport-relative-lengths` (Dynamic Viewport Height `dvh`) em 20-10-2026
  - `https://tailwindcss.com/docs` em 20-10-2026
- **Justificativa**: Atualmente o frontend possui apenas telas de workspace/login. A adição do módulo de chat em `h-dvh` provê experiência idêntica ao WhatsApp Web sem rolagem de janela e com tempo de adaptação zero para os operadores.
