<!-- README.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
# Manuais da Plataforma e Base de Conhecimento

> [!CAUTION]
> **Confidencial — Uso interno da Engenharia e Produto**
> Este diretório contém o conhecimento arquitetural profundo e as estratégias confidenciais do produto. **Não distribua estes arquivos externamente.** Padrões de segurança (como PII mockado) devem ser estritamente observados e verificados pelo `check_manuals.py`.

Bem-vindo à base de conhecimento da Plataforma. Aqui, o comportamento dita o sistema. Esta documentação foi desenhada para nunca ficar obsoleta, integrando-se nativamente com testes automatizados e regras de governança contínuas.

## Legenda de Fidelidade Arquitetural
Para que o leitor saiba o que é real e o que é projeto, todos os documentos (e o inventário de evidências) utilizam os seguintes rótulos:
- ✅ **Implementado**: Funcionalidade em produção, validada por testes e código.
- 🟡 **Parcial**: Código base existe, mas faltam camadas lógicas/integrações finais.
- 🧭 **Design de Referência**: Funcionalidade planejada, comentada, mas ainda sem código ativo no banco ou runtime (ex: RAG mockado, sinais pendentes).

---

## 📚 Índice por Trilha (Público-Alvo)

### 1. Trilha de Produto (Stakeholders & Novos PMs)
Entenda o "O Quê" e o "Por Quê" do sistema, suas hierarquias e as capacidades de negócio da IA.
- [00. Visão Geral](01-product/00_visao_geral.md)
- [01. Hierarquia Organizacional](01-product/01_hierarquia_organizacional.md)
- [02. Papéis e Permissões](01-product/02_papeis_e_permissoes.md)
- [03. Base de Conhecimento e RAG](01-product/03_conhecimento_e_rag.md)
- [04. WhatsApp e CRM Omnichannel](01-product/04_whatsapp.md)
- [05. Casos Limite de Negócio](01-product/05_casos_limite.md)

### 2. Trilha de Engenharia (Desenvolvedores Backend/IA)
Mergulho Técnico "Deep-Dive" no código, Django ORM, banco de dados vetorial, pipelines e arquitetura.
- [00. Como ler e rodar os laboratórios (Labs)](02-engineering/00_como_ler_e_rodar_labs.md)
- [01. Modelo de Dados e RBAC Matricial](02-engineering/01_modelo_de_dados_rbac.md)
- [02. Resolução Dinâmica de Permissões](02-engineering/02_resolucao_de_permissoes.md)
- [03. Busca Vetorial com pgvector e RAG](02-engineering/03_rag_pgvector.md)
- [04. Pipeline WhatsApp Celery/Websockets](02-engineering/04_pipeline_whatsapp.md)
- [05. Signals, Auditoria e Sanitização PII](02-engineering/05_signals_auditoria_sanitizacao.md)
- [06. Casos Limite Técnico e Edge Cases](02-engineering/06_casos_limite_tecnico.md)

### 3. Histórico e Evolução Arquitetural (Todos)
Post-mortems blameless (falhas passadas) e o Mapa de Decisões (ADRs). Essencial para aprender com as tentativas falhas de arquiteturas antigas.
- [Catálogo de Post-Mortems e Cultura](03-history/README.md)
- [ADR Map (Mapa de Decisões)](03-history/adr-map.md)

### 4. Integração Acadêmica
Guias específicos focados no ambiente universitário e pesquisadores.
- [Trilha de Onboarding (Pesquisadores)](04-academic/trilha_onboarding.md)

---

## 🛠️ Recursos Adicionais
- [GLOSSÁRIO DA PLATAFORMA](GLOSSARY.md): Unificação de termos (Tenant, Squad, Membership, RAG).
- [PERSONAS DE REFERÊNCIA](PERSONAS.md): Dados base da `Universidade Federal Demo` e `Empresa Demo Ltda` mapeados no Seed.
- [Inventário de Evidências](../../specs/product-manual/evidence-inventory.md): A "Prova Material" de onde cada regra foi validada.

---

## 🛡️ Como verificar a documentação (Red-Green)
Esta documentação é validada ativamente na esteira CI (via `sdd_judge` / verificador interno). Qualquer desenvolvedor deve assegurar que não foram vazados dados sensíveis ou adicionados links quebrados.

**Para rodar a verificação localmente:**
```bash
python docs/manuals/_verification/check_manuals.py
```

O script testará se:
1. Houve modificação indevida nos Arc42 originais.
2. A árvore completa de arquivos planejada existe.
3. Não existem PIIs reais (e-mail de produção, CPF) escapados nos manuais.
4. Os cabeçalhos padrão (incluindo o commit de referência `686d444`) estão corretos.
