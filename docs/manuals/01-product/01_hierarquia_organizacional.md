<!-- 01-product/01_hierarquia_organizacional.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

# 01. Hierarquia Organizacional
**Público-alvo:** Stakeholders, Novos PMs  
**Tempo de Leitura:** 5 min

Para suportar clientes variados — desde startups enxutas até corporações acadêmicas gigantes como uma Universidade Federal — o sistema implementa uma taxonomia de 4 níveis. ✅

A regra de ouro é a "Containment Rule": não é possível estar num nível interno (ex: Squad) sem antes estar validado e vinculado ativamente a todos os níveis pais.

## Os Quatro Níveis ✅

### 1. Organization (Tenant)
O topo da cadeia. O limite intransponível de dados.
- **Na Empresa:** Empresa Demo Ltda
- **Na Universidade:** Universidade Federal Demo
- **Isolamento:** Toda conversa, todo chunk no RAG e toda chave criptográfica reside dentro dos muros da Organização.

### 2. Department
A estrutura departamental e burocrática *fixa*.
- **Na Empresa:** TI, Recursos Humanos (RH)
- **Na Universidade:** Pró-Reitoria de Pesquisa (PROPESQ), Instituto de Computação (DCOMP).

### 3. Project
Uma iniciativa de médio/longo prazo com vida útil específica e orçamento/alocação de recursos próprios. É um grande "guarda-chuva" operacional.
- **Na Empresa:** Implantação de CRM Omnichannel
- **Na Universidade:** Projeto de Extensão "Saúde Digital na Comunidade"

### 4. Squad
O nível de execução "na trincheira". Um time ágil e temporário trabalhando de forma colaborativa dentro de um Projeto.
- **Na Empresa:** Squad "Integração WhatsApp", Squad "Conteúdo do Bot".
- **Na Universidade:** Squad "App Móvel", Squad "Coleta de Dados em Campo".

## Personas e Exemplos 🧭
Todo o desenvolvimento é balizado pelos cenários construídos no [PERSONAS](../PERSONAS.md). Se uma pessoa é demitida ou desativada na camada da `Organization`, o seu acesso aos `Squads` e `Projects` é cortado atomicamente sem a necessidade de varrer e deletar vínculos granulares individualmente na camada inferior.
