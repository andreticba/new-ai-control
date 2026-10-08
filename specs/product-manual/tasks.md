<!-- tasks.md | Vitalia SDD v0.6.0 | 07-10-2026 22:55(GMT-04:00) -->
# Tasks: Manual de Produto e Histórico Arquitetural

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Research**: [research.md](./research.md)
**Gerado em**: 07-10-2026

> **Natureza da feature:** documentação (docs-as-code). Nenhum código de produção, teste de produção ou esquema de banco é alterado.
> **Equivalente de TDD (P05):** o verificador `check_manuals.py` é escrito **antes** do conteúdo (Red: falha por falta de arquivos) e o conteúdo é escrito até ele passar (Green). Todo exemplo de código/SQL só é publicado após ser **executado** no laboratório.
> **Rótulos de fidelidade obrigatórios em todo conteúdo técnico:** ✅ Implementado · 🟡 Parcial · 🧭 Design de Referência (não implementado).

---

## MVP Scope

> Implementar **Phase 0 + 1 + 2 + 3 (US1) + 4 (US2) + 5 (US3)** entrega o ecossistema útil ao time de engenharia
> (P1: executivos, devs novos e cultura de falhas). **Phase 6 (US4, acadêmico)** e **Phase 7 (US5, mantenabilidade avançada)** são incrementos (P2).
> Mínimo absoluto demonstrável: Phases 0–2 + US1 + o módulo `02-engineering/02_resolucao_de_permissoes.md` + `PM-001`.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e grounding ANTES de qualquer escrita. Sem label de US.*

- [X] T000-A Ativar venv do projeto: `source /home/andre/projetos/assistidos/ai-control/.venv/bin/activate`
- [X] T000-B Verificar versão Python do venv (não do sistema): `python --version` (esperado 3.14.x, conforme `.venv/lib/python3.14`)
- [X] T000-C Verificar deps instaladas vs `requirements.txt`: `pip list` comparado a `requirements.txt` (Django 6.1.*, pgvector 0.5.0)
- [X] T000-D Reconfirmar em pypi.org as versões de `Django` (6.1.2 verificado em 07-10-2026) e `pgvector`, registrando o resultado em `specs/product-manual/research.md` (resolver o `[NEEDS VERIFICATION]` de F-06 ou deixá-lo explicitamente aceito)
- [X] T000-E Verificar conflitos de compatibilidade entre libs: `pip check`
- [X] T000-F Confirmar serviços do ambiente para os laboratórios: PostgreSQL com extensão `vector` ativa (`psql -c "\dx vector"` ou equivalente via `docker-compose.yml`) e `python manage.py check`

---

## Phase 1: Setup

*Inicialização da estrutura e do verificador (Red). Sem label de US.*

- [X] T001 Criar a árvore de diretórios `docs/manuals/{01-product,02-engineering/labs,03-history/postmortems,04-academic,_templates,_verification}` conforme `plan.md`
- [X] T002 Registrar o commit de referência: `git rev-parse --short HEAD` em `specs/product-manual/evidence-inventory.md` (cabeçalho) para uso em todos os cabeçalhos de módulo (NFR-005)
- [X] T003 [P] Criar `docs/manuals/_templates/module_header.md` (público-alvo, pré-requisitos, tempo de leitura, data, commit de referência, legenda ✅/🟡/🧭) — FR-004, NFR-005
- [X] T004 [P] Criar `docs/manuals/_templates/postmortem_template.md` com as seções obrigatórias: Contexto · Linha do tempo · Causa raiz sistêmica ("como o sistema permitiu a falha?") · O que foi tentado · O que aprendemos · Decisão resultante · Links ADR/código · Lacunas de evidência — FR-017
- [X] T005 Criar `docs/manuals/_verification/check_manuals.py` (**Red**): verifica (a) `git diff --exit-code -- docs/01_*.md … docs/12_*.md`, (b) existência dos arquivos do plano, (c) aviso de confidencialidade no `README.md`, (d) cabeçalho padrão em cada módulo, (e) links relativos, (f) referências `arquivo:símbolo` existentes no repositório, (g) varredura de padrões sensíveis (e-mail, telefone real, CPF, chaves) — FR-002, FR-004, NFR-004/005, SC-005/006/007
- [X] T006 Executar `python docs/manuals/_verification/check_manuals.py` e **confirmar que falha** por ausência de conteúdo (Red registrado)

