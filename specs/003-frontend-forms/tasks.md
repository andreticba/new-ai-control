<!-- tasks.md | AI-Control v0.0.1 | 13-10-2026 23:15(GMT-04:00) -->
# Tasks: Formulários de Governança 4-Tier e Gestão de Membros no Frontend

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Data Model**: [data-model.md](./data-model.md) | **Contracts**: [contracts/api-mutations.yaml](./contracts/api-mutations.yaml)  
**Gerado em**: 13-10-2026 23:15 (GMT-04:00) | **Fuso**: America/Cuiaba  

---

## MVP Scope

> **MVP Scope Definido**: Implementar **Phase 0 + Phase 1 + Phase 2 + Phase 3 (US1)** entrega a governança visual completa das entidades organizacionais 4-Tier (`Organization`, `Department`, `Project`, `Squad`) no Dashboard HUD com feedback reativo via Sonner e garantia de integridade P3.
> As Fases subsequentes (Phase 4: US2 Gestão de Membros, Phase 5: US3 Onboarding LGPD, Phase 6: US4 RBAC Guard) expandem as capacidades operacionais e de segurança.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente, infraestrutura local e grounding documental ANTES de qualquer implementação de código (Princípios P01 e P03). Sem label de US.*

- [X] T000-A Ativar ambiente virtual Python local em .venv/bin/activate
- [X] T000-B Verificar versão do runtime Python do venv com python --version
- [X] T000-C [P] Verificar dependências instaladas do backend vs requirements com pip check
- [X] T000-D [P] Verificar dependências do frontend Node com npm list em frontend/
- [X] T000-E Verificar integridade dos serviços dockerizados locais com docker compose ps

---

## Phase 1: Setup

*Preparação de tipagem, schemas de validação e infraestrutura de contratos. Sem label de US.*

- [X] T001 [P] Criar schemas de validação Zod de workspaces em frontend/src/lib/validations/workspace-schemas.ts
- [X] T002 [P] Criar schemas de validação Zod de membros em frontend/src/lib/validations/membership-schemas.ts
- [X] T003 Validar contrato OpenAPI 3.0 de endpoints contratuais em specs/003-frontend-forms/contracts/api-mutations.yaml
- [X] T004 [P] Construir componente reutilizável Modal em frontend/src/components/ui/Modal.tsx

---

## Phase 2: Foundational

*Camada base de mutações, infraestrutura de serialização e proteção de integridade P3 no backend. Sem label de US.*

- [X] T005 [P] Implementar classes OrganizationCreateSerializer e DepartmentCreateSerializer em core/api/v1/serializers.py
- [X] T006 [P] Implementar classes ProjectCreateSerializer e SquadCreateSerializer com validação P3 em core/api/v1/serializers.py
- [X] T007 Implementar classe WorkspaceMutationViewSet para mutações CRUD em core/api/v1/views/workspace_mutation_views.py
- [X] T008 Registrar rotas de mutação de workspaces em core/api/v1/urls.py
- [X] T009 Criar testes unitários de workspaces garantindo isolamento em core/tests/test_workspace_mutations.py

---

## Phase 3: User Story 1 — Gestão da Estrutura Organizacional 4-Tier (US1)

**Story Goal**: Permitir a administradores e gestores criar e editar Organizações, Departamentos, Projetos e Squads diretamente no painel HUD visual sem redirecionamentos, mantendo integridade P3 e feedback imediato por Sonner.  
**Independent Test**: Executar criação de cada entidade via curl e formulário visual, validando reflexo imediato no dashboard e bloqueio de criação de squad sem projeto pai.  
**Referência**: FR-001, FR-002, FR-003, FR-004 | SC-001, SC-002, SC-003, SC-004  

- [X] T010 [P] [US1] Escrever testes unitários TDD Red Phase de Organization e Department em core/tests/test_workspace_mutations.py
- [X] T011 [P] [US1] Criar testes unitários de validação de Squad com projeto pai obrigatório P3 em core/tests/test_workspace_mutations.py
- [X] T012 [US1] Implementar classes de rotas e visualizações de workspaces em core/api/v1/views/workspace_mutation_views.py
- [X] T013 [P] [US1] Criar hook useWorkspaceMutations no arquivo frontend/src/hooks/useWorkspaceMutations.ts
- [X] T014 [P] [US1] Construir componente visual OrganizationModal no arquivo frontend/src/components/forms/OrganizationModal.tsx
- [X] T015 [P] [US1] Construir componente visual DepartmentModal no arquivo frontend/src/components/forms/DepartmentModal.tsx
- [X] T016 [P] [US1] Construir componente visual ProjectModal no arquivo frontend/src/components/forms/ProjectModal.tsx
- [X] T017 [US1] Construir componente visual SquadModal no arquivo frontend/src/components/forms/SquadModal.tsx
- [X] T018 [US1] Conectar acionadores de abertura dos modais de entidade aos cartões do HUD em frontend/src/app/page.tsx

---

## Phase 4: User Story 2 — Alocação de Membros e Cargos Matriciais com Validação P3 Contínua (US2)

**Story Goal**: Permitir a líderes alocar pessoas em Organizações, Projetos e Squads com papéis e cargos específicos, assegurando que membros de squad possuam vínculo ativo obrigatório no projeto pai da squad em tempo real e de forma contínua.  
**Independent Test**: Tentar alocar um usuário em uma squad cujo vínculo no projeto pai está inativo, verificando a rejeição imediata com erro descritivo tanto na UI quanto no backend (HTTP 400).  
**Referência**: FR-005, FR-006, FR-007 | SC-005, SC-007  

