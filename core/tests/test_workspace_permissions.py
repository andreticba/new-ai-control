# core/tests/test_workspace_permissions.py | AI-Control v0.0.1 | 14-10-2026 07:44(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    Organization, Role, Permission, UserProfile, OrganizationMembership
)


@pytest.fixture
def rbac_setup(db):
    perm_manage, _ = Permission.objects.get_or_create(slug="org.manage", defaults={"name": "Gerenciar Organização"})

    role_admin, _ = Role.objects.get_or_create(
        slug="org_admin",
        defaults={"name": "Admin da Organização", "scope": Role.Scope.ORGANIZATION, "level": 100}
    )
    role_admin.permissions.add(perm_manage)

    role_viewer, _ = Role.objects.get_or_create(
        slug="org_viewer",
        defaults={"name": "Visualizador", "scope": Role.Scope.ORGANIZATION, "level": 10}
    )
    role_viewer.permissions.remove(perm_manage)

    org = Organization.objects.create(name="Hospital RBAC", slug="hosp-rbac", org_type="CLINIC")

    # Usuário Admin
    admin_user = User.objects.create_user(username="admin.rbac", email="admin.rbac@example.org", password="pwd")
    UserProfile.objects.create(user=admin_user, full_name="Admin RBAC")
    OrganizationMembership.objects.create(user=admin_user, organization=org, role=role_admin, is_active=True)

    # Usuário sem permissão de gestão
    limited_user = User.objects.create_user(username="viewer.rbac", email="viewer.rbac@example.org", password="pwd")
    UserProfile.objects.create(user=limited_user, full_name="Viewer RBAC")
    OrganizationMembership.objects.create(user=limited_user, organization=org, role=role_viewer, is_active=True)

    client_admin = APIClient()
    client_admin.force_authenticate(user=admin_user)

    client_limited = APIClient()
    client_limited.force_authenticate(user=limited_user)

    return {
        "client_admin": client_admin,
        "client_limited": client_limited,
        "org": org,
    }


@pytest.mark.django_db
class TestWorkspacePermissions:

    def test_limited_user_cannot_mutate_organization_forbidden(self, rbac_setup):
        """Usuário sem 'org.manage' deve receber HTTP 403 Forbidden em mutações."""
        client = rbac_setup["client_limited"]
        payload = {
            "name": "Org Não Autorizada",
            "slug": "org-nao-auth"
        }
        response = client.post("/api/v1/workspaces/organizations/", payload, format="json")
        assert response.status_code == 403

    def test_admin_user_can_mutate_organization_success(self, rbac_setup):
        """Usuário com 'org.manage' tem acesso autorizado (HTTP 201)."""
        client = rbac_setup["client_admin"]
        payload = {
            "name": "Org Autorizada",
            "slug": "org-auth"
        }
        response = client.post("/api/v1/workspaces/organizations/", payload, format="json")
        assert response.status_code == 201
