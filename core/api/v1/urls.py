# core/api/v1/urls.py | AI-Control v0.0.1 | 15-10-2026 07:45(GMT-04:00)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views.user_views import (
    CurrentUserView,
    ActiveWorkspacesView,
    QuickOnboardView,
    UserSearchView,
    RolesListView,
    JobTitlesListView,
)
from .views.workspace_mutation_views import (
    OrganizationViewSet,
    DepartmentViewSet,
    ProjectViewSet,
    SquadViewSet,
)
from .views.membership_views import (
    OrganizationMembershipViewSet,
    ProjectMembershipViewSet,
    SquadMembershipViewSet,
)

app_name = 'api_v1'

router = DefaultRouter()
router.register(r'workspaces/organizations', OrganizationViewSet, basename='workspace-organization')
router.register(r'workspaces/departments', DepartmentViewSet, basename='workspace-department')
router.register(r'workspaces/projects', ProjectViewSet, basename='workspace-project')
router.register(r'workspaces/squads', SquadViewSet, basename='workspace-squad')
router.register(r'workspaces/memberships/organization', OrganizationMembershipViewSet, basename='membership-organization')
router.register(r'workspaces/memberships/project', ProjectMembershipViewSet, basename='membership-project')
router.register(r'workspaces/memberships/squad', SquadMembershipViewSet, basename='membership-squad')


urlpatterns = [
    # Autenticação JWT Stateless
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoints Agregados do Domínio Core / RBAC & Catálogos
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
    path('users/search/', UserSearchView.as_view(), name='user_search'),
    path('users/quick-onboard/', QuickOnboardView.as_view(), name='quick_onboard'),
    path('workspaces/', ActiveWorkspacesView.as_view(), name='active_workspaces'),
    path('workspaces/catalog/roles/', RolesListView.as_view(), name='catalog_roles'),
    path('workspaces/catalog/job-titles/', JobTitlesListView.as_view(), name='catalog_job_titles'),

    # Mutações de Workspaces 4-Tier
    path('', include(router.urls)),
]

