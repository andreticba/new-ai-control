<!-- constitutional-status: APPROVED | auditor: red-team-vitalia | timestamp: 2026-10-22T09:46:55-04:00 | report: Relatório de inspeção.md -->
<!-- tasks.md | Vitalia SDD v0.6.0 | 22-10-2026 09:46:55(GMT-04:00) -->
> **tasks.md | Vitalia SDD v0.6.0 | 22-10-2026 09:46:55(GMT-04:00)**

# Tasks: 007-omnichannel-hardening

**Spec**: [specs/007-omnichannel-hardening/spec.md](spec.md) | **Plan**: [specs/007-omnichannel-hardening/plan.md](plan.md)  
**Gerado em**: 22-10-2026 09:40:00(GMT-04:00)  

---

## MVP Scope

> O escopo mínimo viável (MVP) compreende **Phase 0 + Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)**.  
> Esta entrega elimina imediatamente o vazamento de segredos em logs, desativa o flood do Celery, garante o isolamento multitenant sem `organization_id=null` e assegura que nenhuma mensagem falsa seja criada no chat em falhas de rede.

---

## Phase 0: Grounding & Environment

*Verificações de ambiente e pré-requisitos antes de qualquer codificação. Sem label de US.*

- [X] T000-A Ativar ambiente virtual Python: `source .venv/bin/activate`
- [X] T000-B [P] Verificar versão Python ativa no ambiente: `python --version` (esperado: Python 3.14+)
- [X] T000-C [P] Verificar integridade de containers Docker essenciais: `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"`
- [X] T000-D [P] Validar conectividade com broker Redis na porta 6379 e banco PostgreSQL na porta 5432
- [X] T000-E Verificar dependências instaladas e conflitos no ambiente: `pip check`

---

## Phase 1: Setup & Middleware de Segurança

*Mecanismos globais de proteção de credenciais e liberação de CORS. Sem label de US.*

- [X] T001 Criar testes unitários para o middleware de mascaramento de segredos em `tests/core/test_sensitive_log_masking.py`
- [X] T002 Implementar o middleware `SensitiveLogMaskingMiddleware` com redação de chaves sensíveis em query strings e bodies em `core/middleware/sensitive_log_masking.py`
- [X] T003 [P] Criar arquivo de exportação de pacote em `core/middleware/__init__.py`
- [X] T004 Registrar `SensitiveLogMaskingMiddleware` no topo da lista `MIDDLEWARE` em `config/settings.py`
- [X] T005 [P] Atualizar a lista `CORS_ALLOWED_ORIGINS` incluindo `http://localhost:3000` e `http://127.0.0.1:3000` em `config/settings.py`
- [X] T006 Executar suíte de testes de middleware: `pytest tests/core/test_sensitive_log_masking.py`

---

## Phase 2: Foundational & Governança de Organização Padrão (P01 & P07)

*Resolução e associação mandatória da Organização Padrão para contatos novos. Sem label de US.*

- [X] T007 Criar testes unitários para a resolução da Organização Padrão em `tests/omnichannel/test_default_organization_service.py`
- [X] T008 Implementar o serviço `DefaultOrganizationService` com o método idempotente `get_default_organization()` em `omnichannel/services/default_organization_service.py`
- [X] T009 [P] Exportar `DefaultOrganizationService` no módulo de serviços em `omnichannel/services/__init__.py`
- [X] T010 Integrar o serviço `DefaultOrganizationService` ao fluxo de recebimento de webhook em `core/services/whatsapp_service.py` para associar novos contatos e conversas sem usuário à Organização Padrão
- [X] T011 [P] Ajustar as permissões e filtros em `omnichannel/api/views.py` garantindo que operadores da Organização Padrão e administradores visualizem e respondam a contatos novos sem erro 401/404, mantendo o filtro mandatório por `organization_id`
- [X] T012 Executar testes de governança de organização: `pytest tests/omnichannel/test_default_organization_service.py`

---

## Phase 3: User Story 1 — Gateway de Webhooks & Descarte Silencioso O(1)

