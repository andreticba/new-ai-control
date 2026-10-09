# test_models.py | Vitalia SDD v0.6.0 | 08-10-2026 19:55(GMT-04:00)
import pytest
from core.models import AuditLog

@pytest.mark.django_db
def test_audit_log_creation():
    log = AuditLog.objects.create(
        action=AuditLog.ActionType.ACCESS,
        details={"test": "data"}
    )
    assert log.id is not None
    assert log.action == 'ACCESS'
