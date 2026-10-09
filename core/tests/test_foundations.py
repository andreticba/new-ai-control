import pytest
from django.db import IntegrityError
from core.models import Organization, AuditLog

@pytest.mark.django_db
def test_organization_internal_constraint():
    org1 = Organization.objects.create(name="Org 1", org_type="PLATFORM", is_internal=True)
    with pytest.raises(IntegrityError):
        Organization.objects.create(name="Org 2", org_type="PLATFORM", is_internal=True)

@pytest.mark.django_db
def test_auditlog_immutability():
    log = AuditLog.objects.create(action="ACCESS")
    with pytest.raises(Exception, match="AuditLog is immutable"):
        log.action = "UPDATE"
        log.save()
