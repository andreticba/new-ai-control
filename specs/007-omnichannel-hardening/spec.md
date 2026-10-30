<!-- spec.md | Vitalia SDD v0.6.0 | 21-10-2026 20:35:00(GMT-04:00) -->
> **spec.md | Vitalia SDD v0.6.0 | 21-10-2026 20:35:00(GMT-04:00)**

# Especificação de Funcionalidade: Hardening, Segurança & Estabilização do Omnichannel

**Data:** 21-10-2026 20:35(GMT-04:00)  
**Feature:** `007-omnichannel-hardening`  
**Status:** ESPECIFICAÇÃO_APROVADA (Brainstorming Concluído | Decisões D1:C, D2:A, D3:A)  
**Artefatos Relacionados:**
- [research-brainstorming.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/research-brainstorming.md) (Síntese do Brainstorming Socrático & Diagnóstico E2E)
- [research.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/research.md) (Decisões Técnicas Fundamentadas, Fontes Autoritativas P03 & Catálogo Oficial de Eventos da Evolution API v2)
- [data-model.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/data-model.md) (Regras de Contact Novo vs. Contact com Usuário, Soft FKs & Máquina de Estados)
- [contracts/hardening_api_contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/contracts/hardening_api_contracts.md) (Contratos REST DRF, Webhook Sanitizado, WebSocket & Celery)
- [checklists/requirements.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/checklists/requirements.md) (Critérios de Qualidade da Spec)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

Durante os testes reais ponta-a-ponta (E2E) com envio e recebimento de mensagens a partir de smartphones pessoais conectados via **Evolution API v2**, foram diagnosticados comportamentos críticos de segurança, performance de logs e inconsistência funcional no módulo Omnichannel:

1. **Vazamento de Segredos e PII em Logs HTTP e da Aplicação:**
   - A configuração legada passava a `apikey` como parâmetro de query string (`?apikey=...`), fazendo com que servidores HTTP (Daphne/Django) gravassem a chave mestra em texto plano a cada requisição.
   - O receptor de webhooks em `core/api/v1/views/webhook_whatsapp.py` ao logar eventos desconhecidos imprimia a chave `'destination'` (com a apikey na URL), a chave `'apikey'` (token da instância) e o telefone real do remetente (`'sender'`), configurando vazamento de credenciais e de dados pessoais (PII / LGPD).
   - O WebSocket do frontend conectava passando o token JWT do operador na query string (`/ws/omnichannel/?token=...`), expondo o Bearer token no terminal do Daphne.

2. **Saturação e Flood de Logs no Celery (Telemetria Inútil):**
   - Eventos de alta frequência do WhatsApp (`presence.update`, `contacts.update`, `chats.update`, `chats.upsert`) estavam sendo aceitos na View e despachados como tasks para o Celery, gerando dezenas de tarefas vazias por minuto e crescendo os logs descontroladamente.

3. **Rejeição de Eventos do Catálogo Evolution API v2 (`qrcode.updated` e outros):**
   - A Evolution API v2 emite eventos estruturados como `qrcode.updated`, `messages.update`, `messages.edited`, `messages.delete`. O gateway rejeitava eventos legítimos como não suportados por falta de ampliação do catálogo.

