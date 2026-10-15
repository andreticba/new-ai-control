# core/api/v1/views/user_views.py | AI-Control v0.0.1 | 15-10-2026 07:45(GMT-04:00)
from collections import defaultdict
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.models import (
    OrganizationMembership, ProjectMembership, SquadMembership, Department, Role, JobTitle
)
from ..serializers import (
    CurrentUserSerializer,
    WorkspaceTreeSerializer,
    QuickOnboardSerializer,
)



class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Obter perfil do usuário autenticado",
        description="Retorna informações de perfil, organização padrão e resumo das memberships 4-tier do usuário atual.",
        responses={200: CurrentUserSerializer}
    )
    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)

        full_name = profile.full_name if profile else None
        primary_org_data = None
        if profile and profile.primary_organization:
            primary_org_data = {
                'id': profile.primary_organization.id,
                'name': profile.primary_organization.name,
                'slug': profile.primary_organization.slug,
            }

        platform_role = profile.platform_role.slug if (profile and profile.platform_role) else None

        # Carregar memberships com select_related contra N+1
        org_mem = OrganizationMembership.objects.filter(
            user=user, is_active=True
        ).select_related('role', 'job_title', 'department').first()

        org_mem_data = None
        if org_mem:
            org_mem_data = {
                'role': org_mem.role.slug if org_mem.role else None,
                'job_title': org_mem.job_title.name if org_mem.job_title else None,
                'department': org_mem.department.code if org_mem.department else None,
            }

        proj_mems = ProjectMembership.objects.filter(
            user=user, is_active=True
        ).select_related('project', 'role', 'job_title')
        projects_data = []
        for pm in proj_mems:
            projects_data.append({
                'project_id': pm.project.id,
                'project_slug': pm.project.slug,
                'project_name': pm.project.name,
                'role': pm.role.slug if pm.role else None,
                'job_title': pm.job_title.name if pm.job_title else None,
            })

        squad_mems = SquadMembership.objects.filter(
            user=user, is_active=True
        ).select_related('squad', 'role', 'job_title')
        squads_data = []
        for sm in squad_mems:
            squads_data.append({
                'squad_id': sm.squad.id,
                'squad_slug': sm.squad.slug,
                'squad_name': sm.squad.name,
                'role': sm.role.slug if sm.role else None,
                'job_title': sm.job_title.name if sm.job_title else None,
            })

        payload = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': full_name,
            'primary_organization': primary_org_data,
            'platform_role': platform_role,
            'memberships': {
                'organization': org_mem_data,
                'projects': projects_data,
                'squads': squads_data,
            }
        }
        return Response(payload)


class ActiveWorkspacesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar workspaces ativos do usuário",
        description="Retorna a árvore hierárquica completa dos 4 níveis (Organização, Departamentos, Projetos e Squads) acessíveis ao usuário.",
        responses={200: WorkspaceTreeSerializer}
    )
    def get(self, request):
        user = request.user

        # 1. Busca organizações ativas do usuário (1 query)
        org_mems = OrganizationMembership.objects.filter(
            user=user, is_active=True
        ).select_related('organization', 'role', 'job_title')

        if not org_mems:
            return Response({'workspaces': []})

        org_ids = [om.organization_id for om in org_mems]

        # 2. Departamentos em lote de todas as organizações acessíveis (1 query)
        depts_by_org = defaultdict(list)
        for dept in Department.objects.filter(organization_id__in=org_ids).values('id', 'name', 'slug', 'code', 'organization_id'):
            org_id = dept.pop('organization_id')
            depts_by_org[org_id].append(dept)

        # 3. Projetos do usuário em lote em todas as organizações (1 query)
        user_proj_mems = ProjectMembership.objects.filter(
            user=user, project__organization_id__in=org_ids, is_active=True
        ).select_related('project', 'role', 'job_title')

        proj_ids = [pm.project_id for pm in user_proj_mems]

        # 4. Squads do usuário em lote para todos os projetos (1 query)
        squads_by_proj = defaultdict(list)
        if proj_ids:
            user_sq_mems = SquadMembership.objects.filter(
                user=user, squad__project_id__in=proj_ids, is_active=True
            ).select_related('squad', 'role', 'job_title')

            for sm in user_sq_mems:
                squads_by_proj[sm.squad.project_id].append({
                    'id': sm.squad.id,
                    'name': sm.squad.name,
                    'slug': sm.squad.slug,
                    'role': sm.role.slug if sm.role else None,
                    'job_title': sm.job_title.name if sm.job_title else None,
                })

        # 5. Agrupamento em memória O(1) de projetos por organização
        projects_by_org = defaultdict(list)
        for pm in user_proj_mems:
            proj = pm.project
            projects_by_org[proj.organization_id].append({
                'id': proj.id,
                'name': proj.name,
                'slug': proj.slug,
                'role': pm.role.slug if pm.role else None,
                'job_title': pm.job_title.name if pm.job_title else None,
                'squads': squads_by_proj[proj.id],
            })

        # 6. Montagem dos workspaces respeitando o contrato exato
        workspaces = []
        for om in org_mems:
            org = om.organization
            workspaces.append({
                'id': org.id,
                'name': org.name,
                'slug': org.slug,
                'org_type': org.org_type,
                'role': om.role.slug if om.role else None,
                'job_title': om.job_title.name if om.job_title else None,
                'departments': depts_by_org[org.id],
                'projects': projects_by_org[org.id],
            })

        return Response({'workspaces': workspaces})


