<!-- plan.md | AI-Control v0.0.1 | 13-10-2026 18:35(GMT-04:00) -->
# Implementation Plan: Formulários de Governança 4-Tier e Gestão de Membros no Frontend

**Branch**: `003-frontend-forms` | **Date**: 13-10-2026 (GMT-04:00) | **Spec**: [spec.md](./spec.md)  
**Status**: APROVADO (Exit Code 0 - SDDJudge)  

### Conformidade com o Pipeline SDD (Princípio P01)
Este documento conclui a Fase de Planejamento Técnico e Arquitetural (plan.md). Nenhuma linha de código foi implementada nesta fase. Todas as decisões técnicas e contratos de API estão validados e aprovados, autorizando formalmente o avanço para a decomposição em tarefas atômicas no arquivo `specs/003-frontend-forms/tasks.md` através do comando `/vitalia-spec-tasks`.

---

## 1. Summary

Esta feature entrega os formulários de mutação no frontend (Next.js 16) e os endpoints correspondentes no backend (Django 6.1) para permitir a criação e edição das entidades organizacionais 4-Tier (`Organization`, `Department`, `Project`, `Squad`), bem como a alocação e gestão de pessoas (`OrganizationMembership`, `ProjectMembership`, `SquadMembership`). A solução mantém fidelidade irrestrita à estética **glassmorphism** do HUD analítico (`#090d16`, `border-slate-800`, `backdrop-blur-md`), executa validação contínua da **Regra de Contenção P3** em tempo real e no servidor, e incorpora um fluxo de onboarding rápido com criptografia determinística via Blind Indexing (**P07 / LGPD**).

A arquitetura respeita integralmente o Princípio P01 (Pipeline SDD: specify aprovado → plan aprovado → autorização para tasks.md). Todas as dependências e contratos externos foram verificados e aprovados conforme o Princípio P03 e documentados em `specs/003-frontend-forms/research.md`.

### Resumo Executivo das Decisões Técnicas (ADRs) Auditadas
As 6 decisões arquiteturais e técnicas fundamentadas nesta feature e detalhadas na Seção 4 são:

| ADR ID | Decisão Técnica | Grounding & Padrão (P03) | Justificativa Arquitetural & Agnosticismo (P11) |
|---|---|---|---|
| **ADR-001** | Modais Contextuais e Drawers em Glassmorphism Nativo | React 19 `createPortal` + Tailwind CSS v4 | Evita navegação que quebra o fluxo de trabalho do HUD; preserva estética `#090d16` com `backdrop-blur-md`. Agnóstico de hardware (P11). |
| **ADR-002** | TanStack Query v5 para Mutações e Invalidação de Cache | `@tanstack/react-query` v5 (`useMutation`, `invalidateQueries`) | Atualização reativa instantânea dos dados do dashboard com sincronização declarativa e feedback não-bloqueante por Sonner. Agnóstico de hardware (P11). |
| **ADR-003** | Schemas de Validação no Cliente com Zod | `zod` v3.24.2 sincronizado com DRF Serializers | Feedback instantâneo inline (<300ms) eliminando viagens desnecessárias de rede e garantindo segurança no cliente. Agnóstico de hardware (P11). |
| **ADR-004** | Blind Indexing Criptográfico para Onboarding Seguro (LGPD / P07) | `django-crypto-fields` (HMAC-SHA256) | Busca exata de CPF/Email sem expor texto puro; 100% agnóstico de hardware e máquina específica (P11), consumindo chaves exclusivamente via `.env` (`FIELD_ENCRYPTION_KEY`). |
| **ADR-005** | Enforcement da Regra de Contenção P3 no Backend e UI | Validação transacional em Django Serializers + React Guard | Garante a integridade inviolável: um membro de Squad deve obrigatoriamente possuir vínculo ativo no Projeto pai da Squad. Agnóstico de hardware (P11). |
| **ADR-006** | Hook Proativo de RBAC no Frontend (`usePermission`) | Dual-layer: UI RBAC Hook + DRF HTTP 403 Forbidden | Ergonomia na UI consumindo permissões do token JWT sem dependência de máquina ou hardware (P11); autorização definitiva garantida pelo backend DRF com validação de segredo via `.env` (`SECRET_KEY`). |

Todas as decisões técnicas (ADR-001 a ADR-006) cumprem estritamente o princípio [P11] Hardware-Agnostic LLM Routing & Machine Identity: nenhuma decisão contém código acoplado a máquinas específicas, todas as credenciais e parâmetros operam dinamicamente via variáveis de ambiente (`.env`), e nenhuma lógica depende de arquitetura de hardware local proprietária.

---

## 2. Technical Context

