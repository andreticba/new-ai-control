<!-- 05_signals_auditoria_sanitizacao.md | Vitalia SDD v0.6.0 | 08-10-2026 00:00(GMT-04:00) -->
<!-- Commit de referência: 686d444 -->

# 05. Signals, Auditoria e Sanitização PII
**Público-alvo:** Desenvolvedores Backend e Operações
**Tempo de Leitura:** 5 min

Manter a confiabilidade de dados médicos e interações confidenciais exige mecanismos subjacentes do sistema que interceptam eventos, mascam dados confidenciais (*PII: Personally Identifiable Information*) em logs, e gravam trilhas de auditoria (*Audit Log*).

## 1. Mitos e Verdades: A Ausência de Signals 🧭
É comum em tutoriais de projetos legado da Plataforma citar a dependência forte de "Signals" do Django (ex: `@receiver(post_save, sender=Conversation)`).
**A Verdade Atual:** Nosso levantamento de inventário não identificou nenhum uso de `@receiver`/Signals atrelado a processamento principal da orquestração. O código que delega IA, webhooks e mensagens não opera em Signals. Essa arquitetura favorece a rastreabilidade via Celery Tasks diretas ou em métodos de negócio dos Serviços (ex: `WhatsAppService`), o que evita surpresas ocultas causadas por post_saves indiretos de Signals perdidos no ecossistema. Use Signals como Design de Referência apenas quando explicitamente projetado para desacoplamentos passivos que não interfeiram no fluxo Crítico.

## 2. AuditLog (Trilha de Auditoria) ✅
O modelo `AuditLog` no `core/models.py` é o coração da rastreabilidade. Ele é estático, infalível e é anexado sempre no contexto da Requisição.
No Gateway de Autenticação/Middlewares, qualquer requisição que tentar bater na API que rege o acesso principal do projeto e for rejeitada por escassez de Permissões ou Token emitirá automaticamente um registro em banco de dados:
`AuditLog.ActionType.FAILED_LOGIN`.
Qualquer desconexão de whatsapp ou queda também vai pro `AuditLog` via webhook ou Celery.
O pacote de terceiros `django_audit_fields` faz o papel de garantir marcação de data (`created_at`) não modificável (inclusive via timezone patch no `apps.py`).

## 3. Sanitização de PII no Log e Channels ✅
Enquanto a gravação de banco de dados guarda o telefone do paciente e sua mensagem criptografada (quando associado a um RAG), as camadas descartáveis de Log via Python (`logger.error`, `logger.info`) e as transições WebSocket pelo Redis não podem conter PIIs visíveis.

A classe `WhatsAppService` chama uma função utilitária `_mask_pii()`:
```python
def _mask_pii(text):
    if not text:
        return text
    if '@' not in text:
        return '***@unknown'
    phone_part, domain = text.split('@', 1)
    if len(phone_part) >= 8:
        return f"{phone_part[:5]}***{phone_part[-4:]}@{domain}"
    return f"***@{domain}"
```

Isso garante que um telefone `551199998888@example.com` transite nas ferramentas efêmeras (Websockets, APM e Loggers) apenas como `55119***8888@example.com`, mantendo os últimos 4 dígitos soltos para Troubleshooting rápido sem esbarrar nas sanções da LGPD ou no compliance SOC2.
