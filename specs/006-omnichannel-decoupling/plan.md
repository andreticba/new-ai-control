<!-- plan.md | Vitalia SDD v0.6.0 | 20-10-2026 23:36:00(GMT-04:00) -->
> **plan.md | Vitalia SDD v0.6.0 | 20-10-2026 23:36:00(GMT-04:00)**

# Implementation Plan: 006-omnichannel-decoupling

**Branch**: `main` | **Date**: 20-10-2026 23:36(GMT-04:00) | **Spec**: [specs/006-omnichannel-decoupling/spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/spec.md)

---

## 1. Summary

Evolução não-destrutiva de desacoplamento e modularização do módulo Omnichannel no `ai-control`, desmontando monolitos acoplados e estabelecendo estrita Separação de Preocupações (SRP). A arquitetura **preserva integralmente** os endpoints existentes, a infraestrutura da Evolution API v2, os modelos de `omnichannel` e a suíte de 29 testes vigentes, agregando:
1. Decomposição de `page.tsx` no frontend para um orquestrador declarativo conciso (< 80 linhas);
2. Encapsulamento de lógica de drag & drop e `localStorage` no custom hook `useColumnResize`;
3. Encapsulamento de ciclo de vida e requisições da Evolution API no custom hook `useWhatsAppInstance`;
4. Componentização atômica em compound components (`NavRail`, `OmnichannelHeader`, `ColumnSplitter`);
5. Implementação de Service Layer pura no backend (`InstanceService`, `TakeoverService`, `MessageDispatchService`);
6. Erradicação de consultas N+1 sob o **Princípio P15** e segregação formal de Serializers de Leitura vs. Escrita sob o **Princípio P17**.

> **Conformidade com a Pipeline SDD (P01 SDD Inviolability):** Este plano segue estritamente o ciclo `specify` (PASS / APROVADO em `specs/006-omnichannel-decoupling/spec.md`) $\rightarrow$ `plan` (validação técnica) $\rightarrow$ `tasks` (próxima etapa mandatória) $\rightarrow$ `implement` $\rightarrow$ `converge`. **Nenhuma linha de código será implementada sem o `tasks.md` formalmente gerado e aprovado**. Domínio: Engenharia de Software / Mensageria Corporativa e CRM (Medical-Gate P09 N/A).

---

## 2. Technical Context

- **Language/Version**: Python 3.14 (Virtualenv `.venv`) / TypeScript 5.8 + Node.js 20+ (Frontend)  
- **Primary Dependencies**: Django 6.1, `djangorestframework~=3.18.3`, `channels>=4.1`, `channels-redis>=4.2`, React 19, Next.js 16 (Turbopack), `@tanstack/react-query^5.0`, Lucide-React, Sonner  
- **Storage**: PostgreSQL 16 (`ai-control_db`) com blind indexing em `phone_hash`, Redis 7  
- **Testing**: `pytest`, `pytest-django` (Backend: 29 testes vigentes) / `tsc --noEmit` + `next build` (Frontend)  
- **Target Platform**: Web API Server (Daphne/ASGI) & Browser Cross-Platform (Desktop `h-dvh` e Mobile responsivo)  
- **Project Type**: Full-Stack Enterprise Web Application (Multi-Tenant B2B2C Omnichannel)  
- **Performance Goals**: Tempo de resposta da listagem de conversas $P95 < 200\text{ms}$; Redimensionamento contínuo a 60 FPS; Zero regressões nos 29 testes vigentes  
- **Constraints**: Viewport fixo obrigatório sem scroll de página (`h-dvh overflow-hidden`); PII blindada (sem telefones na UI, HMAC-SHA256 no banco); P01 Inviolável (implementação somente após `tasks.md`)

---

## 3. Constitution Check & Gatekeepers

