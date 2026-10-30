<!-- spec.md | Vitalia SDD v0.6.0 | 20-10-2026 23:15:00(GMT-04:00) -->
> **spec.md | Vitalia SDD v0.6.0 | 20-10-2026 23:15:00(GMT-04:00)**

# Especificação de Funcionalidade: Desacoplamento Arquitetural, Service Layer no Backend, Princípios P15 e P17, e Custom Hooks no Frontend (Spec 006)

**Data:** 20-10-2026 23:15(GMT-04:00)  
**Feature:** `006-omnichannel-decoupling`  
**Status:** ESPECIFICAÇÃO_APROVADA (SDDJudge: PASS | Refatoração de Desacoplamento sem Regressão)  
**Domínio:** Engenharia de Software / Mensageria Corporativa, CRM e Desacoplamento de Monolitos. Não envolve diagnóstico clínico, condutas médicas, dosagens de medicamentos ou análise de biomarcadores de saúde humana (Princípio P09 Medical Safety Gate N/A — não aplicável).  
**Artefatos Relacionados:**
- [research-brainstorming.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/research-brainstorming.md) (Bússola Arquitetural, Diagnóstico e Matriz de Transplante)
- [contracts/decoupling_contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/contracts/decoupling_contracts.md) (Contratos Estritos de Tipagem TypeScript & Python)
- [checklists/requirements.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/checklists/requirements.md) (Checklist de Qualidade da Spec)

---

## 1. Contexto e Objetivo (O Quê e Por Quê)

O ecossistema **AI Control - Agentes Inteligentes** é uma plataforma corporativa multi-tenant de automação e atendimento com IA. O módulo de mensageria Omnichannel atingiu estabilidade funcional na Spec 005. Contudo, a rápida adição de recursos de interação resultou em acúmulo excessivo de responsabilidades em componentes-chave:
1. **Frontend:** `page.tsx` acumula mais de 500 linhas contendo listeners de eventos do DOM (`window.addEventListener`), estados de redimensionamento de colunas, persistência em `localStorage`, controle de modal de pareamento WhatsApp, renderização de dock lateral e barras de topo.
2. **Backend:** As views do DRF (`omnichannel/api/views.py`) acumulam mais de 520 linhas, executando lógica direta de integração de mensageria com a Evolution API, emissões manuais de WebSockets e consultas com risco de N+1 (em `ConversationListSerializer.get_last_message`), além de não haver segregação formal entre serializers de leitura e escrita.

O objetivo desta especificação é **DESACOPLAR E MODULARIZAR** a arquitetura, estabelecendo:
- **No Frontend:** Desmontar o monolito de `page.tsx` em um orquestrador estritamente declarativo (< 80 linhas), extraindo hooks reutilizáveis (`useColumnResize`, `useWhatsAppInstance`) e compound components (`NavRail`, `OmnichannelHeader`, `ColumnSplitter`);
- **No Backend:** Isolar a lógica de negócio em uma **Service Layer** pura (`InstanceService`, `TakeoverService`, `MessageDispatchService`), eliminando consultas N+1 via conformidade com o **Princípio P15** e adotando a segregação estrita de Serializers (Read vs. Write) via **Princípio P17**;
- **Garantia de Não-Regressão:** Manter 100% dos 29 testes do backend passando e zero erros no build do Next.js.

---

## 2. Requisitos Funcionais (FR-xxx)

