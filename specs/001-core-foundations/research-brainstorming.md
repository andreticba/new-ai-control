<!-- research-brainstorming.md | Atualizado em: 09-10-2026 15:13:54(GMT-04:00) -->
**research-brainstorming.md | AI-Control v0.0.1 | 09-10-2026 15:13(GMT-04:00)**

# Research & Socratic Brainstorming: Correção Arquitetural Core Foundations

Este documento registra as premissas, falhas arquiteturais detectadas e as decisões definitivas tomadas para a reconstrução do pipeline da feature "Core Foundations" (`001-core-foundations`).

## 1. Falhas Identificadas nos Artefatos Anteriores
- **Alucinação de Stack:** O plano original previa Django 5.x e `django-cryptography`, quando a base real opera em **Django 6.1.x** utilizando `django-crypto-fields==1.0.1`.
- **Ignorância de Código Legado:** O plano propunha a criação de um modelo `AuditLog` do zero, ignorando que o `core/models.py` atual já possui um modelo maduro de `AuditLog` com campos cifrados (`EncryptedCharField`, `EncryptedTextField`).
- **Falha de TDD (P05):** A matriz de tarefas (`tasks.md`) pulava a etapa mandatória de escrita de testes (Red Phase) para *Middlewares* e *Signals*.

## 2. Garantias contra Recorrência de Erros
O usuário questionou: *"Que garantias temos de que os mesmos (ou outros) erros não ocorrerão novamente ao recriar do zero?"*

A garantia reside em **Três Barreiras Sistêmicas** ativadas por este documento:
1. **Injeção de Rastro Físico:** Este arquivo (`research-brainstorming.md`) atua como âncora de *Grounding* (P03). O Agente gerador da Spec (`/vitalia-spec-specify`) é obrigado a ler este arquivo e não poderá inventar dependências fora do que está declarado aqui.
2. **Task Verifier de TDD:** A declaração de obrigatoriedade de Testes (abaixo) forçará o juiz a reprovar o `tasks.md` se ele não contiver as tarefas `pytest` atômicas.
3. **Verificação de Limpeza:** A instrução explícita de "limpar chamadas antigas" será validada ativamente na aprovação do PR final.

## 3. Decisões Arquiteturais Consolidadas

| Decisão Tomada | Racional Técnico | Ação Exigida na Nova Spec |
|----------------|------------------|---------------------------|
| **Descarte Total dos Artefatos Anteriores** | O plano antigo assumia a criação de um repositório "new-ai-control", o que destruiria a integração ativa com o Evolution API. | Rodar `/vitalia-spec-specify` forçando a **refatoração in loco** da base atual (`ai-control`), e injetando a inteligência do markdown legado. |
| **Stack Rigorosamente Mantida** | O ecossistema local é o Source of Truth. | Utilizar explicitamente **Django 6.1.x** e **django-crypto-fields==1.0.1**. Sem exceções. |
| **Reaproveitamento de Modelo (`AuditLog`)** | O modelo nativo `core/models.py` já atende à conformidade LGPD e possui os eventos corretos do Omnichannel. | **Manter** o modelo atual no `core`, integrando a nova abordagem Híbrida do Ledger (Triggers + Signals + Crypto-Shredding). |
| **Auditoria Passiva (Signals)** | Remove o fator de esquecimento humano, exigido para segurança. | Plugar *Signals* (`post_save`/`post_delete`) para operar o `AuditLog`. |
| **Sanitização de Legado (.create)** | Evitar logs duplicados na arquitetura orientada a eventos. | A nova lista de Tarefas (**tasks.md**) **deve** prever uma task para varrer e remover todos os `AuditLog.objects.create(...)` explícitos do código atual. |
| **TDD Mandatório (P05)** | Garantir blindagem contra o *Tenant Bleed*. | A Spec e as Tasks devem incluir explicitamente a criação de **Testes Unitários (Pytest)** antes da construção da lógica. |
| **Portabilidade do context_locked** | A flag `context_locked` dita o "caminho rápido" (bypass de RAG). É imperativo preparar os modelos. | O modelo `Conversation` do omnichannel deverá conter os campos: `context_locked`, `locked_at`, `current_intent` e `consecutive_rag_failures`. A lógica procedural fica para spec futura. |
| **Isolamento de Domínio Absoluto (Bounded Context)** | Prevenir acoplamento a nível de banco, preparando a arquitetura para microserviços. | Uso estrito de **Soft Foreign Keys (UUIDs)** para vínculos cross-domain. Ex: `Conversation` apontará para `Organization` via `organization_id (UUIDField)`. Proibido uso de `models.ForeignKey` inter-apps. As lógicas legadas do ORM serão refatoradas. |
| **Recuperação de Regras Legadas** | Preservar as travas antigas sem corromper fronteiras de domínio. | 1. Injetar `UniqueConstraint(is_internal=True)` na `core.Organization`. <br> 2. Criar modelo `OmnichannelPreferences` no `omnichannel` (linkado via UUID) para armazenar `reopen_conversation_timeout_hours`. |
| **Auditoria Imutável e LGPD** | Resolver paradoxo entre Ledger Inalterável e Direito ao Esquecimento. | **Abordagem Híbrida (Crypto-Shredding)**: 1. `Signals` geram o log capturando contexto. 2. `Trigger` Postgres bloqueia estritamente `UPDATE` e `DELETE`. 3. Esquecimento LGPD ocorre por anonimização da chave sem apagar a linha. |

## 4. Rastro de Pesquisa (Grounding)
| # | Afirmação | Verificado? | Fonte Local/Remota | Data |
|---|---|---|---|---|
| 1 | Versão do Django é 6.1.x | ✅ SIM | `ai-control/requirements.txt:3` | 08/10/2026 |
| 2 | Uso de `django-crypto-fields` | ✅ SIM | `ai-control/requirements.txt:9` | 08/10/2026 |
| 3 | Existência de `AuditLog` no Core | ✅ SIM | `core/models.py:693` | 08/10/2026 |
| 4 | Existência de chamadas em Services | ✅ SIM | `core/services/whatsapp_service.py` | 08/10/2026 |
| 5 | Necessidade de campos associados ao `context_locked` | ✅ SIM | `AI-Control 08-11-2025-21-25.md` linhas 2635-2660 | 09/10/2026 |