---

## Phase 2: Foundational

*Bloqueia todas as trilhas. Sem label de US.*

- [ ] T007 Criar `specs/product-manual/evidence-inventory.md`: para cada conceito (Organization, Department, Project, Squad, JobTitle, Role, Permission, OrganizationMembership, ProjectMembership, SquadMembership, UserProfile.platform_role, DataAccessGrant, Document.Visibility, DocumentChunk, Contact/ContactPhoneNumber/ContactOrganizationMembership, Conversation/Message, AuditLog) registrar arquivo/símbolo/linha em `core/models.py`, testes que o comprovam e estado (✅/🟡/🧭) — FR-012, FR-020
- [ ] T008 Ler integralmente `core/models.py` (960 linhas) e anotar em `specs/product-manual/evidence-inventory.md` constraints, `unique_together`, `on_delete`, `clean()`/`save()` e `get_organization_id()` de `BaseMembership` e subclasses
- [ ] T009 [P] Ler `core/tests/test_rbac.py` e `core/management/commands/seed_demo.py` por completo e registrar no inventário os comportamentos **comprovados por teste** e os personagens/dados do seed
- [ ] T010 [P] Ler `core/middleware.py`, `core/apps.py`, `core/admin.py` e procurar `@receiver`/`signals` no repositório (excluindo `.venv`); registrar no inventário se há Signals reais ou apenas projetados (FR-011)
- [ ] T011 [P] Ler `core/services/{whatsapp_service,contact_service,conversation_service,evolution_gateway}.py`, `core/tasks/{whatsapp_tasks,orchestrate,ingest,checkpoint,__init__}.py`, `core/api/v1/views/webhook_whatsapp.py`, `core/views/webhook_views.py`, `core/adapters/evolution.py`, `core/orchestrator/*.py` e registrar o fluxo ponta a ponta real (webhook → Celery → serviço → contato/conversa → IA → gateway) e onde RBAC/Organização/SQUAD influenciam (ou **não** influenciam) o WhatsApp — FR-008, FR-012
- [ ] T012 [P] Extrair do git o "antes": `git show bb10c3b:ai_control_transition/core/{models.py,middleware.py,management/commands/seed_roles.py,management/commands/seed_permissions.py,management/commands/seed_demo.py}` e salvar o resumo comparativo antes/depois em `specs/product-manual/evidence-inventory.md` (D-03)
- [ ] T013 [P] Mapear no `AI_AGENT_CONVERSATION.md` (2592 linhas) as decisões e falhas com número de linha: Django Groups globais (~1832), roles atreladas a títulos (~1837), embedding 4096d (~2082), seeds ausentes (~1607), vertical de saúde (ADR-002), e registrar no inventário a lista **final** de candidatos a Post-Mortem com evidência (arquivo/commit/linha) ou **lacuna** — A-005
- [ ] T014 [P] Reler o README completo do pgvector (raw.githubusercontent.com/pgvector/pgvector/master/README.md) — seção Filtering sem truncamento — e atualizar F-03 em `specs/product-manual/research.md`
- [ ] T015 Executar o baseline de testes: `pytest core/tests tests -q` e registrar no inventário quais comportamentos têm cobertura automatizada (base de AS-007)
- [ ] T016 [P] Criar `docs/manuals/GLOSSARY.md` partindo de `docs/12_Glossary.md` (somente leitura) + termos novos (Squad, Membership, Visibility, slug de permissão, platform_role, denormalização de escopo, recall, Design de Referência) — FR-021
- [ ] T017 [P] Criar `docs/manuals/PERSONAS.md` com as organizações, departamentos, projetos, squads e personagens **fictícios** alinhados ao `seed_demo.py`, incluindo telefones/JIDs/e-mails claramente falsos (ex.: domínio `example.org`, números `+55 11 0000-0000`) — FR-010, FR-013
- [ ] T018 Criar `docs/manuals/README.md`: índice por público (1 clique até cada trilha), aviso "Confidencial — Uso interno da Engenharia", legenda ✅/🟡/🧭, como ler, e como rodar `check_manuals.py` — FR-001, NFR-004