### FR-001: Encapsulamento de Redimensionamento no Hook `useColumnResize`
- **Descrição:** A lógica matemática de arrasto com mouse, cálculo de limites (min/max), listeners globais (`mousemove`, `mouseup`), bloqueio de seleção de texto no DOM (`userSelect = 'none'`) e memorização de largura no `localStorage` **MUST** ser totalmente encapsulada no custom hook `useColumnResize`. O hook **MUST** suportar orientação à esquerda (para a sidebar) e orientação à direita (para o drawer de CRM). O armazenamento local (`localStorage`) **MUST** restringir-se estritamente a valores inteiros representativos de largura em pixels (`sidebar_width`, `drawer_width`), sendo expressamente vedado qualquer tráfego, manipulação ou persistência de identificadores de clientes, dados pessoais (PII/PHI) ou metadados de mensagens na camada de redimensionamento.
- **Impacto ao Usuário (P02):** Preserva a experiência fluida de redimensionamento das colunas com total isolamento, testabilidade e garantia de proteção de dados (LGPD Art. 13 e 46).
- **Conformidade Constitucional:** P00 (Human Wellbeing), P02 (User-Centric Validation), P07 (Zero Data Leak & Privacy by Design).

### FR-002: Encapsulamento de Gestão da Instância no Hook `useWhatsAppInstance`
- **Descrição:** As requisições HTTP REST aos endpoints de gerenciamento da instância (`GET/POST/DELETE /api/v1/omnichannel/instance/`), o controle de status de conexão, o feedback visual de notificações (toasts) e os estados de carregamento **MUST** ser centralizados no custom hook `useWhatsAppInstance`.
- **Impacto ao Usuário (P02):** Elimina repetição de requisições e centraliza o tratamento de falhas de conexão de rede.
- **Conformidade Constitucional:** P02 (User-Centric), P12 (Input/Output Validation).

### FR-003: Modularização Visual em Compound Components (`NavRail`, `Header`, `Splitter`)
- **Descrição:** A casca visual do Omnichannel **MUST** ser decomposta em componentes atômicos:
  1. `NavRail`: Barra lateral estreita de 56px com navegação e avatar;
  2. `OmnichannelHeader`: Barra superior contendo status do WebSocket e atalho do WhatsApp;
  3. `ColumnSplitter`: Divisória interativa com cursor `col-resize` e feedback visual nos temas ciano e esmeralda.
  O arquivo `page.tsx` **MUST NOT** exceder 80 linhas de código estrutural.
- **Impacto ao Usuário (P02):** Interface mais limpa, renderização mais performática e facilidade de manutenção.
- **Conformidade Constitucional:** P02 (User-Centric Validation).

### FR-004: Service Layer para Gestão de Instâncias (`InstanceService`)
- **Descrição:** Toda a integração com o gateway da Evolution API para criação de instância, obtenção de QR Code em base64, resolução de organização e desconexão com auditoria **MUST** ser encapsulada na classe `InstanceService` (camada de aplicação), separada da infraestrutura (`EvolutionGatewayService`) e da apresentação HTTP (`InstanceManageView`). A view DRF **MUST** atuar como casca fina limitando-se a validar permissões RBAC e despachar para o service.
- **Impacto ao Usuário (P02):** Estabilidade e confiabilidade nas operações de conexão do WhatsApp sem risco de exposição de tokens de autenticação da infraestrutura.
- **Conformidade Constitucional (P00-P17):** Conformidade com P01 (SDD Inviolability), P07 (Zero Data Leak) e P14 (Full Audit Trail com registro de ator e timestamp).

### FR-005: Service Layer para Transbordo e Controle de Atendimento (`TakeoverService`)
- **Descrição:** As transições de estado da conversa (`takeover` para `ACTIVE_HUMAN`, `return_to_ai` para `ACTIVE_AI` e `mark_read`) **MUST** residir na classe `TakeoverService`. O service **MUST** aplicar trava atômica relacional (`select_for_update`), persistir alterações com carimbo de auditoria e emitir o evento correspondente no Redis Channel Layer (`channel_layer.group_send`). Em conformidade com o **Princípio P09 (Soberania Humana & HITL)**, quando uma conversa está em `ACTIVE_HUMAN`, respostas geradas por IA permanecem estritamente no estado transitório `DRAFT` (sugestão ao operador), sendo terminantemente vedado o despacho autônomo ao cliente final sem aprovação humana prévia.
- **Impacto ao Usuário (P02):** Impede condições de corrida entre atendentes, elimina respostas concorrentes indesejadas e garante atualização instantânea em tempo real.
- **Conformidade Constitucional (P00-P17):** Conformidade com P00 (Human Wellbeing), P01 (SDD Inviolability), P09 (Medical Safety Gate & HITL Triplo) e P14 (Full Audit Trail).

