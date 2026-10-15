# core/api/v1/permissions.py | AI-Control v0.0.1 | 14-10-2026 07:45(GMT-04:00)
from rest_framework import permissions
from core.middleware import _check_permission


class HasWorkspaceManagePermission(permissions.BasePermission):
    """
    Controla permissões de mutação em workspaces e membros (US4).
    - Métodos seguros (GET, HEAD, OPTIONS): permitidos para qualquer usuário autenticado.
    - Mutações (POST, PUT, PATCH, DELETE): exigem papel de gestão ('org_admin', 'platform_superadmin' ou 'org.manage').
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if user.is_superuser:
            return True

        if hasattr(user, 'profile') and user.profile and user.profile.platform_role:
            if user.profile.platform_role.slug in ['platform_superadmin', 'platform_support']:
                return True

        # Checa permissões granulares via roles organizacionais ativas
        has_manage = (
            _check_permission(user, 'org.manage') or
            _check_permission(user, 'platform.manage_organizations') or
            _check_permission(user, 'org.manage_members')
        )
        return has_manage
