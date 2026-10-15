<!-- specs/004-full-stack-realignment/research-brainstorming.md | AI-Control v0.0.1 | 14-10-2026 15:32(GMT-04:00) -->

# Registro de Concepção e Brainstorming (Spec 004)
## Realinhamento Estrutural Completo: TanStack Query & Backend Anti-N+1

---

## 1. Resumo Executivo das Decisões

Durante a sessão socrática de depuração e concepção arquitetural entre o Arquiteto e o Usuário, foram estabelecidos os seguintes consensos invioláveis:

1. **Rejeição do "Modelo Pobre":** O data fetching imperativo com `useEffect` + `useState` do Dashboard original e a ausência do `QueryClientProvider` em `Providers.tsx` foram formalmente identificados como um desvio do design canônico do projeto.
2. **Superioridade do TanStack Query:** O gerenciamento de estado do servidor via `@tanstack/react-query` é confirmado como o padrão oficial da plataforma (Princípio P16), devendo assumir 100% das leituras e escritas de dados remotos.
3. **Escopo Expandido (Opção 1 - Realinhamento Completo):** Em vez de um hotfix superficial, a Spec 004 atuará de forma holística:
   - **Frontend:** Provedor React Query seguro para SSR, hooks `useWorkspacesQuery` e `useAuth`, desmembramento do monólito de 730 linhas em componentes modulares e montagem condicional de modais `{isOpen && <Modal />}`.
   - **Backend:** Eliminação do problema N+1 em `ActiveWorkspacesView` (reduzindo de 20+ queries para 4 queries pré-computadas), blindagem multi-tenant nos `get_queryset()` e adoção do Princípio P17 (Serializers dedicados de Leitura vs. Escrita).
4. **Blindagem Contra Quebras de Versão:** É vetado o copy-paste cego do código legado de 2024/2025. Toda a inteligência arquitetural é implementada nativamente com compatibilidade estrita para **React 19.2, Next.js 16.4 (Turbopack), Tailwind v4, Python 3.14 e Django 6.1**.
5. **Governança de Código:** O código não foi comitado nem enviado ao GitHub em estado intermediário quebrado, garantindo a integridade do repositório remoto.

---

## 2. Rastro de Pesquisa e Validação (Grounding Log)

| # | Afirmação Técnica | Verificado? | Fonte Autorizada | Data / Hora |
| :-: | :--- | :-: | :--- | :-: |
| 1 | O Princípio P16 prescreve TanStack Query para Server State e RTK para Client State | **SIM** | [`AI-Control completo.md:L5639`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5639) | 14-10-2026 15:05 |
| 2 | O Princípio P15 exige obrigatoriamente select_related/prefetch_related contra N+1 | **SIM** | [`AI-Control completo.md:L5635`](file:///home/andre/projetos/assistidos/ai-control/AI-Control%20completo.md#L5635) | 14-10-2026 15:05 |
| 3 | React 19 App Router exige criação do QueryClient em useState para isolamento multi-tenant | **SIM** | Documentação Oficial TanStack Query v5 / Next.js 16 | 14-10-2026 15:15 |
| 4 | ActiveWorkspacesView atual executava N+1 queries síncronas em loop aninhado | **SIM** | [`core/api/v1/views/user_views.py:L113-150`](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/user_views.py#L113-L150) | 14-10-2026 15:14 |
| 5 | ViewSets de workspaces permitiam listagem global sem filtro de tenant em get_queryset | **SIM** | [`core/api/v1/views/workspace_mutation_views.py:L26`](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/workspace_mutation_views.py#L26) | 14-10-2026 15:14 |

---

## 3. Estrutura de Decomposição Prevista para o SDD

- **Fase 1 (Specify):** Geração do `spec.md` formal detalhando FR-001 a FR-008 e Acceptance Scenarios SC-001 a SC-006.
- **Fase 2 (Plan):** Geração do `plan.md` com arquitetura de componentes modulares, contratos OpenAPI atualizados e plano de queries SQL.
- **Fase 3 (Tasks):** Geração do `tasks.md` contendo tarefas atômicas sequenciais (T001 a T025) divididas em fases com TDD obrigatório.
- **Fase 4 (Implement):** Execução rigorosa com verificação contínua via `pytest` e `npm run build`.
- **Fase 5 (Converge):** Auditoria constitucional de encerramento da feature.
