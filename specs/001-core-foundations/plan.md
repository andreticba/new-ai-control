<!-- plan.md | Vitalia SDD v0.6.0 | 09-10-2026 15:35(GMT-04:00) -->
**plan.md | AI-Control v0.0.1 | 09-10-2026 15:35(GMT-04:00)**

# Implementation Plan: Core Foundations

**Branch**: `001-core-foundations` | **Date**: 09-10-2026 | **Spec**: [spec.md](spec.md)

## Summary
Refatoração in loco do monolito `core` para separar os apps `omnichannel`, injetar regras legadas avançadas de IA e Tenant, utilizando Soft FKs e reconstrução limpa de banco (idempotência).

## Technical Context
**Language/Version**: Python 3.14, Django 6.1.x
**Primary Dependencies**: django-crypto-fields==1.0.1, celery, psycopg2
**Storage**: PostgreSQL (ai-control_db), Redis (DB 0 para Cache, DB 2 para Worker Omnichannel)
**Testing**: pytest
**Target Platform**: Server (Backend)
**Project Type**: web-app (API)
**Performance Goals**: Baixa latência para metadados via GinIndex.
**Constraints**: Zero models.ForeignKey cruzando Bounded Contexts. Uso exclusivo de UUIDField.

## Constitution Check
- **Veredicto**: PASS (Aprovado pelo Juiz SDD)
- **Notas**: Nenhuma violação detectada. O modelo local validou as decisões técnicas e operacionais.

## Dependências de Contexto (Grounding)
Para compreender as regras de negócio intrínsecas ao monolito atual, o Agente executor da fase de Implementação DEVERÁ consultar obrigatoriamente:
1. `core/models.py`: Para compreender o esquema do banco atual e do 4-Tier RBAC.
2. Diretório `docs/`: Manuais e Arc42 que embasam as regras operacionais da IA legada e ditam o critério de sucesso absoluto da arquitetura final.
3. Arquivo `AI-Control 08-11-2025-21-25.md`: Este arquivo contém o código e a inteligência de negócios original superior (ex: lógica de RAG profundo, travamento de contexto). É a bússola para não regredirmos.
4. Arquivo `alinhamento.md`: Mapeia de onde extrair cada parte do sistema e crava a restrição contra alucinações (o código não pode divergir do Arc42).

## Technical Decisions
Ver [research.md](research.md) (Abordagem Híbrida do AuditLog, Soft FKs, DB Dedicado Celery, Stack).

## Project Structure
### Documentation (this feature)
- `specs/001-core-foundations/spec.md`
- `specs/001-core-foundations/plan.md`
- `specs/001-core-foundations/data-model.md`
- `specs/001-core-foundations/research.md`

### Source Code
- `core/models.py`
- `core/signals.py` (criação via post_save)
- `core/migrations/`
- `omnichannel/apps.py`
- `omnichannel/models.py`
- `omnichannel/migrations/`

## Phase Overview

### Phase 1: Setup & TDD Inicial
- Criar a app `omnichannel` via `python manage.py startapp omnichannel` (se não existir). Adicionar em `INSTALLED_APPS` (`config/settings/base.py`).
- Escrever testes unitários em `core/tests/` e `omnichannel/tests/` garantindo falhas (Red Phase) para UniqueConstraint, Signals e Soft FKs.

### Phase 2: Foundational (Models & DB Schema)
**Gate OBRIGATÓRIO**: O Executor DEVE carregar o arquivo `core/models.py` na memória (Source of Truth) e analisar a estrutura atual antes de agir.
- `core.Organization`: Injetar a constraint de Tenant Interno (`is_internal`).
- `core.AuditLog`: Injetar o `GinIndex`.
- App `omnichannel`: Recortar **fisicamente** os modelos `Conversation`, `Message`, `Contact` e `OmnichannelPreferences` (se existirem) de `core/models.py` e colar em `omnichannel/models.py`. Trocar **todos** os `models.ForeignKey` ou relacionamentos diretos que apontem para o `core` para Soft FKs (`models.UUIDField(db_index=True)`).
- `core/signals.py`: Criar o `post_save` da `Organization` para instanciar a `OmnichannelPreferences` apontando via Soft FK.

### Phase 3: DB Enforcement (Triggers)
- Criar a migração `RunSQL` no `core` adicionando a function e trigger que lançam EXCEPTION para comandos `UPDATE` e `DELETE` na tabela `core_auditlog`. (O SQL deve ser nativo Postgres via `migrations.RunSQL`, com reversão).

### Phase 4: Migration Clean & Seed
- **ATENÇÃO CRÍTICA**: Antes de apagar as migrações atuais, **copie/faça backup** da lógica de seed (`INTERNAL_USERS_DATA`, `create_internal_data` e `RunPython`) presente na `core/migrations/0001_initial.py` atual. O arquivo original não pode ser perdido.
- Deletar fisicamente os arquivos de migração existentes.
- Executar `makemigrations core omnichannel` gerando o `0001_initial.py` definitivo (Zero-State Greenfield).
- Injetar o código de backup do Seed (`RunPython`) diretamente no final das `operations` do novo `0001_initial.py` gerado.
