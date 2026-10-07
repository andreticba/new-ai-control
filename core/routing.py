# routing.py | Atualizado em: 02-10-2026 13:35:45(GMT-04:00)
# core/routing.py | AI-Control SDD v0.6.0 | 01-10-2026 20:12(GMT-04:00)
#
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Roteamento de WebSockets do Django Channels                       ║
# ║                                                                    ║
# ║  Funciona como o urls.py, mas para conexões WebSocket.             ║
# ║  Cada path mapeia uma URL ws:// para um Consumer.                  ║
# ║                                                                    ║
# ║  COMO ADICIONAR NOVAS ROTAS:                                       ║
# ║  1. Crie um novo Consumer em core/consumers.py                     ║
# ║  2. Adicione um re_path aqui apontando para ele                    ║
# ║  3. O config/asgi.py já importa este arquivo automaticamente       ║
# ╚══════════════════════════════════════════════════════════════════════╝

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # O frontend conecta em: ws://localhost:8000/ws/whats-gt/messages/
    # O DebugConsumer gerencia o ciclo de vida dessa conexão.
    re_path(r"ws/whats-gt/messages/$", consumers.DebugConsumer.as_asgi()),
]