---

## Phase 3: User Story 1 — Stakeholders / Executivos (P1)

**Story Goal**: executivo entende, sem código, como Organização, Roles, SQUADs, RAG e WhatsApp se combinam.
**Independent Test**: AS-001 — questionário de 10 perguntas ≥ 80%; AS-006 — caso "usuário sem SQUAD" coerente com a trilha de Engenharia.
**Referência**: FR-003, FR-005–FR-010, FR-022, FR-023

- [ ] T019 [P] [US1] Criar `docs/manuals/01-product/00_visao_geral.md` (o que é o produto hoje: plataforma agnóstica de Data Vault; mapa visual Mermaid das peças) — FR-003, FR-023
- [ ] T020 [P] [US1] Criar `docs/manuals/01-product/01_hierarquia_organizacional.md` (Organização → Departamento → Projeto → Squad: pertencimento, herança, isolamento; exemplo narrativo com `PERSONAS.md`) — FR-005, FR-010
- [ ] T021 [P] [US1] Criar `docs/manuals/01-product/02_papeis_e_permissoes.md` (roles, slugs, acúmulo de roles em escopos distintos, resolução final de acesso, platform_role) — FR-006, FR-010
- [ ] T022 [P] [US1] Criar `docs/manuals/01-product/03_conhecimento_e_rag.md` (quem vê quais documentos por `Visibility` e `ai_accessible`; o que está implementado × 🧭 Design de Referência) — FR-007, FR-010
- [ ] T023 [P] [US1] Criar `docs/manuals/01-product/04_whatsapp.md` (identificação do remetente, escopo de resposta, limites, como Organização/Role/SQUAD influenciam — apenas o que o inventário T011 comprovar) — FR-008, FR-010
- [ ] T024 [US1] Criar `docs/manuals/01-product/05_casos_limite.md` (usuário sem SQUAD, múltiplas organizações, remoção de Role, documento sem escopo, remetente desconhecido) com comportamento observável — FR-009
- [ ] T025 [US1] Criar `docs/manuals/01-product/questionario_validacao.md` (10 perguntas + gabarito) para AS-001 — AS-001
- [ ] T026 [US1] Revisar a trilha 01-product: sem blocos de código, cabeçalho padrão, links, rótulos de fidelidade; rodar `check_manuals.py` para os arquivos da trilha — FR-022, FR-004

---

## Phase 4: User Story 2 — Engenharia Deep-Dive (P1)

**Story Goal**: dev novo, não-clínico, implementa e mantém a lógica de acesso sem quebrar o isolamento.
**Independent Test**: AS-002/AS-003/AS-007 — reprodução local dos exemplos; equivalência ORM↔SQL explícita; violação bloqueada observada.
**Referência**: FR-005–FR-014, FR-020

