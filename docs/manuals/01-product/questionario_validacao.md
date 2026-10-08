<!-- 01-product/questionario_validacao.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

**Público-alvo:** Novos PMs
**Commit de referência:** 686d444

# Questionário de Validação (Trilha de Produto)

Este questionário visa testar a absorção do conhecimento da Trilha de Produto. Um novo Product Manager deve obter pontuação igual ou superior a 80%.

## Questões

**1. O que significa "Agnosticismo Radical" na nossa arquitetura?**
a) O sistema opera com bancos SQL e NoSQL ao mesmo tempo.
b) O núcleo do sistema não processa regras de negócio fixas de um setor (ex: "Paciente", "Aluno"), delegando esse contexto aos metadados e à IA.
c) A inteligência artificial pode usar qualquer modelo de mercado indiscriminadamente sem limite de custos.

**2. Na hierarquia de 4 níveis, qual é a "Containment Rule"?**
a) Você pode pertencer a um Squad sem pertencer à Organização, caso seja um convidado.
b) Projetos podem conter Organizações dentro deles.
c) Um usuário só pode estar em um nível interno (Squad) se estiver ativo e vinculado a todos os níveis superiores (Projeto, Departamento, Organização).

**3. Qual a diferença fundamental entre `Role` e `JobTitle`?**
a) `Role` é um rótulo visual (ex: "Professor"), enquanto `JobTitle` define as permissões reais no sistema.
b) `Role` (Papel Sistêmico) define o que o usuário pode fazer no código, enquanto `JobTitle` (Cargo) é apenas um texto visual interpretado pelos humanos ou IA.
c) Nenhuma, ambos são os mesmos campos no banco de dados.

**4. O que acontece com as permissões de um "Líder de Projeto" quando ele atua num projeto diferente do seu?**
a) Ele mantém os poderes de líder em toda a plataforma.
b) O acesso é negado até o administrador global autorizar.
c) Devido ao RBAC Matricial, o poder dele é restrito apenas ao escopo onde a Membership dele concede liderança. No outro projeto, ele pode ser apenas um Membro ou Convidado.

**5. Qual a função exclusiva do `platform_role`?**
a) Conceder acesso vitalício à presidência da Organização Cliente.
b) Permitir que clientes criem sub-empresas livremente.
c) Acesso macro para a equipe interna de software/suporte (Tier 3) realizar troubleshooting contornando os limites de Tenant.

**6. Como funciona o "Isolamento de Escopo Garantido" no RAG?**
a) A IA lê o documento inteiro e apaga da resposta o que achar sensível.
b) Filtros SQL restritivos são aplicados junto com o índice vetorial. A engine *não enxerga* fragmentos que não pertençam ao usuário, antes mesmo de enviar à IA.
c) Uma senha é requisitada toda vez que a IA precisa ler um documento protegido.

**7. O que significa a priorização do "Isolamento Absoluto vs Taxa de Recall"?**
a) O sistema é lento, mas seguro.
b) A segurança rigorosa dos filtros (WHERE) aplicados sobre a busca aproximada (HNSW) pode fazer a IA dizer "não encontrei o dado", garantindo que ela nunca alucine vazando dados de outros departamentos, priorizando segurança ao invés de tentar advinhar ("recall").
c) A IA tem memória limitada e esquece informações antigas (recall) para caber novas informações.

**8. Onde ocorre a "Separação de Águas" de Multitenancy no Pipeline do WhatsApp?**
a) No celular do usuário final, que escolhe para qual clínica enviar.
b) No aplicativo da Meta/Facebook.
c) Na nossa retaguarda, através do Gateway, que quebra a URL da "Instância" recebida, extraindo o slug da organização (`ai_control_{org_slug}`).

**9. Se um colaborador (Owner) é demitido, o que ocorre com os documentos que ele criou no Data Vault?**
a) São deletados via CASCADE para conformidade automática.
b) Ficam inacessíveis para sempre e irrecuperáveis.
c) Permanecem intactos e acessíveis aos membros da Organização/Squad, pois a propriedade intelectual pertence à corporação, mesmo que ele perca o login instantaneamente.

**10. Como um "Pesquisador Externo" tem acesso limitado sem visualizar o resto da Universidade?**
a) Ganha a role `org_guest` na Organização (bloqueando acesso macro) e permissões específicas restritas no seu Squad.
b) A IA envia os relatórios por e-mail semanalmente.
c) Cria-se um banco de dados espelho sem restrições.

---
## Gabarito
1-b, 2-c, 3-b, 4-c, 5-c, 6-b, 7-b, 8-c, 9-c, 10-a
