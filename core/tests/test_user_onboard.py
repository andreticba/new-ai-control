# core/tests/test_user_onboard.py | AI-Control v0.0.1 | 14-10-2026 07:38(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import UserProfile


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(
        username="admin.onboard",
        email="admin.onboard@example.org",
        password="secretpassword"
    )
    UserProfile.objects.create(user=user, full_name="Admin Onboarding")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestUserOnboard:

    def test_quick_onboard_success(self, auth_client):
        payload = {
            "username": "dr.roberto",
            "email": "roberto.med@example.org",
            "full_name": "Dr. Roberto Medeiros"
        }
        response = auth_client.post("/api/v1/users/quick-onboard/", payload, format="json")
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "dr.roberto"
        assert data["email"] == "roberto.med@example.org"
        assert data["full_name"] == "Dr. Roberto Medeiros"
        assert "id" in data

        user = User.objects.get(username="dr.roberto")
        assert user.profile is not None
        assert user.profile.search_tokens is not None
        assert len(user.profile.search_tokens) > 0  # Blind Indexing gerado com sucesso!

    def test_quick_onboard_duplicate_username_fails(self, auth_client):
        User.objects.create_user(
            username="lucas.dev",
            email="lucas.antigo@example.org",
            password="pwd"
        )
        payload = {
            "username": "lucas.dev",
            "email": "lucas.novo@example.org",
            "full_name": "Lucas Dev"
        }
        response = auth_client.post("/api/v1/users/quick-onboard/", payload, format="json")
        assert response.status_code == 400
        error_msg = str(response.json())
        assert "username" in error_msg.lower() or "já existe" in error_msg.lower()

    def test_quick_onboard_duplicate_email_fails(self, auth_client):
        User.objects.create_user(
            username="maria.original",
            email="maria.corp@example.org",
            password="pwd"
        )
        payload = {
            "username": "maria.nova",
            "email": "maria.corp@example.org",
            "full_name": "Maria Silva"
        }
        response = auth_client.post("/api/v1/users/quick-onboard/", payload, format="json")
        assert response.status_code == 400
        error_msg = str(response.json())
        assert "email" in error_msg.lower() or "já existe" in error_msg.lower()
