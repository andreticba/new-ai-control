from django.http import HttpResponseForbidden
from core.models import AuditLog

def rbac_middleware(get_response):
    def middleware(request):
        if request.path.startswith('/api/v1/gateway/'):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Not authenticated")
                
            has_permission = False
            
            if hasattr(request.user, 'profile'):
                roles = request.user.profile.roles.values_list('name', flat=True)
                if 'ADMIN' in roles or 'PLATFORM_ADMIN' in roles:
                    has_permission = True
            
            if not has_permission:
                AuditLog.objects.create(
                    actor=request.user,
                    action='FAILED_LOGIN',
                    details={'path': request.path, 'reason': 'RBAC Denied (Gateway Management)'}
                )
                return HttpResponseForbidden("Forbidden: Admins only")
                
        response = get_response(request)
        return response

    return middleware
