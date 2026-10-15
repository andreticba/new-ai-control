<!-- spec.md | AI-Control v0.0.1 | 13-10-2026 17:35(GMT-04:00) -->
# spec.md | AI-Control v0.0.1 | 13-10-2026 17:35(GMT-04:00)

# Especificação de Funcionalidade: Formulários de Governança 4-Tier e Gestão de Membros no Frontend

**Data:** 13-10-2026  
**Autor/Agente:** Nexus Architect (via vitalia-spec-specify)  
**Feature:** `specs/003-frontend-forms`  
**Status:** APROVADO (Exit Code 0 - SDDJudge)  

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

Com a consolidação da infraestrutura em Django 6.1 e a entrega da primeira versão do HUD de visualização em Next.js 16 (`specs/002-frontend-seed`), o sistema passou a renderizar a topologia de governança em modo exclusivamente leitura (`GET /api/v1/workspaces/`).

O objetivo desta especificação (P0) é entregar a capacidade operacional completa para que gestores e operadores realizem mutações estruturais diretamente pela interface web:
1. **Governança Estrutural:** Adicionar e editar Organizações, Departamentos, Projetos e Squads, com validações de unicidade e respeito irrestrito à regra hierárquica.
2. **Gestão de Pessoas e Vínculos:** Alocar e editar membros nos três níveis hierárquicos (`OrganizationMembership`, `ProjectMembership`, `SquadMembership`), atribuindo papéis de autorização (`Role`) e cargos de interface (`JobTitle`).
3. **Onboarding Rápido:** Permitir o cadastro imediato de novos usuários durante o fluxo de alocação de equipe, mantendo a geração automática de Blind Indexing criptográfico.
4. **Ergonomia e Integridade P3:** Garantir uma experiência fluida com Modais e Drawer lateral preservando o design com **glassmorphism**, com filtragem reativa que impede violações da **Regra de Contenção (P3)** antes do envio ao backend.

---

## 2. Requisitos Funcionais

- **FR-001: Gestão e Criação de Organizações:**
  - O sistema MUST permitir que operadores autorizados criem e editem organizações informando Nome (`name`), Slug (`slug`), Tipo (`org_type`: HEALTHCARE, UNIVERSITY, COMPANY, NGO, GOVERNMENT, INDIVIDUAL, OTHER) e Status Ativo (`is_active`).
  - O slug MUST ser único em toda a base de dados. Caso não informado, o backend MUST derivá-lo de forma segura a partir do nome.
  - A operação MUST exigir a permissão `org.manage` no nível da organização ou papel de plataforma correspondente.

- **FR-002: Gestão e Criação de Departamentos:**
  - O sistema MUST permitir que operadores criem e editem departamentos vinculados à organização ativa informando Nome (`name`), Código (`code` textual curto, ex.: "TI", "FIN", "DCOMP") e Descrição (`description`).
  - A combinação de organização e código (`organization_id`, `code`) MUST ser estritamente única.
  - A operação MUST vincular o departamento obrigatoriamente à organização selecionada no contexto da interface e exigir a permissão `org.manage`.

- **FR-003: Gestão e Criação de Projetos:**
  - O sistema MUST permitir a criação e edição de projetos vinculados à organização ativa informando Nome (`name`), Slug (`slug`), Tipo de Projeto (`project_type`: RESEARCH, DEVELOPMENT, OPERATIONAL, CONSULTING, OTHER), Status (`status`: PLANNING, ACTIVE, PAUSED, COMPLETED, CANCELLED) e Descrição.
  - O slug do projeto MUST ser único dentro do escopo da organização proprietária.
  - A operação MUST exigir a permissão `project.manage` no projeto ou `org.manage` na organização pai.

- **FR-004: Gestão e Criação de Squads com Regra de Contenção P3:**
  - O sistema MUST permitir a criação e edição de squads informando Nome (`name`), Slug (`slug`), Missão (`mission`) e Status Ativo (`is_active`).
  - Cada squad MUST ser subordinada rigidamente a um projeto específico da organização ativa, sendo vedada a existência de squads sem projeto pai (inviolabilidade P3).
  - O slug da squad MUST ser único dentro do escopo do projeto pai.
  - A operação MUST exigir a permissão `squad.manage` na squad, `project.manage` no projeto ou `org.manage` na organização.

- **FR-005: Alocação e Gestão de Membros de Organização (`OrganizationMembership`):**
  - O sistema MUST permitir associar usuários a organizações ativas, definindo Papel (`role_id` com escopo obrigatório `ORGANIZATION`), Cargo (`job_title_id` opcional com nível `ORGANIZATION`) e Lotação departamental (`department_id` opcional).
  - O sistema MUST permitir editar o papel/cargo de um membro ou desativar o vínculo (`is_active=False`).
  - O sistema MUST garantir a unicidade de vínculo ativo por par `(user, organization)`.

