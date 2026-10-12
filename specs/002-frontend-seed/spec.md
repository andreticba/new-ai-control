<!-- spec.md | Vitalia SDD v0.6.0 | 11-10-2026 20:50(GMT-04:00) -->
**spec.md | AI-Control v0.0.1 | 11-10-2026 20:50(GMT-04:00)**

# Especificação de Funcionalidade: Frontend v1 & Adequação do Seed Demo

**Data:** 11-10-2026
**Autor/Agente:** Nexus Architect (via vitalia-spec-specify)

## 1. Contexto e Objetivo (O Quê e Por Quê)
Com a conclusão bem-sucedida da Spec 001 (`001-core-foundations`), a base do `ai-control` consolidou os Bounded Contexts (`core` e `omnichannel`), Soft Foreign Keys (`UUIDField`), RBAC Hierárquico 4-Tier e o Ledger Imutável com Triggers PostgreSQL. 
O objetivo deste marco (P0) é criar a ponte de consumo entre o backend e a interface de usuário:
1. Adequar o comando `seed_demo.py` para semear exclusivamente dados de demonstração (Acadêmico e Corporativo) sem tocar na infraestrutura da plataforma, preenchendo PIIs com Blind Indexing automático e dados mockados de omnichannel.
2. Expor a Frente Síncrona do API Gateway no Django (JWT com `rest_framework_simplejwt`, endpoints agregados `/api/v1/users/me/` e `/api/v1/workspaces/`, e CORS configurado).
3. Disponibilizar o contrato OpenAPI 3.0 dinâmico via `drf-spectacular` com segurança condicional por ambiente.
4. Construir a primeira versão funcional do Frontend em `frontend/` utilizando a stack homologada de `vitalia-01/frontend` (Next.js 16, React 19, Tailwind CSS v4, shadcn/ui, TanStack Query v5 e Redux Toolkit), entregando a tela de login reativa e o shell do dashboard contextualizado com os dados do usuário.

## 2. Requisitos Funcionais
O que o software deve fazer de forma observável?

- **FR-001: Segregação Absoluta de Plataforma:** O comando `seed_demo.py` MUST NOT criar, alterar, duplicar ou excluir os usuários de plataforma (`admin`, `suporte`, `ai-bot`) nem a Organização Interna (`slug='ai-control'`, `is_internal=True`, `name='AI Control (Plataforma)'`), mantendo estrita fidelidade aos dados fundacionais provisionados na migração `core/migrations/0001_initial.py`.
- **FR-002: Carga de Demonstração Canônica e Blind Indexing:** O comando `seed_demo.py` MUST semear as organizações demo e personas rigorosamente definidas em `docs/manuals/PERSONAS.md` e nos laboratórios (`docs/manuals/02-engineering/labs/`):
  - **Perfil Acadêmico (`ufdemo` - ACADEMIC):** 6 Departamentos (`PROPESQ`, `PROEC`, `DCOMP`, `DENF`, `FIN`, `SGP`), 2 Projetos (`saude-digital` com squads `app-movel` e `campo-coleta`; e `ia-triagem` com squads `modelagem` e `dados-clinicos`) e 7 Personas (`prof.ana`, `prof.carlos`, `prof.lucia`, `aluno.joao`, `aluna.maria`, `pesq.externo`, `tae.paulo`), respeitando a *Containment Rule* (obrigatoriedade de `ProjectMembership` antes de `SquadMembership`) e populando `JobTitle` separado de `Role`.
  - **Perfil Corporativo (`empresa-demo` - COMPANY):** 5 Departamentos (`FIN`, `RH`, `COM`, `ATD`, `TI`), 1 Projeto (`implantacao-crm` com squads `integracao` e `conteudo-bot`) e 6 Personas (`gerente.ti`, `dev.rafa`, `supervisor.bia`, `atendente.leo`, `analista.rh`, `diretora.fin`).
  - Todo membro demo MUST ser criado com `full_name` preenchido em texto claro para que o método `UserProfile.save()` gere automaticamente os hashes de busca segura no campo `search_tokens` (Blind Indexing at-rest com `django-crypto-fields`).
