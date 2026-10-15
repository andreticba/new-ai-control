import pytest
from django.db import IntegrityError
from core.models import Organization, AuditLog

@pytest.mark.django_db
def test_organization_internal_constraint():
    # As migrations do sistema já criam a organização interna única ('AI Control (Plataforma)')
    # A tentativa de criar uma nova organização com is_internal=True deve disparar IntegrityError
    assert Organization.objects.filter(is_internal=True).exists()
    with pytest.raises(IntegrityError):
        Organization.objects.create(name="Org Interna Duplicada", org_type="PLATFORM", is_internal=True)

@pytest.mark.django_db
def test_auditlog_immutability():
    log = AuditLog.objects.create(action="ACCESS")
    with pytest.raises(Exception, match="AuditLog is immutable"):
        log.action = "UPDATE"
        log.save()
