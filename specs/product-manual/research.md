<!-- research.md | Vitalia SDD v0.6.0 | 07-10-2026 22:45(GMT-04:00) -->
# Technical Research: Manual de Produto e Histórico Arquitetural

Feature: [spec.md](./spec.md) | Plan: [plan.md](./plan.md)

> Esta feature produz **documentação**, não código. As "decisões técnicas" abaixo tratam de
> formato, ferramental, metodologia de extração de evidência e de **fatos verificados sobre as
> tecnologias que os manuais ensinarão** (resolvendo os `[NEEDS VERIFICATION]` da spec).

---

## Decisão D-01: Formato dos Post-Mortems — Blameless, um arquivo por falha
- **Escolhido**: Post-Mortem blameless em arquivo próprio, template fixo (contexto → linha do tempo → causa raiz sistêmica → o que tentamos → lições → decisão → links).
- **Verificado em**: https://sre.google/sre-book/postmortem-culture/ em 07-10-2026 (página obtida via fetch; cultura *blameless*, foco em causa sistêmica e em compartilhar post-mortems amplamente).
- **Justificativa**: Atende FR-016/017/018. Um arquivo por falha mantém independência e permite linkar a partir do onboarding.
- **Alternativas**:
  - Seção única "Lições aprendidas" no Histórico: rejeitada — contraria a decisão do usuário de post-mortems independentes e amplos.
  - Apenas ADRs: rejeitada — ADR registra a decisão, não a narrativa didática da falha (ver D-02: são complementares).

## Decisão D-02: ADRs como camada complementar (decisão), Post-Mortem como narrativa (falha)
- **Escolhido**: Post-Mortem explica *por que falhou*; ADR (já existentes ADR-001…004 em `docs/09_Architecture_Decisions.md`) registra *o que decidimos*. Cada PM linka ADR correspondente; decisões sem ADR formal são listadas como lacuna (FR-019). **Não** criamos nem editamos ADRs nesta feature (Arc42 intocado).
- **Verificado em**: https://adr.github.io/ em 07-10-2026 (página obtida via fetch; ADR como registro de decisão arquitetural significativa).
- **Justificativa**: Evita duplicar fonte de verdade; respeita FR-002.
- **Alternativas**:
  - Criar novos ADRs em `docs/manuals/`: rejeitada — dividiria o registro de ADRs em dois lugares.

## Decisão D-03: Fonte de evidência para o Histórico (hierarquia de confiança)
- **Escolhido**: ordem de precedência: (1) código atual + testes; (2) diff do git entre `bb10c3b` (first commit, diretório `ai_control_transition/`) e `HEAD`; (3) `AI_AGENT_CONVERSATION.md` (2592 linhas); (4) `docs/09_Architecture_Decisions.md`; (5) contexto de sessão Vitalia.
- **Verificado em**: inspeção local do repositório em 07-10-2026 (`git log`, `git show`, `grep`). Histórico git tem apenas 3 commits (`bb10c3b`, `1ccdb3d`, `686d444`).
- **Justificativa**: O git tem pouca granularidade; o diff `bb10c3b → HEAD` ainda mostra o estado "antes" real (ex.: middleware com `'ADMIN' in roles`, `seed_roles.py` com `PLATFORM_ADMIN`/`PARTICIPANT`). A conversa cobre o *porquê*.
- **Alternativas**:
  - Reconstruir a narrativa só pela conversa: rejeitada — viola FR-020 (verificável contra código).
- **Consequência (Edge Case da spec)**: onde não houver evidência (ex.: legado `vitalia-01`, fora do repositório), o PM declara explicitamente a **lacuna de evidência**.

## Decisão D-04: Estrutura e convenções de arquivos
- **Escolhido**: `docs/manuals/` com 4 trilhas numeradas + `_templates/` + `GLOSSARY.md` + `README.md` (ver plan.md). Markdown GFM; diagramas Mermaid; cabeçalho padrão em cada arquivo (público, pré-requisitos, tempo de leitura, data, commit de referência).
- **Verificado em**: convenção interna do repositório (cabeçalho `<!-- arquivo | versão | data -->` observado em `docs/*.md` e `core/*.py`) em 07-10-2026.
- **Justificativa**: NFR-003/005; legível no repositório sem ferramenta extra.
- **Alternativas**:
  - MkDocs/Docusaurus: rejeitada — fora do escopo (publicação futura) e adiciona dependência.

## Decisão D-05: Mocks seguros via `seed_demo`, não dados inventados em prosa
- **Escolhido**: Exemplos usam personagens/organizações fictícias **alinhados ao `core/management/commands/seed_demo.py` existente** (ex.: projeto "Implantação CRM WhatsApp") para que o leitor reproduza no ambiente local (AS-002, SC-004). Onde o seed não cobrir o cenário, o manual traz um script de laboratório próprio em `docs/manuals/02-engineering/labs/`, sem tocar em código de produção.
- **Verificado em**: leitura local de `core/management/commands/seed_demo.py` (linha 195) em 07-10-2026.
- **Justificativa**: FR-012/013; garante exemplos executáveis.
- **Alternativas**:
  - Exemplos só narrativos/pseudo-código: rejeitada — viola FR-011/012 (profundidade máxima, baseada em código real).

---

## Fatos verificados sobre as tecnologias ensinadas (resolve `[NEEDS VERIFICATION]` da spec)

