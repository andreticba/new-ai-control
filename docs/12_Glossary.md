<!-- 12_Glossary.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 12. Glossary

Este glossário unifica os termos técnicos e de negócio para comunicação clara entre desenvolvedores e stakeholders.

- **Tenant:** A empresa ou inquilino que contrata a plataforma. Todos os dados da plataforma orbitam de forma criptograficamente isolada sob um Tenant.
- **Usuário Final:** O consumidor ou cliente do *Tenant*. É o verdadeiro dono dos dados sensíveis trafegados na plataforma.
- **Data Vault (Cofre de Dados):** Na nossa arquitetura, refere-se ao mecanismo que ofusca, fragmenta e criptografa dados para garantir rastreabilidade, em conformidade com leis como a LGPD.
- **AI Ingestion (Ingestão de IA):** O processo de coletar dados estruturados e desestruturados, formatá-los (como Embeddings) e direcioná-los aos motores de LLM de maneira automatizada e anonimizada.
- **Webhook:** Um mecanismo pelo qual provedores externos (ex: APIs do WhatsApp, plataformas parceiras) notificam nosso sistema em tempo real sobre eventos, através de requisições HTTP POST.
- **Agnosticismo (Hardware/Domínio):** O princípio de engenharia no qual o software não pode ser permanentemente "amarrado" a serviços proprietários (ex: não usar funções fechadas da AWS) ou a nichos comerciais (ex: clínicas médicas).

