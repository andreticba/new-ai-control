# core/middleware.py | Atualizado em: 06-10-2026 21:43:00(GMT-04:00)
from django.http import HttpResponseForbidden
from core.models import AuditLog


def rbac_middleware(get_response):
    """
    Middleware que protege rotas de administração do WhatsApp Gateway.
    Verifica se o usuário possui a permissão 'org.manage_whatsapp'
    via platform_role ou OrganizationMembership.
    """
    def middleware(request):
        if request.path.startswith('/api/v1/gateway/'):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Not authenticated")

            has_permission = _check_permission(request.user, 'org.manage_whatsapp')

            if not has_permission:
                AuditLog.objects.create(
                    actor=request.user,
                    action='FAILED_LOGIN',
                    details={'path': request.path, 'reason': 'RBAC Denied (Gateway Management)'}
                )
                return HttpResponseForbidden("Forbidden: insufficient permissions")

        response = get_response(request)
        return response

    return middleware


def _check_permission(user, permission_slug):
    """
    Verifica se o usuário possui uma permissão, checando:
      1. platform_role do UserProfile (escopo PLATFORM)
      2. Qualquer OrganizationMembership ativa cujo role tenha a permissão
    """
    # 1. Platform role (superadmin, suporte)
    if hasattr(user, 'profile') and user.profile.platform_role_id:
        if user.profile.platform_role.permissions.filter(slug=permission_slug).exists():
            return True

    # 2. Org-level roles (via membership)
    from core.models import OrganizationMembership
    return OrganizationMembership.objects.filter(
        user=user,
        is_active=True,
        role__permissions__slug=permission_slug,
    ).exists()
