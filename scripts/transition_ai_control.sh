#!/bin/bash
# transition_ai_control.sh | AI-Control SDD v0.6.0 | 06-10-2026 10:06(GMT-04:00)

echo "Starting AI-Control transition..."

TARGET_DIR="ai-control-transition"

echo "Limpiando diretório de transição..."
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"

echo "Copiando arquivos vitais (Fresh Start)..."
cp -r config/ "$TARGET_DIR/"
cp -r core/ "$TARGET_DIR/"
cp -r telemetry/ "$TARGET_DIR/"
cp -r tests/ "$TARGET_DIR/"
cp -r docs/ "$TARGET_DIR/"
cp -r crypto_keys/ "$TARGET_DIR/"
cp -r scripts/ "$TARGET_DIR/"
cp manage.py "$TARGET_DIR/"
cp requirements.txt "$TARGET_DIR/"
cp docker-compose.yml "$TARGET_DIR/"
cp .env.example "$TARGET_DIR/"
cp Makefile "$TARGET_DIR/"
cp pytest.ini "$TARGET_DIR/"

echo "Removendo caches (pycache)..."
find "$TARGET_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$TARGET_DIR" -type f -name "*.pyc" -delete

echo "Limpando arquivo de tracking de path do django_crypto_fields..."
rm -f "$TARGET_DIR/crypto_keys/django_crypto_fields"

echo "Substituindo 'ai-control' por 'ai-control'..."
find "$TARGET_DIR" -type f -exec sed -i 's/ai-control/ai-control/g' {} +

echo "Substituindo 'ai-control' por 'ai-control' e 'AI-Control' por 'AI-Control'..."
find "$TARGET_DIR" -type f -exec sed -i 's/ai-control/ai-control/g' {} +
find "$TARGET_DIR" -type f -exec sed -i 's/AI-Control/AI-Control/g' {} +

echo "Corrigindo syntax python..."
find "$TARGET_DIR" -type f -name "*.py" -exec sed -i 's/ai-control_/ai_control_/g' {} +

echo "Verificando se o postgres do docker-compose foi ajustado para evitar colisão..."
sed -i 's/POSTGRES_DB: aibase/POSTGRES_DB: aictl_db/g' "$TARGET_DIR/docker-compose.yml" || true

echo "Transição concluída! Arquivos isolados na pasta $TARGET_DIR/"
