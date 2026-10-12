<!-- quickstart.md | Vitalia SDD v0.6.0 | 11-10-2026 20:48(GMT-04:00) -->
**quickstart.md | AI-Control v0.0.1 | 11-10-2026 20:48(GMT-04:00)**

# Quickstart de Validação: Frontend v1 & Seed Demo

Guia executável para validação ponta a ponta (E2E) dos fluxos entregues neste marco.

---

## Pré-requisitos
- PostgreSQL rodando com extensões ativas (`pgvector`).
- Redis rodando nas portas padrão (6379).
- Virtualenv Python ativo com dependências instaladas.
- Node.js 20+ e npm instalados.

---

## Cenário 1: Execução e Validação do `seed_demo.py`

1. Executar o comando de semeamento:
   ```bash
   ./.venv/bin/python manage.py seed_demo
   ```
2. **Esperado**:
   - Terminal exibe a tabela formatada com as 13 personas canônicas (`prof.ana`, `gerente.ti`, etc.) e a senha padrão `demo1234`.
   - Organização interna (`ai-control`) e operadores (`admin`, `suporte`, `ai-bot`) permanecem intocados.
   - Hashes de Blind Indexing gerados no campo `search_tokens` para todos os usuários demo.
   - Contatos e conversas omnichannel gerados com Soft FK (`organization_id`).

3. Testar a remoção limpa com `--flush`:
   ```bash
   ./.venv/bin/python manage.py seed_demo --flush
   ```
   **Esperado**: Apenas os dados demo de `ufdemo` e `empresa-demo` são expurgados; `admin` de plataforma permanece ativo.

---

## Cenário 2: Emissão e Validação de Tokens JWT na API

1. Iniciar o servidor Django:
   ```bash
   ./.venv/bin/python manage.py runserver 8000
   ```
2. Realizar autenticação da Professora Ana via curl:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "prof.ana", "password": "demo1234"}'
   ```
   **Esperado**: Retorna HTTP 200 com JSON contendo `access` e `refresh`.

3. Consultar o endpoint de perfil agregado `/users/me/`:
   ```bash
   curl -X GET http://localhost:8000/api/v1/users/me/ \
     -H "Authorization: Bearer <TOKEN_OBTIDO>"
   ```
   **Esperado**: Retorna `full_name`: "Profa. Ana Santos", organização `ufdemo`, papel `org_member` e projetos `saude-digital` e `ia-triagem`.

---

## Cenário 3: Inicialização do Frontend e Two-Step Login

1. Navegar até a pasta `frontend/`:
   ```bash
   cd frontend
   npm run dev
   ```
2. Abrir o navegador em `http://localhost:3000/login`.
3. Inserir as credenciais:
   - Usuário: `prof.ana`
   - Senha: `demo1234`
4. Clicar em "Entrar".
5. **Esperado**:
   - Notificação Sonner exibindo "Bem-vindo de volta, Profa. Ana Santos!".
   - Redirecionamento instantâneo para o Dashboard (`/`).
   - Barra superior exibindo o nome, organização "Universidade Federal Demo", badges dos projetos e squads.
   - Botão de Logout remove os tokens e redireciona para `/login`.

---

## Cenário 4: Geração Dinâmica de Tipos TypeScript

1. Na pasta `frontend/`, com o backend ativo na porta 8000 (`DEBUG=True`):
   ```bash
   npm run api:generate
   ```
2. **Esperado**:
   - Arquivo `src/lib/api-schema.d.ts` é gerado/atualizado com sucesso.
   - Compilação TypeScript sem erros (`npm run build` ou `npx tsc --noEmit`).

---

## Cenário 5: Verificação de Segurança do Schema OpenAPI em Produção

1. Iniciar o backend com `DEBUG=False` (modo de produção simulado).
2. Tentar acessar o schema anonimamente:
   ```bash
   curl -i http://localhost:8000/api/schema/
   ```
3. **Esperado**:
   - Retorna HTTP 401 Unauthorized ou HTTP 403 Forbidden.
   - Acesso permitido apenas com cabeçalho de usuário administrador:
     ```bash
     curl -i http://localhost:8000/api/schema/ \
       -H "Authorization: Bearer <TOKEN_ADMIN>"
     ```
