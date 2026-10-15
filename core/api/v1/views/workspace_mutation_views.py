# core/api/v1/views/workspace_mutation_views.py | AI-Control v0.0.1 | 14-10-2026 16:30(GMT-04:00)
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import Organization, Department, Project, Squad
from ..permissions import HasWorkspaceManagePermission
from ..serializers import (
    OrganizationCreateSerializer,
    DepartmentCreateSerializer,
    ProjectCreateSerializer,
    SquadCreateSerializer,
)


def _is_platform_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile and user.profile.platform_role:
        return user.profile.platform_role.slug in ['platform_superadmin', 'platform_support']
    return False


@extend_schema_view(
    list=extend_schema(summary="Listar organizações"),
    create=extend_schema(summary="Criar organização"),
    retrieve=extend_schema(summary="Detalhar organização"),
    update=extend_schema(summary="Atualizar organização"),
    destroy=extend_schema(summary="Remover organização"),
)
class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    serializer_class = OrganizationCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Organization.objects.none()
        if _is_platform_admin(user):
            return Organization.objects.all().order_by('name')
        return Organization.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).distinct().order_by('name')


@extend_schema_view(
    list=extend_schema(summary="Listar departamentos"),
    create=extend_schema(summary="Criar departamento"),
    retrieve=extend_schema(summary="Detalhar departamento"),
    update=extend_schema(summary="Atualizar departamento"),
    destroy=extend_schema(summary="Remover departamento"),
)
class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    serializer_class = DepartmentCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Department.objects.none()
        if _is_platform_admin(user):
            return Department.objects.all().select_related('organization').order_by('name')
        return Department.objects.filter(
            organization__memberships__user=user,
            organization__memberships__is_active=True
        ).select_related('organization').distinct().order_by('name')


@extend_schema_view(
    list=extend_schema(summary="Listar projetos"),
    create=extend_schema(summary="Criar projeto"),
    retrieve=extend_schema(summary="Detalhar projeto"),
    update=extend_schema(summary="Atualizar projeto"),
    destroy=extend_schema(summary="Remover projeto"),
)
class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    serializer_class = ProjectCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Project.objects.none()
        if _is_platform_admin(user):
            return Project.objects.all().select_related('organization').order_by('name')
        return Project.objects.filter(
            organization__memberships__user=user,
            organization__memberships__is_active=True
        ).select_related('organization').distinct().order_by('name')


@extend_schema_view(
    list=extend_schema(summary="Listar squads"),
    create=extend_schema(summary="Criar squad (com validação P3)"),
    retrieve=extend_schema(summary="Detalhar squad"),
    update=extend_schema(summary="Atualizar squad"),
    destroy=extend_schema(summary="Remover squad"),
)
class SquadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasWorkspaceManagePermission]
    serializer_class = SquadCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Squad.objects.none()
        if _is_platform_admin(user):
            return Squad.objects.all().select_related('project').order_by('name')
        return Squad.objects.filter(
            project__organization__memberships__user=user,
            project__organization__memberships__is_active=True
        ).select_related('project').distinct().order_by('name')

