<!-- alinhamento1.md | Vitalia SDD v0.6.0 | 11-10-2026 09:30(GMT-04:00) -->
**alinhamento1.md | AI-Control v0.0.1 | 11-10-2026 09:30(GMT-04:00)**

# Prancheta de Alinhamento: Frontend v1 & Adequação do Seed Demo (v0.6.0)

Este documento estabelece o alinhamento arquitetural, funcional e de segurança para o marco prioritário (P0) do produto: **Adequação do comando `core/management/commands/seed_demo.py` e criação da primeira versão do frontend para consumo da API**.

---

## 1. Visão Geral e Fontes da Verdade Estrutural

Dando continuidade ao sucesso consolidado na Spec 001 (`001-core-foundations`), a base do `ai-control` opera com isolamento de Bounded Contexts (`core` e `omnichannel`), Soft Foreign Keys (`UUIDField`), RBAC Hierárquico 4-Tier e Ledger imutável com Triggers SQL PostgreSQL. 

Para este novo ciclo, as fontes da verdade são delimitadas sem qualquer ambiguidade:

1. **Backend Estrutural e Segurança Ativa**:
   - Repositório local `ai-control/` (Python 3.14+, Django 6.1.x, Django REST Framework 3.18.x, Celery 5.6.x, Redis 5.0+, PostgreSQL com extensão `pgvector`, e `django-crypto-fields==1.0.1`).
   - O backend é a **fonte única da verdade** para autorização, integridade de dados e proteção de privacidade.
2. **Frontend de Referência de Produto**:
   - Repositório `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend` — última versão homologada do produto, consolidando Next.js 16.1.7 (App Router), React 19.2.0, Tailwind CSS v4, shadcn/ui, TanStack Query v5.90, Redux Toolkit v2.11, React Hook Form, Zod e Sonner.
3. **Inteligência de Negócios e Agente de Frontend**:
   - O arquivo `AI-Control completo.md` (especialmente as diretrizes do Agente **React-Vinci**, linhas 5400–5446 e 7480–7650, bem como a lógica de orquestração de IA e agentes de triagem).
4. **Manuais de Arquitetura e Governança**:
   - Diretório `docs/` (`01_Introduction_and_Goals.md`, `04_Solution_Strategy.md` e `08_Crosscutting_Concepts.md`), que formalizam os princípios do PaaS Data Vault Agnóstico, Criptografia At-Rest e Blind Indexing.

---

## 2. Adequação Detalhada de `core/management/commands/seed_demo.py`

O comando `seed_demo.py` é a ferramenta primordial para que engenheiros e testers populam dados de demonstração no ambiente local e validem o frontend imediatamente. Ele é reestruturado sob as seguintes regras estritas:

### 2.1 Segregação Absoluta: Não Tocar em Usuários de Plataforma
- **Regra Fundamental**: Os usuários globais de plataforma (`admin`, `suporte`, `ai-bot`) e a Organização Interna da plataforma (`slug='ai-control'`, `is_internal=True`, `name='AI Control (Plataforma)'`) já são provisionados na migração fundacional (`core/migrations/0001_initial.py:401-490`).
- O `seed_demo.py` **NÃO DEVE** criar, alterar, redefinir senhas nem remover os usuários de plataforma.
- A flag `--flush` do `seed_demo.py` deve remover **estritamente** os dados de demonstração (slugs `ufdemo`, `empresa-demo` e seus respectivos usuários demo), garantindo a preservação total da Organização Interna e dos operadores de suporte e administração.

### 2.2 Semeamento da Hierarquia e Personas Canônicas (`docs/manuals/PERSONAS.md`)
O comando popula os dois perfis de negócio com fidelidade absoluta aos manuais de referência e aos laboratórios de engenharia (`docs/manuals/02-engineering/labs/`):

