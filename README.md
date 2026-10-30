# AI-Control — Plataforma de Atendimento Inteligente, CRM Omnichannel e Governança Multi-Tenant

> **Plataforma corporativa full-stack para governança hierárquica RBAC 4-Tier, CRM Omnichannel integrado ao WhatsApp (Evolution API v2), orquestrador híbrido de IA (Ollama local + Gemini), base vetorial RAG (pgvector) e proteção estrita de privacidade (Data Vault / LGPD).**

---

## 🎯 Visão Geral do Sistema

O **AI-Control** é uma plataforma corporativa e acadêmica orientada a governança estrita de dados, privacidade e automação inteligente de processos, composta por um backend em **Django 6.1 / Python 3.14 (ASGI/Daphne)** e uma interface moderna em **Next.js 16 (Turbopack) / React 19**.

| Módulo / Camada | Tecnologias Chave | Responsabilidade no Código |
|---|---|---|
| **Governança RBAC 4-Tier** | Django ORM, PostgreSQL | Hierarquia estrita: Organização → Departamento → Projeto → Squad, com validação de parentesco P3 e resolução de permissões por escopo. |
| **Frontend HUD & Dashboard** | Next.js 16, React 19, TailwindCSS v4, Redux Toolkit | Interface interativa com autenticação JWT, visualização da topologia 4-Tier, renovação resiliente de sessão e OpenAPI tipada. |
| **Omnichannel & CRM** | Django App (`omnichannel`), Channels, WebSockets | Web clone responsivo do WhatsApp, conversas com status (`ACTIVE_AI`, `ACTIVE_HUMAN`, `CLOSED`), transbordo humano, Copiloto preditivo e dados PII blindados. |
| **Hardening de Mensageria (Spec 007)** | Service Layer, Middleware ASGI, Evolution API v2 | Despacho síncrono com falha atômica (D2), retenção de texto no input em erro 502/400, descarte silencioso $O(1)$ de eventos `presence.update` e mascaramento de credenciais em logs (`?apikey=[REDACTED]`). |
| **Orquestrador de IA Híbrido** | Ollama local, Google Gemini, Redis | Agente em dois passos: classificação de domínio local (sem vazamento de PHI/PII) e geração de resposta com Safety Gate, memória de contexto em Redis e telemetria. |
| **Base de Conhecimento (RAG)** | `pgvector` (HNSW 768d) | Ingestão e busca vetorial de fragmentos de documentos com pré-filtragem estrita por escopo (`ORG`, `DEPT`, `PROJECT`, `SQUAD`, `PRIVATE`). |
| **Data Vault & LGPD** | `django-crypto-fields`, SHA-256 | Criptografia em repouso de dados sensíveis (`full_name`, `cpf`, `phone_number`), blind indexing para busca exata sem decriptação, `ConsentLog` e `AuditLog` imutável. |
| **Gamificação & Perfis** | Django ORM (`core.models`) | Perfis de usuário (`UserProfile`, `ParticipantProfile` com wallet e streaks, `ProfessionalProfile` com registros de conselho, `OnboardingProcess`). |

---

## 🏗️ Arquitetura do RBAC Hierárquico 4-Tier

O modelo de autorização do AI-Control opera em 4 níveis hierárquicos:

```text
PLATFORM             ← superadmin, suporte, bot
  └── ORGANIZATION   ← admin, gestor, supervisor, atendente, membro, convidado
        └── PROJECT  ← coordenação, membro, observador
              └── SQUAD  ← líder, membro, observador
```

### Princípios Fundamentais (Inviolabilidade P1–P5)

1. **P1 — Escopo Obrigatório:** Todo `Role` pertence rigidamente a um escopo (`PLATFORM`, `ORGANIZATION`, `PROJECT`, `SQUAD`).
2. **P2 — Resolução de Conflitos por Nível:** Roles possuem valor numérico `level` (ex.: 90 > 30) para priorização hierárquica.
3. **P3 — Regra de Contenção (Containment Rule):** Um vínculo em `ProjectMembership` exige `OrganizationMembership` ativa na organização pai. Um vínculo em `SquadMembership` exige `ProjectMembership` no projeto pai.
4. **P4 — Permissões Atômicas por Slug:** Validação baseada em slugs `domain.action` (ex.: `conversation.reply`, `org.manage_whatsapp`), verificadas dinamicamente no gateway e middleware.
5. **P5 — RAG Scoped:** A busca semântica no banco vetorial aplica pré-filtros relacionais para que o usuário ou bot só recupere fragmentos aos quais tenha acesso explícito.

---

## 🔄 Guia de Reset Completo, Reconstrução e Roteiro de Testes

