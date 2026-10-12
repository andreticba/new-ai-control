# core/api/v1/views/schema_views.py | AI-Control v0.0.1 | 12-10-2026 09:35(GMT-04:00)
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.settings import perform_import
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.settings import spectacular_settings


class ConditionalSpectacularAPIView(SpectacularAPIView):
    """
    Schema OpenAPI dinâmico com controle de segurança condicional por ambiente (OWASP API9:2023):
    - Em ambiente de desenvolvimento (DEBUG=True): Público para geração de tipos via CLI.
    - Em ambiente de produção (DEBUG=False): Protegido, exigindo privilégios administrativos.
    """
    def get_permissions(self):
        user_spec = getattr(settings, 'SPECTACULAR_SETTINGS', {})
        serve_perms = user_spec.get('SERVE_PERMISSIONS')
        if serve_perms is not None:
            resolved = []
            for perm in serve_perms:
                if isinstance(perm, str):
                    resolved.append(perform_import(perm, 'SERVE_PERMISSIONS')())
                else:
                    resolved.append(perm() if callable(perm) else perm)
            return resolved

        if getattr(settings, 'DEBUG', False):
            return [AllowAny()]
        return [IsAdminUser()]
