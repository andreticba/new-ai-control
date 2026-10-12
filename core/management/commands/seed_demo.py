# core/management/commands/seed_demo.py | AI-Control v0.0.1 | 12-10-2026 09:20(GMT-04:00)
"""
Cria organizações de demonstração (acadêmica e/ou corporativa) com projetos,
squads, departamentos, 13 personas canônicas, Blind Indexing (search_tokens),
vínculos omnichannel (soft FKs) e tabela de credenciais para desenvolvimento/testes.

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
from django.utils import timezone
from core.models import (
    Organization, Department, Project, Squad,
    Role, JobTitle, UserProfile,
    OrganizationMembership, ProjectMembership, SquadMembership,
)
from omnichannel.models import (
    Contact, ContactPhoneNumber, ContactOrganizationMembership,
    Conversation, Message
)

DEMO_PASSWORD = os.environ.get('DEMO_PASSWORD', 'demo1234')

DEMO_USERNAMES = [
    'prof.ana', 'prof.carlos', 'prof.lucia', 'aluno.joao', 'aluna.maria',
    'pesq.externo', 'tae.paulo',
    'gerente.ti', 'dev.rafa', 'supervisor.bia', 'atendente.leo',
    'analista.rh', 'diretora.fin',
]


def _role(slug):
    return Role.objects.filter(slug=slug).first()


def _title(slug):
    if not slug:
        return None
    return JobTitle.objects.filter(slug=slug, organization__isnull=True).first()


def _create_user(username, email, full_name, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'password': make_password(DEMO_PASSWORD),
            'is_staff': is_staff,
            'is_active': True,
        }
    )
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.full_name = full_name
    profile.save()
    return user, created


# ═══════════════════════════════════════════════════════════════════════════════
# ACADEMIC PROFILE — "Universidade Federal Demo"
# ═══════════════════════════════════════════════════════════════════════════════

def seed_academic(stdout):
    stdout.write("  ── Perfil ACADÊMICO (Universidade Federal Demo) ─────────────")

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

    # 7 Personas Canônicas
    users_spec = [
        ('prof.ana', 'prof.ana@example.org', 'Profa. Ana Santos', 'org_member', 'professor', 'DCOMP', [
            (proj_saude, 'project_lead', 'project_coordinator', [
                (sq_app, 'squad_lead', 'tech_lead'),
            ]),
            (proj_ia, 'project_member', 'collaborating_researcher', []),
        ]),
        ('prof.carlos', 'prof.carlos@example.org', 'Prof. Carlos Eduardo', 'org_manager', 'pro_rector', 'PROPESQ', [
            (proj_ia, 'project_lead', 'project_coordinator', []),
        ]),
        ('prof.lucia', 'prof.lucia@example.org', 'Profa. Lúcia Oliveira', 'org_member', 'professor', 'DENF', [
            (proj_saude, 'project_lead', 'project_coordinator', [
                (sq_campo, 'squad_lead', 'squad_leader'),
            ]),
        ]),
        ('aluno.joao', 'aluno.joao@example.org', 'João Victor Aluno', 'org_member', 'undergrad_student', 'DCOMP', [
            (proj_saude, 'project_member', 'scholarship_holder', [
                (sq_app, 'squad_member', 'developer'),
            ]),
        ]),
        ('aluna.maria', 'aluna.maria@example.org', 'Maria Clara Aluna', 'org_member', 'masters_student', 'DCOMP', [
            (proj_ia, 'project_member', 'scholarship_holder', [
                (sq_model, 'squad_member', 'developer'),
            ]),
        ]),
        ('pesq.externo', 'pesq.externo@example.org', 'Dr. Roberto Pesquisador', 'org_guest', 'researcher', None, [
            (proj_ia, 'project_member', 'collaborating_researcher', [
                (sq_dados, 'squad_member', 'developer'),
            ]),
        ]),
        ('tae.paulo', 'tae.paulo@example.org', 'Paulo Henrique TAE', 'org_member', 'technician', 'FIN', []),
    ]

    for username, email, full_name, org_role, org_title_slug, dept_code, projects in users_spec:
        user, _ = _create_user(username, email, full_name)

        profile = user.profile
        profile.primary_organization = org
        profile.save()

        dept = depts.get(dept_code)
        OrganizationMembership.objects.get_or_create(
            user=user, organization=org,
            defaults={
                'role': _role(org_role),
                'job_title': _title(org_title_slug),
                'department': dept,
            }
        )

        for proj, proj_role, proj_title, squad_specs in projects:
            is_ext = (org_role == 'org_guest')
            ProjectMembership.objects.get_or_create(
                user=user, project=proj,
                defaults={
                    'role': _role(proj_role),
                    'job_title': _title(proj_title),
                    'is_external': is_ext,
                }
            )
            for sq, sq_role, sq_title in squad_specs:
                SquadMembership.objects.get_or_create(
                    user=user, squad=sq,
                    defaults={
                        'role': _role(sq_role),
                        'job_title': _title(sq_title),
                    }
                )

        stdout.write(f"    -> {username} ({full_name}) configurado.")

    return org


# ═══════════════════════════════════════════════════════════════════════════════
# CORPORATE PROFILE — "Empresa Demo Ltda"
# ═══════════════════════════════════════════════════════════════════════════════

def seed_corporate(stdout):
    stdout.write("  ── Perfil CORPORATIVO (Empresa Demo Ltda) ───────────────────")

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

    # 6 Personas Canônicas
    users_spec = [
        ('gerente.ti', 'gerente.ti@example.com', 'Roberto Gerente TI', 'org_manager', 'manager', 'TI', [
            (proj_crm, 'project_lead', 'project_manager', [(sq_integ, 'squad_lead', 'tech_lead')]),
        ]),
        ('dev.rafa', 'dev.rafa@example.com', 'Rafael Dev Silva', 'org_member', 'analyst', 'TI', [
            (proj_crm, 'project_member', None, [(sq_integ, 'squad_member', 'developer')]),
        ]),
        ('supervisor.bia', 'supervisor.bia@example.com', 'Beatriz Supervisora', 'org_supervisor', 'supervisor', 'ATD', [
            (proj_crm, 'project_lead', 'product_owner', [(sq_bot, 'squad_lead', 'squad_leader')]),
        ]),
        ('atendente.leo', 'atendente.leo@example.com', 'Leonardo Atendente', 'org_agent', 'attendant', 'ATD', []),
        ('analista.rh', 'analista.rh@example.com', 'Fernanda Analista RH', 'org_member', 'analyst', 'RH', []),
        ('diretora.fin', 'diretora.fin@example.com', 'Patrícia Diretora FIN', 'org_admin', 'director', 'FIN', [
            (proj_crm, 'project_member', 'sponsor', []),
        ]),
    ]

    for username, email, full_name, org_role, org_title_slug, dept_code, projects in users_spec:
        user, _ = _create_user(username, email, full_name)

        profile = user.profile
        profile.primary_organization = org
        profile.save()

        OrganizationMembership.objects.get_or_create(
            user=user, organization=org,
            defaults={
                'role': _role(org_role),
                'job_title': _title(org_title_slug),
                'department': depts.get(dept_code),
            }
        )

        for proj, proj_role, proj_title, squad_specs in projects:
            ProjectMembership.objects.get_or_create(
                user=user, project=proj,
                defaults={
                    'role': _role(proj_role),
                    'job_title': _title(proj_title),
                }
            )
            for sq, sq_role, sq_title in squad_specs:
                SquadMembership.objects.get_or_create(
                    user=user, squad=sq,
                    defaults={
                        'role': _role(sq_role),
                        'job_title': _title(sq_title),
                    }
                )

        stdout.write(f"    -> {username} ({full_name}) configurado.")

    return org


# ═══════════════════════════════════════════════════════════════════════════════
# OMNICHANNEL MOCK DATA — Soft FKs via UUIDField
# ═══════════════════════════════════════════════════════════════════════════════

def seed_omnichannel(org_academic, org_corporate, stdout):
    stdout.write("  ── Domínio Omnichannel (Contatos, Conversas e Mensagens) ────")

    contacts_spec = [
        ('5511000000001@example.org', '+55 11 00000-0001', 'Profa. Ana Santos', org_academic),
        ('5511000000002@example.org', '+55 11 00000-0002', 'João Victor Aluno', org_academic),
        ('5511000000003@example.com', '+55 11 00000-0003', 'Roberto Gerente TI', org_corporate),
    ]

    for jid, phone, name, org in contacts_spec:
        pn = ContactPhoneNumber.objects.filter(whatsapp_jid=jid).first()
        if not pn:
            contact = Contact.objects.create(
                full_name=name,
                status=Contact.Status.CLIENT
            )
            ContactPhoneNumber.objects.create(
                contact=contact,
                whatsapp_jid=jid,
                phone_number=phone,
                description=f"Telefone Demo de {name}"
            )
        else:
            contact = pn.contact

        ContactOrganizationMembership.objects.get_or_create(
            contact=contact,
            organization_id=org.id,
            defaults={'notes': f"Contato cadastrado no tenant {org.name}"}
        )

        # Conversa ativa sob a organização
        conv, created = Conversation.objects.get_or_create(
            contact=contact,
            organization_id=org.id,
            defaults={
                'status': Conversation.Status.ACTIVE_AI,
                'access_level': Conversation.AccessLevel.PUBLIC,
                'context_locked': False,
                'consecutive_rag_failures': 0,
            }
        )

        if created:
            now = timezone.now()
            Message.objects.create(
                conversation=conv,
                sender_whatsapp=jid,
                direction=Message.Direction.INBOUND,
                content="Olá! Gostaria de informações sobre o andamento dos projetos.",
                sent_by_ai=False,
                timestamp=now,
            )
            Message.objects.create(
                conversation=conv,
                sender_whatsapp="ai-bot",
                direction=Message.Direction.OUTBOUND,
                content=f"Olá {name}! Sou o assistente virtual da {org.name}. Como posso ajudar?",
                sent_by_ai=True,
                timestamp=now,
            )
        stdout.write(f"    -> Contato e conversa criados para {name} ({jid})")


# ═══════════════════════════════════════════════════════════════════════════════
# FLUSH DEMO & CREDENTIALS TABLE
# ═══════════════════════════════════════════════════════════════════════════════

def flush_demo(stdout):
    """Remove estritamente os dados de demonstração sem tocar em operadores ou org interna."""
    demo_slugs = ['ufdemo', 'empresa-demo']
    demo_orgs = list(Organization.objects.filter(slug__in=demo_slugs))
    demo_org_ids = [org.id for org in demo_orgs]

    if demo_org_ids:
        demo_contacts = Contact.objects.filter(memberships__organization_id__in=demo_org_ids).distinct()
        convs = Conversation.objects.filter(contact__in=demo_contacts) | Conversation.objects.filter(organization_id__in=demo_org_ids)
        Message.objects.filter(conversation__in=convs).delete()
        convs.delete()
        ContactOrganizationMembership.objects.filter(organization_id__in=demo_org_ids).delete()
        demo_contacts.delete()

    deleted_users, _ = User.objects.filter(username__in=DEMO_USERNAMES).delete()
    deleted_orgs, _ = Organization.objects.filter(slug__in=demo_slugs).delete()
    stdout.write(f"  -> {deleted_users} usuários demo e {deleted_orgs} organizações demo removidos.")


def print_credentials_table(stdout):
    """Exibe tabela formatada com credenciais e estrutura RBAC 4-Tier para desenvolvedores."""
    stdout.write("\n" + "=" * 92)
    stdout.write("🔑  TABELA DE CREDENCIAIS DE DEMONSTRAÇÃO (AI-Control v0.0.1)")
    stdout.write("=" * 92)
    stdout.write(f"{'Username':<16} | {'Senha':<10} | {'Organização':<18} | {'Cargo / Papel':<26} | {'Squads'}")
    stdout.write("-" * 92)

    personas_info = [
        ('prof.ana', DEMO_PASSWORD, 'ufdemo', 'professor / org_member', 'app-movel (lead)'),
        ('prof.carlos', DEMO_PASSWORD, 'ufdemo', 'pro_rector / org_manager', '-'),
        ('prof.lucia', DEMO_PASSWORD, 'ufdemo', 'professor / org_member', 'campo-coleta (lead)'),
        ('aluno.joao', DEMO_PASSWORD, 'ufdemo', 'undergrad / org_member', 'app-movel (dev)'),
        ('aluna.maria', DEMO_PASSWORD, 'ufdemo', 'masters / org_member', 'modelagem (dev)'),
        ('pesq.externo', DEMO_PASSWORD, 'ufdemo', 'researcher / org_guest', 'dados-clinicos (dev)'),
        ('tae.paulo', DEMO_PASSWORD, 'ufdemo', 'technician / org_member', '-'),
        ('gerente.ti', DEMO_PASSWORD, 'empresa-demo', 'manager / org_manager', 'integracao (lead)'),
        ('dev.rafa', DEMO_PASSWORD, 'empresa-demo', 'analyst / org_member', 'integracao (dev)'),
        ('supervisor.bia', DEMO_PASSWORD, 'empresa-demo', 'supervisor / supervisor', 'conteudo-bot (lead)'),
        ('atendente.leo', DEMO_PASSWORD, 'empresa-demo', 'attendant / org_agent', '-'),
        ('analista.rh', DEMO_PASSWORD, 'empresa-demo', 'analyst / org_member', '-'),
        ('diretora.fin', DEMO_PASSWORD, 'empresa-demo', 'director / org_admin', '-'),
    ]

    for username, pwd, org, role, squads in personas_info:
        stdout.write(f"{username:<16} | {pwd:<10} | {org:<18} | {role:<26} | {squads}")
    stdout.write("=" * 92 + "\n")


class Command(BaseCommand):
    help = "Semeia dados canônicos de demonstração (Acadêmico, Corporativo e Omnichannel)"

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
        org_acad = None
        org_corp = None

        if profile in ('academic', 'all'):
            org_acad = seed_academic(self.stdout)
        if profile in ('corporate', 'all'):
            org_corp = seed_corporate(self.stdout)

        if org_acad and org_corp:
            seed_omnichannel(org_acad, org_corp, self.stdout)

        print_credentials_table(self.stdout)
        self.stdout.write(self.style.SUCCESS("  ✅ Seed demo canônico concluído com sucesso."))
