# AI-Control — Plataforma de Atendimento Inteligente, CRM Omnichannel e Governança Multi-Tenant

> **Backend e Frontend unificados para atendimento automatizado com IA, CRM integrado ao WhatsApp (Evolution API), base vetorial (RAG) e governança hierárquica RBAC 4-Tier.**

---

## 🎯 Visão Geral do Sistema

O **AI-Control** é uma plataforma full-stack orientada a governança, privacidade e automação inteligente, composta por um backend robusto em **Django 6.1 / Python 3.14** e uma interface de usuário moderna em **Next.js 16 / React 19**.

| Módulo / Camada | Tecnologias Chave | Responsabilidade no Código |
|---|---|---|
| **Governança RBAC 4-Tier** | Django ORM, PostgreSQL | Hierarquia estrita: Organização → Departamento → Projeto → Squad, com validação de parentesco P3 e resolução de permissões por escopo. |
| **Frontend HUD & Dashboard** | Next.js 16, React 19, TailwindCSS v4, Redux Toolkit | Interface interativa com autenticação JWT, visualização da topologia organizacional 4-Tier, interceptor resiliente de refresh e consumo de OpenAPI tipada. |
| **Omnichannel & CRM** | Django App (`omnichannel`), Evolution API | Gestão de contatos com PII criptografada, conversas com status de atendimento (`ACTIVE_AI`, `WAITING_HUMAN`, `ACTIVE_HUMAN`) e histórico de mensagens. |
| **Orquestrador de IA Híbrido** | Ollama local, Google Gemini, Redis, LangChain concepts | Agente em dois passos: classificação de domínio local (sem vazamento de PHI/PII) e geração de resposta com Safety Gate, memória de contexto em Redis e telemetria append-only. |
| **Base de Conhecimento (RAG)** | `pgvector` (HNSW 768d) | Ingestão e busca vetorial de documentos e chunks com pré-filtragem estrita por escopo de visibilidade (`ORG`, `DEPT`, `PROJECT`, `SQUAD`, `PRIVATE`). |
| **Data Vault & LGPD** | `django-crypto-fields`, SHA-256 | Criptografia em repouso de dados sensíveis (`full_name`, `cpf`, `phone_number`), blind indexing para busca sem decriptação, consentimento (`ConsentLog`) e `AuditLog` imutável. |
| **Gamificação & Perfis** | Django ORM (`core.models`) | Perfis especializados (`UserProfile`, `ParticipantProfile` com wallet e streaks, `ProfessionalProfile` com registros de conselho, `OnboardingProcess`). |

---

## 🏗️ Arquitetura do RBAC Hierárquico 4-Tier

O modelo de autorização do AI-Control opera em 4 níveis hierárquicos:

```
PLATFORM             ← superadmin, suporte, bot
  └── ORGANIZATION   ← admin, gestor, supervisor, atendente, membro, convidado
        └── PROJECT  ← coordenação, membro, observador
              └── SQUAD  ← líder, membro, observador
```

### Princípios Fundamentais (Inviolabilidade P1–P5)

1. **P1 — Escopo Obrigatório:** Todo `Role` pertence rigidamente a um escopo (`PLATFORM`, `ORG`, `PROJECT`, `SQUAD`).
2. **P2 — Resolução de Conflitos por Nível:** Roles possuem valor numérico `level` (ex.: 90 > 30) para priorização hierárquica.
3. **P3 — Regra de Contenção (Containment Rule):** Um vínculo em `ProjectMembership` exige `OrganizationMembership` ativa na organização pai. Um vínculo em `SquadMembership` exige `ProjectMembership` no projeto pai.
4. **P4 — Permissões Atômicas por Slug:** Validação baseada em slugs `domain.action` (ex.: `conversation.send`, `document.read`), verificadas dinamicamente no gateway e middleware.
5. **P5 — RAG Scoped:** A busca semântica no banco vetorial aplica pré-filtros relacionais para que o usuário ou bot só recupere fragmentos aos quais tenha acesso explícito.

### Catálogo Pré-Semeado (Migrations & Seed)

As migrações nativas (`core/migrations/0008_*` e `0009_*`) provisionam automaticamente:
- **30 Permissões** divididas por domínios (`org.*`, `project.*`, `squad.*`, `document.*`, `conversation.*`, `bot.*`).
- **15 Roles** distribuídos entre plataforma, organização, projeto e squad.
- **40 Cargos (JobTitles)** categorizados em corporativos, acadêmicos, clínicos e operacionais.
- **Organização Interna:** "AI Control (Plataforma)" com 8 departamentos administrativos.
- **Usuários de Sistema:** `admin` (superadmin), `suporte` e `ai-bot`.

