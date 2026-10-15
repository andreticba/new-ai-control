<!-- specs/004-full-stack-realignment/tasks.md | AI-Control v0.0.1 | 15-10-2026 07:52(GMT-04:00) -->
# tasks.md | AI-Control v0.0.1 | 15-10-2026 07:52(GMT-04:00)

# Tasks: Spec 004 — Full-Stack Realignment
## Frontend TanStack Query, Modularização do Dashboard e Backend Anti-N+1 Multi-Tenant

**Spec**: [spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/spec.md) | **Plan**: [plan.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/plan.md)  
**Grounding**: [grounding.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/grounding.md) | [component-contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/contracts/component-contracts.md) | [AI-Control completo.md](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md)  
**Gerado em**: 14-10-2026 16:20(GMT-04:00)

---

## MVP Scope

> **Definição de MVP**:  
> A execução sequencial das **Phase 0 + Phase 1 (Setup) + Phase 2 (Backend Anti-N+1) + Phase 3 (US1 - Dashboard Modular Reativo)** entrega o produto plenamente operacional, sanando o erro de runtime no navegador, eliminando o gargalo de banco de dados e exibindo os dados de workspaces de forma 100% reativa.  
> As fases seguintes (US2, US3, US4 e Polish) consolidam a reatividade pós-mutação, a higiene de memória dos formulários e os testes de regressão de ponta a ponta.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e integridade de dependências antes de qualquer escrita de código. Sem label de US.*

- [X] T000-A Ativar ambiente virtual: `.venv/bin/activate` em core
- [X] T000-B Verificar versão do interpretador Python: `.venv/bin/python --version` (Python 3.14.4)
- [X] T000-C Verificar saúde dos containers de infraestrutura: `docker compose ps` (PostgreSQL 16 e Redis 7)
- [X] T000-D Verificar dependências do frontend e Next.js 16: `cd frontend && npm list @tanstack/react-query next react`
- [X] T000-E Verificar integridade de dependências Python: `.venv/bin/pip check`

---

## Phase 1: Setup da Camada de Dados e Provedores (Sem US)

*Fundação da infraestrutura do TanStack Query e hooks de consumo de dados. Sem label de US.*

- [X] T001 Implementar helper getQueryClient seguro para SSR em frontend/src/lib/get-query-client.ts
- [X] T002 Injetar QueryClientProvider no encapsulador global em frontend/src/components/Providers.tsx
- [X] T003 Implementar custom hook useWorkspacesQuery em frontend/src/hooks/useWorkspacesQuery.ts
- [X] T004 Implementar custom hook useAuth para desacoplar Redux em frontend/src/hooks/useAuth.ts

---

## Phase 2: Foundational — Backend Anti-N+1 & Blindagem Multi-Tenant (TDD) (Sem US)

*Otimização relacional no banco de dados e isolamento rigoroso por organização (P07/P15). Sem label de US.*

- [X] T005 [P] Criar testes unitários de contagem de queries SQL Anti-N+1 em core/tests/test_workspace_performance.py
- [X] T006 [P] Criar testes unitários de isolamento multi-tenant de listagem em core/tests/test_workspace_isolation.py
- [X] T007 Refatorar ActiveWorkspacesView com carregamento em lote (prefetch) em core/api/v1/views/user_views.py
- [X] T008 Implementar get_queryset com filtro de tenant do usuário logado em core/api/v1/views/workspace_mutation_views.py

---

## Phase 3: User Story 1 — Componentização Atômica e Reativa do Dashboard (US1)

**Story Goal**: Carregar o Dashboard HUD sem erros de runtime, consumindo dados reativos do TanStack Query e dividindo o monólito de 730 linhas em componentes modulares especializados.  
**Independent Test**: Acessar `http://localhost:3000/`, verificar ausência de tela vermelha e confirmar renderização correta de Hero, Stats, Tabs, Cards e Projetos.  
**Referência**: FR-001, FR-002, FR-005 | SC-001  

- [X] T009 [P] [US1] Implementar componente WorkspaceHero em frontend/src/components/dashboard/WorkspaceHero.tsx
- [X] T010 [P] [US1] Implementar componente WorkspaceStats em frontend/src/components/dashboard/WorkspaceStats.tsx
- [X] T011 [P] [US1] Implementar componente OrganizationTabs em frontend/src/components/dashboard/OrganizationTabs.tsx
- [X] T012 [P] [US1] Implementar componente DepartmentCard em frontend/src/components/dashboard/DepartmentCard.tsx
- [X] T013 [P] [US1] Implementar componente OmnichannelCard em frontend/src/components/dashboard/OmnichannelCard.tsx
- [X] T014 [P] [US1] Implementar componente ProjectsSection em frontend/src/components/dashboard/ProjectsSection.tsx
- [X] T015 [US1] Refatorar DashboardPage conectando useWorkspacesQuery, useAuth e componentes modulares em frontend/src/app/page.tsx

---

## Phase 4: User Story 2 — Reatividade Pós-Mutação Instantânea (US2)

