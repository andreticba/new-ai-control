<!-- spec.md | Vitalia SDD v0.6.0 | 09-10-2026 15:15(GMT-04:00) -->
**spec.md | AI-Control v0.0.1 | 09-10-2026 15:15(GMT-04:00)**

# Especificação de Funcionalidade: Core Foundations (Refatoração de Domínios)

**Data:** 09-10-2026
**Autor/Agente:** Nexus Architect (via vitalia-spec-specify)

## 1. Contexto e Objetivo (O Quê e Por Quê)
O projeto atual `ai-control` opera corretamente integrado à Evolution API, mas sofre de acoplamento monolítico em seu módulo `core`. O objetivo desta fundação é refatorar a base *in loco* (sem reescrever do zero), quebrando o monolito em três *Bounded Contexts* (`core`, `omnichannel` e `knowledge_hub`). Além disso, injetaremos as estratégias de negócios avançadas do legado (Context Lock da IA, Hierarquia 4-Tier, Tenant Único) e consolidaremos o `AuditLog` como um *Ledger Híbrido* inviolável que atende ao Direito ao Esquecimento da LGPD.

## 2. Requisitos Funcionais
O que o software deve fazer de forma observável?
- **[FR-001] Isolamento via Soft FKs:** O sistema MUST separar os domínios usando `models.UUIDField` para todas as chaves estrangeiras inter-apps. `models.ForeignKey` está proibido para cruzar domínios.
- **[FR-002] Tenant Interno Blindado:** O modelo `core.Organization` MUST implementar `UniqueConstraint(is_internal=True)`.
- **[FR-003] Desacoplamento Omnichannel:** O sistema MUST abrigar `Conversation`, `Message`, `Contact` e `OmnichannelPreferences` no novo app `omnichannel`.
- **[FR-004] Inteligência RAG e Context Lock:** O modelo `Conversation` MUST receber os campos lógicos da IA: `context_locked` (bool), `locked_at` (datetime), `current_intent` (string) e `consecutive_rag_failures` (int).
- **[FR-005] Sincronização Cross-Domain:** O sistema MUST usar um Signal assíncrono para auto-criar a `OmnichannelPreferences` quando uma nova `Organization` for instanciada.
- **[FR-006] Ledger Híbrido:** O `AuditLog` no `core` MUST receber um `GinIndex` (para metadados JSONB LLM) e uma Migração com `Trigger` SQL Postgres nativo bloqueando operações de `UPDATE` e `DELETE`, que **DEVE estar posicionado no final da migração**. O esquecimento ocorrerá via *Crypto-Shredding*.
- **[FR-007] Worker Isolado (SC-003):** O sistema MUST configurar um DB Redis Dedicado (ex: DB 2) exclusivo para o Celery Worker do `omnichannel`.
- **[FR-008] Reinício Limpo de Banco:** O sistema MUST reconstruir o `0001_initial.py` para gerar o schema refatorado e inserir os dados básicos de configuração (via `RunPython` ou seed).

## 3. Requisitos Não-Funcionais (Restrições)
Quais as regras de performance, segurança, ou aderência à Constituição do Arquiteto?
- **[NFR-001] Compatibilidade Estrita (P03):** Uso exclusivo de Django 6.1.x e `django-crypto-fields==1.0.1` (nenhuma regressão de stack tolerada).
- **[NFR-002] TDD Inviolável (P05):** A implementação MUST iniciar pela fase Red. Nenhuma lógica procedural (Signals, Triggers, Models) será aceita sem teste prévio validando a ausência do "Tenant Bleed" e o bloqueio do Trigger no banco.
- **[NFR-003] Proteção de Dados (P07):** Logs e metadados LLM NÃO DEVEM vazar PII em texto puro, cumprindo a lei de criptografia do Data Vault.

## 4. Histórias de Usuário (User Stories)
- **Como um** administrador da plataforma, **eu quero** garantir que a Organização Interna seja única no banco **para que** dados administrativos não se misturem com dados de Tenants Clientes.
- **Como um** auditor de compliance (LGPD), **eu quero** que os logs gerados pela IA no AuditLog sejam imutáveis a nível de banco de dados, **para que** evidências operacionais não sofram adulteração.
- **Como um** engenheiro de SRE, **eu quero** que as filas de processamento RAG (`omnichannel`) operem num Redis isolado do `core` **para que** picos de chat não derrubem o envio de e-mails transacionais.

## 5. Critérios de Aceite (Acceptance Criteria)
Condições estritas para considerar a funcionalidade concluída.
- **[AC-01]** Dado o isolamento arquitetural, quando se buscar a chave `organization_id` no app `omnichannel`, então ela deve ser do tipo `UUIDField` com `db_index=True`, e não um `ForeignKey`.
- **[AC-02]** Dado o banco de dados rodando, quando uma instrução bruta de `DELETE FROM core_auditlog` for enviada, então o banco deve retornar erro imediato devido ao Trigger de proteção.
- **[AC-03]** Dada a criação de uma `Organization` via Django Admin, quando ela for salva, então uma `OmnichannelPreferences` correspondente deve ser criada automaticamente sem criar vínculo duro.

## 6. Fora do Escopo (Out of Scope)
- Não inclui a implementação completa da pipeline semântica RAG (Apenas preparação estrutural do `Conversation` e do `Document`).
- Não inclui integração nativa de novos provedores LLM (Mantém-se a infra Evolution/ollama existente).

## 7. Suposições Verificadas (Grounding)
- **Mapeamento de Fontes e Critério de Sucesso**: O arquivo `alinhamento.md` detalha que a estrutura base vem de `core/models.py`, a inteligência vem de `AI-Control 08-11-2025-21-25.md` e o código final deve ser o reflexo exato dos manuais em `docs/`.
- "Django 6.1.x" e "django-crypto-fields==1.0.1": Verificados localmente em `ai-control/requirements.txt` (Data: 09-10-2026).
- "Trigger Postgres para Imutabilidade": Suportado ativamente no PostgreSQL via `CREATE TRIGGER` e `RAISE EXCEPTION`.
- "Redis DB Isolation": Configuração suportada nativamente pela URL de broker do Celery (`redis://.../DB_NUMBER`).
