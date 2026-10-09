# Tasks: Core Foundations (Refatoração de Domínios)

**Spec**: [specs/001-core-foundations/spec.md](specs/001-core-foundations/spec.md) | **Plan**: [specs/001-core-foundations/plan.md](specs/001-core-foundations/plan.md)
**Gerado em**: 2026-10-09

---

## MVP Scope

> Implementar **Phase 1 + Phase 2 + Phase 3 (US2) + Phase 4 (US1)** entrega produto funcionando com a arquitetura exigida.
> Phase 5 é o incremento operacional para SRE.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e grounding ANTES de qualquer implementação. Sem label de US.*

- [X] T000-A Ativar venv: `source .venv/bin/activate` (ou equivalente do projeto)
- [X] T000-B Verificar versão Python do venv (não do sistema): `python --version`
- [X] T000-C Verificar deps instaladas vs requirements.txt: `pip list --outdated` ou equivalente
- [X] T000-D Verificar dependências essenciais: confirmar se `django-crypto-fields==1.0.1`, `celery` e `psycopg2` estão no ambiente.
- [X] T000-E Carregar na memória as dependências de grounding cruciais: `core/models.py`, manuais da pasta `docs/`, `AI-Control 08-11-2025-21-25.md` e `alinhamento.md`.

---

## Phase 1: Setup

- [X] T001 [P] Criar a app `omnichannel` via comando `python manage.py startapp omnichannel` e registrar em `INSTALLED_APPS` no arquivo `config/settings/base.py`.
- [X] T002 [P] Configurar estrutura base de testes em `core/tests/` e `omnichannel/tests/`, escrevendo testes falhos que validarão UniqueConstraint, Signals e Soft FKs no futuro.

---

## Phase 2: Foundational

- [X] T003 Injetar a constraint `UniqueConstraint(is_internal=True)` no model `Organization` dentro de `core/models.py`.
- [X] T004 Injetar o `GinIndex` na tabela do `AuditLog` dentro de `core/models.py`.
- [X] T005 Recortar fisicamente os modelos `Conversation`, `Message`, `Contact` e `OmnichannelPreferences` (se existirem) de `core/models.py` e colar em `omnichannel/models.py`. Caso não existam no core atual, extraí-los do legado `AI-Control 08-11-2025-21-25.md`.
- [X] T006 Substituir todas as chaves relacionais diretas (`models.ForeignKey`, etc.) para o `core` por Soft FKs `models.UUIDField(db_index=True)` no model `omnichannel/models.py`.
- [X] T007 Adicionar os campos lógicos de IA da especificação (`context_locked`, `locked_at`, `current_intent`, `consecutive_rag_failures`) no modelo `Conversation` em `omnichannel/models.py`.
- [X] T008 Implementar o signal `post_save` no model `Organization` para instanciar remotamente a `OmnichannelPreferences` no arquivo `core/signals.py`.

---

## Phase 3: DB Enforcement (Triggers) — User Story 2

**Story Goal**: Auditoria de compliance (LGPD) garantindo logs imutáveis a nível de banco de dados.
**Independent Test**: Executar uma SQL crua de DELETE em `core_auditlog` e observar falha do PostgreSQL.
**Referência**: FR-006

- [ ] T009 [US2] Gerar migração vazia no core via `python manage.py makemigrations core --empty`.
- [ ] T010 [US2] Editar a migração gerada em `core/migrations/` e injetar `migrations.RunSQL` com a trigger e function nativas bloqueando `UPDATE` e `DELETE` em `core_auditlog`, garantindo o código de reversão (DROP TRIGGER/DROP FUNCTION).

---

## Phase 4: Migration Clean & Seed — User Story 1

**Story Goal**: Administrador da plataforma garante a organização interna única sem misturar dados de tenant, partindo de um banco resetado idêntico à documentação.
**Independent Test**: Migrações passam do zero e injetam `INTERNAL_USERS_DATA` no banco com sucesso.
**Referência**: FR-001, FR-002, FR-008

- [ ] T011 [US1] FAZER BACKUP: Copiar a lógica da função `create_internal_data` e `INTERNAL_USERS_DATA` e a cláusula `RunPython` que existem no final de `core/migrations/0001_initial.py` para um arquivo de texto temporário seguro.
- [ ] T012 [US1] Deletar fisicamente as pastas antigas de migrações ou limpar arquivos não essenciais de `core/migrations/` e `omnichannel/migrations/` (deletar os `.py`, mantendo `__init__.py`).
- [ ] T013 [US1] Rodar comando `python manage.py makemigrations core omnichannel` para gerar a migração definitiva Greenfield (`0001_initial.py`).
- [ ] T014 [US1] RESTAURAR BACKUP: Injetar a lógica e o `RunPython` do seed copiados anteriormente no final da array `operations` do novo `core/migrations/0001_initial.py`.
- [ ] T015 [US1] Realizar o Reset ou Migrate inicial (via `python manage.py migrate`) testando a idempotência.

---

## Phase 5: Redis Isolation (SRE) — User Story 3

**Story Goal**: Engenheiro de SRE separa workers para que picos de fila não afetem o RAG.
**Independent Test**: Instância Celery sobe apontada no DB especificado pelo env.
**Referência**: FR-007

- [ ] T016 [P] [US3] Atualizar `config/settings/base.py` ou `config/celery.py` (conforme padrão do projeto) para ler a variável `CELERY_OMNICHANNEL_REDIS_URL` para gerenciar a fila isolada.

---

## Dependency Graph

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 (US2) → Phase 4 (US1) → Phase 5 (US3)
```

## Parallel Execution

Tasks marcadas [P] dentro da mesma fase podem ser executadas simultaneamente.
