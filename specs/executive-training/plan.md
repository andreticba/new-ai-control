<!-- plan.md | Vitalia SDD v0.6.0 | 08-10-2026 08:20(GMT-04:00) -->
# Implementation Plan: Treinamento Socrático e Sumário Executivo

**Branch**: `docs/executive-training` | **Date**: 08-10-2026 | **Spec**: [spec.md](spec.md)

## Summary
Estruturação e redação de manuais educacionais e sumário executivo em formato Markdown. A abordagem técnica foca em separar fisicamente os documentos para o público C-Level (focado em valor e ROI) dos documentos para Engenharia (focados em cenários Socráticos e Roleplay de incidentes).

## Technical Context

**Language/Version**: Markdown (GFM)
**Primary Dependencies**: `check_manuals.py` (validador de compliance interno)
**Storage**: Git Repository (Apenas Acesso Autenticado)
**Testing**: CI Validator Script (Regex de PII e links quebrados)
**Target Platform**: GitHub / GitLab Web Interface / IDEs
**Project Type**: Documentation
**Performance Goals**: N/A (Arquivos estáticos textuais)
**Constraints**: Todos os arquivos devem estar livres de PII/PHI reais e passar na verificação automatizada.

## Constitution Check
✅ VEREDICTO FINAL: PASS (com Warning mitigado em P07 - Privacy by Design). Os dados reais nos Post-Mortems foram anonimizados conforme exigência.

## Technical Decisions
- **Decisão: Hosppagem via Git (Não exposto)**
  - **Escolhido**: Armazenar os manuais de negócio confidenciais estritamente no repositório.
  - **Verificado em**: [OWASP Security Practices for Sensitive Data](https://owasp.org/) em 08-10-2026.
  - **Justificativa**: Evita exposição acidental em portais estáticos inseguros de documentos que contêm estratégias de engenharia e regras de RBAC do sistema.
  - **Alternativas**:
    - [MkDocs/Docusaurus com autenticação]: rejeitado devido à complexidade infraestrutural para gerir controle de acesso externo nesta fase inicial.

- **Decisão: Padrão Socrático em Markdown**
  - **Escolhido**: Adotar blocos de *collapsible* (details/summary) ou estruturas visuais em Markdown para omitir respostas diretas, forçando o leitor a pensar no problema.
  - **Verificado em**: [GitHub Docs - Basic Writing and Formatting Syntax](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections) em 08-10-2026.
  - **Justificativa**: Emulando um sistema socrático, o usuário precisa parar e analisar as perguntas que levaram à falha arquitetural, antes de ler a solução do Post-Mortem.

## Project Structure

### Documentation (this feature)
- `specs/executive-training/`
  - `spec.md`
  - `plan.md`
  - `checklists/`
  - `research-brainstorming.md`

### Source Code (Destinos)
- `docs/executive/`
  - `01_executive_summary.md` (FR-001, FR-002)
- `docs/training/`
  - `socratic_01_tenant_bleed.md` (FR-003, FR-004)
  - `socratic_02_django_groups.md` (FR-003, FR-004)

## Phase Overview

### Phase 1: Setup e Estrutura Inicial
- Criação dos diretórios `docs/executive/` e `docs/training/`.
- Configuração dos templates base dos arquivos com os headers obrigatórios GMT-04:00.

### Phase 2: Sumário Executivo
- Redação do `01_executive_summary.md` traduzindo o RAG Seguro e RBAC para impacto financeiro e mitigação de risco regulatório.

### Phase 3: Módulos de Treinamento Socrático
- Adaptação do `pm_001_falha_django_groups.md` e `pm_002_vector_tenant_bleed.md` em formatos interativos usando cenários e reflexões de arquitetura (`socratic_01` e `socratic_02`).

### Phase 4: Validação de Compliance
- Execução do script `check_manuals.py` nos novos documentos para atestar integridade de links e sanitização.
