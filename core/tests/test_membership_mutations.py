# core/tests/test_membership_mutations.py | AI-Control v0.0.1 | 14-10-2026 07:31(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    Organization, Department, Project, Squad,
    Role, JobTitle, UserProfile,
    OrganizationMembership, ProjectMembership, SquadMembership,
)


@pytest.fixture
def test_setup(db):
    admin_user = User.objects.create_superuser(
        username="admin.mem",
        email="admin.mem@example.org",
        password="secretpassword"
    )
    target_user = User.objects.create_user(
        username="colab.joao",
        email="joao@example.org",
        password="secretpassword"
    )
    UserProfile.objects.create(user=admin_user, full_name="Admin Membros")
    UserProfile.objects.create(user=target_user, full_name="João Silva")

    org = Organization.objects.create(name="Tech Enterprise", slug="tech-ent", org_type="COMPANY")
    dept = Department.objects.create(organization=org, name="Engenharia", code="ENG", slug="eng")
    proj = Project.objects.create(organization=org, name="Core Banking", slug="core-bank")
    squad = Squad.objects.create(project=proj, name="Squad Pagamentos", slug="squad-pag")

    role_org = Role.objects.filter(slug='org_member').first()
    if not role_org:
        role_org = Role.objects.create(name="Membro Org", slug="org_member", scope="ORGANIZATION", level=10)

    role_proj = Role.objects.filter(slug='proj_member').first()
    if not role_proj:
        role_proj = Role.objects.create(name="Membro Projeto", slug="proj_member", scope="PROJECT", level=10)

    role_squad = Role.objects.filter(slug='squad_member').first()
    if not role_squad:
        role_squad = Role.objects.create(name="Membro Squad", slug="squad_member", scope="SQUAD", level=10)

    client = APIClient()
    client.force_authenticate(user=admin_user)

    return {
        "client": client,
        "admin_user": admin_user,
        "target_user": target_user,
        "org": org,
        "dept": dept,
        "proj": proj,
        "squad": squad,
        "role_org": role_org,
        "role_proj": role_proj,
        "role_squad": role_squad,
    }


@pytest.mark.django_db
class TestMembershipMutations:

    def test_allocate_organization_membership_success(self, test_setup):
        s = test_setup
        payload = {
            "organization_id": str(s["org"].id),
            "user_id": s["target_user"].id,
            "role_id": str(s["role_org"].id),
            "department_id": str(s["dept"].id),
        }
        response = s["client"].post("/api/v1/workspaces/memberships/organization/", payload, format="json")
        assert response.status_code == 201
        assert OrganizationMembership.objects.filter(
            user=s["target_user"], organization=s["org"], is_active=True
        ).exists()

    def test_allocate_project_membership_success(self, test_setup):
        s = test_setup
        # Pré-requisito: usuário deve estar na organização
        OrganizationMembership.objects.create(
            user=s["target_user"],
            organization=s["org"],
            role=s["role_org"],
            is_active=True
        )
        payload = {
            "project_id": str(s["proj"].id),
            "user_id": s["target_user"].id,
            "role_id": str(s["role_proj"].id),
        }
        response = s["client"].post("/api/v1/workspaces/memberships/project/", payload, format="json")
        assert response.status_code == 201
        assert ProjectMembership.objects.filter(
            user=s["target_user"], project=s["proj"], is_active=True
        ).exists()

    def test_allocate_squad_membership_success(self, test_setup):
        s = test_setup
        # Pré-requisitos P3: usuário ativo na organização e no projeto pai
        OrganizationMembership.objects.create(
            user=s["target_user"],
            organization=s["org"],
            role=s["role_org"],
            is_active=True
        )
        ProjectMembership.objects.create(
            user=s["target_user"],
            project=s["proj"],
            role=s["role_proj"],
            is_active=True
        )
        payload = {
            "squad_id": str(s["squad"].id),
            "user_id": s["target_user"].id,
            "role_id": str(s["role_squad"].id),
        }
        response = s["client"].post("/api/v1/workspaces/memberships/squad/", payload, format="json")
        assert response.status_code == 201
        assert SquadMembership.objects.filter(
            user=s["target_user"], squad=s["squad"], is_active=True
        ).exists()

    def test_allocate_squad_without_project_membership_fails(self, test_setup):
        """Regra P3: Sem vínculo no projeto pai, a tentativa de alocação em squad DEVE falhar com HTTP 400."""
        s = test_setup
        payload = {
            "squad_id": str(s["squad"].id),
            "user_id": s["target_user"].id,
            "role_id": str(s["role_squad"].id),
        }
        response = s["client"].post("/api/v1/workspaces/memberships/squad/", payload, format="json")
        assert response.status_code == 400
        error_msg = str(response.json())
        assert "projeto pai" in error_msg.lower() or "vínculo" in error_msg.lower() or "p3" in error_msg.lower()

    def test_allocate_squad_with_inactive_project_membership_fails(self, test_setup):
        """Regra P3 contínua: Com vínculo INATIVO no projeto pai, a alocação em squad DEVE falhar com HTTP 400."""
        s = test_setup
        ProjectMembership.objects.create(
            user=s["target_user"],
            project=s["proj"],
            role=s["role_proj"],
            is_active=False  # Vínculo inativo!
        )
        payload = {
            "squad_id": str(s["squad"].id),
            "user_id": s["target_user"].id,
            "role_id": str(s["role_squad"].id),
        }
        response = s["client"].post("/api/v1/workspaces/memberships/squad/", payload, format="json")
        assert response.status_code == 400
        error_msg = str(response.json())
        assert "projeto pai" in error_msg.lower() or "vínculo" in error_msg.lower() or "ativo" in error_msg.lower()
