<!-- specs/004-full-stack-realignment/plan.md | AI-Control v0.0.1 | 14-10-2026 16:05(GMT-04:00) -->
# plan.md | AI-Control v0.0.1 | 14-10-2026 16:05(GMT-04:00)

# Plano de Arquitetura e Implementação Técnica (Spec 004)
## Realinhamento Estrutural Completo: Frontend TanStack Query, Modularização do Dashboard e Backend Anti-N+1 Multi-Tenant

> [!IMPORTANT]
> **Rastreabilidade e Não-Alucinação**:
> Este plano técnico é derivado e auditado pelos seguintes artefatos canônicos:
> 1. [Documento Canônico de Grounding](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/grounding.md) — Matriz de compatibilidade React 19 / Next.js 16 e decisões de blindagem SSR.
> 2. [Contratos de Componentes e Interfaces](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/contracts/component-contracts.md) — Assinaturas de props, orquestração de UI e schema JSON da API.
> 3. [Registro de Concepção e Brainstorming](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/research-brainstorming.md) — Alinhamento socrático com o usuário.
> 4. [Technical Research & ADRs](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/research.md) — Decisões ADR-001 a ADR-005 fundamentadas.
> 5. [Constituição e Bíblia Arquitetural AI-Control](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md) — Princípios canônicos P07, P14, P15, P16, P17.

---

## 1. Summary

A **Spec 004** implementa a reengenharia e o realinhamento estrutural da plataforma AI-Control, conectando as pontas que ficaram desalinhadas entre o Dashboard HUD legado e os formulários de governança da Spec 003:
- **No Frontend**: Estabelece o `@tanstack/react-query` como a espinha dorsal de estado de servidor via `QueryClientProvider` seguro para Next.js 16 / React 19, cria hooks de leitura declarativos (`useWorkspacesQuery`, `useAuth`), particiona o monólito de 730 linhas de `page.tsx` em 6 componentes atômicos modulares em `components/dashboard/` e adota a montagem condicional de modais `{isOpen && <Modal />}`.
- **No Backend**: Elimina o gargalo crítico de N+1 queries síncronas em `ActiveWorkspacesView` (`user_views.py`) reduzindo para no máximo 4 queries em lote com mapeamento em memória, blinda o isolamento multi-tenant nos `get_queryset()` de todos os viewsets e estabelece a separação de serializers de leitura vs. escrita (P17).

---

## 2. Technical Context

- **Linguagens e Versões**:
  - Frontend: **TypeScript 5.x**, **React 19.2.0**, **Next.js 16.4.0 (Turbopack)**.
  - Backend: **Python 3.14.4**, **Django 6.1.2**, **Django Rest Framework 3.16+**.
- **Dependências Primárias**:
  - Frontend: `@tanstack/react-query ^5.90.12`, `@reduxjs/toolkit ^2.11.0`, `axios ^1.13.2`, `lucide-react ^0.555.0`, `sonner ^2.0.7`, `zod ^3.24.2`.
  - Backend: `djangorestframework`, `drf-spectacular`, `pytest-django`.
- **Plataforma e Infraestrutura**: Docker Compose (PostgreSQL 16 com `pgvector`, Redis 7).
- **Metas de Performance (Derivadas dos SC-xxx da Spec 004)**:
  - Resolução da árvore hierárquica `GET /api/v1/workspaces/` em **≤ 4 queries SQL** e tempo de resposta **< 100ms**.
  - Reatividade visual no Dashboard pós-mutação em **< 1 segundo**.
  - Tempo de compilação Turbopack sem erros em **~1s**.
- **Restrições de Compatibilidade**:
  - Proibido uso de singletons fora do ciclo de vida React em `Providers.tsx` (risco de vazamento SSR multi-tenant).
  - Proibido importar pacotes ou CSS com plugins legados do Tailwind v3 que quebrem o Tailwind v4.

---

## 3. Constitution Check (Auditoria de Princípios do AI-Control)

| Princípio | Descrição Canônica | Verificação neste Plano | Status |
| :--- | :--- | :--- | :---: |
| **P07** | Privacy by Design & Multi-Tenant Data Vault | `get_queryset()` filtra estritamente por organizações do usuário autenticado. | **COMPLIANT** |
| **P14** | Contrato de API como Fonte da Verdade | Schemas e anotações `@extend_schema` preservados e sincronizados com OpenAPI 3.0. | **COMPLIANT** |
| **P15** | Performance Anti-N+1 Obrigatória | `prefetch_related` em lote em `ActiveWorkspacesView` reduzindo N+1 para 4 queries. | **COMPLIANT** |
| **P16** | Gerenciamento de Estado Estratégico | TanStack Query para Server-State (`useWorkspacesQuery`) e RTK para Client-State. | **COMPLIANT** |
| **P17** | Serializers de Leitura/Escrita Dedicados | Separação de representação de saída vs. validação estrita de entrada nos viewsets. | **COMPLIANT** |
| **P03** | Grounding & Verificação Externa | Padrões de código validados contra React 19 e Next.js 16 App Router sem alucinações. | **COMPLIANT** |

---

## 4. Technical Decisions (Resumo das ADRs)

