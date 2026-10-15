# core/tests/test_catalogs_and_search.py | AI-Control v0.0.1 | 15-10-2026 07:46(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import Role, JobTitle, Organization


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(username="dr.carlos", email="carlos@hospital.org", password="pass")
    user.first_name = "Carlos"
    user.last_name = "Eduardo"
    user.save()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestCatalogsAndSearch:

    def test_user_search_by_name_and_username(self, auth_client):
        client, current_user = auth_client
        # Cria outro usuário para busca
        User.objects.create_user(username="dra.beatriz", email="beatriz@hospital.org", password="pass")

        # Busca por username parcial
        res = client.get("/api/v1/users/search/?q=beatriz")
        assert res.status_code == 200
        data = res.json()
        assert "users" in data
        assert any(u["username"] == "dra.beatriz" for u in data["users"])

        # Busca por email
        res2 = client.get("/api/v1/users/search/?q=hospital.org")
        assert res2.status_code == 200
        assert len(res2.json()["users"]) >= 2

    def test_roles_catalog_filtered_by_scope(self, auth_client):
        client, _ = auth_client
        res = client.get("/api/v1/workspaces/catalog/roles/?scope=ORGANIZATION")
        assert res.status_code == 200
        roles = res.json()["roles"]
        assert len(roles) > 0
        assert all(r["scope"] == "ORGANIZATION" for r in roles)
        assert any(r["slug"] == "org_admin" for r in roles)

    def test_job_titles_catalog_filtered_by_level(self, auth_client):
        client, _ = auth_client
        res = client.get("/api/v1/workspaces/catalog/job-titles/?level=ORGANIZATION")
        assert res.status_code == 200
        titles = res.json()["job_titles"]
        assert len(titles) > 0
        assert all(t["level"] == "ORGANIZATION" for t in titles)
