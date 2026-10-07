<!-- 08_Crosscutting_Concepts.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 8. Cross-cutting Concepts

Este documento aborda os conceitos que atravessam horizontalmente todos os módulos da plataforma.

## 8.1 Arquitetura Data Vault
O Data Vault aqui não se refere puramente à modelagem de BI tradicional (Hub, Link, Satellite), mas sim ao **conceito de isolamento criptográfico e de privacidade**.
- Dados transacionais de usuários finais não se misturam publicamente.
- O uso de bibliotecas como `django-crypto-fields` impõe que campos marcados como sensíveis (CPF, Telefones, Históricos de Chat) sofram criptografia assimétrica/simétrica via chave RSA/AES antes de tocar o disco do PostgreSQL.

## 8.2 Privacidade e Conformidade (LGPD)
- **Ocultação Automática:** Sempre que um consentimento de usuário final é revogado, filtros globais nos Services impedem que as camadas superiores acessem os registros.
- **Rastreabilidade (LogEntry):** Todas as mutações no banco disparam logs imutáveis (Django Admin / Histórico), amarrados ao identificador do requisitante.

## 8.3 Roteamento LLM Agnóstico
Sistemas modernos baseados em IA sofrem com "Vendor Lock-in". Para evitar que a plataforma dependa inteiramente da OpenAI ou do Google, as chamadas a modelos fundacionais (LLMs) devem abstrair os contratos. O modelo ativo será sempre ditado por variáveis de ambiente (ex: `ROUTER_LLM_PROFILE`), permitindo substituição imediata, inclusive por modelos rodando localmente (Ollama), mantendo o Agnosticismo de Hardware.

