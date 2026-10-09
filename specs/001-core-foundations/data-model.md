<!-- data-model.md | Vitalia SDD v0.6.0 | 09-10-2026 16:05(GMT-04:00) -->
**data-model.md | AI-Control v0.0.1 | 09-10-2026 16:05(GMT-04:00)**

# Data Model Mutations: Core Foundations

> [!IMPORTANT]
> **Source of Truth**: A estrutura completa de atributos e a Hierarquia 4-Tier já existem e estão implementadas em `core/models.py`. Este documento NÃO recria a modelagem; ele apenas define as **mutações (deltas)** que devem ser aplicadas para efetivar a separação arquitetural proposta.

## 1. Mutações no Bounded Context: `core`

### Modelo: `Organization` (Mantido no `core`)
- **Mutação Estrutural**: Garantir a unicidade do Tenant Interno.
- **Delta**: Inserir `UniqueConstraint(fields=['is_internal'], condition=Q(is_internal=True), name='unique_internal_organization')`.

### Modelo: `AuditLog` (Mantido no `core`)
- **Mutação Estrutural**: Otimização LLM e Imutabilidade.
- **Delta**: Inserir `GinIndex(fields=['metadata'])`. A blindagem `UPDATE/DELETE` será feita via SQL nativo na respectiva migração.

## 2. Extração para Bounded Context: `omnichannel`

Os modelos a seguir existem no `core/models.py` atual. Eles **DEVEM SER MOVIDOS** integralmente para `omnichannel/models.py`. Todos os campos originais de negócio (flags da inteligência conversacional `context_locked`, validação de RAG, campos criptografados de PII) serão estritamente preservados.

### Entidades Transferidas:
1. `Conversation`
2. `Message`
3. `Contact`
4. `OmnichannelPreferences`

### Regra Universal de Mutação Cross-Domain (Soft FKs):
Sempre que uma entidade transferida referenciar o domínio `core` (ex: `organization`), a Foreign Key hard-coded deverá ser esmagada:
- **DE:** `organization = models.ForeignKey(Organization, ...)`
- **PARA:** `organization_id = models.UUIDField(db_index=True)`
