<!-- research-brainstorming.md | Vitalia SDD v0.6.0 | 07-10-2026 22:18(GMT-04:00) -->
# Brainstorming & Research: Manual de Produto e Histórico Arquitetural

## 🎯 Resumo das Decisões Tomadas

1. **Tratamento de Dados Sensíveis nos Exemplos (Privacidade)**
   - **Decisão:** Como o sistema é agnóstico e sem dados sensíveis reais ainda, utilizaremos **Mocks e Abstrações Seguras**. Nenhum fluxo clínico ou sensível real será simulado, mitigando qualquer risco de quebra de compliance.

2. **Público e Formato do Manual (Múltiplos Níveis)**
   - **Decisão:** Adoção de um modelo **Segmentado (2-Tier/Multi-modular)**. O manual terá frentes separadas para Stakeholders/Executivos (focado em comportamento e produto) e para Engenharia/Academia (Deep-Dive arquitetural).

3. **Integração com a Documentação Arc42**
   - **Decisão:** **Separação Estrutural.** O conteúdo do novo manual não será mesclado aos 12 arquivos do Arc42. Devido à sua densidade e finalidade didática, ele residirá em um ecossistema próprio (ex: `docs/manuals/`), mantendo o Arc42 puramente como referência executiva de alto nível.

4. **Desafio de Escopo e Cultura de Engenharia (Registro de Falhas)**
   - **Decisão:** As tentativas arquiteturais anteriores que falharam (ex: as "Roles" hardcoded da antiga vertical de saúde) não serão escondidas. Elas serão formalizadas por meio de **Post-Mortems Independentes**, amplos, explicativos e didáticos, ensinando ativamente a cultura de engenharia e aprendizado da empresa.

5. **Profundidade Técnica dos Exemplos Didáticos (RAG/WhatsApp)**
   - **Decisão:** **Profundidade Técnica Máxima.** O manual de engenharia não esconderá a complexidade atrás do ORM do Django. Os exemplos didáticos irão expor consultas nativas SQL, lógicas do `pgvector`, Signals e os detalhes cruciais de como o RBAC 4-Tier e as Organizações blindam o sistema em nível de disco.

## 📚 Rastro de Pesquisa (Padrões da Indústria para Cultura de Falhas)

A busca na web confirmou as melhores práticas para documentar falhas arquiteturais, transformando dívida e erro em cultura de engenharia:

| # | Afirmação Técnica | Verificado? | Fonte (Web/Sub-Agente) | Data |
|---|---|:---:|---|---|
| 1 | **Uso de ADRs (Architecture Decision Records):** Falhas e mudanças devem ser mantidas em documentos imutáveis e leves (`/docs/adr`). Evita o *architectural drift*. | ✅ Sim | [TechTarget](https://www.techtarget.com/) / [Martin Fowler](https://martinfowler.com/) | 07-10-2026 |
| 2 | **Post-Mortems Blameless (Sem Culpa):** Incidentes estruturais devem ser descritos focando em *"como nosso sistema permitiu essa falha?"* e não *"quem falhou?"*. | ✅ Sim | [Spike.sh](https://spike.sh/) / [Medium Engineering](https://medium.com/) | 07-10-2026 |
| 3 | **Democratização de Decisões:** Incluir o histórico de falhas e refatorações no onboarding (via Post-Mortems didáticos) acelera a curva de maturidade técnica dos novos devs. | ✅ Sim | [InfoQ](https://www.infoq.com/) | 07-10-2026 |

---
*Este documento atua como base de conhecimento aprovada para a geração do Specification (spec.md).*
