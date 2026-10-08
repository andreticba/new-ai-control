<!-- evidence-inventory.md | Vitalia SDD v0.6.0 | 07-10-2026 23:45(GMT-04:00) -->
# Evidence Inventory

Commit de referência: `686d444`

## Mapeamento do Domínio (`core/models.py`)

| Conceito | Arquivo | Símbolo | Linhas | Estado | Testes Relacionados |
|---|---|---|---|---|---|
| Organization | `core/models.py` | `Organization` | 87-121 | ✅ | |
| Department | `core/models.py` | `Department` | 124-157 | ✅ | |
| Project | `core/models.py` | `Project` | 200-258 | ✅ | |
| Squad | `core/models.py` | `Squad` | 261-288 | ✅ | |
| JobTitle | `core/models.py` | `JobTitle` | 160-197 | ✅ | |
| Role | `core/models.py` | `Role` | 48-84 | ✅ | |
| Permission | `core/models.py` | `Permission` | 32-45 | ✅ | |
| OrganizationMembership | `core/models.py` | `OrganizationMembership` | 342-368 | ✅ | |
| ProjectMembership | `core/models.py` | `ProjectMembership` | 371-408 | ✅ | |
| SquadMembership | `core/models.py` | `SquadMembership` | 411-439 | ✅ | |
| UserProfile.platform_role | `core/models.py` | `UserProfile` | 444-531 | ✅ | |
| DataAccessGrant | `core/models.py` | `DataAccessGrant` | 644-690 | ✅ | |
| Document.Visibility | `core/models.py` | `Document` | 741-786 | ✅ | |
| DocumentChunk | `core/models.py` | `DocumentChunk` | 789-822 | ✅ | |
| Contact / Phone / OrgMem | `core/models.py` | `Contact`, `ContactPhoneNumber`, `ContactOrganizationMembership` | 826-898 | ✅ | |
| Conversation / Message | `core/models.py` | `Conversation`, `Message` | 900-960 | ✅ | |
| AuditLog | `core/models.py` | `AuditLog` | 693-738 | ✅ | |

## Regras e Constraints (T008)

### Organization
- `unique_together`: N/A
- `on_delete`: N/A
- Comportamentos: Tenant principal (ACADEMIC, CLINIC, etc).

### Department
- `constraints`: `UniqueConstraint(fields=['organization', 'slug'])`
- `on_delete`: `parent` (SET_NULL), `organization` (CASCADE)
- `clean`: Não pode ser pai de si mesmo; o pai precisa ser da mesma organização.

### Project
- `constraints`: `UniqueConstraint(fields=['organization', 'slug'])`, `CheckConstraint(end_date >= start_date)`
- `on_delete`: `organization` (CASCADE), `owner_department` (SET_NULL)
- `clean`: `owner_department` precisa ser da mesma organização.

### Squad
- `constraints`: `UniqueConstraint(fields=['project', 'slug'])`
- `on_delete`: `project` (CASCADE)

### BaseMembership & Subclasses
- **BaseMembership**:
  - `clean`: `role.scope` precisa ser o `SCOPE` da subclasse; `job_title.level` e `organization` são checados. Chama `validate_parent()` se ativo.
  - `save`: Chama `clean()`, ajusta `left_at` baseado em `is_active`.
- **OrganizationMembership**:
  - `constraints`: `UniqueConstraint(fields=['user', 'organization'])`
  - `validate_parent`: Departamento tem que ser da mesma org.
- **ProjectMembership**:
  - `constraints`: `UniqueConstraint(fields=['user', 'project'])`
  - `validate_parent`: Exige membro ativo na organização. Se externo, o papel na organização deve ser `org_guest`.
- **SquadMembership**:
  - `constraints`: `UniqueConstraint(fields=['user', 'squad'])`
  - `validate_parent`: Exige membro ativo no projeto.

