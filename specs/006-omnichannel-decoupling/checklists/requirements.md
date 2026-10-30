<!-- requirements.md | AI Control Omnichannel v0.6.0 | 20-10-2026 23:25:00(GMT-04:00) -->
> **requirements.md | AI Control Omnichannel v0.6.0 | 20-10-2026 23:25:00(GMT-04:00)**

# Specification Quality Checklist: 006-omnichannel-decoupling

**Purpose**: Validar a completude, conformidade constitucional e qualidade arquitetural da especificação de desacoplamento antes de avançar para as etapas subsequentes do pipeline SDD.  
**Feature**: `006-omnichannel-decoupling`  
**Artefatos de Referência**:
- [research-brainstorming.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/research-brainstorming.md)
- [spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/spec.md)
- [contracts/decoupling_contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/contracts/decoupling_contracts.md)

---

## 1. Decomposição e Isolamento do Frontend
- [x] O hook `useColumnResize` encapsula 100% da matemática de drag, limites min/max e listeners no `window` [Clarity]
- [x] O hook `useWhatsAppInstance` isola chamadas REST da Evolution API e feedbacks visuais [Completeness]
- [x] A casca visual foi decomposta em compound components (`NavRail`, `OmnichannelHeader`, `ColumnSplitter`) [Modularity]
- [x] O arquivo `page.tsx` foi especificado para atuar estritamente como orquestrador declarativo (< 80 linhas) [Simplicity]
- [x] Preservação do viewport fixo sem scroll (`h-dvh overflow-hidden`) e persistência no `localStorage` [UX]

---

## 2. Service Layer & Governança no Backend
- [x] A lógica de criação, QR Code e logout da Evolution API está isolada em `InstanceService` [Modularity]
- [x] As operações de transbordo e de devolução para IA estão isoladas em `TakeoverService` com travas atômicas [Safety]
- [x] O envio outbound e tratamento de mensagens citadas (`quoted`) está isolado em `MessageDispatchService` [Completeness]
- [x] As Views do DRF atuam como cascas finas (< 35 linhas por método) [Simplicity]

---

## 3. Conformidade Constitucional (P15 & P17)
- [x] Princípio P15: Erradicação de consultas N+1 via desnormalização de preview e eager loading no ORM [Performance]
- [x] Princípio P17: Segregação formal de Serializers em `serializers/read.py` e `serializers/write.py` [Security]
- [x] Retrocompatibilidade estrita: `serializers/__init__.py` exporta aliases canônicos para garantir que os 29 testes passem sem alterações [Zero-Regression]
- [x] Blindagem contínua de PII: Zero exposição de números de telefone em payloads da interface [LGPD]

---

## 4. Requirement Quality (FRs & Acceptance Scenarios)
- [x] Todos os 8 requisitos funcionais (FR-001 a FR-008) possuem descrição clara, impacto ao usuário e conformidade [Clarity]
- [x] Critérios de sucesso mensuráveis (SC-001 a SC-005) definidos com métricas objetivas [Measurability]
- [x] Acceptance Scenarios formulados em Given/When/Then para os cenários críticos [Coverage]
- [x] Casos de borda tratados (localStorage desativado, desconexão no meio do drag, concorrência de takeover) [Robustness]
