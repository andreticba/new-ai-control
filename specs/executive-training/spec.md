<!-- spec.md | Vitalia SDD v0.6.0 | 08-10-2026 08:11(GMT-04:00) -->
# Especificação de Funcionalidade: Treinamento Socrático e Sumário Executivo

**Data:** 08-10-2026
**Autor/Agente:** Vitalia Architect

## 1. Contexto e Objetivo (O Quê e Por Quê)
Desmembrar a documentação da fase de engenharia base para criar materiais educacionais e executivos de alto nível. O Sumário Executivo foca em demonstrar o valor de negócio das capacidades de IA (Híbrido - Business Value & Capabilities). O Treinamento Socrático documenta falhas e escolhas arquiteturais através de cenários de roleplay (Post-Mortems iterativos) para integrar e treinar novos talentos de forma resiliente e crítica. Tudo permanecerá em Markdown protegido pelo Git.

## 2. Requisitos Funcionais
O que o artefato final deve entregar?
- [FR-001] O sistema deve incluir um Sumário Executivo direcionado a stakeholders e executivos C-level.
- [FR-002] O Sumário Executivo deve mapear capacidades técnicas (ex: RAG Seguro, RBAC) para Retorno sobre Investimento (ROI) e mitigação de risco corporativo.
- [FR-003] O sistema deve incluir módulos de Treinamento Socrático para engenheiros.
- [FR-004] Os módulos de Treinamento Socrático devem ser estruturados como *Cenários de Desafio* baseados nos Post-Mortems de incidentes passados (ex: Tenant Bleed, Django Groups).
- [FR-005] Toda a documentação deve ser formatada e hospedada em Markdown diretamente no repositório Git.

## 3. Requisitos Não-Funcionais (Restrições)
Quais as regras de aderência à Constituição do Arquiteto?
- [SC-001] Sigilo e Segurança: Acesso aos arquivos confidenciais deve requerer permissões estritas via controle de acesso Git, sem exposição pública prévia em portais estáticos inseguros.
- [SC-002] Verificabilidade: A documentação não pode quebrar os cheques do `check_manuals.py` se colocada em pastas monitoradas.
- [SC-003] Impacto Declarado (P02): O sumário deve conectar claramente o impacto na privacidade (HIPAA/LGPD) e isolamento multi-tenant para os usuários finais.

## 4. Histórias de Usuário (User Stories)
**Como um** stakeholder executivo, **eu quero** ler um sumário híbrido **para que** eu entenda como o RAG seguro protege o IP da empresa e gera ROI.
**Como um** engenheiro sênior em onboarding, **eu quero** interagir com um material socrático baseado em falhas passadas **para que** eu internalize as escolhas do RBAC matricial do projeto.

## 5. Critérios de Aceite (Acceptance Criteria)
Condições estritas para considerar a funcionalidade concluída.
- [ ] Dado que um executivo lê o sumário, quando ele buscar informações de isolamento de dados, então ele deve ver referências claras ao valor do negócio sem código exposto.
- [ ] Dado que um engenheiro abre o módulo de treinamento, quando ele estudar o caso de "Tenant Bleed", então ele deve enfrentar questionamentos sobre o porquê do Vector DB externo ter falhado em vez de ler apenas a resposta direta.
- [ ] Dado que a documentação é comitada, quando o CI rodar, então todos os links internos para os Post-Mortems e ADRs devem ser válidos e as regras de sanitização de PII respeitadas.

## 6. Fora do Escopo (Out of Scope)
O que NÃO será feito nesta etapa (para evitar scope creep).
- [ ] Não inclui portais web de documentação pública (MkDocs, Docusaurus).
- [ ] Não inclui automações via IA (como bots interativos automatizados fora da IDE).

## Suposições Verificadas
- Estruturação baseada nos artefatos isolados previamente gerados em `specs/executive-training/research-brainstorming.md`.