Este roteiro fornece o procedimento passo a passo para reiniciar a infraestrutura do zero, recriar os containers e bancos de dados, semear o catálogo básico e executar o teste funcional completo de ponta a ponta.

---

### Fase 1: Limpeza Total e Recriação dos Containers

Execute os comandos abaixo a partir da raiz do repositório:

#### 1. Parar processos locais em execução
Encerre qualquer instância em execução no terminal do Django (`runserver` ou `daphne`), Celery ou Next.js (`Ctrl+C`).

#### 2. Derrubar e expurgar todos os containers e volumes Docker
```bash
docker compose down -v --remove-orphans
```
> [!WARNING]
> A flag `-v` remove os volumes persistentes do PostgreSQL, pgvector e Open-WebUI, garantindo um ambiente 100% limpo.

#### 3. Subir a infraestrutura em background
```bash
docker compose up -d
```
Verifique se todos os containers estão saudáveis:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
*Serviços esperados:*
- `ai-control_db` (PostgreSQL 16 + pgvector na porta `5432`)
- `ai-control_redis` (Redis Alpine na porta `6379`)
- `ai-control_evolution_api` (Evolution API v2 na porta `8081`)
- `ai-control_ollama` (Motor Ollama na porta `11434`)
- `ai-control_open_webui` (Interface WebUI na porta `4000`)

#### 4. Verificar o banco dedicado da Evolution API (`evl_db`)
A **Evolution API v2** (via Prisma ORM) detecta a ausência do banco na inicialização e o **cria automaticamente** com o schema `evolution`, pois o usuário `ai-control_admin` possui permissões no PostgreSQL.

Caso queira garantir ou criar manualmente de forma idempotente (sem erro caso já exista):
```bash
docker exec -i ai-control_db psql -U ai-control_admin -d ai-control_db -c "SELECT 'CREATE DATABASE evl_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'evl_db')\gexec"
```
Se a Evolution API tiver subido antes do banco estar acessível, reinicie o container:
```bash
docker compose restart evolution-api
```
#### 5. Baixar os modelos locais no Ollama
Como o volume persistente `ollama_data` foi recriado do zero, o container do Ollama inicia sem modelos na memória. Execute o download do modelo local configurado no `.env`:

```bash
# Baixar o modelo configurado no .env (recomendado para CPU/GPU: phi4-mini:latest ou qwen2.5:3b)
docker exec -it ai-control_ollama ollama pull phi4-mini:latest

# (Opcional) Modelo para busca semântica e embeddings no banco vetorial RAG (pgvector)
docker exec -it ai-control_ollama ollama pull nomic-embed-text
```
*Dica:* Para puxar dinamicamente o modelo ativo configurado no seu `.env`:
```bash
docker exec -it ai-control_ollama ollama pull $(grep VITALIA_LOCAL_MODEL .env | cut -d '=' -f2 | tr -d "'\"")
```
Confirme se os modelos foram baixados com sucesso:
```bash
docker exec -i ai-control_ollama ollama list
```

---

### Fase 2: Reconstrução e Injeção dos Dados Básicos

#### 1. Ativar o Virtualenv Python
```bash
source .venv/bin/activate
```

#### 2. Garantir as Variáveis de Ambiente
Certifique-se de que o arquivo `.env` existe na raiz (baseado em `.env.example`). Verifique se a variável `WHATS_GT_API_KEY` corresponde à chave do Evolution API:
```bash
grep -E "WHATS_GT_API_KEY|POSTGRES_DB|REDIS_URL" .env
```

#### 3. Executar as Migrações do Banco de Dados
```bash
python manage.py migrate
```
*Isto provisionará as tabelas do Core, membros 4-Tier, Data Vault, extensões do pgvector e modelos Omnichannel (`Contact`, `Conversation`, `Message`, `CopilotDraft`).*

#### 4. Atualizar a Senha do Superadministrador
```bash
python manage.py changepassword admin
# Digite uma senha segura (ou configure AICONTROL_ADMIN_PASSWORD no .env)
```

#### 5. Semear os Dados de Demonstração

##### A) Governança, RBAC e Estrutura Organizacional:
```bash
python manage.py seed_demo
```
*Cria a Organização da Plataforma, 2 organizações demo (acadêmica e corporativa), departamentos, projetos, squads e 13 personas de teste com a senha padrão `demo1234`.*

##### B) Dados de Demonstração do Omnichannel:
```bash
python manage.py seed_omnichannel_demo
```
*Cria contatos com telefones criptografados, conversas ativas (IA e Humano), histórico de mensagens e sugestões do Copiloto de IA.*