- **FR-003: Semeamento Omnichannel via Soft FKs e Instâncias Reais:** O comando `seed_demo.py` MUST gerar contatos (`Contact`) com os JIDs canônicos de `PERSONAS.md` (`5511000000001@example.org`, `5511000000002@example.org`, `5511000000003@example.org`), conversas (`Conversation` com status `ACTIVE_AI` e flags lógicas de IA) e mensagens (`Message`) mockadas associadas via Soft FK `organization_id` (`UUIDField`), simulando instâncias padrão `ai_control_ufdemo` e `ai_control_empresa_demo` sem violação de fronteira relacional entre bounded contexts.
- **FR-004: Tabela de Credenciais para o Desenvolvedor:** O comando `seed_demo.py` MUST imprimir no terminal uma tabela formatada contendo Username, Senha padrão (`demo1234`), Organização, Papéis 4-Tier, JobTitle e Vínculos de Projetos/Squads de todos os usuários criados, além de suportar a flag `--flush` que deleta estritamente os registros demo.
- **FR-005: Autenticação JWT Stateless:** O backend Django MUST implementar autenticação JWT através de `rest_framework_simplejwt`, expondo as rotas `POST /api/v1/auth/token/` (emissão do par `access` e `refresh`) e `POST /api/v1/auth/token/refresh/` (renovação do `access` token).
- **FR-006: Endpoints Agregados (/users/me/ e /workspaces/):** O backend MUST expor endpoints REST agregados para suprir o estado inicial do frontend sem requisições em cascata:
  - `GET /api/v1/users/me/`: Retorna dados do usuário autenticado, `full_name` descriptografado, organização primária, papel de plataforma e lista detalhada de memberships organizacionais e de projeto.
  - `GET /api/v1/workspaces/`: Retorna a árvore hierárquica acessível ao usuário (Organizações às quais pertence, seus Departamentos, Projetos e Squads) em formato agregado de 4 níveis com os respectivos `job_title` e permissões para consumo da UI sem requisições em cascata.
- **FR-007: Suporte a CORS Restrito:** O frontend Next.js 16 requer políticas de CORS restritas para requisições controladas oriundas do frontend (operando por padrão em `http://localhost:3000`). O backend MUST integrar o pacote `django-cors-headers~=4.3` e implementar as seguintes modificações obrigatórias no arquivo `settings.py` (`config/settings/base.py`):
  1. Adicionar `'corsheaders'` em `INSTALLED_APPS`.
  2. Incluir `'corsheaders.middleware.CorsMiddleware'` na lista `MIDDLEWARE`, antes de `django.middleware.common.CommonMiddleware`.
  3. Configurar políticas de CORS restritas com as seguintes configurações no arquivo `settings.py`:
     ```python
     CORS_ORIGIN_ALLOW_ALL = False
     CORS_ALLOW_CREDENTIALS = True
     CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
     ```
  4. Garantir que requisições cross-origin não autorizadas sejam rejeitadas com status HTTP 403 / CORS preflight block, e requisições de `http://localhost:3000` recebam cabeçalhos `Access-Control-Allow-Origin: http://localhost:3000` e `Access-Control-Allow-Credentials: true`.
- **FR-008: Contrato Dinâmico OpenAPI 3.0:** O backend MUST expor `GET /api/schema/` gerado dinamicamente via `drf-spectacular` com anotações `@extend_schema` em todos os ViewSets e endpoints da API, servindo de base formal para contratos tipados.
- **FR-009: Frontend v1 com Two-Step Login e Shell:** O sistema MUST disponibilizar o frontend na pasta `frontend/`, derivando a estrutura de arquivos e dependências de `vitalia-01/frontend`, contendo:
  - Rota `/login`: Formulário reativo com validação Zod, Sonner para feedback, limpeza preventiva de sessões anteriores e Two-Step Login (`/auth/token/` seguido de `/users/me/`).
  - Rota `/`: Shell do Dashboard com barra de navegação exibindo o nome do usuário, tenant ativo, papéis 4-Tier e botão de logout funcional.
