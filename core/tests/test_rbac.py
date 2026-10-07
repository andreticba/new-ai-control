# core/tests/test_rbac.py | Atualizado em: 06-10-2026 21:45:00(GMT-04:00)
import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from core.models import (
    Permission, Role, Organization, Department, Project, Squad,
    UserProfile, OrganizationMembership, ProjectMembership, SquadMembership,
)


@pytest.fixture
def role_catalog(db):
    """Retrieves or creates the minimal RBAC catalog for testing.
    
    The seed migration (0008) already populates the catalog in production,
    so we use get_or_create to be idempotent.
    """
    # Permissions
    perms = {}
    for slug in [
        'org.manage_whatsapp', 'org.manage_members',
        'project.view', 'document.read', 'rag.query',
        'squad.view',
    ]:
        obj, _ = Permission.objects.get_or_create(slug=slug, defaults={'name': slug})
        perms[slug] = obj

    # Roles
    org_admin, _ = Role.objects.get_or_create(
        slug='org_admin',
        defaults={'name': 'Admin', 'scope': 'ORGANIZATION', 'level': 90, 'is_system_role': True}
    )
    if not org_admin.permissions.exists():
        org_admin.permissions.set(perms.values())

    org_member, _ = Role.objects.get_or_create(
        slug='org_member',
        defaults={'name': 'Membro', 'scope': 'ORGANIZATION', 'level': 30, 'is_system_role': True}
    )
    if not org_member.permissions.filter(slug='document.read').exists():
        org_member.permissions.set([perms['document.read'], perms['rag.query']])

    org_guest, _ = Role.objects.get_or_create(
        slug='org_guest',
        defaults={'name': 'Convidado', 'scope': 'ORGANIZATION', 'level': 10, 'is_system_role': True}
    )
    if not org_guest.permissions.filter(slug='document.read').exists():
        org_guest.permissions.set([perms['document.read']])

    project_lead, _ = Role.objects.get_or_create(
        slug='project_lead',
        defaults={'name': 'Coord.', 'scope': 'PROJECT', 'level': 70, 'is_system_role': True}
    )
    if not project_lead.permissions.filter(slug='project.view').exists():
        project_lead.permissions.set([perms['project.view'], perms['document.read']])

    project_member, _ = Role.objects.get_or_create(
        slug='project_member',
        defaults={'name': 'Membro Projeto', 'scope': 'PROJECT', 'level': 30, 'is_system_role': True}
    )
    if not project_member.permissions.filter(slug='project.view').exists():
        project_member.permissions.set([perms['project.view'], perms['document.read']])

    squad_member, _ = Role.objects.get_or_create(
        slug='squad_member',
        defaults={'name': 'Membro Squad', 'scope': 'SQUAD', 'level': 30, 'is_system_role': True}
    )
    if not squad_member.permissions.filter(slug='squad.view').exists():
        squad_member.permissions.set([perms['squad.view'], perms['document.read']])

    return {
        'perms': perms,
        'org_admin': org_admin,
        'org_member': org_member,
        'org_guest': org_guest,
        'project_lead': project_lead,
        'project_member': project_member,
        'squad_member': squad_member,
    }


@pytest.fixture
def org_structure(db, role_catalog):
    """Creates two orgs with a project and squad."""
    org_a = Organization.objects.create(name="Org A", slug="org-a")
    org_b = Organization.objects.create(name="Org B", slug="org-b")
    dept_a = Department.objects.create(organization=org_a, name="Engenharia", slug="eng", code="ENG")
    project = Project.objects.create(organization=org_a, name="Projeto Alpha", slug="alpha", status='ACTIVE')
    squad = Squad.objects.create(project=project, name="Squad Backend", slug="backend")
    return {
        'org_a': org_a, 'org_b': org_b, 'dept_a': dept_a,
        'project': project, 'squad': squad,
        **role_catalog,
    }


@pytest.mark.django_db
class TestMembershipIntegrity:
    """Tests P3: membership at lower level requires active membership above."""

    def test_org_membership_created(self, org_structure):
        user = User.objects.create_user(username="test_om", password="123")
        m = OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_member']
        )
        assert m.is_active
        assert m.role.scope == 'ORGANIZATION'

    def test_project_membership_requires_org(self, org_structure):
        user = User.objects.create_user(username="test_pm", password="123")
        # No org membership → should fail
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            ProjectMembership.objects.create(
                user=user, project=org_structure['project'],
                role=org_structure['project_member'],
            )

    def test_project_membership_succeeds_with_org(self, org_structure):
        user = User.objects.create_user(username="test_pms", password="123")
        OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_member']
        )
        pm = ProjectMembership.objects.create(
            user=user, project=org_structure['project'],
            role=org_structure['project_member'],
        )
        assert pm.is_active

    def test_squad_membership_requires_project(self, org_structure):
        user = User.objects.create_user(username="test_sm", password="123")
        OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_member']
        )
        # No project membership → should fail
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            SquadMembership.objects.create(
                user=user, squad=org_structure['squad'],
                role=org_structure['squad_member'],
            )

    def test_squad_membership_full_chain(self, org_structure):
        user = User.objects.create_user(username="test_fc", password="123")
        OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_member']
        )
        ProjectMembership.objects.create(
            user=user, project=org_structure['project'],
            role=org_structure['project_member'],
        )
        sm = SquadMembership.objects.create(
            user=user, squad=org_structure['squad'],
            role=org_structure['squad_member'],
        )
        assert sm.is_active

    def test_wrong_scope_role_rejected(self, org_structure):
        """A project-scoped role cannot be used in an org membership."""
        user = User.objects.create_user(username="test_ws", password="123")
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            OrganizationMembership.objects.create(
                user=user, organization=org_structure['org_a'],
                role=org_structure['project_lead'],  # wrong scope
            )

    def test_external_member_needs_org_guest(self, org_structure):
        """An external collaborator must have org_guest role."""
        user = User.objects.create_user(username="test_ext", password="123")
        # Give org_member instead of org_guest
        OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_member']
        )
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            ProjectMembership.objects.create(
                user=user, project=org_structure['project'],
                role=org_structure['project_member'],
                is_external=True,  # requires org_guest
            )


@pytest.mark.django_db
class TestMiddlewareRBAC:
    """Tests the RBAC middleware for gateway access."""

    def test_gateway_access_admin_allowed(self, org_structure):
        from core.middleware import rbac_middleware

        user = User.objects.create_user(username="gw_admin", password="123")
        OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_admin'],
        )

        factory = RequestFactory()
        request = factory.get('/api/v1/gateway/')
        request.user = user

        # Ensure profile exists (middleware checks it)
        UserProfile.objects.create(user=user, primary_organization=org_structure['org_a'])

        def dummy_view(request):
            return "OK"

        response = rbac_middleware(dummy_view)(request)
        assert response == "OK"

    def test_gateway_access_member_denied(self, org_structure):
        from core.middleware import rbac_middleware
        from core.models import AuditLog

        user = User.objects.create_user(username="gw_member", password="123")
        UserProfile.objects.create(user=user, primary_organization=org_structure['org_a'])
        OrganizationMembership.objects.create(
            user=user, organization=org_structure['org_a'],
            role=org_structure['org_member'],
        )

        factory = RequestFactory()
        request = factory.get('/api/v1/gateway/')
        request.user = user

        def dummy_view(request):
            return "OK"

        response = rbac_middleware(dummy_view)(request)
        assert response.status_code == 403
        assert AuditLog.objects.filter(action='FAILED_LOGIN').exists()
