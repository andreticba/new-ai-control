# core/tests/test_workspace_isolation.py | AI-Control v0.0.1 | 14-10-2026 16:30(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    Organization,
    Role,
    OrganizationMembership,
    UserProfile,
)


@pytest.fixture
def multi_tenant_setup(db):
    user_a = User.objects.create_user(
        username="user.org.a",
        email="user.org.a@example.org",
        password="password"
    )
    UserProfile.objects.create(user=user_a, full_name="User Org A")

    user_b = User.objects.create_user(
        username="user.org.b",
        email="user.org.b@example.org",
        password="password"
    )
    UserProfile.objects.create(user=user_b, full_name="User Org B")

    superadmin = User.objects.create_superuser(
        username="superadmin",
        email="superadmin@example.org",
        password="password"
    )
    UserProfile.objects.create(user=superadmin, full_name="Super Admin")

    org_a = Organization.objects.create(name="Hospital Alpha", slug="hosp-alpha", org_type="CLINIC")
    org_b = Organization.objects.create(name="Hospital Beta", slug="hosp-beta", org_type="CLINIC")

    role_admin, _ = Role.objects.get_or_create(
        slug="org_admin",
        defaults={"name": "Org Admin", "scope": "ORGANIZATION"}
    )

    OrganizationMembership.objects.create(
        user=user_a,
        organization=org_a,
        role=role_admin,
        is_active=True
    )
    OrganizationMembership.objects.create(
        user=user_b,
        organization=org_b,
        role=role_admin,
        is_active=True
    )

    return user_a, user_b, superadmin, org_a, org_b


@pytest.mark.django_db
class TestWorkspaceIsolation:

    def test_user_a_only_lists_own_organization(self, multi_tenant_setup):
        user_a, user_b, _, org_a, org_b = multi_tenant_setup
        client = APIClient()
        client.force_authenticate(user=user_a)

        response = client.get("/api/v1/workspaces/organizations/")
        assert response.status_code == 200
        data = response.json()

        # Deve conter apenas a organização A
        org_ids = [item["id"] for item in data]
        assert str(org_a.id) in org_ids
        assert str(org_b.id) not in org_ids

    def test_user_b_only_lists_own_organization(self, multi_tenant_setup):
        user_a, user_b, _, org_a, org_b = multi_tenant_setup
        client = APIClient()
        client.force_authenticate(user=user_b)

        response = client.get("/api/v1/workspaces/organizations/")
        assert response.status_code == 200
        data = response.json()

        # Deve conter apenas a organização B
        org_ids = [item["id"] for item in data]
        assert str(org_b.id) in org_ids
        assert str(org_a.id) not in org_ids

    def test_superadmin_lists_all_organizations(self, multi_tenant_setup):
        _, _, superadmin, org_a, org_b = multi_tenant_setup
        client = APIClient()
        client.force_authenticate(user=superadmin)

        response = client.get("/api/v1/workspaces/organizations/")
        assert response.status_code == 200
        data = response.json()

        org_ids = [item["id"] for item in data]
        assert str(org_a.id) in org_ids
        assert str(org_b.id) in org_ids
