<!-- specs/004-full-stack-realignment/research.md | AI-Control v0.0.1 | 14-10-2026 16:00(GMT-04:00) -->
# research.md | AI-Control v0.0.1 | 14-10-2026 16:00(GMT-04:00)

# Technical Research & Architecture Decision Records (ADRs)
## Spec 004: Realinhamento Estrutural Completo (Full-Stack Realignment)

> [!IMPORTANT]
> **Rastreabilidade e Não-Alucinação**:
> Este documento técnico baseia-se e complementa os artefatos de fundamentação:
> - [Documento Canônico de Grounding](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/grounding.md)
> - [Registro de Brainstorming](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/research-brainstorming.md)
> - [Constituição Canônica AI-Control](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md) — Princípios P07, P14, P15, P16, P17.

---

## ADR-001: Instanciação Segura do QueryClient para Next.js 16 (App Router / React 19)

- **Contexto**: No Next.js 16 com React 19, criar uma instância global singleton de `new QueryClient()` fora dos componentes resulta em compartilhamento de cache entre diferentes requisições HTTP durante o Server-Side Rendering (SSR). Em um sistema multi-tenant empresarial com LGPD (P07), isso constitui risco crítico de vazamento de dados entre organizações.
- **Decisão Técnica**: Instanciar o `QueryClient` dentro de um `useState(() => new QueryClient(...))` no componente cliente [`frontend/src/components/Providers.tsx`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/components/Providers.tsx).
- **Verificado em**: Documentação oficial do TanStack Query v5 (Guia de Integração com Next.js App Router) em 14-10-2026.
- **Configurações Padronizadas**:
  - `staleTime: 60 * 1000` (1 minuto de cache fresco).
  - `gcTime: 5 * 60 * 1000` (5 minutos para coleta de lixo).
  - `retry: 1` (resiliência sem retentativas infinitas).
  - `refetchOnWindowFocus: false` (evita refetches indesejados durante preenchimento de formulários).
- **Alternativas Rejeitadas**:
  - *Singleton global fora do React*: Rejeitado devido ao risco de vazamento de memória e contaminação de cache entre requisições SSR multi-tenant.
  - *Criação de novo client a cada render*: Rejeitado porque reiniciaria o cache do cliente a cada re-render da árvore de componentes.

---

## ADR-002: Desacoplamento da Camada de Leitura no Frontend via Custom Hooks Declarativos

- **Contexto**: O Dashboard HUD (`page.tsx`) utilizava `useState(workspaceData)` e uma função manual `loadWorkspaces()` acionada por `useEffect`. Isso tornava inoperante a invalidação de queries disparada pelas mutações (`useWorkspaceMutations` e `useMembershipMutations`).
- **Decisão Técnica**: 
  1. Criar o hook `useWorkspacesQuery` em `frontend/src/hooks/useWorkspacesQuery.ts` consumindo `/api/v1/workspaces/` sob a query key `["workspaces"]`.
  2. Criar o hook `useAuth` em `frontend/src/hooks/useAuth.ts` para centralizar a leitura do Redux Toolkit (`authSlice`), encapsulando `{ user, isAuthenticated, isInitialized, logout }`.
- **Verificado em**: Princípio canônico **(P16) Gerenciamento de Estado Estratégico** em [`AI-Control completo.md:L5639`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5639).
- **Alternativas Rejeitadas**:
  - *Manter callbacks imperativos `onSuccess={() => loadWorkspaces()}`*: Rejeitado por gerar forte acoplamento (prop drilling) e impedir que a UI reaja a eventos de cache desacoplados.

---

## ADR-003: Decomposição Atômica do Monólito de 730 Linhas do Dashboard

- **Contexto**: O arquivo [`frontend/src/app/page.tsx`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/app/page.tsx) acumulava 730 linhas, misturando layout, hero, estatísticas, abas, cartões, drawers e seis modais, violando o Princípio P11 (Código Limpo e Desacoplado).
- **Decisão Técnica**: Particionar o dashboard em componentes atômicos em `frontend/src/components/dashboard/`:
  - `WorkspaceHero.tsx` (~60 linhas)
  - `WorkspaceStats.tsx` (~45 linhas)
  - `OrganizationTabs.tsx` (~50 linhas)
  - `DepartmentCard.tsx` (~40 linhas)
  - `OmnichannelCard.tsx` (~35 linhas)
  - `ProjectsSection.tsx` (~80 linhas)
- **Verificado em**: Boas práticas de Clean Architecture e Diretrizes de Engenharia Didática (P10/P11).
- **Alternativas Rejeitadas**:
  - *Manter o monólito*: Rejeitado pela baixa testabilidade e complexidade de manutenção.

---

## ADR-004: Eliminação do Gargalo N+1 em `ActiveWorkspacesView` via `prefetch_related`

- **Contexto**: A view [`core/api/v1/views/user_views.py`](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/user_views.py#L113-L150) executava queries SQL síncronas dentro de loops aninhados para cada organização e projeto do usuário logado, gerando 20 a 60 queries por request.
- **Decisão Técnica**: Substituir o loop por carregamento em lote com `organization_id__in` e `project_id__in`, agrupando os dados em dicionários na memória com complexidade O(1).
- **Verificado em**: Princípio canônico **(P15) Performance como Funcionalidade (Anti-N+1)** em [`AI-Control completo.md:L5635`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5635).
- **Garantia de Performance**: O endpoint responderá com **no máximo 4 queries SQL** no PostgreSQL, garantindo tempo de resposta sub-100ms.
- **Alternativas Rejeitadas**:
  - *Cache em Redis da view inteira*: Rejeitado como paliativo; a query relacional primária deve ser otimizada na raiz.

---

## ADR-005: Blindagem de Isolamento Multi-Tenant em `get_queryset()` nos ViewSets

- **Contexto**: `OrganizationViewSet` e demais viewsets de workspace retornavam `Organization.objects.all()`, permitindo que usuários comuns de um tenant listassem organizações alheias.
- **Decisão Técnica**: Sobrescrever `get_queryset()` em `OrganizationViewSet`, `DepartmentViewSet`, `ProjectViewSet` e `SquadViewSet` para filtrar estritamente pelos registros vinculados ao `request.user` via memberships ativas, a menos que o usuário seja `platform_superadmin`.
- **Verificado em**: Princípio canônico **(P07) Isolamento de Dados Multi-Tenant** em [`AI-Control completo.md:L5774`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5774).
- **Alternativas Rejeitadas**:
  - *Confiar apenas no frontend para ocultar dados*: Rejeitado veementemente; viola o princípio P14 (API como fonte inquestionável da verdade).