## Comportamentos Comprovados por Testes (`test_rbac.py`)
- **P3 Membership Hierarchy:**
  - Criação de `OrganizationMembership` com papel válido (`ORGANIZATION`) funciona.
  - Criar `ProjectMembership` **sem** ter `OrganizationMembership` ativa na mesma org lança `ValidationError`.
  - Criar `SquadMembership` **sem** ter `ProjectMembership` ativa no projeto lança `ValidationError`.
  - Membership em todos os 3 níveis funciona quando a cadeia é seguida.
- **Isolamento de Escopo:**
  - Atribuir um papel de `PROJECT` (ex: `project_lead`) numa `OrganizationMembership` lança `ValidationError`.
- **Membro Externo:**
  - `ProjectMembership(is_external=True)` exige que o `OrganizationMembership` tenha o papel `org_guest`. Falha se o papel na org for `org_member`.
- **Middleware RBAC Gateway:**
  - Um usuário com papel `org_admin` tem acesso à rota `/api/v1/gateway/` via `rbac_middleware`.
  - Um usuário com papel `org_member` tem o acesso **negado** (403) e gera um registro no `AuditLog` (`FAILED_LOGIN`).

## Personagens e Dados do Seed (`seed_demo.py`)
O seed possui 2 perfis principais (Academic e Corporate).

### Perfil ACADEMIC ("Universidade Federal Demo")
- **Organização**: `ufdemo`
- **Departamentos**: PROPESQ, PROEC, DCOMP, DENF, FIN, SGP.
- **Projetos e Squads**:
  - `saude-digital` (Projeto Extensão) -> Squads: `app-movel`, `campo-coleta`
  - `ia-triagem` (Projeto Pesquisa) -> Squads: `modelagem`, `dados-clinicos`
- **Personagens (Usuários Mock)**:
  - `prof.ana`: org_member (DCOMP). Coordenadora em `saude-digital` e Tech Lead no squad `app-movel`. Pesquisadora colaboradora em `ia-triagem`.
  - `prof.carlos`: org_manager (PROPESQ). Coordenador geral do projeto `ia-triagem`.
  - `prof.lucia`: org_member (DENF). Vice-coordenadora em `saude-digital` e Pesquisadora de Campo no squad `campo-coleta`.
  - `aluno.joao`: org_member (DCOMP). Desenvolvedor no squad `app-movel` do projeto `saude-digital`.
  - `aluna.maria`: org_member (DCOMP). Analista de Dados no squad `modelagem` do projeto `ia-triagem`.
  - `pesq.externo`: org_guest (Parceiro Externo). Somente leitura (`squad_viewer`) no squad `dados-clinicos` de `ia-triagem`.
  - `tae.paulo`: org_member (Técnico Administrativo, FIN). Sem vinculação a projetos.

### Perfil CORPORATE ("Empresa Demo Ltda")
- **Organização**: `empresa-demo`
- **Departamentos**: FIN, RH, COM, ATD, TI.
- **Projeto e Squads**:
  - `implantacao-crm` (Projeto Corporativo TI) -> Squads: `integracao`, `conteudo-bot`
- **Personagens (Usuários Mock)**:
  - `gerente.ti`: org_manager (TI). Líder do projeto `implantacao-crm` e líder do squad `integracao`.
  - `dev.rafa`: org_member (TI). Desenvolvedor no squad `integracao`.
  - `supervisor.bia`: org_supervisor (ATD). Product Owner no projeto e líder do squad `conteudo-bot`.
  - `atendente.leo`: org_agent (ATD). Apenas membro da org.
  - `analista.rh`: org_member (RH). Apenas membro da org.
  - `diretora.fin`: org_admin (FIN). Sponsor (viewer) do projeto `implantacao-crm`.