---

## 🧠 Orquestrador de IA e Integração WhatsApp

O fluxo de atendimento inteligente está implementado em `core/orchestrator/` e nos serviços de mensageria:

```
[WhatsApp / Usuário]
         │
         ▼
[Evolution API] ──(Webhook HTTP POST)──► [WebhookGatewayView (/api/v1/webhook/whatsapp/)]
                                                           │
                                                           ▼ (Enfileira Celery)
                                            [process_whatsapp_webhook_task]
                                                           │
                                                           ▼
                                               [Orquestrador de IA]
                                               ├── 1. Carrega histórico Redis (TTL 24h)
                                               ├── 2. Classificação local (Ollama)
                                               ├── 3. Safety Gate (Regex + HITL)
                                               ├── 4. Geração (Gemini Flash / Ollama)
                                               ├── 5. Telemetria (wa_transactions.jsonl)
                                               └── 6. Disparo via EvolutionGatewayService
```

- **Classificação Local:** O domínio (`clinical` vs `general`) é avaliado primeiramente no Ollama local, garantindo que dados altamente sensíveis não sejam despachados para serviços em nuvem sem consentimento.
- **Safety Gate:** Se termos de alerta médico ou risco forem detectados, a mensagem é mantida como `DRAFT` para auditoria humana (princípio EU AI Act / HITL).
- **Interface de Pareamento WhatsApp:** O Django Admin inclui uma tela de visualização de QR Code em `/admin/core/debug/qr/` para inicializar a instância da Evolution API.

---

## 💻 Frontend (Next.js 16 + React 19)

Localizado no diretório `frontend/`, a interface conecta-se diretamente à API REST:

- **Framework:** Next.js 16.1.7 (App Router), React 19.2.0, TailwindCSS v4.
- **Gerenciamento de Estado:** Redux Toolkit 2.11 + React-Redux 9.2 (controle de sessão, tokens JWT e usuário ativo).
- **Resiliência de Rede:** Cliente Axios centralizado (`frontend/src/lib/api.ts`) com fila assíncrona de requisições pendentes durante a renovação automática do access token (`/api/v1/auth/token/refresh/`).
- **Contratos e Tipagem:** Tipos gerados diretamente do OpenAPI do backend (`openapi-typescript` alimentando `src/lib/api-schema.d.ts`).
- **Telas Prontas:**
  - `/login`: Autenticação via JWT com feedback visual (Sonner toasts).
  - `/` (Dashboard / HUD): Painel analítico com contadores de organizações, departamentos, projetos e squads; seletor interativo de organizações; decodificação visual de campos criptografados; e inspetor de payload REST em tempo real.

---

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.14 (ou Python 3.12+)
- Node.js 20+ e npm
- Docker e Docker Compose (para PostgreSQL, Redis e Evolution API)

### 1. Subir Infraestrutura de Apoio (Docker)

O projeto possui um arquivo `docker-compose.yml` pré-configurado:

```bash
docker compose up -d
```
Serviços provisionados:
- **PostgreSQL 15+ com pgvector** (porta `5432`)
- **Redis** (porta `6379`)
- **Evolution API v2.2.3** (porta `8081` para comunicação com WhatsApp)

### 2. Configurar o Backend

```bash
# 1. Ativar o virtualenv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Ajuste DJANGO_SECRET_KEY, DATABASE_URL, REDIS_URL, WHATS_GT_* conforme necessário

# 4. Executar migrações
python manage.py migrate

# 5. Criar/atualizar senha do administrador
python manage.py changepassword admin

# 6. (Opcional) Popular dados de demonstração
python manage.py seed_demo
```

### 3. Rodar o Backend

```bash
# Servidor HTTP / Django de desenvolvimento
python manage.py runserver 0.0.0.0:8000

# (Para suporte completo a WebSockets e Channels via ASGI)
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Worker assíncrono do Celery
celery -A config worker -l info
```

### 4. Configurar e Rodar o Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento (porta 3000)
npm run dev

