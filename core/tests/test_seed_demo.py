# core/tests/test_seed_demo.py | AI-Control v0.0.1 | 12-10-2026 09:20(GMT-04:00)
import pytest
from io import StringIO
from django.core.management import call_command
from django.contrib.auth.models import User
from core.models import (
    Organization, UserProfile, SquadMembership, ProjectMembership
)

CANONICAL_USERNAMES = [
    'prof.ana', 'prof.carlos', 'prof.lucia', 'aluno.joao', 'aluna.maria',
    'pesq.externo', 'tae.paulo',
    'gerente.ti', 'dev.rafa', 'supervisor.bia', 'atendente.leo',
    'analista.rh', 'diretora.fin',
]


@pytest.mark.django_db
def test_seed_demo_creates_13_personas_with_search_tokens():
    """Valida se o comando seed_demo instancia as 13 personas canônicas com search_tokens gerados."""
    out = StringIO()
    call_command('seed_demo', stdout=out)
    output = out.getvalue()

    # Verifica se as 13 personas existem
    for username in CANONICAL_USERNAMES:
        user = User.objects.filter(username=username).first()
        assert user is not None, f"Persona '{username}' não foi criada pelo seed_demo"
        profile = getattr(user, 'profile', None)
        assert profile is not None, f"UserProfile ausente para persona '{username}'"
        assert profile.full_name, f"full_name não preenchido para persona '{username}'"
        assert profile.search_tokens, f"search_tokens (Blind Indexing) vazio para '{username}'"

    # Verifica organizações demo
    assert Organization.objects.filter(slug='ufdemo').exists()
    assert Organization.objects.filter(slug='empresa-demo').exists()

    # Verifica impressão de tabela com credenciais
    assert "demo1234" in output


@pytest.mark.django_db
def test_seed_demo_preserves_internal_organization_and_operators():
    """Valida se a organização interna (ai-control) e operadores de plataforma são preservados."""
    # Garante que a organização interna e o operador de plataforma existem
    internal_org, _ = Organization.objects.get_or_create(
        slug='ai-control',
        defaults={'name': 'AI Control Interno', 'org_type': 'PLATFORM', 'is_internal': True}
    )
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.org', 'is_staff': True, 'is_superuser': True}
    )

    out = StringIO()
    call_command('seed_demo', stdout=out)

    # Executa o flush e garante que a org interna e o admin permanecem intactos
    call_command('seed_demo', flush=True, stdout=out)
    assert Organization.objects.filter(slug='ai-control', is_internal=True).exists()
    assert User.objects.filter(username='admin').exists()


@pytest.mark.django_db
def test_seed_demo_containment_rule():
    """Valida a Containment Rule: usuário em Squad deve obrigatoriamente estar no Projeto pai."""
    out = StringIO()
    call_command('seed_demo', stdout=out)

    squad_memberships = SquadMembership.objects.all()
    assert squad_memberships.count() > 0

    for sm in squad_memberships:
        parent_project = sm.squad.project
        has_project_membership = ProjectMembership.objects.filter(
            user=sm.user, project=parent_project
        ).exists()
        assert has_project_membership, (
            f"Containment Rule violada: Usuário {sm.user.username} na Squad {sm.squad.slug} "
            f"não possui ProjectMembership no Projeto pai {parent_project.slug}"
        )
