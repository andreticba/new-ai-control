# config/routing.py | AI-Control SDD v0.6.0 | 20-10-2026 19:27:00(GMT-04:00)
from django.urls import re_path
import core.routing
from omnichannel.consumers.omnichannel_consumer import OmnichannelConsumer

websocket_urlpatterns = core.routing.websocket_urlpatterns + [
    re_path(r"^ws/omnichannel/$", OmnichannelConsumer.as_asgi()),
    re_path(r"^ws/omnichannel/(?P<organization_id>[0-9a-f-]+)/$", OmnichannelConsumer.as_asgi()),
]