#### 1. Perfil Acadêmico: Universidade Federal Demo (`ufdemo`)
- **Organização**: `name="Universidade Federal Demo"`, `slug="ufdemo"`, `org_type=ACADEMIC`.
- **6 Departamentos**: 
  - `PROPESQ` (Pró-Reitoria de Pesquisa)
  - `PROEC` (Pró-Reitoria de Extensão)
  - `DCOMP` (Departamento de Computação)
  - `DENF` (Departamento de Enfermagem)
  - `FIN` (Departamento Financeiro)
  - `SGP` (Superintendência de Gestão de Pessoas)
- **2 Projetos e 4 Squads**:
  - Projeto `saude-digital` (Saúde Digital na Comunidade - Extensão, owner `PROEC`):
    - Squad `app-movel` (Squad App Móvel)
    - Squad `campo-coleta` (Squad Campo-Coleta)
  - Projeto `ia-triagem` (IA para Triagem Clínica - Pesquisa, owner `PROPESQ`):
    - Squad `modelagem` (Squad Modelagem)
    - Squad `dados-clinicos` (Squad Dados Clínicos)
- **7 Personas Canônicas**:
  | Username | Nome Completo (Blind Index) | JobTitle | Depto | Role Org | Roles Projeto / Squad | JID Contato |
  |---|---|---|---|---|---|---|
  | `prof.ana` | Profa. Ana Santos | Professor | DCOMP | `org_member` | `project_lead` em `saude-digital` (Líder `app-movel`); `project_member` em `ia-triagem` | `5511000000001@example.org` |
  | `prof.carlos` | Prof. Carlos Eduardo | Pró-Reitor | PROPESQ | `org_manager` | `project_lead` em `ia-triagem` | `prof.carlos@example.org` |
  | `prof.lucia` | Profa. Lúcia Oliveira | Professor | DENF | `org_member` | `project_lead` em `saude-digital` (Líder `campo-coleta`) | `prof.lucia@example.org` |
  | `aluno.joao` | João Victor Aluno | Aluno de Grad. | DCOMP | `org_member` | `project_member` em `saude-digital` (Bolsista `app-movel`) | `5511000000002@example.org` |
  | `aluna.maria` | Maria Clara Aluna | Aluno de Mestrado | DCOMP | `org_member` | `project_member` em `ia-triagem` (Analista `modelagem`) | `aluna.maria@example.org` |
  | `pesq.externo` | Dr. Roberto Pesquisador | Pesquisador Externo | *N/A* | `org_guest` | `project_member` em `ia-triagem` (Apenas visualização em `dados-clinicos`) | `pesq.externo@example.org` |
  | `tae.paulo` | Paulo Henrique TAE | Técnico Administrativo | FIN | `org_member` | Apenas nível organizacional | `tae.paulo@example.org` |

#### 2. Perfil Corporativo: Empresa Demo Ltda (`empresa-demo`)
- **Organização**: `name="Empresa Demo Ltda"`, `slug="empresa-demo"`, `org_type=COMPANY`.
- **5 Departamentos**:
  - `FIN` (Financeiro)
  - `RH` (Recursos Humanos)
  - `COM` (Comercial)
  - `ATD` (Atendimento)
  - `TI` (Tecnologia da Informação)
- **1 Projeto e 2 Squads**:
  - Projeto `implantacao-crm` (Implantação CRM WhatsApp - Corporativo, owner `TI`):
    - Squad `integracao` (Squad Integração)
    - Squad `conteudo-bot` (Squad Conteúdo do Bot)
- **6 Personas Canônicas**:
  | Username | Nome Completo (Blind Index) | JobTitle | Depto | Role Org | Roles Projeto / Squad | JID Contato |
  |---|---|---|---|---|---|---|
  | `gerente.ti` | Roberto Gerente TI | Gerente | TI | `org_manager` | `project_lead` em `implantacao-crm` (Líder `integracao`) | `5511000000003@example.org` |
  | `dev.rafa` | Rafael Dev Silva | Analista | TI | `org_member` | `project_member` em `implantacao-crm` (Membro `integracao`) | `dev.rafa@example.org` |
  | `supervisor.bia` | Beatriz Supervisora | Supervisor | ATD | `org_supervisor` | `project_lead` em `implantacao-crm` (Líder `conteudo-bot`) | `supervisor.bia@example.org` |
  | `atendente.leo` | Leonardo Atendente | Atendente | ATD | `org_agent` | Apenas nível organizacional (Acesso a Inbox) | `atendente.leo@example.org` |
  | `analista.rh` | Fernanda Analista RH | Analista | RH | `org_member` | Apenas nível organizacional | `analista.rh@example.org` |
  | `diretora.fin` | Patrícia Diretora FIN | Diretora | FIN | `org_admin` | `project_member` em `implantacao-crm` (Sponsor) | `diretora.fin@example.org` |

