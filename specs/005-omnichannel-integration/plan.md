<!-- plan.md | Vitalia SDD v0.6.0 | 20-10-2026 18:03:00(GMT-04:00) -->
> **plan.md | Vitalia SDD v0.6.0 | 20-10-2026 18:03:00(GMT-04:00)**

# Implementation Plan: 005-omnichannel-integration

**Branch**: `005-omnichannel-integration` | **Date**: 20-10-2026 | **Spec**: [spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/spec.md)

---

## 1. Summary

Evolução não-destrutiva do módulo Omnichannel no `ai-control`, conectando o ecossistema WhatsApp em execução à nova interface corporativa no frontend React 19. A arquitetura **preserva integralmente** o gateway ativo ([core/services/evolution_gateway.py](file:///home/andre/projetos/assistidos/ai-control/core/services/evolution_gateway.py)), o webhook em `/api/v1/webhook/whatsapp/` ([core/api/v1/views/webhook_whatsapp.py](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/webhook_whatsapp.py)), variáveis `WHATS_GT_*`, modelos em [omnichannel/models.py](file:///home/andre/projetos/assistidos/ai-control/omnichannel/models.py) e os 53 testes vigentes, agregando:
1. Endpoints REST DRF de consulta e Takeover Humano (`ACTIVE_AI` $\leftrightarrow$ `ACTIVE_HUMAN`);
2. Eventos WebSocket via Channel Layer (`channels_redis`);
3. Modelo complementar `CopilotDraft` com geração assíncrona de sugestões;
4. Interface inspirada no WhatsApp Web em viewport fixo `h-dvh` com responsividade mobile no React 19;
5. **Blindagem de PII:** Telefones **NÃO** são exibidos na interface, sendo substituídos exclusivamente por Nome de Exibição (`whatsapp_push_name` / `full_name`) e Foto (`avatar_url`).

> **Conformidade com a Pipeline SDD (P01 SDD Inviolability):** Este plano segue estritamente o ciclo `specify` (PASS) $\rightarrow$ `plan` (validação técnica) $\rightarrow$ `tasks` (próxima etapa mandatória) $\rightarrow$ `implement` $\rightarrow$ `converge`. **Nenhuma linha de código será implementada sem o `tasks.md` aprovado**. Domínio: Mensageria Corporativa / CRM (Medical-Gate P09 N/A).

---

## 2. Technical Context

- **Language/Version**: Python 3.14 (Virtualenv `.venv`) / TypeScript 5.x (Node 20+)
- **Primary Dependencies**: Django 6.1, `djangorestframework~=3.18.3`, `celery>=5.3`, `channels>=4.1`, `channels-redis>=4.2`, `redis>=5.0`, `@tanstack/react-query^5.0`, TailwindCSS v4, Lucide-React
- **Storage**: PostgreSQL 16 (`ai-control_db`) com tabelas de `omnichannel` e índice `phone_hash`. Redis 7 (DB 0: Cache, DB 1: Channels, DB 2: Celery Broker)
- **Testing**: `pytest`, `pytest-django`, `pytest-asyncio`, `pytest-cov`, `@testing-library/react`
- **Target Platform**: Web API Server (Daphne/ASGI + Celery) & Browser Cross-Platform (Desktop `h-dvh` e Mobile/Tablet responsivo)
- **Project Type**: Full-Stack Enterprise Web Application
- **Performance Goals**: Ingestão de Webhook $P95 \le 200\text{ms}$; Sugestão do Copiloto $P90 \le 3.5\text{s}$; 60 FPS na UI; Zero regressões nos 53 testes vigentes
- **Constraints**: Host NVIDIA GTX 1060 6GB (`OLLAMA_FLASH_ATTENTION=0`, modelo `phi4-mini:latest`); PII blindada (sem telefones na UI, HMAC-SHA256 no banco); P01 Inviolável (implementação somente após `tasks.md`)

---

## 3. Constitution Check & Gatekeepers

- **P00 (Human Wellbeing):** Soberania humana garantida por Takeover imediato e aprovação de 1-clique em drafts de IA.
- **P01 (SDD Pipeline Inviolability):** Pipeline obrigatório respeitado (`specify` $\rightarrow$ `plan` $\rightarrow$ `tasks` $\rightarrow$ `implement` $\rightarrow$ `converge`). Nenhum código sem `tasks.md`. Medical-Gate P09 N/A.
- **P02 (User-Centric Validation):** Interface idêntica ao WhatsApp Web, eliminando atrito cognitivo e tempo de treinamento.
- **P03 (External Verification):** Decisões fundamentadas em fontes autoritativas registradas em [research.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/research.md).
- **P04 (Timestamp GMT-04:00):** Cabeçalhos datados e sincronizados no fuso America/Cuiaba.
- **P06 (Secrets Never in Git):** Credenciais e chaves `WHATS_GT_*` mantidas exclusivamente no `.env`.
- **P07 (Zero Data Leak / PII):** Telefone proibido em tela; identidade visual por Nome de Exibição e Avatar.
- **P11 (Hardware Agnosticism):** Modelos LLM configuráveis dinamicamente via `.env` (`OLLAMA_MODEL=phi4-mini:latest`).
- **P15 (Observability & Logging):** Filas Celery com structured logging e monitoramento de latência.
- **P16 (Mermaid Defensive):** Labels entre aspas duplas prevenindo falhas de parser.

---

## 4. Technical Decisions (ADRs)

- **ADR-001 (Preservação do Webhook Canônico `/api/v1/webhook/whatsapp/`):** Manutenção de `WebhookGatewayView` com despacho para Celery, preservando integração do `docker-compose.yml` e testes. *Verificado em: `https://doc.evolution-api.com/v2/pt-BR/`.*
- **ADR-002 (Extensão Não-Destrutiva dos Modelos):** Reutilização de `Contact`, `ContactPhoneNumber`, `Conversation` e `Message`, adicionando campos aditivos (`external_id`, `delivery_status`, `media_*`, `quoted_message`, `sender_user_id`, `unread_count`, `avatar_url`, `whatsapp_push_name`) e `CopilotDraft`. *Verificado em: `https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm`.*
- **ADR-003 (WebSockets via Django Channels e Cache TanStack Query v5):** Conexão ao Channel Layer (`WHATS_GT_CHANNELS_REDIS_URL`) com broadcast por tenant e atualização otimista de tela. *Verificado em: `https://channels.readthedocs.io/en/latest/`.*
- **ADR-004 (Triagem Determinística e Trava Anti-Colisão de Takeover):** Bloqueio atômico de auto-respostas da IA quando `Conversation.status == ACTIVE_HUMAN`, ativando sugestões do copiloto. *Verificado em: `https://owasp.org/www-project-top-10-for-large-language-model-applications/`.*
- **ADR-005 (Interface WhatsApp Web Clone em Viewport Fixo `h-dvh`):** Frontend React 19 em viewport fixo `h-dvh` com 3 colunas (desktop) e suporte mobile/tablet responsivo. *Verificado em: `https://www.w3.org/TR/css-values-4/#viewport-relative-lengths`.*

---

## 5. Project Structure

- **Documentação:** `spec.md`, `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, `plan.md`.
- **Código Preservado:** `core/api/v1/views/webhook_whatsapp.py`, `core/services/evolution_gateway.py`, `core/services/whatsapp_service.py`, `omnichannel/models.py`.
- **Extensões:** `omnichannel/models.py` (campos aditivos e `CopilotDraft`), `omnichannel/api/` (views DRF e serializers), `omnichannel/consumers/` (WebSocket), `src/app/(dashboard)/omnichannel/page.tsx` (frontend React 19).

---

## 6. Phase Overview & Atomic Execution

- **Phase 1: Setup & Data Foundations:** Adicionar extensões em `omnichannel/models.py` (`external_id`, `delivery_status`, `media_*`, `quoted_message`, `sender_user_id`, `unread_count`, `avatar_url`, `whatsapp_push_name`, `CopilotDraft`), gerar migração aditiva e validar compatibilidade.
- **Phase 2: REST API & Real-Time Engine:** Desenvolver ViewSets DRF de conversas/mensagens com filtros (sem expor PII) e consumer WebSocket no Channel Layer.
- **Phase 3: US1 — Triagem Determinística e Takeover Humano:** Endpoints de Takeover e devolução para IA com bloqueio de auto-respostas em `ACTIVE_HUMAN`.
- **Phase 4: US2 — Copilot de Atendimento Preditivo com IA:** Task Celery de geração de drafts contextuais via Ollama (`phi4-mini:latest`) e WebSocket `copilot.draft.generated`.
- **Phase 5: US3 — Interface de Atendimento WhatsApp Web Clone:** Telas React 19 em viewport `h-dvh` com 3 colunas (desktop) e suporte mobile com TanStack Query v5.
- **Phase 6: Polish, Observabilidade & Testes End-to-End:** Execução integrada dos 53 testes existentes + novos testes de API e componentes, garantindo cobertura $\ge 90\%$.
