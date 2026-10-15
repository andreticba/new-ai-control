<!-- specs/004-full-stack-realignment/spec.md | AI-Control v0.0.1 | 14-10-2026 15:55(GMT-04:00) -->
# spec.md | AI-Control v0.0.1 | 14-10-2026 15:55(GMT-04:00)

# Especificação Funcional: Realinhamento Estrutural Completo (Full-Stack Realignment)
## Frontend TanStack Query, Decomposição Modular do Dashboard e Backend Anti-N+1 Multi-Tenant

> [!IMPORTANT]
> **Fontes Obrigatórias de Grounding e Não-Alucinação**:
> Este documento e todas as implementações subsequentes derivam e são estritamente auditados com base nos seguintes documentos:
> 1. [Documento Canônico de Grounding da Spec 004](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/grounding.md) — Diretrizes de compatibilidade, arquitetura e blindagem SSR.
> 2. [Contratos de Componentes e Interfaces](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/contracts/component-contracts.md) — Assinaturas exatas de props, orquestração de UI e schema JSON da API.
> 3. [Registro de Concepção e Brainstorming da Spec 004](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/research-brainstorming.md) — Rastro de decisões técnicas e alinhamento socrático.
> 4. [Constituição e Bíblia Arquitetural AI-Control](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md) — Princípios canônicos invioláveis: P07 (Isolamento de Dados), P14 (Contrato da API), P15 (Performance Anti-N+1), P16 (Gerenciamento de Estado Estratégico) e P17 (Serializers Dedicados).

---

## 1. Visão Geral e Declaração do Problema

### 1.1. Contexto
No ciclo de desenvolvimento anterior, os formulários e modais de governança 4-Tier da Spec 003 foram construídos sobre a stack moderna do `@tanstack/react-query`, porém o Dashboard HUD existente permanecia operando sob um padrão imperativo e defasado (`useEffect` com `useState` local e chamadas manuais). Essa discrepância resultou na ausência do `QueryClientProvider` no encapsulador global, causando falha fatal de runtime (`No QueryClient set`) ao acessar a raiz do frontend.

Adicionalmente, uma auditoria aprofundada na camada de backend revelou que o endpoint agregador de leitura da árvore hierárquica (`ActiveWorkspacesView`) continha um padrão N+1 severo (executando mais de 20 queries síncronas aninhadas), violando o Princípio P15, e que os viewsets de workspaces careciam de filtros estritos de tenant em requisições de listagem, violando o Princípio P07.

### 1.2. Objetivo
Executar o **Realinhamento Estrutural Completo** da plataforma:
1. **No Frontend:** Estabelecer o `@tanstack/react-query` como a fonte única da verdade para o estado de servidor (Server-State), instanciando o `QueryClientProvider` de forma segura para Next.js 16 / React 19, criando hooks declarativos de leitura (`useWorkspacesQuery`, `useAuth`), desmembrando o monólito de 730 linhas do dashboard em componentes atômicos modulares e garantindo higiene de ciclo de vida aos modais 4-Tier via renderização condicional externa.
2. **No Backend:** Sanar definitivamente o gargalo N+1 reescrevendo `ActiveWorkspacesView` com `prefetch_related` pré-computado (reduzindo a resolução da árvore para no máximo 4 queries), blindar o isolamento multi-tenant nos `get_queryset()` e separar serializers de leitura e escrita conforme o Princípio P17.

---

## 2. Requisitos Funcionais (Functional Requirements)

- **[FR-001] Provedor TanStack Query Resiliente a SSR (MUST):**  
  O frontend DEVE instanciar o `QueryClient` dentro de um hook de ciclo de vida seguro (`useState`) no componente cliente [`Providers.tsx`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/components/Providers.tsx), garantindo que instâncias de cache não vazem entre requisições de renderização do servidor em ambiente Next.js 16 (App Router / React 19).

- **[FR-002] Hook Declarativo de Árvore de Workspaces (MUST):**  
  O frontend DEVE implementar o custom hook `useWorkspacesQuery` utilizando a query key canônica `["workspaces"]` para carregar a topologia 4-Tier do usuário logado, expondo estados semânticos nativos (`isLoading`, `isError`, `data`, `refetch`).

