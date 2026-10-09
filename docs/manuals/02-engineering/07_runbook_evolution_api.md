<!-- 07_runbook_evolution_api.md | Vitalia SDD v0.6.0 | 09-10-2026 18:50(GMT-04:00) -->

# 07. Runbook: Teste de Integração e Instalação do Zero (E2E)
**Público-alvo:** Engenheiros SRE, Desenvolvedores Backend e QA
**Tempo de Leitura:** 20 min

Este documento é o manual oficial de Instalação do Zero e testes fim-a-ponta (E2E) da integração com a Evolution API. Desenvolvido para abranger o ecossistema híbrido onde o **Django e o Celery rodam nativamente na máquina hospedeira (Bare Metal / Host)**, enquanto dependências de infraestrutura pesada (Postgres, Redis, Evolution) sobem via containers.

---

## 1. Arquitetura Refatorada (O Que Estamos Testando)

Antes de iniciar, tenha em mente a arquitetura fundamental que foi refatorada para suportar a alta escala:
1. **Soft FKs (`UUIDField`):** O módulo `omnichannel` interage com o `core` através de UUIDs puros, isolando completamente o CRM.
2. **Workers Isolados (SRE):** O Celery dedicado ao omnichannel roda na fila local através da variável `CELERY_OMNICHANNEL_REDIS_URL`.
3. **Database Seed Nativo:** O script Greenfield cria e alimenta as tabelas automaticamente na primeira migração (`0001_initial.py`).
4. **Imutabilidade (AuditLog):** Protegido por uma *Trigger* PostgreSQL contra deleção e update.

---

## 2. Instalação do Zero (Copiando para Outra Máquina)

Se você copiou a pasta deste projeto para um novo servidor ou máquina de desenvolvimento, siga estes passos para inicializá-lo completamente do zero.

### 2.1. Pré-Requisitos da Máquina
- **Python 3.14+** instalado nativamente.
- **Docker e Docker Compose** (para infraestrutura).
- (Opcional, mas recomendado) Bibliotecas de compilação do PostgreSQL caso o `psycopg2` precise ser construído: `sudo apt install libpq-dev gcc`.

### 2.2. Preparando o Ambiente Python (Host)
No diretório raiz do projeto copiado, instale o ambiente virtual e as dependências:

```bash
# 1. Cria e ativa o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# 2. Instala os pacotes
pip install -r requirements.txt
```

### 2.3. Configurando as Variáveis de Ambiente e Criptografia
A aplicação depende de chaves de criptografia (`django-crypto-fields`) e um arquivo `.env` bem configurado.

```bash
# 1. Copie o arquivo de exemplo
cp .env.example .env

# 2. Se necessário, gere as chaves locais do Data Vault
# ATENÇÃO: Se for um backup real, você deve COPIAR a pasta `crypto_keys/` da máquina origem.
# Se for um ambiente do zero, rode o comando abaixo para gerar novas chaves:
python manage.py generate_crypto_keys
```

### 2.4. Subindo a Infraestrutura de Base (Docker)
Como você roda o Django e o Celery no host, o Docker Compose servirá **apenas** para fornecer os bancos de dados e a Evolution API.

> 💡 **Nota sobre Rede (`network_mode: "host"`):** No nosso `docker-compose.yml`, a Evolution API está configurada nativamente com `network_mode: "host"`. Isso resolve a maioria dos problemas de conectividade em ambientes híbridos (WSL2/Linux). O container passa a compartilhar a pilha de rede da sua máquina. Consequências diretas: a Evolution API consegue disparar webhooks direto para `localhost:8000` (seu Django rodando fora do container) e acessa o PostgreSQL em `localhost:5432` sem a necessidade de bridges ou mapeamento de portas (`ports:` não é necessário).

```bash
# Sobe o Postgres (com pgvector), o Redis e a Evolution API em background
docker compose up -d postgres redis evolution-api
```
*(Verifique no seu `docker-compose.yml` se os nomes dos serviços correspondem a estes. O importante é não subir os serviços do `django` e `celery_worker` que estiverem declarados lá).*

### 2.5. Populando o Banco Greenfield (Reset Limpo)
Agora, executamos a migração nativa do Django no Host. O Seed de dados será engatilhado automaticamente.

