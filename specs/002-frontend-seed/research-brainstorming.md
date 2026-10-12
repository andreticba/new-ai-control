<!-- research-brainstorming.md | Vitalia SDD v0.6.0 | 11-10-2026 09:30(GMT-04:00) -->
**research-brainstorming.md | AI-Control v0.0.1 | 11-10-2026 09:30(GMT-04:00)**

# Research & Socratic Brainstorming: Adequação do Seed Demo & Frontend v1

Este documento registra as pesquisas, levantamentos técnicos e decisões de concepção para o marco prioritário (P0): **Adequação do `core/management/commands/seed_demo.py` e criação da primeira versão do frontend para consumo da API**.

---

## 1. Falhas Identificadas e Lições da Spec 001
- **Preservação de Conquistas**: A Spec 001 (`001-core-foundations`) isolou com sucesso os domínios `core` e `omnichannel` via Soft Foreign Keys (`UUIDField`), aplicou a restrição de Tenant Único (`is_internal=True`), implementou o Ledger Híbrido com Triggers PostgreSQL nativos e isolou o Redis para filas assíncronas (Redis DB 2).
- **Risco de Alucinação de Stack no Frontend**: A diretriz genérica do ambiente padrão sugere Vite e Vanilla CSS para web apps. No entanto, o ecossistema consolidado do produto em `vitalia-01` e o contrato do agente **React-Vinci** (`AI-Control completo.md:5400-5446`) exigem taxativamente **Next.js 16 (App Router), React 19, Tailwind CSS v4, shadcn/ui, TanStack Query v5 e Redux Toolkit**. Qualquer proposta divergente causaria retrabalho e inconsistência com o produto maduro.
- **Lacuna de Integração Backend <-> Frontend**: No estado atual do `ai-control`, embora os modelos estejam maduros, a camada de API REST ainda não possui o pacote `djangorestframework-simplejwt` instalado, nem expõe os endpoints `/api/v1/auth/token/`, `/api/v1/users/me/` e `/api/v1/workspaces/`. O `seed_demo.py` atual não imprime credenciais, cria instâncias sem `full_name` e não popula dados de demonstração no app `omnichannel`.

---

## 2. Garantias contra Recorrência de Erros e Preservação da Segurança de Ponta
1. **Preservação dos Avanços de Segurança Ativos (`ai-control`)**: O código local em `ai-control` já implementa pilares que representam os mais altos padrões da indústria e que estão documentados formalmente em `docs/` (`04_Solution_Strategy.md` e `08_Crosscutting_Concepts.md`):
   - **Data Vault Criptográfico**: Criptografia em nível de campo at-rest com `django-crypto-fields` (não apenas isolamento lógico).
   - **Blind Indexing**: Hashes determinísticos (`search_tokens`) permitindo busca segura de PII sem descriptografar registros nem vazar texto claro.
   - **Ledger Imutável**: Proteção a nível de engine PostgreSQL via Triggers SQL impedindo `UPDATE` e `DELETE` no `AuditLog`.
   - **Soft Foreign Keys (UUIDs)**: Isolamento estrutural de Bounded Contexts preparando para arquitetura distribuída.
   - **RBAC Hierárquico 4-Tier**: Organização -> Departamento -> Projeto -> Squad com controle granular via slugs de permissão.
2. **Backend como Fonte Única da Verdade para o Frontend**: Toda regra de autorização, validação de segurança, criptografia e conformidade reside no Backend Django. O Frontend (Next.js 16) é um consumidor estritamente tipado que nunca toma decisões de segurança por conta própria, não armazena segredos e não recebe ciphertexts brutos.
3. **Âncora de Grounding Local**: Este documento e o `alinhamento1.md` atuam como travas físicas. Qualquer proposta técnica deve harmonizar a estratégia e inteligência do legado com as diretrizes de segurança de última geração ativas em `ai-control`.
4. **Espelhamento do Produto Referência (`vitalia-01`)**: O código do frontend e do cliente HTTP utilizará os padrões já comprovados em produção no repositório `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend`, especialmente o interceptor resiliente de Axios (`lib/api.ts`) e a estratégia de Two-Step Login (`loginAndFetchUser`).
5. **Validação Red-Green-Refactor (TDD)**: As novas rotas de autenticação e os endpoints de perfil do usuário serão acompanhados de testes no backend (`pytest`) antes da entrega final.

