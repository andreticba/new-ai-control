-- docs/manuals/02-engineering/labs/lab_03_rag_visibilidade.sql
-- Este arquivo demonstra a busca vetorial real com pgvector, usando o operador de cosseno (<=>) e isolamento RAG.

-- 1. Explicação do plano de execução
EXPLAIN (ANALYZE)
SELECT 
    id, 
    content, 
    1 - (embedding <=> '[0.1, 0.2, 0.3]'::vector) AS cosine_similarity
FROM core_documentchunk
WHERE organization_id = (SELECT id FROM core_organization WHERE slug = 'ufdemo')
  AND visibility IN ('ORGANIZATION', 'PROJECT', 'SQUAD')
ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector
LIMIT 5;

-- 2. Mitigação do problema de recall em HNSW com filtros severos
SET LOCAL hnsw.iterative_scan = strict_order;
SELECT 
    id, 
    content
FROM core_documentchunk
WHERE organization_id = (SELECT id FROM core_organization WHERE slug = 'ufdemo')
ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector
LIMIT 5;