- **FR-006: Alocação e Gestão de Membros de Projeto (`ProjectMembership`) com Validação P3 Contínua:**
  - O sistema MUST validar obrigatoriamente, em tempo real e durante todo o processo de adição, alteração de cargo ou reativação de membros de projeto, a existência e o status ativo (`is_active=True`) de `OrganizationMembership` na organização pai (ou papel `org_guest` caso `is_external=True`), rejeitando qualquer associação inválida.
  - O sistema MUST permitir associar usuários elegíveis a projetos, definindo Papel (`role_id` com escopo `PROJECT`), Cargo (`job_title_id` opcional com nível `PROJECT`) e indicador de Colaborador Externo (`is_external`).
  - O sistema MUST garantir a continuidade da Regra de Contenção P3: caso o vínculo de um usuário na organização pai seja inativado, qualquer tentativa de manter ou alterar seu status ativo no projeto subordinado MUST ser bloqueada.

- **FR-007: Alocação e Gestão de Membros de Squad (`SquadMembership`) com Validação P3 Contínua e em Tempo Real:**
  - O sistema MUST validar obrigatoriamente, em tempo real e durante todo o processo de adição, alteração de cargo ou reativação de membros de squad, a existência e o status ativo (`is_active=True`) de `ProjectMembership` do usuário no projeto pai da squad, rejeitando imediatamente qualquer operação caso o usuário não seja membro ativo do projeto pai.
  - O sistema MUST garantir a continuidade da Regra de Contenção P3: caso o vínculo do usuário no projeto pai seja inativado (`is_active=False`), o sistema MUST impedir qualquer alteração de cargo ou reativação desse membro na squad até que seu status ativo no projeto pai seja restabelecido.
  - O sistema MUST permitir associar usuários elegíveis a squads, definindo Papel (`role_id` com escopo `SQUAD`) e Cargo (`job_title_id` opcional com nível `SQUAD`).
  - O formulário e o Drawer de Equipe no frontend MUST consultar e verificar em tempo real o status de `ProjectMembership` ativo no projeto pai para filtrar os candidatos elegíveis e sinalizar imediatamente bloqueios na interface.

- **FR-008: Onboarding Rápido com Cadastro Seguro de Usuário (Blind Indexing) e Permissão RBAC:**
  - O sistema MUST disponibilizar um fluxo de cadastro rápido durante a seleção de pessoas no frontend, condicionado à posse da permissão `org.manage` ou privilégio de administrador, impedindo a criação de usuários por operadores não autorizados.
  - O sistema MUST executar validação de unicidade de Username e E-mail em tempo real durante o preenchimento do formulário, rejeitando instantaneamente valores duplicados antes da submissão final à base de dados.
  - O backend MUST persistir o usuário gerando automaticamente os tokens determinísticos de busca segura (`search_tokens`) via `UserProfile.save()` (Blind Indexing com `django-crypto-fields`).
  - Após a criação do usuário, o sistema MUST selecioná-lo automaticamente no combobox de alocação de membros.

- **FR-009: Interface Reativa de Modais e Painel de Gestão de Equipe:**
  - O sistema MUST fornecer interfaces visuais modais sobrepostas diretamente nos cards da hierarquia organizacional para a criação e edição imediata de Organizações, Departamentos, Projetos e Squads, sem redirecionar o usuário para fora do painel de controle.
  - Cada entidade organizacional no painel MUST possuir um controle de ação "Gerenciar Equipe" que abre um painel lateral retrátil (drawer) exibindo a lista de membros ativos daquela entidade, com botões para alocar novos membros, alterar cargos ou desativar vínculos.
  - As interfaces modais MUST validar os dados em tempo real antes da submissão, exibir mensagens de sucesso ou erro imediatas em notificações não bloqueantes e atualizar os dados do painel instantaneamente após cada alteração.

- **FR-010: Controle Proativo de Permissões na Interface (RBAC Frontend):**
  - O sistema MUST validar a autorização de cada ação na interface através de uma função de verificação de permissão (`hasPermission`), que avalia as permissões do usuário logado e retorna estritamente verdadeiro (`true`) ou falso (`false`) para cada operação solicitada em FR-001 a FR-008.
  - Os botões de adição ("Nova Organização", "Novo Departamento", "Novo Projeto", "Nova Squad", "Alocar Membro", "Novo Usuário") e de edição MUST permanecer desabilitados ou ocultos caso o retorno de `hasPermission` seja falso para o escopo correspondente (`org.manage`, `project.manage`, `squad.manage`).
  - Todas as tentativas de mutação MUST ser adicionalmente validadas pelo servidor no backend com retorno HTTP 403 Forbidden caso o usuário não possua os privilégios necessários.

