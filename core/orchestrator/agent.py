# core/orchestrator/agent.py | AI-Control SDD v0.6.0 | 28-09-2026 11:30(GMT-04:00)
"""
Orquestrador de IA — Roteamento em Duas Chamadas.

Fluxo:
  1. CLASSIFICAÇÃO (sempre Ollama local) → domain: clinical | general
     PHI nunca sai da máquina nesta fase.

  2. GERAÇÃO DE RESPOSTA:
     ├─ clinical  → Ollama local → DRAFT (aguarda revisão HITL — P09)
     └─ general   → Gemini REST → fallback Ollama → DELIVERED (enviado direto)

  3. Telemetria gravada em logs/wa_transactions_YYYYMMDD.jsonl (append-only, P04/P07).
  4. AuditLog Django salvo (EU AI Act Art. 12).

Variáveis .env relevantes (P11 — sem hardcode):
  VITALIA_NODE          → URL do Ollama (ex: http://localhost:11434)
  VITALIA_LOCAL_MODEL   → Modelo Ollama (ex: llama3.2:latest)
  GEMINI_API_KEY        → Chave Gemini (vazio = fallback direto para Ollama)
  GEMINI_MODEL_FLASH    → Modelo Gemini (ex: gemini-3.6-flash)
  SESSION_CONTEXT_TTL_SECONDS → TTL do cache de contexto Redis (padrão: 86400)
  CONTEXT_WINDOW_SIZE   → Nº de turnos no contexto do prompt (padrão: 20)
"""
import logging
import uuid
from typing import Optional

from core.orchestrator.providers.ollama import OllamaOrchestratorProvider
from core.orchestrator.providers.gemini import GeminiOrchestratorProvider
from core.orchestrator.memory import load_context, save_context
from core.orchestrator.safety_gate import classify_response
from core.orchestrator.telemetry import write_transaction
from core.services.evolution_gateway import EvolutionGatewayService
from core.models import ConversationTurn, AuditLog

logger = logging.getLogger(__name__)