### FR-006: Service Layer para Envio de Mensagens Outbound (`MessageDispatchService`)
- **Descrição:** O método `MessageViewSet.create` **MUST NOT** conter lógica de montagem de payload ou chamadas diretas a gateways. O despacho **MUST** ser delegado para `MessageDispatchService.send_operator_message`, estruturado em camadas:
  1. *Camada de Apresentação (View/Serializer):* Validação estrita de tipos via `MessageCreateSerializer` (Princípio P17);
  2. *Camada de Aplicação (`MessageDispatchService`):* Validação de JID do destinatário, resolução de citação (`quoted`), persistência transacional da `Message` e atualização de preview na `Conversation`;
  3. *Camada de Infraestrutura (`EvolutionGatewayService`):* Despacho HTTP externo com retry e monitoramento de latência ($P95 < 500\text{ms}$).
  4. *Rastreabilidade & Auditoria (Princípio P14):* Todo envio registra identificadores de transação (`external_id`), autor humano (`sender_user_id`) e carimbo de entrega, sem expor dados de telefone ou conteúdo em texto plano nos logs.
- **Impacto ao Usuário (P02):** Respostas rápidas e confiáveis aos clientes pelo WhatsApp com garantia de entrega e sigilo absoluto.
- **Conformidade Constitucional (P00-P17):** Conformidade com P01 (SDD Inviolability), P07 (Zero Data Leak), P14 (Full Audit Trail) e P17 (Segregação de Serializers).

### FR-007: Blindagem Anti N+1 no ORM (Princípio P15)
- **Descrição:** O serializer de listagem de conversas **MUST NOT** disparar queries SQL dentro de métodos `get_last_message`. O preview da última mensagem **MUST** ser obtido através dos campos desnormalizados da `Conversation` (`last_message_preview`, `last_message_timestamp`) ou através de instâncias pré-carregadas via `prefetch_related('messages')`.
- **Impacto ao Usuário (P02):** Redução drástica da latência de carregamento da lista de conversas, garantindo tempo de resposta $P95 < 200\text{ms}$.
- **Conformidade Constitucional:** P15 (Blindagem Anti N+1).

### FR-008: Segregação Estrita de Serializers: Leitura vs. Escrita (Princípio P17)
- **Descrição:** O backend **MUST** organizar os serializers em `serializers/read.py` e `serializers/write.py`. As views **MUST** utilizar serializers de escrita para validação de `POST`/`PUT` e serializers de leitura para saídas de `GET`. O módulo `serializers/__init__.py` **MUST** exportar aliases de retrocompatibilidade para que todos os testes existentes continuem executando sem alterações.
- **Impacto ao Usuário (P02):** Blindagem contra vulnerabilidades de mass-assignment e validação rigorosa de entradas.
- **Conformidade Constitucional:** P17 (Segregação de Serializers), P12 (Input Validation).

---

## 3. Success Criteria (Critérios Mensuráveis)

