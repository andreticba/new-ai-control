<!-- tasks.md | Vitalia SDD v0.6.0 | 11-10-2026 21:00(GMT-04:00) -->
**tasks.md | AI-Control v0.0.1 | 11-10-2026 21:00(GMT-04:00)**

# Tasks: Frontend v1 & Adequação do Seed Demo

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)
**Gerado em**: 11-10-2026 21:00(GMT-04:00)

---

## MVP Scope

> Implementar **Phase 1 + Phase 2 (US1) + Phase 3 (US2/US3)** entrega produto funcionando com a arquitetura exigida:
> - Carga canônica de demonstração no PostgreSQL sem corromper operadores de plataforma.
> - API Gateway síncrono funcional (JWT, `/users/me/`, `/workspaces/`, CORS estrito e contrato OpenAPI condicional).
> - Frontend v1 com Two-Step login e Dashboard contextualizada.
> Phases 4 e 5 consolidam a experiência de UI e os testes ponta a ponta.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e grounding ANTES de qualquer implementação. Sem label de US.*

- [X] T000-A Ativar ambiente virtual Python: `source .venv/bin/activate`
- [X] T000-B Verificar versão do Python no virtualenv ativo: `python --version` (esperado Python 3.14+)
- [X] T000-C Verificar pacotes já instalados vs requirements: `./.venv/bin/pip list`
- [X] T000-D Verificar versões homologadas no PyPI e package.json: `djangorestframework-simplejwt~=5.3.1`, `django-cors-headers~=4.3.1`, `drf-spectacular==0.30.0` e stack do frontend Next.js 16 em `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json`
- [X] T000-E Carregar na memória as dependências canônicas de grounding e governança: manuais de arquitetura (`docs/manuals/PERSONAS.md`, `docs/manuals/01-product/01_hierarquia_organizacional.md`, `docs/manuals/01-product/02_papeis_e_permissoes.md`, `docs/manuals/02-engineering/01_modelo_de_dados_rbac.md`), post-mortems de segurança (`docs/manuals/03-history/postmortems/pm_001_falha_django_groups.md`, `pm_002_vector_tenant_bleed.md`), e artefatos da especificação (`specs/002-frontend-seed/data-model.md`, `specs/002-frontend-seed/contracts/api_contracts.md`, `specs/002-frontend-seed/quickstart.md`)

---

## Phase 1: Setup & Dependências do Backend

*Inicialização do ambiente e dependências compartilhadas do backend. Sem label de US.*

- [X] T001 [P] Adicionar dependências `djangorestframework~=3.16.1`, `djangorestframework-simplejwt~=5.3.1` e `django-cors-headers~=4.3.1` no arquivo `requirements.txt`
- [X] T002 Instalar dependências atualizadas no virtualenv do projeto via `./.venv/bin/pip install -r requirements.txt`
- [X] T003 Configurar políticas de CORS estritas no arquivo `config/settings/base.py`: registrar `'rest_framework'` e `'corsheaders'` em `INSTALLED_APPS`, inserir `'corsheaders.middleware.CorsMiddleware'` em `MIDDLEWARE` antes de `django.middleware.common.CommonMiddleware`, e definir `CORS_ORIGIN_ALLOW_ALL = False`, `CORS_ALLOW_CREDENTIALS = True` e `CORS_ALLOWED_ORIGINS = ['http://localhost:3000']`
- [X] T004 [P] Configurar autenticação JWT e OpenAPI no arquivo `config/settings/base.py`: adicionar `REST_FRAMEWORK` (com `JWTAuthentication` e `DEFAULT_SCHEMA_CLASS='drf_spectacular.openapi.AutoSchema'`), parâmetros `SIMPLE_JWT` (tokens de 60m/1d) e `SPECTACULAR_SETTINGS` com segurança condicional por ambiente (`AllowAny` em `DEBUG=True`; `IsAdminUser` e Bearer JWT em `DEBUG=False`)

---

## Phase 2: User Story 1 — Carga de Demonstração Canônica (`seed_demo.py`)

**Story Goal**: Desenvolvedor ou testador executa `python manage.py seed_demo` e obtém a árvore canônica (Acadêmico `ufdemo` e Corporativo `empresa-demo`) com as 13 personas de `PERSONAS.md`, Blind Indexing via `UserProfile.save()`, contatos e conversas mockadas de omnichannel sem corromper operadores de plataforma (`admin`, `suporte`, `ai-bot`, `ai-control`).
**Independent Test**: Executar `python manage.py seed_demo` e verificar no Postgres a presença de 13 personas com `search_tokens` preenchidos, tabela formatada com credenciais `demo1234` impressa no stdout e organização `ai-control` inalterada.
**Referência**: FR-001, FR-002, FR-003, FR-004