def process_turn(session, turn, wa_id_raw: str) -> None:
    """
    Ponto de entrada do Orquestrador. Chamado pela Celery task após ingestão do webhook.

    Args:
        session   : WhatsAppSession — sessão ativa do usuário.
        turn      : ConversationTurn — turno INBOUND recem-criado.
        wa_id_raw : str — número de telefone real (NUNCA persistido em claro).
    """
    org_id = str(session.organization.id)
    org_slug = session.organization.slug
    session_id = str(session.id)
    turn_id = str(turn.id)
    user_message = turn.message_text

    # ── 1. Carregar contexto Redis ─────────────────────────────────────────
    context = load_context(org_id, session_id)
    history = _format_history(context)

    ollama = OllamaOrchestratorProvider()
    gemini = GeminiOrchestratorProvider()

    # ── 2. CLASSIFICAÇÃO — Ollama local (PHI nunca sai da máquina) ─────────
    logger.info(f"[Orchestrator] Classificando turn {turn_id} via Ollama ({ollama.model})...")
    classification = ollama.classify(history, user_message)

    domain: str = classification.get("domain", "clinical")
    confidence: float = float(classification.get("confidence", 0.0))
    reason: str = classification.get("reason", "")
    mc_constraints: list = classification.get("mc_constraints", [])
    cls_elapsed: float = float(classification.get("_elapsed_ms", 0))

    # Safety Gate duplo: LLM + regex (segurança em profundidade — P09)
    safety_override = classify_response(user_message)
    if safety_override and domain != "clinical":
        logger.warning(f"[Orchestrator] Safety Gate override: forçando domain=clinical (LLM disse '{domain}').")
        domain = "clinical"
        mc_constraints.append("safety_gate_keyword_override")

    logger.info(f"[Orchestrator] Domínio: {domain} (confiança: {confidence:.2f}) | Reason: {reason}")

    # ── 3. GERAÇÃO DE RESPOSTA ─────────────────────────────────────────────
    response_text: Optional[str] = None
    response_provider = "unknown"
    response_model = "unknown"
    response_elapsed = 0.0
    response_tokens: dict = {}
    ai_response_status = "ERROR"

    if domain == "clinical":
        # ── 3a. CLÍNICO → Ollama local obrigatório → DRAFT ────────────────
        logger.info(f"[Orchestrator] Domínio clínico → gerando via Ollama local ({ollama.model})...")
        raw = ollama.generate_clinical(history, user_message)
        response_provider = "ollama"
        response_model = ollama.model

        if raw:
            response_text = raw
            ai_response_status = "DRAFT"
            ConversationTurn.objects.create(
                session=session,
                message_id=f"ai-draft-{uuid.uuid4().hex}",
                direction="OUTBOUND",
                message_text=response_text,
                ai_response_status="DRAFT",
            )
            logger.info(f"[Orchestrator] Resposta clínica salva como DRAFT (aguarda HITL — P09).")
        else:
            logger.error(f"[Orchestrator] Ollama falhou para domínio clínico. Turn {turn_id} sem resposta.")

    else:
        # ── 3b. GERAL → Gemini (fallback Ollama) → DELIVERED ──────────────
        logger.info("[Orchestrator] Domínio geral → tentando Gemini REST...")
        gemini_text, tokens = gemini.generate(history, user_message)
        response_tokens = tokens

        if gemini_text is not None:
            response_text = gemini_text
            response_provider = "gemini"
            response_model = tokens.get("model", "gemini-3.6-flash")
            response_elapsed = tokens.get("elapsed_ms", 0.0)
            logger.info(f"[Orchestrator] Resposta geral via Gemini ({response_model}).")
        else:
            # Fallback: Ollama responde para geral
            logger.warning("[Orchestrator] Gemini indisponível. Fallback para Ollama (geral)...")
            raw = ollama.generate_general(history, user_message)
            response_provider = "ollama_fallback"
            response_model = ollama.model
            if raw:
                response_text = raw

        if response_text:
            ai_response_status = "DELIVERED"
            gw = EvolutionGatewayService()
            instance_name = gw._instance_name(org_slug)
            gw.send_text_message(instance_name, wa_id_raw, response_text)
            ConversationTurn.objects.create(
                session=session,
                message_id=f"ai-outbound-{uuid.uuid4().hex}",
                direction="OUTBOUND",
                message_text=response_text,
                ai_response_status="DELIVERED",
            )
            logger.info("[Orchestrator] Resposta geral enviada via gateway.")
        else:
            logger.error(f"[Orchestrator] Todos os providers falharam para turn {turn_id}.")

    # ── 4. Atualizar contexto Redis ───────────────────────────────────────
    if response_text:
        context.append({"direction": "INBOUND", "text": user_message})
        context.append({"direction": "OUTBOUND", "text": response_text})
        save_context(org_id, session_id, context)

    # ── 5. AuditLog Django (EU AI Act Art. 12 / P07) ─────────────────────
    AuditLog.objects.create(
        action="AI_DECISION",
        details={"session_id": session_id, "turn_id": turn_id},
        ai_reasoning_snapshot={
            "classification_domain": domain,
            "classification_confidence": confidence,
            "classification_reason": reason,
            "mc_constraints": mc_constraints,
            "response_provider": response_provider,
            "response_model": response_model,
            "ai_response_status": ai_response_status,
            "safety_gate_override": safety_override,
        },
    )

    # ── 6. Telemetria de tokens (append-only JSONL — P04/P07) ─────────────
    write_transaction(
        session_id=session_id,
        turn_id=turn_id,
        org_id=org_id,
        classification_provider="ollama",
        classification_model=ollama.model,
        classification_domain=domain,
        classification_confidence=confidence,
        classification_reason=reason,
        classification_elapsed_ms=cls_elapsed,
        response_provider=response_provider,
        response_model=response_model,
        response_elapsed_ms=response_elapsed,
        ai_response_status=ai_response_status,
        response_tokens=response_tokens,
        extra={"mc_constraints": mc_constraints},
    )


def _format_history(context: list) -> str:
    """Formata o histórico de turnos para o prompt."""
    if not context:
        return ""
    return "\n".join(
        f"{'Usuário' if c['direction'] == 'INBOUND' else 'AI-Control'}: {c['text']}"
        for c in context
    )
