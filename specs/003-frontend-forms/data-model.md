<!-- data-model.md | AI-Control v0.0.1 | 13-10-2026 18:05(GMT-04:00) -->
# Data Model: Formulários de Governança 4-Tier e Gestão de Membros

**Feature:** `specs/003-frontend-forms`  
**Data:** 13-10-2026  
**Status:** Consolidado para Planejamento  

---

## 1. Visão Geral da Topologia de Dados 4-Tier

O modelo de dados do AI-Control estrutura a governança corporativa em 4 camadas rígidas com contenção hierárquica (**Regra P3**):

```
+-----------------------------------------------------------+
|                      Organization                         |
|  - id, name, slug, org_type, is_active, is_internal       |
+-----------------------------------------------------------+
       |                                      |
       | (1:N)                                | (1:N)
       v                                      v
+-----------------------+              +------------------------------------+
|      Department       |              |              Project               |
|  - id, name, code,    |              |  - id, name, slug, project_type,   |
|    description        |              |    status, organization_id         |
+-----------------------+              +------------------------------------+
                                                      |
                                                      | (1:N)
                                                      v
                                       +------------------------------------+
                                       |               Squad                |
                                       |  - id, name, slug, mission,        |
                                       |    is_active, project_id           |
                                       +------------------------------------+
```

---

## 2. Entidades de Governança Estrutural

### 2.1 Entity: `Organization`
- **Tabela:** `core_organization`
- **Campos:**
  - `id`: UUID — Primary Key, default `uuid.uuid4`
  - `name`: VARCHAR(255) — Obrigatório
  - `slug`: SLUG(255) — Único, indexado
  - `org_type`: VARCHAR(50) — Choices: `HEALTHCARE`, `UNIVERSITY`, `COMPANY`, `NGO`, `GOVERNMENT`, `INDIVIDUAL`, `OTHER`
  - `is_active`: BOOLEAN — Default `True`
  - `is_internal`: BOOLEAN — Default `False` (define o tenant matriz do AI-Control)
  - `created_at`: TIMESTAMP — Auto now add
  - `updated_at`: TIMESTAMP — Auto now
- **Constraints:**
  - `unique(slug)`
  - `unique(name)`

### 2.2 Entity: `Department`
- **Tabela:** `core_department`
- **Campos:**
  - `id`: UUID — Primary Key, default `uuid.uuid4`
  - `organization_id`: UUID — FK `Organization(id)`, on_delete=CASCADE
  - `name`: VARCHAR(255) — Obrigatório
  - `code`: VARCHAR(50) — Código departamental curto (ex: "FIN", "DCOMP", "TI")
  - `description`: TEXT — Opcional
- **Constraints:**
  - `unique(organization_id, code)`

### 2.3 Entity: `Project`
- **Tabela:** `core_project`
- **Campos:**
  - `id`: UUID — Primary Key, default `uuid.uuid4`
  - `organization_id`: UUID — FK `Organization(id)`, on_delete=CASCADE
  - `name`: VARCHAR(255) — Obrigatório
  - `slug`: SLUG(255) — Obrigatório
  - `project_type`: VARCHAR(50) — Choices: `RESEARCH`, `DEVELOPMENT`, `OPERATIONAL`, `CONSULTING`, `OTHER`
  - `status`: VARCHAR(50) — Choices: `PLANNING`, `ACTIVE`, `PAUSED`, `COMPLETED`, `CANCELLED`, default `ACTIVE`
  - `description`: TEXT — Opcional
- **Constraints:**
  - `unique(organization_id, slug)`

### 2.4 Entity: `Squad`
- **Tabela:** `core_squad`
- **Campos:**
  - `id`: UUID — Primary Key, default `uuid.uuid4`
  - `project_id`: UUID — FK `Project(id)`, on_delete=CASCADE (Inviolabilidade P3: squad SEMPRE subordinada a um projeto)
  - `name`: VARCHAR(255) — Obrigatório
  - `slug`: SLUG(255) — Obrigatório
  - `mission`: TEXT — Opcional
  - `is_active`: BOOLEAN — Default `True`
- **Constraints:**
  - `unique(project_id, slug)`

---

## 3. Entidades de Gestão de Membros (Memberships)

A alocação de pessoas baseia-se em `BaseMembership` e heranças especializadas:

### 3.1 Entity: `OrganizationMembership`
- **Tabela:** `core_organizationmembership`
- **Campos:**
  - `id`: UUID — Primary Key
  - `user_id`: INT/UUID — FK `auth_user(id)`, on_delete=CASCADE
  - `organization_id`: UUID — FK `Organization(id)`, on_delete=CASCADE
  - `department_id`: UUID — FK `Department(id)`, NULL=True, on_delete=SET_NULL
  - `role_id`: UUID — FK `Role(id)`, escopo restrito a `ORGANIZATION`
  - `job_title_id`: UUID — FK `JobTitle(id)`, NULL=True, nível restrito a `ORGANIZATION`
  - `is_active`: BOOLEAN — Default `True`
- **Constraints:**
  - `unique(user_id, organization_id)` para vínculos ativos

### 3.2 Entity: `ProjectMembership`
- **Tabela:** `core_projectmembership`
- **Campos:**
  - `id`: UUID — Primary Key
  - `user_id`: INT/UUID — FK `auth_user(id)`, on_delete=CASCADE
  - `project_id`: UUID — FK `Project(id)`, on_delete=CASCADE
  - `role_id`: UUID — FK `Role(id)`, escopo restrito a `PROJECT`
  - `job_title_id`: UUID — FK `JobTitle(id)`, NULL=True, nível restrito a `PROJECT`
  - `is_external`: BOOLEAN — Default `False`
  - `is_active`: BOOLEAN — Default `True`
- **Regra de Contenção P3:**
  - Validação estrita em `clean()` e serializers: O usuário DEVE possuir `OrganizationMembership` ativa na organização dona do projeto (ou `org_guest` se `is_external=True`).

### 3.3 Entity: `SquadMembership`
- **Tabela:** `core_squadmembership`
- **Campos:**
  - `id`: UUID — Primary Key
  - `user_id`: INT/UUID — FK `auth_user(id)`, on_delete=CASCADE
  - `squad_id`: UUID — FK `Squad(id)`, on_delete=CASCADE
  - `role_id`: UUID — FK `Role(id)`, escopo restrito a `SQUAD`
  - `job_title_id`: UUID — FK `JobTitle(id)`, NULL=True, nível restrito a `SQUAD`
  - `is_active`: BOOLEAN — Default `True`
- **Regra de Contenção P3:**
  - Validação contínua em tempo real: O usuário DEVE possuir `ProjectMembership` ativa no projeto pai da squad antes de ser alocado ou ter seu cargo alterado.

---

## 4. Entity de Onboarding: `UserProfile` com Blind Indexing

- **Tabela:** `core_userprofile`
- **Campos Relevantes:**
  - `id`: UUID — Primary Key
  - `user_id`: FK `auth_user`
  - `full_name`: EncryptedCharField — Nome criptografado
  - `search_tokens`: JSONField / ArrayField — Tokens determinísticos para busca confidencial (Blind Indexing)
  - `created_at`: TIMESTAMP
