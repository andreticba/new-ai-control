<!-- 01-product/02_papeis_e_permissoes.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

# 02. Papéis e Permissões (RBAC Matricial)
**Público-alvo:** Stakeholders, Novos PMs  
**Tempo de Leitura:** 6 min

Um dos maiores legados de dívida técnica do sistema anterior era o uso da taxonomia de "cargos de saúde" atrelada diretamente às permissões de tela. Em suma: o sistema concedia o mesmo nível de permissão "global" baseado em rótulos como "Profissional" ou "Paciente".

O novo motor de acesso é estritamente **Agnóstico e Matricial**.

## A Separação entre Título e Permissão ✅
No painel do produto, é fundamental entender essa dicotomia:

1. **`Role` (Papel Sistêmico)**: Entendido apenas pelo computador. É estático, pré-calculado na base de dados (`Admin`, `Manager`, `Member`, `Guest`). Um `Role` detém `Permissions` (ex: `org.manage_whatsapp`).
2. **`JobTitle` (Cargo/Função)**: Entendido apenas pelo humano. É textual e flexível ("Pró-Reitor de Extensão", "Desenvolvedor Júnior", "Coordenador de TI"). O `JobTitle` **não** concede poderes dentro da plataforma; ele serve apenas para rótulo visual e uso referencial por parte da Inteligência Artificial.

## RBAC Matricial através de Memberships ✅
O sistema implementa o **RBAC Matricial**. O poder do usuário não está atrelado globalmente a si próprio. O poder dele "nasce" na interseção entre o Usuário e o Escopo (a Tabela de Vínculo: `Membership`).

**Exemplo Prático na UFMT (PERSONAS):**
A Professora Ana pode ser `org_member` na *Universidade* inteira. Mas, quando ela atua no *Projeto de Saúde Digital*, a sua `ProjectMembership` indica que o Role dela ali é `project_lead` (ela é a dona do projeto). No entanto, num outro *Projeto de IA Triagem*, ela atua apenas como conselheira com o papel `project_member` (leitura e submissões básicas).
Essa maleabilidade permite segurança absoluta Zero Trust: ao vazar a credencial dela num determinado squad, o atacante jamais ganharia privilégios de Admin em outras áreas onde ela não lidera.

## O Único Papel Global: Platform Role ✅
Fora do domínio dos Tenants (Empresas/Hospitais), existem as `platform_role`. Elas são estritamente reservadas para a equipe interna da empresa de software e suporte técnico de Tier 3. Eles podem acessar todas as configurações subjacentes do banco, contornando a malha de Tenants para realizar Troubleshooting e depuração. É de alto risco e altamente auditado.
