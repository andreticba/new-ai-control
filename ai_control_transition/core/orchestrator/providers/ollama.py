# core/orchestrator/providers/ollama.py | AI-Control SDD v0.6.0 | 28-09-2026 11:30(GMT-04:00)
"""
Provedor Ollama para o Orquestrador de IA.

Lê do .env (via P11 — sem hardcode):
  VITALIA_NODE        → URL base do servidor Ollama (ex: http://localhost:11434)
  VITALIA_LOCAL_MODEL → Modelo de geração/classificação (ex: llama3.2:latest)
  OLLAMA_TIMEOUT_SEC  → Timeout em segundos (padrão: 480)

Responsabilidades neste módulo:
  - classify()         → Primeira chamada: classifica domínio (clinical/general) sem enviar PHI para fora.
  - generate_clinical() → Segunda chamada (domínio clínico): gera resposta localmente. PHI nunca sai da máquina.
  - generate_general()  → Chamada de fallback quando Gemini falha.
"""
import os
import json
import time
import logging
from typing import Optional, Dict, Any

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)


class OllamaOrchestratorProvider:
    """Cliente Ollama para classificação e geração clínica."""

    def __init__(self):
        self.base_url = os.environ.get('VITALIA_NODE', 'http://localhost:11434').rstrip('/')
        self.model = os.environ.get('VITALIA_LOCAL_MODEL', 'llama3.2:latest')
        self.timeout = int(os.environ.get('OLLAMA_TIMEOUT_SEC', '480'))

    # ── Public API ──────────────────────────────────────────────────────────

    def classify(self, context_history: str, user_message: str) -> Dict[str, Any]:
        """
        Classifica a mensagem do usuário sem enviar PHI para fora.
        Retorna dict com: domain, confidence, reason, _elapsed_ms, _model.
        Em caso de falha, retorna 'clinical' como fail-safe (P09).
        """
        system = (
            "You are a clinical triage classifier. Analyze the conversation and classify the intent.\n"
            "Return ONLY valid JSON with exactly these fields:\n"
            '{"domain": "clinical" or "general", "confidence": 0.0-1.0, "reason": "brief reason in pt-BR", "mc_constraints": []}\n\n'
            "clinical = symptoms, diagnosis, medication, treatment, lab results, medical advice, health protocols, nutrition plans, training zones\n"
            "general  = scheduling, greetings, administrative, platform usage, general info, pricing"
        )
        prompt = (
            f"[SYSTEM]\n{system}\n\n"
            f"[HISTÓRICO]\n{context_history or 'Sem histórico.'}\n\n"
            f"[USUÁRIO]\n{user_message}\n\n"
            "[CLASSIFICAÇÃO JSON]:"
        )
        result = self._call(prompt, json_mode=True)
        if result is None:
            # Fail-safe: falha na classificação → tratar como clínico (P09)
            logger.error("[OllamaProvider] Falha na classificação. Aplicando fail-safe: domain=clinical")
            return {
                "domain": "clinical",
                "confidence": 0.0,
                "reason": "classification_failure_failsafe",
                "mc_constraints": [],
                "_elapsed_ms": 0,
                "_model": self.model,
            }

        raw = result.get("response", "{}")
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"[OllamaProvider] JSON inválido na classificação: {raw[:200]}")
            parsed = {"domain": "clinical", "confidence": 0.0, "reason": "parse_error"}

        parsed.setdefault("mc_constraints", [])
        parsed["_elapsed_ms"] = result.get("_elapsed_ms", 0)
        parsed["_model"] = self.model
        return parsed

    def generate_clinical(self, context_history: str, user_message: str) -> Optional[str]:
        """
        Gera resposta para domínio clínico. 100% local — PHI não trafega para a nuvem.
        A resposta é salva como DRAFT e aguarda revisão HITL (P09).
        """
        system = (
            "Você é a IA da AI-Control, assistente de saúde especializada.\n"
            "REGRAS INVIOLÁVEIS:\n"
            "- NUNCA faça diagnósticos definitivos.\n"
            "- NUNCA prescreva medicamentos ou doses específicas.\n"
            "- SEMPRE oriente o usuário a consultar um profissional de saúde habilitado.\n"
            "- Use linguagem empática, clara e acolhedora.\n"
            "- Responda em português brasileiro.\n"
            "- Esta resposta será REVISADA por um profissional antes de ser enviada ao paciente."
        )
        return self._generate_text(system, context_history, user_message)

    def generate_general(self, context_history: str, user_message: str) -> Optional[str]:
        """Fallback: gera resposta geral quando Gemini falha."""
        system = (
            "Você é a IA da AI-Control, assistente de saúde e bem-estar.\n"
            "Responda de forma amigável, útil e objetiva.\n"
            "Responda em português brasileiro."
        )
        return self._generate_text(system, context_history, user_message)

    # ── Private helpers ──────────────────────────────────────────────────────

    def _generate_text(self, system: str, context_history: str, user_message: str) -> Optional[str]:
        prompt = (
            f"[SISTEMA]\n{system}\n\n"
            f"[HISTÓRICO]\n{context_history or 'Início da conversa.'}\n\n"
            f"[USUÁRIO]\n{user_message}\n\n"
            "[VITALIA]:"
        )
        result = self._call(prompt, json_mode=False)
        if result is None:
            return None
        return result.get("response", "")

    def _call(self, prompt: str, json_mode: bool = False) -> Optional[Dict[str, Any]]:
        if not _REQUESTS_OK:
            logger.error("[OllamaProvider] Pacote 'requests' não instalado.")
            return None

        url = f"{self.base_url}/api/generate"
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if json_mode:
            payload["format"] = "json"

        t_start = time.time()
        try:
            resp = _requests.post(url, json=payload, timeout=self.timeout)
            elapsed_ms = (time.time() - t_start) * 1000
            if resp.status_code == 200:
                data = resp.json()
                data["_elapsed_ms"] = round(elapsed_ms, 2)
                data["_model"] = self.model
                return data
            logger.error(f"[OllamaProvider] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as exc:
            elapsed_ms = (time.time() - t_start) * 1000
            logger.error(f"[OllamaProvider] Erro de conexão ({elapsed_ms:.0f}ms): {exc}")
        return None
