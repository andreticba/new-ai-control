# core/api/v1/serializers.py | AI-Control v0.0.1 | 12-10-2026 09:35(GMT-04:00)
from rest_framework import serializers


class PrimaryOrganizationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()


class OrgMembershipDetailSerializer(serializers.Serializer):
    role = serializers.CharField(allow_null=True)
    job_title = serializers.CharField(allow_null=True)
    department = serializers.CharField(allow_null=True)


class ProjectMembershipDetailSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    project_slug = serializers.CharField()
    project_name = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    job_title = serializers.CharField(allow_null=True)


class SquadMembershipDetailSerializer(serializers.Serializer):
    squad_id = serializers.UUIDField()
    squad_slug = serializers.CharField()
    squad_name = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    job_title = serializers.CharField(allow_null=True)


class MembershipsSummarySerializer(serializers.Serializer):
    organization = OrgMembershipDetailSerializer(allow_null=True)
    projects = ProjectMembershipDetailSerializer(many=True)
    squads = SquadMembershipDetailSerializer(many=True)


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    full_name = serializers.CharField(allow_null=True)
    primary_organization = PrimaryOrganizationSerializer(allow_null=True)
    platform_role = serializers.CharField(allow_null=True)
    memberships = MembershipsSummarySerializer()


class DepartmentItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    code = serializers.CharField()


class SquadItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    job_title = serializers.CharField(allow_null=True)


class ProjectItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    job_title = serializers.CharField(allow_null=True)
    squads = SquadItemSerializer(many=True)


class WorkspaceItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    org_type = serializers.CharField()
    role = serializers.CharField(allow_null=True)
    job_title = serializers.CharField(allow_null=True)
    departments = DepartmentItemSerializer(many=True)
    projects = ProjectItemSerializer(many=True)


class WorkspaceTreeSerializer(serializers.Serializer):
    workspaces = WorkspaceItemSerializer(many=True)


# ============================================================================
# Serializers de Mutação de Workspaces (Phase 2 & US1)
# ============================================================================

from django.utils.text import slugify
from core.models import Organization, Department, Project, Squad


class OrganizationCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    slug = serializers.SlugField(max_length=100, required=False, allow_blank=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'org_type', 'is_active']

    def validate(self, attrs):
        name = attrs.get('name')
        slug = attrs.get('slug')
        if not slug and name:
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Organization.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            attrs['slug'] = slug
        elif slug and Organization.objects.filter(slug=slug).exists():
            raise serializers.ValidationError({'slug': 'Organização com este identificador já existe.'})
        return attrs


class DepartmentCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    organization_id = serializers.UUIDField(write_only=True)
    slug = serializers.SlugField(max_length=100, required=False, allow_blank=True)

    class Meta:
        model = Department
        fields = ['id', 'organization_id', 'name', 'code', 'slug', 'description']

    def validate(self, attrs):
        org_id = attrs.get('organization_id')
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError({'organization_id': 'Organização associada não encontrada.'})

        code = attrs.get('code', '').upper()
        attrs['code'] = code

        slug = attrs.get('slug')
        if not slug and code:
            slug = slugify(code)
            attrs['slug'] = slug

        if Department.objects.filter(organization=organization, code=code).exists():
            raise serializers.ValidationError({'code': f"Departamento com código '{code}' já existe nesta organização."})

        attrs['organization'] = organization
        return attrs

    def create(self, validated_data):
        validated_data.pop('organization_id', None)
        return super().create(validated_data)


class ProjectCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    organization_id = serializers.UUIDField(write_only=True)
    slug = serializers.SlugField(max_length=100, required=False, allow_blank=True)

    class Meta:
        model = Project
        fields = ['id', 'organization_id', 'name', 'slug', 'project_type', 'status', 'description']

    def validate(self, attrs):
        org_id = attrs.get('organization_id')
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError({'organization_id': 'Organização associada não encontrada.'})

        name = attrs.get('name')
        slug = attrs.get('slug')
        if not slug and name:
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Project.objects.filter(organization=organization, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            attrs['slug'] = slug

        attrs['organization'] = organization
        return attrs

    def create(self, validated_data):
        validated_data.pop('organization_id', None)
        return super().create(validated_data)


class SquadCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    slug = serializers.SlugField(max_length=100, required=False, allow_blank=True)
    mission = serializers.CharField(source='description', required=False, allow_blank=True)

    class Meta:
        model = Squad
        fields = ['id', 'project_id', 'name', 'slug', 'mission', 'is_active']

    def validate(self, attrs):
        project_id = attrs.get('project_id')
        if not project_id:
            raise serializers.ValidationError({'project_id': 'Projeto pai obrigatório não informado (Violação P3).'})

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError({'project_id': 'Projeto pai informado não existe (Violação P3).'})

        name = attrs.get('name')
        slug = attrs.get('slug')
        if not slug and name:
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Squad.objects.filter(project=project, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            attrs['slug'] = slug

        attrs['project'] = project
        return attrs

    def create(self, validated_data):
        validated_data.pop('project_id', None)
        return super().create(validated_data)


# ============================================================================
# Serializers de Alocação de Membros (Phase 4 & US2)
# ============================================================================

from django.contrib.auth.models import User
from core.models import (
    Role, JobTitle, OrganizationMembership, ProjectMembership, SquadMembership
)


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    organization_id = serializers.UUIDField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    role_id = serializers.CharField(write_only=True)
    job_title_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    department_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = OrganizationMembership
        fields = [
            'id', 'organization_id', 'user_id', 'role_id',
            'job_title_id', 'department_id', 'is_active'
        ]

    def validate(self, attrs):
        org_id = attrs.get('organization_id')
        user_id = attrs.get('user_id')
        role_id = attrs.get('role_id')
        dept_id = attrs.get('department_id')
        job_id = attrs.get('job_title_id')

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise serializers.ValidationError({'organization_id': 'Organização não encontrada.'})

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Usuário não encontrado.'})

        role = None
        try:
            role = Role.objects.get(id=role_id, scope=Role.Scope.ORGANIZATION)
        except (Role.DoesNotExist, ValueError, Exception):
            try:
                role = Role.objects.get(slug=str(role_id), scope=Role.Scope.ORGANIZATION)
            except Role.DoesNotExist:
                raise serializers.ValidationError({'role_id': 'Papel organizacional inválido.'})

        department = None
        if dept_id:
            try:
                department = Department.objects.get(id=dept_id, organization=organization)
            except (Department.DoesNotExist, ValueError, Exception):
                try:
                    department = Department.objects.get(code__iexact=str(dept_id), organization=organization)
                except Department.DoesNotExist:
                    try:
                        department = Department.objects.get(slug=str(dept_id), organization=organization)
                    except Department.DoesNotExist:
                        raise serializers.ValidationError({'department_id': 'Departamento não pertence a esta organização.'})

        job_title = None
        if job_id:
            try:
                job_title = JobTitle.objects.get(id=job_id, level=JobTitle.Level.ORGANIZATION)
            except (JobTitle.DoesNotExist, ValueError, Exception):
                try:
                    job_title = JobTitle.objects.get(slug=str(job_id), level=JobTitle.Level.ORGANIZATION)
                except JobTitle.DoesNotExist:
                    raise serializers.ValidationError({'job_title_id': 'Cargo organizacional inválido.'})

        attrs['organization'] = organization
        attrs['user'] = user
        attrs['role'] = role
        attrs['department'] = department
        attrs['job_title'] = job_title
        return attrs

    def create(self, validated_data):
        validated_data.pop('organization_id', None)
        validated_data.pop('user_id', None)
        validated_data.pop('role_id', None)
        validated_data.pop('job_title_id', None)
        validated_data.pop('department_id', None)

        user = validated_data.get('user')
        organization = validated_data.get('organization')
        existing = OrganizationMembership.objects.filter(user=user, organization=organization).first()
        if existing:
            for key, val in validated_data.items():
                setattr(existing, key, val)
            existing.save()
            return existing

        return super().create(validated_data)


class ProjectMembershipSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    role_id = serializers.CharField(write_only=True)
    job_title_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ProjectMembership
        fields = [
            'id', 'project_id', 'user_id', 'role_id',
            'job_title_id', 'is_external', 'is_active'
        ]

    def validate(self, attrs):
        project_id = attrs.get('project_id')
        user_id = attrs.get('user_id')
        role_id = attrs.get('role_id')
        job_id = attrs.get('job_title_id')
        is_external = attrs.get('is_external', False)

        try:
            project = Project.objects.select_related('organization').get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError({'project_id': 'Projeto não encontrado.'})

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Usuário não encontrado.'})

        role = None
        try:
            role = Role.objects.get(id=role_id, scope=Role.Scope.PROJECT)
        except (Role.DoesNotExist, ValueError, Exception):
            try:
                role = Role.objects.get(slug=str(role_id), scope=Role.Scope.PROJECT)
            except Role.DoesNotExist:
                raise serializers.ValidationError({'role_id': 'Papel de projeto inválido.'})

        # Validação de Contenção P3: Usuário deve ser membro ativo da Organização dona do projeto
        org_membership = OrganizationMembership.objects.filter(
            user=user, organization=project.organization, is_active=True
        ).first()

        if not org_membership:
            raise serializers.ValidationError({
                'user_id': 'Usuário precisa possuir vínculo ativo na organização dona do projeto (Inviolabilidade P3).'
            })

        job_title = None
        if job_id:
            try:
                job_title = JobTitle.objects.get(id=job_id, level=JobTitle.Level.PROJECT)
            except (JobTitle.DoesNotExist, ValueError, Exception):
                try:
                    job_title = JobTitle.objects.get(slug=str(job_id), level=JobTitle.Level.PROJECT)
                except JobTitle.DoesNotExist:
                    raise serializers.ValidationError({'job_title_id': 'Cargo de nível de projeto inválido.'})

        attrs['project'] = project
        attrs['user'] = user
        attrs['role'] = role
        attrs['job_title'] = job_title
        return attrs

    def create(self, validated_data):
        validated_data.pop('project_id', None)
        validated_data.pop('user_id', None)
        validated_data.pop('role_id', None)
        validated_data.pop('job_title_id', None)

        user = validated_data.get('user')
        project = validated_data.get('project')
        existing = ProjectMembership.objects.filter(user=user, project=project).first()
        if existing:
            for key, val in validated_data.items():
                setattr(existing, key, val)
            existing.save()
            return existing

        return super().create(validated_data)


class SquadMembershipSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    squad_id = serializers.UUIDField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    role_id = serializers.CharField(write_only=True)
    job_title_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = SquadMembership
        fields = [
            'id', 'squad_id', 'user_id', 'role_id',
            'job_title_id', 'is_active'
        ]

    def validate(self, attrs):
        squad_id = attrs.get('squad_id')
        user_id = attrs.get('user_id')
        role_id = attrs.get('role_id')
        job_id = attrs.get('job_title_id')

        try:
            squad = Squad.objects.select_related('project').get(id=squad_id)
        except Squad.DoesNotExist:
            raise serializers.ValidationError({'squad_id': 'Squad não encontrada.'})

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({'user_id': 'Usuário não encontrado.'})

        role = None
        try:
            role = Role.objects.get(id=role_id, scope=Role.Scope.SQUAD)
        except (Role.DoesNotExist, ValueError, Exception):
            try:
                role = Role.objects.get(slug=str(role_id), scope=Role.Scope.SQUAD)
            except Role.DoesNotExist:
                raise serializers.ValidationError({'role_id': 'Papel de squad inválido.'})

        # Validação Contínua P3: Usuário DEVE possuir vínculo ATIVO no projeto pai da squad
        has_active_project_membership = ProjectMembership.objects.filter(
            user=user, project=squad.project, is_active=True
        ).exists()

        if not has_active_project_membership:
            raise serializers.ValidationError({
                'user_id': 'O usuário precisa ter vínculo ativo no projeto pai desta squad (Validação Contínua P3).'
            })

        job_title = None
        if job_id:
            try:
                job_title = JobTitle.objects.get(id=job_id, level=JobTitle.Level.SQUAD)
            except (JobTitle.DoesNotExist, ValueError, Exception):
                try:
                    job_title = JobTitle.objects.get(slug=str(job_id), level=JobTitle.Level.SQUAD)
                except JobTitle.DoesNotExist:
                    raise serializers.ValidationError({'job_title_id': 'Cargo de nível squad inválido.'})

        attrs['squad'] = squad
        attrs['user'] = user
        attrs['role'] = role
        attrs['job_title'] = job_title
        return attrs

    def create(self, validated_data):
        validated_data.pop('squad_id', None)
        validated_data.pop('user_id', None)
        validated_data.pop('role_id', None)
        validated_data.pop('job_title_id', None)

        user = validated_data.get('user')
        squad = validated_data.get('squad')
        existing = SquadMembership.objects.filter(user=user, squad=squad).first()
        if existing:
            for key, val in validated_data.items():
                setattr(existing, key, val)
            existing.save()
            return existing

        return super().create(validated_data)


# ============================================================================
# Serializer de Onboarding Rápido com Blind Indexing LGPD (Phase 5 & US3)
# ============================================================================

from core.models import UserProfile


class QuickOnboardSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(max_length=254)
    full_name = serializers.CharField(max_length=255)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Nome de usuário já existe.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Endereço de e-mail já existe.")
        return value

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        full_name = validated_data['full_name']

        user = User.objects.create_user(
            username=username,
            email=email
        )
        user.set_unusable_password()
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.full_name = full_name
        profile.save()

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': full_name,
        }