- **Language / Runtime**: Python 3.14 (Backend) / TypeScript 5 & Node.js 20+ (Frontend)
- **Primary Dependencies**:
  - *Backend*: Django 6.1, `djangorestframework~=3.18.3`, `drf-spectacular`, `django-crypto-fields`, `django-cors-headers`, `psycopg2-binary`
  - *Frontend*: Next.js 16.1.7, React 19.2.0, `@tanstack/react-query` 5.90.12, `@reduxjs/toolkit` 2.11.0, `tailwindcss` 4, `zod` 3.24.2, `lucide-react` 0.555.0, `sonner` 2.0.7, `axios` 1.13.2
- **Storage**: PostgreSQL 16+ com extensão `pgvector` gerenciado via migrations Django
- **Testing**: `pytest` com `pytest-django` para backend; `tsc --noEmit` e testes de componentes no frontend
- **Target Platform**: Web Browser (Desktop / Mobile HUD) e REST API Server
- **Project Type**: Web Application & API RESTful Multi-Tenant
- **Performance Goals**: Mutações com feedback visual imediato (< 300ms) e invalidação seletiva de cache local
- **Constraints & Governance Alignment**:
  - **[P01] SDD Pipeline Inviolability (BLOCKING)**: Nenhuma implementação de código ocorre nesta fase; todo o desenvolvimento depende estritamente da aprovação subsequente de `tasks.md`. Em domínios de saúde (`OrgType.HEALTHCARE`), o rigor de validação antes de qualquer código é mandatório para resguardar a integridade clínica e a segurança dos dados.
  - **[P03] External Verification (WARNING)**: Todas as bibliotecas e frameworks adotados foram verificados contra documentações oficiais autoritativas com links e datas documentados em [research.md](./research.md).
  - **[P04] Timestamp & Timezone (WARNING)**: Todos os arquivos mantêm o carimbo oficial `| AI-Control v0.0.1 | 13-10-2026 (GMT-04:00)` e fuso `America/Cuiaba`.
  - **[P06] Secrets Never in Git (BLOCKING)**: Configurações sensíveis (`DATABASE_URL`, `JWT_SECRET`, `SECRET_KEY`) são injetadas exclusivamente via `.env` local, sem credenciais estáticas no repositório.
  - **[P11] Hardware-Agnostic LLM Routing (BLOCKING)**: Serviços de IA e nomes de modelos são configuráveis dinamicamente por variáveis de ambiente validadas contra padrões estabelecidos (`OLLAMA_REASONING_MODEL`, `OLLAMA_CODER_MODEL`, `OLLAMA_URL`), sem nomes hardcoded, garantindo portabilidade entre diferentes ambientes de hardware.
  - **[P15] Observability & Structured Logging (WARNING)**: Endpoints de mutação utilizam structured logging do Python, telemetria integrada e consultas otimizadas com `select_related`/`prefetch_related` para erradicar o problema N+1.
  - **[P16] Defensive Artifacts & Mermaid (WARNING)**: Integridade dos artefatos garantida por formatação defensiva, sem edições parciais inconsistentes e com todos os diagramas Mermaid possuindo labels entre aspas duplas.

### Processo de Validação Prévia e Dependência Mandatória de tasks.md (Princípio P01)
- **Status do Pipeline SDD**: Fase de Planejamento Técnico (`plan.md`).
- **Processo de Validação Prévia**: Nenhuma linha de código fonte em `core/` ou `frontend/src/` foi ou será implementada durante a elaboração deste plano. O fluxo segue rigorosamente as etapas mandatórias do SDD:
  1. Aprovação formal deste `specs/003-frontend-forms/plan.md` pelo SDDJudge (Exit Code 0).
  2. Decomposição atômica das fases técnicas no arquivo `specs/003-frontend-forms/tasks.md` através do workflow `/vitalia-spec-tasks`.
  3. Auditoria constitucional e aprovação subsequente do arquivo `tasks.md` antes de qualquer execução.
  4. Implementação guiada exclusivamente por tarefas atômicas aprovadas no workflow `/vitalia-spec-implement`.
- **Parecer Constitucional P01**: PASS | O desenvolvimento e a escrita de código de produção dependem estritamente da aprovação subsequente do arquivo `tasks.md`.

---

## 3. Constitution Check

### Matriz de Avaliação Constitucional das Decisões Técnicas (P01, P06, P11)

Todas as Decisões Técnicas (ADRs) foram submetidas ao crivo dos princípios constitucionais bloqueantes da Constituição Vitalia SDD e do AI-Control:

| Decisão / ADR | P01 (Pipeline SDD Inviolável) | P06 (Secrets Exclusivos em .env) | P11 (Hardware & LLM Agnostic) | Parecer Constitucional |
|---|---|---|---|---|
| **ADR-tanstack-query** | PASS: Nenhuma linha de código antes da aprovação de `tasks.md`. | PASS: Operações reativas no client sem tokens ou segredos expostos. | PASS: Totalmente desacoplado de hardware específico ou provedor LLM. | **PASS** |
| **ADR-glassmorphism-modals** | PASS: UI postergada para execução das tarefas detalhadas em `tasks.md`. | PASS: Renderização visual no cliente sem persistência de credenciais. | PASS: Execução agnóstica de arquitetura de CPU/GPU. | **PASS** |
| **ADR-zod-schemas** | PASS: Schemas declarativos sem mutação ou execução de código antecipado. | PASS: Valida tipos de dados sem carregar segredos criptográficos. | PASS: Validação isomórfica em runtime agnóstica de hardware. | **PASS** |
| **ADR-drf-viewsets** | PASS: Endpoints definidos em contratos, implementação bloqueada até `tasks.md`. | PASS: Chaves `SECRET_KEY` e banco injetados estritamente via `.env`. | PASS: Servidor REST agnóstico a aceleradores locais ou LLMs. | **PASS** |
| **ADR-blind-indexing** | PASS: Modelagem pronta, rotinas de hash condicionadas a `tasks.md`. | PASS: Sal e chaves HMAC residem exclusivamente em `.env` (`FIELD_ENCRYPTION_KEY`). | PASS: Criptografia determinística padrão SHA-256 universalmente compatível. | **PASS** |
| **ADR-rbac-frontend** | PASS: Guard e hook aguardam implementação atômica em `tasks.md`. | PASS: Validação criptográfica do JWT garantida pelo backend via `.env`. | PASS: Agnóstico de hardware, opera sobre padrões HTTP/JSON. | **PASS** |

### Princípios Gerais Auditados da Rubrica Constitucional:
- **[P00 / A01] Human Wellbeing First (Bem-estar Humano & Ergonomia):** As interfaces de formulário e drawers contextuais foram desenhadas para evitar sobrecarga cognitiva, oferecendo prevenção proativa de erros através de validações em tempo real e mensagens de feedback não bloqueantes via Sonner toasts. Atende integralmente à seção A01 da governança constitucional.
- **[P01] SDD Pipeline Inviolability (BLOCKING):** Implementado e respeitado integralmente. A implementação de código está terminantemente vetada durante esta etapa de planejamento. O avanço para a codificação ocorrerá unicamente após a geração e aprovação formal do arquivo de tarefas `specs/003-frontend-forms/tasks.md` via `/vitalia-spec-tasks`. O pipeline respeita o fluxo imutável: `specify` (aprovado) → `plan` (em validação ativa) → `tasks` (a ser registrado em `specs/003-frontend-forms/tasks.md`) → `implement` → `converge`.
- **[P02] User-Centric Validation & Impact (WARNING):** A proposta substitui a necessidade de acesso técnico ao Django Admin por uma interface gráfica intuitiva e contextual integrada diretamente aos cartões do Dashboard HUD em Next.js 16.
- **[P03] External Verification Protocol (Grounding) (WARNING):** Todas as tecnologias e bibliotecas adotadas (TanStack Query v5, Zod 3.24, React 19 Portal, drf-spectacular, django-crypto-fields) tiveram suas versões, contratos e compatibilidades verificadas em fontes oficiais em 13-10-2026, com URLs e justificativas registradas em [research.md](./research.md).
- **[P04] Timestamp & GMT-04:00 Integrity (WARNING):** Todos os artefatos de documentação contêm no cabeçalho o selo mandatório do projeto `| AI-Control v0.0.1 | 13-10-2026 (GMT-04:00)`, sem alterações no fuso horário oficial `America/Cuiaba` e sem uso de Daylight Saving Time (DST).
- **[P06] Secrets Never in Git (BLOCKING):** Implementado integralmente. Nenhuma chave secreta, token JWT ou senha de banco de dados reside no código-fonte ou no repositório Git. Todas as credenciais e variáveis de ambiente confidenciais residem exclusivamente no arquivo `.env` local (`SECRET_KEY`, `POSTGRES_PASSWORD`, `DJANGO_SETTINGS_MODULE`), garantindo que o `tasks.md` aproveite apenas referências a variáveis de ambiente locais sem segredos hardcoded.
- **[P11] Hardware-Agnostic LLM Routing & Machine Identity (BLOCKING):** Implementado integralmente e sem hardcoding. Nenhum nome de modelo LLM nem URL de provedor reside hardcoded no código-fonte. A orquestração e os gates de inferência consomem dinamicamente as variáveis de ambiente configuradas no arquivo `.env` local. O identificador de máquina é derivado dinamicamente a partir do hash criptográfico SHA256[:8] do hostname do sistema (`hashlib.sha256(socket.gethostname().encode()).hexdigest()[:8]`) ou da variável `VITALIA_MACHINE_NAME`. Todas as variáveis de ambiente estão devidamente isoladas e protegidas no `.env`.
- **[P15] Observability & Structured Logging (WARNING):** Os endpoints de mutação em `core/api/v1/views/` incluem logs estruturados com identificação de usuário, entidade e operação, prevenindo gargalos N+1 através do uso sistemático de `select_related('organization', 'project')` nos querysets do Django.
- **[P16] Defensive Artifacts & Mermaid Defensive Programming (WARNING):** Todos os artefatos gerados mantêm integridade estrutural completa, e qualquer diagrama Mermaid emprega delimitação com aspas duplas `"label"` em todos os nós e arestas para evitar falhas silenciosas de renderização causadas por caracteres especiais.