### F-01: pgvector — operadores e índice HNSW
- **Verificado em**: https://github.com/pgvector/pgvector (README, obtido via raw.githubusercontent.com) em 07-10-2026.
- Operadores: `<->` L2, `<#>` produto interno (negativo), `<=>` **distância de cosseno**, `<+>` L1.
- Similaridade de cosseno: `1 - (embedding <=> query)`.
- Índice HNSW de cosseno: `CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);` com parâmetros `WITH (m = 16, ef_construction = 64)`; `SET hnsw.ef_search = 100;` (ou `SET LOCAL`) ajusta a busca.
- **Alinhamento com o código**: `DocumentChunk.Meta.indexes` em `core/models.py` usa `HnswIndex(m=16, ef_construction=64, opclasses=['vector_cosine_ops'])` ✅ consistente com o README.

### F-02: pgvector — limite de dimensões por tipo
- **Verificado em**: mesmo README, seção Indexing, em 07-10-2026.
- `vector`: até **2.000** dimensões indexáveis; `halfvec`: até 4.000; `bit`: até 64.000.
- **Relevância**: explica a observação registrada em `AI_AGENT_CONVERSATION.md` (linha ~2082): embedding de 4096 dimensões excede o limite do índice `vector` → busca sem índice (varredura completa). O modelo atual usa **768d** (dentro do limite). Candidato a Post-Mortem/lição.

### F-03: pgvector — filtragem com índice aproximado ⚠️ ACHADO RELEVANTE
- **Verificado em**: mesmo README, seção Filtering (Completa via Curl), em 07-10-2026.
- Texto verificado: "With approximate indexes, filtering is applied *after* the index is scanned. If a condition matches 10% of rows, with HNSW and the default `hnsw.ef_search` of 40, only 4 rows will match on average. For more rows, enable iterative index scans (`SET hnsw.iterative_scan = strict_order;`)."
- **Impacto sobre o código e a conversa**: `DocumentChunk` documenta "pré-filtragem SQL **antes** da busca vetorial (P5)" e a conversa afirma "o dado nunca chega à IA / matematicamente impossível". Com HNSW, o filtro `WHERE organization_id=… AND visibility…` é aplicado **após** o scan do índice. **Segurança permanece garantida** (o `WHERE` continua sendo aplicado, nada vaza), mas o **recall** cai drasticamente em filtragem muito seletiva: um usuário com poucos documentos visíveis pode receber **menos de K resultados ou nenhum**, mesmo existindo chunks relevantes, pois o HNSW parou de buscar no `ef_search` padrão (40). O Deep-Dive deve ensinar as soluções recomendadas pela biblioteca: habilitar `hnsw.iterative_scan = strict_order`, usar particionamento ou Partial Indexing.
- **Ação (FR-020)**: o manual sinaliza a divergência técnica na implementação. A solução mitigadora deve ser demonstrada no módulo (ex: `SET LOCAL hnsw.iterative_scan = strict_order;` antes da query).

### F-04: Estado de implementação do RAG no repositório ⚠️ ACHADO RELEVANTE
- **Verificado em**: `grep` local em 07-10-2026.
- **Não existe consulta vetorial implementada no código.** A única ocorrência é um **comentário** em `core/tasks/__init__.py` (linhas 25–30) com `L2Distance` e filtro apenas por `document__organization` (sem `visibility`/squad/projeto) — e o índice HNSW é de **cosseno**, não L2 (o operador `L2Distance` não usaria esse índice). A resposta da IA é **mockada** (`"Resposta automática da IA para: ..."`).
- **Consequência para o Manual**: seguindo o Edge Case da spec ("funcionalidade descrita na conversa e não implementada → marcada como planejada"), o módulo RAG apresentará **(a) o que existe** (esquema `Document`/`DocumentChunk`, campos denormalizados, `Visibility`, `ai_accessible`, índices) e **(b) o contrato de consulta projetado** como "Design de Referência (não implementado)", com SQL/ORM equivalentes, claramente rotulado e validável em laboratório.

### F-05: Resolução de permissões — estado real
- **Verificado em**: leitura de `core/middleware.py` (versão atual) e `git show bb10c3b:ai_control_transition/core/middleware.py` em 07-10-2026.
- **Antes**: `request.user.profile.roles.values_list('name')` e checagem de nome literal `'ADMIN'`/`'PLATFORM_ADMIN'`.
- **Agora**: `_check_permission(user, 'org.manage_whatsapp')` — consulta por **slug**, via `platform_role.permissions` ou `OrganizationMembership(is_active=True, role__permissions__slug=...)`.
- **Limitação a documentar**: a checagem de Organização usa `.exists()` sobre *qualquer* `OrganizationMembership` ativo do usuário — **não valida a qual organização** a rota se refere. Em usuário com múltiplas organizações, a permissão de uma org vale como permissão geral nessa rota. Documentar como comportamento atual/limitação (candidata a lição), sem alterar o código.

### F-06: Versões do stack
- **Verificado em**: https://pypi.org/pypi/Django/json em 07-10-2026 → versão estável corrente **6.1.2**; `requirements.txt` fixa `Django==6.1.*` ✅ compatível.
- `pgvector` (pacote Python, integração Django: `HnswIndex`, `VectorField`) — versão confirmada como `0.5.0` via script PyPI. A extensão no banco de dados está na versão `0.8.7`. Ambas são suportadas para ensino do HNSW e limite de 2000 dimensões. (F-06 verificado e confirmado)

---

## Pendências de verificação remanescentes
| Item | Estado | Ação |
|---|---|---|
| InfoQ / Spike.sh / Medium / TechTarget / Fowler (rastro do brainstorming) | Não verificadas individualmente | **Não serão citadas** nos manuais; base normativa = Google SRE + adr.github.io (verificadas) |
| Versão atual do pacote `pgvector` (Python) | Não extraída | Irrelevante; manuais citam versão fixada em `requirements.txt` |
| README pgvector truncado na seção Filtering | Parcial | Reler o README completo (raw) na Task de escrita do módulo RAG |