#### 6. Iniciar os Serviços da Aplicação

Abra terminais dedicados para cada componente:

- **Terminal 1 — Servidor ASGI / Daphne (Backend HTTP + WebSockets):**
  ```bash
  source .venv/bin/activate
  daphne -b 0.0.0.0 -p 8000 config.asgi:application
  ```

- **Terminal 2 — Worker Assíncrono do Celery:**
  ```bash
  source .venv/bin/activate
  celery -A config worker -l INFO -Q celery,omnichannel
  ```

- **Terminal 3 — Frontend Next.js (Dashboard + Omnichannel):**
  ```bash
  cd frontend
  npm run dev
  ```
  *O frontend estará disponível em `http://localhost:3000`.*

---

### Fase 3: Roteiro de Teste Prático (End-to-End Walkthrough)

Siga este roteiro no navegador para validar 100% das funcionalidades do sistema:

```
[Passo 1: Login] ──► [Passo 2: Dashboard/HUD] ──► [Passo 3: WhatsApp Pareamento] ──► [Passo 4: Chat & Hardening]
```

#### Passo 1: Autenticação no Frontend
1. Acesse `http://localhost:3000/login` no seu navegador.
2. Insira as credenciais do superadministrador:
   - **Usuário:** `admin`
   - **Senha:** A senha definida no passo 4 da Fase 2.
3. Clique em **Entrar**: você deve ver o toast de boas-vindas da Sonner e ser redirecionado para `/`.

#### Passo 2: Navegação no Dashboard & Governança 4-Tier
1. Na tela principal (`/`), observe o HUD analítico:
   - Contadores em tempo real de Organizações, Departamentos, Projetos e Squads.
   - O seletor de Organização no canto superior.
2. Teste o seletor alternando entre a "AI Control (Plataforma)" e as organizações demo criadas.
3. Observe os dados protegidos: campos com PII (nomes, telefones) são decodificados dinamicamente via tokens de sessão autorizados.

#### Passo 3: Acesso ao Módulo Omnichannel e Pareamento de WhatsApp
1. No menu de navegação lateral (ou pelo topo), acesse a rota `/omnichannel` (`http://localhost:3000/omnichannel`).
2. Observe o layout em 3 colunas (Splitter de redimensionamento dinâmico):
   - **Esquerda:** Lista lateral de conversas com abas de filtro (`Todas`, `Não lidas`, `IA`, `Minhas`, `Fixadas`), busca textual e contadores não lidos.
   - **Centro:** Timeline de mensagens, balões com status de entrega e caixa de entrada inferior (`ChatInput`).
   - **Direita:** Drawer lateral de detalhes do contato (abra clicando no avatar do cabeçalho).
3. **Parear WhatsApp via Smartphone:**
   - No topo do Omnichannel, clique no botão **Conectar WhatsApp** (ou no badge de status).
   - O modal `WhatsAppConnectionModal` será aberto exibindo o QR Code gerado pela Evolution API.
   - No seu smartphone, abra o WhatsApp → **Aparelhos Conectados** → **Conectar um aparelho**.
   - Aponte a câmera para o QR Code na tela.
   - **Validação de Hardening (FR-006):** Assim que a conexão for estabelecida, o modal exibirá o badge verde "WhatsApp Conectado" e **fechará automaticamente após 1.5 segundos**.

#### Passo 4: Teste de Conversação, Falha Atômica e Copiloto de IA
1. **Envio Normal com Confirmação:**
   - Selecione uma conversa na lista lateral.
   - Digite uma mensagem de teste no campo inferior e pressione `Enter`.
   - A mensagem é despachada síncronamente para a Evolution API com timeout de 5.0s, confirmada com `key.id`, gravada como `SENT` no banco e renderizada na timeline via WebSocket. O campo de digitação é limpo.
2. **Teste de Falha Atômica (D2 / SC-004):**
   - Para simular indisponibilidade, desconecte a internet do smartphone ou pare temporariamente a Evolution API:
     ```bash
     docker stop ai-control_evolution_api
     ```
   - No chat, digite: `Mensagem que não deve ser perdida`. Pressione `Enter`.
   - **Resultado esperado:**
     - A interface exibe um toast de erro: *"Não foi possível enviar a mensagem no WhatsApp. A instância pode estar desconectada..."* (HTTP 502 Bad Gateway).
     - **O texto `Mensagem que não deve ser perdida` PERMANECE intacto na caixa de texto**, permitindo que o operador retente o envio sem perder o que escreveu.
     - Nenhuma mensagem fantasma é inserida no PostgreSQL.
   - Reinicie a Evolution API após o teste:
     ```bash
     docker start ai-control_evolution_api
     ```
