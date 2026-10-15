<!-- specs/004-full-stack-realignment/contracts/component-contracts.md | AI-Control v0.0.1 | 14-10-2026 16:15(GMT-04:00) -->
# component-contracts.md | AI-Control v0.0.1 | 14-10-2026 16:15(GMT-04:00)

# Blindagem Contratual de Componentes e Interfaces (Spec 004)
## Contratos Estritos de Tipagem, Dados e Arquitetura Frontend/Backend

> [!IMPORTANT]
> **Propósito deste Artefato**: Eliminar 100% de qualquer margem de alucinação ou divergência de implementação. Qualquer LLM ou desenvolvedor que for escrever o código DEVE seguir estritamente as interfaces, nomes de propriedades e schemas aqui declarados, sem inventar novas props ou renomear chaves.
> 
> **Documentos de Referência**:
> - [spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/spec.md) | [plan.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/plan.md) | [grounding.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/grounding.md) | [AI-Control completo.md](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md)

---

## 1. Contrato da Camada de Dados (Backend `ActiveWorkspacesView` ↔ Frontend `types/auth.ts`)

A resposta do endpoint `GET /api/v1/workspaces/` otimizado contra N+1 **DEVE** satisfazer rigorosamente a seguinte estrutura JSON canônica:

```json
{
  "workspaces": [
    {
      "id": "UUID-string",
      "name": "Nome da Organização",
      "slug": "slug-organizacao",
      "org_type": "COMPANY | HEALTHCARE | UNIVERSITY | ...",
      "role": "org_admin | org_member | null",
      "job_title": "Cargo na Organização | null",
      "departments": [
        {
          "id": "UUID-string",
          "name": "Tecnologia da Informação",
          "slug": "ti",
          "code": "TI"
        }
      ],
      "projects": [
        {
          "id": "UUID-string",
          "name": "Plataforma IA",
          "slug": "plataforma-ia",
          "role": "project_lead | null",
          "job_title": "Líder Técnico | null",
          "squads": [
            {
              "id": "UUID-string",
              "name": "Squad Triagem",
              "slug": "squad-triagem",
              "role": "tech_lead | squad_member | null",
              "job_title": "Engenheiro de ML | null"
            }
          ]
        }
      ]
    }
  ]
}
```

> **Regra Anti-Alucinação para o Backend**: No arquivo `core/api/v1/views/user_views.py`, o carregamento em lote deve agrupar departamentos e projetos mantendo exatamente essas chaves (`id`, `name`, `slug`, `org_type`, `role`, `job_title`, `departments`, `projects`, `squads`). Proibido renomear para `teams`, `units`, `groups` ou qualquer sinônimo.

---

## 2. Contrato de Arquitetura: `page.tsx` como Orquestrador de Estado

Para evitar duplicação ou perda de sincronismo de estado na interface:
- **`DashboardPage` (`frontend/src/app/page.tsx`) é o ÚNICO dono do estado de UI da tela**:
  - Controla `selectedOrgIndex: number` (qual organização está ativa no seletor de abas).
  - Controla abertura/fechamento dos modais (`isOrgModalOpen`, `isDeptModalOpen`, `isProjModalOpen`, `isSquadModalOpen`, `isQuickUserModalOpen`).
  - Controla o estado de `selectedProjectIdForSquad` para pré-vincular o projeto correto no modal de Squad.
  - Controla os estados compartilhados de `isDrawerOpen`, `drawerConfig`, `isAllocationModalOpen` e `allocationTarget`.
- **Os 6 novos componentes são COMPONENTES PUROS DE APRESENTAÇÃO**:
  - Não possuem `useEffect` de busca de dados nem criam instâncias concorrentes de estado de seleção.
  - Recebem dados via props e emitem ações do usuário via callbacks de função (`onSelectOrg`, `onOpenModal`, `onOpenDrawer`).

---

## 3. Contratos de Interfaces TypeScript dos Novos Componentes Modulares

Todos os novos componentes residirão em `frontend/src/components/dashboard/`:

### 3.1. `WorkspaceHero.tsx`
```tsx
import { UserProfile } from '@/types/auth';

export interface WorkspaceHeroProps {
  user: UserProfile | null;
  loading: boolean;
  showJsonInspector: boolean;
  onRefresh: () => void;
  onToggleJsonInspector: () => void;
}
```
*Responsabilidade*: Renderizar o bloco Hero superior com nome do usuário, badges Blind Indexing e RBAC 4-Tier, botão de recarregar (`refetch`) e botão de inspecionar payload REST.

---

### 3.2. `WorkspaceStats.tsx`
```tsx
export interface WorkspaceStatsProps {
  totalOrgs: number;
  totalDepts: number;
  totalProjects: number;
  totalSquads: number;
}
```
*Responsabilidade*: Exibir o grid de 4 cartões com as métricas quantitativas de Organizações, Departamentos, Projetos e Squads com ícones temáticos (Cyan, Indigo, Amber, Emerald).

---