### 2.3 Regra de Integridade: Containment Rule Obrigatória
- Conforme documentado em `docs/manuals/02-engineering/01_modelo_de_dados_rbac.md`: **nenhum usuário pode ter vínculo em uma `SquadMembership` sem possuir vínculo ativo em `ProjectMembership` no projeto pai correspondente**.
- O `seed_demo.py` MUST criar o `ProjectMembership` antes de instanciar o `SquadMembership` para evitar exceções de validação (`ValidationError`) no método `clean()`.

### 2.4 Dicotomia Arquitetural: `Role` vs `JobTitle`
- `Role`: Papel sistêmico estático que rege as `Permission` associadas (`org_member`, `org_manager`, `org_admin`, `org_guest`, `project_lead`, `project_member`, `squad_lead`, `squad_member`).
- `JobTitle`: Instância de modelo descritivo que indica o cargo humano/textual (`Professor`, `Pró-Reitor`, `Gerente`, `Aluno de Grad.`, etc.). **Não concede permissões**, servindo para visualização na UI e metadados de RAG.

### 2.5 Preenchimento de PII e Blind Indexing Automático
- O `seed_demo.py` define o `full_name` de cada usuário demo em texto claro.
- O método `UserProfile.save()` aciona a criptografia at-rest (`django-crypto-fields`) e gera os hashes determinísticos no campo `search_tokens` via `generate_search_tokens()`, validando a funcionalidade de Blind Indexing (busca segura sem expor texto claro).

### 2.6 Semeamento de Dados Omnichannel via Soft FKs e Instâncias Reais
- Criação de `Contact` para os contatos com JIDs canônicos (`5511000000001@example.org`, `5511000000002@example.org`, `5511000000003@example.org`).
- Criação de `Conversation` com status `ACTIVE` (`status=Conversation.Status.ACTIVE_AI`), vinculada à organização cliente através de `organization_id = org.id` (`UUIDField`), mantendo o isolamento de Bounded Context sem Foreign Keys relacionais diretas.
- Criação de mensagens (`Message`) mockadas simulando o fluxo de atendimento da instância padrão `ai_control_{org_slug}` (`ai_control_ufdemo` e `ai_control_empresa_demo`), conforme documentado em `docs/manuals/02-engineering/04_pipeline_whatsapp.md`.

### 2.7 Saída Formatada e Feedback de Credenciais (Developer Experience)
Ao final da execução do comando, o console exibe uma tabela formatada com as credenciais:
- Senha unificada padrão: `demo1234` (configurável via `DEMO_PASSWORD`).
- Tabela com colunas: **Username**, **Senha**, **Organização**, **Papel 4-Tier**, **JobTitle**, **Projetos/Squads**.
- Suporte à flag `--flush` que remove estritamente os dados demo sem afetar os operadores de plataforma (`admin`, `suporte`, `ai-bot`) nem a Organização Interna (`slug='ai-control'`, `is_internal=True`).

---

## 3. Contrato de API, Arquitetura em Duas Frentes e Política de Schemas

Para conectar o Frontend Next.js à API Django com estabilidade e desempenho industrial, a comunicação é estruturada em duas frentes independentes:

### 3.1 Diagrama Conceitual da Arquitetura

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

### 3.2 Frente Síncrona: API Gateway Agregado (BFF)
Projetada para garantir tempos de resposta da interface inferiores a 200ms:
1. `POST /api/v1/auth/token/`:
   - Payload de entrada: `{ "username": "...", "password": "..." }`.
   - Resposta: `{ "access": "<jwt>", "refresh": "<jwt>" }`.
