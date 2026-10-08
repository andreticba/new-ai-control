<!-- PERSONAS.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Público-alvo:** Todos
**Commit de referência:** 686d444

# Personas e Organizações de Referência

Para manter a consistência dos Manuais de Produto e Laboratórios de Engenharia, todos os exemplos documentais utilizam as seguintes organizações e personagens fictícios. Eles estão codificados no script de seed do ambiente (`core/management/commands/seed_demo.py`), permitindo que desenvolvedores reproduzam os tutoriais passo a passo.

## 1. Perfil Acadêmico: Universidade Federal Demo
**Organização:** `ufdemo` (Universidade Federal Demo)
**Tipo:** ACADEMIC

### Estrutura
- **Departamentos:** PROPESQ (Pró-Reitoria de Pesquisa), PROEC (Extensão), DCOMP (Computação), DENF (Enfermagem), FIN (Financeiro), SGP (Gestão de Pessoas).
- **Projetos e Squads:**
  - **Projeto:** `saude-digital` (Saúde Digital na Comunidade - Extensão)
    - **Squads:** `app-movel` (Squad App Móvel), `campo-coleta` (Squad Campo-Coleta)
  - **Projeto:** `ia-triagem` (IA para Triagem Clínica - Pesquisa)
    - **Squads:** `modelagem` (Squad Modelagem), `dados-clinicos` (Squad Dados Clínicos)

### Personagens (Usuários Mock)
| Usuário | Papel na Organização | Cargo (Job Title) | Depto | Vinculações Relevantes | Contato Fictício |
|---|---|---|---|---|---|
| `prof.ana` | Membro (`org_member`) | Professor | DCOMP | Coordenadora em `saude-digital` (Líder da `app-movel`); Pesquisadora Parceira em `ia-triagem` | `prof.ana@example.org`, JID: `5511000000001@example.org` |
| `prof.carlos` | Gerente (`org_manager`) | Pró-Reitor | PROPESQ | Coordenador Geral de `ia-triagem` | `prof.carlos@example.org` |
| `prof.lucia` | Membro (`org_member`) | Professor | DENF | Vice-coordenadora de `saude-digital`; Líder na Squad `campo-coleta` | `prof.lucia@example.org` |
| `aluno.joao` | Membro (`org_member`) | Aluno de Grad. | DCOMP | Bolsista desenvolvedor na Squad `app-movel` | `aluno.joao@example.org`, JID: `5511000000002@example.org` |
| `aluna.maria` | Membro (`org_member`) | Aluno de Mestrado | DCOMP | Analista de Dados na Squad `modelagem` | `aluna.maria@example.org` |
| `pesq.externo` | Convidado (`org_guest`) | Pesquisador Externo | *N/A* | Membro externo (apenas visualização) na Squad `dados-clinicos` | `pesq.externo@example.org` |
| `tae.paulo` | Membro (`org_member`) | Técnico Administrativo | FIN | Apenas organização | `tae.paulo@example.org` |

---

## 2. Perfil Corporativo: Empresa Demo Ltda
**Organização:** `empresa-demo` (Empresa Demo Ltda)
**Tipo:** COMPANY

### Estrutura
- **Departamentos:** FIN (Financeiro), RH (Recursos Humanos), COM (Comercial), ATD (Atendimento), TI (Tecnologia).
- **Projetos e Squads:**
  - **Projeto:** `implantacao-crm` (Implantação CRM WhatsApp - Corporativo)
    - **Squads:** `integracao` (Squad Integração), `conteudo-bot` (Squad Conteúdo do Bot)

### Personagens (Usuários Mock)
| Usuário | Papel na Organização | Cargo (Job Title) | Depto | Vinculações Relevantes | Contato Fictício |
|---|---|---|---|---|---|
| `gerente.ti` | Gerente (`org_manager`) | Gerente | TI | Líder do Projeto `implantacao-crm` e da Squad `integracao` | `gerente.ti@example.org`, JID: `5511000000003@example.org` |
| `dev.rafa` | Membro (`org_member`) | Analista | TI | Desenvolvedor na Squad `integracao` | `dev.rafa@example.org` |
| `supervisor.bia` | Supervisor (`org_supervisor`) | Supervisor | ATD | PO do projeto; Líder da Squad `conteudo-bot` | `supervisor.bia@example.org` |
| `atendente.leo` | Atendente (`org_agent`) | Atendente | ATD | Apenas organização (Acesso a Inbox) | `atendente.leo@example.org` |
| `analista.rh` | Membro (`org_member`) | Analista | RH | Apenas organização | `analista.rh@example.org` |
| `diretora.fin` | Admin (`org_admin`) | Diretora | FIN | Sponsor/Viewer do Projeto `implantacao-crm` | `diretora.fin@example.org` |