---

## 3. Requisitos Não-Funcionais (Restrições)

- **[NFR-001] Design System Glassmorphism:** Todos os novos componentes de interface (modais, drawers, inputs, selects e botões) MUST aderir estritamente ao tema dark com glassmorphism já implementado em `frontend/src/app/page.tsx` e `globals.css`.
- **[NFR-002] Proteção de Dados e Data Vault (P07 / LGPD):** Dados pessoais identificáveis (PII) inseridos no cadastro de usuários (como `full_name`) NUNCA devem transitar descriptografados para logs do sistema nem expor chaves de criptografia para o navegador.
- **[NFR-003] Validação de Integridade P3 (Inviolabilidade Hierárquica):** Nenhuma transação de banco de dados pode permitir membros em squads sem projeto pai ou em projetos sem organização pai. Toda validação ocorre no nível do modelo do Django (`clean()`) e nos serializers de entrada.
- **[NFR-004] TDD Mandatório (P05):** Todos os novos endpoints de mutação no backend (CRUD de workspaces e memberships) MUST ser cobertos por testes unitários e de integração em `pytest` antes da liberação.
- **[NFR-005] Contratos Dinâmicos OpenAPI 3.0:** Todos os ViewSets e serializers novos MUST conter anotações `@extend_schema` completas via `drf-spectacular`, garantindo atualização automática de tipos TypeScript via `npm run api:generate`.

---

## 4. Histórias de Usuário (User Stories)

- **US1 — Gestão da Estrutura Organizacional:**  
  **Como um** administrador ou gestor de organização,  
  **eu quero** adicionar e editar departamentos, projetos e squads diretamente no painel visual,  
  **para que** a topologia de trabalho reflita fielmente as unidades de negócio e pesquisa em andamento.

- **US2 — Alocação de Membros e Cargos Matriciais:**  
  **Como um** líder de projeto ou squad,  
  **eu quero** alocar pessoas na minha equipe, escolhendo seu papel e cargo específico para aquele escopo,  
  **para que** cada membro tenha as permissões exatas para operar sem acesso indevido a outros projetos.

- **US3 — Admissão Imediata de Novo Colaborador:**  
  **Como um** gestor cadastrando uma nova equipe,  
  **eu quero** criar o registro de um novo colaborador diretamente pelo formulário de membros caso ele ainda não conste no sistema,  
  **para que** eu não precise interromper o fluxo de trabalho nem acessar a interface administrativa crua.

- **US4 — Segurança e Clareza Operacional:**  
  **Como um** membro com permissão apenas de observador ou atendente,  
  **eu quero** visualizar a árvore de trabalho sem poluição de botões de edição inoperantes,  
  **para que** eu tenha clareza do meu papel e não execute ações não autorizadas.

---

## 5. Critérios de Aceite (Acceptance Scenarios)

### SC-001: Criação e Edição de Organização
- **Dado que** um usuário com permissão de plataforma ou `org.manage` está no HUD,
- **Quando** ele clica em "+ Nova Organização", preenche o nome "Hospital Universitário", seleciona o tipo `HEALTHCARE` e confirma,
- **Então** o sistema cria a organização no PostgreSQL, exibe toast de sucesso e adiciona a nova aba no seletor de organizações sem reload de página.

### SC-002: Criação de Departamento com Unicidade de Código
- **Dado que** o departamento com código "TI" já existe na Organização ativa,
- **Quando** o operador tenta criar outro departamento com o mesmo código "TI" na mesma Organização,
- **Então** o sistema rejeita a operação com erro de validação claro ("O código 'TI' já está em uso nesta organização") e preserva os dados no formulário.

### SC-003: Subordinação de Squad e Regra de Contenção (P3)
- **Dado que** um projeto ativo "Saúde Digital" está selecionado,
- **Quando** o operador clica em "+ Squad" dentro do card deste projeto e preenche "App Móvel",
- **Então** a squad é criada com vínculo obrigatório a esse projeto pai e renderizada imediatamente no container de squads.

### SC-004: Alocação de Membro na Organização com Cargo e Papel Válidos
- **Dado que** um usuário "dr.roberto" existe no sistema,
- **Quando** o gestor abre o Drawer de Equipe da Organização, seleciona "dr.roberto", escolhe o papel `admin` e o cargo `Médico(a)`,
- **Então** o vínculo `OrganizationMembership` é persistido com sucesso e listado na equipe da organização.

