<!-- tasks.md | Vitalia SDD v0.6.0 | 08-10-2026 08:27(GMT-04:00) -->
# Tasks: Treinamento Socrático e Sumário Executivo

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)
**Gerado em**: 08-10-2026

---

## MVP Scope

> Implementar **Phase 1 + Phase 2 (US1) + Phase 3 (US2) + Phase 4** entrega o escopo documental completo funcionando.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e grounding ANTES de qualquer implementação. Sem label de US.*

- [X] T000-A Verificar existência dos Post-Mortems originais (`pm_001` e `pm_002`) no projeto para servirem de base.
- [X] T000-B Verificar disponibilidade do validador `check_manuals.py` no projeto.

---

## Phase 1: Setup

*Inicialização do ambiente documental. Sem label de US.*

- [X] T001 [P] Criar diretório `docs/executive/`
- [X] T002 [P] Criar diretório `docs/training/`

---

## Phase 2: User Story 1 — Sumário Executivo Híbrido

**Story Goal**: Entregar leitura clara para stakeholders sobre RAG Seguro e RBAC atrelado a ROI e mitigação de risco.
**Independent Test**: Leitura do artefato confirma ausência de código complexo e destaque para o valor de negócio (compliance com check_manuals.py).
**Referência**: FR-001, FR-002, SC-003

- [X] T003 [US1] Criar arquivo base com cabeçalhos em `docs/executive/01_executive_summary.md`
- [X] T004 [US1] Redigir seção de Valor de Negócio (ROI) mapeando a arquitetura do RAG Seguro contra riscos em `docs/executive/01_executive_summary.md`
- [X] T005 [US1] Redigir seção de Capacidades (Capabilities) detalhando a adoção do RBAC Matricial em `docs/executive/01_executive_summary.md`

---

## Phase 3: User Story 2 — Módulos Socráticos de Engenharia

**Story Goal**: Entregar treinamentos interativos para onboarding com base nas falhas arquiteturais reais do projeto.
**Independent Test**: Leitura dos módulos comprova o uso da tag `<details>` para esconder respostas.
**Referência**: FR-003, FR-004

- [X] T006 [P] [US2] Estruturar caso do Vector DB no modelo desafio Socrático com `<details>` em `docs/training/socratic_01_tenant_bleed.md`
- [X] T007 [P] [US2] Estruturar caso das Roles hardcoded no modelo desafio Socrático com `<details>` em `docs/training/socratic_02_django_groups.md`

---

## Phase 4: Polish & Cross-Cutting (Validação de Compliance)

*Garantir conformidade SC-002 e SC-003 antes de encerrar.*

- [X] T008 Rodar a validação de links e sanitização com o script python no arquivo `docs/executive/01_executive_summary.md`
- [X] T009 Rodar a validação de links e sanitização com o script python nos arquivos de `docs/training/`

---

## Dependency Graph

```
Phase 0 → Phase 1 → Phase 2 (US1)
                  ↘ Phase 3 (US2) ↘ 
                                    Phase 4
```

## Parallel Execution

Tasks marcadas [P] dentro da mesma fase podem ser executadas simultaneamente.