## Signals (T010)
- **Achado**: Não existem signals reais implementados no repositório. O arquivo `core/apps.py` tenta importar `core.signals` no método `ready()`, mas o arquivo não existe e nenhum uso de `@receiver` ou `models.signals` foi encontrado nos apps.
- **Status de Fidelidade**: 🧭 Design de Referência. O módulo 05 sobre auditoria e sanitização deve deixar claro que os signals são apenas um design projetado.
## Pipeline WhatsApp (T011)

### Fluxo Ponta a Ponta:
1. **Webhook Recebido (`core/api/v1/views/webhook_whatsapp.py`)**:
   - `WebhookGatewayView` recebe requisições (POST) da Evolution API.
   - Valida autenticação (apikey).
   - Ignora silenciosamente `chats.set` e `chats.update` (O(1)).
   - Roteamento atômico enviando o payload validado ao Celery: `process_whatsapp_webhook_task.delay(event_item)`.
2. **Fila do Celery (`core/tasks/whatsapp_tasks.py`)**:
   - `process_whatsapp_webhook_task` extrai o slug da organização (`ai_control_{org_slug}`) a partir do nome da instância. Resolve isolamento de multitenancy.
   - Instancia o `WhatsAppService` e repassa o processamento.
3. **Serviço Core (`core/services/whatsapp_service.py`)**:
   - `process_message_upsert` é chamado via Adapter `EvolutionWebhookAdapter.parse_messages`.
   - Se a mensagem não é "from me":
     - Garante a `Organization` usando o slug recebido.
     - Busca ou cria `ContactPhoneNumber` e `Contact` associado.
     - Busca ou cria `Conversation` ativa para a organização e contato.
     - Registra a `Message`.
     - Transmite os dados do evento para os Websockets via `django-channels` (com pii "mascarado" via `_mask_pii` para o log).
     - Aciona a delegação para a IA via task assíncrona: `AIIngestionDelegator.delay(payload)`.
     - Envia sinal de "digitando" para feedback visual com delay de 5s: `send_typing_signal.apply_async`.
4. **Camada de IA**:
   - Atualmente `AIIngestionDelegator` (em `core/tasks/whatsapp_tasks.py`) está implementada apenas como um `pass` (Design de Referência).
5. **Gateway (`core/services/evolution_gateway.py`)**:
   - Serviço responsável pela comunicação HTTP direta de saída com o provedor Evolution API (criação de instância, definição de webhooks de retorno, consulta de status e envio de mensagens: `send_text_message`).

### Influência do RBAC / SQUAD no Fluxo:
- **Organização**: A organização governa de quem a mensagem é processada. O isolamento começa do nome da Instância no provedor (via Gateway) até o registro da Conversa em Banco.
- **Squad**: Atualmente, a pipeline **não sofre influência do Squad**. Mensagens de WhatsApp são atreladas diretamente a `Conversation`, que se atrelam a uma `Organization`. A granularidade em nível de Projeto e Squad é **apenas em interface e relatórios** (não está bloqueando/direcionando as trocas de mensagens na camada base). O roteamento para o humano baseado no Squad ainda é um "Design de Referência".

## Comparativo Antes/Depois (T012)
*Baseado no commit `bb10c3b` vs `HEAD` (`686d444`)*

### 1. `core/models.py`
- **Antes (`bb10c3b`)**: 559 linhas. RBAC era linear e baseado em títulos estáticos (`SystemRole`, `JobTitle`) que herdavam de `Group` do Django. Não havia conceito de isolamento de tenant/organização e a permissão era fixada no perfil do usuário de forma global (ex: Admin Global, Pesquisador).
- **Depois (`HEAD`)**: 960 linhas. Substituição dos Grupos do Django pelo `BaseMembership` polimórfico (Escopos: Organization, Project, Squad). Os papéis (`Role`) não dependem do cargo (`JobTitle`) e podem ser aplicados de forma matricial (um usuário pode ser Coordenador no Projeto A e Observador no Projeto B).

