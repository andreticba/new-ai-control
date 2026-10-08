<!-- 01-product/05_casos_limite.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
**Commit de referência:** 686d444

# 05. Casos Limite de Negócio (Edge Cases)
**Público-alvo:** Stakeholders, Novos PMs  
**Tempo de Leitura:** 4 min

No mundo corporativo e acadêmico do B2B de IA, regras felizes (Happy Paths) não sustentam os acordos de nível de serviço (SLA). Este documento aborda o que acontece quando vínculos complexos de negócio colidem com as restrições da plataforma.

## Exclusão de Acessos vs Retenção de Documentos (O Problema do Autor) ✅
**O Cenário:** O "Professor Carlos" foi exonerado da Organização "Universidade Federal Demo". Ele produziu dezenas de documentos confidenciais com o seu nome (AuditLog/Owner) durante os meses de Projeto. O que ocorre com os dados?

**A Regra da Plataforma (Containment Rule):**
Quando excluímos ou desativamos a `OrganizationMembership` raiz do Professor, todas as ramificações de Projeto (`ProjectMembership`) e Esquadrão (`SquadMembership`) associadas ao usuário naquela universidade param de conceder acesso **instantaneamente**. A IA bloqueia seu acesso no mesmo milissegundo.

No entanto, em atendimento à soberania de dados do contratante (Tenant), os documentos criados pelo usuário **não são apagados** (Não usamos `CASCADE` para exclusão de membros). Os relatórios da pessoa física permanecem acessíveis ao Squad/Organization para auditoria corporativa contínua.

## Pesquisadores Externos e Convidados ✅
**O Cenário:** O Laboratório A quer compartilhar acesso do seu App apenas com um "Consultor Externo" sem dar a ele acessos aos departamentos de Recursos Humanos e Financeiro da Empresa principal.

**A Solução (External Guest):**
O modelo de dados implementou um sistema rígido à prova de escalonamento indevido de privilégios. Criamos o vínculo da empresa `OrganizationMembership` mas amarramos uma Role `org_guest`. Esse papel significa "Esta pessoa está aqui por educação; bloqueie-a por completo de qualquer listagem macro". Na camada da Membership específica do Squad, ela recebe a permissão que necessita.

## Colisão de Inquilinos no Telefone do Contato ✅
**O Cenário:** E se um "Paciente" (Telefone X) ativado no Hospital (Organization A) amanhã entrar em contato com o WhatsApp da Imobiliária (Organization B) que também usa a Plataforma?
**A Solução:** Cada conversa e contato flui num silo completamente fechado atrelado àquela Organização. O motor de mensagens trata o telefone do Contato como instâncias separadas (graças aos adaptadores que instanciam `ContactPhoneNumber` baseando-se no contexto de `Conversation` de entrada e `Organization`). A plataforma abstrai e cega as operadoras e as instâncias LLMs de outras empresas.
