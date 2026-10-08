<!-- socratic_02_django_groups.md | Vitalia SDD v0.6.0 | 08-10-2026 09:30(GMT-04:00) -->
# Desafio Socrático 02: O Administrador Acidental

Neste módulo, revisaremos uma escolha clássica de frameworks e como ela se comportou quando o negócio escalou de um sistema simples para B2B.

## O Cenário (Roleplay)
**Data do Incidente:** Agosto de 2026
**Situação:** O sistema foi construído rapidamente usando o padrão ouro do framework: os grupos de permissão nativos (`django.contrib.auth.models.Group`). Os usuários eram "Administradores" ou "Participantes". Tudo funcionava perfeitamente na Sprint 1.

Na Sprint 3, o sistema virou Multi-Tenant.
Na Sprint 4, a usuária Ana, que é "Administradora" da Universidade A, foi convidada para ser apenas "Participante" em um projeto pequeno do Hospital B.
Minutos depois, recebemos um alerta: Ana conseguiu deletar os faturamentos do Hospital B.

Você audita o código e percebe que ela foi corretamente convidada como Participante.
O código do endpoint verifica `@permission_required('core.delete_invoice')`.

**Desafio:** Se ela foi convidada corretamente, por que ela pôde deletar o faturamento? Pense sobre a natureza da ferramenta nativa que foi usada e o que significa "Contexto" em Multi-Tenant.

---

<details>
<summary>👉 Tem uma hipótese sobre o acoplamento do framework? Clique para comparar.</summary>

### Causa Raiz: Permissões Globais vs Contextuais
A falha ocorreu porque a relação nativa do `auth.Group` é `User <-> Group` globalmente. Se a Ana é colocada no grupo "Administradores" na Universidade A, o sistema (e o decorador padrão do Django) apenas pergunta: "A Ana é Administradora?" e recebe "Sim" como resposta. A ferramenta não sabia perguntar "A Ana é Administradora **AQUI**?". 

**O erro foi arquitetural:** usar ferramentas de Single-Tenant em arquiteturas B2B causa falha sistêmica.
</details>

<details>
<summary>👉 Como você redesenharia o RBAC? Clique para ver a decisão final.</summary>

### Solução Adotada (A Escolha do Arquiteto)
A equipe baniu completamente o uso de `auth.Group` no sistema Vitalia.
Migramos para um modelo **RBAC Matricial**, onde a permissão não pertence ao Usuário, mas à interseção do triângulo: `Usuário + Escopo (Tenant/Projeto) + Role`. 

Criamos a classe `BaseMembership` e middleware próprio (`_check_permission`), forçando que cada chamada no backend passe o ID do tenant ou projeto como contexto para validar a permissão localmente, não globalmente.

**Lição:** A conveniência das baterias inclusas de um framework não deve ditar a arquitetura corporativa do projeto.
</details>

*Baseado no [Post-Mortem 001: Falha Django Groups](../../manuals/03-history/postmortems/pm_001_falha_django_groups.md).*
