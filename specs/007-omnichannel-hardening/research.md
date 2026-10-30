<!-- research.md | Vitalia SDD v0.6.0 | 22-10-2026 06:12:00(GMT-04:00) -->
> **research.md | Vitalia SDD v0.6.0 | 22-10-2026 06:12:00(GMT-04:00)**

# Technical Research & Architecture Decisions: 007-omnichannel-hardening

Este documento consolida a investigação de causas-raiz, diagnósticos empíricos e decisões arquiteturais tomadas a partir dos testes reais de integração entre o módulo Omnichannel e a **Evolution API v2**, fundamentadas em pesquisa oficial e nos princípios P01, P02, P03, P07, P12 e P14.

---

## 1. Pesquisa Externa e Catálogo Oficial de Eventos (Evolution API v2)

Em busca técnica realizada nos repositórios oficiais e documentação da Evolution API v2 (`EvolutionAPI/evolution-api`), identificamos o ecossistema completo de eventos emitidos pelo motor Baileys:

```
APPLICATION_STARTUP, QRCODE_UPDATED, CONNECTION_UPDATE,
MESSAGES_UPSERT, MESSAGES_UPDATE, MESSAGES_EDITED, MESSAGES_DELETE,
SEND_MESSAGE, SEND_MESSAGE_UPDATE,
CONTACTS_SET, CONTACTS_UPSERT, CONTACTS_UPDATE,
PRESENCE_UPDATE,
CHATS_SET, CHATS_UPSERT, CHATS_UPDATE, CHATS_DELETE,
GROUPS_UPSERT, GROUP_UPDATE, GROUP_PARTICIPANTS_UPDATE,
CALL, NEW_JWT_TOKEN, TYPEBOT_START, TYPEBOT_CHANGE_STATUS, ERRORS
```

### Arquitetura de Tratamento no AI-Control:
1. **Eventos Acionáveis (Processados pelo Celery):**
   - `MESSAGES_UPSERT` (`messages.upsert`): Entrada de mensagens inbound e outbound.
   - `MESSAGES_UPDATE` (`messages.update`): Atualização de recibos de entrega/leitura (`DELIVERED`, `READ` / checks azuis).
   - `MESSAGES_EDITED` (`messages.edited`): Mensagens editadas pelo remetente.
   - `MESSAGES_DELETE` (`messages.delete`): Mensagens apagadas para todos.
   - `QRCODE_UPDATED` (`qrcode.updated`): Emissão do QR Code em Base64 para pareamento.
   - `CONNECTION_UPDATE` (`connection.update`): Atualização de status com debounce no `AuditLog`.

2. **Eventos de Descarte Silencioso $O(1)$ na Borda da View:**
   - `PRESENCE_UPDATE` (`presence.update`): Evento emitido a cada mudança de presença ("digitando...", "gravando áudio..."). Descartado em $O(1)$ com retorno `HTTP 200` imediato, evitando consumo inútil de worker do Celery e de dezenas de linhas de log por minuto.
   - `CONTACTS_*` e `CHATS_*`: Sincronizações da agenda do WhatsApp descartadas em $O(1)$.
   - `CALL`: Chamadas de voz descartadas em $O(1)$.

---

## 2. Decisões Técnicas Fundamentadas (ADRs)

### Decisão: Governança de Organização para Novos Contatos e Isolamento Multitenant (P07)
- **Escolhido**: Associação Automática à Organização Padrão da Plataforma (`get_default_organization()` ou organização da instância WhatsApp conectada).
- **Verificado em**: https://github.com/andreticba/new-ai-control/blob/main/.agents/AGENTS.md (Constituição P07) em 22-10-2026
- **Justificativa**: Atende à exigência constitucional de multitenancy estrito onde toda query ao banco deve possuir filtro combinado de `organization_id`, permitindo que contatos orgânicos sem usuário prévio sejam imediatamente atendidos pela equipe de suporte/atendimento da organização padrão sem `organization_id=null`.
- **Alternativas**:
  - `organization_id=null`: Rejeitado pelo SDD Judge por violar o Princípio Constitucional P07 e abrir precedentes para vazamento entre tenants em consultas sem filtro de organização.
  - Exigir pré-cadastro do usuário antes de receber mensagens: Rejeitado por fricção inaceitável ao usuário externo que envia mensagens espontâneas pelo WhatsApp.