- [ ] T027 [US2] Criar `docs/manuals/02-engineering/labs/_lab_base.py`: utilitário que roda cada lab em `transaction.atomic()` com **rollback ao final** e carrega personagens mock (sem poluir o banco; sem alterar código de produção)
- [ ] T028 [P] [US2] Criar `docs/manuals/02-engineering/labs/lab_01_hierarquia_rbac.py` (cria Org/Dept/Project/Squad/Roles/Memberships mock; imprime SQL via `connection.queries`) e executar com `python manage.py shell < …`, anexando a saída real ao módulo 01
- [ ] T029 [P] [US2] Criar `docs/manuals/02-engineering/labs/lab_02_permissoes.py` (chama `_check_permission` com cenários: platform_role, org role, usuário sem membership, **usuário em 2 orgs** — F-05) e executar
- [ ] T030 [P] [US2] Criar `docs/manuals/02-engineering/labs/lab_03_rag_visibilidade.sql` e `lab_03_rag_visibilidade.py` (insere `Document`/`DocumentChunk` mock com embeddings sintéticos de 768d; executa o **Design de Referência** em SQL nativo com `<=>` e em ORM com `CosineDistance`; `EXPLAIN (ANALYZE)`; cenário de filtro seletivo para demonstrar isolamento × recall — F-01/F-03) e executar
- [ ] T031 [P] [US2] Criar `docs/manuals/02-engineering/labs/lab_04_whatsapp_pipeline.py` (simula payload `messages.upsert` mock → `WhatsAppService.process_event` com gateway/Celery **mockados**; verifica criação de Contact/ContactPhoneNumber/Conversation/Message e mascaramento de PII) e executar
- [ ] T032 [US2] Criar `docs/manuals/02-engineering/01_modelo_de_dados_rbac.md` (diagrama ER Mermaid; `BaseMembership` e subclasses; Role/Permission por slug; ORM + SQL equivalente + saída do lab 01; ✅/🟡) — FR-005, FR-006, FR-011, FR-012, FR-014
- [ ] T033 [US2] Criar `docs/manuals/02-engineering/02_resolucao_de_permissoes.md` (middleware antes×depois; `_check_permission`; SQL gerado — `.exists()` com JOIN `role__permissions`; limitação multi-org F-05; caso feliz e violação bloqueada com `AuditLog`) — FR-006, FR-011, FR-014, FR-020
- [ ] T034 [US2] Criar `docs/manuals/02-engineering/03_rag_pgvector.md` (esquema `Document`/`DocumentChunk`; denormalização de escopo; `HnswIndex` cosseno m=16/ef_construction=64; 768d × limite 2000; ✅ existente × 🧭 Design de Referência; SQL nativo + ORM; `EXPLAIN`; isolamento × recall; divergência comentário `L2Distance`/"pré-filtragem" — F-01…F-04) — FR-007, FR-011, FR-012, FR-014, FR-020
- [ ] T035 [US2] Criar `docs/manuals/02-engineering/04_pipeline_whatsapp.md` (webhook → Celery → serviço → contato/conversa → IA mockada → gateway; onde Org/Role/SQUAD influenciam; sanitização de PII; ✅/🟡/🧭) — FR-008, FR-011, FR-012
- [ ] T036 [US2] Criar `docs/manuals/02-engineering/05_signals_auditoria_sanitizacao.md` (Signals **reais** conforme T010 — se não existirem, rotular 🧭 e descrever o contrato esperado; `AuditLog`; `_mask_pii`; testes `test_sanitization.py`) — FR-011, FR-020
- [ ] T037 [US2] Criar `docs/manuals/02-engineering/06_casos_limite_tecnico.md` (cada caso de FR-009 com ORM, SQL, teste/lab e comportamento real; consistente com `01-product/05_casos_limite.md` — AS-006) — FR-009, FR-014
- [ ] T038 [US2] Criar `docs/manuals/02-engineering/00_como_ler_e_rodar_labs.md` (pré-requisitos, passo a passo ≤ 30 min, comandos exatos, troubleshooting) — SC-004, AS-002
- [ ] T039 [US2] Executar todos os labs a partir do guia T038 em ambiente limpo e registrar tempo total e discrepâncias; corrigir o texto (nunca o código de produção) até os resultados coincidirem — AS-002, AS-003, AS-007, SC-004

---

## Phase 5: User Story 3 — Histórico e Post-Mortems (P1)

**Story Goal**: engenharia entende por que o modelo atual existe e não repete os erros.
**Independent Test**: AS-004 (template completo, sem culpa), AS-005 (≤ 2 cliques do índice até a causa das roles hardcoded).
**Referência**: FR-015–FR-019, FR-020

