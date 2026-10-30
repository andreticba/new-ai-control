<!-- plan.md | Vitalia SDD v0.6.0 | 22-10-2026 09:21:00(GMT-04:00) -->
> **plan.md | Vitalia SDD v0.6.0 | 22-10-2026 09:21:00(GMT-04:00)**

# Implementation Plan: 007-omnichannel-hardening

**Branch**: `007-omnichannel-hardening` | **Date**: 22-10-2026 | **Spec**: [specs/007-omnichannel-hardening/spec.md](spec.md)

---

## 1. Summary

Este plano estabelece o hardening estrutural, arquitetural e operacional do módulo Omnichannel e sua integração com a **Evolution API v2**, sanando de forma definitiva falhas críticas de segurança, concorrência e experiência de uso diagnosticadas em testes reais com smartphones:
1. **Blindagem e Mascaramento Preventivo de Segredos (P12):** Eliminação de vazamento de credenciais (`apikey`, senhas de banco/redis e tokens JWT) nas saídas de console do Django e Daphne através do middleware `SensitiveLogMaskingMiddleware` no pipeline ASGI/WSGI.
2. **Governança de Eventos na Borda do Webhook (P04):** Descarte imediato em tempo constante $O(1)$ de eventos de telemetria e ruído (`presence.update`, `contacts.set/update/upsert`, `chats.*`, `call`), silenciando o flood de logs e reduzindo em até 80% a sobrecarga de workers no Celery. Expansão simultânea do suporte acionável para `qrcode.updated`, `messages.update`, `messages.edited` e `messages.delete`.
3. **Isolamento Multitenant Estrito e Contatos Novos (P01 & P07):** Associação automática de contatos sem usuário prévio à Organização Padrão configurada (`DefaultOrganizationService.get_default_organization()`), garantindo `organization_id` válido e não-nulo, satisfazendo a obrigatoriedade de filtros por tenant em 100% das consultas ORM e permitindo atendimento sem barreiras por operadores autorizados.
4. **Despacho Outbound com Confirmação Estrita e Falha Atômica (D2):** Envio síncrono para a Evolution API (`POST /message/sendText/{instance}`) com timeout de 5.0s. A mensagem só é persistida no PostgreSQL e emitida via WebSocket após a confirmação inequívoca contendo `key.id`. Em caso de erro ou indisponibilidade, dispara `MessageDispatchError`, responde HTTP 502/400 e preserva o texto digitado na caixa de entrada do operador.
5. **Resolução de Conectividade Cross-Origin (CORS) e Pareamento Reativo (D3 & P02):** Unificação de origens locais (`localhost:3000` e `127.0.0.1:3000`) em `CORS_ALLOWED_ORIGINS` eliminando o "Network Error", e auto-fechamento do modal de pareamento em 1.5s após a transição para o estado `open`.
6. **Arquitetura Limpa e Anti-Monólitos (SRP):** Views DRF restritas a < 35 linhas, componentes frontend < 120 linhas, segregando regras em Service Layer e Custom Hooks dedicados.

> **Conformidade com a Pipeline SDD (P01 SDD Inviolability):** Este plano segue estritamente o ciclo `specify` (PASS) $\rightarrow$ `plan` (validação técnica) $\rightarrow$ `tasks` (próxima etapa mandatória) $\rightarrow$ `implement` $\rightarrow$ `converge`. Nenhuma linha de código será implementada sem o `tasks.md` aprovado. Domínio: Mensageria Corporativa / Hardening (Medical-Gate P09 N/A).

---

## 2. Technical Context

- **Language/Version:** Python 3.14 (Virtualenv `.venv`) / TypeScript 5.7+ (Node 20+)
- **Primary Dependencies:** Django 5.1+, `djangorestframework~=3.15`, `channels~=4.2`, `celery~=5.4`, `channels-redis~=4.2`, `redis~=7.0`, `django-cors-headers~=4.4`, `@tanstack/react-query^5.0`, Axios, TailwindCSS v4, Lucide-React
- **Storage:** PostgreSQL 16 (`ai-control_db`) com tabelas `omnichannel_contact`, `omnichannel_conversation`, `omnichannel_message`, `core_user` e `core_organization`. Redis 7 (`REDIS_URL` configurável para Celery Broker, Channel Layer e cache de debounce)
- **Testing:** `pytest`, `pytest-django`, `pytest-asyncio`, `pytest-cov`, `@testing-library/react`
- **Target Platform:** Web API Server (Daphne/ASGI + Celery) & Browser Cross-Platform (Desktop `h-dvh` e Mobile responsivo)
- **Performance Goals:**
  - Ingestão de webhook com descarte $O(1) \le 15\text{ms}$;
  - Despacho outbound com confirmação $\le 1200\text{ms}$ (timeout máximo de 5.0s);
  - Latência de auto-close do modal = 1.5s;
  - Zero falsos positivos de entrega no chat;
  - Zero segredos expostos nos logs do console.