**Story Goal**: Fazer com que toda criação ou edição de entidades 4-Tier revalide automaticamente o cache `["workspaces"]` sem exigir recarga manual de página.  
**Independent Test**: Submeter o formulário de uma nova entidade e verificar seu aparecimento imediato no Dashboard HUD.  
**Referência**: FR-004 | SC-002  

- [X] T016 [US2] Validar e assegurar invalidateQueries pós-mutação de workspaces em frontend/src/hooks/useWorkspaceMutations.ts
- [X] T017 [US2] Validar e assegurar invalidateQueries pós-mutação de membros em frontend/src/hooks/useMembershipMutations.ts

---

## Phase 5: User Story 3 — Higiene de Memória e Ciclo de Vida dos Modais (US3)

**Story Goal**: Montar os modais condicionalmente sob demanda explícita, liberando memória e garantindo formulários limpos a cada acionamento.  
**Independent Test**: Abrir modal, preencher dados, cancelar e reabrir, verificando que os campos e erros foram totalmente zerados.  
**Referência**: FR-006 | SC-003  

- [X] T018 [US3] Aplicar renderização condicional externa {isOpen && <Modal />} em todos os modais de frontend/src/app/page.tsx

---

## Phase 6: User Story 4 — Blindagem de Permissões e Segurança Multi-Tenant (US4)

**Story Goal**: Garantir que as restrições de RBAC 4-Tier e isolamento de tenant sejam refletidas visualmente nos botões dos novos componentes e reforçadas no backend.  
**Independent Test**: Autenticar como usuário comum e verificar botões desabilitados na UI e bloqueio de dados de outras organizações no backend.  
**Referência**: FR-008 | SC-004, SC-005  

- [X] T019 [US4] Integrar guards de permissão usePermission nos botões de OrganizationTabs e ProjectsSection
- [X] T020 [US4] Executar verificação de isolamento multi-tenant via DRF com usuário restrito

---

## Phase 7: Polish & Cross-Cutting

*Garantia de qualidade, validação de contratos, testes de ponta a ponta e auditoria constitucional final. Sem label de US.*

- [X] T021 [P] Executar testes unitários do backend com pytest em core/tests/
- [X] T022 [P] Executar verificação de tipos TypeScript com tsc em frontend/
- [X] T023 [P] Executar compilação de produção com npm run build em frontend/
- [X] T024 Validar cenários de aceitação BDD SC-001 a SC-005 em specs/004-full-stack-realignment/spec.md
- [X] T025 Executar auditoria de tarefas no SDDJudge em specs/004-full-stack-realignment/tasks.md

---

## Phase 8: Humanização de UX & Eliminação de Códigos/UUIDs Manuais (US5)

**Story Goal**: Eliminar completamente a necessidade de digitação de IDs numéricos, UUIDs ou siglas forçadas nos formulários, oferecendo busca de usuários autocomplete e seletores amigáveis com auto-preenchimento.  
**Independent Test**: Abrir MemberAllocationModal e selecionar usuário, papel e cargo por nome sem preencher nenhum UUID manual.  

- [X] T026 [P] [US5] Implementar endpoints de busca de usuários e catálogos amigáveis de Roles e Job Titles no backend em core/api/v1/views/user_views.py e core/api/v1/urls.py
- [X] T027 [P] [US5] Criar testes unitários para busca de usuários e catálogos em core/tests/test_catalogs_and_search.py
- [X] T028 [US5] Flexibilizar serializers de membership para aceitar UUID ou slug/código amigável em core/api/v1/serializers.py
- [X] T029 [US5] Reescrever MemberAllocationModal com busca autocomplete por nome/e-mail e dropdowns amigáveis em frontend/src/components/members/MemberAllocationModal.tsx
- [X] T030 [US5] Implementar auto-geração inteligente de siglas e identificadores em DepartmentModal, ProjectModal e SquadModal em frontend/src/components/forms/

---

## Dependency Graph

```text
Phase 0: Grounding & Environment (T000-A a T000-E)
  ↓
Phase 1: Setup da Camada de Dados (T001 a T004)
  ↓
Phase 2: Backend Anti-N+1 & Multi-Tenant (T005 a T008)
  ↓
Phase 3: US1 — Dashboard Modular Reativo (T009 a T015) [MVP Concluído]
  ↓
Phase 4: US2 — Reatividade Pós-Mutação (T016 e T017)
  ↓
Phase 5: US3 — Higiene de Memória dos Modais (T018)
  ↓
Phase 6: US4 — Blindagem RBAC & Multi-Tenant (T019 e T020)
  ↓
Phase 7: Polish & Testes E2E (T021 a T025)
```

---

## Parallel Execution

Tasks marcadas com `[P]` dentro da mesma fase podem ser executadas simultaneamente ou em paralelo:
- **Phase 2**: `T005` (testes performance) e `T006` (testes isolamento) podem ser criados em paralelo.
- **Phase 3**: `T009`, `T010`, `T011`, `T012`, `T013`, `T014` (os 6 componentes modulares) podem ser criados em paralelo por afetarem arquivos isolados em `frontend/src/components/dashboard/`.
- **Phase 7**: `T021` (pytest), `T022` (tsc) e `T023` (build) podem ser executados concorrentemente.
