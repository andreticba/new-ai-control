<!-- research.md | Vitalia SDD v0.6.0 | 20-10-2026 23:32:00(GMT-04:00) -->
> **research.md | Vitalia SDD v0.6.0 | 20-10-2026 23:32:00(GMT-04:00)**

# Technical Research: 006-omnichannel-decoupling

## Decisão 1: Decomposição do Frontend via Compound Components e Custom Hooks
- **Escolhido**: Extrair `useColumnResize`, `useWhatsAppInstance`, `NavRail`, `OmnichannelHeader` e `ColumnSplitter`.
- **Verificado em**: [React 19 Hooks Documentation](https://react.dev/reference/react) e [TanStack Architecture Patterns](https://tanstack.com/query/latest/docs/framework/react/guides/custom-hooks) em 20-10-2026.
- **Justificativa**: Componentes puros de visualização desacoplados de listeners do DOM e chamadas HTTP evitam re-renderizações em cascata, eliminam acoplamento de estados no `page.tsx` e viabilizam testes unitários isolados.
- **Alternativas**:
  - *Context API Global (`OmnichannelContext`)*: rejeitado porque propaga re-renderizações para todos os consumidores durante o arrasto de colunas a 60 FPS.
  - *Manter estados em `page.tsx`*: rejeitado por violar o Princípio da Responsabilidade Única (SRP) e ultrapassar 500 linhas de código.

## Decisão 2: Service Layer Pura no Backend (DRF + Services)
- **Escolhido**: Implementar `InstanceService`, `TakeoverService` e `MessageDispatchService` em `omnichannel/services/`.
- **Verificado em**: [Django Design Patterns: Clean Architecture & Service Layer](https://docs.djangoproject.com/en/5.1/topics/db/transactions/) e Martin Fowler (Service Layer Pattern) em 20-10-2026.
- **Justificativa**: Views do Django REST Framework devem ser cascas finas de validação e roteamento HTTP. Encapsular transações com `select_for_update`, disparos de WebSocket e chamadas a gateways de terceiros (Evolution API) em classes de serviço desacopladas garante testabilidade e elimina código duplicado.
- **Alternativas**:
  - *Lógica em Métodos de Models*: rejeitado porque integrações com Evolution API e emissões de WebSocket não pertencem ao modelo relacional de banco de dados.
  - *Manter nas Views do DRF*: rejeitado porque métodos de View com 100+ linhas dificultam manutenção e isolamento de falhas.

## Decisão 3: Blindagem Anti N+1 no ORM (Princípio P15)
- **Escolhido**: Uso exclusivo de campos já desnormalizados (`last_message_preview`, `last_message_timestamp`) ou instâncias em cache via `prefetch_related('messages')` na serialização da listagem de conversas.
- **Verificado em**: [Django Documentation: Database access optimization (select_related & prefetch_related)](https://docs.djangoproject.com/en/5.1/topics/db/optimization/) em 20-10-2026.
- **Justificativa**: Elimina a consulta oculta `.messages.order_by('-timestamp').first()` que gerava 50+ queries SQL extras a cada carregamento de página, derrubando o tempo de resposta da listagem de conversas para $P95 < 200\text{ms}$.
- **Alternativas**:
  - *Subquery ORM com OuterRef*: mais complexo e redundante, dado que os campos de preview já são mantidos atomicamente na entidade `Conversation`.

## Decisão 4: Segregação Estrita de Serializers Read vs. Write (Princípio P17)
- **Escolhido**: Módulo `serializers/read.py` e `serializers/write.py` com aliases de retrocompatibilidade em `serializers/__init__.py`.
- **Verificado em**: [Django REST Framework Serializer Best Practices (Read/Write Separation)](https://www.django-rest-framework.org/api-guide/serializers/) e OWASP API Security Top 10 (Mass Assignment Mitigation) em 20-10-2026.
- **Justificativa**: Serializers de entrada exigem validação restritiva de tipos e campos permitidos, enquanto serializers de saída aninham metadados enriquecidos para o frontend sem risco de poluição de payloads.
- **Alternativas**:
  - *Serializer único com campos read_only*: aumenta a complexidade de validação condicional e facilita vazamento de campos em updates parciais.