**Story Goal:** Silenciar o flood contínuo de eventos de presença e agenda no Celery, poupando workers e CPU, expandir eventos acionáveis e estabilizar o `AuditLog`.  
**Independent Test:** Disparar `presence.update` via curl e verificar que a View responde `HTTP 200` em $\le 15\text{ms}$ sem tarefas na fila do Celery.  
**Referência:** FR-001, FR-002, FR-007 | SC-001, SC-002  

- [X] T013 [P] [US1] Criar testes unitários para o gateway de webhooks cobrindo descarte silencioso e eventos acionáveis em `tests/core/test_webhook_whatsapp.py`
- [X] T014 [US1] Implementar as listas `SILENT_DROP_EVENTS` e `ACTIONABLE_EVENTS` com resposta $O(1)$ na view `WebhookGatewayView` em `core/api/v1/views/webhook_whatsapp.py`
- [X] T015 [US1] Adicionar suporte aos eventos `qrcode.updated`, `messages.update`, `messages.edited` e `messages.delete` no despachante do webhook em `core/api/v1/views/webhook_whatsapp.py`
- [X] T016 [P] [US1] Sanitizar o log de warnings para eventos não suportados em `core/api/v1/views/webhook_whatsapp.py` removendo JIDs, telefones e apikeys
- [X] T017 [US1] Implementar mecanismo de debounce com cache Redis (TTL 10s) no método `process_connection_update` em `core/services/whatsapp_service.py` para evitar flapping no `AuditLog`
- [X] T018 [US1] Executar testes do webhook e validar latência: `pytest tests/core/test_webhook_whatsapp.py`

---

## Phase 4: User Story 2 — Despacho Outbound com Confirmação e Falha Atômica

**Story Goal:** Garantir que nenhuma mensagem falsa seja criada no banco ou exibida no chat em caso de falha ou desconexão da Evolution API.  
**Independent Test:** Simular envio com instância desconectada e verificar que o backend responde `HTTP 502`, nenhuma linha é inserida no PostgreSQL e o texto permanece na caixa de entrada.  
**Referência:** FR-004, FR-008 | SC-003, SC-007  

- [X] T019 [P] [US2] Criar testes unitários para o despacho síncrono com mocks de sucesso e falha da Evolution API em `tests/omnichannel/test_message_dispatch_service.py`
- [X] T020 [US2] Definir a exceção de domínio `MessageDispatchError` em `omnichannel/services/message_dispatch_service.py`
- [X] T021 [US2] Refatorar `dispatch_text_message` em `omnichannel/services/message_dispatch_service.py` para chamada síncrona com timeout de 5.0s, validando `status_code in (200, 201)` e extração de `response['key']['id']` antes de persistir a mensagem
- [X] T022 [US2] Atualizar o método `create` do `MessageViewSet` em `omnichannel/api/views.py` para capturar `MessageDispatchError` e retornar HTTP 502/400 mantendo o método magro (< 35 linhas)
- [X] T023 [US2] Executar testes do serviço de despacho: `pytest tests/omnichannel/test_message_dispatch_service.py`

---

## Phase 5: User Story 3 — Frontend Hardening & Pareamento Reativo

**Story Goal:** Fornecer feedback visual em tempo real no chat, reter o texto digitado em falhas de envio e fechar automaticamente o modal de pareamento após leitura do QR Code.  
**Independent Test:** Abrir modal de pareamento, conectar WhatsApp e verificar que o modal fecha sozinho em 1.5s; simular erro no chat e verificar toast explicativo com texto retido.  
**Referência:** FR-005, FR-006, FR-008 | SC-004, SC-006, SC-007  

- [X] T024 [P] [US3] Atualizar o hook `useOmnichannelSocket` em `frontend/src/hooks/use-omnichannel-socket.ts` para tratar o evento `whatsapp.qrcode.updated` e gerenciar subprotocolo seguro
- [X] T025 [P] [US3] Atualizar o modal `WhatsAppConnectionModal` em `frontend/src/components/omnichannel/whatsapp-modal.tsx` implementando auto-fechamento após 1.5s de transição para o estado `open`
- [X] T026 [P] [US3] Adicionar botão de refresh no modal `WhatsAppConnectionModal` em `frontend/src/components/omnichannel/whatsapp-modal.tsx` com invalidação de cache do TanStack Query
- [X] T027 [US3] Refatorar o tratamento de envio no componente `ChatContainer` em `frontend/src/components/omnichannel/chat-container.tsx` para preservar o texto digitado na caixa de entrada e emitir toast de erro em respostas HTTP 502/400
- [X] T028 [P] [US3] Criar testes de componente com React Testing Library para validar a retenção de texto em falha de envio em `frontend/src/components/omnichannel/__tests__/chat-container.test.tsx`