### 2. `core/middleware.py`
- **Antes**: Limitado a injetar o profile no Request ou não existia bloqueio robusto por domínio.
- **Depois**: Introdução do `rbac_middleware` que intercepta requisições ao `/api/v1/gateway/` exigindo a permissão `org.manage_whatsapp` e emitindo `FAILED_LOGIN` no `AuditLog` em caso de falha.

### 3. `core/management/commands/seed_*`
- **Antes**: Arquivos separados (`seed_roles.py`, `seed_permissions.py`) que populavam dados fixos (ex: `Paciente`, `Profissional`). O `seed_demo.py` original simulava dados globais.
- **Depois**: Seeds granulares foram migrados para data migrations. O novo `seed_demo.py` cria árvores completas simulando multitenancy complexo (Perfil Acadêmico "Universidade Federal Demo" e Corporativo "Empresa Demo Ltda"), comprovando o comportamento de Membership e isolamento entre Orgs/Projetos.

## Lista de Candidatos a Post-Mortem (T013)
*Baseado nas falhas e decisões do `AI_AGENT_CONVERSATION.md`*

1. **Falha de Acoplamento RBAC (Frontend Hardcoded)**
   - **Evidência**: `AI_AGENT_CONVERSATION.md:L1871-L1881` (`if roles.includes('Profissional de Saúde')`)
   - **Contexto**: O sistema antigo usava a Opção A, misturando título profissional com nível de acesso. Isso quebrava o front-end ao tentar escalar para novos cargos (ex: UFMT).
   - **Decisão Final**: Migrar para a Opção B (Separação Limpa), onde Role é abstrato (ex: `MANAGER`) e JobTitle é textual.

2. **Limite Físico de Banco de Dados (Post-Mortem: O problema das 4096 dimensões)**
   - **Evidência**: `AI_AGENT_CONVERSATION.md:L2082`
   - **Contexto**: Uso de embedding de 4096 dimensões estourava o limite do índice HNSW do pgvector (que suporta com eficiência até 2000 dimensões para HNSW puro/ivfflat).
   - **Decisão Final**: Trocar para embeddings menores (como Nomic 768d - `VectorField(dimensions=768)` no `core/models.py`).

3. **Arquitetura de Dados Monolítica vs Microsserviços (Vertical de Saúde vs Agnóstico)**
   - **Evidência**: `AI_AGENT_CONVERSATION.md:L1633-L1662` (ADR-002)
   - **Contexto**: O sistema legado misturava seeds clínicos/nutricionais pesados no banco transacional de orquestração de IA.
   - **Decisão Final**: Manter o banco do `ai-control` ágil e leve (Gateway Agnóstico), delegando metadados de saúde pesados para outro serviço ou recuperados via RAG, não em foreign keys autoritativas rígidas no core.

4. **Isolamento de Segurança em Ambientes Múltiplos (O problema do auth.Group)**
   - **Evidência**: `AI_AGENT_CONVERSATION.md:L1830-L1832`
   - **Contexto**: Uso de Django `auth.Group` causava permissões globais não intencionais, quebrando a segurança de multi-tenancy (um coordenador de uma org virava coordenador de outra se tivesse no mesmo grupo).
   - **Decisão Final**: Eliminação do `auth.Group` a favor do `BaseMembership` isolando poder por escopo (Organização, Projeto, Squad).

## Cobertura Automatizada (T015)
- **Status do Baseline**: Executado `pytest core/tests` em 07-10-2026 com sucesso (20 passed). O arquivo `tests/core/test_evolution_events_task.py` fora do app `core` falha por depender de módulo inexistente (legado não migrado).
- **Comportamentos Cobertos**:
  - Restrições de Associação (`MembershipIntegrity`): Impede vincular num nível sem vínculo no nível pai.
  - Rejeição de Escopos Incorretos (`wrong_scope_role_rejected`).
  - Restrição para Convidados (`external_member_needs_org_guest`).
  - Proteção de Rota (RBAC Middleware): Impede que membros não administrativos acessem `/api/v1/gateway/` e gera falha no `AuditLog`.