# (Opcional) Atualizar tipagens da API a partir do backend ativo
npm run api:generate
```

---

## 🌐 Endpoints Principais da API REST

A API do AI-Control implementa autenticação JWT Stateless e documentação OpenAPI 3.0 interativa:

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/v1/auth/token/` | Obtenção do par Access/Refresh Token JWT |
| `POST` | `/api/v1/auth/token/refresh/` | Rotação e renovação do Access Token JWT |
| `GET` | `/api/v1/users/me/` | Perfil decodificado do usuário logado e papéis |
| `GET` | `/api/v1/workspaces/` | Árvore agregada de organizações, departamentos, projetos e squads |
| `POST` | `/api/v1/webhook/whatsapp/` | Webhook receptor de eventos e mensagens da Evolution API |
| `GET` | `/api/schema/` | Schema canônico OpenAPI 3.0 (drf-spectacular) |
| `GET` | `/api/schema/swagger-ui/` | Interface interativa Swagger UI |
| `GET` | `/admin/core/debug/qr/` | Interface visual no Django Admin para pareamento QR Code da Evolution API |

*Nota sobre segurança OpenAPI:* Em modo de produção (`DEBUG=False`), os endpoints de documentação (`/api/schema/*`) exigem autenticação administrativa com Bearer Token JWT (OWASP API9:2023).

---

## 🧪 Testes Automatizados

O repositório utiliza `pytest` com cobertura para os modelos, serviços e APIs:

```bash
# Executar a suíte de testes do core
.venv/bin/pytest core/tests/ -v

# Testes específicos do RBAC Hierárquico
.venv/bin/pytest core/tests/test_rbac.py -v

# Testes da API v1 e autenticação JWT
.venv/bin/pytest core/tests/test_api_v1.py -v

# Testes do gerador OpenAPI Spectacular
.venv/bin/pytest core/tests/test_api_schema.py -v

# Testes do comando seed_demo
.venv/bin/pytest core/tests/test_seed_demo.py -v
```

---

## 📁 Estrutura de Diretórios Real do Projeto

```
ai-control/
├── config/                  # Configurações do Django (settings base/local, urls, asgi, wsgi, celery)
├── core/                    # Módulo central de Governança, RBAC, RAG, Perfis e Orquestração
│   ├── adapters/            # Clientes para serviços externos (Evolution API)
│   ├── api/v1/              # Endpoints REST (Auth JWT, CurrentUser, Workspaces, Webhooks, Schemas)
│   ├── management/commands/ # Comandos de gestão (seed_demo)
│   ├── migrations/          # Migrações do banco de dados e sementes do catálogo
│   ├── models.py            # Modelos relacionais (Organization, Project, Squad, Memberships, Document, etc.)
│   ├── orchestrator/        # Agente de IA, provedores (Ollama/Gemini), Safety Gate, memória e telemetria
│   ├── services/            # Camada de serviços (EvolutionGateway, WhatsAppService, ContactService)
│   ├── tasks/               # Workers em background (Celery)
│   └── tests/               # Testes automatizados do core
├── omnichannel/             # Módulo isolado de CRM e Mensageria (Contact, Conversation, Message)
├── frontend/                # Aplicação Next.js 16 (React 19, TypeScript, TailwindCSS v4, Redux)
│   ├── src/app/             # Páginas (Dashboard /, Login /login) e layout global
│   ├── src/components/      # Componentes de interface (Navbar, Providers)
│   ├── src/lib/             # Cliente Axios com interceptor e tipagens api-schema.d.ts
│   ├── src/store/           # Redux Toolkit store e authSlice
│   └── src/types/           # Definições de tipos TypeScript
├── docs/                    # Documentação técnica e arquitetural (Arc42, manuais, histórico e ADRs)
├── specs/                   # Especificações estruturadas SDD (especificações, planos e checklists)
├── scripts/                 # Scripts utilitários de manutenção
├── docker-compose.yml       # Orquestração de containers (Postgres, pgvector, Redis, Evolution API)
├── Makefile                 # Comandos rápidos de automação
├── manage.py                # Utilitário CLI do Django
├── pytest.ini               # Configuração do executor de testes
└── requirements.txt         # Dependências Python do backend
```

---

## 🔐 Privacidade e Conformidade Legal

- **Criptografia em Repouso:** Dados pessoais identificáveis (PII) são criptografados pelo `django-crypto-fields` utilizando chaves em `crypto_keys/`.
- **Blind Indexing:** Buscas exatas por CPF, telefone e nome ocorrem através de tokens gerados por SHA-256 sem necessidade de descriptografar a base.
- **Rastreabilidade e Logs Imutáveis:** Cada evento de criação, leitura ou alteração de dados sensíveis gera registros em `AuditLog`, blindados contra alterações posteriores.
- **Conformidade com a LGPD:** Suporte a registros de consentimento explícito (`ConsentLog`) e concessão temporária de acesso (`DataAccessGrant`).

---

## 📝 Licença

Uso interno e restrito — Plataforma AI-Control.
