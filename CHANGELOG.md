# Changelog

## [0.2.0] - 2026-10-31

### ✨ Features
- **Frontend Next.js 16 & React 19:** Arquitetura reativa moderna com Turbopack, TanStack Query v5 e layout responsivo.
- **Módulo Omnichannel (WhatsApp Web Clone):**
  - Integração bidirecional com Evolution API v2 para atendimento em tempo real.
  - WebSockets (Django Channels) multi-tenant com isolamento estrito `private-org-{org_id}`.
  - Triagem de atendimento e alternância de controle (Takeover Humano vs IA Autônoma).
  - Sugestões preditivas do Copiloto de IA local (`phi4-mini`) com aprovação/edição direta pelo operador.
  - Gestão de leitura reativa desacoplada com delay perceptivo de 1.5s e verificação de foco de janela (`document.hasFocus()`, `visibilitychange`).
  - Alerta dinâmico na aba e barra de tarefas do sistema operacional via Web Notification API.
- **Autenticação e Multi-Tenancy 4-Tier:**
  - Autenticação JWT Stateless com interceptor Axios resiliente.
  - RBAC hierárquico com escopo em 4 níveis (Organization, Department, Project, Squad).
  - Carga canônica de demonstração via `seed_demo.py` e `seed_omnichannel_demo.py`.

### 🔒 Security & Hardening
- **Proteção Estrita de PII & Criptografia:** Sanitização e blindagem de dados sensíveis em logs e banco de dados via `django_crypto_fields`.
- **Mascaramento de Credenciais em Logs:** `SensitiveLogMaskingMiddleware` para expurgo automático de tokens, senhas e API keys da query string e URIs nos logs de acesso HTTP (Daphne/Channels).
- **Validação de Webhook:** Autenticação de instâncias Evolution API via header nativo `apikey`.
- **Descarte Silencioso $O(1)$:** Descarte de eventos de telemetria de alta frequência (`presence.update`, `contacts.*`) na view, poupando workers Celery.

### 🐛 Bug Fixes & Refactors
- **Unificação da Suíte Pytest:** Remoção do arquivo conflitante `omnichannel/tests.py`, permitindo execução atômica de todos os 130 testes com 100% de sucesso.
- **Compatibilidade Python 3.14 & Django 6.1:** Mocks assíncronos (`AsyncMock`) para Channel Layer e adequação de compatibilidade com DRF 3.18.3.
- **Next.js 16 Lint:** Adequação do script `lint` no `package.json` para alinhamento com a nova CLI do Next.js 16.

## [0.1.0] - 2026-10-08

### ✨ Features
- feat(docs): adicionado Sumário Executivo e Módulos Socráticos de Treinamento
