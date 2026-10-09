<!-- alinhamento.md | Atualizado em: 09-10-2026 15:13:54(GMT-04:00) -->
**alinhamento.md | AI-Control v0.0.1 | 09-10-2026 14:55(GMT-04:00)**

# Prancheta de Alinhamento: Refatoração AI-Control (v0.6.0)

## 1. Fonte da Verdade Estrutural: A Base Atual (`ai-control`)
Diferente das assunções anteriores, o código do projeto atual `ai-control` **está funcionando corretamente** com o Evolution API e já possui a base estrutural correta. Ele não será descartado, mas sim refatorado in loco.
- **Hierarquia 4-Tier:** O modelo `Organization`, `Department`, `Project`, e `Squad` (existentes no `core/models.py`) representam a arquitetura RBAC correta e são o alicerce absoluto.

## 2. Injeção de Inteligência do Legado Superior
O arquivo `AI-Control 08-11-2025-21-25.md` contém um código mais antigo, mas que detém a **estratégia de negócios e orquestração de IA superior**. As lógicas extraídas de lá e mescladas na base atual:
- **`core.Organization`**: Receberá a trava `UniqueConstraint(is_internal=True)` para blindar o Tenant da plataforma, além da transferência da propriedade de negócio (`reopen_conversation_timeout_hours`) para uma entidade isolada.
- **`Conversation` (Context Lock e RAG)**: A lógica avançada da IA utiliza a flag `context_locked` (bypass de roteamento semântico), `locked_at`, `current_intent` e `consecutive_rag_failures`. Esses campos e suas mecânicas processuais (`process_incoming_message`) moldarão as regras no novo módulo.

## 3. Isolamento de Domínios (Bounded Contexts)
A base atual sofre de acoplamento monolítico (tudo no `core`). Aplicaremos a extração de domínios sem quebrar o Evolution API, utilizando estritamente **Soft Foreign Keys (UUIDs)**:
- **`core`**: Restrito a RBAC, LGPD, Consentimentos e Auditoria.
- **`omnichannel`**: Novo app para hospedar `Contact`, `Conversation`, `Message` e `OmnichannelPreferences` (antigas regras de negócio da Organization).
- **`knowledge_hub`**: Novo app para lidar com vetores RAG (`Document` e `DocumentChunk`).

## 4. O Paradoxo do Ledger Imutável e a LGPD (AuditLog)
O `AuditLog` requer atenção dupla. A versão do legado é focada em acessos simples, enquanto a versão do `ai-control` possui eventos complexos de IA.
- **A Abordagem Híbrida**: Juntaremos as duas visões.
  1. **Velocidade**: Implementação do `GinIndex` do Postgres na coluna JSONB de metadados para auditorias de LLM em tempo real.
  2. **Imutabilidade Real**: Criação de uma migração customizada com `Trigger` SQL no Postgres bloqueando preventivamente comandos `UPDATE` e `DELETE` na tabela `core_auditlog`.
  3. **Esquecimento (LGPD)**: O cumprimento do Direito ao Esquecimento ocorrerá via *Crypto-Shredding* (as PIIs nunca ficam em texto claro; exclui-se a chave de indexação cega que anonimiza irrevogavelmente os rastros no ledger).

## 5. Decisões do Brainstorming Socrático (Grounding)
1. **Reinício Limpo e Dados Básicos**: Confirmada a limpeza completa (Reset Greenfield) da base de dados atual. A recriação dos dados fundamentais (organização interna, papéis básicos) está garantida pela própria migração `0001_initial.py` e por scripts de seed.
2. **Comunicação Cross-Domain (Preferences)**: O acoplamento indireto será feito via **Signals Inter-Apps**. Quando uma `Organization` for instanciada no `core` (ex: via Admin), um signal disparará a criação do `OmnichannelPreferences` no novo app `omnichannel`, mantendo os domínios isolados.
3. **Isolamento de Worker (SC-003)**: A exigência de isolamento do processamento assíncrono da IA (`context_locked` triage) será cumprida através de um **DB Redis Dedicado** exclusivo para o Celery do `omnichannel`.

## 6. Próximos Passos
O próximo passo formal no pipeline SDD é alinhar os testes e gerar o `tasks.md`, guiando a implementação atômica dessa fusão no próprio repositório `ai-control`.

## 7. Critérios de Sucesso e Mapeamento de Fontes (Anti-Alucinação)
Para evitar ambiguidades e alucinações na entrega final, o Agente executor DEVE observar o seguinte mapeamento de fontes da verdade:
- **Origem do Código-Base Estrutural**: Vem estritamente do arquivo ativo `core/models.py`. O Agente não deve recriar a roda, mas sim usar as entidades físicas já declaradas ali.
- **Origem da Inteligência de Negócio**: Vem do arquivo raiz `AI-Control 08-11-2025-21-25.md`. A lógica documentada neste legado prevalece para orquestração de IA.
- **Critério de Sucesso Definitivo**: O código final refatorado (ao término do `tasks.md`) **deve refletir a realidade arquitetural documentada nos manuais e no Arc42 presentes na pasta `docs/`**. Qualquer divergência com os manuais de `docs/` constitui falha da tarefa.