### 3.3. `OrganizationTabs.tsx`
```tsx
import { OrganizationNode } from '@/types/auth';

export interface OrganizationTabsProps {
  organizations: OrganizationNode[];
  selectedIndex: number;
  canManageOrg: boolean;
  onSelectIndex: (index: number) => void;
  onOpenNewOrgModal: () => void;
}
```
*Responsabilidade*: Renderizar o seletor horizontal de abas com scroll suave e badges de slug, botão de adicionar organização com guard de permissão visual (`disabled` se sem privilégio).

---

### 3.4. `DepartmentCard.tsx`
```tsx
import { DepartmentNode } from '@/types/auth';

export interface DepartmentCardProps {
  departments: DepartmentNode[];
  canManageOrg: boolean;
  onOpenNewDeptModal: () => void;
}
```
*Responsabilidade*: Exibir o card de departamentos da organização ativa, listando nome e código (`code`) e botão `+ Depto` protegido por guard de permissão.

---

### 3.5. `OmnichannelCard.tsx`
```tsx
export interface OmnichannelCardProps {
  orgSlug: string;
}
```
*Responsabilidade*: Exibir o card de demonstração de roteamento omnichannel com Soft Foreign Key (`organization_id`), indicando status da instância de IA e canal de mensageria.

---

### 3.6. `ProjectsSection.tsx`
```tsx
import { ProjectNode } from '@/types/auth';
import { DrawerMemberItem } from '@/components/members/TeamDrawer';
import { MembershipScope } from '@/components/members/MemberAllocationModal';

export interface ProjectsSectionProps {
  projects: ProjectNode[];
  canManageThisOrg: boolean;
  isPlatformSuperadmin: boolean;
  onOpenNewProjectModal: () => void;
  onOpenNewSquadModal: (projectId: string) => void;
  onOpenTeamDrawer: (
    title: string,
    subtitle: string,
    scope: MembershipScope,
    targetId: string,
    targetName: string,
    members: DrawerMemberItem[]
  ) => void;
}
```
*Responsabilidade*: Renderizar a listagem de projetos com Containment Rule (squads aninhadas), badges de papéis (`project_lead`, `tech_lead`), botão "+ Squad" e botões "Time" para abrir o `TeamDrawer` contextual.

---

## 4. Contrato do Client TanStack Query (`frontend/src/lib/get-query-client.ts`)

```ts
import { isServer, QueryClient } from '@tanstack/react-query';

function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: (failureCount, error: any) => {
          if (error?.response?.status === 401 || error?.response?.status === 403) return false;
          return failureCount < 1;
        },
        refetchOnWindowFocus: false,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

export function getQueryClient(): QueryClient {
  if (isServer) {
    return makeQueryClient();
  } else {
    if (!browserQueryClient) browserQueryClient = makeQueryClient();
    return browserQueryClient;
  }
}
```

---

## 5. Contrato de Montagem Condicional dos Modais em `page.tsx`

Nenhum modal deve ser montado incondicionalmente no JSX. A montagem no final de `page.tsx` deve seguir estritamente:

```tsx
{isOrgModalOpen && (
  <OrganizationModal isOpen onClose={() => setIsOrgModalOpen(false)} />
)}

{isDeptModalOpen && (
  <DepartmentModal
    isOpen
    organizationId={activeOrg?.id}
    organizations={orgList.map((o) => ({ id: o.id, name: o.name }))}
    onClose={() => setIsDeptModalOpen(false)}
  />
)}

{isProjModalOpen && (
  <ProjectModal
    isOpen
    organizationId={activeOrg?.id}
    organizations={orgList.map((o) => ({ id: o.id, name: o.name }))}
    onClose={() => setIsProjModalOpen(false)}
  />
)}

{isSquadModalOpen && (
  <SquadModal
    isOpen
    projectId={selectedProjectIdForSquad || activeOrg?.projects?.[0]?.id}
    projects={activeOrg?.projects?.map((p) => ({ id: p.id, name: p.name })) || []}
    onClose={() => setIsSquadModalOpen(false)}
  />
)}

{isDrawerOpen && (
  <TeamDrawer
    isOpen
    onClose={() => setIsDrawerOpen(false)}
    title={drawerConfig.title}
    subtitle={drawerConfig.subtitle}
    members={drawerConfig.members}
    onAllocateClick={() => {
      setIsDrawerOpen(false);
      openAllocationModal(drawerConfig.scope, drawerConfig.targetId, drawerConfig.targetName);
    }}
  />
)}

{isAllocationModalOpen && (
  <MemberAllocationModal
    isOpen
    onClose={() => setIsAllocationModalOpen(false)}
    scope={allocationTarget.scope}
    targetId={allocationTarget.targetId}
    targetName={allocationTarget.targetName}
    onOpenQuickUserModal={() => setIsQuickUserModalOpen(true)}
  />
)}

{isQuickUserModalOpen && (
  <QuickUserModal
    isOpen
    onClose={() => setIsQuickUserModalOpen(false)}
  />
)}
```

---

**Com este contrato de interfaces fixado, qualquer alucinação de nomes de variáveis, props ou formato de JSON é bloqueada por checagem estrita de tipos do TypeScript.**
