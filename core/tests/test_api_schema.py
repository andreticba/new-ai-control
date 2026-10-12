# core/tests/test_api_schema.py | AI-Control v0.0.1 | 12-10-2026 09:30(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.test import override_settings


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_test",
        email="admin@example.org",
        password="adminpassword123"
    )


@pytest.mark.django_db
def test_schema_open_in_debug_mode(api_client):
    """Em ambiente de desenvolvimento (DEBUG=True), /api/schema/ deve ser público (HTTP 200)."""
    with override_settings(
        DEBUG=True,
        SPECTACULAR_SETTINGS={
            'TITLE': 'AI-Control API',
            'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
        }
    ):
        res = api_client.get('/api/schema/')
        assert res.status_code == 200
        assert 'openapi' in res.data or 'components' in res.data or 'info' in res.data


@pytest.mark.django_db
def test_schema_restricted_in_production_mode(api_client, admin_user):
    """Em ambiente de produção (DEBUG=False), /api/schema/ deve bloquear anônimos (401/403) e liberar admins."""
    with override_settings(
        DEBUG=False,
        SPECTACULAR_SETTINGS={
            'TITLE': 'AI-Control API',
            'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAdminUser'],
        }
    ):
        # 1. Anônimo -> Bloqueado
        res_anon = api_client.get('/api/schema/')
        assert res_anon.status_code in (401, 403)

        # 2. Usuário comum -> Bloqueado
        normal_user = User.objects.create_user(username="normal", password="password")
        api_client.force_authenticate(user=normal_user)
        res_normal = api_client.get('/api/schema/')
        assert res_normal.status_code == 403

        # 3. Superuser / Admin -> Permitido
        api_client.force_authenticate(user=admin_user)
        res_admin = api_client.get('/api/schema/')
        assert res_admin.status_code == 200