- **FR-010: Cliente Axios Resiliente:** O frontend MUST encapsular o Axios em `src/lib/api.ts` com request interceptor injetando `Authorization: Bearer <token>` e response interceptor gerenciando fila assíncrona `isRefreshing` para renovação transparente de tokens em erros 401.
- **FR-011: Tipagem Dinâmica no Frontend:** O frontend MUST conter o script `npm run api:generate` configurado para consumir o schema OpenAPI do backend e gerar o arquivo de tipos estritos `src/lib/api-schema.d.ts`.
- **FR-012: Segurança Condicional do Contrato OpenAPI por Ambiente:** O contrato OpenAPI 3.0 MUST ser dinâmico e possuir segurança condicional configurada de acordo com o ambiente ativo via `drf-spectacular`. Em ambiente de desenvolvimento (`DEBUG=True`), a rota `/api/schema/` MUST operar aberta (`AllowAny`) para viabilizar a execução de `npm run api:generate` pelo frontend local. Em ambiente de produção (`DEBUG=False`), o sistema MUST aplicar classe de permissão restritiva (`permission_classes=[IsAdminUser]`) e configurar esquema de segurança Bearer JWT em `SPECTACULAR_SETTINGS` para evitar Information Disclosure (OWASP API9:2023) sobre a estrutura interna do PaaS Data Vault.

## 3. Requisitos Não-Funcionais (Restrições)
Quais as regras de performance, segurança, ou aderência à Constituição do Arquiteto?

- **[NFR-001] Stack Fixada do Frontend (Constituição React-Vinci):** O frontend MUST utilizar estritamente Next.js 16+ (App Router), React 19, Tailwind CSS v4, shadcn/ui, TanStack Query v5 e Redux Toolkit. Geradores genéricos que alterem essas dependências estão proibidos.
- **[NFR-002] TDD Mandatório (P05):** A implementação dos novos endpoints de autenticação, perfil e workspaces no Django MUST ser acompanhada de testes unitários automatizados em `pytest`, cobrindo casos de sucesso e credenciais inválidas.
- **[NFR-003] Proteção de Dados e Data Vault (P07):** Dados pessoais sensíveis (PII) armazenados no banco com `django-crypto-fields` NUNCA devem vazar em texto puro para logs nem expor ciphertexts brutos para o frontend. A decodificação ocorre exclusivamente na camada de serialização segura para usuários autenticados.
- **[NFR-004] Blindagem contra Information Disclosure:** A especificação da API em produção MUST mitigar riscos de OWASP API9:2023, restringindo Swagger e OpenAPI a operadores autenticados.
- **[NFR-005] Imutabilidade da Spec 001:** O diretório `specs/001-core-foundations/` MUST permanecer intocado; todo o trabalho novo vive no escopo da feature `002-frontend-seed`.

## 4. Histórias de Usuário (User Stories)
- **Como um** desenvolvedor ou testador da plataforma, **eu quero** rodar `python manage.py seed_demo` e obter uma tabela clara de credenciais sem corromper o usuário admin de plataforma, **para que** eu possa testar imediatamente os diferentes níveis de acesso na interface web.
- **Como um** membro de organização (ex: professor ou gerente), **eu quero** realizar login na tela `/login` do Next.js e ser redirecionado para um Dashboard com meu nome e minha organização, **para que** eu visualize os projetos e squads sob meu escopo de permissão.
- **Como um** engenheiro de segurança, **eu quero** que a rota de schema OpenAPI não fique exposta abertamente na internet em produção, **para que** agentes maliciosos não descubram a estrutura de dados interna do PaaS Data Vault.

## 5. Critérios de Aceite (Acceptance Criteria)
Condições estritas para considerar a funcionalidade concluída:

- **[AC-01]** Dado o banco resetado ou com migrações iniciais, quando o comando `python manage.py seed_demo` for executado, então os operadores de plataforma (`admin`, `suporte`, `ai-bot`) devem permanecer inalterados, as 13 personas canônicas de `docs/manuals/PERSONAS.md` devem ser criadas com seus `search_tokens` preenchidos via Blind Indexing, os contatos e conversas omnichannel devem ser criados sob as instâncias `ai_control_ufdemo` e `ai_control_empresa_demo`, e uma tabela formatada com credenciais e vínculos de projeto/squad deve ser exibida no terminal.
- **[AC-02]** Dado o frontend rodando na porta 3000 e o backend na porta 8000 com `django-cors-headers` configurado (`CORS_ALLOWED_ORIGINS = ['http://localhost:3000']`, `CORS_ORIGIN_ALLOW_ALL = False`), quando um usuário submeter credenciais demo válidas na tela `/login`, então a requisição deve responder com cabeçalhos CORS válidos sem bloqueios de Cross-Origin, os tokens JWT devem ser armazenados e o Dashboard (`/`) deve carregar os dados vindos de `/api/v1/users/me/`.
- **[AC-03]** Dado um access token expirado no frontend, quando uma requisição for disparada, então o interceptor do Axios deve renovar o token silenciosamente via `POST /api/v1/auth/token/refresh/` sem desconectar o usuário da tela.
- **[AC-04]** Dado o backend rodando com `DEBUG=True`, quando o comando `npm run api:generate` for executado na pasta `frontend/`, então o arquivo `src/lib/api-schema.d.ts` deve ser gerado sem erros de compilação TypeScript.
- **[AC-05]** Dado o backend rodando com `DEBUG=False` (produção), quando uma requisição anônima ou não-administrativa for enviada para `GET /api/schema/`, então a resposta deve retornar HTTP 401 ou 403, mantendo a estrutura interna do PaaS Data Vault protegida.

## 6. Fora do Escopo (Out of Scope)
- Não inclui a implementação completa de salas de chat interativas em tempo real via WebSockets (Django Channels).
- Não inclui a esteira de execução de inferência de LLM ou RAG síncrono no frontend (mantém-se isolado na esteira assíncrona do Celery).
- Não inclui telas complexas de edição administrativa de departamentos e projetos (apenas leitura agregada via `/workspaces/`).

## 7. Suposições Verificadas (Grounding)
- **"Next.js 16.1.7, React 19.2.0, Tailwind v4, TanStack Query v5"**: Verificado em `/home/andre/projetos/assistidos/ai-base/vitalia-01/frontend/package.json` em 11-10-2026.
- **"django-crypto-fields==1.0.1 e Blind Indexing"**: Verificado em `ai-control/core/models.py:465-470` e `504-520` em 11-10-2026.
- **"Criação de usuários de plataforma em 0001_initial.py"**: Verificado em `ai-control/core/migrations/0001_initial.py:401-490` em 11-10-2026.
- **"Necessidade de djangorestframework-simplejwt e django-cors-headers"**: Verificado localmente no ambiente venv e em `vitalia-01/backend/requirements.txt:6` em 11-10-2026.
- **"drf-spectacular==0.30.0 já homologado"**: Verificado em `ai-control/requirements.txt:21` em 11-10-2026.
- **"Catálogo Canônico de Personas e Organizações Demo"**: Verificado em `ai-control/docs/manuals/PERSONAS.md` (13 personas, 2 tenants demo) em 12-10-2026.
- **"Hierarquia 4-Tier e Containment Rule (Squad -> Projeto)"**: Verificado em `ai-control/docs/manuals/01-product/01_hierarquia_organizacional.md:10` em 12-10-2026.
- **"Separação Estrita de Role (Máquina) vs JobTitle (Rótulo/LLM)"**: Verificado em `ai-control/docs/manuals/01-product/02_papeis_e_permissoes.md:15-16` em 12-10-2026.
- **"Modelo RBAC Matricial (BaseMembership) e Desacoplamento Soft FK"**: Verificado em `ai-control/docs/manuals/02-engineering/01_modelo_de_dados_rbac.md:35-37` em 12-10-2026.
- **"Prevenção de Vazamento Multi-Tenant e Banimento de auth.Group"**: Verificado em `ai-control/docs/manuals/03-history/postmortems/pm_001_falha_django_groups.md` e `pm_002_vector_tenant_bleed.md` em 12-10-2026.