```bash
# Certifique-se de que o .venv está ativo
python manage.py migrate
```
> **Nota de Sucesso:** Você deverá ver no console o print da criação da Organização Interna e dos usuários `admin` e `suporte`.

---

## 3. Caminho Feliz (Iniciando e Testando)

Com o ecossistema instalado, vamos iniciar os processos no Host e conectar o WhatsApp.

### Passo 3.1: Subir os Workers do Celery (Abertos em terminais separados)
Para evitar que o tráfego omnichannel afete os processos do Core, inicie o Celery separadamente.

**Terminal 2 (Celery Padrão - Core):**
```bash
source .venv/bin/activate
celery -A config worker -l INFO -Q celery
```

**Terminal 3 (Celery Omnichannel):**
```bash
source .venv/bin/activate
# Passamos a flag indicando o worker isolado
WORKER_TYPE=omnichannel celery -A config worker -l INFO -Q omnichannel
```

### Passo 3.2: Subir o Django
**Terminal 4 (Servidor Web):**
```bash
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Passo 3.3: Conectando a Evolution API (WhatsApp)
A Evolution API estará rodando no Docker (geralmente mapeada para porta `8080`).

1. Acesse o painel da Evolution (ou use requisições via Postman/cURL) para criar sua instância (Ex: `ai_control_teste`).
2. Vincule a URL de Webhook para o seu Django hospedeiro.
   Graças ao `network_mode: "host"` configurado no Docker, a Evolution API enxerga a sua rede local diretamente. Portanto, a URL do webhook apontará para o host de forma orgânica:
   `http://localhost:8000/api/v1/webhook/whatsapp/`
   *(Atenção: Se você estiver usando Mac ou não possuir suporte total ao modo host, e a conexão for recusada, altere para `http://host.docker.internal:8000/...`).*
3. Gere e capture o QR Code com o seu celular.
4. Envie uma mensagem pelo WhatsApp.

---

## 4. Troubleshooting e Debug Avançado

### Problema: Evolution API diz que não alcança o Webhook
- **O que é:** A Evolution pode não estar resolvendo o `localhost:8000` caso a sua plataforma de Docker não suporte perfeitamente o `network_mode: "host"` (mais comum no Docker Desktop para Mac ou versões antigas do Windows).
- **Solução:** No `docker-compose.yml`, remova ou comente a linha `network_mode: "host"`, reinicie o container, expor as portas manualmente (`ports: - "8081:8081"`) e volte a usar a ponte clássica `http://host.docker.internal:8000` (ou o IP real da máquina na LAN, ex: `192.168.0.X`) lá na URL do webhook.

### Problema: "type vector does not exist" no Migrate
- **O que é:** O container do Postgres que você subiu não está usando a imagem com o `pgvector` ativado.
- **Solução:** No seu `docker-compose.yml`, verifique se o banco está utilizando a imagem `pgvector/pgvector:pg16` em vez da imagem padrão `postgres`. Derrube o banco (`docker compose down -v`) e suba novamente.

### Problema: A mensagem chega, mas não entra no Chat
- **O que é:** O Celery não recebeu ou engasgou com a mensagem.
- **Diagnóstico:** Olhe os logs no Terminal 3 (Celery Omnichannel).
- **Solução:** Verifique se as variáveis `CELERY_OMNICHANNEL_REDIS_URL` e `REDIS_URL` no `.env` do seu Host estão apontando para o Redis do Docker (`redis://localhost:6379/0`).

### Validação da Imutabilidade (AuditLog)
Para comprovar que as travas de banco funcionaram nesta nova máquina:
```bash
python manage.py shell
```
```python
from core.models import AuditLog
# Forçando uma quebra de LGPD:
audit = AuditLog.objects.first()
if audit:
    audit.delete() # Deve estourar: "AuditLog is immutable. UPDATE or DELETE operations are not allowed."
```

---

> **Nota de SRE:** Para produção ou máquinas onde você deixará o sistema online permanentemente, lembre-se de configurar serviços como `systemd` ou `supervisor` para gerenciar os processos do Celery e o Gunicorn (ao invés do `runserver`), a fim de garantir resiliência aos reboots.
