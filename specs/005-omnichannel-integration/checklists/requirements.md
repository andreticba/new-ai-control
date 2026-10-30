<!-- requirements.md | AI Control Omnichannel v0.1.0 | 20-10-2026 09:10(GMT-04:00) -->
# Specification Quality Checklist: 005-omnichannel-integration

**Purpose**: Validar a completude, consistência relacional e qualidade arquitetural antes de avançar para a especificação formal (`/vitalia-spec-specify`) e planejamento técnico.  
**Feature**: Atendimento Omnichannel (WhatsApp Web Clone, B2B2C, Celery & IA Copilot)  
**Artefatos de Referência**:
- [research-brainstorming.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/research-brainstorming.md)
- [data-model.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/data-model.md)
- [omnichannel_api_contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/005-omnichannel-integration/contracts/omnichannel_api_contracts.md)

---

## 1. Content & Domain Quality (Domínio B2B2C e Funil)
- [x] O papel de `Contact` está estritamente desacoplado de `User` (contato externo desconhecido inicia como Lead sem exigir criação de conta) [Clarity]
- [x] O vínculo B2B2C multi-tenant é intermediado via `ContactOrganizationMembership` [Completeness]
- [x] Suporte a números múltiplos por contato com identificação do canal de origem [Completeness]
- [x] Sem acoplamentos legados de ForeignKey rígida com o monolito: Soft FKs com `UUID` e blind indexes indexados (`phone_hash`) [Governance]
- [x] Risco de colisão atendente vs IA neutralizado (supressão estrita de envio autônomo em `ACTIVE_HUMAN`) [Safety]

---

## 2. Experiência de Usuário (WhatsApp Web Clone & Copilot UX)
- [x] Layout em viewport fixo `h-dvh overflow-hidden` (Zero Page Scroll) [UX]
- [x] Painel de 3 colunas independentes: Lista de conversas, Timeline da conversa ativa, e Drawer retrátil de CRM do contato [Completeness]
- [x] Modo Copiloto proativo: chip de sugestão de resposta renderizado diretamente no campo de composição do atendente (`Draft Mode`) [Clarity]
- [x] Ações de 1 clique para o atendente: "Inserir no campo", "Aprovar e Enviar", "Descartar" [Completeness]
- [x] Distinção visual explícita entre mensagens do cliente, IA autônoma e agente humano [Clarity]

---

## 3. Resiliência de Backend e Integrações (Celery & Evolution API v2)
- [x] Webhook `MESSAGES_UPSERT` processado com idempotência estrita via `external_id` / `data.key.id` [Measurability]
- [x] Tarefa assíncrona desacoplada de geração de sugestão do copiloto (`generate_copilot_draft_task`) sem bloquear o webhook HTTP [Performance]
- [x] Notificação reativa em tempo real para o atendente via WebSocket/SSE sem necessidade de polling de tela [Measurability]
- [x] Tratamento de fallback quando a instância da Evolution API estiver desconectada (`delivery_status: FAILED` com retry exponencial) [Coverage]

---

## 4. Requirement Quality (FRs & Acceptance Scenarios)
- [x] Todos os requisitos contêm critérios mensuráveis agnósticos de implementação [Measurability]
- [x] Acceptance Scenarios formulados em Given/When/Then para cada fluxo principal [Coverage]
- [x] Edge cases identificados (duplicidade de cliques em takeover, queda de rede no envio, número com múltiplos DDI/DDD) [Coverage]
- [x] Escopo claramente delimitado: migração de código legado sem adaptação expressamente vetada [Completeness]