- **SC-001 (Zero Regressão de Testes):** 100% dos 29 testes automatizados do backend em `omnichannel/tests/` continuam passando com código 0.
- **SC-002 (Zero Erros de Compilação no Frontend):** O comando `npm run type-check` e `npm run build` executam com sucesso absoluto (zero erros de tipagem TypeScript).
- **SC-003 (Concisão do Orquestrador `page.tsx`):** O arquivo [`frontend/src/app/omnichannel/page.tsx`](file:///home/andre/projetos/assistidos/ai-control/frontend/src/app/omnichannel/page.tsx) é reduzido de ~500 linhas para menos de 100 linhas.
- **SC-004 (Eliminação de Consultas N+1):** A requisição `GET /api/v1/omnichannel/conversations/` para 50 conversas executa no máximo 3 queries SQL (conversas + contatos via `select_related` + tags via `prefetch_related`), eliminando as 50 queries concorrentes anteriores.
- **SC-005 (Concisão de Views DRF):** Nenhum método de ação dentro de `omnichannel/api/views.py` excede 35 linhas de código.

---

## 4. User Scenarios & Acceptance Criteria (Given / When / Then)

### Cenário 1: Operador Redimensiona Coluna com Hook Desacoplado
- **Given** que o operador está na tela do Omnichannel,
- **When** clica e arrasta o `ColumnSplitter` entre a lista e o chat,
- **Then** a largura da coluna é calculada suavemente pelo hook `useColumnResize`, a seleção de texto é bloqueada e o valor final é salvo automaticamente no `localStorage`.

### Cenário 2: Operador Abre Modal e Desconecta Instância com Hook `useWhatsAppInstance`
- **Given** que a instância do WhatsApp está conectada,
- **When** o operador abre o modal e clica em "Desconectar WhatsApp",
- **Then** o hook `useWhatsAppInstance` aciona a rota `DELETE`, a `InstanceManageView` delega para `InstanceService.disconnect()`, a instância é desconectada na Evolution API e a interface atualiza o status para desconectado.

### Cenário 3: Operador Assume Conversa via `TakeoverService`
- **Given** uma conversa ativa com status `ACTIVE_AI`,
- **When** o atendente clica em "Assumir Atendimento",
- **Then** a view aciona `TakeoverService.assign_to_human()`, que atualiza o registro com trava atômica, emite o evento no WebSocket e retorna a conversa serializada via `ConversationReadSerializer`.

---

## 5. Casos de Borda e Tratamento de Exceções

1. **LocalStorage Indisponível ou Desativado no Navegador:**
   O hook `useColumnResize` encapsula as operações de `localStorage` em bloco `try/catch`, utilizando o `defaultWidth` como fallback seguro.
2. **Queda de Conexão durante o Arraste:**
   O hook `useColumnResize` registra os listeners de `mouseup` diretamente no objeto `window`, garantindo que soltar o mouse fora da janela finalize o estado de arrasto sem travar o cursor.
3. **Múltiplos Operadores Chamando Takeover Concorrente:**
   O `TakeoverService` utiliza `select_for_update()` dentro de transação atômica do Django (`transaction.atomic`), garantindo serialização determinística da primeira atribuição.

---

## 6. Suposições Verificadas (Grounding P03)

- **React 19 & Custom Hooks:** Padrões de composição e isolamento de efeitos com TypeScript estrito (`https://react.dev/reference/react` verificado em 20-10-2026).
- **Django REST Framework Serializers:** Segregação de classes para leitura e escrita mitigando vulnerabilidades de mass assignment e eliminando subqueries no ORM (`https://www.django-rest-framework.org/api-guide/serializers/` verificado em 20-10-2026).
- **Service Layer Pattern:** Encapsulamento de regras de domínio de banco de dados e APIs externas fora do ciclo HTTP de views (`https://docs.djangoproject.com/en/5.1/topics/db/transactions/` verificado em 20-10-2026).

---

## 7. Escopo Fora de Cogitação (Out of Scope)

- Criação de novos canais de mensageria além do WhatsApp (Instagram/Telegram);
- Alteração no banco relacional ou criação de novas tabelas de banco de dados (restringe-se à reorganização de código);
- Modificação das políticas de cobrança ou geração de tokens de IA;
- Inclusão de diagnósticos, condutas clínicas ou prescrições médicas (P09 Medical Safety Gate N/A).