- [X] T019 [P] [US2] Criar suíte de testes unitários de validação contínua P3 em core/tests/test_membership_mutations.py
- [X] T020 [P] [US2] Implementar classes OrganizationMembershipSerializer, ProjectMembershipSerializer e SquadMembershipSerializer em core/api/v1/serializers.py
- [X] T021 [US2] Implementar classes de visualização de membros em core/api/v1/views/membership_views.py
- [X] T022 [US2] Registrar rotas de membership no arquivo core/api/v1/urls.py
- [X] T023 [P] [US2] Criar hook useMembershipMutations com TanStack Query em frontend/src/hooks/useMembershipMutations.ts
- [X] T024 [P] [US2] Construir componente visual MemberAllocationModal no arquivo frontend/src/components/members/MemberAllocationModal.tsx
- [X] T025 [US2] Construir painel retrátil TeamDrawer em frontend/src/components/members/TeamDrawer.tsx
- [X] T026 [US2] Conectar TeamDrawer aos cartões organizacionais em frontend/src/app/page.tsx

---

## Phase 5: User Story 3 — Admissão Imediata de Novo Colaborador (Onboarding com Blind Indexing LGPD / P07) (US3)

**Story Goal**: Permitir a administradores cadastrar um novo colaborador instantaneamente durante a alocação de membros, gerando tokens determinísticos de busca segura (Blind Indexing) e protegendo dados pessoais sensíveis conforme a LGPD.  
**Independent Test**: Submeter cadastro rápido com e-mail duplicado e verificar erro inline no modal; submeter cadastro válido e confirmar seleção automática do novo usuário no combobox de alocação.  
**Referência**: FR-008 | SC-006  

- [X] T027 [P] [US3] Criar testes unitários de cadastro rápido em core/tests/test_user_onboard.py
- [X] T028 [US3] Implementar action quick_onboard no ViewSet em core/api/v1/views/user_views.py
- [X] T029 [P] [US3] Construir componente visual QuickUserModal no arquivo frontend/src/components/members/QuickUserModal.tsx
- [X] T030 [US3] Conectar modal ao combobox de seleção em frontend/src/components/members/MemberAllocationModal.tsx

---

## Phase 6: User Story 4 — Segurança, Ergonomia e Controle RBAC (US4)

**Story Goal**: Exibir ou desabilitar de forma proativa os controles de mutação na UI de acordo com as permissões do usuário logado (`org.manage`, `project.manage`, `squad.manage`), com imposição definitiva no backend via DRF permissions retornando HTTP 403 Forbidden.  
**Independent Test**: Autenticar usuário sem privilégios de gestão e verificar botões de mutação desabilitados/ocultos na UI e bloqueio estrito com HTTP 403 ao tentar forçar requisições diretas de mutação.  
**Referência**: FR-009, FR-010 | SC-008  

- [X] T031 [P] [US4] Criar testes unitários de controle RBAC em core/tests/test_workspace_permissions.py
- [X] T032 [P] [US4] Implementar hook usePermission em frontend/src/hooks/usePermission.ts
- [X] T033 [US4] Conectar guards de permissão aos botões em frontend/src/app/page.tsx
- [X] T034 [US4] Implementar tratamento de erro HTTP 403 no cliente API em frontend/src/lib/api-client.ts

---

## Phase 7: Polish & Cross-Cutting

*Garantia de qualidade, validação de contratos, testes de ponta a ponta e auditoria constitucional final. Sem label de US.*

- [X] T035 [P] Executar testes unitários do backend com pytest em core/tests/test_workspace_mutations.py
- [X] T036 [P] Executar verificação de tipos TypeScript com tsc em frontend/src/app/page.tsx
- [X] T037 Validar cenários de aceitação BDD em specs/003-frontend-forms/spec.md
- [X] T038 Executar auditoria de tarefas no SDDJudge em specs/003-frontend-forms/tasks.md

---

## Dependency Graph

```text
Phase 0: Grounding & Environment (T000-A a T000-E)
  ↓
Phase 1: Setup & Schemas (T001 a T004)
  ↓
Phase 2: Foundational Mutations (T005 a T009)
  ↓
Phase 3: US1 — Estrutura Organizacional 4-Tier (T010 a T018) [MVP Scope Concluído]
  ↓
Phase 4: US2 — Gestão de Membros & P3 Contínuo (T019 a T026)
  ↓
Phase 5: US3 — Onboarding Rápido LGPD (T027 a T030)
  ↓
Phase 6: US4 — RBAC Guard Proativo (T031 a T034)
  ↓
Phase 7: Polish & Testes E2E (T035 a T038)
```

---

## Parallel Execution

Tarefas marcadas com **`[P]`** dentro de cada fase não possuem dependências mútuas e podem ser implementadas simultaneamente:
- **Phase 0**: T000-C e T000-D podem rodar em paralelo.
- **Phase 1**: T001, T002 e T004 operam em arquivos isolados e podem ser construídos simultaneamente.
- **Phase 2**: T005 e T006 tratam de serializers distintos e podem ser implementados em paralelo.
- **Phase 3 (US1)**: Testes unitários T010/T011 e formulários visuais T014/T015/T016 operam independentemente antes da integração em T018.
- **Phase 4 (US2)**: Testes T019, serializers T020 e modal T024 podem ser desenvolvidos em paralelo.
- **Phase 5 (US3)**: Testes T027 e modal visual T029 operam em paralelo.
- **Phase 6 (US4)**: Testes DRF T031 e hook de frontend T032 operam em stacks isoladas.
- **Phase 7**: Testes backend T035 e type-check frontend T036 operam em paralelo.