2. `POST /api/v1/auth/token/refresh/`:
   - Payload de entrada: `{ "refresh": "<jwt>" }`.
   - Resposta: `{ "access": "<jwt>" }`.
3. `GET /api/v1/users/me/`:
   - Resposta: Objeto consolidado do usuário:
     ```json
     {
       "id": 1,
       "username": "prof.ana",
       "email": "prof.ana@demo.local",
       "full_name": "Professora Ana Santos",
       "primary_organization": {
         "id": "c1f73b9e-...",
         "name": "Universidade Federal Demo",
         "slug": "ufdemo"
       },
       "platform_role": null,
       "memberships": {
         "organization": { "role": "org_member", "job_title": "professor", "department": "DCOMP" },
         "projects": [
           { "project_id": "...", "project_slug": "saude-digital", "role": "project_lead", "job_title": "project_coordinator" },
           { "project_id": "...", "project_slug": "ia-triagem", "role": "project_viewer", "job_title": "collaborating_researcher" }
         ],
         "squads": [
           { "squad_id": "...", "squad_slug": "app-movel", "role": "squad_lead", "job_title": "tech_lead" }
         ]
       }
     }
     ```
4. `GET /api/v1/workspaces/`:
   - Resposta: Retorna a árvore hierárquica acessível ao usuário para alimentar menus e seletores da UI:
     ```json
     {
       "workspaces": [
         {
           "id": "c1f73b9e-...",
           "name": "Universidade Federal Demo",
           "slug": "ufdemo",
           "org_type": "ACADEMIC",
           "role": "org_member",
           "departments": [
             { "id": "...", "name": "Depto. de Computação", "slug": "dcomp", "code": "DCOMP" }
           ],
           "projects": [
             {
               "id": "...",
               "name": "Saúde Digital na Comunidade",
               "slug": "saude-digital",
               "role": "project_lead",
               "squads": [
                 { "id": "...", "name": "Squad App Móvel", "slug": "app-movel", "role": "squad_lead" }
               ]
             }
           ]
         }
       ]
     }
     ```
5. **Configuração Mandatória de CORS (`django-cors-headers`)**:
   - Para permitir que o Next.js em `http://localhost:3000` comunique com o Django em `http://localhost:8000`, é **mandatório** adicionar `django-cors-headers~=4.3` ao `requirements.txt`.
   - Adicionar `'corsheaders'` em `INSTALLED_APPS` e `'corsheaders.middleware.CorsMiddleware'` no topo de `MIDDLEWARE` em `config/settings/base.py`.
   - Configurar `CORS_ALLOWED_ORIGINS = ['http://localhost:3000']`, `CORS_ALLOW_CREDENTIALS = True` e `CSRF_TRUSTED_ORIGINS = ['http://localhost:3000']`.
