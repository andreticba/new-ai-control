<!-- 06_casos_limite_tecnico.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# 06. Casos Limite Técnico (Edge Cases)
**Público-alvo:** Desenvolvedores Backend / QA
**Tempo de Leitura:** 6 min

Consistente com a visão de Negócios (Manual 05 da Trilha de Produto), este arquivo ilustra no nível de código como o ORM, as Constraints do Banco, e a lógica Vetorial atuam para prevenir acidentes estruturais e violações de escopo.

## 1. Exclusão de Membros ("The Containment Rule" e `on_delete`) ✅
Em conformidade com a LGPD e regras corporativas, se o Administrador Global excluir o registro da `OrganizationMembership` do "Professor", veja como a deleção em cascata (*CASCADE*) e o RAG se comportam no Banco de Dados:

- As subclasses de Membership vinculadas ao projeto que esse usuário possuía **não** serão excluídas pelo CASCADE base de Membership, porque o Django não exclui na cadeia cruzada do UserProfile para Organizações filhas sem gatilhos explícitos.
- Porém, **é garantido** pela regra de integridade do método `clean()` e das lógicas de API que não possa existir uma SquadMembership sem sua equivalente ProjectMembership.
- A restrição principal mora no bloqueio preventivo via Middleware: Ao descadastrar o usuário da raiz (`is_active=False`), a verificação em cascata do Token bloqueia tudo antes que a consulta aos filhos (Squads) sequer inicie.
- Os *DocumentChunks* (Chunks RAG) originados por aquele "Professor" no banco têm chave estrangeira atrelada ao `owner_id`. Eles configuram `on_delete=models.SET_NULL` para que não sumam caso o perfil inteiro da pessoa seja deletado do banco de dados, protegendo a inteligência corporativa.

## 2. A Malha de Roteamento WhatsApp Multi-Tenancy ✅
Quando o Webhook recebe uma mensagem do número `5511000000000@example.com`, e existem DUAS organizações (Clínica A, e Hospital B) que usam a nossa mesma infraestrutura, como o banco não mistura as conversas?

A mágica reside não apenas na FK do `Contact`, mas sim na separação atômica da FK de `Conversation`. No `whatsapp_service.py`, a criação ou resgate de uma conversa exige explicitamente o `organization_id` fornecido pelo Celery com base na URL da Instância que recebeu a mensagem:
```python
conv, _ = Conversation.objects.get_or_create(
    contact=cpn.contact, 
    organization=org,
    defaults={"status": Conversation.Status.ACTIVE_AI}
)
```
Se a Clínica e o Hospital têm o mesmo número salvo em contatos, serão criados dois objetos Conversation paralelos; as lógicas fluem totalmente blindadas.

## 3. Pesquisador Convidado (The Null Context Fallback) 🟡
Se um pesquisador externo é membro apenas de UMA Squad, com *Role* em nível de Squad, ele não deve herdar os poderes macro de "Membro da Organização", por isso usamos a label de Role *Convidado*.
**Limitação do Middleware Atual:**
Nossos testes provaram que, se a API for consultada de forma não intencional via `/api/v1/gateway/`, sem especificar explicitamente por qual Organização o usuário tenta atuar, se ele for Administrador em sua Org de Origem mas Convidado na Org de Destino, o Middleware pode conceder acesso indevido por olhar `.exists()` globalmente nas suas permissões de Admin.
**O Comportamento Correto e ORM Fix:** Todas as views que implementam painéis de Org/Squad DEVEM requerer o HEADER ou parâmetro `organization_id` ou `squad_id` na URL e validar via `_check_permission_in_scope(...)` atrelado ao `ID` ou então filtrar diretamente o queryset base baseando-se na PK.
