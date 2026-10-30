<!-- research-brainstorming.md | Vitalia SDD v0.6.0 | 21-10-2026 20:40:00(GMT-04:00) -->
> **research-brainstorming.md | Vitalia SDD v0.6.0 | 21-10-2026 20:40:00(GMT-04:00)**

# 🧭 Bússola Arquitetural: Hardening, Segurança & Estabilização do Omnichannel (Spec 007)
## Diagnóstico E2E: Mascaramento de Segredos em Logs, Silent Drop de Telemetria, Ampliação do Catálogo Evolution v2, Auto-close de Modal e Despacho Outbound Confirmado

**Artefatos Relacionados:**
- [spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/spec.md) (Especificação Funcional Formal, Critérios de Sucesso e Cenários Given/When/Then)
- [research.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/research.md) (Pesquisa Oficial nos Repositórios da Evolution API v2 & Matriz de Decisões)
- [data-model.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/data-model.md) (Ontologia Contact vs User & Diagrama de Sequência)
- [contracts/hardening_api_contracts.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/contracts/hardening_api_contracts.md) (Contratos REST DRF, Webhooks & WebSocket)
- [checklists/requirements.md](file:///home/andre/projetos/assistidos/ai-control/specs/007-omnichannel-hardening/checklists/requirements.md) (Checklist de Requisitos da Spec)

---

## 1. Resumo Executivo das Decisões do Brainstorming

Durante a sessão socrática de brainstorming, todos os gargalos e inconsistências observados nos testes práticos com o smartphone foram mapeados e deliberados:

1. **🔴 P0 CRITICAL — Mascaramento de Segredos & Blindagem do Webhook Gateway:**
   - Adotar cabeçalho HTTP nativo `apikey` na comunicação do Webhook.
   - Implementar Middleware Django/ASGI de sanitização de logs para redactar preventivamente ocorrências de `apikey=...`, senhas e tokens na query string e URIs nos logs de acesso HTTP (Daphne/Django/Channels).

2. **🔴 CRITICAL — Ampliação do Catálogo da Evolution API v2 e Silent Drop $O(1)$ de Telemetria:**
   - A partir de pesquisa nos repositórios oficiais da Evolution API v2, os eventos foram segregados:
     * **Acionáveis (Celery):** `messages.upsert`, `messages.update` (recibos/ticks), `messages.edited`, `messages.delete`, `qrcode.updated` e `connection.update` (com debounce).
     * **Silent Drop em $O(1)$ (View):** `presence.update`, `contacts.*`, `chats.*`, `application.startup` e `call`, eliminando o flood desnecessário no terminal e preservando CPU/memória.

3. **🔴 P0 CRITICAL — Governança de Organização: Contact Novo vs. Contact com Usuário Vinculado (Decisão D1: C):**
   - **Regra de Contact Novo:** Se a conversa for originada por um `Contact` novo (lead externo sem conta no sistema), ela pode não ter organização (`organization_id=null`), sendo atendida por operadores com perfil de suporte global ou administradores.
   - **Regra de Contact com Usuário Vinculado:** Se o `Contact` possuir um `User` do sistema relacionado a ele, o filtro de organização é **mandatório** e deve ser estritamente aplicado conforme as memberships do usuário, garantindo a proteção do tenant.

4. **🟡 HIGH-LEVERAGE — Despacho Outbound com Confirmação Estrita da Evolution (Decisão D2: A):**
   - **Falha Atômica com Exceção Explícita:** A mensagem só aparece no chat após a confirmação inequívoca de recebimento/despacho pela Evolution API via HTTP 200/201. Se a Evolution falhar ou der timeout (> 5s), o backend NÃO grava mensagem no banco, lança `MessageDispatchError`, responde HTTP 502/400 e o frontend avisa o operador mantendo o texto na caixa de entrada sem criar balão falso no chat.

5. **🟠 MEDIUM — Política de CORS e Conectividade Local (Decisão D3: A):**
   - Adicionar `http://127.0.0.1:3000` e `http://localhost:3000` em `CORS_ALLOWED_ORIGINS` para erradicar o erro de `Network Error` do Axios.

6. **🟡 HIGH-LEVERAGE — Auto-close do Modal de Pareamento do WhatsApp:**
   - O modal de pareamento fecha automaticamente em 1.5s após a transição para `state === 'open'`. O botão de recarregar QR code limpa erros anteriores e solicita novo código de forma resiliente.

7. **🔴 CRITICAL — Governança de Arquitetura Limpa e Princípio de Responsabilidade Única (SRP - Anti-Monólitos):**
   - **Regra Mandatória de Decomposição:** Nenhum arquivo criado ou refatorado deve assumir múltiplas responsabilidades ou se tornar um monólito extenso.
   - *Backend:* DRF Views puras e magras (< 35 linhas por método) restritas a parsing e retorno HTTP; regras de negócio isoladas na Service Layer (`MessageDispatchService`, `InstanceService`); filtros e middlewares de segurança isolados em utilitários dedicados (`SensitiveLogMaskingMiddleware`).
   - *Frontend:* Componentes visuais concisos (< 120 linhas) focados estritamente na apresentação e disparo de eventos; estado complexo, side-effects de rede e WebSocket isolados em Custom Hooks reutilizáveis (`useWhatsAppInstance`, `useOmnichannelSocket`, `useOmnichannel`).

8. **🔴 P0 CRITICAL — Estabilização do Ciclo de Reatividade no React 19 (Decisão D4: A):**
   - Rastreamento idempotente de marcação de leitura via `lastMarkedConversationIdRef` em `page.tsx` para erradicar o `Maximum update depth exceeded`.
   - Remoção de dependências voláteis no `useOmnichannelSocket` (utilizando `activeConversationIdRef`) para manter a conexão WebSocket perene durante a navegação entre conversas.
   - Proteção de estado idempotente em `useWhatsAppInstance` e `lastReportedConnectedRef` em `WhatsAppConnectionModal`.

9. **🟡 HIGH-LEVERAGE — Reciclagem do Event Loop do Daphne e Estabilização de CPU (Decisão D5: A):**
   - Reciclagem imediata do processo Daphne para restabelecer a porta 8000 e zerar o acúmulo de tempo de CPU no Twisted ASGI.

10. **🔴 CRITICAL — Gestão de Leitura com Foco de Janela, Delay Perceptivo e Alerta na Barra de Tarefas (Decisão D6: Consenso):**
    - **Causa Raiz Sanada:** O `lastMarkedConversationIdRef` em `page.tsx` não era resetado ao navegar para conversas com `unread_count === 0`, impedindo a execução de `markReadMutation` ao retornar para a conversa com mensagens novas.
    - **Delay Perceptivo (1.5s):** Ao selecionar ou receber mensagem em conversa ativa com a janela em foco, aguardar 1.5 segundo para permitir ao operador perceber visualmente a chegada antes de zerar o badge.
    - **Detecção de Foco & Inatividade (`document.hasFocus()`, `visibilitychange`):**
      * Se a janela/aba estiver sem foco ou minimizada: o contador de não lidas **permanece ativo** e **não zera**, mesmo se a conversa ativa estiver selecionada.
      * **Alerta na Barra de Tarefas / Aba:** O título da aba alterna dinamicamente para `(N) Nova mensagem - AI-Control` e dispara notificação do sistema via Web Notification API (`new Notification(...)`).
      * Ao retornar o foco para a janela (`focus` / `visibilitychange`): o título original é restaurado, inicia o delay perceptivo de 1.5s na conversa aberta e zera o contador via `markReadMutation`.

---

## 2. Rastro de Pesquisa e Grounding (Princípio P03)

| # | Afirmação | Verificado? | Fonte | Data |
|---|---|:---:|---|---|
| 1 | A Evolution API v2 envia o evento `qrcode.updated` quando uma instância gera um novo QR Code. | ✅ Sim | Logs reais do usuário / Docs Evolution | 21-10-2026 |
| 2 | O Django Channels e o Daphne logam URLs completas de requisições HTTP, expondo query params em texto puro. | ✅ Sim | Logs reais do runserver no terminal do usuário | 21-10-2026 |
| 3 | `presence.update` e `contacts.update` são disparados continuamente pelo WhatsApp Web protocol via Evolution. | ✅ Sim | Especificação Baileys / Evolution API v2 | 21-10-2026 |
| 4 | O endpoint canônico de envio de texto na Evolution API v2 é `POST /message/sendText/{instance}` com payload `{"number": "...", "text": "..."}`. | ✅ Sim | `core/services/evolution_gateway.py` | 21-10-2026 |
| 5 | Contatos espontâneos externos entram inicialmente sem vínculo de usuário na tabela `Contact` com `PLATFORM_LEAD`. | ✅ Sim | `omnichannel/models.py` / `core/services/whatsapp_service.py` | 21-10-2026 |
| 6 | `document.hasFocus()` e `visibilitychange` da Page Visibility API são os padrões W3C para detectar se o usuário está com foco ativo na janela da aplicação. | ✅ Sim | W3C Page Visibility Level 2 / MDN | 24-10-2026 |
| 7 | A Web Notifications API permite disparar notificações desktop do sistema operacional que piscam/alertam a barra de tarefas em navegadores Chromium/Firefox no Linux/Windows. | ✅ Sim | W3C Web Notifications Standard | 24-10-2026 |
