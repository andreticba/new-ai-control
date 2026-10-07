# urls.py | AI-Control SDD v0.6.0 | 03-10-2026 00:15(GMT-04:00)
from django.urls import path, re_path
from .views.debug_views import whatsgt_debug_view
from .views.whatsgt_views import (
    WhatsGtInstanceQrView,
    WhatsGtInstanceDeleteView,
    WhatsGtMessageSendView,
    WhatsGtMessagesListView
)
from .api.v1.views.webhook_whatsapp import WebhookGatewayView

urlpatterns = [
    # Template View — renderiza a interface de debug no Django Admin
    path('admin/core/debug/qr/', whatsgt_debug_view, name='whatsgt_debug_view'),

    # API endpoints
    path('api/v1/whats-gt/qr/', WhatsGtInstanceQrView.as_view(), name='whatsgt_instance_qr'),
    path('api/v1/whats-gt/instance/', WhatsGtInstanceDeleteView.as_view(), name='whatsgt_instance_delete'),
    path('api/v1/whats-gt/messages/', WhatsGtMessagesListView.as_view(), name='whatsgt_message_list'),
    path('api/v1/whats-gt/messages/send/', WhatsGtMessageSendView.as_view(), name='whatsgt_message_send'),
    
    # Eventos Evolution API Centralizados (Webhook Gateway)
    re_path(r'^api/v1/webhook/whatsapp/?.*$', WebhookGatewayView.as_view(), name='webhook_whatsapp_gateway'),
]
