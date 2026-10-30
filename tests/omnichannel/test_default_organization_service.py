import pytest
from core.models import Organization
from omnichannel.services.default_organization_service import DefaultOrganizationService


@pytest.mark.django_db
def test_get_default_organization_creates_when_empty():
    """Garante que cria uma organização padrão de forma idempotente quando o banco estiver vazio."""
    Organization.objects.all().delete()
    
    org = DefaultOrganizationService.get_default_organization()
    
    assert org is not None
    assert org.id is not None
    assert org.is_active is True
    assert org.is_internal is True
    assert org.org_type == Organization.OrgType.PLATFORM


@pytest.mark.django_db
def test_get_default_organization_idempotency():
    """Garante que chamadas subsequentes não criam múltiplas organizações padrão."""
    Organization.objects.all().delete()
    
    org1 = DefaultOrganizationService.get_default_organization()
    org2 = DefaultOrganizationService.get_default_organization()
    
    assert org1.id == org2.id
    assert Organization.objects.count() == 1


@pytest.mark.django_db
def test_get_default_organization_finds_existing_internal_org():
    """Garante que recupera organização interna existente."""
    Organization.objects.all().delete()
    existing = Organization.objects.create(
        name="Org Interna Existente",
        org_type=Organization.OrgType.PLATFORM,
        slug="platform-existing",
        is_internal=True,
        is_active=True
    )
    
    org = DefaultOrganizationService.get_default_organization()
    assert org.id == existing.id


@pytest.mark.django_db
def test_get_default_organization_prefers_settings_id(settings):
    """Garante que respeita settings.DEFAULT_ORGANIZATION_ID se configurado."""
    Organization.objects.all().delete()
    custom_org = Organization.objects.create(
        name="Org Customizada",
        org_type=Organization.OrgType.COMPANY,
        slug="custom-org",
        is_active=True
    )
    settings.DEFAULT_ORGANIZATION_ID = str(custom_org.id)
    
    org = DefaultOrganizationService.get_default_organization()
    assert org.id == custom_org.id
