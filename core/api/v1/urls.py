# core/api/v1/urls.py | AI-Control v0.0.1 | 12-10-2026 09:35(GMT-04:00)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views.user_views import CurrentUserView, ActiveWorkspacesView

app_name = 'api_v1'

urlpatterns = [
    # Autenticação JWT Stateless
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoints Agregados do Domínio Core / RBAC
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
    path('workspaces/', ActiveWorkspacesView.as_view(), name='active_workspaces'),
]