- [ ] T040 [US3] Criar `docs/manuals/03-history/README.md` (linha do tempo Mermaid `timeline`: first commit `bb10c3b` → `1ccdb3d` → `686d444`; ADR-001…004; separando "produto hoje" de "como chegamos aqui") — FR-015
- [ ] T041 [P] [US3] Criar `docs/manuals/03-history/adr-map.md` (mapa ADR-001…004 de `docs/09_Architecture_Decisions.md` + decisões **sem ADR formal** identificadas no inventário; **não editar** `docs/09_*`) — FR-019, FR-002
- [ ] T042 [P] [US3] Criar `docs/manuals/03-history/postmortems/PM-001_roles_planas_hardcoded.md` (evidência: `bb10c3b` middleware `'ADMIN' in roles`, `seed_roles.py` `PLATFORM_ADMIN`/`PARTICIPANT` → slugs/escopos; blameless, amplo e didático; links ADR/código) — FR-016/017/018
- [ ] T043 [P] [US3] Criar `docs/manuals/03-history/postmortems/PM-002_vertical_saude_acoplada.md` (ADR-002; evidência do `vitalia-01` fora do repo declarada como **lacuna** onde aplicável) — FR-016/017/018
- [ ] T044 [P] [US3] Criar `docs/manuals/03-history/postmortems/PM-003_django_groups_globais_em_multitenant.md` (tentativa **rejeitada** em design; trade-offs da conversa ~1832–1837; sem alegar incidente em produção) — FR-016/017/018
- [ ] T045 [P] [US3] Criar `docs/manuals/03-history/postmortems/PM-004_embedding_4096d_acima_do_limite_do_indice.md` (F-02: limite 2000 do `vector`; 768d + HNSW; lição sobre dimensionamento e `EXPLAIN`) — FR-016/017/018
- [ ] T046 [P] [US3] Criar `docs/manuals/03-history/postmortems/PM-005_banco_sem_seeds_apos_migracao.md` (conversa ~1607; seeds `seed_permissions`/`seed_roles` removidos e substituídos; evidência `git show 1ccdb3d --stat`) — FR-016/017/018
- [ ] T047 [US3] Para cada PM publicado, confirmar que **todo fato** tem evidência (arquivo/commit/linha) ou está marcado como lacuna; **descartar** PM sem evidência e atualizar `README.md` do histórico e `plan.md` (conjunto final) — A-005, FR-020
- [ ] T048 [US3] Auditar cada PM contra `_templates/postmortem_template.md` e contra linguagem blameless (sem nomes/atribuição de culpa) — AS-004
- [ ] T049 [US3] Verificar AS-005: a partir de `docs/manuals/README.md`, a causa do abandono das roles hardcoded é alcançada em ≤ 2 cliques

---

## Phase 6: User Story 4 — Trilha Acadêmica (P2)

**Story Goal**: pesquisador novo entende conceitos e fluxos e consegue contribuir.
**Independent Test**: leitura guiada por 1 pessoa não-engenheira; checklist de compreensão passa.
**Referência**: FR-003, FR-004

- [ ] T050 [US4] Criar `docs/manuals/04-academic/trilha_onboarding.md` (ordem de leitura 01-product → conceitos de 02-engineering sem pressupor Django → PMs selecionados; glossário; exercícios com `PERSONAS.md`) — FR-003, FR-004
- [ ] T051 [US4] Adicionar ao `trilha_onboarding.md` checklist de compreensão (8 itens) e links cruzados verificados por `check_manuals.py`

---

## Phase 7: User Story 5 — Mantenabilidade (P2)

**Story Goal**: mantenedor detecta rapidamente conteúdo obsoleto.
**Independent Test**: AS-008 — cabeçalho com data e commit de referência em todos os módulos.
**Referência**: NFR-005, FR-004

- [ ] T052 [US5] Aplicar o cabeçalho padrão (`_templates/module_header.md`) em **todos** os módulos de `docs/manuals/**` com data e commit de referência (`git rev-parse --short HEAD`) — AS-008, NFR-005
- [ ] T053 [US5] Completar `check_manuals.py` com `--check-staleness`: compara commit do cabeçalho com `HEAD` e lista arquivos de código citados que mudaram desde então; documentar uso em `docs/manuals/README.md` — NFR-005
- [ ] T054 [US5] Executar `check_manuals.py` completo (**Green**) e registrar a saída em `specs/product-manual/verification-report.md`

---

## Phase N: Polish & Cross-Cutting

*Qualidade, segurança e conformidade. Sem label de US.*

