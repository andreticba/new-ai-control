<!-- 04_Solution_Strategy.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 4. Solution Strategy

A estratégia de solução do **Data Vault Agnóstico** baseia-se em quatro pilares fundamentais de arquitetura:

## 4.1 Separação Criptográfica Multitenant
- Ao invés de confiar apenas em filtros lógicos (`tenant_id = X`), a arquitetura aplica criptografia em nível de campo para dados sensíveis.
- Utiliza `django-crypto-fields` para assegurar que violações no banco de dados (ex: dump vazado) não resultem em exposição de PII.

## 4.2 Processamento Assíncrono Desacoplado (Event-Driven)
- O tempo de resposta das APIs de entrada (como o Webhook) deve ser O(1).
- Toda carga pesada (como Ingestão de Dados, chamadas de LLM, relatórios) é descarregada para o `Celery` apoiado no `Redis`.
- Esse desacoplamento protege a aplicação contra indisponibilidade de parceiros (ex: OpenAI cai, o webhook continua aceitando mensagens).

## 4.3 Agnosticismo de Domínio
- Os modelos de banco de dados são nomeados com abstrações generalistas: `Tenant`, `User`, `Profile`, `Interaction`. 
- Nomenclaturas como "Paciente", "Aluno" ou "Cliente Financeiro" não devem existir no núcleo do sistema, permitindo que a mesma codebase atenda setores variados.

## 4.4 Automação via "Docs as Code"
- Documentação não é um wiki separado, vive no repositório.
- Integração de ferramentas como `drf-spectacular` para gerar a interface do Swagger/OpenAPI e `django-extensions` para o Diagrama Entidade-Relacionamento (`ERD.dot`).

