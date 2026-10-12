<!-- research.md | Vitalia SDD v0.6.0 | 11-10-2026 20:40(GMT-04:00) -->
**research.md | AI-Control v0.0.1 | 11-10-2026 20:40(GMT-04:00)**

# Technical Research: Frontend v1 & Adequação do Seed Demo

Este documento formaliza as decisões de arquitetura e tecnologia (ADRs) fundamentadas em evidências concretas, testes locais e fontes autoritativas para o marco P0.

---

### Decisão: Separação de Arquitetura em Duas Frentes (BFF Síncrono vs Esteira Assíncrona)
- **Escolhido**: API Gateway Síncrono no Django (rotas agregadas `/api/v1/users/me/` e `/api/v1/workspaces/` com resposta < 150ms) segregado da Esteira Assíncrona de IA/Ingestão (Celery Workers + Redis DB 2 isolado).
- **Verificado em**: `ai-control/docs/04_Solution_Strategy.md:10-14` e `ai-control/docs/10_Quality_Requirements.md:16-20` em 11-10-2026.
- **Justificativa**: Conforme o requisito de qualidade do produto (Quality Requirement 3), a interface do usuário não pode sofrer bloqueios ou engasgos de latência causados por inferência de LLM ou descriptografia massiva em lote. A frente síncrona utiliza consultas otimizadas com `select_related` e `prefetch_related` para atender a UI instantaneamente.
- **Alternativas**:
  - *Processamento síncrono inline de IA*: Rejeitado porque bloquearia o ciclo de request/response HTTP (SLA de 150ms violado).
  - *Microserviço separado de autenticação*: Rejeitado nesta fase para evitar sobrecarga prematura de infraestrutura e orquestração de rede.

---

### Decisão: Stack de Frontend e Padrão de Provisionamento
- **Escolhido**: Next.js 16.1.7 (App Router), React 19.2.0, Tailwind CSS v4, shadcn/ui, TanStack Query v5.90, Redux Toolkit v2.11 e Axios com interceptor resiliente, provisionado por espelhamento estrutural da base homologada em `vitalia-01/frontend`.
- **Verificado em**: `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json:1-60` e `AI-Control completo.md:5412-5446` em 11-10-2026.
- **Justificativa**: A versão de referência de produto (`vitalia-01`) já estabilizou a coexistência entre React 19, Tailwind v4 e TanStack Query v5. Usar geradores genéricos como `create-next-app` padrão introduziria divergências de dependências com o agente React-Vinci e com o shell do dashboard.
- **Alternativas**:
  - *Vite + React SPA*: Rejeitado taxativamente pela Constituição do Arquiteto e pelas diretrizes do produto (falta de App Router e SSR corporativo).
  - *Next-Auth / Auth.js*: Rejeitado porque a autorização e gestão de tokens deve residir estritamente no backend Django (JWT stateless) e na store centralizada do Redux Toolkit.

---

### Decisão: Contrato OpenAPI 3.0 Dinâmico e Geração Estrita de Tipos
- **Escolhido**: `drf-spectacular~=0.30.0` gerando o schema OpenAPI dinâmico em `GET /api/schema/`, e script `npm run api:generate` no frontend utilizando `npx openapi-typescript http://localhost:8000/api/schema/ -o src/lib/api-schema.d.ts`.
- **Verificado em**: `ai-control/requirements.txt:21` e `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json:10` em 11-10-2026.
- **Justificativa**: Elimina desalinhamentos de dados entre Django e Next.js. O frontend importa `components["schemas"]["UserProfile"]` diretamente de `src/lib/api-schema.d.ts`, garantindo type-safety estrito em tempo de compilação sem necessidade de interfaces manuais duplicadas.
- **Alternativas**:
  - *drf-yasg*: Rejeitado por obsolescência com OpenAPI 3.0 e incompatibilidade com Django 5+/6+.
  - *Interfaces TypeScript manuais*: Rejeitado devido ao alto risco de drift entre modelos do ORM e tipos do frontend.

---

