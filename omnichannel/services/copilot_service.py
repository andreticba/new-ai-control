# copilot_service.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:40:00(GMT-04:00)
import os
import time
import logging
import requests
from django.conf import settings
from omnichannel.models import Conversation, Message, CopilotDraft

logger = logging.getLogger(__name__)


class CopilotService:
    """
    Serviço de geração preditiva de sugestões de resposta para o atendente humano.
    Utiliza LLM local (Ollama / phi4-mini:latest) garantindo privacidade e sem vazamento de PII.
    """

    def __init__(self):
        self.ollama_url = os.environ.get(
            "OLLAMA_BASE_URL",
            getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        ).rstrip('/')
        self.model = os.environ.get(
            "COPILOT_MODEL",
            getattr(settings, "COPILOT_MODEL", "phi4-mini:latest")
        )
        self.timeout = int(os.environ.get("COPILOT_TIMEOUT", getattr(settings, "COPILOT_TIMEOUT", 15)))

    def generate_suggestion(self, conversation_id, trigger_message_id=None):
        conversation = Conversation.objects.filter(id=conversation_id).first()
        if not conversation:
            logger.warning(f"[CopilotService] Conversa {conversation_id} não encontrada.")
            return None

        trigger_msg = None
        if trigger_message_id:
            trigger_msg = Message.objects.filter(id=trigger_message_id, conversation=conversation).first()
        if not trigger_msg:
            trigger_msg = conversation.messages.filter(direction=Message.Direction.INBOUND).order_by('-timestamp').first()

        if not trigger_msg or not trigger_msg.content:
            logger.warning(f"[CopilotService] Nenhuma mensagem inbound para disparar sugestão na conversa {conversation_id}.")
            return None

        # Histórico recente para contextualização (até 5 mensagens anteriores)
        history_msgs = conversation.messages.filter(timestamp__lte=trigger_msg.timestamp).order_by('-timestamp')[:5]
        history_list = list(reversed(list(history_msgs)))

        history_context = []
        for m in history_list:
            role = "Cliente" if m.direction == Message.Direction.INBOUND else "Atendente"
            history_context.append(f"{role}: {m.content}")

        context_str = "\n".join(history_context)

        system_prompt = (
            "Você é o Copiloto Inteligente de Atendimento da clínica/empresa.\n"
            "Sua tarefa é sugerir uma resposta direta, concisa, profissional e empática para o atendente humano enviar ao cliente.\n"
            "Diretrizes:\n"
            "- Gere APENAS o texto da resposta que o atendente deve enviar.\n"
            "- Não inclua saudações redundantes se a conversa já estiver em andamento.\n"
            "- Não inclua explicações, prefixos como 'Sugestão:', nem aspas.\n"
            "- Mantenha a resposta em 1 ou 2 frases curtas.\n"
        )

        full_prompt = (
            f"{system_prompt}\n"
            f"Histórico recente da conversa:\n{context_str}\n\n"
            f"Última mensagem do cliente: {trigger_msg.content}\n"
            f"Sugestão de resposta do atendente:"
        )

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
            }
        }

        start_time = time.perf_counter()
        suggested_text = ""
        try:
            url = f"{self.ollama_url}/api/generate"
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            res_data = response.json()
            suggested_text = res_data.get("response", "").strip()
        except Exception as e:
            logger.error(f"[CopilotService] Falha na inferência do Ollama ({self.model}): {e}")
            # Fallback elegante em caso de falha de conexão do Ollama
            suggested_text = "Olá! Já estou verificando as informações para você, um instante por favor."

        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 2)

        # Higienização de eventuais aspas ou tags extras
        if suggested_text.startswith('"') and suggested_text.endswith('"'):
            suggested_text = suggested_text[1:-1].strip()
        if suggested_text.lower().startswith("sugestão:"):
            suggested_text = suggested_text[9:].strip()

        draft = CopilotDraft.objects.create(
            conversation=conversation,
            trigger_message=trigger_msg,
            suggested_content=suggested_text,
            status=CopilotDraft.Status.PENDING,
            generated_by_model=self.model,
            latency_ms=latency_ms
        )

        logger.info(
            f"[CopilotService] Draft {draft.id} gerado com sucesso para conv {conversation.id} "
            f"via {self.model} ({latency_ms}ms)."
        )
        return draft
