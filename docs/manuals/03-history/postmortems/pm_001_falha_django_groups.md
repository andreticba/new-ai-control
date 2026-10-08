<!-- pm_001_falha_django_groups.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# Post-Mortem 001: A Falha do `auth.Group` do Django no Modelo Multi-Tenant

**Público-alvo:** Desenvolvedores e Engenheiros
**Data da falha/decisão:** 15-08-2026
**Commit de referência:** `686d444`

## Contexto
Durante as fases iniciais do desenvolvimento do `ai-control`, adotamos a funcionalidade nativa do Django de Grupos (`django.contrib.auth.models.Group`) para gerenciar as permissões dos usuários (ex: Grupo "Administradores", Grupo "Participantes"). O objetivo era acelerar o desenvolvimento aproveitando as ferramentas padrão (baterias inclusas) do framework.

## Linha do Tempo
- **Sprint 1:** Implementação do `auth.Group`. Usuários eram adicionados a grupos e recebiam permissões como `core.add_project`.
- **Sprint 3:** Adoção do modelo de Múltiplos Tenants (Múltiplas Organizações usando a mesma infraestrutura, como "Universidade A" e "Hospital B").
- **Sprint 4:** A professora Ana, que era "Administradora" na Universidade A, foi convidada como "Participante" no Hospital B.
- **Incidente:** O sistema concedeu a Ana permissões de Administradora no Hospital B, permitindo que ela apagasse projetos que não lhe pertenciam.
- **Descoberta:** Identificamos que a relação do `auth.Group` é `User <-> Group` globalmente. Não há contexto de "Tenant" (Organização) na relação.

## Causa Raiz Sistêmica
A causa raiz não foi um erro de codificação em um endpoint, mas uma **falha arquitetural de aderência**. O modelo de Grupos do Django foi desenhado para sistemas de um único tenant (Single-Tenant), como painéis administrativos globais (Django Admin), onde o conceito de privilégios é absoluto. No nosso produto, os privilégios são **matriciais e contextuais** (o que o usuário pode fazer depende de *onde* ele está fazendo).

## O que foi tentado
Tentamos criar grupos dinâmicos com o prefixo da organização (ex: `OrgA_Admin`, `OrgB_Participant`). Isso rapidamente explodiu a tabela de grupos e inviabilizou a governança de permissões. A cada novo projeto ou squad criado, a complexidade combinatória criava dezenas de novos grupos, tornando a auditoria impossível.

## O que aprendemos
1. **Evitar Acoplamento com Padrões Globais em Aplicações Multi-Tenant:** Ferramentas nativas de permissão global não escalam para arquiteturas B2B/SaaS onde a identidade do usuário atravessa múltiplos espaços de trabalho.
2. **Autorização Contextual (Matrix RBAC):** A permissão não pertence ao "Usuário", mas sim à intersecção entre o "Usuário", o "Escopo" (Organização, Projeto, Squad) e o "Papel" (Role).

## Decisão Resultante
Foi **estritamente proibido** o uso de `auth.Group` no sistema. A arquitetura migrou para um modelo RBAC Matricial através da classe abstrata `BaseMembership` e do model genérico `Role`, que cruza o Usuário, o Contexto (Tenant/Projeto/Squad) e o Nível de Acesso em tempo de banco de dados.

## Links ADR / Código
- [Mapa de ADRs](../adr-map.md)
- Evidência no código: Acesso via middleware `_check_permission` que valida o escopo em `core.middleware`.

## Lacunas de Evidência
Os logs do incidente no ambiente de homologação foram expurgados devido à política de retenção de 30 dias. A falha foi reconstruída através de testes unitários regressivos (`lab_02_permissoes.py`).
