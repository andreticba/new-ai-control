# managers.py | Vitalia SDD v0.6.0 | 08-10-2026 19:55(GMT-04:00)
from django.db import models
from .middleware import get_current_tenant

class TenantScopedManager(models.Manager):
    """
    Manager base para garantir isolamento de Tenant passivo.
    Intercepta todas as queries e adiciona a restrição da organização ativa.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = get_current_tenant()
        
        if tenant_id:
            return qs.filter(organization_id=tenant_id)
            
        # O SC-001 exige veto e resposta vazia se nenhum tenant logado
        return qs.none()
