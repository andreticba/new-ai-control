# core/orchestrator/providers/gemini.py | AI-Control SDD v0.6.0 | 28-09-2026 11:30(GMT-04:00)
"""
Provedor Gemini REST para o Orquestrador de IA.

Lê do .env (via P11 — sem hardcode):
  GEMINI_API_KEY         → Chave da API Google Gemini
  GEMINI_MODEL_FLASH     → Modelo a usar (ex: gemini-3.6-flash)
  GEMINI_MAX_RETRIES     → Máximo de tentativas (padrão: 5)
  GEMINI_BASE_RETRY_DELAY → Delay base para Full Jitter (padrão: 3.0s)
  GEMINI_MAX_RETRY_DELAY  → Delay máximo (padrão: 60.0s)

Responsabilidade: geração de respostas para domínio GERAL.
Dados PII/PHI NUNCA chegam aqui — apenas conteúdo não-clínico (P09).
"""
import os
import re
import time
import json
import random
import socket
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

# Fuso horário imutável do ecossistema AI-Control (P04)
VITALIA_TZ = timezone(timedelta(hours=-4))


class GeminiOrchestratorProvider:
    """Provedor Gemini REST para geração de respostas gerais (não-clínicas)."""

    def __init__(self):
        self.max_retries = int(os.environ.get("GEMINI_MAX_RETRIES", "5"))
        self.base_delay = float(os.environ.get("GEMINI_BASE_RETRY_DELAY", "3.0"))
        self.max_delay = float(os.environ.get("GEMINI_MAX_RETRY_DELAY", "60.0"))

    # ── Public API ──────────────────────────────────────────────────────────

    def generate(self, context_history: str, user_message: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Gera uma resposta geral via Gemini REST API.
        Retorna (response_text, telemetry_tokens).
        Em caso de falha, retorna (None, {}) para acionar fallback Ollama.
        """
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("[GeminiOrchestrator] GEMINI_API_KEY não configurada. Pulando para fallback Ollama.")
            return None, {}

        model = os.environ.get("GEMINI_MODEL_FLASH", "gemini-3.6-flash").strip()
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )

        system = (
            "Você é a IA da AI-Control, assistente de saúde e bem-estar. "
            "Responda de forma amigável, útil e objetiva em português brasileiro."
        )
        full_text = (
            f"[SISTEMA]\n{system}\n\n"
            f"[HISTÓRICO]\n{context_history or 'Início da conversa.'}\n\n"
            f"[USUÁRIO]\n{user_message}\n\n"
            "[VITALIA]:"
        )
        payload = {
            "contents": [{"parts": [{"text": full_text}]}],
            "generationConfig": {"temperature": 0.3},
        }

        for attempt in range(1, self.max_retries + 1):
            t_start = time.time()
            try:
                resp = _requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
                elapsed_ms = (time.time() - t_start) * 1000

                if resp.status_code == 200:
                    data = resp.json()
                    usage = data.get("usageMetadata", {})
                    candidates = data.get("candidates", [])
                    text = ""
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        text = parts[0].get("text", "") if parts else ""
                    return text, {
                        "elapsed_ms": round(elapsed_ms, 2),
                        "model": model,
                        "prompt": usage.get("promptTokenCount", 0),
                        "candidates": usage.get("candidatesTokenCount", 0),
                        "total": usage.get("totalTokenCount", 0),
                    }

                elif resp.status_code in (429, 503):
                    backoff = self._backoff(attempt, resp)
                    logger.warning(f"[GeminiOrchestrator] HTTP {resp.status_code}. Tentativa {attempt}/{self.max_retries}. Aguardando {backoff:.1f}s.")
                    time.sleep(backoff)
                else:
                    logger.error(f"[GeminiOrchestrator] HTTP {resp.status_code} (não-recuperável): {resp.text[:200]}")
                    return None, {}

            except Exception as exc:
                backoff = self._backoff(attempt)
                logger.error(f"[GeminiOrchestrator] Erro de rede ({exc}). Aguardando {backoff:.1f}s.")
                time.sleep(backoff)

        return None, {}

    # ── Private helpers ──────────────────────────────────────────────────────

    def _get_api_key(self) -> Optional[str]:
        for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            val = os.environ.get(var, "").strip()
            if val:
                return val
        return None

    def _backoff(self, attempt: int, resp=None) -> float:
        if resp is not None:
            try:
                details = resp.json().get("error", {}).get("details", [])
                for d in details:
                    if isinstance(d, dict) and d.get("@type", "").endswith("RetryInfo"):
                        m = re.match(r"^([0-9.]+)s$", str(d.get("retryDelay", "")))
                        if m:
                            return min(float(m.group(1)), self.max_delay)
            except Exception:
                pass
        cap = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        return random.uniform(0.0, cap)