- **ADR-001 (Providers)**: Instanciação de `QueryClient` em `useState(() => new QueryClient(...))` com `staleTime: 60s`, `retry: 1`, `refetchOnWindowFocus: false`.
- **ADR-002 (Queries & Auth)**: Criação de `useWorkspacesQuery` e `useAuth` para desacoplar Redux e chamadas imperativas.
- **ADR-003 (Componentização)**: Divisão de `page.tsx` em componentes atômicos dentro de `frontend/src/components/dashboard/`.
- **ADR-004 (Anti-N+1)**: Carregamento relacional em lote em `ActiveWorkspacesView` com mapeamento O(1) em memória.
- **ADR-005 (Multi-Tenant)**: Sobrescrita de `get_queryset()` com filtro de associação ativa em `OrganizationMembership`.

---

## 5. Estrutura do Projeto e Arquivos Afetados

```text
ai-control/
├── specs/004-full-stack-realignment/
│   ├── grounding.md                   ← Fonte canônica da verdade técnica
│   ├── contracts/component-contracts.md ← Blindagem de contratos de props, dados e orquestração
│   ├── research-brainstorming.md      ← Rastro de concepção e alinhamento socrático
│   ├── spec.md                        ← Especificação funcional formal
│   ├── checklists/requirements.md     ← Checklist de qualidade de requisitos
│   ├── research.md                    ← Architecture Decision Records (ADR-001 a 005)
│   ├── plan.md                        ← Este plano técnico de arquitetura
│   ├── quickstart.md                  ← Guia executável de validação de ponta a ponta
│   └── tasks.md                       ← Tarefas atômicas sequenciais (próximo passo)
│
├── frontend/src/
│   ├── components/
│   │   ├── Providers.tsx              ← Injeção do QueryClientProvider seguro para SSR
│   │   └── dashboard/                 ← [NOVO] Componentes atômicos do Dashboard
│   │       ├── WorkspaceHero.tsx      ← Apresentação do usuário e status Blind Indexing
│   │       ├── WorkspaceStats.tsx     ← Grid de métricas de Organizações, Deptos, Proj, Squads
│   │       ├── OrganizationTabs.tsx   ← Seletor horizontal de abas das organizações
│   │       ├── DepartmentCard.tsx     ← Card lateral de unidades departamentais
│   │       ├── OmnichannelCard.tsx    ← Card lateral de instância omnichannel Soft FK
│   │       └── ProjectsSection.tsx    ← Lista de projetos e squads com containment rule
│   ├── hooks/
│   │   ├── useWorkspacesQuery.ts      ← [NOVO] Query declarativa de árvore de workspaces
│   │   └── useAuth.ts                 ← [NOVO] Hook de abstração e consumo de sessão Redux
│   └── app/
│       └── page.tsx                   ← Refatorado (< 180 linhas, limpo e reativo)
│
└── core/
    ├── api/v1/views/
    │   ├── user_views.py              ← Otimização Anti-N+1 em ActiveWorkspacesView
    │   └── workspace_mutation_views.py← get_queryset() com filtro estrito de tenant
    └── tests/
        ├── test_workspace_performance.py ← [NOVO] Teste assertNumQueries para validar Anti-N+1
        └── test_workspace_isolation.py   ← [NOVO] Teste de isolamento multi-tenant em get_queryset
```

---

## 6. Visão Geral das Fases de Implementação

### Phase 1: Setup & Grounding da Camada de Dados
- Configuração do `QueryClientProvider` resiliente a SSR em `frontend/src/components/Providers.tsx`.
- Implementação dos hooks canônicos `useWorkspacesQuery.ts` e `useAuth.ts`.
- Validação de compilação Turbopack (`npm run build`).

### Phase 2: Backend Anti-N+1 & Blindagem Multi-Tenant (TDD)
- Criação dos testes unitários `test_workspace_performance.py` (usando `django_assert_num_queries`) e `test_workspace_isolation.py`.
- Refatoração de `ActiveWorkspacesView` em `user_views.py` com carregamento em lote e dicionários em memória.
- Sobrescrita de `get_queryset()` em `OrganizationViewSet`, `DepartmentViewSet`, `ProjectViewSet` e `SquadViewSet`.
- Execução da suíte completa de testes no backend via `pytest`.

### Phase 3: Decomposição Atômica do Dashboard HUD (US1 & US2)
- Criação dos componentes atômicos em `frontend/src/components/dashboard/`:
  - `WorkspaceHero.tsx`
  - `WorkspaceStats.tsx`
  - `OrganizationTabs.tsx`
  - `DepartmentCard.tsx`
  - `OmnichannelCard.tsx`
  - `ProjectsSection.tsx`
- Refatoração de [`frontend/src/app/page.tsx`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/app/page.tsx) substituindo `useState`/`loadWorkspaces` por `useWorkspacesQuery` e consumindo os novos componentes modulares.

### Phase 4: Higiene de Memória e Reatividade dos Modais (US3 & US4)
- Envelopamento de todos os modais 4-Tier com renderização condicional externa `{isOpen && <Modal />}`.
- Conexão da reatividade pós-mutação: confirmação de que criar/editar entidades atualiza a árvore automaticamente via cache do TanStack Query sem reload manual.

### Phase 5: Polish, Validação Cruzada & Verificação Constitucional
- Execução de `npx tsc --noEmit` e `npm run build` no frontend.
- Execução completa do `pytest` com os novos testes de performance e isolamento.
- Validação dos Cenários de Aceitação BDD (SC-001 a SC-005).
- Auditoria constitucional final via SDDJudge.
