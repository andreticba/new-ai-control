# Mapa de ADRs e Histórico Arquitetural

Lista das Decisões de Arquitetura (Architecture Decision Records) e Post-Mortems que fundamentam a base técnica do `ai-control`.

## Post-Mortems e Lições Aprendidas

- [PM-001: A Falha do auth.Group do Django no Modelo Multi-Tenant](postmortems/pm_001_falha_django_groups.md)
  *Motivação da transição para um modelo RBAC Matricial customizado.*
- [PM-002: Tenant Bleed no Banco Vetorial Externo (IDOR)](postmortems/pm_002_vector_tenant_bleed.md)
  *Motivação da transição de serviços de Vector DB em nuvem para o `pgvector` acoplado ao modelo transacional seguro.*