3. **Transbordo Humano / IA:**
   - No cabeçalho da conversa, clique em **Assumir Atendimento**.
   - O status transiciona para `ACTIVE_HUMAN`.
   - Se o Copiloto sugerir uma resposta, o `CopilotBanner` aparecerá no topo do chat.
   - Clique em **Inserir** para preencher o texto na caixa de entrada ou **Aprovar** para despachar imediatamente.
   - Clique em **Devolver para IA** para retornar o status da conversa para `ACTIVE_AI`.

---

## 💻 Frontend (Next.js 16 + React 19)

Localizado em `frontend/`, a interface conecta-se ao backend via REST e WebSockets:

- **Framework:** Next.js 16.4 (App Router com Turbopack), React 19.2.0, TailwindCSS v4.
- **Gerenciamento de Estado:** Redux Toolkit 2.11 + React-Redux 9.2 (tokens JWT, usuário ativo e preferências).
- **Cache & SWR:** TanStack React Query v5 (invalidação em tempo real sob eventos de WebSocket).
- **WebSockets Reativos:** Hook `useOmnichannelSocket` conectado a `ws://localhost:8000/ws/omnichannel/` com heartbeat ping/pong a cada 30s e reconexão exponencial com backoff.
- **Resiliência de Rede:** Cliente Axios com fila assíncrona para rotação de token via `/api/v1/auth/token/refresh/`.
- **Rotas Disponíveis:**
  - `/login`: Autenticação JWT com validação visual.
  - `/`: Dashboard analítico do HUD de Governança 4-Tier.
  - `/omnichannel`: Plataforma completa de atendimento e chat (WhatsApp Web clone).

---

## 🌐 Endpoints Principais da API REST e WebSockets

| Protocolo | Método | Endpoint | Descrição |
|---|---|---|---|
| HTTP | `POST` | `/api/v1/auth/token/` | Obtenção do par Access/Refresh Token JWT |
| HTTP | `POST` | `/api/v1/auth/token/refresh/` | Rotação e renovação do Access Token JWT |
| HTTP | `GET` | `/api/v1/users/me/` | Perfil decodificado do usuário ativo e permissões resolvidas |
| HTTP | `GET` | `/api/v1/workspaces/` | Árvore agregada de organizações, departamentos, projetos e squads |
| HTTP | `POST` | `/api/v1/webhook/whatsapp/` | Gateway de Webhooks da Evolution API com descarte silencioso $O(1)$ de presença |
| HTTP | `GET, POST` | `/api/v1/omnichannel/instance/` | Consulta de status e geração de QR Code da instância WhatsApp |
| HTTP | `GET` | `/api/v1/omnichannel/conversations/` | Listagem paginada de conversas com filtros por status, abas e busca |
| HTTP | `POST` | `/api/v1/omnichannel/conversations/{id}/takeover/` | Transbordo de atendimento da IA para o operador humano |
| HTTP | `POST` | `/api/v1/omnichannel/conversations/{id}/return-to-ai/` | Devolução do atendimento humano para a IA autônoma |
| HTTP | `POST` | `/api/v1/omnichannel/messages/` | Despacho outbound de mensagens com falha atômica (HTTP 502 em erro) |
| HTTP | `POST` | `/api/v1/omnichannel/copilot-drafts/{id}/approve/` | Aprovação e despacho de sugestão preditiva do Copiloto de IA |
| HTTP | `GET` | `/api/schema/` | Schema canônico OpenAPI 3.0 (drf-spectacular) |
| HTTP | `GET` | `/api/schema/swagger-ui/` | Interface visual Swagger UI para documentação |
| WS | `CONNECT` | `/ws/omnichannel/?token={jwt}&org_id={uuid}` | Canal WebSocket em tempo real para eventos de chat, presença e QR Code |

---

## 🧪 Bateria de Testes Automatizados

O projeto mantém cobertura rigorosa de testes no backend (`pytest`) e tipagem estrita no frontend (`TypeScript`):

```bash
# 1. Executar bateria completa de testes do backend (41 testes unitários e de integração)
.venv/bin/pytest tests/ -v

# 2. Testar o middleware de mascaramento de segredos e prevenção de vazamento
.venv/bin/pytest tests/core/test_sensitive_log_masking.py -v

# 3. Testar o gateway de webhooks e descarte silencioso O(1)
.venv/bin/pytest tests/core/test_webhook_whatsapp.py -v

# 4. Testar governança de organização padrão (P01 & P07)
.venv/bin/pytest tests/omnichannel/test_default_organization_service.py -v

# 5. Testar despacho outbound síncrono e falha atômica (D2 / HTTP 502)
.venv/bin/pytest tests/omnichannel/test_message_dispatch_service.py -v

# 6. Testar o RBAC Hierárquico 4-Tier
.venv/bin/pytest core/tests/test_rbac.py -v

# 7. Validar tipagem e build do Frontend Next.js
npm --prefix frontend run type-check
npm --prefix frontend run build
```

