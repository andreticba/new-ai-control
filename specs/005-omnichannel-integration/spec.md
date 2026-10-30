<!-- spec.md | Vitalia SDD v0.6.0 | 20-10-2026 17:31:00(GMT-04:00) -->
> **spec.md | Vitalia SDD v0.6.0 | 20-10-2026 17:31:00(GMT-04:00)**

# Especificação de Funcionalidade: Atendimento Omnichannel, Integração WhatsApp, Funil B2B2C e IA Copiloto

**Data:** 20-10-2026 17:31(GMT-04:00)  
**Feature:** `005-omnichannel-integration`  
**Status:** ESPECIFICAÇÃO_APROVADA (SDDJudge: PASS | Preservação Estrita da Infraestrutura Ativa)  
**Artefatos Relacionados:**
- [research.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/research.md) (Decisões Técnicas Fundamentadas & Fontes Autoritativas P03)
- [data-model.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/data-model.md) (Entidades Alinhadas a omnichannel/models.py, Soft FKs & Máquina de Estados)
- [contracts/omnichannel_api_contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/contracts/omnichannel_api_contracts.md) (Contratos REST DRF, Webhook Canônico, WebSocket & Celery)
- [quickstart.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/quickstart.md) (Guia Executável End-to-End com curl)
- [checklists/requirements.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/checklists/requirements.md) (Critérios de Qualidade da Spec)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

