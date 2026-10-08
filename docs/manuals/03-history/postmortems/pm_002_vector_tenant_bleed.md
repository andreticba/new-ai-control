<!-- pm_002_vector_tenant_bleed.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# Post-Mortem 002: Tenant Bleed no Banco Vetorial Externo (IDOR)

**Público-alvo:** Desenvolvedores e Engenheiros de Dados
**Data da falha/decisão:** 22-09-2026
**Commit de referência:** `686d444`

## Contexto
Na arquitetura inicial de IA do `ai-control`, adotamos um banco de dados vetorial externo (SaaS) para armazenar os embeddings dos documentos e acelerar as buscas RAG (Retrieval-Augmented Generation). O objetivo era utilizar um motor HNSW nativo de mercado para garantir baixa latência na busca de similaridade sem sobrecarregar o banco transacional.

## Linha do Tempo
- **Dia 1:** Migração de todos os chunks de texto para o Vector DB SaaS. O schema continha o embedding e o texto, mas apenas metadados básicos (ex: `doc_id`).
- **Dia 14:** Implementação da funcionalidade RAG no bot do WhatsApp para todos os tenants.
- **Incidente:** Um médico da Clínica A perguntou ao bot sobre "procedimentos de faturamento". A IA recuperou um documento de "Políticas de Faturamento" que, na verdade, pertencia ao Hospital B, gerando uma resposta com dados sensíveis de outra organização.
- **Descoberta:** A busca vetorial por similaridade (KNN) retornou os 5 chunks mais próximos matematicamente da pergunta, ignorando a qual tenant eles pertenciam, caracterizando um caso clássico de *Tenant Bleed* via *IDOR (Insecure Direct Object Reference)* no pipeline de Machine Learning.

## Causa Raiz Sistêmica
- **Isolamento Lógico Fraco:** Ferramentas de busca vetorial na nuvem muitas vezes dependem de filtros de metadados aplicados em memória *após* a busca KNN, ou possuem filtros que não escalam quando o banco cresce.
- **Desconexão Transacional:** Ao separar o banco relacional (onde mora a regra de RBAC e o ID do Tenant) do banco vetorial, a validação de autorização de dados tornou-se uma operação assíncrona, frágil e custosa. A aplicação buscava similaridade global e tentava filtrar o resultado depois, um padrão sujeito a falhas e vazamento de dados.

## O que foi tentado
Tentamos usar metadados de filtragem na API do banco vetorial externo (`filter={"tenant_id": "X"}`). Porém, isso afetava a densidade do índice HNSW, fazendo com que buscas em tenants menores retornassem resultados de baixa qualidade ou vazios, pois a aproximação dos vizinhos mais próximos era calculada globalmente, não particionada por tenant de forma robusta.

## O que aprendemos
1. **RAG Seguro Requer Defesa em Profundidade:** A busca vetorial não pode contornar a camada de autorização (RBAC). A segurança não pode ser um "post-filter".
2. **ACID e Vetores devem andar juntos em dados multi-tenant sensíveis:** O custo de sincronizar e garantir o isolamento entre dois datastores distintos para o mesmo domínio de negócio (Documentos Corporativos) é mais alto do que escalar um banco relacional com capacidades vetoriais.

## Decisão Resultante
Foi decidido **abandonar o SaaS de Vector DB externo** e internalizar os embeddings no banco transacional utilizando a extensão `pgvector` do PostgreSQL. Isso permitiu usar os filtros SQL *duros* e atômicos (`WHERE organization_id = X AND visibility = Y`) diretamente na query vetorial, garantindo a aplicação de Row-Level Security (RLS) e o isolamento total dos dados de cada Tenant antes do cálculo de similaridade.

## Links ADR / Código
- [Mapa de ADRs](../adr-map.md)
- Evidência no código: A busca RAG foi reescrita no `lab_03_rag_visibilidade.py` usando `CosineDistance` combinado com `filter(organization=...)`.

## Lacunas de Evidência
Os logs do vazamento foram capturados no sistema de APM, mas não foram registrados no banco local, pois a arquitetura anterior não possuía a camada de AuditLog unificada que existe hoje.
