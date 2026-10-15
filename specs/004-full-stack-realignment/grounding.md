<!-- specs/004-full-stack-realignment/grounding.md | AI-Control v0.0.1 | 14-10-2026 15:30(GMT-04:00) -->

# Documento Canônico de Grounding Técnico (Spec 004)
## Realinhamento Estrutural Completo: Frontend TanStack Query & Backend Anti-N+1 Multi-Tenant

> [!IMPORTANT]
> **Propósito do Documento**: Este artefato é a **Fonte Canônica da Verdade Técnica** para guiar, fundamentar e auditar todas as fases do ciclo dSDD (Specify → Plan → Tasks → Implement → Converge) da **Spec 004**. Nenhum código ou plano deve desviar das regras aqui homologadas.

---

## 1. Contexto Histórico e Justificativa de Engenharia

O projeto **AI-Control** possui como base canônica o documento [`AI-Control completo.md`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md), que estabeleceu a Constituição do Arquiteto com 19 princípios invioláveis.

Durante a construção inicial do dashboard, um modelo imperativo "pobre" (`useEffect` + `useState` com N+1 queries síncronas) foi introduzido. Ao adicionarmos os formulários da Spec 003, construídos sobre a stack moderna do `@tanstack/react-query`, manifestou-se um **conflito de paradigmas de estado** (erro de runtime `No QueryClient set`).

Esta Spec 004 executa o **Realinhamento Estrutural Completo**, eliminando a dívida técnica tanto no Frontend quanto no Backend, conectando a arquitetura nativamente à stack de ponta de 2026 sem copy-paste cego do legado.

---

## 2. Matriz Constitucional de Princípios Aplicáveis

| Princípio | Definição Canônica (`AI-Control completo.md`) | Aplicação Estrita na Spec 004 |
| :--- | :--- | :--- |
| **(P16) Gerenciamento de Estado Estratégico** | *TanStack Query para estado de servidor (cache, revalidação e loading); Redux Toolkit (RTK) exclusivamente para estado de cliente (tokens JWT, flags de sessão).* | Frontend unificado: eliminar `loadWorkspaces()` manual; adotar `useQuery` para leituras e `useMutation` para escritas com invalidação automática de `["workspaces"]`. |
| **(P15) Performance como Funcionalidade (Anti-N+1)** | *O uso de `select_related` e `prefetch_related` é obrigatório em QuerySets que acessem dados relacionados em views e serializers.* | Reescrever `ActiveWorkspacesView` no backend para eliminar o loop aninhado de 20+ queries, reduzindo para **2 queries com `prefetch_related`**. |
| **(P17) Serializers Dedicados Leitura vs. Escrita** | *Criar serializers distintos para leitura (`ReadOnlySerializer`) e escrita (`WriteOnlySerializer`).* | Separar serializers em `OrganizationViewSet`, `DepartmentViewSet`, `ProjectViewSet` e `SquadViewSet` (usando serializers detalhados para `list`/`retrieve` e enxutos para `create`/`update`). |
| **(P07) Isolamento Multi-Tenant Rigoroso** | *Isolamento de dados por `organization_id`. Queries sempre com filtro de tenant auditável.* | Sobrescrever `get_queryset()` em todos os ViewSets de workspaces e memberships para restringir acesso às organizações vinculadas ao usuário autenticado. |
| **(P14) O Contrato da API como Fonte da Verdade** | *Serializers do DRF com anotações `@extend_schema` completas via `drf-spectacular`.* | Manter 100% dos novos endpoints documentados para geração automática de tipos TypeScript via `npm run api:generate`. |
| **(P03) Grounding e Blindagem de Versões** | *Validar comportamento real de APIs e dependências antes de implementar.* | Não utilizar dependências obsoletas do legado de 2024; adaptar padrões ao **React 19.2 + Next.js 16.4 Turbopack + Tailwind v4 + Django 6.1**. |

---

## 3. Matriz de Compatibilidade de Versões (Fronteira 2026 vs. Legado 2024)

