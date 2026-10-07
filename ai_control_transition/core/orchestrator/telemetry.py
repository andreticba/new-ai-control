# core/orchestrator/telemetry.py | AI-Control SDD v0.6.0 | 28-09-2026 11:30(GMT-04:00)
"""
Telemetria de Auditoria do Orquestrador WhatsApp.

Grava registros imutáveis (append-only) em:
  <PROJECT_ROOT>/logs/wa_transactions_YYYYMMDD.jsonl

Schema por registro:
  - Quem chamou (session, turn, org)
  - Classificação: qual provider/model, domínio detectado, confiança, latência
  - Resposta: qual provider/model, status HITL, tokens (quando disponível), latência
  - Metadados de rastreabilidade: machine_id, pid, timestamp GMT-04:00 (P04)

Propósito: auditoria de custos (tokens Gemini), segurança (domínio clínico vs geral),
           performance e conformidade EU AI Act Art. 12 (logs automáticos para IA).
"""
import os
import json
import socket
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Fuso horário imutável do ecossistema AI-Control (P04)
VITALIA_TZ = timezone(timedelta(hours=-4))


def _get_log_path() -> Path:
    """Resolve o caminho do arquivo de log dentro do projeto."""
    # Caminho relativo à raiz do projeto Django
    project_root = Path(os.environ.get("DJANGO_BASE_DIR", Path(__file__).resolve().parents[3]))
    log_dir = project_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(VITALIA_TZ).strftime("%Y%m%d")
    return log_dir / f"wa_transactions_{date_str}.jsonl"


def _machine_id() -> str:
    name = os.environ.get("VITALIA_MACHINE_NAME") or socket.gethostname()
    return hashlib.sha256(name.encode()).hexdigest()[:8]


def write_transaction(
    *,
    session_id: str,
    turn_id: str,
    org_id: str,
    # ── Classificação ────────────────────────────────────────────────────
    classification_provider: str,
    classification_model: str,
    classification_domain: str,
    classification_confidence: float,
    classification_reason: str,
    classification_elapsed_ms: float,
    # ── Resposta ─────────────────────────────────────────────────────────
    response_provider: str,
    response_model: str,
    response_elapsed_ms: float,
    ai_response_status: str,          # 'DRAFT' | 'DELIVERED' | 'ERROR'
    response_tokens: Optional[Dict[str, int]] = None,
    # ── Extra ─────────────────────────────────────────────────────────────
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Grava uma transação de auditoria completa do Orquestrador de IA.
    Nunca lança exceção — falha silenciosa com log de warning (não pode bloquear a resposta ao usuário).
    """
    try:
        now_str = datetime.now(VITALIA_TZ).strftime("%d-%m-%Y %H:%M:%S(GMT-04:00)")
        record = {
            "schema_version": "0.6.0",
            "schema_type": "wa_orchestrator_telemetry",
            "timestamp": now_str,
            "machine_id": _machine_id(),
            "pid": os.getpid(),
            # ── Contexto ──────────────────────────────────────────────
            "session_id": session_id,
            "turn_id": turn_id,
            "org_id": org_id,
            # ── Fase 1: Classificação (sempre Ollama local) ────────────
            "classification": {
                "provider": classification_provider,
                "model": classification_model,
                "domain": classification_domain,
                "confidence": round(classification_confidence, 4),
                "reason": classification_reason,
                "elapsed_ms": classification_elapsed_ms,
            },
            # ── Fase 2: Geração de Resposta ────────────────────────────
            "response": {
                "provider": response_provider,
                "model": response_model,
                "ai_response_status": ai_response_status,
                "elapsed_ms": response_elapsed_ms,
                "tokens": response_tokens or {},
            },
        }
        if extra:
            record["extra"] = extra

        path = _get_log_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    except Exception as exc:
        logger.warning(f"[Telemetry] Falha ao gravar transação wa_transactions: {exc}")