- **Constraints:**
  - P07 Inviolável (filtros mandatórios de `organization_id` em toda query);
  - P12 Ativo (zero chaves em logs);
  - P01 Inviolável (implementação somente após `tasks.md` aprovado);
  - Single Responsibility Principle (SRP) estrito (< 35 linhas por método DRF, < 120 linhas por componente React).

---

## 3. Constitution Check & Gatekeepers (P00–P17)

Verificação detalhada contra os 18 princípios canônicos da Constituição Vitalia SDD v0.6.0:

- **P00 (Human Wellbeing First):** Atendido. Elimina a ansiedade do atendente humano causada por mensagens exibidas com checks azuis que nunca chegaram ao cliente, e garante feedback imediato com preservação de texto em falhas de rede.
- **P01 (SDD Pipeline Inviolability):** Atendido. O pipeline obrigatório é estritamente seguido (`specify` $\rightarrow$ `plan` $\rightarrow$ `tasks` $\rightarrow$ `implement` $\rightarrow$ `converge`). Nenhum arquivo de produção será alterado antes da geração e aprovação do `tasks.md`.
- **P02 (User-Centric Validation):** Atendido. Feedback síncrono no chat com retenção do input em caso de erro, modal reativo com auto-close de 1.5s e botão de atualização de QR Code sem necessidade de refresh manual.
- **P03 (External Verification & Grounding):** Atendido. Eventos da Evolution API v2, especificações de CORS (W3C Fetch) e middlewares Django fundamentados com URLs e evidências registradas em [research.md](research.md).
- **P04 (Timestamp GMT-04:00 & Qualidade):** Atendido. Todos os artefatos possuem cabeçalhos datados no fuso America/Cuiaba e a estrutura do código adota responsabilidade única (SRP).
- **P05 (Test-First & Regression Defense):** Atendido. Testes de unidade e integração previstos antes da implementação de cada componente novo, cobrindo cenários de sucesso e falha.
- **P06 (Secrets Never in Git):** Atendido. Chaves `WHATS_GT_*` mantidas exclusivamente no `.env` e parâmetros sensíveis redigidos de saídas de log.
- **P07 (Multitenancy Estrito & Data Isolation):** Atendido. Contatos novos associados à Organização Padrão (`DefaultOrganizationService`), garantindo `organization_id` válido e não-nulo em 100% das consultas ORM, impedindo vazamentos de tenant.
- **P08 / P12 (Agent Security & Credential Protection):** Atendido. Middleware `SensitiveLogMaskingMiddleware` higieniza requisições HTTP antes de logs do Daphne/Django e prioriza cabeçalho HTTP nativo `apikey`.
- **P09 (Clinical Safety & Domain Gates):** N/A para mensageria corporativa; módulo atua em camada de transporte de atendimento humano.
- **P10 (Didactic Engineering):** Atendido. Documentação clara e estruturada para operadores e desenvolvedores.
- **P11 (Hardware Agnosticism):** Atendido. Variáveis de ambiente configuráveis para broker Redis, URLs de serviço e provedores.
- **P13 (Safe Execution Boundaries):** Atendido. Timeouts estritos de 5.0s no despacho para evitar bloqueio de threads síncronas.
- **P14 (Full Audit Trail):** Atendido. Transições de conexão gravadas em `AuditLog` com debounce via cache Redis para prevenir flapping de status.
- **P15 (Observability & Structured Logging):** Atendido. Logs estruturados no Celery e telemetria sanitizada de latência e status HTTP.
- **P16 (Mermaid Defensive Syntax):** Atendido. Todos os diagramas utilizam rótulos entre aspas duplas prevenindo quebras de parser.
- **P17 (Regulatory Compliance / LGPD):** Atendido. Proteção contra vazamento de PII (JIDs e telefones higienizados nos logs de descarte e na interface).