- **P00 (Human Wellbeing):** Soberania humana garantida por Takeover imediato e aprovação de 1-clique em drafts de IA.
- **P01 (SDD Pipeline Inviolability):** Pipeline obrigatório respeitado (`specify` $\rightarrow$ `plan` $\rightarrow$ `tasks` $\rightarrow$ `implement` $\rightarrow$ `converge`). Nenhum código sem `tasks.md`. Medical-Gate P09 N/A.
- **P02 (User-Centric Validation):** Interface idêntica ao WhatsApp Web, eliminando atrito cognitivo e tempo de treinamento.
- **P03 (External Verification):** Decisões fundamentadas em fontes autoritativas registradas em [research.md](file:///home/andre/projetos/assistidos/ai-control/specs/006-omnichannel-decoupling/research.md).
- **P04 (Timestamp GMT-04:00):** Cabeçalhos datados e sincronizados no fuso America/Cuiaba.
- **P06 (Secrets Never in Git):** Credenciais e chaves mantidas exclusivamente no `.env`.
- **P07 (Zero Data Leak / PII):** Telefone proibido em tela; identidade visual por Nome de Exibição e Avatar.
- **P11 (Hardware Agnosticism):** Modelos LLM configuráveis dinamicamente via `.env`.
- **P15 (Anti N+1 & Observability):** Erradicação de subqueries no `ConversationReadSerializer`.
- **P16 (Mermaid Defensive):** Labels entre aspas duplas prevenindo falhas de parser.
- **P17 (Segregação de Serializers):** Módulos separados `read.py` e `write.py` com aliases canônicos.

---

## 4. Technical Decisions (ADRs)

- **ADR-001 (Decomposição do Frontend via Compound Components e Custom Hooks):** Extração de lógica de drag e estado da instância para `useColumnResize` e `useWhatsAppInstance`, com componentes dedicados `NavRail`, `OmnichannelHeader` e `ColumnSplitter`, reduzindo `page.tsx` para orquestrador declarativo enxuto. *Verificado em: `https://react.dev/reference/react`.*
- **ADR-002 (Service Layer Pura no Backend para Desacoplamento de Views):** Encapsulamento de regras de integração da Evolution API, travas de concorrência e despacho de mensagens em `InstanceService`, `TakeoverService` e `MessageDispatchService`. *Verificado em: `https://docs.djangoproject.com/en/5.1/topics/db/transactions/`.*
- **ADR-003 (Blindagem Anti N+1 no ORM sob o Princípio P15):** Uso exclusivo de campos desnormalizados de preview e eager loading no ORM (`select_related`/`prefetch_related`), eliminando queries ocultas na listagem de conversas. *Verificado em: `https://docs.djangoproject.com/en/5.1/topics/db/optimization/`.*
- **ADR-004 (Segregação Estrita de Serializers Read vs. Write sob o Princípio P17):** Separação de serializers em `read.py` e `write.py` com aliases canônicos em `__init__.py` para preservar 100% de compatibilidade reversa com os 29 testes existentes. *Verificado em: `https://www.django-rest-framework.org/api-guide/serializers/`.*

---

## 5. Project Structure

- **Documentação:** `spec.md`, `contracts/decoupling_contracts.md`, `research.md`, `checklists/requirements.md`, `plan.md`.
- **Código Frontend Desacoplado:** `frontend/src/hooks/use-column-resize.ts`, `frontend/src/hooks/use-whatsapp-instance.ts`, `frontend/src/components/omnichannel/nav-rail.tsx`, `frontend/src/components/omnichannel/omnichannel-header.tsx`, `frontend/src/components/omnichannel/column-splitter.tsx`, `frontend/src/app/omnichannel/page.tsx`.
- **Código Backend Desacoplado:** `omnichannel/services/instance_service.py`, `omnichannel/services/takeover_service.py`, `omnichannel/services/message_dispatch_service.py`, `omnichannel/api/serializers/read.py`, `omnichannel/api/serializers/write.py`, `omnichannel/api/serializers/__init__.py`, `omnichannel/api/views.py`.

---

## 6. Phase Overview & Atomic Execution

- **Phase 1: Setup & Data Foundations:** Estruturar diretórios `omnichannel/services/` e `omnichannel/api/serializers/`, preparando os módulos base e contratos.
- **Phase 2: US1 — Frontend Hooks (Isolamento de Estado):** Implementar `useColumnResize` e `useWhatsAppInstance`, validando compilação estática com `npm run type-check`.
- **Phase 3: US2 — Frontend Compound Components & Decomposição de page.tsx:** Implementar `NavRail`, `OmnichannelHeader`, `ColumnSplitter`, simplificar `whatsapp-modal.tsx` e refatorar `page.tsx` para < 80 linhas com validação Turbopack (`npm run build`).
- **Phase 4: US3 — Backend Serializers P15 & P17 (Anti N+1 e Segregação):** Criar `read.py`, `write.py` e aliases em `__init__.py`, garantindo aprovação dos 29 testes existentes no pytest.
- **Phase 5: US4 — Backend Service Layer & Enxugamento de Views:** Implementar `InstanceService`, `TakeoverService` e `MessageDispatchService`, simplificando views para delegação direta.
- **Phase 6: Polish, Observabilidade & Testes End-to-End:** Execução integrada dos 29 testes do backend + validação TypeScript e verificação de conformidade GMT-04:00 (P04).