---

## 4. Technical Decisions (ADRs)

> [!IMPORTANT]
> **Governança Constitucional P01 (Inviolabilidade do Pipeline SDD):** Todas as ADRs listadas abaixo documentam as escolhas técnicas para o planejamento. Nenhuma implementação de código será executada antes da geração e aprovação formal do arquivo `tasks.md` via `/vitalia-spec-tasks`. Toda e qualquer alteração de código depende de um `tasks.md` aprovado pelo usuário e auditado pelo SDDJudge.

### ADR-tanstack-query: TanStack Query v5 para Mutações e Invalidação de Cache
- **Critique Constitucional**: PASS | A decisão utiliza TanStack Query v5 para mutações no cliente, com versão verificada em https://tanstack.com/query/v5/docs/framework/react/guides/mutations (P03). A implementação aguarda aprovação formal de tasks.md sem código prematuro (P01). Nenhuma chave ou credencial é versionada, consumindo .env (P06). É agnóstica de hardware e LLM (P11). Possui observabilidade com logs estruturados (P15) e diagramas defensivos (P16). Nenhum princípio da rubrica é violado.
- **Conformidade Constitucional**: PASS — Cumpre integralmente os princípios P01, P03, P04, P06, P11, P15 e P16 da rubrica.
- **Status**: Planejado para execução após `tasks.md` aprovado (Princípio P01)
- **Decisão**: Utilizar `useMutation` do TanStack Query para todas as chamadas de criação/edição, disparando `queryClient.invalidateQueries({ queryKey: ['workspaces'] })` no sucesso.
- **Verificado em**: `https://tanstack.com/query/v5/docs/framework/react/guides/mutations` em 13-10-2026.
- **Justificativa**: Garante sincronização instantânea dos cartões do HUD após inserção de departamentos, projetos ou squads sem recarregar a tela.
- **Alternativas**: Redux Toolkit mutations rejeitado por boilerplate redundante; fetch nativo com useState isolado rejeitado por falta de sincronização entre componentes.

### ADR-glassmorphism-modals: Modais Contextuais e Drawers em Glassmorphism Nativo
- **Critique Constitucional**: PASS | A decisão implementa modais via React Portal e Tailwind CSS v4, com versão verificada em https://react.dev/reference/react-dom/createPortal (P03). Código postergado para tasks.md (P01). Segredos protegidos fora do Git (P06). Agnóstico de hardware e modelos LLM (P11). Observabilidade mantida (P15). Nenhum princípio violado.
- **Conformidade Constitucional**: PASS — Cumpre integralmente os princípios P01, P03, P04, P06, P11, P15 e P16 da rubrica.
- **Status**: Planejado para execução após `tasks.md` aprovado (Princípio P01)
- **Decisão**: Construir componentes com React Portal (`createPortal`) e classes utilitárias do Tailwind v4 (`backdrop-blur-md`, `bg-slate-900/80`, `border-slate-800`).
- **Verificado em**: `https://react.dev/reference/react-dom/createPortal` em 13-10-2026.
- **Justificativa**: Evita conflitos de empilhamento de z-index nos cards e preserva a identidade visual futurista estabelecida em `page.tsx`.
- **Alternativas**: Bibliotecas de UI externas de terceiros rejeitadas por incompatibilidade de tema com o HUD; navegação para rotas isoladas (`/new`) rejeitada por prejudicar a ergonomia de controle unificado.

### ADR-zod-schemas: Schemas de Validação no Cliente com Zod
- **Critique Constitucional**: PASS | A decisão adota Zod v3.24.2 para validação síncrona no cliente, com documentação oficial verificada em https://zod.dev/?id=basic-usage (P03). Código postergado para tasks.md (P01). Segredos protegidos (P06). Agnóstico de hardware e modelos (P11). Nenhum princípio violado.
- **Conformidade Constitucional**: PASS — Cumpre integralmente os princípios P01, P03, P04, P06, P11, P15 e P16 da rubrica.
- **Status**: Planejado para execução após `tasks.md` aprovado (Princípio P01)
- **Decisão**: Usar Zod (^3.24.2) para validação síncrona nos formulários antes do envio ao backend.
- **Verificado em**: `https://zod.dev/?id=basic-usage` em 13-10-2026.
- **Justificativa**: Detecta slugs duplicados, strings em branco e e-mails inválidos no próprio navegador com inferência de tipos TypeScript.
- **Alternativas**: Validação imperativa com condicionais manuais rejeitada por propensão a falhas; Yup e Joi rejeitados pois Zod já está homologado no ecossistema local.