4. **Bloqueio de Envio para Contatos Sem Organização e "Network Error":**
   - Quando um número desconhecido entra em contato, ele é cadastrado como lead inicial sem vínculo prévio a uma organização (`organization_id = None`).
   - A View de mensagens [`omnichannel/api/views.py`](file:///home/andre/projetos/assistidos/ai-control/omnichannel/api/views.py) exigia estritamente `conversation__organization_id__in=authorized_orgs`, tornando impossível ao operador enviar mensagens para leads globais.
   - **Regra de Negócio Soberana:** Se a conversa for de um `Contact` novo (lead externo sem conta no sistema), ela pode não ter organização (`organization_id=null`), sendo atendida por operadores qualificados. No entanto, se o contato possuir um `User` do sistema relacionado a ele, o filtro de organização é **mandatório** e deve ser estritamente aplicado conforme as memberships desse usuário.
   - A política de CORS (`CORS_ALLOWED_ORIGINS`) continha apenas `http://localhost:3000`, disparando `Network Error` via Axios quando acessado por `http://127.0.0.1:3000`.

5. **Falha Silenciosa de Despacho Outbound e Falta de Confirmação da Evolution API:**
   - Em caso de falha de rede ou rejeição pela Evolution API, o `MessageDispatchService` capturava a exceção silenciosamente em `except Exception` e salvava a mensagem no banco como `delivery_status=SENT` com ID fictício (`outbound_...`).
   - **Diretriz Mandatória do Usuário (Decisão D2: A):** A mensagem enviada pelo atendente **SÓ DEVE APARECER NO CHAT** após a confirmação inequívoca de recebimento e despacho pela Evolution API. Se a Evolution falhar, o sistema deve acusar o erro e não renderizar falso sucesso.

6. **Ciclo de Vida do Modal do WhatsApp:**
   - O modal de pareamento não fecha sozinho quando a conexão é estabelecida (`state === 'open'`) e não recupera adequadamente caso o operador clique em atualizar o QR Code.

---

## 2. Requisitos Funcionais (FR-xxx)

### FR-001: Mascaramento Preventivo de Credenciais e Higienização de Logs HTTP
- **Descrição:** O sistema **MUST** implementar um middleware/filtro de segurança no Django/ASGI (`SensitiveLogMaskingMiddleware`) que intercepte saídas de log de requisições HTTP e mascare qualquer parâmetro contendo chaves como `apikey`, `token`, `password`, `secret` (substituindo por `[REDACTED]`). O receptor de webhook **MUST** extrair credenciais preferencialmente do cabeçalho HTTP `apikey`, aceitando a query string apenas como fallback legado e sanitizando-a antes de qualquer processamento ou log.
- **Impacto ao Usuário (P02):** Garante conformidade com o Princípio P12 (Segurança de Agente e Credenciais), impedindo que senhas e chaves de integração vazem em consoles de desenvolvedores, capturas de tela ou logs de monitoramento.
- **Conformidade Constitucional (P00-P17):** P07 (Privacy by Design), P12 (Agent Security).

### FR-002: Ampliação do Catálogo de Eventos da Evolution API v2 e Silent Drop $O(1)$ de Telemetria
- **Descrição:** 
  1. A `WebhookGatewayView` **MUST** ampliar a lista de eventos acionáveis (`ACTIONABLE_EVENTS`) com base na especificação oficial da Evolution API v2:
     - `messages.upsert`: Criação de mensagem inbound no banco e emissão via WebSocket;
     - `messages.update`: Atualização do status de entrega (`DELIVERED`, `READ` / checks azuis);
     - `messages.edited`: Atualização do conteúdo textual de mensagens editadas;
     - `messages.delete`: Marcação de mensagem revogada/apagada na timeline;
     - `qrcode.updated`: Broadcast em tempo real do novo QR Code Base64 via WebSocket para o modal de pareamento;
     - `connection.update`: Atualização de status da conexão WhatsApp com debounce no `AuditLog`.
  2. A view **MUST** incluir os eventos contínuos de telemetria em `SILENT_DROP_EVENTS`: `presence.update`, `contacts.set`, `contacts.update`, `contacts.upsert`, `chats.set`, `chats.update`, `chats.upsert`, `chats.delete`, `application.startup` e `call`. Tais eventos **MUST** receber resposta `200 OK` imediata em tempo $O(1)$ na borda da View, **SEM** enfileirar tarefas no Celery.
  3. No tratamento de qualquer evento descartado ou desconhecido, o log de aviso **MUST** sanitizar estritamente o payload, removendo as chaves `destination`, `apikey`, `sender` e qualquer dado identificador de PII.
- **Impacto ao Usuário (P02):** Elimina o flood infinito de logs no terminal do Celery, reduz consumo de CPU e memória do worker em até 80% e permite o pareamento contínuo de QR Code em tempo real com ticks de leitura precisos.
- **Conformidade Constitucional (P00-P17):** P01 (Pipeline Inviolability), P04 (Performance e Estabilidade).

### FR-003: Governança de Organização: Associação à Organização Padrão para Contatos Novos e Isolamento Multitenant Estrito (P07)
- **Descrição:**
  1. **Regra de Contato Novo (Sem Usuário Prévio):** Quando uma mensagem chegar de um número novo (sem usuário prévio vinculado no sistema), o sistema **MUST** associar automaticamente o novo `Contact` e a `Conversation` à **Organização Padrão da Plataforma** (determinada via configuração do sistema ou pela organização proprietária da instância WhatsApp que admitiu o contato). O campo `organization_id` **NUNCA DEVE SER NULO**, garantindo integridade referencial total e estrita conformidade com o Princípio P07 (Multitenancy Estrito).
  2. **Atendimento pelos Operadores Autorizados:** Operadores autenticados pertencentes à organização padrão da plataforma (ou com perfil global de suporte/administração) **MUST** ter permissão para visualizar, listar e responder a essas conversas sem que ocorra erro 401 ou 404.
  3. **Regra de Contato com Usuário Vinculado:** Se o `Contact` possuir um `User` do sistema relacionado a ele (mesmo telefone, e-mail ou vínculo corporativo pré-existente), a conversa **MUST** pertencer obrigatoriamente à organização à qual esse usuário está vinculado. O filtro de organização **MUST** ser estritamente aplicado (`organization_id__in=authorized_orgs`), proibindo operadores de outras organizações de visualizar ou interagir com essa conversa.
  4. **Despacho Outbound Conforme a Instância:** No envio outbound para o contato, o sistema **MUST** validar o acesso do operador com filtro mandatório de `organization_id` e despachar a mensagem através da instância WhatsApp vinculada à organização.
- **Impacto ao Usuário (P02):** Permite acolher e atender imediatamente contatos e leads novos que chegam espontaneamente pelo WhatsApp sem travar o atendimento com erros de permissão ou "Network Error", mantendo o isolamento multi-tenant blindado em 100% das consultas de banco.
- **Conformidade Constitucional (P00-P17):** P00 (Human Wellbeing First), P02 (User-Centric Validation), P07 (Isolamento Multitenant Estrito com user_id e organization_id mandatórios).

### FR-004: Despacho Outbound com Confirmação Estrita da Evolution API v2 (Decisão D2: A)
- **Descrição:**
  1. Ao enviar mensagem pelo chat ([`omnichannel/services/message_dispatch_service.py`](file:///home/andre/projetos/assistidos/ai-control/omnichannel/services/message_dispatch_service.py)), a chamada REST para a Evolution API (`POST /message/sendText/{instance}`) **MUST** ser validada de forma síncrona quanto ao seu status HTTP e corpo da resposta.
  2. A mensagem no banco de dados **SÓ DEVE SER CRIADA** com `delivery_status=SENT` e emitida via WebSocket caso a Evolution API retorne sucesso (`status_code == 200/201`) contendo o identificador real da mensagem do WhatsApp (`key.id`).
  3. Caso a Evolution API retorne erro (timeout > 5s, instância desconectada ou erro de payload), o serviço **MUST** propagar uma exceção de domínio explícita (`MessageDispatchError`), e a View DRF **MUST** responder com `HTTP 502 Bad Gateway` ou `HTTP 400 Bad Request` detalhando o motivo.
  4. O frontend **NÃO DEVE** exibir a mensagem na timeline antes de receber a resposta de sucesso da API (proibição de renderização otimista prematura). O chat **MUST** manter o estado de carregamento (`isSending`) e, caso a requisição falhe, manter o texto digitado na caixa de entrada e exibir toast de erro explicativo.
- **Impacto ao Usuário (P02):** Elimina a falsa impressão de que a mensagem foi entregue ao cliente quando a instância do WhatsApp estiver desconectada ou com instabilidade, garantindo transparência total ao operador.
- **Conformidade Constitucional (P00-P17):** P01 (Pipeline Inviolability), P02 (User-Centric Validation).

### FR-005: Resolução de Conectividade Cross-Origin (CORS) e Blindagem de Token em WebSockets (Decisão D3: A)
- **Descrição:**
  1. A configuração `CORS_ALLOWED_ORIGINS` no backend **MUST** incluir nativamente tanto `http://localhost:3000` quanto `http://127.0.0.1:3000`, bem como respeitar origens configuradas via variável de ambiente (`CORS_ALLOWED_ORIGINS_ENV`).
  2. A conexão WebSocket em [`use-omnichannel-socket.ts`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/hooks/use-omnichannel-socket.ts) e [`OmnichannelConsumer`](file:///home/andre/projetos/assistidos/ai-control/omnichannel/consumers/omnichannel_consumer.py) **MUST** permitir autenticação pelo protocolo de subprotocolo WebSocket (`Sec-WebSocket-Protocol: Bearer, <token>`) ou manter a query string protegida contra log no servidor ASGI.
- **Impacto ao Usuário (P02):** Elimina erros de "Network Error" causados por disparidade de hostname local e protege o token JWT contra exposição em logs.
- **Conformidade Constitucional (P00-P17):** P12 (Agent Security).

### FR-006: Ciclo de Vida Reativo do Modal de Pareamento WhatsApp
- **Descrição:**
  1. O modal [`WhatsAppConnectionModal`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/components/omnichannel/whatsapp-modal.tsx) **MUST** monitorar ativamente a transição para o estado `open` (conectado). Ao detectar a conexão com sucesso, o modal **MUST** exibir indicador de sucesso (badge verde) e fechar automaticamente após um delay sutil de 1.5 segundos (`auto-close`).
  2. O botão "Atualizar QR Code" **MUST** invalidar o cache de consulta do TanStack Query, limpar estados de erro residuais e solicitar um novo código sem requerer fechamento ou recarregamento manual da página.
- **Impacto ao Usuário (P02):** Proporciona uma experiência limpa, intuitiva e sem fricção no pareamento do WhatsApp do operador.
- **Conformidade Constitucional (P00-P17):** P02 (User-Centric Validation).

### FR-007: Debounce e Estabilização de Auditoria de Conexão no `AuditLog`
- **Descrição:** O método `process_connection_update` em `core/services/whatsapp_service.py` **MUST** implementar um mecanismo de verificação de idempotência/debounce (via cache Redis ou consulta de estado anterior) para gravar registros em `AuditLog` exclusivamente quando houver uma mudança real e consolidada de estado (`open` $\leftrightarrow$ `close`), impedindo que oscilações temporárias de rede gravem centenas de registros duplicados na tabela imutável.
- **Impacto ao Usuário (P02):** Mantém a trilha de auditoria limpa, auditável e evita desperdício de armazenamento no PostgreSQL.
- **Conformidade Constitucional (P00-P17):** P14 (Full Audit Trail).

### FR-008: Governança de Arquitetura Limpa e Princípio de Responsabilidade Única (SRP - Anti-Monólitos)
- **Descrição:** Todos os componentes novos ou refatorados nesta spec **MUST** obedecer estritamente ao Princípio de Responsabilidade Única (Single Responsibility Principle - SRP), evitando o surgimento de monólitos extensos no backend ou frontend:
  1. *Backend (DRF & Service Layer):* As Views DRF **MUST** permanecer magras (< 35 linhas por método), delegando 100% da lógica de negócio e regras transacionais para serviços especializados (`MessageDispatchService`, `InstanceService`, `WebhookIngestionService`). Filtros de logging e middlewares (`SensitiveLogMaskingMiddleware`) devem ser desacoplados em módulos utilitários de segurança específicos.
  2. *Frontend (React 19 & Next.js 16):* Componentes de UI **MUST** ter escopo estrito (< 120 linhas), segregando estado complexo e efeitos colaterais em Custom Hooks dedicados (`useWhatsAppInstance`, `useOmnichannelSocket`, `useOmnichannel`). É expressamente vedado misturar chamadas HTTP diretas ou manipulação de sockets dentro de componentes puramente visuais.
- **Impacto ao Usuário (P02):** Garante alta manutenibilidade, testabilidade isolada e previne regressões em futuras evoluções da plataforma.
- **Conformidade Constitucional (P00-P17):** P01 (Pipeline Inviolability), P04 (GMT-04:00 & Qualidade Estrutural).

---

## 3. Success Criteria (Critérios Mensuráveis)

- **SC-001 (Zero Vazamento de Segredos em Logs):** 100% das saídas de log HTTP e de aplicação não contêm strings de `apikey`, senhas de banco/redis ou JWT em texto plano, comprovado por testes automatizados de regex.
- **SC-002 (Silenciamento de Telemetria no Celery):** Disparo de eventos `presence.update` e `contacts.update` resulta em 0 (zero) tarefas enfileiradas no Celery e tempo de resposta da View $\le 10\text{ms}$.
- **SC-003 (Envio Garantido com Confirmação Evolution):** Em 100% dos testes de envio manual, nenhuma mensagem é persistida no banco ou exibida no chat como `SENT` se a Evolution API retornar código de erro ou se a instância estiver desconectada.
- **SC-004 (Interoperabilidade CORS):** Requisições provenientes de `http://localhost:3000` e `http://127.0.0.1:3000` respondem com cabeçalhos CORS válidos e zero ocorrências de `Network Error`.
- **SC-005 (Atendimento a Contatos Novos via Organização Padrão):** 100% dos novos contatos sem usuário prévio são automaticamente associados à organização padrão da plataforma (`organization_id` válido e não-nulo), permitindo atendimento imediato pelos operadores autorizados enquanto todas as queries ao banco mantêm os filtros combinados de multitenancy estrito (P07).
- **SC-006 (Auto-close de Pareamento):** O modal de conexão fecha automaticamente em até 2 segundos após a leitura e validação do QR Code pelo WhatsApp.
- **SC-007 (Conformidade com SRP e Limites Anti-Monólito):** 100% dos arquivos criados ou modificados respeitam o limite de responsabilidade única, com Views DRF < 35 linhas por método e componentes de UI desacoplados de regras de transporte.

---

## 4. User Scenarios & Acceptance Criteria (Given / When / Then)

### Cenário 1: Envio de Mensagem para Contato Novo Vinculado à Organização Padrão
- **Given** que um novo número de WhatsApp enviou mensagem e foi registrado como contato novo sem `User` vinculado e associado à Organização Padrão da plataforma (`organization_id = default_org.id`),
- **When** o atendente humano com permissão na organização padrão abre a conversa no chat, digita "Olá, como posso ajudar?" e clica em Enviar,
- **Then** o backend autoriza a operação com validação estrita de multitenant (`organization_id`), despacha a mensagem via Evolution API usando a instância ativa vinculada à organização, recebe confirmação com `key.id`, salva a mensagem como `SENT` e a devolve para renderização no chat.

### Cenário 2: Bloqueio Multi-Tenant para Contato com Usuário Vinculado a Outra Organização
- **Given** que um contato de WhatsApp está associado a um `User` do sistema pertencente exclusivamente à organização `Universidade Federal Demo`,
- **When** um operador pertencente exclusivamente à `Empresa Demo Ltda` tenta consultar ou enviar mensagem para essa conversa,
- **Then** o backend rejeita a requisição com `HTTP 404 Not Found` ou `HTTP 403 Forbidden`, impedindo vazamento de dados entre tenants.

### Cenário 3: Falha de Envio por Instância WhatsApp Desconectada
- **Given** que a instância na Evolution API está desconectada ou indisponível,
- **When** o atendente humano tenta enviar uma mensagem,
- **Then** a Evolution API responde com erro, o backend não grava a mensagem no banco, retorna `HTTP 502 Bad Gateway` com a mensagem de erro, o frontend exibe um toast explicativo e o texto digitado permanece preservado na caixa de entrada sem criar balão falso na timeline.

### Cenário 4: Pareamento com Auto-close Reativo
- **Given** que o atendente abre o modal de conexão do WhatsApp e o QR Code é exibido,
- **When** o operador aponta a câmera do celular e autentica a conexão via WhatsApp Web,
- **Then** o webhook recebe `connection.update` com `state: open`, a interface atualiza o badge para "Conectado" em verde e o modal se fecha automaticamente em 1.5s sem ação adicional.

### Cenário 5: Blindagem contra Vazamento de API Key no Receptor de Webhooks
- **Given** que uma requisição externa chega ao webhook contendo `?apikey=minha_chave_secreta` ou cabeçalho `apikey`,
- **When** o servidor HTTP e o Django processam a requisição e emitem logs,
- **Then** o middleware mascara a query string para `?apikey=[REDACTED]` em todos os logs de console e nenhum evento rejeitado imprime a apikey ou número de telefone no logger.
