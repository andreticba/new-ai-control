<!-- 05_Building_Block_View.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 5. Building Block View

A arquitetura interna do backend está contida primariamente na pasta `core/` e baseada na modularidade do Django.

## Nível 1: Visão Geral do Sistema
- **API Gateway (Daphne / WSGI):** Camada de entrada. Lida com autenticação JWT e rotas WebSocket.
- **Core App:** Centraliza as regras de negócio, a criptografia e os modelos de domínio.
- **Celery Workers:** Componentes de background que executam a lógica pesada (Ingestão, AI Delegation).

## Nível 2: Módulos do Core
1. **`core.api.v1.views`**: Controladores de entrada. Destaca-se o `webhook_whatsapp.py`, que valida os cabeçalhos de segurança (API Keys) antes de admitir qualquer dado.
2. **`core.models`**: O coração do Data Vault. Define tabelas vetoriais (`pgvector` com HnswIndex em 768 dimensões) e tabelas criptografadas. Destaca-se a modelagem do **RBAC Hierárquico 4-Tier** (`Organization` -> `Department` -> `Project` -> `Squad`) acoplado ao modelo de visibilidade do RAG (`Document`).
3. **`core.tasks`**: Workers Assíncronos. Ex: `process_whatsapp_webhook_task`, que consome os dados e aplica a separação de *Tenant*.

## Padrões de Projeto Utilizados
- **Fat Models / Service Layer:** Lógicas atômicas encapsuladas em serviços, não nas Views.
- **Graceful Degradation:** Views que não conseguem inferir schemas (como Webhooks arbitrários) usam decoradores (`@extend_schema`) para evitar a quebra das gerações da OpenAPI.

