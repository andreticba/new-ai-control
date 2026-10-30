# urls.py | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:34:00(GMT-04:00)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from omnichannel.api.views import (
    ConversationViewSet,
    MessageViewSet,
    CopilotDraftViewSet,
    InstanceManageView,
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'copilot-drafts', CopilotDraftViewSet, basename='copilot-draft')

urlpatterns = [
    path('instance/', InstanceManageView.as_view(), name='omnichannel_instance_manage'),
    path('', include(router.urls)),
]
