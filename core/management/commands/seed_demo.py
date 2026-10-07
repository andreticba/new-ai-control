# core/management/commands/seed_demo.py | Atualizado em: 06-10-2026 21:56:00(GMT-04:00)
"""
Cria organizações de demonstração (acadêmica e/ou corporativa) com projetos,
squads, departamentos e usuários-exemplo para validar o RBAC hierárquico.

Uso:
    python manage.py seed_demo                 # cria tudo
    python manage.py seed_demo --profile=academic
    python manage.py seed_demo --profile=corporate
    python manage.py seed_demo --flush         # remove os dados demo
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from core.models import (
    Organization, Department, Project, Squad,
    Role, JobTitle, UserProfile,
    OrganizationMembership, ProjectMembership, SquadMembership,
)

DEMO_PASSWORD = os.environ.get('DEMO_PASSWORD', 'demo1234')
DEMO_DOMAIN = 'demo.local'


def _role(slug):
    return Role.objects.filter(slug=slug).first()


def _title(slug):
    return JobTitle.objects.filter(slug=slug, organization__isnull=True).first()


def _create_user(username, email, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'password': make_password(DEMO_PASSWORD),
            'is_staff': is_staff,
        }
    )
    if created:
        UserProfile.objects.get_or_create(user=user)
    return user, created


# ═══════════════════════════════════════════════════════════════════════════════
# ACADEMIC PROFILE — "Universidade Federal Demo"
# ═══════════════════════════════════════════════════════════════════════════════

def seed_academic(stdout):
    stdout.write("  ── Perfil ACADÊMICO ──────────────────────────────────────")

    org, _ = Organization.objects.get_or_create(
        slug='ufdemo',
        defaults={'name': 'Universidade Federal Demo', 'org_type': 'ACADEMIC'}
    )

    # Departamentos
    depts = {}
    for code, name, slug in [
        ('PROPESQ', 'Pró-Reitoria de Pesquisa', 'propesq'),
        ('PROEC', 'Pró-Reitoria de Extensão', 'proec'),
        ('DCOMP', 'Depto. de Computação', 'dcomp'),
        ('DENF', 'Depto. de Enfermagem', 'denf'),
        ('FIN', 'Financeiro', 'financeiro'),
        ('SGP', 'Gestão de Pessoas', 'sgp'),
    ]:
        d, _ = Department.objects.get_or_create(
            organization=org, slug=slug, defaults={'name': name, 'code': code}
        )
        depts[code] = d

    # Projetos
    proj_saude, _ = Project.objects.get_or_create(
        organization=org, slug='saude-digital',
        defaults={
            'name': 'Saúde Digital na Comunidade',
            'project_type': 'EXTENSION', 'status': 'ACTIVE',
            'owner_department': depts['PROEC'],
        }
    )
    proj_ia, _ = Project.objects.get_or_create(
        organization=org, slug='ia-triagem',
        defaults={
            'name': 'IA para Triagem Clínica',
            'project_type': 'RESEARCH', 'status': 'ACTIVE',
            'owner_department': depts['PROPESQ'],
        }
    )

    # Squads
    sq_app, _ = Squad.objects.get_or_create(project=proj_saude, slug='app-movel', defaults={'name': 'Squad App Móvel'})
    sq_campo, _ = Squad.objects.get_or_create(project=proj_saude, slug='campo-coleta', defaults={'name': 'Squad Campo-Coleta'})
    sq_model, _ = Squad.objects.get_or_create(project=proj_ia, slug='modelagem', defaults={'name': 'Squad Modelagem'})
    sq_dados, _ = Squad.objects.get_or_create(project=proj_ia, slug='dados-clinicos', defaults={'name': 'Squad Dados Clínicos'})

    # Usuários
    users_spec = [
        # (username, org_role, org_title, org_dept, [(project, role, title, squad_specs)])
        ('prof.ana', 'org_member', 'professor', 'DCOMP', [
            (proj_saude, 'project_lead', 'project_coordinator', [
                (sq_app, 'squad_lead', 'tech_lead'),
            ]),
            (proj_ia, 'project_viewer', 'collaborating_researcher', []),
        ]),
        ('prof.carlos', 'org_manager', 'pro_rector', 'PROPESQ', [
            (proj_ia, 'project_lead', 'project_coordinator', []),
        ]),
        ('prof.lucia', 'org_member', 'professor', 'DENF', [
            (proj_saude, 'project_member', 'project_vice_coordinator', [
                (sq_campo, 'squad_lead', 'field_researcher'),
            ]),
        ]),
        ('aluno.joao', 'org_member', 'undergrad_student', 'DCOMP', [
            (proj_saude, 'project_member', 'scholarship_holder', [
                (sq_app, 'squad_member', 'developer'),
            ]),
        ]),
        ('aluna.maria', 'org_member', 'masters_student', 'DCOMP', [
            (proj_ia, 'project_member', 'scholarship_holder', [
                (sq_model, 'squad_member', 'data_analyst'),
            ]),
        ]),
        ('pesq.externo', 'org_guest', 'researcher', None, [
            (proj_ia, 'project_member', 'external_partner', [
                (sq_dados, 'squad_viewer', None),
            ]),
        ]),
        ('tae.paulo', 'org_member', 'technician', 'FIN', []),
    ]

    for username, org_role, org_title_slug, dept_code, projects in users_spec:
        user, created = _create_user(username, f"{username}@{DEMO_DOMAIN}")
        if not created:
            stdout.write(f"    -> {username} já existe, pulando.")
            continue

        profile = user.profile
        profile.primary_organization = org
        profile.save()

        dept = depts.get(dept_code)
        OrganizationMembership.objects.create(
            user=user, organization=org,
            role=_role(org_role), job_title=_title(org_title_slug),
            department=dept,
        )

        for proj, proj_role, proj_title, squad_specs in projects:
            is_ext = (org_role == 'org_guest')
            ProjectMembership.objects.create(
                user=user, project=proj,
                role=_role(proj_role), job_title=_title(proj_title),
                is_external=is_ext,
            )
            for sq, sq_role, sq_title in squad_specs:
                SquadMembership.objects.create(
                    user=user, squad=sq,
                    role=_role(sq_role), job_title=_title(sq_title) if sq_title else None,
                )

        stdout.write(f"    -> {username} criado com memberships.")


# ═══════════════════════════════════════════════════════════════════════════════
# CORPORATE PROFILE — "Empresa Demo Ltda"
# ═══════════════════════════════════════════════════════════════════════════════

def seed_corporate(stdout):
    stdout.write("  ── Perfil CORPORATIVO ───────────────────────────────────")

    org, _ = Organization.objects.get_or_create(
        slug='empresa-demo',
        defaults={'name': 'Empresa Demo Ltda', 'org_type': 'COMPANY'}
    )

    depts = {}
    for code, name, slug in [
        ('FIN', 'Financeiro', 'financeiro'),
        ('RH', 'Recursos Humanos', 'rh'),
        ('COM', 'Comercial', 'comercial'),
        ('ATD', 'Atendimento', 'atendimento'),
        ('TI', 'Tecnologia', 'ti'),
    ]:
        d, _ = Department.objects.get_or_create(
            organization=org, slug=slug, defaults={'name': name, 'code': code}
        )
        depts[code] = d

    proj_crm, _ = Project.objects.get_or_create(
        organization=org, slug='implantacao-crm',
        defaults={
            'name': 'Implantação CRM WhatsApp',
            'project_type': 'CORPORATE', 'status': 'ACTIVE',
            'owner_department': depts['TI'],
        }
    )

    sq_integ, _ = Squad.objects.get_or_create(project=proj_crm, slug='integracao', defaults={'name': 'Squad Integração'})
    sq_bot, _ = Squad.objects.get_or_create(project=proj_crm, slug='conteudo-bot', defaults={'name': 'Squad Conteúdo do Bot'})

    users_spec = [
        ('gerente.ti', 'org_manager', 'manager', 'TI', [
            (proj_crm, 'project_lead', 'project_manager', [(sq_integ, 'squad_lead', 'squad_leader')]),
        ]),
        ('dev.rafa', 'org_member', 'analyst', 'TI', [
            (proj_crm, 'project_member', None, [(sq_integ, 'squad_member', 'developer')]),
        ]),
        ('supervisor.bia', 'org_supervisor', 'supervisor', 'ATD', [
            (proj_crm, 'project_member', 'product_owner', [(sq_bot, 'squad_lead', 'squad_leader')]),
        ]),
        ('atendente.leo', 'org_agent', 'attendant', 'ATD', []),
        ('analista.rh', 'org_member', 'analyst', 'RH', []),
        ('diretora.fin', 'org_admin', 'director', 'FIN', [
            (proj_crm, 'project_viewer', 'sponsor', []),
        ]),
    ]

    for username, org_role, org_title_slug, dept_code, projects in users_spec:
        user, created = _create_user(username, f"{username}@{DEMO_DOMAIN}")
        if not created:
            stdout.write(f"    -> {username} já existe, pulando.")
            continue

        profile = user.profile
        profile.primary_organization = org
        profile.save()

        OrganizationMembership.objects.create(
            user=user, organization=org,
            role=_role(org_role), job_title=_title(org_title_slug),
            department=depts.get(dept_code),
        )

        for proj, proj_role, proj_title, squad_specs in projects:
            ProjectMembership.objects.create(
                user=user, project=proj,
                role=_role(proj_role), job_title=_title(proj_title) if proj_title else None,
            )
            for sq, sq_role, sq_title in squad_specs:
                SquadMembership.objects.create(
                    user=user, squad=sq,
                    role=_role(sq_role), job_title=_title(sq_title) if sq_title else None,
                )

        stdout.write(f"    -> {username} criado com memberships.")


def flush_demo(stdout):
    """Remove tudo que foi criado pelo seed_demo."""
    demo_slugs = ['ufdemo', 'empresa-demo']
    demo_usernames = [
        'prof.ana', 'prof.carlos', 'prof.lucia', 'aluno.joao', 'aluna.maria',
        'pesq.externo', 'tae.paulo',
        'gerente.ti', 'dev.rafa', 'supervisor.bia', 'atendente.leo',
        'analista.rh', 'diretora.fin',
    ]
    deleted_users, _ = User.objects.filter(username__in=demo_usernames).delete()
    deleted_orgs, _ = Organization.objects.filter(slug__in=demo_slugs).delete()
    stdout.write(f"  -> {deleted_users} usuários demo e {deleted_orgs} organizações demo removidos.")


class Command(BaseCommand):
    help = "Semeia dados de demonstração (acadêmico e/ou corporativo)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile',
            choices=['academic', 'corporate', 'all'],
            default='all',
            help='Qual perfil de demo criar (default: all)',
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Remove todos os dados demo antes de criar.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            flush_demo(self.stdout)

        profile = options['profile']
        if profile in ('academic', 'all'):
            seed_academic(self.stdout)
        if profile in ('corporate', 'all'):
            seed_corporate(self.stdout)

        self.stdout.write(self.style.SUCCESS("\n  ✅ Seed demo concluído."))
