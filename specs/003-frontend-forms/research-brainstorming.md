<!-- research-brainstorming.md | AI-Control v0.0.1 | 13-10-2026 17:25(GMT-04:00) -->
**research-brainstorming.md | AI-Control v0.0.1 | 13-10-2026 17:25(GMT-04:00)**

# Research & Socratic Brainstorming: Formulários de Governança 4-Tier & Gestão de Membros no Frontend

Este documento consolida as pesquisas, decisões arquiteturais e o grounding no código legado para a construção dos **Formulários no Frontend (Next.js 16)** destinados à adição e edição de Organizações, Departamentos, Projetos e Squads, bem como a **Gestão e Alocação de Membros e Cargos** nos 3 níveis hierárquicos, preservando a identidade visual com **glassmorphism**, a inteligência de negócio original e as garantias de conformidade do AI-Control.

---

## 1. Contexto e Motivação (Por que este documento existe)

Com a estabilização do backend em Django 6.1 e a entrega da primeira versão do HUD analítico no Next.js 16 (`specs/002-frontend-seed`), o sistema alcançou a capacidade de autenticar via JWT e renderizar a topologia de governança em modo leitura (`GET /api/v1/workspaces/`).

O próximo marco prioritário (**P0**) é permitir que operadores e gestores realizem mutações estruturais completas diretamente pela interface web:
1. Criar e editar Organizações, Departamentos, Projetos e Squads.
2. Alocar e editar os membros (pessoas), associando seus respectivos papéis de sistema (`Role`) e cargos/funções exibidos na interface (`JobTitle`).
3. Cadastrar novos usuários de forma rápida durante a própria alocação (onboarding instantâneo com geração de Blind Indexing criptográfico).
4. Assegurar a obediência irrestrita à **Regra de Contenção (P3)** através de uma interface guiada e reativa.

---

## 2. Decisões Arquiteturais Consolidadas no Brainstorming

| # | Decisão | Racional Técnico | Impacto na Implementação |
|---|---|---|---|
| **D01** | **Preservação da Estética Glassmorphism** | Manter a identidade visual premium já entregue no HUD (`frontend/src/app/page.tsx`), utilizando painéis escuros (`#090d16`), bordas translúcidas (`border-slate-800`), efeitos de desfoque (`backdrop-blur-md`), gradientes ciano/índigo e feedback reativo com `Sonner`. | Os novos modais e drawers herdarão estritamente a paleta de cores e componentes do design system ativo. |
| **D02** | **Nomenclatura Core Estrita (Anti-Alucinação)** | A verdade do sistema são os modelos reais do código: `Organization` (com `is_internal`), `Department`, `Project`, `Squad`, `BaseMembership`, `UserProfile`, `ParticipantProfile`, `ProfessionalProfile`, `Contact`, `Conversation`, `Message`. Termos conceituais legados (ex.: `Tenant`, `Team`) estão banidos da camada de mutação. | Serializers e contratos do frontend espelharão os nomes exatos das tabelas do Postgres. |
| **D03** | **Manutenção das Verticais de Negócio (Saúde e Academia)** | Saúde (`OrgType.HEALTHCARE`) e Academia (`OrgType.UNIVERSITY`) são clientes prioritários do produto. O motor clínico (`core/orchestrator/agent.py`) e os 40 cargos (médicos, enfermeiros, professores) permanecem ativos, com foco expandido na proteção de PII e sigilo de dados. | Formulários de Organização e Cargos oferecerão suporte nativo a esses tipos de organização e categorias de cargo. |
| **D04** | **Endpoints de Mutação RESTful Modulares** | Criação de ViewSets dedicados no Django (`core/api/v1/views/workspace_mutation_views.py`) com serializers granulares em vez de rotas genéricas. Cada entidade terá validação de entrada, `@extend_schema` e permissões RBAC estritas. | O OpenAPI Schema (`/api/schema/`) expõe contratos previsíveis para tipagem automática via `openapi-typescript`. |
| **D05** | **Modais Contextuais Integrados ao HUD** | Padrão de UX baseado em Modais/Drawers acionados diretamente nos cards da hierarquia 4-Tier, preservando o contexto espacial do operador sem navegação disruptiva de telas. | Gerenciamento de estado local no cliente (`useState`/`useCallback`), espelhando e expandindo o padrão legado de `upload-document-modal.tsx`. |
| **D06** | **Controle de Acesso Proativo na UI (RBAC Frontend)** | Ocultação ou desativação condicional dos botões de ação ("+ Adicionar", "Editar", "Gerenciar Equipe") caso o usuário logado não possua a permissão necessária (`org.manage`, `project.manage`, `squad.manage`) vinda de `/users/me/`. | Previne erros 403 desnecessários e melhora a ergonomia de uso. Validação definitiva continua mandatória no backend. |
| **D07** | **Inviolabilidade da Regra de Contenção (P3)** | Squads pertencem rigidamente a Projetos; Projetos pertencem a Organizações; Departamentos pertencem a Organizações. Criações e edições validam slugs únicos por escopo pai. | Serializers do Django rejeitam qualquer vínculo órfão ou fora da árvore hierárquica. |
| **D08** | **Gestão e Alocação de Membros/Cargos Integrada (Full-Stack)** | Atribuir e alterar papéis (`Role`) e cargos (`JobTitle`) de pessoas nos 3 níveis hierárquicos (`OrganizationMembership`, `ProjectMembership`, `SquadMembership`) de forma totalmente funcional. | Criação de endpoints de membership com validação de escopo estrito (`role.scope == SCOPE` e `job_title.level == SCOPE`). |
| **D09** | **Seleção de Pessoas com Cadastro Rápido Modal** | Autocomplete/Combobox para selecionar usuários já cadastrados no sistema, com botão/modal de "Cadastrar Novo Usuário" (`username`, `email`, `full_name`) para suprir admissões imediatas sem sair da tela. | Criação do endpoint `POST /api/v1/users/` com preenchimento de `full_name` e disparo de Blind Indexing (`UserProfile.save()`). |
| **D10** | **Prevenção Ativa da Regra P3 via Filtragem Guiada na UI** | Ao alocar em um Projeto, o select de pessoas lista apenas membros ativos da Organização. Ao alocar em uma Squad, lista apenas membros ativos do Projeto pai. Evita erros 400/ValidationError do backend por meio de uma UX guiada e blindada. | O frontend consulta a árvore de membros antes de renderizar as opções de alocação, impedindo violações de parentesco. |