6. **Variável de Ambiente do Frontend**:
   - O frontend deve incluir `.env.local` contendo `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.
7. **Estratégia de Provisionamento do Frontend (`frontend/`)**:
   - Para evitar conflitos de versão do React 19 / Tailwind CSS v4, o diretório `frontend/` deve ser inicializado derivando sua estrutura e arquivos base (`package.json`, `tsconfig.json`, `postcss.config.mjs`, `components.json`) diretamente de `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend`, executando em seguida `npm install`. Proibido usar geradores genéricos como `create-next-app` com configurações padrão.
8. **Blindagem de UI**: A Frente Síncrona nunca aguarda inferência de LLM ou descriptografia em lote.

### 3.3 Frente Assíncrona: Esteira de Eventos (Celery + Redis DB 2)
- Toda a carga pesada de inteligência herdada do legado (orquestração de embeddings, RAG contextualizado por tenant, prompts de triagem, funil de desambiguação e tarefas periódicas de retenção) é processada exclusivamente em segundo plano.
- O Celery consome da fila isolada configurada na Spec 001 (`CELERY_OMNICHANNEL_REDIS_URL`, Redis DB 2), mantendo o Gateway síncrono livre de concorrência.

### 3.4 Política de Segurança da Rota `/api/schema/` e Swagger
A exposição do contrato da API é gerenciada conforme o ambiente para evitar riscos de **Information Disclosure (OWASP API9:2023)**:
- **Ambiente de Desenvolvimento (`DEBUG=True`)**:
  - A rota `GET /api/schema/` é mantida acessível localmente para que o script do frontend (`npm run api:generate`) obtenha o schema HTTP sem complexidade de autenticação CLI.
- **Ambiente de Produção (`DEBUG=False`)**:
  - A rota `SpectacularAPIView` e a interface Swagger UI (`/api/docs/`) são protegidas por `permission_classes = [IsAdminUser]`, impedindo que usuários anônimos ou atacantes façam engenharia reversa da API.
- **Modo Offline / Build-Time**:
  - Em esteiras de integração contínua (CI/CD) e builds estáticos de produção, o frontend não faz requisições HTTP para a API viva. O schema pode ser exportado offline via `python manage.py spectacular --file schema.yml` e o TypeScript gerado diretamente a partir do arquivo local.

### 3.5 Tipagem Dinâmica no Frontend (`api:generate`)
- No `package.json` do frontend, é configurado o script oficial:
  ```json
  "api:generate": "npx openapi-typescript http://localhost:8000/api/schema/ -o src/lib/api-schema.d.ts"
  ```
- O arquivo gerado `src/lib/api-schema.d.ts` alimenta os tipos globais (`UserProfile`, `Organization`, `Membership`, etc.), garantindo type safety absoluto entre Django e React.

---

## 4. Arquitetura da Primeira Versão do Frontend (`frontend/`)

O frontend v1 é estruturado na raiz do repositório em monorepo co-localizado (`frontend/`), espelhando a organização de arquivos já testada e validada em `vitalia-01/frontend`.

### 4.1 Estrutura de Arquivos
```text
frontend/
├── package.json               # Next.js 16, React 19, Tailwind v4, TanStack Query v5, RTK
├── tsconfig.json              # Configurações TypeScript com path alias @/*
├── postcss.config.mjs         # Suporte ao Tailwind CSS v4
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout com AppProviders e fonte Inter/Sans
│   │   ├── page.tsx           # Dashboard Shell inicial (NavBar, Contexto do Usuário, Logout)
│   │   ├── globals.css        # Variáveis CSS e tokens de design do shadcn/ui
│   │   └── login/
│   │       └── page.tsx       # Tela de autenticação reativa com Zod e Sonner
│   ├── components/
│   │   └── ui/                # Botões, Cards, Inputs, Toaster e Dropdowns (shadcn/ui)
│   ├── features/
│   │   └── auth/
│   │       ├── authSchema.ts  # Schema Zod para login (username e password)
│   │       └── authApi.ts     # Funções Two-Step Login (loginAndFetchUser)
│   ├── lib/
│   │   ├── api.ts             # Cliente Axios com interceptors de Bearer token e auto-refresh
│   │   ├── api-schema.d.ts    # Tipos gerados automaticamente pelo drf-spectacular
│   │   └── utils.ts           # Utilitários de classe cn() (clsx + tailwind-merge)
│   ├── providers/
│   │   └── AppProviders.tsx   # Redux Provider, QueryClientProvider, Sonner Toaster
│   ├── store/
│   │   ├── index.ts           # Configuração do Redux Toolkit store
│   │   └── slices/
│   │       └── authSlice.ts   # Estado de tokens, usuário logado e persistência
│   └── types/
│       └── auth.ts            # Aliases e interfaces estritas derivadas do api-schema
```

### 4.2 Comportamento da Tela de Login (`/login`)
- **Limpeza Preventiva de Sessão**: Ao renderizar a tela de login, qualquer resquício de sessão anterior é expurgado (`dispatch(logout())`, limpeza de `sessionStorage`/`localStorage`), prevenindo vazamento de menus administrativos entre trocas de usuário na mesma máquina.
- **Validação com Zod**: Validação em tempo real de preenchimento dos campos `username` e `password`.
- **Feedback não-bloqueante**: Utilização de toasts do Sonner para erros amigáveis de credenciais inválidas ou status de conexão.
- **Two-Step Login**:
  1. Chamada a `POST /api/v1/auth/token/` para obter `access` e `refresh`.
  2. Chamada imediata com o Bearer token a `GET /api/v1/users/me/` para obter a identidade e memberships do usuário.
  3. Despacho dos dados para o `authSlice` e redirecionamento para o Dashboard (`/`).

### 4.3 Comportamento do Cliente Axios (`lib/api.ts`)
- **Request Interceptor**: Anexa automaticamente o token JWT no cabeçalho `Authorization: Bearer <access>` a partir do Redux (com fallback em `sessionStorage`).
- **Response Interceptor Resiliente**:
  - Ao receber status `401 Unauthorized`, intercepta a requisição e ativa a fila de espera `isRefreshing`.
  - Dispara requisição a `POST /api/v1/auth/token/refresh/` utilizando o `refreshToken`.
  - Em caso de sucesso, atualiza o token na store, reprocessa as requisições enfileiradas e reenvia a requisição original de forma imperceptível para o usuário.
  - Em caso de expiração do refresh token, executa `logout()` e redireciona para `/login`.

---

## 5. Diretrizes Anti-Alucinação para a Nova Fase

Para que as etapas seguintes de especificação (`spec.md`), planejamento (`plan.md`) e implementação (`tasks.md`) mantenham o padrão de excelência:

1. **Stack Tecnológica Bloqueada**: Proibição terminante de sugerir Vite, Tailwind v3 legado, ou bibliotecas genéricas de autenticação como Next-Auth. A stack oficial é rigorosamente **Next.js 16+ (App Router), Tailwind CSS v4, shadcn/ui, TanStack Query v5 e Redux Toolkit**.
2. **Imutabilidade da Spec 001**: O diretório `specs/001-core-foundations/` é imutável. Todo o trabalho novo viverá na nova spec (`specs/002-frontend-seed/`).
3. **Respeito aos Bounded Contexts com Soft FKs**: O app `omnichannel` nunca deve receber chaves estrangeiras relacionais (`models.ForeignKey`) apontando para `core.Organization` ou `core.UserProfile`. A comunicação permanece 100% via `UUIDField`.
4. **Isolamento Criptográfico de PII**: A UI nunca recebe dados criptografados brutos (ciphertexts RSA). A API entrega campos limpos sob sessão autenticada autorizada e aplica mascaramento quando a permissão for restrita.
5. **Não Duplicação de Usuários de Plataforma**: O `seed_demo.py` nunca tenta criar `admin`, `suporte` ou `ai-bot`.

---

## 6. Critérios de Sucesso e Mapeamento de Fontes

| Pilar | Fonte da Verdade | Critério de Sucesso Mensurável |
|---|---|---|
| **Segurança e RBAC** | `ai-control/core/models.py` | Modelos mantêm criptografia at-rest, Blind Indexing e Triggers no banco sem regressão. |
| **Isolamento de Bootstrap** | `core/migrations/0001_initial.py` | Usuários de plataforma (`admin`, `suporte`, `ai-bot`) intocados pelo `seed_demo.py`. |
| **Carga de Demonstração** | `core/management/commands/seed_demo.py` | Execução de `python manage.py seed_demo` cria perfis acadêmico e corporativo, preenche `full_name` com Blind Index, gera conversas mockadas no omnichannel e exibe tabela ASCII de logins. |
| **Contrato da API** | `AI-Control completo.md:315-330` e `drf-spectacular` | Endpoints `/api/v1/auth/token/`, `/api/v1/users/me/` e `/api/schema/` respondem conforme especificação OpenAPI 3.0. |
| **Geração de Tipos** | `vitalia-01/frontend/package.json:10` | Script `npm run api:generate` gera `src/lib/api-schema.d.ts` sem erros de parsing. |
| **Frontend v1** | `vitalia-01/frontend/src/` | Usuário acessa `http://localhost:3000/login`, autentica com `prof.ana` / `demo1234` e visualiza o Dashboard com tenant e perfil 4-Tier carregados via API. |
