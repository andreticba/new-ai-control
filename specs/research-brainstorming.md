# research-brainstorming.md | Vitalia SDD v0.6.0 | 08-10-2026 21:42(GMT-04:00)

## Resumo das Decisões Tomadas (Refatoração Base AI-Control)

1. **Profundidade do Modelo Matricial (RBAC):** Transplante Integral (4 Níveis - Organization, Department, Project, Squad) respeitando estritamente o manual `01_modelo_de_dados_rbac.md`.
2. **Portabilidade do Data Vault:** Portar integralmente com a criptografia ativada desde o início (Blind Indexing com `django-crypto-fields`).
3. **Estratégia de Reconstrução:** Reconstrução Atômica (Linha a Linha) para não herdar dívida técnica.
4. **Isolamento de Domínio no Core:** Core Estrito (Clean Core). Foco absoluto em Segurança, RBAC e Isolamento de Tenant. Gamificação, Onboarding e Perfil Médico não farão parte deste app.
5. **RAG e Vetorização:** Extrair `Document` e `DocumentChunk` para uma app própria (ex: `knowledge_hub`), apontando via FK referencial para a Organização do `core`.
6. **Mensageria e Roteamento de IA:** O complexo orquestrador de chat (Celery Tasks, Roteamento de LLM, e tabelas de `Contact`, `Conversation`, `Message`) encontrado no legado `AI-Control 08-11-2025-21-25.md` será totalmente migrado, mas **isolado em uma app unificada `omnichannel` (ou `crm`)**, deixando o `core` enxuto.
7. **Tratamento de Migrations:** Greenfield Absoluto. O banco vai nascer do zero.

## Rastro de Pesquisa e Descoberta

| # | Afirmação | Verificado? | Fonte | Data |
|---|---|---|---|---|
| 1 | Referências de FK cross-app no Django causam *Circular Dependency* (ImportError) se importadas via objeto, devendo-se usar strings. | ✅ Sim | Documentação Django / Fóruns | 08-10-2026 |
| 2 | O vitalia-01 original não tinha histórico ou mensageria; a lógica foi concebida no AI-Control original. | ✅ Sim | `legacy_schema.sql` (vitalia-01) | 08-10-2026 |
| 3 | A orquestração robusta de IA (Triage, Context Lock) residia em tasks isoladas no `AI-Control 08-11-2025-21-25.md`. | ✅ Sim | Arquivo Mestre Legado | 08-10-2026 |
