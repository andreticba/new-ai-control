<!-- 01-product/04_whatsapp.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

# 04. Integração WhatsApp e CRM Omnichannel
**Público-alvo:** Stakeholders, Novos PMs  
**Tempo de Leitura:** 5 min

Nossa plataforma não é dona da infraestrutura de telecomunicações do WhatsApp. Atuamos orquestrando o fluxo usando o Gateway Evolution API, que atua como nosso SaaS terceirizado para disparos e recebimentos de mensagens de vários números simulando sessões web.

## O Pipeline e Isolamento de Multitenancy ✅
O que acontece quando o Usuário Final manda um "Bom dia" no WhatsApp?

1. **Webhook (Gateway):** O gateway recebe e avisa nossa plataforma disparando para a URL unificada (`/api/v1/webhook/whatsapp`). Para que não trave a interface, o servidor captura essa notificação super-rápida e envia o "pacote" cru para nossa fila de processamento assíncrona (Celery).
2. **Separação de Águas (Isolamento de Organization):** A nossa retaguarda examina as credenciais do Gateway. Como ele sabe de qual clínica (Tenant) o celular enviou? Nós forçamos o Gateway a usar nomes de "Instâncias" codificados com o slug da organização (`ai_control_{org_slug}`). O processo "quebra" a string, descobre que é da Organização Alfa e encaminha a conversa.
3. **Contato e Websockets:** O Contato é registrado. A conversa é ativada e disparada para o front-end via Mensageria em Tempo Real (Websockets via `django-channels`) permitindo que o PM ou desenvolvedor acompanhe num console em tempo real. PIIs (como números no log) sofrem sanitização pesada neste fluxo (ex: mascarando o celular com asteriscos).

## Conflito Arquitetural: Squads vs WhatsApp 🟡
Uma limitação arquitetural atual documentada no inventário: O fluxo de recepção de WhatsApp ocorre de maneira linear a nível de Organização e de Contato. *Ainda não implementamos no código real* um funil onde a pessoa manda mensagem e essa conversa seja alocada imediatamente a um Squad ou Projeto interno, barrando outros atendentes de enxergá-la. Hoje, o roteamento da conversa para a IA (`AIIngestionDelegator`) ou para diferentes abas de Atendimento (humanos baseados em seu Depto) é parte do nosso **Design de Referência**, precisando de lógicas adicionais de negócio no CRM.
