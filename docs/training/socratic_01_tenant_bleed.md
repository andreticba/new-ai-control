<!-- socratic_01_tenant_bleed.md | Vitalia SDD v0.6.0 | 08-10-2026 09:30(GMT-04:00) -->
# Desafio Socrático 01: O Paradoxo da Memória Perfeita

Bem-vindo ao módulo de onboarding avançado. Neste cenário, você será confrontado com um caso real da história do sistema Vitalia. O objetivo não é apenas ler, mas deduzir as falhas antes de expandir a resposta oficial.

## O Cenário (Roleplay)
**Data do Incidente:** Setembro de 2026
**Situação:** Você é o Engenheiro Chefe. A equipe migrou com sucesso milhões de documentos para um poderoso banco de dados vetorial (SaaS externo) que utiliza busca KNN ultrarrápida.
No dia 14 após o lançamento do bot no WhatsApp, um médico da Clínica A pergunta ao bot sobre "políticas de faturamento".
O bot responde brilhantemente. Contudo, o médico percebe que as regras citadas pertencem ao **Hospital B** (concorrente).

Você corre para os logs e nota que o banco transacional (PostgreSQL) aplicou perfeitamente as regras de autorização do usuário na API. Mas a IA ainda vazou os dados.

**Desafio:** Onde está a falha arquitetural? Como um sistema perfeitamente autorizado no Middleware vazou o documento na busca semântica? Pense sobre o "quando" e o "onde" a autorização ocorre.

---

<details>
<summary>👉 Clique aqui apenas quando tiver uma hipótese de arquitetura para a causa raiz.</summary>

### Causa Raiz: Tenant Bleed via Desconexão Transacional
A falha ocorreu devido a um isolamento lógico fraco (IDOR no pipeline RAG). Como o banco vetorial externo não tinha a inteligência nativa de RBAC da nossa API e a aproximação de vizinhos (KNN) ignorava tenants para maximizar performance, a IA resgatou a resposta "matematicamente" mais próxima, ignorando de quem era a posse do documento. 

**O erro não estava no código do endpoint, mas em separar o motor de busca (Vector DB) do motor de autorização (Relacional).**
</details>

<details>
<summary>👉 Qual seria a sua solução? Clique após rascunhar uma abordagem arquitetural.</summary>

### Solução Adotada (A Escolha do Arquiteto)
A equipe de engenharia decidiu abandonar o SaaS externo e internalizar o banco vetorial usando `pgvector` dentro do PostgreSQL.
Isso permitiu unir buscas de texto e vetoriais debaixo da mesma transação SQL. 
A partir desse dia, a busca passou a exigir obrigatoriamente a cláusula `WHERE organization_id = X` em nível de banco de dados (Row-Level Security), garantindo que a filtragem ocorresse antes e não depois da busca de vizinhos.

**Lição:** Segurança (RAG Seguro) requer defesa em profundidade. Metadados pós-filtro na nuvem não escalam com segurança em domínios críticos.
</details>

*Baseado no [Post-Mortem 002: Tenant Bleed](../../manuals/03-history/postmortems/pm_002_vector_tenant_bleed.md).*