---

## 📁 Estrutura de Diretórios do Projeto

```text
ai-control/
├── config/                      # Configurações do Django (settings base/local, urls, asgi, wsgi, celery)
│   ├── asgi.py                  # Pipeline ASGI integrando HTTP e Channels (WebSockets)
│   ├── routing.py               # Roteamento WebSocket (/ws/omnichannel/)
│   └── settings/                # Configurações modulares (base.py com middlewares e CORS, local.py)
├── core/                        # Módulo central de Governança, RBAC, RAG e Orquestração
│   ├── adapters/                # Clientes e parsers de serviços externos (Evolution API v2)
│   ├── api/v1/                  # Endpoints REST (Auth JWT, Workspaces, Webhooks, Schemas)
│   ├── middleware/              # Pacote de middlewares (SensitiveLogMaskingMiddleware, RBAC)
│   ├── models.py                # Modelos relacionais (Organization, Project, Squad, Memberships, AuditLog)
│   ├── orchestrator/            # Orquestrador híbrido de IA (Ollama/Gemini), Safety Gate e telemetria
│   ├── services/                # Camada de serviços (EvolutionGatewayService, WhatsAppService)
│   └── tasks/                   # Workers assíncronos do Celery (whatsapp_tasks, checkpoint)
├── omnichannel/                 # Módulo de CRM Omnichannel e Mensageria
│   ├── api/                     # ViewSets DRF (ConversationViewSet, MessageViewSet, CopilotDraftViewSet)
│   ├── consumers/               # WebSocket Consumer (OmnichannelConsumer com canais de organização)
│   ├── management/commands/     # Comandos de seed (seed_omnichannel_demo, flush_omnichannel)
│   ├── models.py                # Modelos (Contact, ContactPhoneNumber, Conversation, Message, CopilotDraft)
│   └── services/                # Service Layer (MessageDispatchService, TakeoverService, DefaultOrganizationService)
├── frontend/                    # Aplicação Next.js 16 (React 19, TypeScript, TailwindCSS v4, Redux)
│   ├── src/app/                 # Rotas do App Router (/login, /, /omnichannel)
│   ├── src/components/          # Componentes visuais do HUD e Omnichannel (ChatInput, Timeline, Modal, Splitter)
│   ├── src/hooks/               # Custom hooks (useOmnichannel, useOmnichannelSocket, useWhatsAppInstance)
│   ├── src/lib/                 # Cliente Axios resiliente com refresh interceptor e OpenAPI schemas
│   └── src/store/               # Redux Toolkit store e authSlice
├── specs/                       # Especificações formais Vitalia SDD (007-omnichannel-hardening, etc.)
├── docs/                        # Documentação técnica e arquitetural (Arc42, manuais e ADRs)
├── tests/                       # Suíte unificada de testes (core, omnichannel)
├── docker-compose.yml           # Orquestração de containers (Postgres 16, pgvector, Redis, Evolution API, Ollama)
├── Makefile                     # Comandos rápidos de automação
├── manage.py                    # Utilitário CLI do Django
├── pytest.ini                   # Configuração de execução de testes do pytest
└── requirements.txt             # Dependências Python do backend
```

---

## 🔐 Privacidade e Conformidade Legal

- **Criptografia em Repouso:** Dados pessoais identificáveis (PII) são criptografados pelo `django-crypto-fields` utilizando chaves AES-256 e RSA em `crypto_keys/`.
- **Blind Indexing:** Buscas exatas por CPF, telefone e nome ocorrem através de tokens gerados por SHA-256 sem necessidade de descriptografar a base.
- **Zero Vazamento de Credenciais em Logs:** O middleware `SensitiveLogMaskingMiddleware` mascara qualquer ocorrência de `apikey`, `token` ou senhas em query strings e bodies (`[REDACTED]`).
- **Rastreabilidade e Logs Imutáveis:** Cada evento de autenticação, transbordo ou alteração de dados sensíveis gera registros em `AuditLog`, blindados contra alterações posteriores.
- **Conformidade com a LGPD:** Suporte a registros de consentimento explícito (`ConsentLog`) e concessão temporária de acesso (`DataAccessGrant`).

---

## 📝 Licença

Uso interno e restrito — Plataforma AI-Control.
