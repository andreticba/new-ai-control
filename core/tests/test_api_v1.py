# core/tests/test_api_v1.py | AI-Control v0.0.1 | 12-10-2026 09:30(GMT-04:00)
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from core.models import (
    Organization, Department, Project, Squad,
    Role, JobTitle, UserProfile,
    OrganizationMembership, ProjectMembership, SquadMembership,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def demo_setup(db):
    user = User.objects.create_user(
        username="prof.ana",
        email="prof.ana@example.org",
        password="demo1234"
    )
    profile = UserProfile.objects.create(
        user=user,
        full_name="Profa. Ana Santos"
    )

    org = Organization.objects.create(
        name="Universidade Federal Demo",
        slug="ufdemo",
        org_type="ACADEMIC"
    )
    profile.primary_organization = org
    profile.save()

    dept = Department.objects.create(
        organization=org,
        name="Depto. de Computação",
        code="DCOMP",
        slug="dcomp"
    )

    role_org = Role.objects.filter(slug='org_member').first()
    title_prof = JobTitle.objects.filter(slug='professor', organization__isnull=True).first()

    OrganizationMembership.objects.create(
        user=user,
        organization=org,
        role=role_org,
        job_title=title_prof,
        department=dept
    )

    proj = Project.objects.create(
        organization=org,
        name="Saúde Digital na Comunidade",
        slug="saude-digital",
        project_type="EXTENSION",
        owner_department=dept
    )
    role_proj_lead = Role.objects.filter(slug='project_lead').first()
    title_coord = JobTitle.objects.filter(slug='project_coordinator', organization__isnull=True).first()

    ProjectMembership.objects.create(
        user=user,
        project=proj,
        role=role_proj_lead,
        job_title=title_coord
    )

    sq = Squad.objects.create(
        project=proj,
        name="Squad App Móvel",
        slug="app-movel"
    )
    role_sq_lead = Role.objects.filter(slug='squad_lead').first()
    title_tech_lead = JobTitle.objects.filter(slug='tech_lead', organization__isnull=True).first()

    SquadMembership.objects.create(
        user=user,
        squad=sq,
        role=role_sq_lead,
        job_title=title_tech_lead
    )

    return user, org, proj, sq


@pytest.mark.django_db
def test_jwt_auth_flow(api_client, demo_setup):
    """Testa emissão e rotação de tokens JWT via /api/v1/auth/token/."""
    user, org, proj, sq = demo_setup

    # 1. Login com credenciais válidas
    res = api_client.post('/api/v1/auth/token/', {
        'username': 'prof.ana',
        'password': 'demo1234'
    }, format='json')
    assert res.status_code == 200
    data = res.json()
    assert 'access' in data
    assert 'refresh' in data
    access_token = data['access']
    refresh_token = data['refresh']

    # 2. Renovação de token de acesso com o refresh token
    res_refresh = api_client.post('/api/v1/auth/token/refresh/', {
        'refresh': refresh_token
    }, format='json')
    assert res_refresh.status_code == 200
    assert 'access' in res_refresh.json()

    # 3. Tentativa de login com senha incorreta -> 401
    res_fail = api_client.post('/api/v1/auth/token/', {
        'username': 'prof.ana',
        'password': 'wrongpassword'
    }, format='json')
    assert res_fail.status_code == 401


@pytest.mark.django_db
def test_users_me_endpoint(api_client, demo_setup):
    """Testa GET /api/v1/users/me/ agregando perfil, organização primária e memberships 4-tier."""
    user, org, proj, sq = demo_setup

    # Obter token
    res = api_client.post('/api/v1/auth/token/', {
        'username': 'prof.ana',
        'password': 'demo1234'
    }, format='json')
    token = res.json()['access']

    # Requisição desautenticada -> 401
    res_unauth = api_client.get('/api/v1/users/me/')
    assert res_unauth.status_code == 401

    # Requisição autenticada
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    res_me = api_client.get('/api/v1/users/me/')
    assert res_me.status_code == 200
    me_data = res_me.json()

    assert me_data['username'] == 'prof.ana'
    assert me_data['email'] == 'prof.ana@example.org'
    assert me_data['full_name'] == 'Profa. Ana Santos'
    assert me_data['primary_organization']['slug'] == 'ufdemo'

    memberships = me_data['memberships']
    assert memberships['organization']['role'] == 'org_member'
    assert memberships['organization']['job_title'] == 'Professor(a)'
    assert memberships['organization']['department'] == 'DCOMP'

    assert len(memberships['projects']) == 1
    assert memberships['projects'][0]['project_slug'] == 'saude-digital'
    assert memberships['projects'][0]['role'] == 'project_lead'

    assert len(memberships['squads']) == 1
    assert memberships['squads'][0]['squad_slug'] == 'app-movel'
    assert memberships['squads'][0]['role'] == 'squad_lead'


@pytest.mark.django_db
def test_workspaces_endpoint(api_client, demo_setup):
    """Testa GET /api/v1/workspaces/ retornando a árvore hierárquica completa dos 4 níveis."""
    user, org, proj, sq = demo_setup

    res = api_client.post('/api/v1/auth/token/', {
        'username': 'prof.ana',
        'password': 'demo1234'
    }, format='json')
    token = res.json()['access']

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    res_ws = api_client.get('/api/v1/workspaces/')
    assert res_ws.status_code == 200
    ws_data = res_ws.json()

    assert 'workspaces' in ws_data
    assert len(ws_data['workspaces']) == 1

    ws = ws_data['workspaces'][0]
    assert ws['slug'] == 'ufdemo'
    assert ws['org_type'] == 'ACADEMIC'
    assert ws['role'] == 'org_member'
    assert ws['job_title'] == 'Professor(a)'

    assert len(ws['departments']) == 1
    assert ws['departments'][0]['code'] == 'DCOMP'

    assert len(ws['projects']) == 1
    p = ws['projects'][0]
    assert p['slug'] == 'saude-digital'
    assert p['role'] == 'project_lead'

    assert len(p['squads']) == 1
    s = p['squads'][0]
    assert s['slug'] == 'app-movel'
    assert s['role'] == 'squad_lead'


@pytest.mark.django_db
def test_cors_policy_headers(api_client):
    """Testa se o middleware de CORS adiciona os cabeçalhos apropriados para a origem permitida."""
    res = api_client.options('/api/v1/auth/token/', HTTP_ORIGIN='http://localhost:3000')
    assert res.headers.get('Access-Control-Allow-Origin') == 'http://localhost:3000'
