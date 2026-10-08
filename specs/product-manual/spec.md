<!-- spec.md | Vitalia SDD v0.6.0 | 07-10-2026 22:25(GMT-04:00) -->
# Especificação de Funcionalidade: Manual de Produto e Histórico Arquitetural

**Data:** 07-10-2026
**Autor/Agente:** Claude Sonnet 5.5 (Antigravity) com o Arquiteto do projeto
**Feature dir:** `specs/product-manual/`
**Base aprovada:** [research-brainstorming.md](./research-brainstorming.md)
**Preset:** `software`

## 1. Contexto e Objetivo (O Quê e Por Quê)

O último ciclo de desenvolvimento (registrado em `AI_AGENT_CONVERSATION.md`) transformou o produto de uma vertical de saúde com papéis fixos em uma **plataforma agnóstica de cofre de dados** com hierarquia de 4 níveis (Organização → Departamento → Projeto → SQUAD), permissões por *slugs*, visibilidade de documentos RAG atrelada a essa hierarquia e comunicação via WhatsApp influenciada por ela.

Hoje não existe documento que explique **como essas peças se relacionam e se comportam**, nem **por que chegamos neste modelo** (tentativas anteriores falharam). A documentação Arc42 em `docs/01`–`12` é referência executiva de alto nível, com densidade e finalidade diferentes, e **não será alterada**.

**Objetivo:** produzir um ecossistema documental próprio, em `docs/manuals/`, composto por:
1. Um **Manual de Produto** baseado em comportamento (para executivos/stakeholders).
2. Um **Manual Arquitetural Deep-Dive** (para engenheiros e novos devs não-clínicos), com exemplos didáticos de profundidade técnica máxima.
3. Um **Histórico de Desenvolvimento** com **Post-Mortems independentes e blameless** das tentativas que falharam, ensinando a cultura de engenharia.
4. Uma trilha de **onboarding acadêmico** (novos pesquisadores) derivada dos módulos anteriores.

**Audiência atual:** confidencial, destinada primariamente aos engenheiros do projeto. Documentação pública é um objetivo futuro (fora do escopo desta entrega).

## 2. Requisitos Funcionais

### 2.1 Estrutura e Segmentação
- **FR-001 (MUST):** O ecossistema documental MUST residir em `docs/manuals/`, com um índice (`README.md`) que direciona cada público ao módulo correto em até 1 clique.
- **FR-002 (MUST):** Os arquivos Arc42 existentes (`docs/01_*.md` a `docs/12_*.md`) MUST permanecer inalterados.
- **FR-003 (MUST):** O conteúdo MUST ser segmentado em módulos separados por público: (a) Stakeholders/Executivos, (b) Engenharia/Novos Devs, (c) Histórico e Post-Mortems, (d) Acadêmicos.
- **FR-004 (SHOULD):** Cada módulo SHOULD declarar no cabeçalho público-alvo, pré-requisitos de leitura e tempo estimado de leitura.

### 2.2 Cobertura de Domínio (Product Manual)
- **FR-005 (MUST):** O manual MUST explicar a hierarquia **Organização → Departamento → Projeto → SQUAD** e as relações entre elas (pertencimento, herança e isolamento).
- **FR-006 (MUST):** O manual MUST explicar o modelo de **Roles e Permissões por slug**, incluindo como uma Role concede permissões, como um usuário acumula Roles em escopos distintos e como a resolução final de acesso é calculada.
- **FR-007 (MUST):** O manual MUST explicar como a **visibilidade de documentos do RAG** é determinada pela hierarquia (quem vê, quem busca, o que o mecanismo de recuperação devolve).
- **FR-008 (MUST):** O manual MUST explicar como a **comunicação via WhatsApp** é influenciada por Organização, Role e SQUAD (identificação do remetente, escopo de resposta, limites).
- **FR-009 (MUST):** O manual MUST descrever o comportamento do sistema em casos-limite: usuário sem SQUAD, usuário em múltiplas organizações, remoção de Role, documento sem escopo, mensagem de remetente desconhecido.

### 2.3 Exemplos Didáticos
- **FR-010 (MUST):** Cada relação do FR-005 a FR-008 MUST ser ilustrada por ao menos 1 exemplo didático narrativo com **personagens e dados fictícios (mocks)**.
- **FR-011 (MUST):** O módulo de Engenharia MUST expor a **profundidade técnica máxima**: consultas SQL nativas (incluindo busca vetorial com `pgvector`), código ORM correspondente, Signals e *middleware* que aplicam o isolamento, mostrando a equivalência entre a abstração e o que ocorre no banco.
- **FR-012 (MUST):** Os exemplos MUST ser extraídos do **código real** do repositório (referenciando arquivo e símbolo), e não inventados a partir apenas de `AI_AGENT_CONVERSATION.md`.
- **FR-013 (MUST):** Nenhum exemplo MUST conter dados clínicos, PII ou credenciais reais; todos os dados MUST ser mocks seguros.
- **FR-014 (SHOULD):** Os exemplos SHOULD incluir ao menos 1 cenário “caminho feliz” e 1 cenário “tentativa de violação bloqueada” por relação.