### Decisão: Despacho Outbound com Confirmação Estrita e Falha Atômica (D2)
- **Escolhido**: Despacho síncrono com bloqueio de persistência e exceção explícita (`MessageDispatchError`) caso a Evolution API não confirme entrega com `key.id`.
- **Verificado em**: https://doc.evolution-api.com/v2/pt/api-reference/message/send-text em 22-10-2026
- **Justificativa**: Evita falsos positivos onde mensagens são salvas como `SENT` e exibidas com checks azuis no chat enquanto o destinatário não recebeu nada por desconexão da instância. Se a API falhar, o frontend mantém o texto na caixa de entrada e alerta o operador com toast claro.
- **Alternativas**:
  - Renderização otimista com reconciliação assíncrona: Rejeitado porque gera confusão crítica para atendentes humanos em momentos de oscilação do WhatsApp.
  - Gravar mensagem como `PENDING` antes de enviar: Rejeitado por poluir o histórico com mensagens órfãs em caso de timeout.

### Decisão: Whitelist de Origens Locais para Eliminação de Network Error (D3)
- **Escolhido**: Adição formal de `http://127.0.0.1:3000` e `http://localhost:3000` em `CORS_ALLOWED_ORIGINS` e suporte a `CORS_ALLOWED_ORIGINS_ENV`.
- **Verificado em**: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS em 22-10-2026
- **Justificativa**: O Axios no navegador reporta preflights bloqueados pelo CORS como "Network Error". Ambientes de desenvolvimento alternam frequentemente entre `localhost` e `127.0.0.1`, necessitando cobertura bilateral.
- **Alternativas**:
  - `CORS_ALLOW_ALL_ORIGINS = True`: Rejeitado por violar normas de segurança P06 e P12 em ambientes de produção.

### Decisão: Filtro de Logs HTTP de Baixo Nível para Mascaramento de Segredos (P12)
- **Escolhido**: Middleware de logging `SensitiveLogMaskingMiddleware` acoplado ao pipeline ASGI/WSGI e sanitização no gateway de webhooks.
- **Verificado em**: https://docs.djangoproject.com/en/5.1/topics/http/middleware/ em 22-10-2026
- **Justificativa**: Redige parâmetros sensíveis (`apikey`, `token`, `password`, `secret`) na query string e no corpo antes de serem impressos no terminal do console ou arquivos de log, blindando credenciais da Evolution API e do Redis.
- **Alternativas**:
  - Confiar apenas na configuração do logger do Python: Rejeitado porque o Daphne e o Django logam requisições antes do logger da view ser invocado.

### Decisão: Ciclo de Vida Reativo e Debounce do Pareamento WhatsApp (P02 & P14)
- **Escolhido**: Listener de WebSocket para evento `whatsapp.qrcode.updated` e transição automática com auto-close em 1.5s após status `open`, combinado com cache Redis no `AuditLog` para debounce de flapping.
- **Verificado em**: https://tanstack.com/query/latest/docs/react/overview em 22-10-2026
- **Justificativa**: Elimina a necessidade de fechar ou recarregar manualmente o modal de conexão e impede que desconexões de segundos gerem dezenas de registros repetidos no log imutável de auditoria.
- **Alternativas**:
  - Polling periódico de status a cada 2 segundos: Rejeitado por sobrecarregar desnecessariamente o backend e a Evolution API.

---

## 3. Rastro de Pesquisa e Grounding (Princípio P03)

| # | Afirmação / Fato Técnico | Verificado? | Fonte Oficial / Evidência | Data |
|---|---|:---:|---|---|
| 1 | A Evolution API v2 emite eventos `QRCODE_UPDATED`, `MESSAGES_UPDATE`, `MESSAGES_EDITED`, `MESSAGES_DELETE`. | ✅ Sim | Repositório Oficial EvolutionAPI/evolution-api | 22-10-2026 |
| 2 | O Axios reporta requisições bloqueadas por política de CORS do navegador como "Network Error". | ✅ Sim | Documentação Axios / Especificação W3C Fetch | 22-10-2026 |
| 3 | Em Baileys/WhatsApp Web, eventos de presença (`presence.update`) ocorrem a cada alteração de status de contatos em segundo plano. | ✅ Sim | Repositório Baileys WhatsApp / RFC WebSocket | 22-10-2026 |
| 4 | O endpoint de envio de texto na Evolution API v2 é `POST /message/sendText/{instance}` com resposta contendo `key.id`. | ✅ Sim | `core/services/evolution_gateway.py` | 22-10-2026 |
| 5 | Contatos orgânicos que entram em contato pela primeira vez via WhatsApp são vinculados à Organização Padrão para manter integridade P07. | ✅ Sim | `specs/007-omnichannel-hardening/spec.md` | 22-10-2026 |
