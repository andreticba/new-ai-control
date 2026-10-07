<!-- 07_Deployment_View.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 7. Deployment View

O ecossistema é projetado para conteinerização total.

## Componentes de Infraestrutura (Nós)

1. **Proxy Reverso / Load Balancer (Nginx / Traefik)**
   - Ponto de entrada SSL/TLS.
   - Roteamento HTTP para aplicação e WS para Daphne.
2. **Application Server (Django/Daphne)**
   - Escalável horizontalmente. Gerencia conexões e APIs.
3. **Message Broker (Redis)**
   - Opera tanto para a fila do Celery quanto como camada do Channels (WebSocket).
4. **Task Runners (Celery Workers)**
   - Processos separados da web. Podem ser escalados de acordo com a carga de Ingestão de IA.
5. **Banco de Dados (PostgreSQL + pgvector)**
   - Armazenamento persistente. Requer extensões instaladas. Criptografia transparente no disco.

## Agnosticismo de Hardware
Por definição de arquitetura, nenhum destes nós exige provedores restritos (como DynamoDB ou SQS). Eles podem subir em uma única VPS de 2GB usando `docker-compose.yml` ou em um cluster EKS/GKE gigante, bastando alterar as variáveis de ambiente.

