# models.py | Atualizado em: 06-10-2026 21:40:00(GMT-04:00)
# backend/core/models.py em 2025-12-14 11:48

import uuid
from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from pgvector.django import HnswIndex, VectorField

# Importa os campos de criptografia
from django_crypto_fields.fields import EncryptedCharField, EncryptedTextField

# Importa o utilitário de Blind Indexing
from .utils import generate_search_tokens

# --- 1. RBAC Escopado e Governança Hierárquica (Organização → Projeto → Squad) ---
#
# Princípios (ver README.md, seção "Controle de Acesso"):
#   P1. Role ≠ Cargo: `Role` concede permissões; `JobTitle` é apenas rótulo exibido.
#   P2. O papel mora na *membership* (RBAC matricial): o mesmo usuário pode ser
#       Coordenador num projeto e Observador em outro.
#   P3. Escopo aninhado e estrito: Squad ⊂ Projeto ⊂ Organização.
#   P4. Herança só de cima para baixo e controlada por `Role.inheritance`.

class Permission(models.Model):
    """
    Permissões granulares do sistema, no formato `<domínio>.<ação>`.
    Ex: 'org.manage_members', 'project.manage_squads', 'document.read'.
    """
    slug = models.SlugField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return self.slug


class Role(models.Model):
    """
    Papel de sistema que agrupa permissões e vale **dentro de um escopo**.
    Ex: 'org_admin' (ORGANIZATION), 'project_lead' (PROJECT), 'squad_member' (SQUAD).
    """
    class Scope(models.TextChoices):
        PLATFORM = 'PLATFORM', _('Plataforma')
        ORGANIZATION = 'ORGANIZATION', _('Organização')
        PROJECT = 'PROJECT', _('Projeto')
        SQUAD = 'SQUAD', _('Squad')

    class Inheritance(models.TextChoices):
        NONE = 'NONE', _('Sem herança')
        ALL = 'ALL', _('Herda para todos os níveis abaixo')
        DEPARTMENT = 'DEPARTMENT', _('Herda apenas para projetos do próprio departamento')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100, unique=True, help_text=_("Identificador estável usado no código (ex: 'org_admin')."))
    name = models.CharField(max_length=100, help_text=_("Rótulo exibido na interface."))
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.ORGANIZATION, db_index=True)
    level = models.PositiveSmallIntegerField(default=0, help_text=_("Peso para comparação entre papéis do mesmo escopo (maior = mais poder)."))
    inheritance = models.CharField(
        max_length=20, choices=Inheritance.choices, default=Inheritance.NONE,
        help_text=_("Se as permissões de gestão deste papel descem para os níveis inferiores.")
    )
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    is_system_role = models.BooleanField(
        default=False, 
        help_text=_("Papéis de sistema não podem ser deletados (ex: Admin, Participante).")
    )

    class Meta:
        ordering = ['scope', '-level', 'slug']

    def __str__(self):
        return f"{self.name} [{self.get_scope_display()}]"


class Organization(models.Model):
    """
    Representa o tenant B2B (Instituição Acadêmica, Empresa, Clínica, Profissional Solo).
    Para profissionais liberais, é uma 'Organização de um homem só'.
    """
    class OrgType(models.TextChoices):
        PLATFORM = 'PLATFORM', _('Plataforma AI-Control')
        ACADEMIC = 'ACADEMIC', _('Instituição Acadêmica')
        COMPANY = 'COMPANY', _('Empresa')
        CLINIC = 'CLINIC', _('Clínica/Hospital')
        SOLO_PRACTITIONER = 'SOLO', _('Profissional Liberal')
        PARTNER = 'PARTNER', _('Parceiro de Marketplace')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=OrgType.choices, default=OrgType.SOLO_PRACTITIONER)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, help_text=_("Identificador único para URLs e APIs."))
    is_active = models.BooleanField(default=True)
    is_internal = models.BooleanField(
        default=False,
        help_text=_("Organização da própria plataforma. Apenas seus membros podem receber papéis de PLATAFORMA.")
    )
    
    # White-Labeling e Configuração
    theme_config = models.JSONField(
        default=dict, 
        blank=True,
        help_text=_("Configurações visuais: cores, logo, terminologia.")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['is_internal'], 
                condition=Q(is_internal=True), 
                name='unique_internal_organization'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()})"