---

## 4. Technical Decisions (ADRs)

### ADR-001: Governança de Organização Padrão e Multitenancy Estrito (P01 & P07)
- **Contexto:** Contatos orgânicos que enviam mensagens espontâneas pelo WhatsApp não possuem usuário pré-cadastrado no sistema. Permitir `organization_id=null` no banco de dados violaria o princípio P07 (Multitenancy Estrito) e impediria a aplicação de filtros combinados obrigatórios.
- **Decisão:** Criar o serviço `DefaultOrganizationService.get_default_organization()` que recupera a Organização Padrão da plataforma (via `DEFAULT_ORGANIZATION_ID` ou lookup idempotente da primeira organização ativa). Todo novo `Contact` e `Conversation` gerado por webhook recebe esse `organization_id`. Operadores com permissão nessa organização (ou administradores/suporte) atendem a conversa normalmente.
- **Fontes Verificadas:** https://github.com/andreticba/new-ai-control/blob/main/.agents/AGENTS.md em 22-10-2026.
- **Alternativas Rejeitadas:**
  - `organization_id = null`: Rejeitado por violar o isolamento de tenant P07 e abrir precedentes para consultas vazarem dados entre organizações.
  - Bloquear contato até cadastro de usuário: Rejeitado por impor atrito inaceitável a novos clientes.

### ADR-002: Despacho Outbound com Confirmação Estrita e Falha Atômica (D2)
- **Contexto:** Mensagens enviadas pelo chat podiam ser gravadas como `SENT` mesmo se a Evolution API falhasse ou estivesse desconectada, enganando o atendente.
- **Decisão:** O serviço `MessageDispatchService.dispatch_text_message` realiza uma chamada síncrona `POST /message/sendText/{instance}` com timeout de 5.0s. Apenas se a Evolution API responder `status_code in (200, 201)` contendo o identificador real do WhatsApp (`response['key']['id']`), a mensagem é persistida no PostgreSQL com `delivery_status=SENT` e emitida via WebSocket. Caso contrário, lança `MessageDispatchError`, responde HTTP 502/400 e preserva o texto digitado na caixa de entrada do operador.
- **Fontes Verificadas:** https://doc.evolution-api.com/v2/pt/api-reference/message/send-text em 22-10-2026.
- **Alternativas Rejeitadas:**
  - Persistência otimista com cancelamento assíncrono: Rejeitado pela complexidade de reversão e incerteza operacional para o atendente humano.

### ADR-003: Whitelist CORS Bilateral Local (D3)
- **Contexto:** O frontend acessado em `http://127.0.0.1:3000` recebia "Network Error" porque o backend só listava `http://localhost:3000` em `CORS_ALLOWED_ORIGINS`.
- **Decisão:** Adicionar formalmente tanto `http://localhost:3000` quanto `http://127.0.0.1:3000` em `CORS_ALLOWED_ORIGINS` e carregar origens adicionais via variável de ambiente `CORS_ALLOWED_ORIGINS_ENV`.
- **Fontes Verificadas:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS em 22-10-2026.
- **Alternativas Rejeitadas:**
  - `CORS_ALLOW_ALL_ORIGINS = True`: Rejeitado por representar vulnerabilidade crítica de segurança.

### ADR-004: Middleware de Mascaramento Preventivo de Segredos em Logs (P12)
- **Contexto:** Daphne e Django registram no console a URI completa de cada request HTTP, expondo `?apikey=sua_chave` e senhas em texto puro.
- **Decisão:** Desenvolver o middleware `SensitiveLogMaskingMiddleware` inserido no topo da pipeline de middlewares do Django. O middleware higieniza `request.META['QUERY_STRING']` e substitui parâmetros como `apikey=[REDACTED]`, além de incentivar o envio preferencial do cabeçalho `apikey`.
- **Fontes Verificadas:** https://docs.djangoproject.com/en/5.1/topics/http/middleware/ em 22-10-2026.
- **Alternativas Rejeitadas:**
  - Filtro apenas dentro da View: Rejeitado porque o servidor ASGI do Daphne loga a URI antes do roteamento da view.

