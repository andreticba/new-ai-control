<!-- plan.md | Vitalia SDD v0.6.0 | 11-10-2026 20:50(GMT-04:00) -->
**plan.md | AI-Control v0.0.1 | 11-10-2026 20:50(GMT-04:00)**

# Implementation Plan: Frontend v1 & Adequação do Seed Demo

**Branch**: `main` | **Date**: 11-10-2026 | **Spec**: [spec.md](spec.md)

---

## 1. Summary

Este plano estabelece a implementação técnica para construir a ponte de consumo entre o backend Django e o frontend Next.js 16, além de adequar o semeamento de demonstração local:
1. **Adequação Canônica do `seed_demo.py`**: Criação rigorosa das 13 personas e hierarquias de `docs/manuals/PERSONAS.md` (tenants `ufdemo` e `empresa-demo`), blind indexing (`search_tokens`) e mock de omnichannel com Soft FKs (`organization_id`), sem tocar na infraestrutura nem nos usuários de plataforma (`admin`, `suporte`, `ai-bot`, `ai-control`).
2. **API Gateway Síncrono (BFF)**: Autenticação JWT stateless com `djangorestframework-simplejwt`, endpoints agregados `/api/v1/users/me/` e `/api/v1/workspaces/` (4 níveis com `job_title` e roles), suporte a CORS restrito (`django-cors-headers`) e contrato dinâmico OpenAPI 3.0 via `drf-spectacular` com segurança condicional por ambiente.
3. **Frontend v1 (Next.js 16)**: Espelhamento da stack homologada de `vitalia-01/frontend`, implementando cliente Axios com interceptor resiliente (`src/lib/api.ts`), script de tipagem `npm run api:generate`, Two-Step Login reativo na rota `/login` e Shell contextualizado no Dashboard (`/`).

---

## 2. Technical Context

- **Language/Version**: Python 3.14+ (Backend), TypeScript 5.8+ / Node.js 20+ (Frontend)
- **Primary Dependencies**: 
  - Backend: `Django~=6.1.2`, `djangorestframework~=3.16.1`, `djangorestframework-simplejwt~=5.3.1`, `django-cors-headers~=4.3.1`, `drf-spectacular~=0.30.0`, `django-crypto-fields==1.0.1`, `psycopg2-binary~=2.9.11`, `celery~=5.6.2`, `redis~=5.0.0`
  - Frontend: `next@16.1.7`, `react@19.2.0`, `tailwindcss@^4.0.0`, `@reduxjs/toolkit@^2.11.0`, `@tanstack/react-query@^5.90.12`, `axios@^1.13.2`, `react-hook-form@^7.71.1`, `zod@^3.25.76`, `sonner@^2.0.7`, `lucide-react@^1.16.0`
- **Storage**: PostgreSQL 16 com extensão `pgvector`, Redis 7+ (DB 0 para Cache, DB 2 para Celery Omnichannel)
- **Testing**: `pytest`, `pytest-django`, testes de integração REST
- **Target Platform**: Web (Next.js SSR/Client), Servidor Linux (WSGI/ASGI Daphne)
- **Project Type**: Monorepo Co-localizado (`frontend/` e `core/`)
- **Performance Goals**: Resposta média do API Gateway Síncrono < 150ms; Renovação silenciosa de token em background sem flickers de UI
- **Constraints**: Zero Secrets no Git (P06); Agnosticismo de Hardware (P11); Eager Loading contra N+1 (P15); Blind Indexing de PII (P07)

---

## 3. Constitution Check

