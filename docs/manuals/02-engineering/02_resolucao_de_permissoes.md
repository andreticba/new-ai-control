<!-- 02_resolucao_de_permissoes.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# 02. Resolução de Permissões
**Público-alvo:** Desenvolvedores Backend
**Tempo de Leitura:** 7 min

O middleware e o sistema de rotas precisam interceptar requisições em tempo real e decidir se a porta abre ou não.

## 1. O Motor Interno: `_check_permission` ✅
Historicamente, o código tentava buscar `if "ADMIN" in user.roles` direto na view (Hardcoded). Hoje, toda a proteção invoca `_check_permission(user, slug_da_permissao)`.
A permissão é uma string com escopo (ex: `org.manage_whatsapp`).

**Como funciona a checagem dupla:**
1. A função verifica se o `user.platform_role` (O Sysadmin global) possui essa permissão.
2. Caso negativo, a função verifica se existe alguma `OrganizationMembership` **ativa** para esse usuário cuja respectiva `Role` detenha essa permissão.

**SQL Gerado via `.exists()`:**
```sql
SELECT 1 AS "a" 
FROM "core_organizationmembership" 
INNER JOIN "core_role_permissions" ON ("core_organizationmembership"."role_id" = "core_role_permissions"."role_id") 
INNER JOIN "core_permission" ON ("core_role_permissions"."permission_id" = "core_permission"."id") 
WHERE ("core_organizationmembership"."is_active" 
  AND "core_permission"."slug" = 'org.manage_whatsapp' 
  AND "core_organizationmembership"."user_id" = 2) 
LIMIT 1;
```

## 2. Limitação Multi-Org e Edge Case F-05 🟡
Conforme os nossos testes levantaram, existe um comportamento conhecido. A função `_check_permission(user, slug)` checa se o usuário tem a permissão em **alguma** Organização. Se um usuário participar da Organização Alfa (como Admin) e da Organização Beta (como Convidado), e ele bater na URL `/api/v1/gateway/` sem passar um cabeçalho identificando qual org ele está operando, o middleware deixará passar (pois ele é Admin em Alfa).
Esta limitação exige que Views subjacentes isolem e validem `user` e `organization_id` juntas sempre que formarem querysets. Apenas confie no middleware para bloqueios macros (ex: O usuário não é admin em nenhum lugar).

## 3. Registro de Falhas (AuditLog) ✅
Se o usuário bater no Gateway sem possuir a permissão `org.manage_whatsapp`, o interceptador emitirá um sinal falho para o `AuditLog`:
`AuditLog.objects.create(action=FAILED_LOGIN, actor=request.user)`.

## Laboratório Recomendado
Acesse o laboratório de inicialização para visualizar esta permissão no terminal.
`python manage.py shell < docs/manuals/02-engineering/labs/lab_02_permissoes.py`