- [X] T005 [P] [US1] Criar teste automatizado TDD em `core/tests/test_seed_demo.py` validando que `seed_demo` preserva a organização interna `ai-control`, instancia 13 personas com `search_tokens` preenchidos e aceita a flag `--flush`
- [X] T006 [US1] Refatorar comando `core/management/commands/seed_demo.py` para isolar a criação demo: proteger os operadores de plataforma (`admin`, `suporte`, `ai-bot`) e organização interna (`ai-control`, `is_internal=True`)
- [X] T007 [US1] Implementar no comando `core/management/commands/seed_demo.py` o Perfil Acadêmico (`ufdemo`): 6 departamentos (`PROPESQ`, `PROEC`, `DCOMP`, `DENF`, `FIN`, `SGP`), 2 projetos (`saude-digital` e `ia-triagem`), 4 squads e 7 personas canônicas de `specs/002-frontend-seed/data-model.md` (`prof.ana`, `prof.carlos`, `prof.lucia`, `aluno.joao`, `aluna.maria`, `pesq.externo`, `tae.paulo`) com nomes canônicos em `full_name` acionando `UserProfile.save()` para gerar Blind Indexing (`search_tokens`) e respeitando a Containment Rule (`ProjectMembership` antes de `SquadMembership`)
- [X] T008 [US1] Implementar no comando `core/management/commands/seed_demo.py` o Perfil Corporativo (`empresa-demo`): 5 departamentos (`FIN`, `RH`, `COM`, `ATD`, `TI`), 1 projeto (`implantacao-crm`), 2 squads e 6 personas canônicas de `specs/002-frontend-seed/data-model.md` (`gerente.ti`, `dev.rafa`, `supervisor.bia`, `atendente.leo`, `analista.rh`, `diretora.fin`) com `JobTitle` separado de `Role` e `full_name` preenchido
- [X] T009 [US1] Implementar no comando `core/management/commands/seed_demo.py` o semeamento omnichannel: contatos com JIDs canônicos de `PERSONAS.md`, conversas com status `ACTIVE_AI` e mensagens mockadas via Soft FK `organization_id` (`UUIDField`) sob instâncias padrão `ai_control_ufdemo` e `ai_control_empresa_demo`
- [X] T010 [US1] Implementar formatação da tabela de credenciais no terminal (Username, Senha `demo1234`, Organização, Papéis 4-Tier, JobTitle, Squads) e suporte à flag `--flush` no comando `core/management/commands/seed_demo.py`
- [X] T011 [US1] Executar testes automatizados do seed via `./.venv/bin/pytest core/tests/test_seed_demo.py` e validar cobertura

---

## Phase 3: User Story 2 & 3 — API Gateway Síncrona & Segurança OpenAPI (TDD)

**Story Goal**: Backend expõe autenticação JWT stateless, endpoints agregados `/api/v1/users/me/` e `/api/v1/workspaces/` (4 níveis com `job_title` e roles) e schema OpenAPI dinâmico com segurança condicional (`DEBUG=True` aberto / `DEBUG=False` protegido).
**Independent Test**: Executar `pytest core/tests/test_api_v1.py` validando rotas de autenticação, `/users/me/`, `/workspaces/` e `/api/schema/`.
**Referência**: FR-005, FR-006, FR-007, FR-008, FR-012

- [X] T012 [P] [US2] Criar suíte de testes TDD em `core/tests/test_api_v1.py` cobrindo: emissão/renovação de JWT (`/auth/token/`, `/auth/token/refresh/`), endpoint `/api/v1/users/me/` com decodificação segura de `full_name`, endpoint `/api/v1/workspaces/` com estrutura hierárquica de 4 níveis e cabeçalhos CORS restritos
- [X] T013 [P] [US3] Criar testes em `core/tests/test_api_schema.py` validando segurança condicional do OpenAPI: resposta aberta (HTTP 200) em `DEBUG=True` e resposta protegida (HTTP 401/403) para requisições anônimas em `DEBUG=False`
- [X] T014 [P] [US2] Implementar serializers agregados `CurrentUserSerializer` e `WorkspaceTreeSerializer` no arquivo `core/api/v1/serializers.py` com anotações `@extend_schema`
- [X] T015 [US2] Implementar views da API `CurrentUserView` (`GET /api/v1/users/me/`) e `ActiveWorkspacesView` (`GET /api/v1/workspaces/`) no arquivo modular `core/api/v1/views/user_views.py` com consultas otimizadas (`select_related`/`prefetch_related`)
- [X] T016 [US3] Implementar view de schema dinâmico com segurança condicional no arquivo `core/api/v1/views/schema_views.py` e registrar em `config/urls.py`
- [X] T017 [US2] Registrar rotas de autenticação JWT (`/api/v1/auth/token/`, `/api/v1/auth/token/refresh/`) e endpoints de domínio nos arquivos `core/api/v1/urls.py` e `config/urls.py`
- [X] T018 [US2] Executar suíte de testes do backend via `./.venv/bin/pytest core/tests/test_api_v1.py core/tests/test_api_schema.py` e confirmar status Green