---

## 3. Decisões Arquiteturais e de Concepção Consolidadas

| Decisão Tomada | Racional Técnico | Ação Exigida na Nova Spec |
|---|---|---|
| **Arquitetura em Duas Frentes** | Separar requisições ultra-rápidas da UI das tarefas pesadas de IA/criptografia. | 1. **Frente Síncrona**: API Gateway (endpoints agregados). <br> 2. **Frente Assíncrona**: Celery Worker + Redis DB 2 para LLM/RAG/Ingestão. |
| **Localização do Frontend** | Manter o frontend na raiz do repositório em pasta dedicada `frontend/` (padrão monorepo idêntico ao `vitalia-01`). | Criar/estruturar o diretório `frontend/` na raiz do `ai-control`. |
| **Stack Oficial do Frontend** | Seguir a stack moderna do `vitalia-01`: Next.js 16.1.x, React 19, Tailwind CSS v4, shadcn/ui, TanStack Query v5.90, RTK v2.11. | Inicializar a estrutura do `frontend/` mantendo as dependências de `vitalia-01/frontend/package.json`. |
| **Contrato Dinâmico OpenAPI 3.0** | O backend Django gera o schema formal via `drf-spectacular` para eliminar divergências de API. | Expor `/api/schema/` com `drf-spectacular` e anotações `@extend_schema`. |
| **Política de Segurança da Rota `/api/schema/`** | Evitar Information Disclosure (OWASP API9:2023) em produção mantendo facilidade no dev local. | Aberto (`AllowAny`) quando `DEBUG=True`. Protegido por `[IsAdminUser]` quando `DEBUG=False`. Suporte a exportação offline CLI (`spectacular --file schema.yml`). |
| **Tipagem Automatizada (`api:generate`)** | O frontend converte o schema OpenAPI em tipos TypeScript estritos, espelhando o legado. | Configurar script `npm run api:generate` chamando `openapi-typescript` para gerar `src/lib/api-schema.d.ts`. |
| **Autenticação JWT Stateless** | O backend Django deve emitir tokens JWT compatíveis com o cliente Axios do frontend. | Adicionar `djangorestframework-simplejwt` ao `requirements.txt` e plugar rotas de token em `config/urls.py` ou `core/urls.py`. |
| **Configuração de CORS (`django-cors-headers`)** | Sem CORS configurado, o navegador bloqueia chamadas do Next.js (porta 3000) para o Django (porta 8000). | Adicionar `django-cors-headers~=4.3` ao `requirements.txt`, plugar `CorsMiddleware` no topo de `MIDDLEWARE` e configurar `CORS_ALLOWED_ORIGINS = ['http://localhost:3000']`. |
| **Endpoints Agregados (`/users/me/` e `/workspaces/`)** | O frontend precisa carregar perfil e árvore de trabalho (organização, projetos, squads) sem waterfalls nem múltiplos round-trips. | Criar `CurrentUserView` e `ActiveWorkspacesView` retornando payloads agregados tipados otimizados para a UI. |
| **Provisionamento do Frontend (`frontend/`)** | Evitar conflitos de pacotes de geradores genéricos como `create-next-app` padrão. | Espelhar a estrutura e manifestos de `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend` (`package.json`, `tsconfig.json`, `postcss.config.mjs`) e rodar `npm install`. |
| **Segregação de Usuários no `seed_demo.py`** | Os usuários de plataforma (`admin`, `suporte`, `ai-bot`) e a Organização Interna já são gerados na migração fundacional (`0001_initial.py`). O `seed_demo.py` não deve duplicá-los. | Restringir `seed_demo.py` exclusivamente à geração de dados de demonstração (tenants Acadêmico e Corporativo, projetos, squads e membros de exemplo). |
| **Adequação de `seed_demo.py` (PII e Blind Index)** | Atualmente os usuários demo são criados sem `full_name`, deixando o campo nulo e os `search_tokens` vazios. | Atualizar `seed_demo.py` para definir `full_name`, acionando a geração automática de `search_tokens` criptográficos. |
| **Adequação de `seed_demo.py` (Omnichannel)** | O novo app `omnichannel` precisa de dados para validação da UI e testes de chat. | `seed_demo.py` deve criar contatos e conversas mockadas vinculadas à organização via Soft FK (`organization_id = org.id`), respeitando o desacoplamento. |
| **Personas Canônicas no Seed (`docs/manuals/PERSONAS.md`)** | Evitar alucinações de dados fictícios discrepantes que quebrariam os testes e labs (`labs/lab_01` a `lab_04`). | O `seed_demo.py` deve criar exatamente a taxonomia de `PERSONAS.md`: `ufdemo` (6 deptos, 2 projetos, 4 squads, 7 personas) e `empresa-demo` (5 deptos, 1 projeto, 2 squads, 6 personas). |
| **Integridade da Containment Rule** | Evitar `ValidationError` do Django na associação de membros a squads. | O seed deve obrigatoriamente criar `ProjectMembership` antes de `SquadMembership` para o mesmo usuário e escopo. |
| **Dicotomia Estrita entre `Role` e `JobTitle`** | Separar permissões de sistema (`Role`) de cargos textuais visuais (`JobTitle`). | Modelos `Role` (permissões RBAC) e `JobTitle` (rótulo visual sem poder) criados e associados separadamente nas memberships. |
| **Contrato Agregado de Workspaces em 4 Níveis** | Permitir que o Dashboard do Next.js exiba a hierarquia contextualizada e os papéis matriciais do usuário. | Endpoint `GET /api/v1/workspaces/` retorna árvore hierárquica `Org -> Dept -> Proj -> Squad` com `job_title` e roles. |
| **Mock Omnichannel com Instâncias Padronizadas** | Coerência com a arquitetura de instâncias do WhatsApp Service (`docs/manuals/02-engineering/04_pipeline_whatsapp.md`). | `seed_demo.py` gera contatos com JIDs das personas, conversas com status `ACTIVE_AI` e mensagens de teste simulando `ai_control_ufdemo` e `ai_control_empresa_demo`. |
| **Gestão de Sessão no Frontend** | Evitar vazamento de privilégios ou persistência de estado entre trocas de usuário na mesma máquina. | Implementar limpeza preventiva de `sessionStorage`/`localStorage` e disparo de `logout()` ao acessar a rota `/login`, conforme feito em `vitalia-01/frontend/src/app/login/page.tsx`. |

