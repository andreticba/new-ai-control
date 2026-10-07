# config/asgi.py | AI-Control SDD v0.6.0 | 01-10-2026 20:12(GMT-04:00)
#
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Ponto de Entrada ASGI (Daphne)                                    ║
# ║                                                                    ║
# ║  O ProtocolTypeRouter do Django Channels decide:                   ║
# ║  - Requisição HTTP → encaminha para o Django (views normais)       ║
# ║  - Requisição WebSocket → encaminha para os consumers              ║
# ║                                                                    ║
# ║  O AuthMiddlewareStack injeta o request.user no scope do WS,       ║
# ║  permitindo que o consumer verifique se é staff.                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

# IMPORTANTE: get_asgi_application() DEVE ser chamado antes de importar
# qualquer módulo que use modelos Django (consumers, routing, etc).
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

application = ProtocolTypeRouter({
    # HTTP continua sendo servido pelo Django normalmente.
    "http": django_asgi_app,

    # WebSocket: AuthMiddlewareStack popula scope["user"] a partir
    # do cookie de sessão do Django (o admin já está logado via HTTP).
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
