<!-- 10_Quality_Requirements.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 10. Quality Requirements

A plataforma prioriza três atributos de qualidade arquitetural sobre todos os outros:

## 1. Segurança e Privacidade (Prioridade Máxima)
- **Cenário:** O banco de dados da aplicação é vazado por uma falha de rede na infraestrutura B2B.
- **Requisito:** PII de usuários finais continuam ilegíveis sem acesso físico às chaves RSA/AES hospedadas separadamente em cofres na aplicação.
- **Medida:** Testes automatizados verificando a criptografia de campos.

## 2. Manutenibilidade e Baixo Acoplamento
- **Cenário:** A empresa deseja trocar o provedor de disparo de mensagens ou provedor de LLM.
- **Requisito:** A troca deve ser feita com 0 refatorações do Core e sem instabilidade do banco de dados, configurando apenas o arquivo `.env`.
- **Medida:** Agnosticismo de provedores garantido via interfaces.

## 3. Desempenho e Resiliência
- **Cenário:** Um pico absurdo de milhares de requisições de mensagens de webhook ocorre simultaneamente em 1 minuto.
- **Requisito:** A API deve manter resposta média sob 150ms.
- **Medida:** Tudo que é assíncrono é delegado para o Redis/Celery. O endpoint deve operar em `O(1)`.

