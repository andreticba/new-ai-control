<!-- specs/004-full-stack-realignment/quickstart.md | AI-Control v0.0.1 | 14-10-2026 16:10(GMT-04:00) -->
# quickstart.md | AI-Control v0.0.1 | 14-10-2026 16:10(GMT-04:00)

# Guia de Validação Rápida (Quickstart): Spec 004 — Full-Stack Realignment

**Propósito**: Roteiro executável de comandos e cenários para validação de ponta a ponta do realinhamento da stack.  
**Referências**: [spec.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/spec.md) | [plan.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/plan.md) | [grounding.md](file:///home/andre/projetos/assistidos/ai-control/specs/004-full-stack-realignment/grounding.md)

---

## 1. Pré-Requisitos

Ambiente Docker Compose ativo e saudável:
```bash
docker compose ps
# Serviços esperados: db (PostgreSQL 16 healthy), redis (Redis 7 healthy)
```

Ambiente virtual Python e dependências do frontend instaladas:
```bash
.venv/bin/python --version  # Python 3.14.x
cd frontend && npm run type-check
```

---

## 2. Cenário 1: Validação de Performance Anti-N+1 e Isolamento Multi-Tenant no Backend

Executar os novos testes unitários automatizados do backend:
```bash
.venv/bin/pytest core/tests/test_workspace_performance.py core/tests/test_workspace_isolation.py -v
```

**Resultado Esperado**:
- `test_active_workspaces_query_count_anti_n1`: PASSED (confirma execução em ≤ 4 queries SQL).
- `test_workspace_isolation_blocks_cross_tenant_listing`: PASSED (confirma isolamento estrito de tenant).

---

## 3. Cenário 2: Validação de Compilação Turbopack no Frontend

Executar o build de produção do Next.js 16:
```bash
cd frontend && npm run build
```

**Resultado Esperado**:
- Compilação concluída com sucesso (0 erros de tipagem TypeScript).
- Otimização das rotas estáticas (`/`, `/_not-found`, `/login`) concluída sem exceções de SSR.

---

## 4. Cenário 3: Validação de Reatividade e Carregamento no Navegador

1. Iniciar o servidor de desenvolvimento:
   ```bash
   cd frontend && npm run dev
   ```
2. Acessar `http://localhost:3000/`.
3. **Verificações Visuais**:
   - O HUD carrega instantaneamente sem o erro `No QueryClient set`.
   - A identidade decodificada é apresentada no card `WorkspaceHero`.
   - As métricas numéricas agregadas são apresentadas no `WorkspaceStats`.
   - Ao clicar em "+ Novo Projeto" e salvar, o projeto aparece imediatamente na lista sem necessidade de recarregar a página (reatividade automática via cache do TanStack Query).
   - Ao abrir e cancelar qualquer modal, o formulário é descartado e reaberto 100% limpo (higiene de ciclo de vida).
