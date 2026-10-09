# middleware.py | Vitalia SDD v0.6.0 | 08-10-2026 19:55(GMT-04:00)
import contextvars
import uuid
import logging

logger = logging.getLogger(__name__)

# ContextVar que armazenará o UUID do tenant ativo para a thread/task assíncrona atual.
_current_tenant = contextvars.ContextVar('current_tenant', default=None)

def set_current_tenant(tenant_id):
    """Define o tenant ativo no contexto atual."""
    if tenant_id and not isinstance(tenant_id, uuid.UUID):
        try:
            tenant_id = uuid.UUID(str(tenant_id))
        except ValueError:
            logger.warning(f"ID de tenant inválido: {tenant_id}")
            tenant_id = None
            
    return _current_tenant.set(tenant_id)

def get_current_tenant():
    """Recupera o tenant ativo do contexto atual."""
    return _current_tenant.get()

def reset_tenant(token):
    """Limpa o tenant do contexto (essencial para evitar Tenant Bleed em Async)."""
    _current_tenant.reset(token)

class TenantContextMiddleware:
    """
    Middleware que extrai o ID do tenant (ex: do JWT ou header)
    e o injeta no ContextVar para garantir isolamento no nível de DAO/Manager.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = request.headers.get('X-Tenant-ID')
        token = set_current_tenant(tenant_id)
        try:
            response = self.get_response(request)
        finally:
            reset_tenant(token)
            
        return response