| Princípio | Descrição | Status no Plano |
|---|---|---|
| **[P00] Purpose Arbiter** | Foco absoluto no bem-estar de quem usa e gerencia a plataforma | ✅ Conforme — feedback claro de credenciais e navegação intuitiva no frontend |
| **[P01] SDD Pipeline** | Inviolabilidade do ciclo spec → plan → tasks → implement | ✅ Conforme — plano técnico deriva estritamente da spec formal |
| **[P02] User-Centric Validation** | Declaração explícita de impacto e conformidade multi-tenant/RBAC | ✅ Conforme — validação da matriz 4-Tier e isolamento estrito de tenants |
| **[P03] Grounding Verification** | Decisões técnicas embasadas com "Verificado em:" e fontes oficiais | ✅ Conforme — 7 ADRs mapeadas em `research.md` e ancoradas nos manuais de `docs/manuals/` e post-mortems |
| **[P04] Timestamp & Timezone** | Header obrigatório `GMT-04:00` em todos os artefatos | ✅ Conforme — carimbo estrito aplicado em todos os arquivos |
| **[P06] Zero Secrets in Git** | Senhas e chaves ausentes do histórico e protegidas em variáveis | ✅ Conforme — chaves carregadas via `crypto_keys`, senha demo parametrizável |
| **[P11] Hardware Agnosticism** | Sem models ou provedores LLM hardcoded | ✅ Conforme — contratos agnósticos com suporte a fallbacks |
| **[P15] Observability & Eager Loading** | Sem N+1, queries otimizadas e processamento pesado fora da web | ✅ Conforme — `select_related`/`prefetch_related` nos endpoints de workspaces |
| **[P16] Defensive Mermaid** | Labels de diagramas entre aspas para prevenir quebras de sintaxe | ✅ Conforme — todos os nós dos diagramas utilizam aspas duplas |

---

## 4. Technical Decisions

### Decisão: Separação de Arquitetura em Duas Frentes
- **Escolhido**: API Gateway Síncrono no Django (rotas agregadas `/api/v1/users/me/` e `/api/v1/workspaces/` com resposta < 150ms) segregado da Esteira Assíncrona de IA/Ingestão (Celery Workers + Redis DB 2 isolado).
- **Verificado em**: `ai-control/docs/04_Solution_Strategy.md:10-14` e `ai-control/docs/10_Quality_Requirements.md:16-20` em 11-10-2026.
- **Justificativa**: A UI precisa carregar instantaneamente sem disputar CPU com inferência de LLM ou descriptografia pesada do Data Vault.
- **Alternativas**: Processamento síncrono inline de IA rejeitado por violar SLA de latência.

### Decisão: Stack de Frontend e Padrão de Provisionamento
- **Escolhido**: Next.js 16.1.7, React 19.2.0, Tailwind CSS v4, shadcn/ui, TanStack Query v5 e Redux Toolkit, inicializado por espelhamento estrutural de `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend`.
- **Verificado em**: `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json:1-60` e `AI-Control completo.md:5412-5446` em 11-10-2026.
- **Justificativa**: Garante consistência arquitetural total com o produto maduro e com o agente React-Vinci, prevenindo problemas de incompatibilidade de geradores externos.
- **Alternativas**: Vite SPA e Next-Auth rejeitados pela Constituição do Arquiteto.

### Decisão: Contrato OpenAPI 3.0 Dinâmico e Geração Estrita de Tipos
- **Escolhido**: `drf-spectacular~=0.30.0` gerando `GET /api/schema/` dinâmico e script frontend `npm run api:generate` com `openapi-typescript`.
- **Verificado em**: `ai-control/requirements.txt:21` e `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json:10` em 11-10-2026.
- **Justificativa**: Type-safety garantido do backend para o frontend, eliminando interfaces declaradas manualmente.
- **Alternativas**: Interfaces manuais e drf-yasg rejeitados por risco de drift e obsolescência.

### Decisão: Segurança Condicional do Schema OpenAPI por Ambiente (OWASP API9:2023)
- **Escolhido**: Segurança condicional por ambiente via `SPECTACULAR_SETTINGS`: `AllowAny` em `DEBUG=True` e `IsAdminUser` + Bearer JWT em `DEBUG=False`.
- **Verificado em**: `https://drf-spectacular.readthedocs.io/en/latest/settings.html` e OWASP API Security Top 10 em 11-10-2026.
- **Justificativa**: Permite flexibilidade no desenvolvimento local enquanto impede Information Disclosure de rotas e tabelas em produção.
- **Alternativas**: Desativar schema em prod ou deixá-lo público rejeitados por quebra de governança.

### Decisão: Suporte a CORS Restrito com `django-cors-headers`
- **Escolhido**: Instalação de `django-cors-headers~=4.3.1` e implementação das seguintes configurações no backend Django (`config/settings/base.py`):
  1. Adicionar `'corsheaders'` em `INSTALLED_APPS`.
  2. Incluir `'corsheaders.middleware.CorsMiddleware'` na lista `MIDDLEWARE`, antes de `django.middleware.common.CommonMiddleware`.
  3. Configurar políticas de CORS restritas:
     ```python
     CORS_ORIGIN_ALLOW_ALL = False
     CORS_ALLOW_CREDENTIALS = True
     CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
     ```
