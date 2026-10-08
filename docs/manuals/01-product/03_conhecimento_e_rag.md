<!-- 01-product/03_conhecimento_e_rag.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

# 03. Base de Conhecimento e RAG Seguro
**Público-alvo:** Stakeholders, Novos PMs  
**Tempo de Leitura:** 7 min

A IA atua lendo o banco de dados e utilizando essas informações cruas para responder. Mas como garantir que a IA não leia a folha de pagamento de um departamento e responda isso para um estagiário na interface?

## A Busca Vetorial (RAG) 🧭
O paradigma implementado se chama RAG (*Retrieval-Augmented Generation*). Funciona em duas fases:
1. O texto real do documento da empresa (ex: PDF de folha de pagamento) é particionado em fragmentos menores chamados *Chunks*.
2. Esses *chunks* viram números vetoriais matemáticos (Embeddings, usando o padrão `Nomic-768d`).
3. Ao enviar uma pergunta à IA, o sistema realiza uma busca de similaridade, traz os *Chunks* pertinentes e anexa na memória da IA antes de responder.
*Nota: a orquestração completa ainda está em Design de Referência e é simulada por um Mock em produção atual.*

## Isolamento de Escopo Garantido (O Segredo da Segurança) ✅
Para garantir segurança inquebrável, nós implementamos a **Denormalização de Escopo** e a **Visibilidade Estrutural**.

Todo documento e chunk criado herda e "carimba" fisicamente de qual Organização, Departamento, Projeto e Squad ele veio. Ele possui o metadado `Visibility` definindo se ele pode ser lido apenas por membros do seu Squad restrito ou se pode ser lido por qualquer membro do seu Projeto maior.

Quando o sistema busca os chunks, nós aplicamos **Filtros SQL Duros** *junto* com o indexador (`pgvector`). A engine vetorial *só enxerga* os vetores que pertencerem exatamente às Memberships da qual aquele usuário (ou atendimento humano) faz parte. Se o estagiário perguntar sobre a folha de pagamento, os dados confidenciais são excluídos do resultado da busca **antes de chegarem na IA**. Para a Inteligência Artificial, é como se os documentos da Diretoria Financeira nunca tivessem existido.

## O Compromisso com a Taxa de Recall 🟡
Um ponto importante em Produto: ao aplicar os filtros rigorosos de segurança (WHERE) sobre as buscas vetoriais eficientes do `pgvector`, pode haver uma ligeira degradação técnica em encontrar dados raros. Conforme verificado por nossa equipe técnica, a filtragem vetorial ocorre de forma "Iterativa" devido aos índices aproximados (HNSW). Nossa missão de Produto é sempre priorizar o isolamento absoluto de segurança, mesmo ao custo de a IA dizer "não encontrei", em detrimento de uma IA com vazamento e hiper-alucinação de privilégios.