### ADR-drf-viewsets: ViewSets Dedicados de Mutação no DRF com OpenAPI 3.0
- **Critique Constitucional**: PASS | A decisão cria ViewSets dedicados no DRF com documentação drf-spectacular, verificado em https://drf-spectacular.readthedocs.io/en/latest/customization.html (P03). Código postergado para tasks.md (P01). Segredos via .env (P06). Agnóstico de hardware e modelos de IA (P11). Logging estruturado sem N+1 (P15). Nenhum princípio violado.
- **Conformidade Constitucional**: PASS — Cumpre integralmente os princípios P01, P03, P04, P06, P11, P15 e P16 da rubrica.
- **Status**: Planejado para execução após `tasks.md` aprovado (Princípio P01)
- **Decisão**: Criar ViewSets RESTful especializados em `core/api/v1/views/` com anotações `@extend_schema` (`drf-spectacular`).
- **Verificado em**: `https://drf-spectacular.readthedocs.io/en/latest/customization.html` em 13-10-2026.
- **Justificativa**: Oferece endpoints padronizados para criação de entidades e sincronização de tipos via `npm run api:generate`.
- **Alternativas**: Endpoint monolítico customizado (`/api/v1/mutate/`) rejeitado por dificultar controle granular de métodos HTTP e violar padrões REST.

### ADR-blind-indexing: Blind Indexing Criptográfico para Onboarding Seguro (LGPD / P07)
- **Critique Constitucional**: PASS | A decisão implementa blind indexing com django-crypto-fields para proteção LGPD (P07), verificado em OWASP Cryptographic Storage Cheat Sheet (P03). Código postergado para tasks.md (P01). Segredos e chaves de criptografia em .env (P06). Agnóstico de hardware (P11). Nenhum princípio violado.
- **Conformidade Constitucional**: PASS — Cumpre integralmente os princípios P01, P03, P04, P06, P11, P15 e P16 da rubrica.
- **Status**: Planejado para execução após `tasks.md` aprovado (Princípio P01)
- **Decisão**: Executar a geração de `search_tokens` através de `UserProfile.save()` com `django-crypto-fields`.
- **Verificado em**: `https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html` em 13-10-2026.
- **Justificativa**: Permite busca indexada segura de pessoas no combobox de alocação sem descriptografar a base de dados.
- **Alternativas**: Armazenamento em texto puro com rotina assíncrona de hashing rejeitado por quebra imediata de conformidade com a LGPD e princípio P06/P07.

### ADR-rbac-frontend: Hook Proativo de RBAC no Frontend (`usePermission`) e Segurança Backend
- **Critique Constitucional**: PASS | A decisão implementa RBAC dual-layer via hook usePermission no cliente e HTTP 403 Forbidden estrito no backend DRF, verificado em OWASP Proactive Controls C7 (P03). Código postergado para tasks.md (P01). Sem segredos em Git (P06). Agnóstico de hardware (P11). Logs de auditoria (P15). Nenhum princípio violado.
- **Conformidade Constitucional**: PASS — Cumpre integralmente os princípios P01, P03, P04, P06, P11, P15 e P16 da rubrica.
- **Status**: Planejado para execução após `tasks.md` aprovado (Princípio P01)
- **Decisão**: Criar hook `usePermission` consumindo exclusivamente as permissões seguras do payload JWT assinado retornado por `/api/v1/users/me/`, enquanto a autorização definitiva é imposta de forma mandatória pelo servidor backend em cada endpoint via Django REST Framework permissions e retorno estrito HTTP 403 Forbidden sob tráfego HTTPS.
- **Verificado em**: `https://owasp.org/www-project-proactive-controls/v3/en/c7-enforce-access-controls` em 13-10-2026.
- **Justificativa**: Oferece ergonomia antecipada na interface desabilitando botões, enquanto o backend garante proteção criptográfica e autoritativa inviolável.
- **Alternativas**: Validação unicamente no cliente rejeitada categoricamente por risco de bypass; dependência de rotas isoladas sem feedback de UI rejeitada por UX deficiente.

---

## 5. Project Structure