---

## 4. Rastro de Pesquisa (Grounding)

| # | Afirmação / Fato Técnico | Verificado? | Fonte Local / Remota | Data |
|---|---|---|---|---|
| 1 | `vitalia-01` utiliza Next.js 16.1.7, React 19.2.0, Tailwind v4 e TanStack Query v5 | ✅ SIM | `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json:12-60` | 11/10/2026 |
| 2 | Agente React-Vinci especifica Next.js, shadcn/ui, RTK e Axios com interceptor | ✅ SIM | `AI-Control completo.md:5412-5423` e `7480-7540` | 11/10/2026 |
| 3 | `simplejwt` não está instalado no venv atual de `ai-control` | ✅ SIM | Execução `.venv/bin/python -c "import rest_framework_simplejwt"` retornou `ModuleNotFoundError` | 11/10/2026 |
| 4 | Usuários de plataforma (`admin`, `suporte`, `ai-bot`) são criados nas migrações fundacionais | ✅ SIM | `ai-control/core/migrations/0001_initial.py:401-490` | 11/10/2026 |
| 5 | `seed_demo.py` atual cria usuários demo mas não preenche `full_name` nem `search_tokens` | ✅ SIM | `ai-control/core/management/commands/seed_demo.py:34-46` | 11/10/2026 |
| 6 | `ai-control/core/models.py` possui `UserProfile` com `full_name` (EncryptedTextField) e `search_tokens` | ✅ SIM | `ai-control/core/models.py:453-520` | 11/10/2026 |
| 7 | Diretrizes de segurança de ponta (Data Vault Criptográfico e Blind Indexing) documentadas | ✅ SIM | `docs/04_Solution_Strategy.md` e `docs/08_Crosscutting_Concepts.md` | 11/10/2026 |
| 8 | Endpoint `CurrentUserView` (`/users/me/`) já está validado e funcional no produto de referência | ✅ SIM | `vitalia-01/backend/core/views.py:17-31` e `urls.py:14` | 11/10/2026 |
| 9 | Contrato de interceptor de Axios com renovação em fila (`isRefreshing`) | ✅ SIM | `vitalia-01/frontend/src/lib/api.ts:60-98` | 11/10/2026 |
| 10 | Suporte a Soft FKs no app `omnichannel` criado na Spec 001 | ✅ SIM | `specs/001-core-foundations/spec.md:14` e `tasks.md:38-40` | 11/10/2026 |
| 11 | Personas canônicas e taxonomia de departamentos/projetos/squads/JIDs documentadas | ✅ SIM | `docs/manuals/PERSONAS.md:1-53` e `docs/manuals/02-engineering/labs/_lab_base.py:30-48` | 11/10/2026 |
| 12 | Containment Rule e modelo RBAC matricial com `BaseMembership` documentados | ✅ SIM | `docs/manuals/02-engineering/01_modelo_de_dados_rbac.md:31-42` | 11/10/2026 |
| 13 | Separação conceitual entre `Role` (permissão) e `JobTitle` (cargo descritivo) | ✅ SIM | `docs/manuals/01-product/02_papeis_e_permissoes.md:12-24` | 11/10/2026 |
| 14 | Formato de instâncias Evolution API `ai_control_{org_slug}` e isolamento WhatsApp | ✅ SIM | `docs/manuals/02-engineering/04_pipeline_whatsapp.md:14-20` | 11/10/2026 |
| 15 | Proibição de `auth.Group` do Django após falha de isolamento multi-tenant (Post-Mortem 001) | ✅ SIM | `docs/manuals/03-history/postmortems/pm_001_falha_django_groups.md:30-33` | 11/10/2026 |

