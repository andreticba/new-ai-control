# core/tests/test_workspace_performance.py | AI-Control v0.0.1 | 14-10-2026 16:30(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    Organization,
    Department,
    Project,
    Squad,
    Role,
    OrganizationMembership,
    ProjectMembership,
    SquadMembership,
    UserProfile,
)


@pytest.fixture
def complex_workspace_user(db):
    user = User.objects.create_user(
        username="perf.user",
        email="perf.user@example.org",
        password="secretpassword"
    )
    UserProfile.objects.create(
        user=user,
        full_name="Performance Test User"
    )
    role_admin, _ = Role.objects.get_or_create(
        slug="org_admin",
        defaults={"name": "Org Admin", "scope": "ORGANIZATION"}
    )
    role_proj, _ = Role.objects.get_or_create(
        slug="project_lead",
        defaults={"name": "Project Lead", "scope": "PROJECT"}
    )
    role_squad, _ = Role.objects.get_or_create(
        slug="squad_member",
        defaults={"name": "Squad Member", "scope": "SQUAD"}
    )

    # Cria 3 organizações com departamentos, projetos e squads
    for i in range(3):
        org = Organization.objects.create(
            name=f"Org Perf {i}",
            slug=f"org-perf-{i}",
            org_type="COMPANY"
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role=role_admin,
            is_active=True
        )

        for d in range(2):
            Department.objects.create(
                organization=org,
                name=f"Dept {i}-{d}",
                slug=f"dept-{i}-{d}",
                code=f"D{i}{d}"
            )

        for p in range(2):
            proj = Project.objects.create(
                organization=org,
                name=f"Proj {i}-{p}",
                slug=f"proj-{i}-{p}",
                status="ACTIVE"
            )
            ProjectMembership.objects.create(
                user=user,
                project=proj,
                role=role_proj,
                is_active=True
            )

            for s in range(2):
                squad = Squad.objects.create(
                    project=proj,
                    name=f"Squad {i}-{p}-{s}",
                    slug=f"squad-{i}-{p}-{s}"
                )
                SquadMembership.objects.create(
                    user=user,
                    squad=squad,
                    role=role_squad,
                    is_active=True
                )

    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestWorkspacePerformance:

    def test_active_workspaces_query_count_anti_n1(self, complex_workspace_user, django_assert_num_queries):
        client = complex_workspace_user

        # Anti-N+1: A resolução da árvore completa deve ser executada em exatamente 4 queries em lote
        # Em vez do loop N+1 que executaria 1 + 3 + 3*2 + 3*2*2 = 22+ queries
        with django_assert_num_queries(4):
            response = client.get("/api/v1/workspaces/")

        assert response.status_code == 200
        data = response.json()
        assert "workspaces" in data
        assert len(data["workspaces"]) == 3
        # Valida que todos os departamentos, projetos e squads estão presentes
        for org_item in data["workspaces"]:
            assert len(org_item["departments"]) == 2
            assert len(org_item["projects"]) == 2
            for proj_item in org_item["projects"]:
                assert len(proj_item["squads"]) == 2