O ecossistema **AI Control - Agentes Inteligentes** é uma plataforma multi-tenant de automação e atendimento com IA. Atualmente, o backend possui uma infraestrutura operacional ativa e funcional de comunicação com o WhatsApp via **Evolution API v2**, composta por:
- Receptor canônico de webhooks em [core/api/v1/views/webhook_whatsapp.py](file:///home/andre/projetos/assistidos/ai-control/core/api/v1/views/webhook_whatsapp.py) atendendo em `/api/v1/webhook/whatsapp/`;
- Gateway de instâncias e conexão Baileys QR Code em [core/services/evolution_gateway.py](file:///home/andre/projetos/assistidos/ai-control/core/services/evolution_gateway.py);
- Orquestração de mensageria assíncrona em [core/services/whatsapp_service.py](file:///home/andre/projetos/assistidos/ai-control/core/services/whatsapp_service.py) e [core/tasks/whatsapp_tasks.py](file:///home/andre/projetos/assistidos/ai-control/core/tasks/whatsapp_tasks.py);
- Modelos relacionais com blind indexing de telefone em [omnichannel/models.py](file:///home/andre/projetos/assistidos/ai-control/omnichannel/models.py).

O objetivo desta especificação **NÃO É RECRIAR** a infraestrutura existente, mas sim **CONECTAR e COMPLETAR** os elos faltantes para viabilizar a experiência do operador humano e do cliente final:
1. **Preservação e Aproveitamento Integral da Stack Vigente:** Manter o endpoint de webhook `/api/v1/webhook/whatsapp/`, as variáveis `WHATS_GT_*`, os modelos de `omnichannel` e a suíte de 53 testes existentes sem qualquer quebra ou regressão;
2. **Endpoints REST de Consulta e Controle de Atendimento:** Prover views DRF para alimentar o frontend (listagem de conversas por status/filtro, histórico paginado de mensagens e ação atômica de Takeover `ACTIVE_AI` $\leftrightarrow$ `ACTIVE_HUMAN`);
3. **Modo IA Copiloto Contínuo (Agent Assist):** Quando o atendente humano assume a conversa (`ACTIVE_HUMAN`), a IA suspende o envio automático de mensagens ao WhatsApp e passa a atuar exclusivamente como copiloto gerando sugestões de resposta em tempo real (`CopilotDraft`) via WebSocket;
4. **Interface Clone do WhatsApp Web no Frontend:** Criar a interface responsiva em viewport fixo (`h-dvh overflow-hidden`) no React 19 / Next.js 16 (atualmente inexistente no frontend), com navegação em pilha para dispositivos móveis e zero rolagem indesejada na janela.

---

## 2. Requisitos Funcionais (FR-xxx)

### FR-001: Ingestão Idempotente de Webhooks Inbound (WhatsApp Evolution API v2)
- **Descrição:** O sistema **MUST** expor um endpoint seguro para recebimento de eventos de mensageria da Evolution API v2 (`messages.upsert`). O processamento do webhook **MUST** extrair o identificador externo da mensagem (`data.key.id`) e verificar a sua existência prévia no banco de dados. Caso a mensagem já tenha sido registrada, o payload **MUST** ser descartado com retorno HTTP `200 OK` (idempotência). Mensagens válidas **MUST** ser persistidas no estado transitório e delegadas imediatamente para uma tarefa assíncrona do Celery (`process_inbound_message_task`), liberando o webhook HTTP em menos de 200ms.
- **Impacto ao Usuário (P02):** Evita processamentos duplicados, respostas repetidas ao cliente e garante alta disponibilidade mesmo sob rajadas de mensagens no WhatsApp.
- **Conformidade Constitucional (P00-P17):** Conformidade com P01 (SDD Inviolability), P02 (User-Centric Validation) e P07 (Zero Data Leak / Sanitização pré-log).

### FR-002: Desacoplamento Ontológico de Contato vs. Operador e Funil B2B2C
- **Descrição:** O sistema **MUST** tratar qualquer número de WhatsApp desconhecido estritamente como uma entidade `Contact` (armazenado com status inicial `PLATFORM_LEAD`), e **MUST NOT** criar instâncias na tabela `User` de autenticação para participantes externos. A associação entre um `Contact` e as organizações clientes (`Organization`) **MUST** ocorrer por meio de registros na tabela associativa `ContactOrganizationMembership`. Um mesmo `Contact` pode manter múltiplos relacionamentos com organizações distintas com total segregação de dados.
- **Impacto ao Usuário (P02):** Impede a corrupção do controle de acesso (RBAC), protege contra criação descontrolada de contas de acesso e viabiliza a jornada real de conversão de leads B2B2C.
- **Conformidade Constitucional (P00-P17):** Conformidade com P02 (User-Centric) e P07 (Privacy by Design).

### FR-003: Isolamento Criptográfico e Blindagem Máxima de PII (Proibição de Exibição de Telefone)
- **Descrição:** Todos os números de telefone em formato internacional E.164 **MUST** ser armazenados de forma criptografada em repouso (`phone_number` via criptografia assimétrica/simétrica) e indexados exclusivamente por hash determinístico (`phone_hash = HMAC-SHA256(phone, salt)`), permitindo buscas $O(1)$ sem expor PII. **Diretriz Máxima de PII:** É terminantemente proibida a exibição de números de telefone (mesmo com máscara de asteriscos) na lista de conversas, no cabeçalho do chat ativo ou nos balões de mensagem. A identificação visual do contato na interface **MUST** utilizar com exclusividade:
  1. *Nome de Exibição:* O `whatsapp_push_name` vindo do webhook ou o `full_name` qualificado no CRM;
  2. *Foto de Perfil:* O `avatar_url` obtido junto ao WhatsApp/Evolution API ou fallback de iniciais estilizadas.
- **Impacto ao Usuário (P02):** Garante privacidade absoluta em conformidade com a LGPD (Art. 13 e 46), impedindo vazamento de números de clientes em capturas de tela, gravações ou olhares de terceiros sobre o monitor do operador.
- **Conformidade Constitucional (P00-P17):** Inviolabilidade do Princípio P07 (*Privacy by Design & Data Vault*).

### FR-004: Máquina de Estados da Conversa e Soft Foreign Keys
- **Descrição:** Cada sessão de atendimento **MUST** ser gerenciada pela entidade `Conversation`, identificada por chave primária UUID e particionada por `organization_id` (Soft Foreign Key UUID). O campo `status` **MUST** transitar deterministicamente entre os seguintes estados canônicos:
  1. `ACTIVE_AI`: Atendimento conduzido de forma autônoma pela IA;
  2. `ACTIVE_HUMAN`: Atendimento sob controle de um operador humano;
  3. `CLOSED`: Conversa finalizada;
  4. `ARCHIVED`: Conversa arquivada para fins de histórico e compliance.
- **Impacto ao Usuário (P02):** Clareza no fluxo operacional do time de atendimento, rastreabilidade de histórico e garantia de que nenhum cliente fique sem resposta.
- **Conformidade Constitucional (P00-P17):** Conformidade com P01 (SDD Inviolability) e P14 (Full Audit Trail).

### FR-005: Transbordo Humano com Prevenção Ativa de Colisão (Supressão de Envio de IA)
- **Descrição:** Quando uma conversa estiver no estado `ACTIVE_HUMAN`, a tarefa assíncrona do Celery responsável pelo processamento de mensagens inbound **MUST NOT** disparar comandos de envio externo de mensagens para a Evolution API. É terminantemente vedado à IA responder diretamente ao cliente no WhatsApp enquanto um humano estiver responsável pelo atendimento. O transbordo (`takeover`) para humano **MUST** registrar o operador responsável (`assigned_user_id`) e atualizar o estado da conversa atomicamente com trava de concorrência.
- **Impacto ao Usuário (P02):** Elimina o atrito de clientes receberem mensagens automáticas de IA enquanto estão conversando ativamente com um operador humano.
- **Conformidade Constitucional (P00-P17):** Conformidade com P00 (Human Wellbeing) e P02 (User-Centric Validation).

### FR-006: Modo IA Copiloto Proativo (Agent Assist / Draft Mode)
- **Descrição:** Em conversas no estado `ACTIVE_HUMAN`, ao receber uma nova mensagem do cliente, o sistema **MUST** disparar uma tarefa assíncrona (`generate_copilot_draft_task`) para formular uma sugestão de resposta contextual com base no histórico da conversa e na base de conhecimento. Essa sugestão **MUST** ser salva como `CopilotDraft` e transmitida via WebSocket para o painel do atendente. A interface **MUST** disponibilizar ações de 1 clique:
  1. *Inserir no campo:* Transfere o texto sugerido para a caixa de edição do operador para ajuste manual antes do envio;
  2. *Aprovar e Enviar:* Despacha imediatamente a mensagem ao cliente via Evolution API e encerra o draft como aprovado;
  3. *Descartar:* Remove a sugestão sem qualquer impacto na conversa.
- **Impacto ao Usuário (P02):** Aumenta a produtividade do time de atendimento em até 60%, reduz o tempo médio de resposta (TMR) e mantém a soberania do operador humano na comunicação final.
- **Conformidade Constitucional (P00-P17):** Conformidade com P00 (Human Wellbeing) e P02 (User-Centric).

### FR-007: Interface de Atendimento em Viewport Fixo e Suporte Cross-Platform (Layout WhatsApp Web Clone)
- **Descrição:** O frontend corporativo **MUST** ser renderizado em container de viewport fixo com altura estrita `h-dvh` e classe `overflow-hidden`, eliminando rolagem na janela do navegador, com suporte cross-platform garantido para os principais navegadores modernos (Chrome, Firefox, Safari, Edge) em Windows, macOS e Linux. O layout **MUST** ser responsivo e organizar-se em 3 colunas articuladas:
  1. *Coluna 1 (Lista de Conversas):* Largura fixa (320px–380px no desktop) com campo de busca, abas de filtro (`Todos`, `Não Lidos`, `IA`, `Meus Atendimentos`), contadores de mensagens não lidas (`unread_count`), prévia de texto, badge de status, foto de perfil (`avatar_url`) e Nome de Exibição (`whatsapp_push_name` / `full_name`) — sem exibir telefones;
  2. *Coluna 2 (Timeline de Chat):* Área central expandida com cabeçalho de atendimento (nome do contato, avatar, canal, status, botão de Takeover / Devolver para IA), histórico de mensagens com rolagem independente, suporte a mídias (áudio com player, imagens, documentos), balões estilizados com carimbos de entrega (Pending, Sent, Delivered, Read), suporte a respostas citadas (`quoted_message`), chip visual de sugestão do Copiloto no rodapé e caixa de digitação com suporte a texto multiline e atalho `Enter` para envio;
  3. *Coluna 3 (Drawer de Contexto CRM):* Painel retrátil na lateral direita exibindo dados do contato (nome, avatar, estágio no funil B2B2C, tags, organização cliente e observações de CRM).
  4. *Adaptação Responsiva e Mobile (Cross-Device):* Em telas compactas (tablets e smartphones < 1024px), o layout transiciona deterministicamente de 3 colunas simultâneas para visualização em pilha de navegação (drill-down view: Lista -> Chat ativo via drawer/view unificada com botão 'Voltar', e Drawer de CRM acionado via sheet modal deslizante), preservando 100% da usabilidade em dispositivos móveis.
- **Impacto ao Usuário (P02):** Proporciona uma experiência de usuário (UX) extremamente familiar e intuitiva, inspirada no padrão universal do WhatsApp Web, com curva de aprendizado nula para novos operadores e acessibilidade em qualquer dispositivo ou plataforma de trabalho.
- **Conformidade Constitucional (P00-P17):** Conformidade com P02 (User-Centric Validation) e P11 (Equalização de Recursos).

### FR-008: Notificações e Atualizações em Tempo Real (WebSocket / Server-Sent Events)
- **Descrição:** O sistema **MUST** emitir eventos em tempo real para os canais de frontend autenticados (`private-org-{org_id}`) para:
  1. `conversation.message.new`: Inserção instantânea de nova mensagem (inbound ou outbound) na timeline sem recarregar a tela;
  2. `copilot.draft.generated`: Apresentação imediata da sugestão do copiloto no chat ativo;
  3. `conversation.status.updated`: Atualização dinâmica de status da fila e contadores não lidos.
  O cliente frontend **MUST** integrar esses eventos com a camada de cache do TanStack Query v5 para sincronização otimista e consistente.
- **Impacto ao Usuário (P02):** Elimina a necessidade de polling contínuo (F5), reduzindo consumo de bateria, latência de tela e sobrecarga no servidor.
- **Conformidade Constitucional (P00-P17):** Conformidade com P02 (User-Centric) e P11 (Equalização de Recursos).

---

## 3. Success Criteria (Critérios Mensuráveis)

- **SC-001 (Latência de Ingestão de Mensagem):** O endpoint receptor do webhook da Evolution API responde com `200 OK` em tempo $P95 \le 200\text{ms}$, delegando o processamento pesado integralmente para a fila do Celery.
- **SC-002 (Velocidade de Sugestão do Copiloto):** Quando uma mensagem inbound chega em uma conversa com atendente humano (`ACTIVE_HUMAN`), o draft de resposta sugerido pela IA é entregue na tela do operador via WebSocket em tempo $P90 \le 3.5\text{s}$.
- **SC-003 (Zero Colisão Atendente vs IA):** Em 100% dos testes de estresse com mensagens concorrentes em modo `ACTIVE_HUMAN`, nenhuma mensagem automática gerada por LLM é disparada diretamente para o WhatsApp do cliente sem aprovação humana prévia.
- **SC-004 (Performance Visual e Estabilidade):** A interface clone do WhatsApp Web carrega a lista das primeiras 50 conversas em menos de 1.2s e mantém a taxa de quadros em 60 FPS durante a digitação e a rolagem das mensagens.
- **SC-005 (Proteção e Sigilo de PII):** 100% dos registros de números de telefone são blindados no banco de dados com chave hash determinística, sem qualquer exposição de número E.164 em texto plano nos logs da aplicação.
- **SC-006 (Cobertura de Testes Automatizados):** O módulo atinge cobertura mínima de testes de 90% nos services de mensageria e triagem, e 85% nos modelos de dados em conformidade com o Princípio P05 (TDD Inviolável).

---

## 4. User Scenarios & Acceptance Criteria (Given / When / Then)

### Cenário 1: Entrada de Novo Contato no Funil B2B2C via WhatsApp
- **Given** que um número não cadastrado (`+55 65 99999-0000`) envia a mensagem "Olá, gostaria de saber mais sobre os planos" via WhatsApp,
- **When** o webhook da Evolution API recebe o payload `messages.upsert`,
- **Then** o sistema cria um novo registro de `Contact` com `contact_type='PLATFORM_LEAD'`, associa o número criptografado em `ContactPhoneNumber`, instancia a `Conversation` em modo `ACTIVE_AI` e despacha a tarefa de resposta autônoma ao Celery.

### Cenário 2: Atendente Humano Assume a Conversa (Takeover)
- **Given** que uma conversa está sendo atendida pela IA no modo `ACTIVE_AI`,
- **When** o operador humano clica no botão "Assumir Atendimento" no cabeçalho do chat,
- **Then** a conversa transiciona para `ACTIVE_HUMAN`, o operador logado é registrado em `assigned_agent_id`, o cliente de WebSocket atualiza a UI instantaneamente e o sistema silencia qualquer despacho automático de IA para o WhatsApp.

### Cenário 3: IA Copiloto Sugere Resposta em Atendimento Humano
- **Given** que a conversa está em modo `ACTIVE_HUMAN` sob os cuidados do atendente João,
- **When** o cliente final envia uma pergunta ("Qual o horário de funcionamento aos sábados?"),
- **Then** a mensagem é inserida na timeline, a tarefa `generate_copilot_draft_task` formula a resposta sugerida e um chip no rodapé do atendente exibe a sugestão com as opções "Inserir no campo", "Aprovar e Enviar" e "Descartar".

### Cenário 4: Atendente Aprova e Despacha Sugestão do Copiloto
- **Given** que uma sugestão do copiloto está visível no rodapé do chat,
- **When** o atendente clica em "Aprovar e Enviar",
- **Then** a sugestão é salva como mensagem de saída (`sender_type='HUMAN_AGENT'`), despachada para a Evolution API, entregue ao WhatsApp do cliente e o draft é marcado como `status='APPROVED_SENT'`.

---

## 5. Casos de Borda (Edge Cases) e Tratamento de Exceções

1. **Tentativa de Takeover Simultâneo por Dois Atendentes:**  
   Se dois operadores clicarem no botão "Assumir" quase ao mesmo tempo, a transição utiliza trava relacional atômica (`select_for_update`). O primeiro assume com sucesso; o segundo recebe notificação informando que a conversa já foi assumida pelo colega.
2. **Queda de Conexão da Instância da Evolution API:**  
   Se a Evolution API v2 estiver offline ou desconectada do WhatsApp, a tarefa de envio do Celery registra `delivery_status='FAILED'` e aciona política de retry exponencial (3 tentativas em 2s, 5s e 10s) sem travar a interface do operador.
3. **Mensagem Duplicada por Reenvio de Webhook:**  
   Se o webhook reenviar o mesmo payload, a busca pelo `external_id` (ID do WhatsApp) detecta a duplicação em $O(1)$ e descarta silenciosamente o payload com resposta HTTP 200.
4. **Mensagens com Mídias (Áudio, Imagem, PDF):**  
   O sistema armazena a URL da mídia e exibe na timeline o player de áudio ou thumbnail de imagem com opção de download seguro.

---

## 6. Suposições Verificadas (Grounding P03)

- **Evolution API v2:** Documentação oficial da API v2 e eventos de webhook `messages.upsert` validados conforme especificação OpenAPI e compatibilidade com Baileys (`https://doc.evolution-api.com/v2/pt/` verificado em 20-10-2026).
- **Celery 5.4.x + Redis 7:** Modelo de tarefas assíncronas com `@shared_task(bind=True, max_retries=3)` validado contra a documentação oficial (`https://docs.celeryq.dev/en/stable/` verificado em 20-10-2026).
- **Django REST Framework CursorPagination:** Uso de paginação baseada em cursor para chats em tempo real validado para evitar problemas de offset sob inserções concorrentes (`https://www.django-rest-framework.org/api-guide/pagination/#cursorpagination` verificado em 20-10-2026).
- **React 19 & Next.js 16 App Router:** Renderização de layouts de tela cheia sem vazamento de scroll (`h-dvh overflow-hidden`) com suporte a server components e client boundaries (`https://nextjs.org/docs/app` verificado em 20-10-2026).
- **TanStack Query v5 Singleton:** Gerenciamento reativo de cache de conversas com invalidação pontual via WebSockets (`https://tanstack.com/query/v5` verificado em 20-10-2026).

---

## 7. Escopo Fora de Cogitação (Out of Scope)

- Implementação de campanhas de disparos em massa (Broadcast/Disparador);
- Criação de novos canais como Telegram ou Messenger neste turno (restrito a WhatsApp via Evolution API v2);
- Modificação na camada de billing ou faturamento de tokens de IA;
- Cópia direta de código legado de `AI-Control completo.md` sem adaptação para o stack desacoplado atual.