### Decisão: Segurança Condicional do Schema OpenAPI por Ambiente (OWASP API9:2023)
- **Escolhido**: Segurança condicional configurada dinamicamente via `SPECTACULAR_SETTINGS`: quando `DEBUG=True` (desenvolvimento), a rota `/api/schema/` opera aberta (`permission_classes=[AllowAny]`) para viabilizar a geração de tipos localmente via CLI; quando `DEBUG=False` (produção), a rota exige privilégio administrativo (`permission_classes=[IsAdminUser]`) e declara esquema Bearer JWT.
- **Verificado em**: `https://drf-spectacular.readthedocs.io/en/latest/settings.html` e OWASP API Security Top 10 (API9:2023 - Improper Inventory Management) em 11-10-2026.
- **Justificativa**: Protege o PaaS Data Vault contra exploração de rotas internas e vazamento da topologia do banco de dados em ambientes produtivos expostos à internet.
- **Alternativas**:
  - *Desativar totalmente o schema em produção*: Rejeitado porque operadores e ferramentas de auditoria precisam inspecionar contratos via token admin.
  - *Deixar aberto publicamente em produção*: Rejeitado por violação de segurança e bloqueio pelo SDDJudge.

---

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
- **Justificativa**: Permite que o frontend Next.js (porta 3000) envie requisições HTTP e tokens JWT com suporte a credenciais para a API Django (porta 8000), bloqueando qualquer outra origem não autorizada.
- **Alternativas**:
  - *CORS_ORIGIN_ALLOW_ALL = True*: Rejeitado por severa falha de segurança (violação do princípio P06/P07).
  - *Proxy reverso Nginx obrigatório em dev local*: Rejeitado para preservar agilidade no ciclo de desenvolvimento local.

---

### Decisão: Autenticação JWT Stateless com `djangorestframework-simplejwt`
- **Escolhido**: `djangorestframework-simplejwt~=5.3.1` provisionando `POST /api/v1/auth/token/` (emissão de access/refresh) e `POST /api/v1/auth/token/refresh/` (rotação de access token).
- **Verificado em**: `https://pypi.org/project/djangorestframework-simplejwt/` e `/home/andre/projetos/assistidos/ai-base/vitalia-01/backend/requirements.txt:6` em 11-10-2026.
- **Justificativa**: Padrão stateless leve, escalável horizontalmente e 100% aderente ao interceptor de requisição e fila de refresh (`isRefreshing`) do Axios em `frontend/src/lib/api.ts`.
- **Alternativas**:
  - *Session-based Auth (Cookies de sessão do Django)*: Rejeitado devido à complexidade de CSRF e estado compartilhado em arquiteturas de API desacopladas.
  - *Tokens opacos em banco (`rest_framework.authtoken`)*: Rejeitado por exigir consulta ao banco relacional em cada requisição (overhead desnecessário).

---

### Decisão: Fidelidade Canônica de Personas e RBAC 4-Tier no `seed_demo.py`
- **Escolhido**: Semeamento rigoroso das 13 personas canônicas, 11 departamentos, 3 projetos e 6 squads especificados em `docs/manuals/PERSONAS.md` e `docs/manuals/02-engineering/labs/`:
  - **`ufdemo` (ACADEMIC)**: `prof.ana`, `prof.carlos`, `prof.lucia`, `aluno.joao`, `aluna.maria`, `pesq.externo`, `tae.paulo`.
  - **`empresa-demo` (COMPANY)**: `gerente.ti`, `dev.rafa`, `supervisor.bia`, `atendente.leo`, `analista.rh`, `diretora.fin`.
  - Respeito estrito à **Containment Rule**: `ProjectMembership` criada obrigatoriamente antes de `SquadMembership`.
  - Preservação intacta da Organização Interna (`slug='ai-control'`, `is_internal=True`) e dos usuários de plataforma (`admin`, `suporte`, `ai-bot`).
- **Verificado em**: `docs/manuals/PERSONAS.md:1-53`, `docs/manuals/02-engineering/01_modelo_de_dados_rbac.md:31-42`, `docs/manuals/03-history/postmortems/pm_001_falha_django_groups.md`, `pm_002_vector_tenant_bleed.md` e verificação no banco PostgreSQL em 12-10-2026.
- **Justificativa**: Garante que todos os laboratórios executáveis (`labs/lab_01` a `lab_04`) rodem sem quebras e que a interface web apresente dados reais para validação de perfis docentes, discentes, corporativos e de atendimento.
- **Alternativas**:
  - *Dados demo fictícios aleatórios*: Rejeitado porque quebraria os testes automatizados da base de conhecimento que buscam slugs canônicos (`dcomp`, `ia-triagem`, `prof.ana`).
