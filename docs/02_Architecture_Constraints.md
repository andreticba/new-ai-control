<!-- 02_Architecture_Constraints.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 2. Architecture Constraints

## 2.1 Restrições de Software e Hardware
- **Agnosticismo de Hardware:** A plataforma não pode assumir infraestruturas específicas de vendors (como AWS específicas, serviços fechados da GCP). Deve rodar através de contêineres Docker, permitindo orquestração em Kubernetes, Swarm ou simples Docker Compose, para deploy on-premise ou cloud.
- **Python e Django:** O backend central é construído em Python 3.14+ e Django 6.1+, tirando proveito de ecossistemas robustos de ORM, migrações e bibliotecas de segurança (Cryptography, Celery).
- **PostgreSQL + pgvector:** Único banco de dados relacional homologado. Requer extensão `pgvector` para buscas vetoriais nativas e ingestão semântica.
- **Redis:** Mandatório como Message Broker (Celery) e camada de cache/Channels (WebSockets).

## 2.2 Restrições de Segurança (Security by Design)
- **Zero Secrets in Git (P06):** Chaves, tokens e credenciais devem residir exclusivamente em cofres (Vaults) ou variáveis de ambiente (`.env`).
- **Criptografia At-Rest (django-crypto-fields):** Campos de PII (Personally Identifiable Information) devem ser criptografados diretamente na coluna do banco, exigindo carregamento de chaves assimétricas/simétricas via arquivos seguros (extensão `crypto_keys`).

## 2.3 Restrições Organizacionais e de Processo
- **Pipeline SDD (Specification-Driven Development - P01):** Qualquer alteração de código ou arquitetura requer especificação prévia (`spec.md` -> `plan.md` -> `tasks.md`). O código não antecede a especificação.
- **Padrão de Data (P04):** Todo arquivo editado/criado deve possuir o carimbo imutável `GMT-04:00`.