class Department(models.Model):
    """
    Unidade **fixa** do organograma (ex: 'Financeiro', 'RH', 'Depto. de Computação').
    Antigo `Team`. Para grupos de execução multidisciplinares, use `Squad`.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='departments')
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
        help_text=_("Departamento superior (opcional), para subdepartamentos.")
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True, help_text=_("Sigla, ex: 'PROPESQ', 'FIN'."))
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['organization', 'name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'slug'], name='uniq_department_slug_per_org'),
        ]

    def clean(self):
        if self.parent_id:
            if self.parent_id == self.pk:
                raise ValidationError({'parent': _("Um departamento não pode ser pai de si mesmo.")})
            if self.parent.organization_id != self.organization_id:
                raise ValidationError({'parent': _("O departamento pai precisa ser da mesma organização.")})

    def __str__(self):
        return f"{self.name} - {self.organization.name}"


class JobTitle(models.Model):
    """
    Cargo/Função exibido na interface. **Não concede permissão nenhuma** (P1).
    Ex: 'Professor(a)' (ORGANIZATION), 'Bolsista' (PROJECT), 'Tech Lead' (SQUAD).
    `organization` nulo = catálogo global; preenchido = cargo próprio do tenant.
    """
    class Level(models.TextChoices):
        ORGANIZATION = 'ORGANIZATION', _('Organização')
        PROJECT = 'PROJECT', _('Projeto')
        SQUAD = 'SQUAD', _('Squad')

    class Category(models.TextChoices):
        CORPORATE = 'CORPORATE', _('Corporativo')
        ACADEMIC = 'ACADEMIC', _('Acadêmico')
        TECH = 'TECH', _('Tecnologia')
        GENERIC = 'GENERIC', _('Genérico')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=100)
    name = models.CharField(max_length=150)
    level = models.CharField(max_length=20, choices=Level.choices, db_index=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERIC)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True, related_name='job_titles'
    )
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ['level', 'category', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['slug'], condition=Q(organization__isnull=True), name='uniq_global_jobtitle_slug'
            ),
            models.UniqueConstraint(fields=['organization', 'slug'], name='uniq_org_jobtitle_slug'),
        ]

    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Iniciativa com ciclo de vida dentro de uma Organização (pesquisa, extensão,
    projeto corporativo...). Agrupa Squads e possui membros próprios.
    """
    class ProjectType(models.TextChoices):
        RESEARCH = 'RESEARCH', _('Pesquisa')
        EXTENSION = 'EXTENSION', _('Extensão')
        TEACHING = 'TEACHING', _('Ensino')
        INNOVATION = 'INNOVATION', _('Inovação')
        CORPORATE = 'CORPORATE', _('Corporativo')
        INTERNAL = 'INTERNAL', _('Interno')
        OPERATIONS = 'OPERATIONS', _('Operações (contínuo)')

    class Status(models.TextChoices):
        PLANNING = 'PLANNING', _('Planejamento')
        ACTIVE = 'ACTIVE', _('Ativo')
        PAUSED = 'PAUSED', _('Pausado')
        COMPLETED = 'COMPLETED', _('Concluído')
        ARCHIVED = 'ARCHIVED', _('Arquivado')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices, default=ProjectType.INTERNAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING, db_index=True)
    owner_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_projects',
        help_text=_("Departamento responsável (usado na herança do papel 'Gestor').")
    )
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    metadata = models.JSONField(
        default=dict, blank=True,
        help_text=_("Dados livres: edital, processo SEI, agência de fomento, centro de custo...")
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['organization', 'name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'slug'], name='uniq_project_slug_per_org'),
            models.CheckConstraint(
                condition=Q(start_date__isnull=True) | Q(end_date__isnull=True) | Q(end_date__gte=F('start_date')),
                name='project_end_after_start',
            ),
        ]

    def clean(self):
        if self.owner_department_id and self.owner_department.organization_id != self.organization_id:
            raise ValidationError({'owner_department': _("O departamento responsável precisa ser da mesma organização.")})

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Squad(models.Model):
    """
    Time de execução multidisciplinar. Sempre pertence a um Projeto (P3).
    Para um time contínuo, crie um Projeto do tipo OPERATIONS para abrigá-lo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='squads')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['project', 'name']
        constraints = [
            models.UniqueConstraint(fields=['project', 'slug'], name='uniq_squad_slug_per_project'),
        ]

    @property
    def organization_id(self):
        return self.project.organization_id

    def __str__(self):
        return f"{self.name} ({self.project.name})"


class BaseMembership(models.Model):
    """
    Base abstrata das memberships. Cada subclasse define `SCOPE`, `user` e `role`.

    Regras garantidas em `clean()` (chamado também no `save()`):
      - o papel (`role.scope`) e o cargo (`job_title.level`) precisam ser do escopo da membership;
      - para estar ativa, a membership exige membership ativa no nível acima (P3).
    """
    SCOPE = None

    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    is_active = models.BooleanField(default=True, db_index=True)
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def get_organization_id(self):
        raise NotImplementedError

    def validate_parent(self):
        """Retorna um dict de erros sobre a membership do nível acima."""
        return {}

    def clean(self):
        errors = {}
        if self.role_id and self.role.scope != self.SCOPE:
            errors['role'] = _("Este papel pertence ao escopo '%(scope)s'.") % {'scope': self.role.scope}
        if self.job_title_id:
            if self.job_title.level != self.SCOPE:
                errors['job_title'] = _("Este cargo é do nível '%(level)s'.") % {'level': self.job_title.level}
            elif self.job_title.organization_id and self.job_title.organization_id != self.get_organization_id():
                errors['job_title'] = _("Este cargo pertence a outra organização.")
        if self.is_active:
            errors.update(self.validate_parent())
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        if self.is_active:
            self.left_at = None
        elif self.left_at is None:
            self.left_at = timezone.now()
        super().save(*args, **kwargs)


class OrganizationMembership(BaseMembership):
    """Vínculo usuário ↔ organização, com papel, cargo e lotação (departamento)."""
    SCOPE = Role.Scope.ORGANIZATION

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='org_memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name='org_memberships',
        limit_choices_to={'scope': Role.Scope.ORGANIZATION}
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='memberships')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'organization'], name='uniq_org_membership'),
        ]

    def get_organization_id(self):
        return self.organization_id

    def validate_parent(self):
        if self.department_id and self.department.organization_id != self.organization_id:
            return {'department': _("O departamento precisa ser da mesma organização.")}
        return {}

    def __str__(self):
        return f"{self.user} @ {self.organization.name} ({self.role.slug})"


class ProjectMembership(BaseMembership):
    """Vínculo usuário ↔ projeto. Exige membership ativa na organização do projeto."""
    SCOPE = Role.Scope.PROJECT

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name='project_memberships',
        limit_choices_to={'scope': Role.Scope.PROJECT}
    )
    is_external = models.BooleanField(
        default=False,
        help_text=_("Colaborador de outra instituição/empresa. Exige papel 'org_guest' na organização do projeto.")
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'project'], name='uniq_project_membership'),
        ]

    def get_organization_id(self):
        return self.project.organization_id

    def validate_parent(self):
        org_membership = (
            OrganizationMembership.objects
            .filter(user_id=self.user_id, organization_id=self.project.organization_id, is_active=True)
            .select_related('role')
            .first()
        )
        if org_membership is None:
            return {'user': _("O usuário precisa ser membro ativo da organização do projeto.")}
        if self.is_external and org_membership.role.slug != 'org_guest':
            return {'is_external': _("Colaboradores externos precisam ter o papel 'org_guest' na organização.")}
        return {}

    def __str__(self):
        return f"{self.user} @ {self.project.name} ({self.role.slug})"


class SquadMembership(BaseMembership):
    """Vínculo usuário ↔ squad. Exige membership ativa no projeto do squad."""
    SCOPE = Role.Scope.SQUAD

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='squad_memberships')
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name='squad_memberships',
        limit_choices_to={'scope': Role.Scope.SQUAD}
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'squad'], name='uniq_squad_membership'),
        ]

    def get_organization_id(self):
        return self.squad.project.organization_id

    def validate_parent(self):
        has_project = ProjectMembership.objects.filter(
            user_id=self.user_id, project_id=self.squad.project_id, is_active=True
        ).exists()
        if not has_project:
            return {'user': _("O usuário precisa ser membro ativo do projeto deste squad.")}
        return {}

    def __str__(self):
        return f"{self.user} @ {self.squad.name} ({self.role.slug})"


# --- 2. Identidade e Perfis (Unificado) ---

class UserProfile(models.Model):
    """
    Perfil base estendendo o User do Django.
    Contém os dados PII criptografados e o mecanismo de busca segura.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Dados Pessoais Sensíveis (PII) - Criptografados
    # EncryptedTextField usado para evitar limite de tamanho RSA em nomes longos
    full_name = EncryptedTextField(null=True, blank=True)
    
    # Blind Indexing: Tokens de busca (Hashes) para permitir buscar por nome sem descriptografar
    search_tokens = ArrayField(
        models.CharField(max_length=32),
        blank=True,
        default=list,
        help_text=_("Hashes das partes do nome para busca segura (Blind Index).")
    )
    
    # Estes são pequenos o suficiente para manter CharField (limite ~214 chars no RSA)
    phone_number = EncryptedCharField(max_length=20, null=True, blank=True)
    cpf = EncryptedCharField(max_length=14, null=True, blank=True, unique=True)
    
    # Contexto Organizacional (organização padrão exibida na UI; NÃO concede acesso)
    primary_organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='members',
        help_text=_("A organização principal do usuário (nula para Participantes independentes).")
    )
    
    # RBAC: o acesso a organizações, projetos e squads vem das *Memberships*.
    # Aqui fica apenas o papel global de PLATAFORMA (superadmin, suporte, bot).
    platform_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='platform_profiles',
        limit_choices_to={'scope': Role.Scope.PLATFORM},
        help_text=_("Papel global de plataforma. Só para membros da organização interna.")
    )

    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Intercepta o salvamento para atualizar os tokens de busca
        sempre que o nome mudar.
        """
        if self.full_name:
            # Gera os tokens a partir do texto plano antes dele ser criptografado pelo field
            # Nota: O django-crypto-fields criptografa no get_prep_value, então aqui 
            # self.full_name ainda é legível se foi setado recentemente.
            # Se for update sem mudar o nome, pode ser necessário lógica extra,
            # mas para MVP isso cobre criação e edição explícita.
            try:
                self.search_tokens = generate_search_tokens(self.full_name)
            except Exception:
                # Fallback se full_name já estiver criptografado ou inválido
                pass
        else:
            self.search_tokens = []
            
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            # Índice GIN para busca ultra-rápida no Array de tokens
            GinIndex(fields=['search_tokens'], name='user_name_blind_idx'),
        ]

    @property
    def has_completed_onboarding(self):
        """
        Para o MVP, consideramos sempre True ou False fixo,
        ou checamos em outro local, pois o app 'medical' não existe.
        """
        return False

    def __str__(self):
        return self.user.username


class ParticipantProfile(models.Model):
    """
    Dados específicos do Participante (o Paciente/Usuário Final).
    Focado em engajamento, autonomia e gamificação.
    """
    class AutonomyLevel(models.IntegerChoices):
        LEVEL_1_DEPENDENT = 1, _('Nível 1: Dependente (Início)')
        LEVEL_2_COLLABORATIVE = 2, _('Nível 2: Colaborativo (Intermediário)')
        LEVEL_3_AUTONOMOUS = 3, _('Nível 3: Autônomo (Mestre)')

    class PersonalityType(models.TextChoices):
        ACHIEVER = 'ACHIEVER', _('Realizador')
        SOCIALIZER = 'SOCIALIZER', _('Socializador')
        CAUTIOUS = 'CAUTIOUS', _('Cauteloso/Seguro')
        EXPLORER = 'EXPLORER', _('Explorador')
        UNKNOWN = 'UNKNOWN', _('Não Identificado')

    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='participant_data')
    
    # Gamificação & Comportamento
    autonomy_level = models.IntegerField(choices=AutonomyLevel.choices, default=AutonomyLevel.LEVEL_1_DEPENDENT)
    personality_type = models.CharField(max_length=20, choices=PersonalityType.choices, default=PersonalityType.UNKNOWN)
    
    gamification_wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_streak_days = models.PositiveIntegerField(default=0)
    
    # Saúde Básica (Snapshot)
    birth_date = models.DateField(null=True, blank=True)
    
    # Dispositivos e Status Independente
    is_polar_configured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Participante: {self.profile.user.username} (Nível {self.autonomy_level})"


class ProfessionalProfile(models.Model):
    """
    Dados específicos para Profissionais de Saúde e Bem-Estar.
    """
    class ProfessionalLevel(models.TextChoices):
        TRAINEE = 'TRAINEE', _('Em Treinamento')
        SPECIALIST = 'SPECIALIST', _('Especialista Certificado')
        AUTHORITY = 'AUTHORITY', _('Autoridade/Líder')

    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='professional_data')
    
    professional_level = models.CharField(max_length=20, choices=ProfessionalLevel.choices, default=ProfessionalLevel.TRAINEE)
    reputation_score = models.FloatField(default=0.0, help_text="Score de 0 a 5 baseado em feedback e auditoria.")
    specialties = models.JSONField(default=list, blank=True, help_text="Lista de especialidades (ex: ['Cardiologia', 'Nutrição Esportiva']).")
    
    # Auditoria e Capacitação
    is_verified = models.BooleanField(default=False)
    ai_control_academy_progress = models.JSONField(default=dict, blank=True, help_text="Progresso nos cursos obrigatórios.")

    def __str__(self):
        return f"Profissional: {self.profile.user.username} ({self.get_professional_level_display()})"


class OnboardingProcess(models.Model):
    """
    Tabela desacoplada para controle de fluxo e estado do onboarding.
    Permite que o usuário retome de onde parou sem sujar o perfil base.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding_process')
    
    current_step = models.CharField(max_length=50, default='basics')
    org_slug = models.SlugField(max_length=50, default='platform')
    
    # Snapshot dos dados coletados mas ainda não validados/commitados no perfil
    data_snapshot = models.JSONField(default=dict, blank=True)
    
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Onboarding: {self.user.username} - Passo {self.current_step}"