- **Verificado em**: `https://pypi.org/project/django-cors-headers/` e parecer oficial do SDDJudge em 11-10-2026.
- **Justificativa**: Atendimento estrito ao parecer do juiz constitucional para liberar requisições controladas do Next.js sem brechas de segurança.
- **Alternativas**: `CORS_ORIGIN_ALLOW_ALL = True` rejeitado por insegurança.

### Decisão: Autenticação JWT Stateless com `djangorestframework-simplejwt`
- **Escolhido**: `djangorestframework-simplejwt~=5.3.1` provisionando `POST /api/v1/auth/token/` e `POST /api/v1/auth/token/refresh/`.
- **Verificado em**: `https://pypi.org/project/djangorestframework-simplejwt/` e `vitalia-01/backend/requirements.txt:6` em 11-10-2026.
- **Justificativa**: Padrão stateless leve, escalável e compatível com a fila assíncrona `isRefreshing` do Axios no frontend.
- **Alternativas**: Sessões tradicionais de cookies e tokens de banco rejeitados por sobrecarga.

### Decisão: Fidelidade Canônica de Personas e RBAC 4-Tier no `seed_demo.py`
- **Escolhido**: Semeamento estrito das 13 personas canônicas de `docs/manuals/PERSONAS.md` (`prof.ana`, `gerente.ti`, etc.), 11 departamentos, 3 projetos e 6 squads, respeitando a Containment Rule (`ProjectMembership` antes de `SquadMembership`) e preservando intacta a organização interna (`ai-control`) e operadores (`admin`, `suporte`, `ai-bot`).
- **Verificado em**: `docs/manuals/PERSONAS.md:1-53` e `docs/manuals/02-engineering/01_modelo_de_dados_rbac.md:31-42` em 11-10-2026.
- **Justificativa**: Garante execução perfeita de todos os laboratórios de engenharia (`labs/lab_01` a `lab_04`) e validação visual de papéis reais na interface web.
- **Alternativas**: Dados fictícios genéricos rejeitados por quebra de consistência.

---

## 5. Project Structure

### Documentation (this feature)
```text
specs/002-frontend-seed/
├── spec.md                     # Especificação funcional formal aprovada
├── plan.md                     # Este plano de implementação
├── research.md                 # Technical research com decisões arquiteturais
├── data-model.md               # Modelo de dados semeados e diagramas ER
├── quickstart.md               # Roteiro de validação executável passo a passo
├── alinhamento1.md             # Prancheta de alinhamento com matriz de personas
├── research-brainstorming.md   # Registro de grounding e rastro socrático
├── checklists/
│   └── requirements.md         # Checklist de completude de requisitos
└── contracts/
    └── api_contracts.md        # Contratos formais dos endpoints REST
```

### Source Code (affected files)
```text
ai-control/
├── requirements.txt                         # Inclusão de djangorestframework-simplejwt e django-cors-headers
├── config/
│   ├── settings/
│   │   └── base.py                          # Configuração de CORS, SimpleJWT, Spectacular
│   └── urls.py                              # Roteamento global de auth, users, workspaces e schema
├── core/
│   ├── api/
│   │   └── v1/
│   │       ├── serializers.py               # Serializers de UserProfile, WorkspaceTree e Memberships
│   │       ├── views.py                     # CurrentUserView e ActiveWorkspacesView
│   │       └── urls.py                      # Sub-rotas v1
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo.py                 # Atualização para personas canônicas, Blind Indexing e Omnichannel
│   └── tests/
│       └── test_auth_and_workspaces.py      # Testes automatizados pytest TDD
└── frontend/                                # Monorepo do Frontend (Next.js 16)
    ├── package.json                         # Dependências homologadas de vitalia-01
    ├── tsconfig.json                        # Configuração estrita de TypeScript
    ├── postcss.config.mjs                   # Tailwind CSS v4 setup
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx                   # Layout global com providers (Redux, QueryClient, Toaster)
    │   │   ├── page.tsx                     # Dashboard Shell autenticado
    │   │   └── login/
    │   │       └── page.tsx                 # Formulário de login reativo Two-Step
    │   ├── lib/
    │   │   ├── api.ts                       # Axios client resiliente com fila isRefreshing
    │   │   └── api-schema.d.ts              # Tipos TypeScript gerados pelo openapi-typescript
    │   ├── store/                           # Redux Toolkit store e authSlice
    │   └── components/                      # Componentes shadcn/ui e navbar
```

