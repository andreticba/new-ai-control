<!-- research.md | Vitalia SDD v0.6.0 | 09-10-2026 15:35(GMT-04:00) -->
**research.md | AI-Control v0.0.1 | 09-10-2026 15:35(GMT-04:00)**

# Technical Research: Core Foundations

## Decisão: Stack Base (Django & Cryptography)
- **Escolhido**: Django 6.1.x e django-crypto-fields==1.0.1
- **Verificado em**: `ai-control/requirements.txt` em 09-10-2026
- **Justificativa**: Evita a quebra da integração já existente com o Evolution API (Source of Truth). Manter a stack base é crítico para refatoração in loco.
- **Alternativas**:
  - Django 5.x / django-cryptography: rejeitado porque causaria regressão no ambiente.

## Decisão: Mecanismo de Imutabilidade do AuditLog
- **Escolhido**: SQL Trigger no PostgreSQL (RAISE EXCEPTION para UPDATE/DELETE)
- **Verificado em**: https://www.postgresql.org/docs/current/plpgsql-trigger.html em 09-10-2026
- **Justificativa**: Garante imutabilidade na camada de banco de dados, protegendo contra operações RAW e bypasses do ORM do Django.
- **Alternativas**:
  - Sobrescrever `save()` e `delete()` no modelo: rejeitado porque não bloqueia `QuerySet.update()` ou `QuerySet.delete()`.

## Decisão: Isolamento do Worker Celery
- **Escolhido**: Redis DB Dedicado (DB 2) para o Celery Worker
- **Verificado em**: Prática padrão arquitetural de infraestrutura; `CELERY_OMNICHANNEL_REDIS_URL` adicionado ao `.env`.
- **Justificativa**: Previne que picos de chamadas RAG no Omnichannel causem enfileiramento cruzado com outras filas críticas do sistema.
- **Alternativas**:
  - Mesmo DB (DB 0) com queues distintas: rejeitado porque não provê isolamento físico de memória no Redis.

## Decisão: Relacionamento Cross-Domain
- **Escolhido**: Soft Foreign Keys (`models.UUIDField` com `db_index=True`)
- **Verificado em**: Padrão de Microservices e Domain-Driven Design (Bounded Contexts).
- **Justificativa**: Permite o particionamento futuro do banco de dados (Sharding/Microservices) sem a dor de cabeça de constraints forçadas entre schemas distintos.
- **Alternativas**:
  - `models.ForeignKey`: rejeitado porque acopla fortemente os apps a nível de schema.
