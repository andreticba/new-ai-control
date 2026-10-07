#!/bin/bash
# scripts/generate_docs.sh | AI-Control SDD v0.6.0 | 05-10-2026 11:12(GMT-04:00)

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "Iniciando geração de esquemas..."
mkdir -p docs

# OpenAPI
echo "Gerando OpenAPI schema (swagger.yaml)..."
python3 manage.py spectacular --file docs/swagger.yaml

# ERD
echo "Gerando diagrama ERD (ERD.dot)..."
python3 manage.py graph_models -a --dot -o docs/ERD.dot

echo "✅ Documentação técnica automatizada salva em docs/"