---

## 6. Phase Overview

### Phase 1: Setup & Dependências do Backend
- Adicionar `djangorestframework-simplejwt~=5.3.1` e `django-cors-headers~=4.3.1` em `requirements.txt`.
- Instalar pacotes no virtualenv (`./.venv/bin/pip install -r requirements.txt`).
- Configurar `config/settings/base.py`:
  - Registrar `'corsheaders'` em `INSTALLED_APPS`.
  - Inserir `'corsheaders.middleware.CorsMiddleware'` em `MIDDLEWARE` antes de `django.middleware.common.CommonMiddleware`.
  - Configurar `CORS_ORIGIN_ALLOW_ALL = False`, `CORS_ALLOW_CREDENTIALS = True` e `CORS_ALLOWED_ORIGINS = ['http://localhost:3000']`.
  - Configurar `SIMPLE_JWT` e `SPECTACULAR_SETTINGS` com segurança condicional por ambiente (`DEBUG=True` aberto para `npm run api:generate`; `DEBUG=False` fechado com `IsAdminUser`).

### Phase 2: Foundational Backend & Adequação do `seed_demo.py`
- Reestruturar `core/management/commands/seed_demo.py`:
  - Preservar usuários de plataforma (`admin`, `suporte`, `ai-bot`) e org interna (`slug='ai-control'`).
  - Semear departamentos, projetos e squads canônicos de `ufdemo` e `empresa-demo`.
  - Criar as 13 personas com `full_name` em texto claro, acionando o método `UserProfile.save()` para gerar `search_tokens` de Blind Indexing.
  - Criar memberships respeitando a Containment Rule (`ProjectMembership` antes de `SquadMembership`) e associando `JobTitle` e `Role` canônicos.
  - Semear contatos com JIDs oficiais, conversas com status `ACTIVE_AI` via Soft FK (`organization_id`) e mensagens sob instâncias padrão.
  - Implementar saída formatada de credenciais com senha `demo1234` e suporte à flag `--flush`.

### Phase 3: User Story 1 — Endpoints da API Gateway Síncrona (TDD)
- Criar testes automatizados em `core/tests/test_auth_and_workspaces.py` (casos de sucesso e falha para login, perfil e workspaces).
- Implementar serializers agregados para `UserProfile` e `WorkspaceTree` em `core/api/v1/serializers.py`.
- Implementar `CurrentUserView` (`GET /api/v1/users/me/`) e `ActiveWorkspacesView` (`GET /api/v1/workspaces/`) com queries otimizadas (`select_related`/`prefetch_related`).
- Registrar rotas de token (`/api/v1/auth/token/`, `/api/v1/auth/token/refresh/`), views agregadas e endpoint de schema (`/api/schema/`) em `config/urls.py` e `core/api/v1/urls.py`.
- Executar e validar testes automatizados via `pytest`.

### Phase 4: User Story 2 — Frontend v1: Setup, Autenticação e Dashboard
- Inicializar a pasta `frontend/` com os manifestos espelhados de `vitalia-01/frontend`.
- Executar `npm install` no diretório `frontend/`.
- Configurar `src/lib/api.ts` com interceptores de request e fila de refresh token.
- Executar `npm run api:generate` para produzir `src/lib/api-schema.d.ts`.
- Construir a rota `/login` com validação Zod, Sonner, limpeza de sessão anterior e Two-Step Login.
- Construir a rota `/` (Dashboard Shell) exibindo nome do usuário, organização ativa, seletor de workspaces e botão de logout funcional.

### Phase 5: Polish & Validação Ponta a Ponta
- Executar o roteiro de testes do [quickstart.md](quickstart.md).
- Validar geração de tipos e ausência de warnings de compilação TypeScript.
- Validar isolamento do schema OpenAPI com simulação de `DEBUG=False`.
- Validar conformidade contra a Constituição do Arquiteto.