---

## 3. Grounding Detalhado no Código Legado (`AI-Control completo.md`)

A concepção dos formulários e das rotas de mutação ancora-se diretamente nos padrões comprovados no código legado:

### 3.1. Padrão de Modais e Controle de Estado no Cliente
* **Referência Legada**: `AI-Control completo.md:6339-6630` (`ai-control/ai-frontend/src/app/(dashboard)/knowledge-base/_components/upload-document-modal.tsx`)
* **Estrutura Resgatada**:
  - Interface de controle de abertura: `isOpen: boolean`, `onOpenChange: (isOpen: boolean) => void`, `onSuccess: () => void`.
  - Integração de formulários reativos: `react-hook-form` com `zodResolver(schema)`.
  - Mutação e Cache: `useMutation` do `@tanstack/react-query` disparando `queryClient.invalidateQueries({ queryKey: ['workspaces'] })` após mutação bem-sucedida.
  - Notificações de Sucesso/Erro: `toast.success("Operação realizada com sucesso!")` via `sonner`.
  - Diálogos estilizados com classes Tailwind e transições suaves de glassmorphism.
* **Expansão para a Arquitetura 4-Tier**:
  - Modais contextuais de criação/edição de entidades estruturais (`OrganizationModal`, `DepartmentModal`, `ProjectModal`, `SquadModal`).
  - Drawer lateral contextual de **Gerenciamento de Equipe** (`TeamManagementDrawer.tsx`) disparado pelo botão de equipe de cada card (Org, Projeto, Squad), contendo a listagem de membros ativos, alteração de cargos/papéis e acionador de novo vínculo.
  - Mini-modal de **Cadastro Rápido de Usuário** (`QuickUserModal.tsx`) acessível dentro do autocomplete de membros.

### 3.2. Padrão de Serializers e Regras de Negócio no Backend
* **Referência Legada**: `AI-Control completo.md:3092-3219` (`ai-control/core/serializers.py`) e `AI-Control completo.md:4100-4500` (`ai-control/core/views.py`)
* **Estrutura Resgatada**:
  - Validação explícita de campos obrigatórios e sanitização de strings (`slugify` automático se não fornecido).
  - Verificação de duplicidade de slugs no escopo do tenant.
  - Separação entre serializers de leitura agregada e serializers de entrada/mutação (`ModelSerializer` com campos restritos).
* **Adaptação para os Novos Bounded Contexts**:
  - `OrganizationSerializer`, `DepartmentSerializer`, `ProjectSerializer`, `SquadSerializer`.
  - `OrganizationMembershipSerializer`, `ProjectMembershipSerializer`, `SquadMembershipSerializer` com validações mandatórias de `BaseMembership.clean()`:
    1. `role.scope == SCOPE` (rejeita role de projeto em organização).
    2. `job_title.level == SCOPE` (rejeita cargo de squad em projeto).
    3. `validate_parent()` (obrigatoriedade de vínculo ativo no nível superior — Regra P3).
  - `UserCreateSerializer`: criação atômica de `User` e `UserProfile` com cálculo automático de hashes de busca segura (Blind Indexing via `UserProfile.save()`).