- [ ] T055 Varredura de dados sensíveis em `docs/manuals/**` (e-mails, telefones, CPF, tokens, JIDs reais, `.env`): `grep -rEn` com padrões documentados + revisão manual — AS-010, FR-013, SC-007
- [ ] T056 Verificar que `docs/01_*.md … docs/12_*.md` não mudaram: `git diff --exit-code -- docs/01_* docs/02_* docs/03_* docs/04_* docs/05_* docs/06_* docs/07_* docs/08_* docs/09_* docs/10_* docs/11_* docs/12_*` — AS-009, FR-002, SC-006
- [ ] T057 Verificar consistência terminológica entre `GLOSSARY.md`, `01-product` e `02-engineering` (mesmo termo, mesmo sentido) — FR-021
- [ ] T058 Verificar SC-005: ≥ 90% das referências `arquivo:símbolo` resolvem no repositório (saída do `check_manuals.py`)
- [ ] T059 Revisão final dos rótulos ✅/🟡/🧭: nenhum comportamento 🧭 apresentado como implementado — FR-020
- [ ] T060 Executar `/vitalia-analyze` (spec × plan × tasks) e `/vitalia-converge` (conteúdo × repositório) e resolver achados CRITICAL/HIGH
- [ ] T061 Preparar para `/vitalia-session-end`: registrar as decisões (estrutura `docs/manuals/`, rótulos de fidelidade) e os achados F-03/F-04/F-05 como aprendizados do projeto

---

## Cobertura de Requisitos

| FR / NFR | Tasks |
|---|---|
| FR-001 | T018 |
| FR-002 | T005, T041, T056 |
| FR-003 | T019, T050 |
| FR-004 | T003, T026, T050, T052 |
| FR-005 | T020, T032 |
| FR-006 | T021, T032, T033 |
| FR-007 | T022, T034 |
| FR-008 | T011, T023, T035 |
| FR-009 | T024, T037 |
| FR-010 | T017, T020–T023 |
| FR-011 | T030, T032–T036 |
| FR-012 | T007, T011, T032, T034, T035 |
| FR-013 | T017, T055 |
| FR-014 | T032–T034, T037 |
| FR-015 | T040 |
| FR-016/017/018 | T004, T042–T046, T048 |
| FR-019 | T041 |
| FR-020 | T033, T034, T036, T047, T059 |
| FR-021 | T016, T057 |
| FR-022 | T026 |
| FR-023 | T019 |
| NFR-001 | T017, T055 |
| NFR-004 | T005, T018 |
| NFR-005 | T002, T052, T053 |

| Success Criteria | Tasks |
|---|---|
| SC-001 | T018–T050 (existência verificada em T054) |
| SC-002 | T032–T037 |
| SC-003 | T042–T048 |
| SC-004 | T038, T039 |
| SC-005 | T005, T058 |
| SC-006 | T056 |
| SC-007 | T055 |

---

## Dependency Graph

```
Phase 0 → Phase 1 → Phase 2 ─┬→ Phase 3 (US1) ──────────┐
                             ├→ Phase 4 (US2) ──────────┼→ Phase 6 (US4) → Phase 7 (US5) → Phase N
                             └→ Phase 5 (US3) ──────────┘
```

Dependências internas relevantes:
- T005/T006 (Red) antecedem qualquer conteúdo; T054 (Green) fecha o ciclo.
- T007–T015 (inventário/evidências) antecedem US1–US3; T013 define o **conjunto final** de PMs usado em T042–T046.
- T027 antecede T028–T031; T028–T031 antecedem T032–T037 (cada módulo anexa a saída real do respectivo lab).
- T038 antecede T039; T039 antecede a aprovação da trilha de Engenharia.
- T047–T049 dependem de T042–T046.
- Phase 6 depende de US1, US2 e US3 concluídas.

## Parallel Execution

Tasks marcadas `[P]` dentro da mesma fase podem ser executadas simultaneamente (arquivos distintos, sem dependência pendente):
- **Phase 1**: T003, T004
- **Phase 2**: T009, T010, T011, T012, T013, T014, T016, T017
- **Phase 3**: T019, T020, T021, T022, T023
- **Phase 4**: T028, T029, T030, T031 (após T027)
- **Phase 5**: T041, T042, T043, T044, T045, T046
- **Entre fases**: US1, US2 e US3 podem avançar em paralelo após a Phase 2.