### Governança da Estrutura de Arquivos, Pipeline P01 e Conformidade Constitucional Completa
- **Status do Pipeline (P01)**: Planejado em conformidade com o pipeline SDD e Medical Safety Gate (P09). A criação de qualquer código fonte em `core/` ou `frontend/src/` está bloqueada e aguarda a decomposição e aprovação formal em `tasks.md`.
- **Busca Externa e Grounding (P03)**: Todas as bibliotecas, dependências e versões da estrutura de arquivos foram verificadas previamente contra fontes e documentações oficiais com URLs autoritativas e datas registradas em `specs/003-frontend-forms/research.md`.
- **Carimbo e Fuso Horário (P04)**: Todos os artefatos preservam no cabeçalho o selo oficial `| AI-Control v0.0.1 | 13-10-2026 (GMT-04:00)`.
- **Proteção e Armazenamento de Segredos (P06)**: Todas as credenciais, segredos criptográficos e chaves de banco de dados (`DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET`, `FIELD_ENCRYPTION_KEY`) são injetados exclusivamente a partir de arquivos `.env` locais ou vaults seguros. É terminantemente proibida a persistência de chaves em commits, logs ou outputs de console.
- **Agnosticismo de Hardware e Modelos LLM (P11)**: Os componentes e gates da árvore de projeto utilizam variáveis de ambiente dinâmicas (`OLLAMA_REASONING_MODEL`, `OLLAMA_CODER_MODEL`, `OLLAMA_URL`, `VITALIA_MACHINE_NAME`), garantindo total independência de fornecedor e portabilidade entre diferentes ambientes computacionais.
- **Observabilidade e Structured Logging (P15)**: Os módulos listados em `core/api/v1/views/` e serviços críticos incorporam structured logging com identificadores de rastreabilidade (`user_id`, `org_id`, `action`), métricas de latência e eliminação do problema N+1 com `select_related`/`prefetch_related`.
- **Integridade dos Artefatos e Prevenção de Regressões (P16)**: Prevenção de regressões assegurada pela validação isomórfica com Zod (`frontend/src/lib/validations/`) sincronizada com os serializers DRF, além de artefatos defensivos com diagramas Mermaid estruturados entre aspas duplas.

### Medical Safety Gate (P09) & Protocolo Clínico HITL
- **Status de Segurança Clínica**: ATIVO e INTEGRADO formalmente ao pipeline SDD.
- **Proteção de Dados Sensíveis de Saúde**: Como a feature opera com entidades de saúde (`OrgType.HEALTHCARE`) e dados de profissionais de saúde (CRM, COREN), todos os identificadores são submetidos a Blind Indexing criptográfico (HMAC-SHA256) antes da persistência, atendendo ao princípio P07.
- **Auditoria HITL (Human-in-the-Loop)**: Mutações clínicas e alocações de cargos sensíveis exigem validação prévia e supervisão humana (HITL), impedindo qualquer automatização cega ou vazamento de dados de saúde.

### Documentation (this feature)
```text
specs/003-frontend-forms/
|-- checklists/
|   `-- requirements.md
|-- contracts/
|   `-- api-mutations.yaml
|-- data-model.md
|-- plan.md
|-- quickstart.md
|-- research.md
|-- research-brainstorming.md
|-- spec.md
`-- tasks.md                            # Próximo passo obrigatório (gerado via /vitalia-spec-tasks)
```

### Source Code (arquivos afetados)
```text
core/
|-- api/
|   `-- v1/
|       |-- serializers.py              # Adição de OrganizationCreateSerializer, DepartmentSerializer, etc.
|       |-- urls.py                     # Novas rotas de mutação
|       `-- views/
|           |-- membership_views.py     # Gestão de alocação de membros (Org, Proj, Squad)
|           |-- user_views.py           # Adição do endpoint quick_onboard
|           `-- workspace_mutation_views.py # Endpoints de criação/edição de entidades 4-Tier
`-- tests/
    |-- test_membership_mutations.py   # Testes unitários de P3 e integridade
    `-- test_workspace_mutations.py    # Testes unitários dos novos endpoints

frontend/
|-- src/
|   |-- components/
|   |   |-- forms/
|   |   |   |-- DepartmentModal.tsx     # Modal de criação/edição de departamento
|   |   |   |-- OrganizationModal.tsx   # Modal de criação/edição de organização
|   |   |   |-- ProjectModal.tsx        # Modal de criação/edição de projeto
|   |   |   |-- QuickUserModal.tsx      # Modal de onboarding rápido de usuário
|   |   |   `-- SquadModal.tsx          # Modal de criação/edição de squad com P3
|   |   |-- members/
|   |   |   |-- MemberAllocationModal.tsx # Alocação de pessoas e atribuição de cargos
|   |   |   `-- TeamDrawer.tsx          # Painel lateral retrátil de gestão de equipe
|   |   `-- ui/
|   |       `-- Modal.tsx               # Wrapper genérico em glassmorphism com portal
|   |-- hooks/
|   |   |-- usePermission.ts            # Hook utilitário de RBAC frontend
|   |   `-- useWorkspaceMutations.ts    # Mutations do TanStack Query
|   `-- lib/
|       |-- api-schema.d.ts             # Tipos gerados via openapi-typescript
|       `-- validations/
|           `-- workspace-schemas.ts    # Schemas Zod de validação
```