# --- 3. Governança, Auditoria e Data Vault ---

class ConsentLog(models.Model):
    """
    Registro imutável de consentimento do usuário (LGPD/GDPR).
    """
    class ConsentType(models.TextChoices):
        TERMS_OF_SERVICE = 'TERMS', _('Termos de Serviço')
        DATA_SHARING = 'SHARING', _('Compartilhamento de Dados')
        MARKETING = 'MARKETING', _('Comunicações de Marketing')
        RESEARCH = 'RESEARCH', _('Uso para Pesquisa (Knowledge Hub)')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=20, choices=ConsentType.choices)
    granted = models.BooleanField(default=False)
    
    # Metadados de Auditoria
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    version = models.CharField(max_length=50, help_text="Versão do documento aceito.")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "CONCEDIDO" if self.granted else "REVOGADO"
        return f"{self.user.username} - {self.consent_type} - {status}"


class DataAccessGrant(models.Model):
    """
    O Coração do Data Vault.
    Define quem (Grantee) pode acessar o quê (Resource) de quem (Owner).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Atores
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_accesses', help_text="O dono do dado (Participante).")
    grantor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='grants_issued', help_text="Quem realizou a ação (geralmente o owner).")
    
    # Quem recebe o acesso (pode ser um usuário ou escopo organizacional)
    grantee_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_accesses')
    grantee_department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='received_accesses')
    grantee_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='received_accesses')
    grantee_squad = models.ForeignKey(Squad, on_delete=models.CASCADE, null=True, blank=True, related_name='received_accesses')
    
    # O Recurso (Polimórfico - Pode ser um WellnessPlan, um Exame, ou Tudo)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    target_object_id = models.CharField(max_length=255, null=True, blank=True)
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    # Definição do Acesso
    permissions = models.JSONField(default=list, help_text="Lista de permissões concedidas (ex: ['read', 'approve']).")
    consent_log = models.ForeignKey(ConsentLog, on_delete=models.PROTECT, related_name='active_grants')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Acesso temporário (opcional).")
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['owner', 'grantee_user']),
            models.Index(fields=['owner', 'grantee_department']),
            models.Index(fields=['owner', 'grantee_project']),
        ]

    def is_active(self):
        now = timezone.now()
        not_revoked = self.revoked_at is None
        not_expired = self.expires_at is None or self.expires_at > now
        return not_revoked and not_expired

    def __str__(self):
        target = self.target_object or "TODOS"
        grantee = self.grantee_user or self.grantee_department or self.grantee_project or self.grantee_squad
        return f"Grant: {self.owner} -> {grantee} em {target}"


class AuditLog(models.Model):
    """
    Log de Auditoria de Segurança e Compliance.
    Registra acessos, modificações e decisões da IA.
    """
    class ActionType(models.TextChoices):
        ACCESS = 'ACCESS', _('Acesso a Dados')
        CREATE = 'CREATE', _('Criação')
        UPDATE = 'UPDATE', _('Atualização')
        DELETE = 'DELETE', _('Exclusão/Arquivamento')
        AI_DECISION = 'AI_DECISION', _('Decisão/Sugestão da IA')
        HUMAN_REVIEW = 'HUMAN_REVIEW', _('Revisão Humana (HITL)')
        LOGIN = 'LOGIN', _('Login')
        FAILED_LOGIN = 'FAILED_LOGIN', _('Falha de Login')
        HANDOFF_ASSUMED = 'HANDOFF_ASSUMED', _('Handoff Assumido')
        PII_ACCESS_ATTEMPT = 'PII_ACCESS_ATTEMPT', _('Acesso a PII')
        FORCE_ARCHIVE = 'FORCE_ARCHIVE', _('Forçar Arquivamento')
        
        # Ciclo de vida WhatsApp Gateway
        WHATSAPP_INSTANCE_CREATE = 'whatsapp_instance_create', _('WhatsApp: Instância Criada')
        WHATSAPP_CONNECTED       = 'whatsapp_connected',       _('WhatsApp: Conectado')
        WHATSAPP_DISCONNECTED    = 'whatsapp_disconnected',     _('WhatsApp: Desconectado')
        WHATSAPP_INSTANCE_DELETE = 'whatsapp_instance_delete',  _('WhatsApp: Instância Deletada')

    id = models.BigAutoField(primary_key=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ActionType.choices)
    
    # Recurso Afetado
    target_contact_id = models.UUIDField(null=True, blank=True)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    target_object_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Detalhes e IA
    details = models.JSONField(default=dict, blank=True)
    ai_reasoning_snapshot = models.JSONField(
        null=True, 
        blank=True, 
        help_text=_("Snapshot do raciocínio da IA (Chain of Thought) para explicabilidade.")
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            GinIndex(fields=['details'], name='auditlog_details_gin'),
            GinIndex(fields=['ai_reasoning_snapshot'], name='auditlog_ai_reasoning_gin'),
        ]


    def __str__(self):
        return f"Audit: {self.action} by {self.actor} at {self.timestamp}"


class Document(models.Model):
    """
    Documento ingerido para a base de conhecimento (RAG).
    A `visibility` define em que nível do RBAC este documento é acessível.
    """
    class DocumentStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        PROCESSING = "PROCESSING", "Processando"
        EMBEDDING = "EMBEDDING", "Vetorizando"
        COMPLETED = "COMPLETED", "Concluído"
        FAILED = "FAILED", "Falhou"

    class Visibility(models.TextChoices):
        ORGANIZATION = 'ORGANIZATION', _('Organização (toda a org pode ler)')
        DEPARTMENT = 'DEPARTMENT', _('Departamento')
        PROJECT = 'PROJECT', _('Projeto')
        SQUAD = 'SQUAD', _('Squad')
        PRIVATE = 'PRIVATE', _('Privado (só o autor)')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="documents")
    uploaded_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    file = models.FileField(upload_to="documents/", null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_size_bytes = models.PositiveIntegerField(default=0)
    file_hash = models.CharField(max_length=64, db_index=True)
    
    # Escopo de visibilidade (para o filtro do RAG)
    visibility = models.CharField(
        max_length=20, choices=Visibility.choices, default=Visibility.ORGANIZATION,
        db_index=True
    )
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    squad = models.ForeignKey(Squad, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    ai_accessible = models.BooleanField(
        default=True,
        help_text=_("Se False, o bot/IA nunca enxerga este documento no RAG.")
    )
    
    status = models.CharField(max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self): return self.file_name


class DocumentChunk(models.Model):
    """
    Fragmento vetorizado de um Document. Campos de escopo denormalizados para
    permitir pré-filtragem SQL **antes** da busca vetorial (P5).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    content = models.TextField()
    # Embedding de 768 dimensões (Nomic Embed / all-MiniLM). Com HNSW para busca eficiente.
    embedding = VectorField(dimensions=768) 
    page_number = models.PositiveIntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    # Campos denormalizados para filtro SQL rápido do RAG (copiados do Document pai)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='chunks', null=True)
    visibility = models.CharField(max_length=20, choices=Document.Visibility.choices, default=Document.Visibility.ORGANIZATION)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_chunks')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='chunks')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='chunks')
    squad = models.ForeignKey(Squad, on_delete=models.SET_NULL, null=True, blank=True, related_name='chunks')

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'visibility']),
            HnswIndex(
                name='chunk_embedding_hnsw_idx',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_cosine_ops'],
            ),
        ]

    def __str__(self): return f"Chunk de {self.document.file_name}"

# --- 5. CRM Multi-Tenant e Evolution API ---


