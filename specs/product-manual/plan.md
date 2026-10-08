<!-- plan.md | Vitalia SDD v0.6.0 | 07-10-2026 22:50(GMT-04:00) -->
# Implementation Plan: Manual de Produto e Histórico Arquitetural

**Branch**: `main` (feature dir `specs/product-manual`) | **Date**: 07-10-2026 | **Spec**: [spec.md](./spec.md) | **Research**: [research.md](./research.md)

## Summary

Produzir, em `docs/manuals/`, um ecossistema documental em 4 trilhas (Produto, Engenharia, Histórico/Post-Mortems, Acadêmica) mais Glossário, Índice e Templates, **sem alterar** `docs/01`–`12`. O conteúdo é derivado do **código real** (`core/models.py`, `core/middleware.py`, `core/services/*`, `core/tasks/*`, testes), do **diff git `bb10c3b → HEAD`** e de `AI_AGENT_CONVERSATION.md`. Exemplos de engenharia expõem SQL nativo, `pgvector`, ORM, Signals e middleware. Onde o comportamento descrito na conversa **não está implementado** (ex.: consulta RAG), o manual rotula como *Design de Referência* e valida em laboratório.

## Technical Context

**Language/Version**: Markdown (GFM) + Mermaid; trechos de código em Python 3.14 / Django 6.1 / SQL (PostgreSQL + pgvector)
**Primary Dependencies**: nenhuma nova. Ferramentas locais: `git`, `psql`/Django shell, `pytest` (para validar exemplos)
**Storage**: N/A (documentação versionada em Git)
**Testing**: validação por (a) script de verificação de links/referências de código, (b) execução dos laboratórios contra o ambiente local com `seed_demo`, (c) varredura de dados sensíveis, (d) checagem `git diff` em `docs/01`–`12`
**Target Platform**: Repositório Git (leitura em GitHub/IDE)
**Project Type**: documentação (docs-as-code)
**Performance Goals** (de SC-xxx): dev novo reproduz 1º exemplo em ≤ 30 min (SC-004); ≥ 90% das referências de código resolvem (SC-005)
**Constraints**: confidencial/uso interno (NFR-004); pt-BR (NFR-002); zero dados reais (NFR-001); Arc42 intocado (FR-002)

## Constitution Check

*Resultado do gate `sdd_judge --mode plan`: ver seção "Resultado do Gate" ao final deste arquivo.*

| Princípio | Aplicação nesta feature | Status |
|---|---|---|
| P00 Bem-estar humano | Post-mortems blameless; onboarding mais seguro | ✅ |
| P01 SDD Pipeline | spec → plan → tasks → implement → converge respeitado; nenhum código de produção alterado | ✅ |
| P02 Declaração de impacto | Multi-tenancy/RBAC/privacidade são o **tema**; impacto: nenhum no runtime | ✅ |
| P03 Grounding | `research.md` com fontes verificadas + achados F-01…F-06 | ✅ (pendências listadas) |
| P05 TDD | N/A para código; equivalente documental: **validação de exemplos antes de publicar** (Red = exemplo falha → corrigir texto) | ✅ N/A |
| P07 Privacy by Design | Mocks apenas; exemplos citam `user_id + organization_id`; varredura de sensíveis (SC-007) | ✅ |
| P17 EU AI Act | Não é afirmação normativa nesta feature; qualquer menção futura exige verificação (domínio `regulations`) | ✅ N/A |

## Technical Decisions

Ver [research.md](./research.md): D-01 (post-mortem blameless), D-02 (ADR × PM), D-03 (hierarquia de evidências), D-04 (estrutura), D-05 (mocks via `seed_demo`), e fatos F-01…F-06.

### Achados do research que moldam o plano
1. **RAG não implementado** (F-04): módulo RAG = *o que existe* + *Design de Referência* rotulado. Inclui lição sobre o comentário `L2Distance` × índice cosseno.
2. **Filtro após índice HNSW** (F-03): ensinar **isolamento ≠ recall**; incluir `EXPLAIN` e a limitação de `LIMIT` com filtro seletivo.
3. **Permissão de org sem escopo na rota** (F-05): documentar o comportamento exato e a limitação para múltiplas orgs; usar nos casos-limite (FR-009).
4. **Histórico git curto** (D-03): PMs declaram lacunas de evidência.

## Project Structure

### Documentation (this feature)
```text
specs/product-manual/
├── research-brainstorming.md
├── spec.md
├── plan.md                  # este arquivo
├── research.md
├── tasks.md                 # próximo passo (/vitalia-spec-tasks)
└── checklists/requirements.md
```

