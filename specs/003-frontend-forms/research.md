<!-- research.md | AI-Control v0.0.1 | 13-10-2026 18:05(GMT-04:00) -->
# Technical Research: Formulários de Governança 4-Tier e Gestão de Membros no Frontend

**Feature:** `specs/003-frontend-forms`  
**Data:** 13-10-2026  
**Autor:** Nexus Architect (via vitalia-spec-plan)  

---

## 1. Visão Geral da Pesquisa

Esta pesquisa estabelece as bases tecnológicas, validações de bibliotecas e padrões de engenharia para viabilizar as operações de mutação (criação e edição) das entidades organizacionais 4-Tier (`Organization`, `Department`, `Project`, `Squad`), bem como a alocação de pessoas em múltiplos níveis hierárquicos com respeito estrito à **Regra de Contenção P3**, segurança criptográfica de dados pessoais (**P07 / Blind Indexing**) e design reativo com **glassmorphism** no ecossistema Next.js 16 + React 19.

---

## 2. Decisões Técnicas com Rastro de Grounding

### Decisão 1: Gerenciamento de Estado de Mutação e Invalidação de Cache no Frontend
- **Escolhido**: TanStack Query v5 (`useMutation` + `queryClient.invalidateQueries`)
- **Verificado em**: [TanStack Query v5 Documentation](https://tanstack.com/query/v5/docs/framework/react/guides/mutations) em 13-10-2026
- **Justificativa**: O frontend já possui `@tanstack/react-query` (^5.90.12) configurado no `Providers.tsx`. O padrão `useMutation` permite controle unificado de estados de loading (`isPending`), rollback otimista ou invalidação seletiva da query key `['workspaces']`, atualizando instantaneamente os contadores e árvores da HUD após qualquer adição ou edição sem recarregar a página.
- **Alternativas**:
  - *Redux Toolkit global mutations*: rejeitado porque mutações de rede geram boilerplate redundante de reducers e thunks quando o React Query já é o padrão estabelecido no app.
  - *Fetch nativo com `useState` local em cada modal*: rejeitado por falta de sincronização entre os modais e os cartões da topologia no `page.tsx`.

### Decisão 2: Validação de Formulários no Cliente com Zod
- **Escolhido**: Zod (^3.24.2)
- **Verificado em**: [Zod Documentation](https://zod.dev/?id=basic-usage) em 13-10-2026
- **Justificativa**: Já presente nas dependências do `package.json`. Permite inferir tipos TypeScript diretamente dos schemas de validação (`z.infer<typeof Schema>`), garantindo validação em tempo real de slugs, e-mails, campos obrigatórios e regex antes do envio ao backend, reduzindo requisições rejeitadas com erro 400.
- **Alternativas**:
  - *Validação imperativa com if/else*: rejeitado por alta propensão a bugs e duplicação de regras em modais.
  - *Yup / Joi*: rejeitado porque Zod já está instalado e possui integração nativa com TypeScript 5.

### Decisão 3: Padrão Arquitetural de Modais e Drawers Glassmorphism
- **Escolhido**: Componentes React 19 nativos com Tailwind CSS v4 e Portal (`createPortal`)
- **Verificado em**: [React 19 createPortal Reference](https://react.dev/reference/react-dom/createPortal) em 13-10-2026
- **Justificativa**: O design system do AI-Control adota glassmorphism dark (`#090d16`, `border-slate-800`, `backdrop-blur-md`, `bg-slate-900/80`). O uso de portais nativos de React 19 renderiza os modais e o drawer retrátil na raiz do DOM (`document.body`), prevenindo problemas de `z-index` e contexto de empilhamento CSS dentro dos cards do Dashboard, sem a sobrecarga de peso de bibliotecas de componentes externas que exigiriam sobrescrever temas.
- **Alternativas**:
  - *Radix Dialog / Drawer*: considerado, mas a implementação nativa em Tailwind v4 reduz atrito de dependências em React 19 e preserva 100% da fidelidade estética com o HUD.
  - *Páginas separadas (`/organizations/new`)*: rejeitado pelo requisito de ergonomia (FR-009) que exige mutações no contexto dos cartões HUD.

### Decisão 4: Endpoints de Mutação e Serializers no Django REST Framework
- **Escolhido**: ViewSets RESTful dedicados com serializers de escrita especializados e anotações `@extend_schema`
- **Verificado em**: [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/en/latest/customization.html) em 13-10-2026
- **Justificativa**: O backend utiliza Django 6.1 e `djangorestframework~=3.18.3`. A criação de ViewSets dedicados para workspaces e memberships sob `/api/v1/workspaces/` com anotações `@extend_schema` assegura tipagem OpenAPI 3.0 completa, viabilizando a regeneração automática de contratos TypeScript via `npm run api:generate`.
- **Alternativas**:
  - *Endpoint monolítico RPC (`/api/v1/mutate/`)*: rejeitado por violar convenções RESTful e dificultar validações granulares de permissão por método HTTP.

### Decisão 5: Blind Indexing Criptográfico para Onboarding Seguro (LGPD / P07)
- **Escolhido**: `django-crypto-fields` integrado ao método `UserProfile.save()`
- **Verificado em**: [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html) em 13-10-2026
- **Justificativa**: Garante que o cadastro imediato de usuários durante a alocação de equipe produza tokens determinísticos seguros (`search_tokens`) sem expor dados pessoais identificáveis (PII) em texto puro na base de dados, permitindo buscas indexadas confidenciais.
- **Alternativas**:
  - *Armazenamento em texto puro com criptografia posterior em batch*: rejeitado por violar imediatamente P06 e P07.

### Decisão 6: Hook Proativo de RBAC no Frontend
- **Escolhido**: Hook `usePermission` consumindo as permissões agregadas de `GET /api/v1/users/me/`
- **Verificado em**: [OWASP Proactive Controls - Access Control](https://owasp.org/www-project-proactive-controls/v3/en/c7-enforce-access-controls) em 13-10-2026
- **Justificativa**: O endpoint `/api/v1/users/me/` já fornece o perfil do usuário logado e suas permissões ativas. Uma função pura `hasPermission(user, requiredPerm, scope)` com retorno booleano estrito (`true`/`false`) permite renderizar botões condicionalmente ou desabilitá-los com tooltips, enquanto o backend mantém a barreira definitiva (HTTP 403).
- **Alternativas**:
  - *Ocultação pura no CSS sem validação programática*: rejeitado por risco de bypass trivial via DevTools.