### ADR-005: Descarte Silencioso O(1) de Telemetria e Expansão de Eventos (P04)
- **Contexto:** Eventos `presence.update` ("digitando...", "online") disparados continuamente pela Evolution API causavam enfileiramento massivo no Celery e flood de logs de warning.
- **Decisão:** Classificar eventos no webhook em duas categorias:
  - `SILENT_DROP_EVENTS`: `presence.update`, `contacts.*`, `chats.*`, `call` e `application.startup` são descartados imediatamente na View em $O(1)$ respondendo `HTTP 200 OK` em $\le 15\text{ms}$ sem enfileirar no Celery.
  - `ACTIONABLE_EVENTS`: `messages.upsert`, `messages.update`, `messages.edited`, `messages.delete`, `qrcode.updated` e `connection.update` são processados pelo Celery.
- **Fontes Verificadas:** https://github.com/EvolutionAPI/evolution-api em 22-10-2026.
- **Alternativas Rejeitadas:**
  - Desativar webhooks na Evolution API: Rejeitado porque outros eventos legítimos deixariam de ser recebidos.

### ADR-006: Pareamento Reativo com Auto-close e Debounce no AuditLog (P02 & P14)
- **Contexto:** O modal de pareamento não fechava sozinho após a leitura do QR Code pelo celular e oscilações momentâneas de rede geravam centenas de registros duplicados no `AuditLog`.
- **Decisão:** O frontend escuta o evento WebSocket `whatsapp.qrcode.updated` para atualizar o QR Code em tempo real e monitora a transição de estado da instância para `open`. Ao conectar, exibe badge verde e agenda auto-fechamento após 1.5s. No backend, `process_connection_update` utiliza cache Redis com chave de debounce (TTL 10s) para registrar no `AuditLog` somente quando houver mudança real e estável de estado.
- **Fontes Verificadas:** https://tanstack.com/query/latest/docs/react/overview em 22-10-2026.
- **Alternativas Rejeitadas:**
  - Polling a cada 2 segundos: Rejeitado por overhead excessivo de rede e CPU.

---

## 5. Project Structure

### Documentação da Feature
```text
specs/007-omnichannel-hardening/
├── spec.md                                # Requisitos Funcionais, Critérios de Sucesso e Cenários
├── plan.md                                # Este documento (Plano Técnico de Arquitetura)
├── research.md                            # Investigação, Causas-Raiz e ADRs fundamentadas
├── data-model.md                          # Ontologia de Contatos e Catálogo Oficial de Eventos
├── quickstart.md                          # Guia executável de validação de ponta a ponta
├── contracts/
│   └── hardening_api_contracts.md         # Contratos DRF, Webhook Evolution e WebSockets
└── checklists/
    └── requirements.md                    # Checklist de rastreabilidade de requisitos
```

### Código-Fonte Afetado
```text
config/
└── settings.py                            # Inclusão do SensitiveLogMaskingMiddleware e CORS_ALLOWED_ORIGINS

core/
├── middleware/
│   ├── __init__.py
│   └── sensitive_log_masking.py           # NOVO: Middleware de redação de segredos em logs HTTP
├── api/v1/views/
│   └── webhook_whatsapp.py                # Descarte silencioso O(1) e higienização de logs
└── services/
    └── whatsapp_service.py                # Debounce no process_connection_update para AuditLog

omnichannel/
├── api/
│   └── views.py                           # DRF Views magras (< 35 linhas) com filtro por organização
└── services/
    ├── __init__.py
    ├── default_organization_service.py     # NOVO: Resolução da Organização Padrão da plataforma
    └── message_dispatch_service.py        # Despacho síncrono com falha atômica e MessageDispatchError

frontend/
├── src/
│   ├── components/omnichannel/
│   │   ├── chat-container.tsx             # Preservação de texto no input em falhas de envio
│   │   └── whatsapp-modal.tsx             # Auto-close de 1.5s e atualização de QR Code
│   └── hooks/
│       ├── use-whatsapp-instance.ts       # Hook isolado para ciclo de vida da instância
│       └── use-omnichannel-socket.ts      # Suporte a websocket seguro e evento qrcode.updated
```

---

## 6. Phase Overview & Atomic Execution

