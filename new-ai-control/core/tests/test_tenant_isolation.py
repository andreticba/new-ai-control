# test_tenant_isolation.py | Vitalia SDD v0.6.0 | 08-10-2026 19:57(GMT-04:00)
import pytest
import uuid
import threading
import time
from core.models import AuditLog
from core.middleware import set_current_tenant, get_current_tenant, reset_tenant

@pytest.mark.django_db
def test_tenant_isolation_reads():
    """
    Testa se o TenantScopedManager filtra adequadamente baseado no ContextVar
    (FR-001, FR-002, SC-001)
    """
    tenant_1 = uuid.uuid4()
    tenant_2 = uuid.uuid4()
    
    # Injetando usando manager explícito
    AuditLog.all_objects.create(action='ACCESS', organization_id=tenant_1)
    AuditLog.all_objects.create(action='UPDATE', organization_id=tenant_1)
    AuditLog.all_objects.create(action='DELETE', organization_id=tenant_2)

    # Contexto Vazio (SC-001 exige que bloqueie vazamento)
    assert AuditLog.objects.count() == 0
    
    # Validando Tenant 1
    token1 = set_current_tenant(tenant_1)
    assert AuditLog.objects.count() == 2
    reset_tenant(token1)
    
    # Validando Tenant 2
    token2 = set_current_tenant(tenant_2)
    assert AuditLog.objects.count() == 1
    reset_tenant(token2)

@pytest.mark.django_db(transaction=True)
def test_tenant_bleed_threads():
    """
    Testa para garantir que a injeção em Thread A não vaza para a Thread B.
    """
    tenant_1 = uuid.uuid4()
    tenant_2 = uuid.uuid4()
    
    AuditLog.all_objects.create(action='ACCESS', organization_id=tenant_1)
    AuditLog.all_objects.create(action='UPDATE', organization_id=tenant_2)

    def worker(tenant_id, expected_count, result_list):
        token = set_current_tenant(tenant_id)
        time.sleep(0.1) # força interleave
        result_list.append(AuditLog.objects.count() == expected_count)
        reset_tenant(token)

    results_t1 = []
    results_t2 = []

    t1 = threading.Thread(target=worker, args=(tenant_1, 1, results_t1))
    t2 = threading.Thread(target=worker, args=(tenant_2, 1, results_t2))

    t1.start()
    t2.start()
    
    t1.join()
    t2.join()

    assert all(results_t1)
    assert all(results_t2)
