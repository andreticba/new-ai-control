# core/tests/test_workspace_mutations.py | AI-Control v0.0.1 | 14-10-2026 07:23(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import Organization, Department, Project, Squad, UserProfile


@pytest.fixture
def auth_client(db):
    user = User.objects.create_superuser(
        username="admin.test",
        email="admin.test@example.org",
        password="secretpassword"
    )
    profile = UserProfile.objects.create(
        user=user,
        full_name="Admin Teste"
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestWorkspaceMutations:

    def test_create_organization_success(self, auth_client):
        client, user = auth_client
        payload = {
            "name": "Nova Biotech Inovadora",
            "slug": "nova-biotech",
            "org_type": "COMPANY",
            "is_active": True
        }
        response = client.post("/api/v1/workspaces/organizations/", payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Nova Biotech Inovadora"
        assert data["slug"] == "nova-biotech"
        assert Organization.objects.filter(slug="nova-biotech").exists()

    def test_create_department_success(self, auth_client):
        client, user = auth_client
        org = Organization.objects.create(name="Hospital Geral", slug="hosp-geral", org_type="CLINIC")
        payload = {
            "organization_id": str(org.id),
            "name": "Departamento de UTI",
            "code": "UTI",
            "description": "Unidade de Terapia Intensiva"
        }
        response = client.post("/api/v1/workspaces/departments/", payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Departamento de UTI"
        assert data["code"] == "UTI"
        assert Department.objects.filter(organization=org, code="UTI").exists()

    def test_create_project_success(self, auth_client):
        client, user = auth_client
        org = Organization.objects.create(name="Universidade Alpha", slug="uni-alpha", org_type="ACADEMIC")
        payload = {
            "organization_id": str(org.id),
            "name": "Portal de Telemedicina",
            "slug": "telemed-portal",
            "project_type": "RESEARCH",
            "status": "PLANNING",
            "description": "Pesquisa em teleatendimento"
        }
        response = client.post("/api/v1/workspaces/projects/", payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Portal de Telemedicina"
        assert data["status"] == "PLANNING"
        assert Project.objects.filter(organization=org, slug="telemed-portal").exists()

    def test_create_squad_success(self, auth_client):
        client, user = auth_client
        org = Organization.objects.create(name="Tech Corp", slug="tech-corp", org_type="COMPANY")
        project = Project.objects.create(organization=org, name="App Mobile", slug="app-mobile")
        payload = {
            "project_id": str(project.id),
            "name": "Squad Frontend Mobile",
            "slug": "squad-front-mob",
            "mission": "Desenvolver UI/UX reativa em Next/React",
            "is_active": True
        }
        response = client.post("/api/v1/workspaces/squads/", payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Squad Frontend Mobile"
        assert Squad.objects.filter(project=project, slug="squad-front-mob").exists()

    def test_create_squad_violating_p3_fails(self, auth_client):
        """Regra P3: Tentativa de criar squad sem projeto pai válido DEVE falhar com HTTP 400"""
        client, user = auth_client
        payload = {
            "project_id": "00000000-0000-0000-0000-000000000000",
            "name": "Squad Órfã Ilegal",
            "slug": "squad-orfa"
        }
        response = client.post("/api/v1/workspaces/squads/", payload, format="json")
        assert response.status_code == 400
        assert "project_id" in response.json() or "detail" in response.json()
