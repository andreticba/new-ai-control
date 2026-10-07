<!-- 11_Risks_and_Technical_Debt.md | AI-Control SDD v0.6.0 | 05-10-2026 15:40(GMT-04:00) -->
# 11. Risks and Technical Debt

## Riscos Conhecidos

1. **Complexidade Criptográfica vs Performance**
   - **Risco:** Criptografar campos via `django-crypto-fields` em tempo real pode adicionar *overhead* significativo de CPU no servidor durante picos de ingestão.
   - **Mitigação:** Delegar descriptografias massivas estritamente para o Celery de forma a não travar as interfaces web.
2. **Gerenciamento das Chaves Criptográficas (Vault)**
   - **Risco:** Perda das chaves RSA/AES inviabilizará permanentemente a leitura da base de dados inteira.
   - **Mitigação:** Política estrita de backups a frio das chaves.

## Dívidas Técnicas

- **Ausência Nativa do Graphviz:** O script gerador do banco (`generate_docs.sh`) gera em `.dot`. Renderizações nativas em imagem requerem instalação de bibliotecas de SO fora do Python.
- **Monitoramento Inicial de Webhooks:** O sistema atual de observabilidade é majoritariamente centralizado via log console, sem uma telemetria estruturada pronta (como Grafana ou Datadog) para rastrear engasgos de filas.