- **[FR-003] Hook Centralizado de Sessão e Autenticação (MUST):**  
  O frontend DEVE implementar o custom hook `useAuth` para encapsular e desacoplar o consumo do Redux Toolkit (`authSlice`), provendo `{ user, isAuthenticated, isInitialized, logout }` sem que as páginas acessem `useAppSelector` de forma repetitiva.

- **[FR-004] Reatividade Automática Pós-Mutação (MUST):**  
  Toda operação de criação ou edição de Organização, Departamento, Projeto, Squad ou Membro DEVE disparar a invalidação da query `["workspaces"]`, fazendo com que toda a interface do Dashboard HUD revalide e reflita os novos dados em tempo real sem necessidade de reload de página ou callbacks manuais.

- **[FR-005] Decomposição Modular do Dashboard HUD (MUST):**  
  O arquivo monolítico [`frontend/src/app/page.tsx`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/app/page.tsx) DEVE ser refatorado e particionado em componentes atômicos e especializados na pasta `frontend/src/components/dashboard/`:
  - `WorkspaceHero`: Apresentação da identidade decodificada e badges de governança.
  - `WorkspaceStats`: Indicadores numéricos de entidades ativas.
  - `OrganizationTabs`: Navegação em abas entre organizações ativas.
  - `DepartmentCard`: Exibição dos departamentos estruturais.
  - `OmnichannelCard`: Card de instância e roteamento com Soft FK.
  - `ProjectsSection`: Lista de projetos e squads aninhadas com containment rule.

- **[FR-006] Ciclo de Vida e Higiene de Memória dos Modais (MUST):**  
  Todos os modais 4-Tier (`OrganizationModal`, `DepartmentModal`, `ProjectModal`, `SquadModal`, `MemberAllocationModal`, `QuickUserModal`) DEVEM ser montados condicionalmente na página pai (`{isOpen && <Modal />}`), garantindo que seus hooks internos só executem sob demanda explícita do usuário e que os formulários abram limpos a cada acionamento.

- **[FR-007] Resolução Anti-N+1 da Árvore Hierárquica no Backend (MUST):**  
  O endpoint `GET /api/v1/workspaces/` ([`user_views.py`](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/user_views.py)) DEVE ser refatorado para carregar a hierarquia completa de Organizações, Departamentos, Projetos e Squads do usuário utilizando `prefetch_related` e indexação em memória O(1), limitando a execução no banco a **no máximo 4 queries SQL**, independentemente da profundidade ou volume da árvore.

- **[FR-008] Blindagem de Isolamento Multi-Tenant nos ViewSets (MUST):**  
  Os ViewSets de workspaces e memberships no backend DEVEM sobrescrever o método `get_queryset()` para garantir que usuários sem privilégios de plataforma (`platform_superadmin`) visualizem estritamente os registros pertencentes às organizações onde possuem vínculo ativo, prevenindo vazamento de dados de outros clientes.

---

## 3. Requisitos Não-Funcionais (Restrições e Governança)

- **[NFR-001] Preservação do Design System Glassmorphism:** Todos os novos componentes modulares do dashboard DEVEM manter a paleta visual escura, bordas `slate-800`, efeitos `backdrop-blur` e tipografia moderna do projeto.
- **[NFR-002] Compatibilidade Estrita com React 19 e Next.js 16 (P03):** Não utilizar bibliotecas, plugins de Tailwind v3 ou padrões obsoletos de ciclo de vida que provoquem conflitos de peer dependencies ou hydration mismatch no Turbopack.
- **[NFR-003] Manutenibilidade e Limpeza de Código (P11):** Nenhuma tela ou componente deve exceder 250 linhas de código; componentes devem ter responsabilidade única e desacoplada.
- **[NFR-004] TDD e Verificação Contínua (P05):** O backend DEVE manter 100% de testes unitários passando (`pytest`), incluindo novos testes para aferir o limite de queries SQL (Anti-N+1) e o isolamento de tenant em `get_queryset()`.

---

## 4. Histórias de Usuário (User Stories)

- **US1 — Navegação Reativa e Sem Falhas no Dashboard:**  
  **Como um** gestor ou colaborador autenticado,  
  **eu quero** acessar o Dashboard HUD imediatamente sem telas vermelhas de erro e com carregamento suave dos meus workspaces,  
  **para que** eu visualize instantaneamente a estrutura operacional da minha organização.

