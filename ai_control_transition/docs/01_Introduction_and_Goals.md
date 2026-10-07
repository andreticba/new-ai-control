<!-- 01_Introduction_and_Goals.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 1. Introduction and Goals

## 1.1 Visão Geral do Produto
O projeto consiste no desenvolvimento de uma **Plataforma Data Vault Agnóstica**. Seu objetivo principal é fornecer uma infraestrutura robusta, isolada e segura para armazenamento e processamento de dados (Data Vault), garantindo total soberania, rastreabilidade e privacidade sobre as informações.

Inicialmente concebida no contexto de uma plataforma de saúde, esta arquitetura foi intencionalmente desacoplada para operar como um **PaaS (Platform as a Service) Agnóstico**. Dessa forma, ela pode atender a diversos tipos de negócios (educação, finanças, e-commerce, saúde) sem acoplamento a regras de negócio restritas de um único domínio.

## 1.2 Objetivos de Negócio
- **Soberania do Dado:** Garantir que cada *Tenant* (inquilino/empresa) possua isolamento criptográfico e lógico sobre seus dados e os dados de seus respectivos usuários finais.
- **Flexibilidade Multidomínio:** Servir de espinha dorsal para qualquer aplicação que exija alta segurança de dados, gestão de consentimento e esteira de ingestão de IA (AI Ingestion).
- **Adequação Regulatória By Design:** Cumprir com LGPD, GDPR, HIPAA (quando aplicável à saúde) e outras normativas de privacidade, automatizando processos de anonimização e direito ao esquecimento.

## 1.3 Casos de Uso Principais
1. **Onboarding de Tenants:** Criação de novos inquilinos no sistema com isolamento automático de chaves criptográficas.
2. **Ingestão de Dados via Webhooks:** Recebimento assíncrono de grandes volumes de dados (ex: WhatsApp Webhooks, APIs REST) via Gateway, com enfileiramento em Message Brokers.
3. **Gestão de Consentimento e Privacidade:** Usuários finais gerenciando o que pode ser acessado, armazenado ou esquecido.
4. **Delegação AI:** Roteamento de intents e mensagens via IA sem exposição de dados sensíveis na camada de LLM.

## 1.4 Stakeholders
| Stakeholder | Papel e Expectativas |
|-------------|----------------------|
| **Mantenedores da Plataforma** | Alta disponibilidade, baixo acoplamento, facilidade de expansão e deploy. |
| **Tenants (Clientes B2B)** | Segurança, isolamento de dados, APIs performáticas e ausência de vazamento de informações. |
| **Usuários Finais (B2B2C)** | Privacidade absoluta, transparência no uso dos dados e controle (Opt-in/Opt-out). |