### 2.4 Histórico e Post-Mortems
- **FR-015 (MUST):** O Histórico MUST apresentar uma linha do tempo das decisões arquiteturais, separando claramente **o que é o produto hoje** do **como chegamos aqui**.
- **FR-016 (MUST):** Cada tentativa arquitetural que falhou (ex.: *roles* hardcoded da vertical de saúde) MUST ter um **Post-Mortem independente**, em arquivo próprio.
- **FR-017 (MUST):** Cada Post-Mortem MUST seguir formato **blameless** e conter: contexto, linha do tempo, causa raiz sistêmica (“como o sistema permitiu a falha?”), o que foi tentado, o que aprendemos, decisão resultante e links para ADR/código afetado.
- **FR-018 (MUST):** Os Post-Mortems MUST ser **amplos, explicativos e didáticos**, adequados a um dev que nunca viu a versão anterior do sistema.
- **FR-019 (SHOULD):** O Histórico SHOULD apontar para ADRs imutáveis quando existirem, e indicar as decisões ainda sem ADR formal.

### 2.5 Qualidade e Governança do Conteúdo
- **FR-020 (MUST):** Toda afirmação sobre comportamento do sistema MUST ser verificável contra o código/testes do repositório; divergências MUST ser sinalizadas no texto.
- **FR-021 (MUST):** Termos de domínio MUST ser consistentes com o glossário existente (`docs/12_Glossary.md`), e termos novos MUST ser adicionados a um glossário do ecossistema de manuais (sem editar o Arc42).
- **FR-022 (SHOULD):** O módulo de Stakeholders SHOULD ser legível sem conhecimento de programação (sem blocos de código).
- **FR-023 (MAY):** Diagramas (ex.: Mermaid) MAY ilustrar a hierarquia e os fluxos de visibilidade.

## 3. Requisitos Não-Funcionais (Restrições)
- **NFR-001:** Respeitar a Constituição (P07 Privacy by Design): nenhum exemplo expõe dado sensível real; menção a isolamento sempre cita `user_id + organization_id`.
- **NFR-002:** Documentação em português (pt-BR); trechos de código e identificadores permanecem no idioma original.
- **NFR-003:** Markdown puro (GitHub Flavored), renderizável no repositório sem ferramentas adicionais.
- **NFR-004:** Confidencialidade: o diretório MUST conter aviso “Confidencial — Uso interno da Engenharia” no índice até decisão futura de publicação.
- **NFR-005:** Manutenibilidade: cada módulo MUST registrar data e commit/versão de referência do código usado nos exemplos, para detecção de obsolescência.

## 4. Histórias de Usuário (User Stories)

**US1 (P1) — Executivo:** Como **executivo/stakeholder**, eu quero entender, sem ler código, como Organizações, Roles, SQUADs, RAG e WhatsApp se combinam, para que eu consiga tomar decisões de produto e explicá-las a clientes.

**US2 (P1) — Dev novo:** Como **desenvolvedor novo, não-clínico**, eu quero um deep-dive com SQL, ORM e Signals reais de cada mecanismo, para que eu consiga implementar e manter a lógica de acesso sem quebrar o isolamento.

**US3 (P1) — Cultura de falhas:** Como **membro da engenharia**, eu quero ler post-mortems blameless de cada tentativa que falhou, para que eu entenda por que o modelo atual existe e não repita os mesmos erros.

**US4 (P2) — Acadêmico:** Como **pesquisador novo**, eu quero uma trilha de onboarding que traduza a arquitetura em conceitos e fluxos, para que eu consiga usar a plataforma e contribuir com a pesquisa.

**US5 (P2) — Mantenedor:** Como **mantenedor da documentação**, eu quero que cada módulo registre sua referência de código e data, para que eu detecte rapidamente conteúdo obsoleto.

## 5. Critérios de Aceite (Acceptance Scenarios)

- **AS-001 (US1)** — Dado um executivo sem formação técnica, quando ele lê o módulo de Stakeholders, então ele consegue responder corretamente, por escrito, a ≥ 80% de um questionário de 10 perguntas sobre quem vê o quê no sistema.
- **AS-002 (US2)** — Dado um dev novo, quando ele segue um exemplo do Deep-Dive sobre visibilidade de RAG, então ele consegue reproduzir em ambiente local o mesmo resultado (documentos retornados) usando apenas os mocks e comandos descritos.
- **AS-003 (US2)** — Dado um exemplo de busca vetorial, quando o leitor compara o código ORM com o SQL nativo apresentado, então a equivalência entre ambos está explícita e os filtros de organização/escopo aparecem nos dois.
- **AS-004 (US3)** — Dado qualquer Post-Mortem, quando auditado contra o template, então ele contém todas as seções do FR-017 e não atribui culpa a pessoas.
- **AS-005 (US3)** — Dado o Histórico, quando um leitor busca a causa de abandono das *roles* hardcoded, então ele a encontra em um arquivo dedicado em até 2 cliques a partir do índice.
- **AS-006 (US1/US2)** — Dado o caso “usuário sem SQUAD”, quando consultado no manual, então ambos os módulos descrevem o mesmo comportamento observável.
- **AS-007 (US2)** — Dado um exemplo de “tentativa de violação bloqueada”, quando executado conforme descrito, então o sistema nega o acesso e o texto descreve o resultado real obtido.
- **AS-008 (US5)** — Dado um módulo, quando um mantenedor abre o cabeçalho, então encontra data e referência de código usadas.
- **AS-009 (FR-002)** — Dado o repositório após a entrega, quando se compara `docs/01`–`12` com o estado anterior, então não há diferenças.
- **AS-010 (FR-013)** — Dado todo o conteúdo entregue, quando varrido por revisão de segurança, então não há PII, dado clínico ou segredo real.