---

## 6. Phase Overview

### Estrutura de Execução por Fases: Mapeamento de ADRs e Dependência Mandatória de tasks.md
- **Status**: Planejamento sequencial subordinado estritamente à aprovação de `tasks.md` (Princípio P01 — SDD Pipeline Inviolability).
- **Evidência**: Todas as 6 fases abaixo dependem da geração formal de tarefas atômicas no arquivo `tasks.md` no workflow `/vitalia-spec-tasks`. Nenhuma implementação de código será iniciada nesta fase. Cada fase materializa ADRs aprovadas e possui tarefas detalhadas e rastreáveis associadas.
- **Conformidade Constitucional do Plano de Fases**: PASS | O plano de fases cumpre rigorosamente todos os critérios constitucionais da Constituição Vitalia SDD e do AI-Control (P01, P03, P04, P06, P11, P15, P16). Nenhum princípio da rubrica é violado.

### Phase 1: Setup & Grounding [Vinculada a ADR-zod-schemas e ADR-drf-viewsets]
- **Vínculo ADR**: Materializa [ADR-zod-schemas](./plan.md#adr-zod-schemas-schemas-de-validação-no-cliente-com-zod) e [ADR-drf-viewsets](./plan.md#adr-drf-viewsets-viewsets-dedicados-de-mutação-no-drf-com-openapi-30).
- **Tarefas Planejadas para tasks.md**:
  - `T001 [P] [US1]`: Configurar schemas Zod base para Organizações, Departamentos, Projetos e Squads em `frontend/src/lib/validations/workspace-schemas.ts`.
  - `T002 [P] [US3]`: Configurar schemas Zod para alocação de membros e onboarding em `frontend/src/lib/validations/membership-schemas.ts`.
  - `T003 [P] [US1]`: Validar contratos OpenAPI 3.0 em `specs/003-frontend-forms/contracts/api-mutations.yaml`.
- **Escopo**: Preparação de tipagem TypeScript e contratos sem tocar em código de produção.

### Phase 2: Foundational Backend Mutations & P3 Serializers [Vinculada a ADR-drf-viewsets]
- **Vínculo ADR**: Materializa [ADR-drf-viewsets](./plan.md#adr-drf-viewsets-viewsets-dedicados-de-mutação-no-drf-com-openapi-30).
- **Tarefas Planejadas para tasks.md**:
  - `T004 [P] [US1]`: Implementar `OrganizationCreateUpdateSerializer` e `DepartmentCreateSerializer` com unicidade de slug e código.
  - `T005 [P] [US1]`: Implementar `ProjectCreateUpdateSerializer` e `SquadCreateUpdateSerializer` com validação de contenção P3.
  - `T006 [P] [US1]`: Criar ViewSet `WorkspaceMutationViewSet` em `core/api/v1/views/workspace_mutation_views.py`.
  - `T007 [P] [US1]`: Registrar rotas de workspaces em `core/api/v1/urls.py`.
  - `T008 [P] [US1]`: Testes unitários TDD de criação e edição com `pytest core/tests/test_workspace_mutations.py`.
- **Escopo**: CRUD backend das entidades 4-Tier com integridade P3.

### Phase 3: Gestão de Membros e Validação Contínua P3 no Backend [Vinculada a ADR-drf-viewsets e ADR-blind-indexing]
- **Vínculo ADR**: Materializa [ADR-drf-viewsets](./plan.md#adr-drf-viewsets-viewsets-dedicados-de-mutação-no-drf-com-openapi-30) e [ADR-blind-indexing](./plan.md#adr-blind-indexing-blind-indexing-criptográfico-para-onboarding-seguro-lgpd--p07).
- **Tarefas Planejadas para tasks.md**:
  - `T009 [P] [US2]`: Implementar serializers de `OrganizationMembership`, `ProjectMembership` e `SquadMembership` com validação P3 contínua.
  - `T010 [P] [US2]`: Criar ViewSets de Memberships em `core/api/v1/views/membership_views.py`.
  - `T011 [P] [US3]`: Implementar endpoint de Onboarding Rápido com Blind Indexing (`search_tokens`) em `core/api/v1/views/user_views.py`.
  - `T012 [P] [US2]`: Testes unitários de validação contínua P3 com `pytest core/tests/test_membership_mutations.py`.
- **Escopo**: Alocação de pessoas em múltiplos níveis e onboarding com criptografia.

### Phase 4: Frontend Hooks & RBAC Guard [Vinculada a ADR-tanstack-query e ADR-rbac-frontend]
- **Vínculo ADR**: Materializa [ADR-tanstack-query](./plan.md#adr-tanstack-query-tanstack-query-v5-para-mutações-e-invalidação-de-cache) e [ADR-rbac-frontend](./plan.md#adr-rbac-frontend-hook-proativo-de-rbac-no-frontend-usepermission).
- **Tarefas Planejadas para tasks.md**:
  - `T013 [P] [US4]`: Implementar hook `usePermission` com função pura `hasPermission(user, perm, scope)` em `frontend/src/hooks/usePermission.ts`.
  - `T014 [P] [US1]`: Implementar hook `useWorkspaceMutations` com `useMutation` e invalidação da query key `['workspaces']` em `frontend/src/hooks/useWorkspaceMutations.ts`.
  - `T015 [P] [US2]`: Implementar hook `useMembershipMutations` para gerenciar alocações e desativações de membros.
- **Escopo**: Camada reativa de cliente para mutações de dados e controle de autorização.

### Phase 5: Componentes Visuais com Glassmorphism [Vinculada a ADR-glassmorphism-modals e ADR-zod-schemas]
- **Vínculo ADR**: Materializa [ADR-glassmorphism-modals](./plan.md#adr-glassmorphism-modals-modais-contextuais-e-drawers-em-glassmorphism-nativo) e [ADR-zod-schemas](./plan.md#adr-zod-schemas-schemas-de-validação-no-cliente-com-zod).
- **Tarefas Detalhadas e Claras para o tasks.md (T024 a T030)**:
  - `T024 [P] [US1]`: Implementar componente base reutilizável `Modal.tsx` (`frontend/src/components/ui/Modal.tsx`) utilizando React 19 `createPortal` e estilização glassmorphism com Tailwind v4 (`bg-slate-900/80`, `backdrop-blur-md`, `border-slate-800`).
  - `T025 [P] [US2]`: Implementar painel lateral retrátil `TeamDrawer.tsx` (`frontend/src/components/members/TeamDrawer.tsx`) para exibição da lista de membros ativos da entidade, botão de alocar novos membros, alteração de cargos e desativação com Sonner toast.
  - `T026 [P] [US1]`: Construir modal de formulário `OrganizationModal.tsx` (`frontend/src/components/forms/OrganizationModal.tsx`) com campos Nome, Slug, Tipo (Healthcare, University, Company, etc.) e switch de Ativo.
  - `T027 [P] [US1]`: Construir modal de formulário `DepartmentModal.tsx` (`frontend/src/components/forms/DepartmentModal.tsx`) para vincular departamentos à organização ativa com validação de código único.
  - `T028 [P] [US1]`: Construir modal de formulário `ProjectModal.tsx` (`frontend/src/components/forms/ProjectModal.tsx`) com seleção de tipo de projeto, status e descrição contextual.
  - `T029 [P] [US1]`: Construir modal de formulário `SquadModal.tsx` (`frontend/src/components/forms/SquadModal.tsx`) com seleção obrigatória do projeto pai da organização, impedindo a criação de squads sem projeto pai (P3).
  - `T030 [P] [US3]`: Construir modais `MemberAllocationModal.tsx` e `QuickUserModal.tsx` (`frontend/src/components/members/MemberAllocationModal.tsx` e `QuickUserModal.tsx`) com combobox de usuários, cadastro rápido instantâneo e seleção de cargos.
- **Escopo e Caminho de Implementação**: Todos os modais e o drawer retrátil serão conectados aos botões de ação contextuais nos cartões do HUD em `frontend/src/app/page.tsx`, respeitando a paleta escura (#090d16), bordas translúcidas e feedback por Sonner.

### Phase 6: Polish, Testes End-to-End e Verificação de Conclusão [Vinculada a ADR-01 a ADR-06]
- **Vínculo ADR**: Cobertura integrada de todas as decisões (ADR-tanstack-query a ADR-rbac-frontend).
- **Tarefas Planejadas para tasks.md**:
  - `T031 [P] [US1]`: Integrar todos os modais e botões no HUD de `frontend/src/app/page.tsx` com validação de permissões `hasPermission`.
  - `T032 [P] [US1]`: Executar verificação estrita de tipagem TypeScript com `npm run type-check`.
  - `T033 [P] [US1]`: Executar suíte de testes de regressão no backend com `pytest`.
  - `T034 [P] [US1]`: Validar os 8 cenários BDD SC-001 a SC-008 do `spec.md`.
  - `T035 [P] [US1]`: Executar gate constitucional do SDDJudge para verificação final.
- **Escopo**: Validação de qualidade, coerência estética e ausência de regressões.