### Source Code (entregáveis — somente documentação nova)
```text
docs/manuals/
├── README.md                          # índice por público + aviso de confidencialidade (FR-001, NFR-004)
├── GLOSSARY.md                        # termos do ecossistema (FR-021)
├── _templates/
│   ├── postmortem_template.md         # FR-017
│   └── module_header.md               # FR-004, NFR-005
├── 01-product/                        # Trilha Stakeholders (sem código — FR-022)
│   ├── 00_visao_geral.md
│   ├── 01_hierarquia_organizacional.md
│   ├── 02_papeis_e_permissoes.md
│   ├── 03_conhecimento_e_rag.md
│   ├── 04_whatsapp.md
│   └── 05_casos_limite.md
├── 02-engineering/                    # Trilha Deep-Dive (FR-011)
│   ├── 01_modelo_de_dados_rbac.md     # Org/Dept/Project/Squad, Memberships, Role/Permission
│   ├── 02_resolucao_de_permissoes.md  # middleware, _check_permission, SQL gerado, limitações
│   ├── 03_rag_pgvector.md             # Document/DocumentChunk, HNSW, filtro, EXPLAIN, Design de Referência
│   ├── 04_pipeline_whatsapp.md        # webhook→Celery→service→contato/conversa→gateway
│   ├── 05_signals_auditoria_sanitizacao.md
│   ├── 06_casos_limite_tecnico.md
│   └── labs/                          # scripts reproduzíveis com mocks (sem tocar produção)
├── 03-history/
│   ├── README.md                      # linha do tempo; produto-hoje × como-chegamos (FR-015)
│   ├── adr-map.md                     # mapa ADR-001…004 + lacunas (FR-019)
│   └── postmortems/
│       ├── PM-001_roles_planas_hardcoded.md
│       ├── PM-002_vertical_saude_acoplada.md
│       ├── PM-003_django_groups_globais_em_multitenant.md   # tentativa rejeitada
│       ├── PM-004_embedding_4096d_acima_do_limite_do_indice.md
│       └── PM-005_banco_sem_seeds_apos_migracao.md
│       # Conjunto FINAL definido na Fase 2 pela auditoria de evidências (D-03)
├── 04-academic/
│   └── trilha_onboarding.md
└── _verification/
    └── check_manuals.py               # links, refs de código, aviso de confidencialidade, varredura de sensíveis
```
> Os 5 PMs acima são **candidatos** extraídos de `AI_AGENT_CONVERSATION.md`; cada um só é publicado com evidência rastreável (arquivo/commit/linha da conversa), caso contrário recebe a marca "lacuna de evidência" ou é descartado.

## Phase Overview

### Phase 1: Setup
- Criar árvore `docs/manuals/`, templates e `README.md` (índice + confidencialidade).
- Congelar **commit de referência** (`git rev-parse HEAD`) para os cabeçalhos (NFR-005).
- Criar `_verification/check_manuals.py` (esqueleto): falha se `docs/01`–`12` mudarem, se link/ref quebrar, se faltar aviso.

### Phase 2: Foundational (bloqueia as trilhas)
- **Auditoria de evidências** → inventário `evidence-inventory.md` (fora de `docs/manuals/`, em `specs/product-manual/`): para cada conceito (Org, Dept, Project, Squad, Role, Permission, Membership, Visibility, WhatsApp) arquivo/símbolo/linha + testes (`core/tests/test_rbac.py`, etc.) + estado (implementado / parcial / planejado).
- Definir `GLOSSARY.md` base e personagens/organizações mock (alinhados ao `seed_demo`).
- Ler `seed_demo.py` e `core/tests/test_rbac.py` por completo; extrair comportamentos *comprovados por teste*.
- Reler README do pgvector completo (F-03 truncado) antes de escrever o módulo RAG.

### Phase 3: User Story 1 — Stakeholders (P1)
- `01-product/*` em linguagem de comportamento, com narrativas mock e diagramas Mermaid; sem código.
- AS-001: questionário de 10 perguntas para validação.

### Phase 4: User Story 2 — Engenharia Deep-Dive (P1)
- `02-engineering/*` + `labs/`; cada relação com (a) ORM, (b) SQL equivalente, (c) caso feliz e (d) violação bloqueada (FR-014).
- RAG: *existente* vs *Design de Referência* rotulado; `EXPLAIN`; isolamento × recall.
- Resolução de permissões: SQL gerado por `_check_permission`; limitação multi-org (F-05).

### Phase 5: User Story 3 — Histórico e Post-Mortems (P1)
- `03-history/README.md`, `adr-map.md`, PMs conforme inventário de evidências; template blameless; links para ADR/código.

### Phase 6: User Story 4 — Trilha Acadêmica (P2)
- `04-academic/trilha_onboarding.md` derivada das fases 3–5 (conceitos e fluxos, sem pressupor Django).

### Phase 7: User Story 5 — Mantenabilidade (P2)
- Cabeçalho padrão em todos os módulos (data + commit); `check_manuals.py` completo e documentado.

### Phase N: Polish & Cross-Cutting
- Executar `check_manuals.py`; rodar labs; varredura de sensíveis (SC-007); `git diff -- docs/01_* … docs/12_*` vazio (SC-006); revisão de consistência de glossário; `/vitalia-analyze` e `/vitalia-converge`.

## Riscos
| Risco | Mitigação |
|---|---|
| Manual descrever comportamento não implementado como real | Rótulos obrigatórios: ✅ Implementado / 🟡 Parcial / 🧭 Design de Referência; checagem por inventário de evidências |
| Evidência histórica insuficiente (3 commits) | Declarar lacunas; usar `bb10c3b` e conversa; não inventar fatos (A-005) |
| Exemplos ficarem obsoletos | Commit de referência no cabeçalho + `check_manuals.py` |
| Vazamento de dado real em exemplo | Mocks do `seed_demo`; varredura automatizada + revisão |
| Tom de culpa nos PMs | Template blameless + revisão AS-004 |

## Resultado do Gate
`sdd_judge.py --mode plan` em 07-10-2026: **PASS** (exit 0).
Observação: o provedor Gemini estava indisponível (sem `GEMINI_API_KEY`/`GOOGLE_API_KEY`) e o veredicto veio do fallback local (Ollama), com parecer genérico. O Constitution Check manual acima permanece como evidência primária.