---

## Phase 4: User Story 2 — Frontend v1: Setup, Autenticação e Dashboard Shell

**Story Goal**: Usuário acessa `http://localhost:3000/login`, autentica-se com credenciais canônicas, e é direcionado para a dashboard (`/`) exibindo nome em texto claro, organização e memberships.
**Independent Test**: Realizar Two-Step login via Axios no frontend e validar renderização do Shell e tratamento de renovação de token.
**Referência**: FR-009, FR-010, FR-011

- [X] T019 [P] [US2] Inicializar a estrutura de arquivos do frontend em `frontend/` com base nas dependências homologadas de `vitalia-01/frontend` (Next.js 16, React 19, Tailwind CSS v4, TypeScript, Lucide React, Sonner) criando `frontend/package.json` e `frontend/tsconfig.json`
- [X] T020 [P] [US2] Configurar Tailwind CSS v4 e estilos globais em `frontend/src/app/globals.css` e utilitários de tema em `frontend/src/lib/utils.ts`
- [X] T021 [P] [US2] Implementar cliente Axios resiliente no arquivo `frontend/src/lib/api.ts` com request interceptor injetando token Bearer e response interceptor com fila assíncrona `isRefreshing` para renovação transparente em erros HTTP 401
- [X] T022 [P] [US2] Configurar a store Redux Toolkit e slice de autenticação nos arquivos `frontend/src/store/authSlice.ts` e `frontend/src/store/index.ts`
- [X] T023 [US2] Construir a tela de login reativa no arquivo `frontend/src/app/login/page.tsx` com validação de campos, feedback visual via Sonner, limpeza preventiva de tokens anteriores e Two-Step Login (`POST /api/v1/auth/token/` seguido de `GET /api/v1/users/me/`)
- [X] T024 [US2] Construir o Shell do Dashboard e barra de navegação nos arquivos `frontend/src/app/page.tsx` e `frontend/src/components/Navbar.tsx` exibindo o nome descriptografado do usuário, slug da organização ativa, roles e botão de logout funcional

---

## Phase 5: Polish, Contrato Tipado & Validação E2E

*Qualidade, geração de contratos tipados e execução ponta a ponta. Sem label de US.*

- [X] T025 [P] Configurar o script `npm run api:generate` com `openapi-typescript` em `frontend/package.json` para extrair tipos estritos em `frontend/src/lib/api-schema.d.ts` a partir de `http://localhost:8000/api/schema/`
- [X] T026 Executar compilação e verificação de tipos do frontend via `npm run type-check` ou `npm run build` na pasta `frontend/`
- [X] T027 Executar o roteiro de testes ponta a ponta do arquivo `specs/002-frontend-seed/quickstart.md` cobrindo os 5 cenários operacionais (Seed demo, Login JWT, Dashboard Shell, Refresh Token e OpenAPI Security)

---

## Dependency Graph

```
Phase 0 (Grounding & Environment)
   ↓
Phase 1 (Setup Backend & Dependências: T001-T004)
   ↓
Phase 2 (US1: Carga Canônica seed_demo: T005-T011)
   ↓
Phase 3 (US2/US3: API Gateway BFF & OpenAPI: T012-T018)
   ↓
Phase 4 (US2: Frontend v1 Next.js 16: T019-T024)
   ↓
Phase 5 (Polish, OpenAPI Typings & E2E: T025-T027)
```

## Parallel Execution

Tasks marcadas com `[P]` dentro de cada fase não possuem dependências entre si e podem ser executadas paralelamente:
- **Phase 1**: `T001` e `T004` podem ser preparados em paralelo.
- **Phase 2**: `T005` (teste) pode ser escrito antes das implementações de `T006-T010`.
- **Phase 3**: `T012`, `T013` e `T014` são independentes e podem rodar em paralelo.
- **Phase 4**: `T019`, `T020`, `T021` e `T022` tratam de arquivos e módulos desacoplados no frontend.
- **Phase 5**: `T025` roda paralelamente aos scripts de validação.
