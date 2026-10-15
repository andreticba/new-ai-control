# core/api/v1/views/membership_views.py | AI-Control v0.0.1 | 14-10-2026 07:33(GMT-04:00)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import OrganizationMembership, ProjectMembership, SquadMembership
from ..permissions import HasWorkspaceManagePermission
from ..serializers import (
    OrganizationMembershipSerializer,
    ProjectMembershipSerializer,
    SquadMembershipSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="Listar vínculos organizacionais"),
    create=extend_schema(summary="Alocar membro na organização"),
    retrieve=extend_schema(summary="Detalhar vínculo organizacional"),
    update=extend_schema(summary="Atualizar vínculo organizacional"),
    destroy=extend_schema(summary="Remover vínculo organizacional"),
)
class OrganizationMembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    queryset = OrganizationMembership.objects.all().select_related(
        'organization', 'user', 'role', 'department', 'job_title'
    )
    serializer_class = OrganizationMembershipSerializer


@extend_schema_view(
    list=extend_schema(summary="Listar vínculos de projeto"),
    create=extend_schema(summary="Alocar membro no projeto (Contenção P3)"),
    retrieve=extend_schema(summary="Detalhar vínculo de projeto"),
    update=extend_schema(summary="Atualizar vínculo de projeto"),
    destroy=extend_schema(summary="Remover vínculo de projeto"),
)
class ProjectMembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    queryset = ProjectMembership.objects.all().select_related(
        'project', 'user', 'role', 'job_title'
    )
    serializer_class = ProjectMembershipSerializer


@extend_schema_view(
    list=extend_schema(summary="Listar vínculos de squad"),
    create=extend_schema(summary="Alocar membro na squad (Validação Contínua P3)"),
    retrieve=extend_schema(summary="Detalhar vínculo de squad"),
    update=extend_schema(summary="Atualizar vínculo de squad"),
    destroy=extend_schema(summary="Remover vínculo de squad"),
)
class SquadMembershipViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    queryset = SquadMembership.objects.all().select_related(
        'squad', 'user', 'role', 'job_title'
    )
    serializer_class = SquadMembershipSerializer

