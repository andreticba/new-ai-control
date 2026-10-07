#!/usr/bin/env bash
# setup.sh | Vitalia SDD v0.6.0 | 06-10-2026 16:01(GMT-04:00)

set -e

echo "=> Iniciando setup do instalador AI Control..."

# Cria o .venv se não existir
if [ ! -d ".venv" ]; then
    echo "=> Criando .venv global..."
    python3 -m venv .venv
fi

# Ativa o .venv
echo "=> Ativando .venv..."
source .venv/bin/activate

# Atualiza pip
pip install --upgrade pip

# Instala as dependências efêmeras
echo "=> Instalando dependências do instalador..."
pip install -r ai_control_transition/requirements-setup.txt

# Inicia a CLI Python do instalador
echo "=> Iniciando AI Control Installer..."
export PYTHONPATH=$(pwd):$PYTHONPATH
python -m ai_control_transition.installer.cli