- **US2 — Atualização Instantânea Pós-Cadastro:**  
  **Como um** líder operacional cadastrando uma nova squad ou projeto,  
  **eu quero** que o novo elemento apareça na tela assim que o modal confirmar o sucesso,  
  **para que** eu não precise atualizar a página inteira manualmente.

- **US3 — Higiene e Isolamento de Formulários:**  
  **Como um** operador preenchendo um formulário complexo de alocação ou projeto,  
  **eu quero** que o fechamento do modal descarte o rascunho anterior e o reabra limpo,  
  **para que** dados residuais de cadastros anteriores não gerem inconsistências.

- **US4 — Segurança Multi-Tenant e Alta Performance:**  
  **Como um** auditor de segurança e arquiteto de sistemas,  
  **eu quero** que o backend responda à árvore de trabalho em poucas queries otimizadas e filtre rigorosamente os dados por tenant,  
  **para que** a infraestrutura suporte milhares de usuários sem gargalos de banco nem vazamento de dados entre empresas.

---

## 5. Critérios de Aceite (Acceptance Scenarios)

### SC-001: Carregamento do Dashboard HUD sem Erros de Runtime
- **Dado que** o usuário está devidamente autenticado com token JWT válido,
- **Quando** ele navega para `http://localhost:3000/`,
- **Então** a página carrega sem lançar exceções no console, exibe o esqueleto/spinner suave durante a resolução de `useWorkspacesQuery` e renderiza os cards com os dados reais do usuário.

### SC-002: Sincronização Declarativa e Reatividade de Cache
- **Dado que** o usuário está com a aba de uma organização aberta no HUD,
- **Quando** ele clica em "+ Novo Projeto", preenche os dados válidos e confirma a criação,
- **Então** o modal fecha, a query `["workspaces"]` é invalidada automaticamente e o novo projeto é renderizado na lista em menos de 1 segundo sem recarga manual da página.

### SC-003: Higiene de Memória dos Modais
- **Dado que** o usuário abriu o modal de Organização, digitou parte do nome e fechou no botão "Cancelar",
- **Quando** ele clica novamente em "Nova Organização",
- **Então** o formulário é exibido completamente limpo, com campos vazios e sem mensagens de erro remanescentes.

### SC-004: Eficiência de Queries Anti-N+1 no Backend
- **Dado que** um usuário possui vínculos com 3 organizações, cada uma contendo 4 departamentos, 5 projetos e 10 squads,
- **Quando** uma requisição `GET /api/v1/workspaces/` é processada,
- **Então** o total de queries SQL executadas contra o banco de dados PostgreSQL é menor ou igual a 4, eliminando completamente queries em loop.

### SC-005: Isolamento de Tenant em Listagens de Workspace
- **Dado que** um usuário comum "analista.silva" pertence exclusivamente à organização "Hospital Universitário",
- **Quando** ele efetua uma chamada `GET /api/v1/workspaces/organizations/`,
- **Então** a resposta da API contém apenas a organização "Hospital Universitário", não exibindo organizações de outros tenants presentes no banco.

---

## 6. Suposições Verificadas (Grounding Log)

- **`@tanstack/react-query ^5.90.12`**: Verificado em `frontend/package.json` e documentação oficial (v5 App Router pattern).
- **`Next.js 16.4.0 (Turbopack) & React 19.2.0`**: Verificado no log de compilação do container frontend.
- **`Anti-N+1 (Princípio P15)`**: Verificado em [`AI-Control completo.md:L5635`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5635).
- **`Gerenciamento de Estado Estratégico (Princípio P16)`**: Verificado em [`AI-Control completo.md:L5639`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5639).
- **`ActiveWorkspacesView N+1 issue`**: Verificado em [`core/api/v1/views/user_views.py:L113`](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/user_views.py#L113).

---

## 7. Fora do Escopo (Out of Scope)

- Redesenho completo das telas de autenticação ou fluxo de login (permanecem inalteradas).
- Alteração nos modelos de dados do banco de dados (os models Django existentes atendem perfeitamente).
- Implementação de websockets para chat ao vivo (coberto na spec de omnichannel e agentes).