---

## Phase 6: Polish, Observabilidade & Testes End-to-End

*Validação integrada de todo o sistema e regressão defensiva. Sem label de US.*

- [X] T029 Executar bateria completa de testes automatizados do backend: `pytest tests/`
- [X] T030 Validar integridade dos testes do frontend: `npm --prefix frontend test` ou `npm --prefix frontend run build`
- [X] T031 Validar manualmente os 5 cenários do guia executável em `specs/007-omnichannel-hardening/quickstart.md`
- [X] T032 Verificar se nenhum log de console do Django/Daphne exibe `?apikey=` ou credenciais em texto plano
- [X] T033 Confirmar que todas as views DRF têm < 35 linhas e componentes frontend têm < 120 linhas (SRP)

---

## Phase 7: User Story 4 — Gestão de Leitura com Delay Perceptivo, Foco de Janela e Alertas

**Story Goal:** Erradicar a trava de zeramento do contador não lido ao alternar conversas, introduzir delay perceptivo de 1.5s para assimilação visual do operador e alertar na barra de tarefas/aba quando a janela estiver sem foco.  
**Independent Test:** Receber mensagem com a aba em segundo plano e verificar que o contador não zera e o título da aba avisa `(N) Nova mensagem`; ao focar na janela, aguardar 1.5s e confirmar que o contador zera no banco e na tela.  
**Referência:** Decisão D6 em `research-brainstorming.md`  

- [X] T034 [P] [US4] Criar hook `useWindowFocusAndNotification` em `frontend/src/hooks/use-window-focus-and-notification.ts` para monitoramento de foco (`document.hasFocus()`, `visibilitychange`), alternância de título na aba e alerta desktop via Web Notifications API
- [X] T035 [P] [US4] Implementar atualização otimista instantânea no cache do React Query em `markReadMutation` no arquivo `frontend/src/hooks/use-omnichannel.ts`
- [X] T036 [US4] Refatorar o efeito de marcação de leitura em `frontend/src/app/omnichannel/page.tsx` substituindo a trava estática de ID por timer de delay perceptivo de 1.5s acoplado ao foco da janela (`useWindowFocusAndNotification`) com cancelamento seguro no cleanup
- [X] T037 [US4] Ajustar o clique de seleção em `frontend/src/components/omnichannel/conversation-list.tsx` garantindo a transição limpa entre conversas e rearmamento do delay perceptivo
- [X] T038 [US4] Validar tipos TypeScript (`npx tsc --noEmit`) e integridade do build de produção (`npm run build`)

---

## Dependency Graph

```text
Phase 0 (Grounding)
       │
       ▼
Phase 1 (Setup: Middleware & CORS)
       │
       ▼
Phase 2 (Foundational: Organização Padrão P07)
       │
       ├──────────────────────────────┐
       ▼                              ▼
Phase 3 (US1: Gateway Webhooks)  Phase 4 (US2: Despacho Outbound)
       │                              │
       └──────────────┬───────────────┘
                      ▼
       Phase 5 (US3: Frontend Hardening)
                      │
                      ▼
       Phase 6 (Polish & End-to-End)
```

---

## Parallel Execution

As tarefas marcadas com o prefixo `[P]` não possuem dependências entre si e podem ser desenvolvidas em paralelo:
- **Phase 0:** `T000-B`, `T000-C`, `T000-D`
- **Phase 1:** `T003`, `T005`
- **Phase 2:** `T009`, `T011`
- **Phase 3:** `T013`, `T016`
- **Phase 4:** `T019`
- **Phase 5:** `T024`, `T025`, `T026`, `T028`