class QuickOnboardView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Admissão rápida de colaborador com Blind Indexing LGPD",
        description="Cria instantaneamente usuário e perfil blind indexed para alocação 4-Tier.",
        request=QuickOnboardSerializer,
        responses={201: QuickOnboardSerializer}
    )
    def post(self, request):
        serializer = QuickOnboardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)


class UserSearchView(APIView):
    """
    Busca facilitada de usuários por nome, username ou e-mail para alocação nos modais.
    Elimina a necessidade de digitação de IDs numéricos.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Buscar usuários para alocação",
        description="Retorna usuários ativos correspondentes ao termo de busca (nome, username, email).",
    )
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        users_qs = User.objects.filter(is_active=True).select_related('profile')

        if query:
            users_qs = users_qs.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )

        results = []
        for u in users_qs[:20]:
            full_name = u.profile.full_name if hasattr(u, 'profile') and u.profile else None
            
            # Se filtrou por query e não bateu nos campos do user, checa no full_name descriptografado
            if query and not (
                query.lower() in u.username.lower() or
                query.lower() in (u.email or '').lower() or
                (full_name and query.lower() in full_name.lower())
            ):
                continue

            results.append({
                'id': u.id,
                'username': u.username,
                'email': u.email or '',
                'full_name': full_name or u.get_full_name() or u.username,
            })
            if len(results) >= 15:
                break

        return Response({'users': results})


class RolesListView(APIView):
    """
    Catálogo de papéis de acesso (Roles) filtráveis por escopo.
    Permite seleção visual por nome legível em vez de UUID.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar papéis de acesso por escopo",
        description="Retorna os papéis disponíveis para o escopo informado (ORGANIZATION, PROJECT, SQUAD).",
    )
    def get(self, request):
        scope = request.query_params.get('scope')
        qs = Role.objects.all().order_by('-level', 'name')
        if scope:
            qs = qs.filter(scope=scope)

        roles = [
            {
                'id': str(r.id),
                'slug': r.slug,
                'name': r.name,
                'scope': r.scope,
                'level': r.level,
                'description': r.description or '',
            }
            for r in qs
        ]
        return Response({'roles': roles})


class JobTitlesListView(APIView):
    """
    Catálogo de cargos (Job Titles) filtráveis por nível.
    Permite seleção visual por nome legível em vez de UUID.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Listar cargos por nível",
        description="Retorna os cargos disponíveis para o nível informado (ORGANIZATION, PROJECT, SQUAD).",
    )
    def get(self, request):
        level = request.query_params.get('level')
        qs = JobTitle.objects.all().order_by('category', 'name')
        if level:
            qs = qs.filter(level=level)

        job_titles = [
            {
                'id': str(jt.id),
                'slug': jt.slug,
                'name': jt.name,
                'level': jt.level,
                'category': jt.category,
            }
            for jt in qs
        ]
        return Response({'job_titles': job_titles})