| Dependência | Versão Atual no Projeto | Versão no Legado 2024 | Regra de Engenharia na Spec 004 |
| :--- | :---: | :---: | :--- |
| **React** | `19.2.0` | `18.2.0` | **Não usar `forwardRef`**. Props `ref` diretas. Hidratação estrita: instanciar `QueryClient` dentro de `useState` em Client Component. |
| **Next.js** | `16.4.0` (Turbopack) | `14.2.0` | **App Router nativo**. Provedores em `Providers.tsx` com `'use client'`. Zero singletons globais fora do ciclo de vida React para prevenir vazamento SSR. |
| **@tanstack/react-query** | `^5.90.12` | `^5.28.0` | Usar sintaxe moderna com objeto de opções único (`useQuery({ queryKey, queryFn })`). Desabilitar `refetchOnWindowFocus` para evitar piscar formulários. |
| **Tailwind CSS** | `@tailwindcss/postcss ^4` | `v3.4.1` | **CSS-First**. Manter paleta Glassmorphism dark existente (`#090d16`, `border-slate-800`, `backdrop-blur`). Não injetar plugins legados do v3. |
| **Redux Toolkit** | `^2.11.0` | `^2.2.0` | Preservar `authSlice` para tokens e `user` em memória. Criar hook `useAuth()` para desacoplar as telas do Redux direto. |
| **Python / Django** | `3.14.4` / `6.1.2` | `3.11` / `5.0` | `prefetch_related` com `Prefetch` objects explicitamente tipados. Testes unitários com `pytest-django`. |

---

## 4. Arquitetura Detalhada do Frontend

### 4.1. Camada de Provedores (`frontend/src/components/Providers.tsx`)
```tsx
'use client';

import React, { useState } from 'react';
import { Provider as ReduxProvider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { store } from '@/store';
import { AuthHydrator } from './AuthHydrator';

export function Providers({ children }: { children: React.ReactNode }) {
  // Instanciação segura por sessão de cliente (Isolamento SSR multi-tenant)
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minuto de cache fresco
            gcTime: 5 * 60 * 1000, // 5 minutos de coleta de lixo
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <ReduxProvider store={store}>
      <QueryClientProvider client={queryClient}>
        <AuthHydrator>{children}</AuthHydrator>
        <Toaster position="top-right" theme="dark" richColors closeButton />
      </QueryClientProvider>
    </ReduxProvider>
  );
}
```

### 4.2. Custom Hook de Leitura (`frontend/src/hooks/useWorkspacesQuery.ts`)
```ts
'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { WorkspaceTree } from '@/types/auth';

export const WORKSPACES_QUERY_KEY = ['workspaces'] as const;

export function useWorkspacesQuery() {
  return useQuery({
    queryKey: WORKSPACES_QUERY_KEY,
    queryFn: async () => {
      const response = await api.get<WorkspaceTree>('/api/v1/workspaces/');
      return response.data;
    },
    staleTime: 60 * 1000,
  });
}
```

### 4.3. Custom Hook de Autenticação (`frontend/src/hooks/useAuth.ts`)
```ts
'use client';

import { useAppSelector, useAppDispatch } from '@/store';
import { logout as reduxLogout } from '@/store/authSlice';
import { useRouter } from 'next/navigation';

export function useAuth() {
  const dispatch = useAppDispatch();
  const router = useRouter();
  const { user, isAuthenticated, isInitialized } = useAppSelector((state) => state.auth);

  const logout = () => {
    dispatch(reduxLogout());
    router.push('/login');
  };

  return {
    user,
    isAuthenticated,
    isInitialized,
    logout,
  };
}
```

### 4.4. Desmembramento Modular do Dashboard Monolítico (`page.tsx`)
Em vez de um arquivo de 730 linhas, o dashboard será particionado em componentes atômicos em `frontend/src/components/dashboard/`:
1. **`WorkspaceHero.tsx`**: Card superior com identidade decodificada, badges RBAC e botão de inspeção REST.
2. **`WorkspaceStats.tsx`**: Grid de 4 cards com métricas agregadas (Organizações, Departamentos, Projetos, Squads).
3. **`OrganizationTabs.tsx`**: Seletor horizontal de abas das organizações ativas com botão `+ Nova Org`.
4. **`DepartmentCard.tsx`**: Bloco lateral com contagem e lista de departamentos da organização ativa.
5. **`OmnichannelCard.tsx`**: Bloco lateral de status de instância omnichannel e roteamento com Soft FK.
6. **`ProjectsSection.tsx`**: Lista de projetos e squads aninhadas com badges de papel e botões de time/alocação.
7. **Montagem Condicional Externa**:
   ```tsx
   {isOrgModalOpen && <OrganizationModal isOpen onClose={() => setIsOrgModalOpen(false)} />}
   {isDeptModalOpen && <DepartmentModal isOpen ... onClose={() => setIsDeptModalOpen(false)} />}
   {isProjModalOpen && <ProjectModal isOpen ... onClose={() => setIsProjModalOpen(false)} />}
   {isSquadModalOpen && <SquadModal isOpen ... onClose={() => setIsSquadModalOpen(false)} />}
   {isAllocationModalOpen && <MemberAllocationModal isOpen ... onClose={() => setIsAllocationModalOpen(false)} />}
   {isQuickUserModalOpen && <QuickUserModal isOpen ... onClose={() => setIsQuickUserModalOpen(false)} />}
   ```

---

## 5. Arquitetura Detalhada do Backend