### SC-005: Rejeição P3 na Alocação e Edição de Membro de Squad sem Vínculo Ativo no Projeto
- **Dado que** a usuária "analista.maria" é membro da Organização, mas NÃO possui vínculo ativo no Projeto "IA Triagem" (ou teve seu vínculo no projeto inativado),
- **Quando** o gestor tenta alocá-la, alterar seu cargo ou reativar seu status na Squad "Modelagem" subordinada ao Projeto "IA Triagem",
- **Então** o sistema valida em tempo real e bloqueia a ação, ocultando-a da listagem no frontend ou retornando erro 400/P3 no backend ("O usuário deve possuir vínculo ativo no projeto pai antes de qualquer alocação ou alteração na squad").

### SC-006: Alocação Válida em Squad após Vínculo no Projeto Pai
- **Dado que** o usuário "pesquisador.joao" já possui vínculo ativo no Projeto "IA Triagem",
- **Quando** o gestor seleciona seu nome no Drawer da Squad "Modelagem", define o papel `squad_member` e cargo `Cientista de Dados`,
- **Então** o vínculo `SquadMembership` é criado com sucesso e exibido com badge no chip da squad.

### SC-007: Onboarding Rápido com Validação em Tempo Real e Blind Indexing
- **Dado que** o gestor precisa alocar uma nova profissional que não existe no banco,
- **Quando** ele clica em "Cadastrar Novo Usuário", preenche username "dra.luciana", email "luciana@example.org" e full_name "Luciana Silva",
- **Então** o formulário valida a unicidade de username e email em tempo real confirmando a disponibilidade antes do envio, o backend cria o usuário e perfil gerando `search_tokens` criptográficos, e o nome "Luciana Silva" é imediatamente selecionado no formulário de alocação.

### SC-008: Bloqueio Visual para Usuários sem Permissão
- **Dado que** um usuário logado possui apenas o papel de visitante ou membro comum sem `org.manage` nem `project.manage`,
- **Quando** ele visualiza o Dashboard HUD,
- **Então** os botões de "+ Adicionar" e "Editar" não são exibidos nos cards ou aparecem desabilitados com tooltip explicativo.

---

## 6. Fora do Escopo (Out of Scope)

- **Exclusão Física em Cascata (Hard Delete):** Exclusões irreversíveis de entidades ou expurgo de dados não fazem parte deste ciclo (apenas desativação lógica `is_active=False` ou cancelamento de status).
- **Interface de Chat Omnichannel ao Vivo:** O card de mensageria continua sendo um indicador de telemetria; telas de chat ao vivo e disparo de webhooks ativos serão tratadas em especificação própria.
- **Upload e Processamento Vetorial de Documentos (RAG):** O envio de arquivos e consulta semântica via pgvector permanece no backend.
- **Gestão de Carteiras e Streaks de Gamificação:** Saldos e recompensas de participantes continuam restritos ao modelo de dados, sem edição manual pela interface de governança.

---

## 7. Suposições Verificadas (Grounding & Fontes)

- **"Django REST Framework & SimpleJWT":** verificado em [Django REST Framework Docs](https://www.django-rest-framework.org/) e instalado localmente no ambiente virtual (`djangorestframework~=3.16.1`, `djangorestframework-simplejwt~=5.3.1`) em 13-10-2026.
- **"DRF Spectacular (OpenAPI 3.0)":** verificado em [drf-spectacular GitHub](https://github.com/tfranzel/drf-spectacular) e ativo em `config/settings/base.py` em 13-10-2026.
- **"Next.js 16 (App Router) & React 19":** verificado no `frontend/package.json` (`next: ^16.1.7`, `react: 19.2.0`) em 13-10-2026.
- **"Tailwind CSS v4 & Lucide Icons":** verificado no `frontend/package.json` (`tailwindcss: ^4`, `lucide-react: ^0.555.0`) em 13-10-2026.
- **"Sonner (Toast Notification)":** verificado no `frontend/package.json` (`sonner: ^2.0.7`) em 13-10-2026.
- **"TanStack React Query v5":** verificado no `frontend/package.json` (`@tanstack/react-query: ^5.90.12`) em 13-10-2026.
- **"Blind Indexing via search_tokens":** verificado na implementação do modelo `UserProfile` em `core/models.py:440-520` em 13-10-2026.
- **"Regra de Contenção P3 & Validação de Escopo":** verificado nos métodos `clean()` e `validate_parent()` de `BaseMembership` em `core/models.py:270-420` em 13-10-2026.
