<!-- quickstart.md | AI-Control v0.0.1 | 13-10-2026 18:05(GMT-04:00) -->
# Quickstart & Verification Guide: Formulários de Governança 4-Tier

**Feature:** `specs/003-frontend-forms`  
**Data:** 13-10-2026  

---

## 1. Pré-Requisitos

1. Backend Django rodando na porta 8000:
   ```bash
   python manage.py runserver 8000
   ```
2. Frontend Next.js 16 rodando na porta 3000:
   ```bash
   cd frontend && npm run dev
   ```
3. Obtenção do token JWT de operador administrador:
   ```bash
   export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"devpassword"}' | jq -r .access)
   ```

---

## 2. Cenários de Validação End-to-End

### Cenário 1: Criação de Nova Organização via API & Reflexo na HUD
```bash
curl -X POST http://localhost:8000/api/v1/workspaces/organizations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hospital Santa Fé",
    "slug": "hospital-santa-fe",
    "org_type": "HEALTHCARE",
    "is_active": true
  }'
```
**Resultado Esperado:** HTTP 201 Created. No frontend (`http://localhost:3000`), a nova organização aparece imediatamente no seletor de workspaces e os cartões atualizam reativamente sem necessidade de F5.

### Cenário 2: Validação da Regra de Contenção P3 (Criação de Squad)
```bash
# Tentativa de criar squad sem projeto válido
curl -X POST http://localhost:8000/api/v1/workspaces/squads/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Squad Órfã",
    "slug": "squad-orfa"
  }'
```
**Resultado Esperado:** HTTP 400 Bad Request ("project_id é obrigatório para manter a integridade da hierarquia P3").

### Cenário 3: Validação Contínua P3 em Membro de Squad
```bash
# Tentativa de alocar usuário em squad sem que ele seja membro do projeto pai
curl -X POST http://localhost:8000/api/v1/workspaces/memberships/squad/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "squad_id": "<UUID_SQUAD>",
    "user_id": 99,
    "role_id": "<UUID_ROLE>"
  }'
```
**Resultado Esperado:** HTTP 400 Bad Request ("O usuário deve possuir vínculo ativo no projeto pai antes de qualquer alocação ou alteração na squad").

### Cenário 4: Onboarding Rápido com Blind Indexing
```bash
curl -X POST http://localhost:8000/api/v1/users/quick-onboard/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dra.luciana",
    "email": "luciana@example.org",
    "full_name": "Luciana Silva"
  }'
```
**Resultado Esperado:** HTTP 201 Created com tokens determinísticos gerados no backend, e seleção automática do novo usuário no combobox do modal.