## 6. Success Criteria (Mensuráveis)

- **SC-001:** 100% dos módulos previstos (Stakeholders, Engenharia, Histórico/Post-Mortems, Acadêmico, Glossário, Índice) existem em `docs/manuals/`.
- **SC-002:** 100% das relações de FR-005 a FR-008 têm ao menos 1 exemplo narrativo e 1 exemplo técnico equivalente.
- **SC-003:** 100% das tentativas falhas identificadas possuem Post-Mortem próprio com todas as seções obrigatórias.
- **SC-004:** Um dev novo reproduz o primeiro exemplo do Deep-Dive em ≤ 30 minutos, sem ajuda externa.
- **SC-005:** ≥ 90% dos exemplos de código referenciam arquivo/símbolo existente no repositório na data de entrega.
- **SC-006:** 0 alterações nos arquivos `docs/01`–`12`.
- **SC-007:** 0 ocorrências de dado sensível real nos manuais.

## 7. Edge Cases
- Comportamento do código divergir do que `AI_AGENT_CONVERSATION.md` descreve → prevalece o código; divergência documentada.
- Funcionalidade descrita na conversa não implementada → marcada como “planejada/não implementada” e não ensinada como existente.
- Tentativa falha sem registro suficiente (commits/logs) → Post-Mortem declara explicitamente as lacunas de evidência.
- Código mudar após a entrega → NFR-005 sinaliza obsolescência.

## 8. Fora do Escopo (Out of Scope)
- Alterar, reescrever ou integrar conteúdo aos arquivos Arc42 `docs/01`–`12`.
- Documentação pública para usuários externos (futura).
- Mudanças em código de produção, testes ou esquema do banco.
- Tradução para outros idiomas.
- Material em vídeo, slides ou interface web para os manuais.
- Documentação de fluxos clínicos reais ou dados de saúde.

## 9. Entidades-Chave
- **Organização, Departamento, Projeto, SQUAD:** níveis da hierarquia de escopo.
- **Role / Permissão (slug):** conjunto nomeado de permissões atribuído a um usuário em um escopo.
- **Documento (RAG):** conteúdo vetorizado com visibilidade vinculada a um escopo.
- **Canal WhatsApp:** meio de comunicação cuja identidade/escopo derivam da hierarquia.
- **Post-Mortem:** análise blameless independente de uma tentativa arquitetural que falhou.
- **ADR:** registro imutável e leve de uma decisão arquitetural.

## 10. Assumptions
- A-001: Ainda não há dados sensíveis reais no sistema (confirmado pelo usuário em 07-10-2026).
- A-002: O estado do código em `core/models.py` e módulos correlatos é a fonte da verdade do comportamento atual.
- A-003: Padrão de retenção/versionamento dos manuais: Git, junto ao código.
- A-004: Nomes de arquivos e subestrutura exata de `docs/manuals/` serão definidos na fase de plan.
- A-005: Os Post-Mortems serão derivados de evidências do repositório (histórico git, `AI_AGENT_CONVERSATION.md`, contexto de sessão), sem inventar fatos.

## Suposições Verificadas

- "Post-Mortems blameless (cultura sem culpa)": verificado em https://sre.google/sre-book/postmortem-culture/ em 07-10-2026.
- "ADR (Architecture Decision Records) como registro leve e imutável de decisões": verificado em https://adr.github.io/ em 07-10-2026.
- "Democratização de histórico de falhas no onboarding acelera maturidade": [NEEDS VERIFICATION: a fonte citada no brainstorming (InfoQ) foi indicada apenas como domínio raiz; localizar artigo específico antes de citar como fundamento normativo].
- "Spike.sh / Medium Engineering / TechTarget / Martin Fowler" (rastro do brainstorming): [NEEDS VERIFICATION: URLs específicas não registradas; fundamentação principal passa a ser as duas fontes verificadas acima].
- "`pgvector` com índice HNSW de 768 dimensões": [NEEDS VERIFICATION: confirmar versão, sintaxe de índice e operadores em documentação oficial do `pgvector` durante a fase de plan, antes de escrever os exemplos SQL].
- "EU AI Act / LGPD": não citados como obrigação normativa nesta spec; qualquer menção nos manuais exigirá verificação conforme domínio `regulations`.