### 3.3. Padrão de Autenticação e Interceptação no Frontend
* **Referência Legada**: `AI-Control completo.md:7429-7544` (`ai-control/ai-frontend/src/lib/api.ts`) e `frontend/src/lib/api.ts`
* **Garantia Preservada**:
  - Todas as chamadas de mutação (`POST`, `PUT`, `PATCH`, `DELETE`) trafegam pelo cliente `api` centralizado, garantindo injeção automática de `Bearer <token>` e renovação transparente em caso de token expirado (fila assíncrona `isRefreshing`).

---

## 4. Delineamento de Escopo: Funcionalidade Real vs. Preview/Placeholder

Para assegurar clareza absoluta de entrega e evitar expansões de escopo descontroladas, a tabela abaixo demarca rigorosamente a fronteira desta feature:

### 🟢 Totalmente Funcional de Fato (Full-Stack End-to-End: UI + API + Banco)

| Área / Entidade | Operações Funcionais | Campos Suportados nos Formulários | Validações Mandatórias |
|---|---|---|---|
| **Organização** | **Criar e Editar** (`POST` / `PATCH`) | • Nome (`name`)<br>• Slug (`slug` único)<br>• Tipo (`org_type`: HEALTHCARE, UNIVERSITY, COMPANY, NGO, etc.)<br>• Status Ativo (`is_active`) | • Unicidade do `slug`<br>• Enums válidos de `OrgType`<br>• Permissão `org.manage` no backend/frontend |
| **Departamento** | **Criar e Editar** (`POST` / `PATCH`) | • Nome (`name`)<br>• Código (`code` - ex.: "TI", "DCOMP")<br>• Descrição (`description`)<br>• Organização Pai (`organization_id` contextual) | • Unicidade de `(organization, code)`<br>• Vínculo obrigatório com a Org ativa<br>• Permissão `org.manage` |
| **Projeto** | **Criar e Editar** (`POST` / `PATCH`) | • Nome (`name`)<br>• Slug (`slug`)<br>• Tipo (`project_type`: RESEARCH, DEVELOPMENT, etc.)<br>• Status (`status`: PLANNING, ACTIVE, PAUSED, etc.)<br>• Descrição (`description`) | • Subordinação à Org ativa<br>• Unicidade de `slug` por organização<br>• Permissão `project.manage` |
| **Squad** | **Criar e Editar** (`POST` / `PATCH`) | • Nome (`name`)<br>• Slug (`slug`)<br>• Missão (`mission`)<br>• Status Ativo (`is_active`)<br>• Projeto Pai (`project_id` contextual) | • Regra de Contenção (P3): Projeto obrigatório<br>• Unicidade de `slug` por projeto<br>• Permissão `squad.manage` |
| **Alocação de Membros (Organização)** | **Vincular, Editar e Desativar** (`POST` / `PATCH` / `DELETE`) | • Usuário (`user_id`)<br>• Papel (`role_id` - escopo ORG)<br>• Cargo (`job_title_id` - nível ORG)<br>• Departamento (`department_id` opcional) | • `role.scope == ORGANIZATION`<br>• `job_title.level == ORGANIZATION`<br>• Unicidade de `(user, organization)` |
| **Alocação de Membros (Projeto)** | **Vincular, Editar e Desativar** (`POST` / `PATCH` / `DELETE`) | • Usuário (`user_id` restrito a membros da Org)<br>• Papel (`role_id` - escopo PROJECT)<br>• Cargo (`job_title_id` - nível PROJECT)<br>• Colaborador Externo (`is_external`) | • **Regra P3**: Usuário DEVE ser membro ativo da Org pai<br>• Se `is_external=True`, exige papel `org_guest` na Org<br>• Unicidade de `(user, project)` |
| **Alocação de Membros (Squad)** | **Vincular, Editar e Desativar** (`POST` / `PATCH` / `DELETE`) | • Usuário (`user_id` restrito a membros do Projeto)<br>• Papel (`role_id` - escopo SQUAD)<br>• Cargo (`job_title_id` - nível SQUAD) | • **Regra P3**: Usuário DEVE ser membro ativo do Projeto pai<br>• `role.scope == SQUAD`<br>• Unicidade de `(user, squad)` |
| **Cadastro Rápido de Usuário** | **Criar Usuário no Onboarding** (`POST /api/v1/users/`) | • Username (`username`)<br>• E-mail (`email`)<br>• Nome Completo (`full_name`) | • Unicidade de username/email<br>• Geração automática de `search_tokens` de Blind Indexing no `UserProfile.save()` |
| **UX & Reatividade** | **Modais, Drawers & Feedbacks** | • Dialogs/Drawers com glassmorphism nos cards<br>• Drawer lateral "Gerenciar Equipe" por entidade<br>• Validação instantânea com Zod no cliente<br>• Toasts Sonner para sucesso e erro<br>• Atualização imediata do HUD sem refresh de página | • Invalidação da query de workspaces e membros após mutações<br>• Feedback visual de carregamento |
| **Controle de Acesso** | **RBAC na Interface** | • Helper `hasPermission(slug)` inspecionando permissões ativas<br>• Ocultação/desativação visual de botões de edição para usuários sem privilégio | • Validação definitiva por classes de permissão do DRF no backend |