### 5.1. Otimização Anti-N+1 em `ActiveWorkspacesView` ([`user_views.py`](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/user_views.py))
Substituição dos loops aninhados por `prefetch_related` pré-computado:
```python
class ActiveWorkspacesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: WorkspaceTreeSerializer})
    def get(self, request):
        user = request.user
        
        # 1. Carrega todas as memberships de organização do usuário em 1 query com joins
        org_mems = OrganizationMembership.objects.filter(
            user=user, is_active=True
        ).select_related('organization', 'role', 'job_title')

        org_ids = [om.organization_id for om in org_mems]

        # 2. Carrega todos os departamentos em 1 query
        depts_by_org = defaultdict(list)
        for dept in Department.objects.filter(organization_id__in=org_ids).values('id', 'organization_id', 'name', 'slug', 'code'):
            depts_by_org[dept['organization_id']].append(dept)

        # 3. Carrega projetos com memberships do usuário em 1 query
        proj_mems = ProjectMembership.objects.filter(
            user=user, project__organization_id__in=org_ids, is_active=True
        ).select_related('project', 'role', 'job_title')

        proj_ids = [pm.project_id for pm in proj_mems]

        # 4. Carrega squads com memberships do usuário em 1 query
        sq_mems = SquadMembership.objects.filter(
            user=user, squad__project_id__in=proj_ids, is_active=True
        ).select_related('squad', 'role', 'job_title')
        
        # Mapeamento em memória O(1) sem nenhuma query adicional no loop
        # Total de queries: 4 (em vez de 20+ no loop N+1)
```

### 5.2. Isolamento Multi-Tenant em `get_queryset()` dos ViewSets
```python
class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    
    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'platform_role', None) in ['platform_superadmin', 'platform_support']:
            return Organization.objects.all().order_by('name')
        
        # Restringe estritamente às organizações onde o usuário é membro ativo
        return Organization.objects.filter(
            memberships__user=user, memberships__is_active=True
        ).distinct().order_by('name')
```

---

## 6. Rastreabilidade de Testes e Cenários de Aceitação (BDD)

### SC-001: Boot do HUD sem Exceções em Runtime
- **Dado que** o usuário está autenticado e acessa `http://localhost:3000/`,
- **Quando** a página monta no navegador do cliente,
- **Então** nenhum erro de `QueryClientProvider` é lançado, os dados de workspaces são carregados via `useWorkspacesQuery` e exibidos no HUD com estado de loading suave.

### SC-002: Reatividade Instantânea sem Reload Manual
- **Dado que** o gestor abre o modal de criação de departamento ou projeto,
- **Quando** a mutação é confirmada e retorna HTTP 201 Created,
- **Então** o hook dispara `queryClient.invalidateQueries({ queryKey: ["workspaces"] })` e a árvore do Dashboard revalida automaticamente, exibindo o novo elemento sem necessidade de recarregar a página ou clicar em "Atualizar Árvore".

### SC-003: Higiene de Memória e Ciclo de Vida dos Modais
- **Dado que** um formulário foi preenchido parcialmente e fechado pelo usuário,
- **Quando** o usuário clica novamente para abrir o modal,
- **Então** o formulário é remontado com estado limpo, sem persistência de rascunhos acidentais nem erros de validação anteriores.

### SC-004: Anti-N+1 Performance no Backend
- **Dado que** uma requisição `GET /api/v1/workspaces/` é recebida,
- **Quando** o banco de dados executa a resolução da árvore hierárquica,
- **Então** o número total de queries SQL geradas é menor ou igual a 4, independentemente da quantidade de projetos e squads associados.

### SC-005: Blindagem Multi-Tenant nas Listagens
- **Dado que** um usuário comum de uma organização tenta acessar `GET /api/v1/workspaces/organizations/`,
- **Quando** o endpoint responde,
- **Então** apenas as organizações nas quais o usuário possui vínculo ativo são retornadas, bloqueando vazamento de dados de outros tenants.

---

## 7. Rastro de Grounding e Fontes Autorizadas

| # | Fonte Autorizada | Arquivo / Referência | Confirmação |
| :--- | :--- | :--- | :---: |
| 1 | Arquitetura Canônica AI-Control | [`AI-Control completo.md`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5639) (Princípios P14, P15, P16, P17) | **Confirmado** |
| 2 | Padrão AppProviders Legado | [`AI-Control completo.md:L7559`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L7559) | **Confirmado** |
| 3 | React 19 Docs & TanStack Query v5 | `@tanstack/react-query ^5.90.12` App Router Setup | **Confirmado** |
| 4 | DRF & Django 6.1 Multi-Tenant | `core/api/v1/views/workspace_mutation_views.py` | **Confirmado** |

---
**Fim do Documento de Grounding Técnico (Spec 004)**
