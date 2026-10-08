<!-- GLOSSARY.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
# Glossário da Plataforma

Este glossário unifica os termos técnicos e de negócio para a leitura de todos os Manuais de Produto e Engenharia.

## Identidade e Governança
- **Tenant (Organization):** A empresa ou instituição que contrata a plataforma. Todos os dados da plataforma orbitam de forma criptograficamente isolada sob um Tenant.
- **Department (Departamento):** Estrutura fixa do organograma de uma Organization (ex: Financeiro, Pró-Reitoria). Substitui o termo antigo `Team`.
- **Project (Projeto):** Iniciativa com ciclo de vida. Agrupa Squads.
- **Squad:** Time de execução multidisciplinar alocado dentro de um projeto.
- **Membership (Vínculo):** A conexão de um usuário com um escopo (Organization, Project, Squad). O poder de um usuário (Role) existe apenas *dentro* de uma Membership ativa.
- **Role (Papel):** Define permissões dentro de um escopo (ex: `project_lead`). **Não é um cargo** (JobTitle).
- **JobTitle (Cargo/Função):** Rótulo exibido na interface (ex: Professor, Atendente). Não concede permissões.
- **platform_role:** Papel de nível global atribuído no `UserProfile` apenas a membros internos da plataforma (ex: Suporte Técnico, Sysadmin).

## Dados e IA
- **Usuário Final / Contact:** O consumidor ou cliente da plataforma. É o verdadeiro dono dos dados sensíveis trafegados via integrações (ex: WhatsApp).
- **Data Vault (Cofre de Dados):** O mecanismo que ofusca, fragmenta e criptografa dados para garantir rastreabilidade (LGPD/GDPR), usando o conceito de DataAccessGrant.
- **AI Ingestion (Ingestão de IA):** Coletar dados, formatá-los (Embeddings) e direcioná-los aos motores de IA.
- **RAG (Retrieval-Augmented Generation):** Técnica onde a IA recupera documentos da base de conhecimento (pgvector) antes de formular respostas.
- **Visibility (Visibilidade de Documento):** Nível do RBAC no qual o documento pode ser lido (ex: `SQUAD` significa que só os membros daquele squad o acessam).
- **Denormalização de Escopo:** Cópia dos campos estruturais (organization, department, project, squad) para os *Chunks* (fragmentos vetoriais) a fim de permitir filtragem SQL sem JOINs complexos durante a busca vetorial rápida.
- **Recall:** Taxa de recuperação em buscas vetoriais. Em HNSW com filtros altamente restritivos aplicados após o scan, o *recall* pode diminuir, necessitando de parâmetros ajustados (`iterative_scan`).

## Arquitetura de Software
- **Agnosticismo:** O princípio no qual o software não é amarrado a serviços proprietários restritos (ex: apenas AWS) ou a nichos comerciais fechados (ex: apenas clínicas médicas).
- **Webhook:** O mecanismo pelo qual provedores externos (ex: APIs do WhatsApp, Evolution API) notificam nosso sistema em tempo real sobre eventos, através de requisições HTTP POST.
- **Slug de Permissão:** String única que identifica uma permissão no código (ex: `org.manage_whatsapp`), avaliada pelas *roles* associadas.
- **Design de Referência:** Funcionalidade, interface ou código planejado na arquitetura e presente em comentários ou mockups, mas cuja implementação real em produção ainda não ocorreu (ex: o RAG atual que responde mocks).