---

### 🟡 Modo Preview / Somente Leitura / Placeholder (Preservados sem Mutação nesta Fase)

| Área / Componente | Estado nesta Fase | Racional Arquitetural |
|---|---|---|
| **Exclusão Física (Hard Delete de Entidades Estruturais)** | **Placeholder / Desativado** | Exclusão em cascata de Organizações, Projetos ou Squads destruiria chaves estrangeiras protegidas e histórico de auditoria. O ciclo atual foca em criação, edição e desativação lógica (`is_active=False` ou `status='CANCELLED'`). Expurgo físico será tratado em ADR específico de ciclo de vida. |
| **Card "Omnichannel & Agentes IA"** | **Preview Visual** | Permanece exibindo a telemetria da instância conectada (`ai_control_{org.slug}`, status `ACTIVE_AI` e canal de roteamento), sem interface de chat em tempo real neste momento. |
| **Base de Conhecimento & Ingestão (RAG)** | **Placeholder Visual** | O upload e fragmentação vetorial de documentos permanecem na camada de backend, sem formulário de upload no HUD nesta etapa. |
| **Gamificação, Streaks e Wallets** | **Placeholder** | Exibição de saldos de tokens e streaks de participantes permanecem mantidos no modelo de dados, sem edição direta pelos formulários de governança. |

---

## 5. Rastro de Pesquisa (Grounding Table)

| # | Afirmação / Fato Técnico | Verificado? | Fonte Local / Código | Data |
|---|---|---|---|---|
| **01** | O HUD atual utiliza visual Glassmorphism com paleta `#090d16`, bordas `border-slate-800`, Lucide icons e gradientes ciano/índigo. | ✅ Sim | `frontend/src/app/page.tsx:91-140` | 13-10-2026 |
| **02** | O modelo de dados define `Organization` com `OrgType`, `Department` com `code`, `Project` com `ProjectType`/`Status`, e `Squad` com `mission`. | ✅ Sim | `core/models.py:53-270` | 13-10-2026 |
| **03** | O modelo `BaseMembership` valida estritamente `role.scope == SCOPE`, `job_title.level == SCOPE` e a Regra P3 em `clean()`. | ✅ Sim | `core/models.py:270-420` | 13-10-2026 |
| **04** | O código legado utilizava `upload-document-modal.tsx` com `Dialog`, `react-hook-form`, `zodResolver`, `useMutation` e `sonner`. | ✅ Sim | `AI-Control completo.md:6339-6630` | 13-10-2026 |
| **05** | O pacote `sonner` e `@tanstack/react-query` já estão instalados no `frontend/package.json`. | ✅ Sim | `frontend/package.json:15,23` | 13-10-2026 |
| **06** | A rota `/api/v1/workspaces/` retorna a árvore completa em leitura, mas não existem rotas de mutação REST para adicionar ou editar entidades e memberships. | ✅ Sim | `core/api/v1/urls.py:11-20` | 13-10-2026 |
| **07** | A migração `0008_seed_rbac_catalog.py` já provisiona as permissões `org.manage`, `project.manage`, `squad.manage` para verificação de permissão. | ✅ Sim | `core/migrations/` e catálogo seed | 13-10-2026 |
| **08** | O diretório residual `new-ai-control/` foi removido com sucesso pelo usuário, limpando a descoberta do pytest. | ✅ Sim | Verificação via terminal | 13-10-2026 |

---

## 6. Próximos Passos (Handoff ao Pipeline SDD)

Com a consolidação deste documento de pesquisa, decisões e demarcação estrita de escopo:
1. Este artefato serve de âncora técnica definitiva para a elaboração formal do `spec.md` da feature (`/vitalia-spec-specify`).
2. O ciclo de concepção e brainstorming cumpriu rigorosamente todos os requisitos pactuados com o usuário.
