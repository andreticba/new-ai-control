# core/orchestrator/providers/__init__.py | AI-Control SDD v0.6.0 | 28-09-2026 11:30(GMT-04:00)
# Routing: Ollama sempre para classificação; Gemini (→ Ollama fallback) para domínio geral.
from core.orchestrator.providers.ollama import OllamaOrchestratorProvider
from core.orchestrator.providers.gemini import GeminiOrchestratorProvider

__all__ = ['OllamaOrchestratorProvider', 'GeminiOrchestratorProvider']
