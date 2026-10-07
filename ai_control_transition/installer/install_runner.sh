#!/bin/bash
# install_runner.sh | Vitalia SDD v0.6.0 | 06-10-2026 17:50(GMT-04:00)
#
# Este script é invocado pelo orquestrador Python para executar 
# o pipeline completo de instalação do AI Control.
#
# Comportamento de Erro (Opção A):
# Qualquer comando que falhar (retornar código diferente de zero) irá
# abortar a execução imediatamente graças ao 'set -e'. O trap ERR 
# imprimirá uma mensagem amigável no frontend via SSE.

set -e

# Define a função de captura de erro
handle_error() {
    echo ""
    echo "❌ Ocorreu um erro crítico na linha $1."
    echo "============================================================"
    echo "⚠️ A INSTALAÇÃO FOI ABORTADA!"
    echo "Por favor, verifique os logs acima para identificar a causa."
    echo "Corrija o problema no seu sistema e recarregue a página para tentar novamente."
    echo "============================================================"
    exit 1
}

# Associa a função de erro a qualquer falha no script
trap 'handle_error $LINENO' ERR

echo "=> Iniciando orquestração profunda do AI Control..."
sleep 1

# 1. Configuração do Virtual Environment (.venv)
echo "=> [1/4] Configurando ambiente virtual Python global..."
if [ ! -d ".venv" ]; then
    echo "   Criando diretório .venv..."
    python3 -m venv .venv
else
    echo "   Diretório .venv já existe, reutilizando..."
fi

# Ativa o .venv
source .venv/bin/activate
echo "   Atualizando pip..."
pip install --upgrade pip > /dev/null

# Instala dependências globais se existir requirements.txt
if [ -f "requirements.txt" ]; then
    echo "   Instalando dependências do projeto (requirements.txt)..."
    pip install -r requirements.txt
else
    echo "   [Aviso] Nenhum arquivo requirements.txt encontrado na raiz. Pulando..."
fi

# 2. Instalação do Vitalia SDD Kit
echo "=> [2/4] Instalando e injetando o Vitalia SDD Kit..."
# Chama o instalador do SDD Kit nativo do sistema do usuário, se aplicável
if [ -f "$HOME/.vitalia/bin/install-project" ]; then
    bash "$HOME/.vitalia/bin/install-project"
else
    echo "   [Aviso] Instalador do SDD Kit não encontrado em ~/.vitalia/bin/install-project."
    echo "   Pulando injeção do kit (ele pode já estar instalado no projeto)."
fi

# 3. Orquestração Docker Compose
echo "=> [3/4] Subindo containers da infraestrutura via Docker Compose..."
if [ -f "docker-compose.yml" ]; then
    # O sinal -d roda em background (daemon) e libera o terminal
    # --build garante que a imagem do backend pegue o .env mais novo ou código modificado
    docker compose up -d --build
    echo "   Aguardando 10 segundos para a inicialização dos bancos de dados..."
    sleep 10
else
    echo "   [Aviso] docker-compose.yml não encontrado na raiz! Pulando containers..."
fi

# 4. Migrações e Inicialização do Banco (Django)
echo "=> [4/4] Aplicando migrações do banco de dados (Django)..."
if [ -f "docker-compose.yml" ]; then
    echo "   Tentando executar migrações no serviço 'web' via Docker..."
    # Tenta migrar no docker. Se falhar (ex: usuário roda django localmente fora do docker), tenta fallback local.
    docker compose exec -T web python manage.py makemigrations && python manage.py migrate || {
        echo "   [Aviso] Falha ao rodar migrate no serviço 'web'. Container não encontrado ou indisponível."
        echo "   Executando migrações localmente (fallback)..."
        if [ -f "manage.py" ]; then
            python manage.py migrate
        else
            echo "   [Erro] manage.py não encontrado localmente."
            exit 1
        fi
    }
elif [ -f "manage.py" ]; then
    echo "   Executando migrações localmente (sem docker)..."
    python manage.py makemigrations && python manage.py migrate
else
    echo "   [Aviso] manage.py não encontrado. Nenhuma migração Django realizada."
fi

echo "============================================================"
echo "=> Instalação concluída com sucesso!"