### Phase 1: Setup & Middleware de Segurança
- **Objetivo:** Blindar os logs do servidor contra vazamento de segredos e liberar origens locais no CORS.
- **Artefatos:**
  - `core/middleware/sensitive_log_masking.py`: Intercepta requisições HTTP e mascara chaves sensíveis em query strings e bodies para o logger do Daphne/Django.
  - `config/settings.py`: Registra o middleware no início de `MIDDLEWARE` e adiciona `http://localhost:3000` e `http://127.0.0.1:3000` em `CORS_ALLOWED_ORIGINS`.
- **Testes:** Teste unitário enviando requisição com `?apikey=secret` e verificando que a string de log não contém o valor do segredo.

### Phase 2: Governança de Organização Padrão (P01 & P07)
- **Objetivo:** Garantir que todo contato e conversa possuam `organization_id` válido e não-nulo, satisfazendo P07.
- **Artefatos:**
  - `omnichannel/services/default_organization_service.py`: Cria `DefaultOrganizationService.get_default_organization()`.
  - `core/services/whatsapp_service.py`: Ao processar webhook de nova conversa/contato sem usuário, associa-o à organização padrão retornada pelo serviço.
  - `omnichannel/api/views.py`: Ajusta queries para que operadores da organização padrão e administradores listem e respondam a contatos sem erro 401 ou 404, mantendo o filtro mandatório `organization_id`.
- **Testes:** Teste de criação de contato espontâneo validando `assert contact.organization_id is not None`.

### Phase 3: Gateway de Webhooks & Descarte Silencioso O(1)
- **Objetivo:** Eliminar flood no Celery e estabilizar o gateway de webhook da Evolution API v2.
- **Artefatos:**
  - `core/api/v1/views/webhook_whatsapp.py`: Divide catálogo em `SILENT_DROP_EVENTS` e `ACTIONABLE_EVENTS`. Eventos de presença retornam `HTTP 200` imediatamente em $\le 15\text{ms}$. Sanitiza logs de descarte sem imprimir JIDs ou apikeys.
  - `core/services/whatsapp_service.py`: Implementa debounce com cache Redis (TTL 10s) para gravações em `AuditLog`.
- **Testes:** Teste disparando `presence.update` garantindo que o Celery não recebe tasks e latência $\le 15\text{ms}$.

### Phase 4: Despacho Outbound com Falha Atômica (Service Layer)
- **Objetivo:** Garantir que nenhuma mensagem falsa seja criada no banco se a Evolution API falhar.
- **Artefatos:**
  - `omnichannel/services/message_dispatch_service.py`: Refatora `dispatch_text_message` para chamada síncrona com timeout de 5.0s. Persiste `Message` com `SENT` e emite WebSocket somente após confirmação com `key.id`. Lança `MessageDispatchError` em falhas.
  - `omnichannel/api/views.py`: `MessageViewSet.create` captura `MessageDispatchError` e responde com `HTTP 502/400`, mantendo o método com < 35 linhas (SRP).
- **Testes:** Teste com mock de falha da Evolution API verificando que zero mensagens são persistidas no banco e resposta é 502.

### Phase 5: Frontend Hardening & Modal Reativo
- **Objetivo:** Melhorar a experiência do atendente no pareamento do WhatsApp e no envio de mensagens.
- **Artefatos:**
  - `frontend/src/components/omnichannel/whatsapp-modal.tsx`: Monitora WebSocket e transição para `state === 'open'`, exibindo badge verde e fechando o modal em 1.5s (`auto-close`). Adiciona botão de refresh de QR Code com invalidação de cache.
  - `frontend/src/components/omnichannel/chat-container.tsx`: Captura erros de envio HTTP 502/400, exibe toast de erro e preserva o texto digitado na caixa de entrada sem criar balão falso.
  - `frontend/src/hooks/use-omnichannel-socket.ts`: Trata evento `whatsapp.qrcode.updated` e gerencia subprotocolo de autenticação seguro.
- **Testes:** Teste de componente React simulando falha de envio e verificando que o texto permanece no input.

### Phase 6: Validação, Observabilidade & Testes End-to-End
- **Objetivo:** Validação integrada de todos os requisitos funcionais e critérios de sucesso.
- **Artefatos:**
  - Execução dos testes automatizados cobrindo os 5 cenários Given/When/Then.
  - Execução dos testes de regressão dos módulos existentes (`pytest tests/`).
  - Validação manual guiada pelo [quickstart.md](quickstart.md) com os containers Docker ativos.
