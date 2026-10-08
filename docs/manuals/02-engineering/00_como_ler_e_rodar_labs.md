<!-- 00_como_ler_e_rodar_labs.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# 00. Como Ler e Executar os Laboratórios de Engenharia
**Público-alvo:** Desenvolvedores Backend / Novos Engenheiros
**Tempo de Leitura:** 3 min

A arquitetura do Plataforma (`ai-control`) está firmemente acoplada a princípios de segurança pesada. Para não depender puramente de abstração textual, criamos **Laboratórios Mocks** executáveis. Eles funcionam injetando lógica real do Django sobre um banco de dados temporário limpo.

## 1. Regra de Ouro (Rollback Automático)
Todos os laboratórios foram envolvidos na função `_lab_base.run_lab()`, que executa o script sob `transaction.atomic()` e força propositalmente um erro/exceção limpo ao final. **Isto garante que nada fique salvo no banco de dados da sua máquina.** Você pode rodar esses laboratórios mesmo em um banco populado.

## 2. Pré-requisitos
1. Ambiente Virtual ativado e as dependências Python instaladas (ex: `poetry shell`).
2. Conexão ativa com o PostgreSQL/PGVector configurada e as `migrations` executadas. (O repositório principal deve estar operável).

## 3. Os Quatro Laboratórios Básicos
Sugerimos rodá-los na ordem abaixo. No terminal da raiz do seu projeto (onde fica o `manage.py`), execute:

### Lab 01: Criação da Hierarquia Matricial e ORM
```bash
python manage.py shell < docs/manuals/02-engineering/labs/lab_01_hierarquia_rbac.py
```
*O que você verá:* A criação de toda a árvore, até SQUADs, e o script cuspirá o SQL equivalente para você validar a Query real gerada.

### Lab 02: Resolução de Permissões
```bash
python manage.py shell < docs/manuals/02-engineering/labs/lab_02_permissoes.py
```
*O que você verá:* Testes contra o Middleware Global que verifica o cruzamento de Usuários, Roles, e Slug da Permissão na tabela pivot.

### Lab 03: RAG Isolado (Visibilidade e Filtros vs HNSW)
```bash
python manage.py shell < docs/manuals/02-engineering/labs/lab_03_rag_visibilidade.py
```
*O que você verá:* A busca de Similaridade de Cosseno sendo simulada via ORM (`CosineDistance`) onde PIIs e Chunks proibidos pela SQUAD não chegam aos Top 5. (A query de SQL também está disponível no arquivo `lab_03_rag_visibilidade.sql`).

### Lab 04: Processamento do Pipeline Celery WhatsApp
```bash
python manage.py shell < docs/manuals/02-engineering/labs/lab_04_whatsapp_pipeline.py
```
*O que você verá:* Simulação explícita de uma injeção de payload JSON enviada por webhook. Você verá as entidades de `ContactPhoneNumber` sendo montadas pelo service isoladamente do front e a aplicação da máscara LGPD no log.
