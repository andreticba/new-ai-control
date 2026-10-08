<!-- 01-product/00_visao_geral.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

# 00. Visão Geral do Produto
**Público-alvo:** Stakeholders, Executivos, Novos PMs  
**Tempo de Leitura:** 5 min

A Plataforma é um ecossistema B2B multitenant projetado para fornecer governança profunda sobre os fluxos de IA. Seu principal diferencial não é a IA em si, mas as engrenagens de **controle de acesso (RBAC Matricial)** e de **isolamento vetorial (RAG seguro)**.

## Agnosticismo Radical ✅
Diferente de sistemas legados que amarravam seu banco de dados a domínios rígidos (como vertical de saúde), a Plataforma atual foi reescrita sob o princípio do Agnosticismo (ver [GLOSSARY](../GLOSSARY.md)). Isso significa que o núcleo do sistema não sabe o que é um "Paciente" ou um "Exame". O núcleo só reconhece "Organizações", "SQUADs", "Conversas" e "Documentos". A camada de domínio (saúde, finanças, educação) deve ser injetada via prompt ou RAG, sem contaminar o banco de dados principal.

## O Data Vault e a Proteção de PII 🟡
Como o sistema lida com o WhatsApp, informações de identificação pessoal (PII - *Personally Identifiable Information*) fluem livremente nas conversas.
Para que a IA tenha acesso a esse histórico sem vazar dados para provedores de nuvem e para manter a conformidade com a LGPD:
1. **Blind Indexing**: Permite realizar buscas exatas em dados criptografados sem precisar descriptografá-los todos de uma vez (usado no `search_tokens`).
2. **Separação Rígida**: O conteúdo sensível é particionado no cofre de dados (*Data Vault*). Um `DataAccessGrant` controla por quanto tempo e qual entidade terceira pode ler a chave simétrica de um dado.

## Próximos Passos
Siga para a leitura de [01. Hierarquia Organizacional](01_hierarquia_organizacional.md) para compreender como as Universidades e Empresas são mapeadas na arquitetura.
