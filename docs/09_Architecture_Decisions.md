<!-- 09_Architecture_Decisions.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 9. Architecture Decisions (ADRs)

Este arquivo sumariza os registros históricos de decisões arquiteturais do projeto.

| ID | Data | Decisão | Justificativa | Status |
|----|------|---------|---------------|--------|
| **ADR-001** | 03/10/2026 | Padronização de variáveis `WHATS_GT_*` (docker-compose). | Isolar o provedor específico (Evolution API) e garantir agnosticismo do Gateway de Mensagens, abandonando o acoplamento `EVOLUTION_*`. | ✅ Aprovada |
| **ADR-002** | 05/10/2026 | Transição para Plataforma Agnóstica (Remoção do escopo Saúde). | Foco absoluto no core value: Privacidade, Data Vault e Ingestão AI, permitindo expansão comercial para além de verticais clínicas. | ✅ Aprovada |
| **ADR-003** | 05/10/2026 | Exportação de ERD em formato `.dot`. | Contornar dependências C++ complexas do SO (`graphviz`), facilitando integrações CI/CD e diffs textuais no Git. | ✅ Aprovada |
| **ADR-004** | 05/10/2026 | Adoção do `drf-spectacular` com `@extend_schema`. | Compatibilização moderna de OpenAPI 3.0 para o Django, com manipulação explícita de endpoints genéricos (`APIView`). | ✅ Aprovada |

