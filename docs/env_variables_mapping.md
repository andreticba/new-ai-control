# Mapeamento de Variáveis de Ambiente (.env)

Este documento centraliza todas as variáveis de ambiente mapeadas no sistema AI-Control (`ai-control`) e também aquelas utilizadas internamente pelo framework de desenvolvimento (Kit AI-Control). As informações visam orientar a segurança, configuração e troubleshooting do ambiente.

## 1. Variáveis do Projeto `ai-control` (AI-Control)

| Variável | Arquivo de Origem | Linha | Objetivo / Contexto |
| :--- | :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | `config/settings/base.py` | L10 | Hashings internos, cookies de sessão e proteção CSRF. |
| `DEBUG` | `config/settings/base.py` | L11 | Ativa/desativa stack traces detalhados (sempre `False` em produção). |
| `POSTGRES_DB` | `config/settings/base.py` | L68 | Nome do banco de dados relacional principal. |
| `POSTGRES_USER` | `config/settings/base.py` | L69 | Usuário administrador do PostgreSQL. |
| `POSTGRES_PASSWORD` | `config/settings/base.py` | L70 | Senha de conexão do PostgreSQL. |
| `POSTGRES_HOST` | `config/settings/base.py` | L71 | Endereço do host do banco (ex: `localhost`, `db`). |
| `POSTGRES_PORT` | `config/settings/base.py` | L72 | Porta de conexão ao DB (padrão `5432`). |
| `DATABASE_URL` | `config/settings/base.py` | L78 | URL de conexão em formato consolidado (usada pelo dj-database-url). |
| `REDIS_URL` | `config/settings/base.py` | L96 | Message broker e fila do Celery (uso geral, padrão db 0). |
| `WHATS_GT_CHANNELS_REDIS_URL` | `config/settings/base.py` | L115 | Banco Redis dedicado para escalabilidade de WebSockets via Django Channels. |
| `WHATS_GT_API_URL` | `config/settings/base.py` | L126 | Endpoint local ou externo do serviço Evolution API (Gateway WhatsApp). |
| `WHATS_GT_API_KEY` | `config/settings/base.py` | L127 | Credencial global para emissão de mensagens/comandos via Gateway. |
| `WHATS_GT_WEBHOOK_BASE_URL` | `config/settings/base.py` | L128 | Rota de webhook para a qual o Evolution enviará notificações assíncronas. |
| `CRYPTO_KEY_PATH` | `config/settings/base.py` | L131 | Caminho seguro no servidor contendo as chaves AES/RSA para encriptação em banco. |
| `CONTEXT_ENCRYPTION_KEY` | `core/orchestrator/memory.py` | L10 | Chave simétrica usada para descriptografar os buffers contextuais transitórios no Redis. |
| `SESSION_CONTEXT_TTL_SECONDS` | `core/orchestrator/memory.py` | L51 | Tempo máximo (em segundos) que a memória de conversas persiste no cache. |
| `VITALIA_NODE` | `core/orchestrator/providers/ollama.py` | L34 | Endpoint base do servidor Ollama (modelo local/DDNS). |
| `VITALIA_LOCAL_MODEL` | `core/orchestrator/providers/ollama.py` | L35 | Nome do modelo LLM local (ex: `qwen2.5-coder:7b`) de fallback. |
| `OLLAMA_TIMEOUT_SEC` | `core/orchestrator/providers/ollama.py` | L36 | Teto de timeout para a inferência local processar. |
| `CLINICAL_KEYWORDS` | `core/orchestrator/safety_gate.py` | L7 | Array de termos sensíveis que engatilham automaticamente o protocolo HITL/Medical Gate. |
| `GEMINI_MAX_RETRIES` | `core/orchestrator/providers/gemini.py` | L43 | Número de retentativas na API cloud do Gemini (GCP/Vertex). |
| `GEMINI_BASE_RETRY_DELAY` | `core/orchestrator/providers/gemini.py` | L44 | Tempo de atraso inicial antes da retentativa na rede. |
| `GEMINI_MAX_RETRY_DELAY` | `core/orchestrator/providers/gemini.py` | L45 | Teto (corte) de espera do backoff exponencial. |
| `GEMINI_MODEL_FLASH` | `core/orchestrator/providers/gemini.py` | L60 | Versão específica do LLM Gemini para operações velozes e alto throughput. |
| `DJANGO_BASE_DIR` | `core/orchestrator/telemetry.py` | L35 | Fallback para referenciar a raiz do projeto. |
| `VITALIA_MACHINE_NAME` | `core/orchestrator/telemetry.py` | L43 | Identificador legível da estação ativa (usado para logs e rastreio de telemetria). |
| `ROUTER_LLM_PROFILE` | `specs/008-data-vault-docs/plan.md`| L24 | Agnosticismo de Hardware: Define programaticamente o LLM escalado (sem binds rígidos no código). |

---

## 2. Variáveis Internas do Kit (`~/.ai-control`)

Estas variáveis garantem que a máquina do desenvolvedor (host) esteja perfeitamente sincronizada com a telemetria do SDD e com os agentes autônomos.

| Variável | Arquivo de Origem | Linha | Objetivo / Contexto |
| :--- | :--- | :--- | :--- |
| `VITALIA_KIT_DIR` | `src/ai-control_hook_runner.py` | L54 | Path global apontando para a raiz das extensões, memórias e logs do sistema agêntico local. |
| `VITALIA_SESSION_ID` | `src/ai-control_hook_runner.py` | L268 | UID efêmero injetado por cada chamada do agente, separando contextos. |
| `VITALIA_MACHINE_NAME` | `src/ai-control_context_engine.py`| L76 | Sincroniza o Hostname do oráculo local com os artefatos de saída (Dashboard e README). |
| `VITALIA_MACHINE_ID` | `src/core/context_engine.py` | L125 | Hash SHA256 do Machine Name para versionamento distribuído em `.ai-control/memory`. |
| `REVIEW_LLM_PROFILE` | `src/hooks/llm_judge.py` | L36 | Instrui o Agente Validador sobre qual modelo rodar a avaliação de código (ex: `qwen3:4b`). |
| `VITALIA_NODE` | `src/hooks/llm_judge.py` | L37 | Nó de inferência local ou remoto específico para a máquina avaliadora do Kit. |
| `REDIS_URL` | `src/hooks/guardian_context.py` | L445 | Banco central do pipeline, usado pelo pub/sub e fila de controle (Semaphore). |
| `GEMINI_MODEL_PRO` | `src/ai-control_hook_runner.py` | L215 | Configuração fallback global determinando qual a versão "Heavy" do LLM deve assumir pipelines estruturais pesados. |
| `GEMINI_MODEL_FLASH` | `src/ai-control_hook_runner.py` | L219 | Configuração fallback global do modelo "Lightweight" usado em tasks iterativas no pipeline. |
| `OLLAMA_MODEL` / `OLLAMA_URL` | `src/hooks/sdd_judge/providers/ollama.py` | L18 | Interface direta da API do avaliador local. |

---
*Nota: Este documento consolida a varredura (grep scan) em toda a infraestrutura base.*
