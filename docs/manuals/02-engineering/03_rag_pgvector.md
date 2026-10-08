<!-- 03_rag_pgvector.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# 03. Busca Vetorial com pgvector e RAG Seguro
**Público-alvo:** Desenvolvedores Backend / Engenheiros de Dados IA
**Tempo de Leitura:** 10 min

Este módulo trata do banco de dados vetorial PostgreSQL e a integração da estrutura de arquivos de RAG (Retrieval-Augmented Generation) com controle de acesso no banco. O RAG atual em produção **ainda é um Design de Referência 🧭** — a infraestrutura existe no ORM (`DocumentChunk`, índice HNSW), mas a chamada vetorial ao `pgvector` é um MOCK aguardando orquestração LLM.

## 1. Esquema HNSW e as 768 Dimensões ✅
Em vez de depender de nuvens externas (Pinecone/Milvus), todo Embedding mora ao lado do dado relacional no modelo `DocumentChunk` via `VectorField(dimensions=768)`.

**O Limite de Dimensões (Lição F-02):** Historicamente o modelo almejava vetores de 4096 dimensões (ex: modelos gigantes nativos). Porém, o índice `vector` do HNSW só suporta até 2.000 dimensões de forma eficiente. O modelo mudou para **768 dimensões** para garantir a capacidade de indexação (`HnswIndex(m=16, ef_construction=64, opclasses=['vector_cosine_ops'])`).

## 2. Denormalização de Escopo e Segurança ✅
Para buscar contexto na IA, o ORM precisa restringir quem está pedindo o contexto e onde. Nós usamos a Denormalização de Escopo. Os campos de PK `organization`, `department`, `project` e `squad` foram replicados da estrutura relacional direto pro `DocumentChunk`.
A coluna `Visibility` dita a altura na árvore.

## 3. Isolamento vs Recall (O Comportamento do HNSW com WHERE) 🟡
**Divergência Crítica:** Os comentários do código fonte dizem que há "pré-filtragem SQL **antes** da busca vetorial". Na verdade, as evidências apontam (F-03 do Manual do `pgvector`) que, em índices aproximados como o HNSW, os filtros `WHERE` severos (ex: buscando em um squad de apenas 5 documentos no meio de 10.000) ocorrem **após** o scan principal.
Isso quer dizer que a segurança continua perfeita (nada vaza), mas se o scan do vetor passar reto pelos documentos restritos daquele SQUAD, ele pode devolver zero (ou menos resultados que `LIMIT K`) ao usuário.
**Mitigação recomendada:** No módulo Python/SQL final, habilitar a varredura iterativa via `SET LOCAL hnsw.iterative_scan = strict_order;` e utilizar Particionamento ou Partial Indexing caso a degradação escale na Organização.

## 4. Diferença L2 vs Cosseno (A-005) 🧭
Note que os comentários de Design de Referência no Celery apontam para usar o operador `L2Distance` e métricas L2. O índice criado no banco de dados, no entanto, foi instanciado com `opclasses=['vector_cosine_ops']`. Ao rodar a query, as chamadas SQL brutas precisam preferir a distância de Cosseno (`<=>`) para bater no índice correto e evitar Full Table Scan. Ex: `ORDER BY embedding <=> '[0.1...]'`.

## Laboratório Recomendado
Acesse o laboratório de inicialização para visualizar esta busca e o `EXPLAIN`.
`python manage.py shell < docs/manuals/02-engineering/labs/lab_03_rag_visibilidade.py`