---

## 5. Diagrama de Arquitetura e Fluxo de Dados

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND: Next.js 16 + React 19 (App Router)                   │
│                                                                                        │
│   ┌──────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────┐   │
│   │   Páginas & Shell UI     │    │   Redux Toolkit (RTK)   │    │ TanStack Query  │   │
│   │   /login | / (Dashboard) │───▶│   Auth, Token & UI      │───▶│ Cache & Servidor│   │
│   └─────────────┬────────────┘    └─────────────────────────┘    └────────┬────────┘   │
└─────────────────┼─────────────────────────────────────────────────────────┼────────────┘
                  │                                                         │
                  │ Contrato Estrito: `api-schema.d.ts`                     │
                  │ (Gerado via: npm run api:generate)                      │
                  ▼                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                BACKEND SÍNCRONO: Django API Gateway (BFF Agregado)                     │
│                                                                                        │
│   • POST /api/v1/auth/token/          -> Autenticação JWT (Stateless)                  │
│   • POST /api/v1/auth/token/refresh/  -> Renovação em fila (isRefreshing)              │
│   • GET  /api/v1/users/me/            -> Perfil do usuário 4-Tier + Blind Index        │
│   • GET  /api/v1/workspaces/          -> Árvore ativa (Org, Dept, Proj, Squad)        │
│   • GET  /api/schema/                 -> Schema OpenAPI 3.0 (drf-spectacular)          │
└──────────────┬────────────────────────────────────────────────────────────┬────────────┘
               │                                                            │
               │ (Leituras Rápidas & Validações)                            │ (Disparo de Jobs)
               ▼                                                            ▼
┌──────────────────────────────────────────────┐        ┌────────────────────────────────┐
│         DATA VAULT (PostgreSQL)              │        │       ESTEIRA ASSÍNCRONA       │
│                                              │        │                                │
│ • django-crypto-fields (Criptografia At-Rest)│        │ • Redis (DB 2 Isolado)         │
│ • search_tokens (Blind Indexing Hashes)      │◀───────│ • Celery Workers               │
│ • Triggers Postgres (Ledger Imutável)        │        │ • IA / RAG & Context Lock      │
│ • Soft FKs (UUIDs entre Core e Omnichannel)  │        │ • Triagem & Ingestão Pesada    │
└──────────────────────────────────────────────┘        └────────────────────────────────┘
```
