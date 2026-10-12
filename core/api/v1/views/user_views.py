# core/api/v1/views/user_views.py | AI-Control v0.0.1 | 12-10-2026 09:35(GMT-04:00)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from core.models import (
    OrganizationMembership, ProjectMembership, SquadMembership, Department
)
from ..serializers import CurrentUserSerializer, WorkspaceTreeSerializer


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

        # Busca organizações onde o usuário possui membership
        org_mems = OrganizationMembership.objects.filter(
            user=user, is_active=True
        ).select_related('organization', 'role', 'job_title')

        workspaces = []
        for om in org_mems:
            org = om.organization

            # Departamentos da organização
            depts = Department.objects.filter(organization=org).values('id', 'name', 'slug', 'code')

            # Projetos da organização onde o usuário tem ProjectMembership
            user_proj_mems = ProjectMembership.objects.filter(
                user=user, project__organization=org, is_active=True
            ).select_related('project', 'role', 'job_title')

            projects_list = []
            for pm in user_proj_mems:
                proj = pm.project

                # Squads do projeto onde o usuário tem SquadMembership
                user_sq_mems = SquadMembership.objects.filter(
                    user=user, squad__project=proj, is_active=True
                ).select_related('squad', 'role', 'job_title')

                squads_list = []
                for sm in user_sq_mems:
                    squads_list.append({
                        'id': sm.squad.id,
                        'name': sm.squad.name,
                        'slug': sm.squad.slug,
                        'role': sm.role.slug if sm.role else None,
                        'job_title': sm.job_title.name if sm.job_title else None,
                    })

                projects_list.append({
                    'id': proj.id,
                    'name': proj.name,
                    'slug': proj.slug,
                    'role': pm.role.slug if pm.role else None,
                    'job_title': pm.job_title.name if pm.job_title else None,
                    'squads': squads_list,
                })

            workspaces.append({
                'id': org.id,
                'name': org.name,
                'slug': org.slug,
                'org_type': org.org_type,
                'role': om.role.slug if om.role else None,
                'job_title': om.job_title.name if om.job_title else None,
                'departments': list(depts),
                'projects': projects_list,
            })

        return Response({'workspaces': workspaces})
