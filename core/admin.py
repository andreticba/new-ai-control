# core/admin.py | Atualizado em: 06-10-2026 21:42:00(GMT-04:00)
from django.contrib import admin
from .models import (
    Permission, Role, Organization, Department, JobTitle,
    Project, Squad,
    OrganizationMembership, ProjectMembership, SquadMembership,
    UserProfile, ParticipantProfile, ProfessionalProfile, OnboardingProcess,
    ConsentLog, DataAccessGrant, AuditLog,
    Document, DocumentChunk,
    Contact, ContactPhoneNumber, ContactOrganizationMembership,
    Conversation, Message,
)


# --- RBAC & Governance ---

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('slug', 'name')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'scope', 'level', 'inheritance', 'is_system_role')
    list_filter = ('scope', 'is_system_role')
    search_fields = ('slug', 'name')
    filter_horizontal = ('permissions',)


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 0
    fields = ('name', 'code', 'slug', 'parent')


class OrgMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    fields = ('user', 'role', 'job_title', 'department', 'is_active')
    raw_id_fields = ('user',)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'org_type', 'slug', 'is_internal', 'is_active', 'created_at')
    list_filter = ('org_type', 'is_internal', 'is_active')
    search_fields = ('name', 'slug')
    inlines = [DepartmentInline, OrgMembershipInline]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organization', 'parent', 'created_at')
    list_filter = ('organization',)
    search_fields = ('name', 'code', 'slug')


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'level', 'category', 'organization', 'is_system')
    list_filter = ('level', 'category', 'is_system')
    search_fields = ('name', 'slug')


class SquadInline(admin.TabularInline):
    model = Squad
    extra = 0
    fields = ('name', 'slug', 'is_active')


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0
    fields = ('user', 'role', 'job_title', 'is_external', 'is_active')
    raw_id_fields = ('user',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'project_type', 'status', 'owner_department', 'created_at')
    list_filter = ('project_type', 'status', 'organization')
    search_fields = ('name', 'slug')
    inlines = [SquadInline, ProjectMembershipInline]


class SquadMembershipInline(admin.TabularInline):
    model = SquadMembership
    extra = 0
    fields = ('user', 'role', 'job_title', 'is_active')
    raw_id_fields = ('user',)


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'is_active', 'created_at')
    list_filter = ('is_active', 'project__organization')
    search_fields = ('name', 'slug')
    inlines = [SquadMembershipInline]


# --- Memberships standalone ---

@admin.register(OrganizationMembership)
class OrgMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'job_title', 'department', 'is_active')
    list_filter = ('is_active', 'role', 'organization')
    raw_id_fields = ('user',)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'role', 'job_title', 'is_external', 'is_active')
    list_filter = ('is_active', 'role', 'is_external')
    raw_id_fields = ('user',)


@admin.register(SquadMembership)
class SquadMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'squad', 'role', 'job_title', 'is_active')
    list_filter = ('is_active', 'role')
    raw_id_fields = ('user',)


# --- Profiles ---

admin.site.register(UserProfile)
admin.site.register(ParticipantProfile)
admin.site.register(ProfessionalProfile)
admin.site.register(OnboardingProcess)


# --- Governance & Audit ---

admin.site.register(ConsentLog)
admin.site.register(DataAccessGrant)
admin.site.register(AuditLog)


# --- Documents ---

admin.site.register(Document)
admin.site.register(DocumentChunk)


# --- CRM ---

admin.site.register(Contact)
admin.site.register(ContactPhoneNumber)
admin.site.register(ContactOrganizationMembership)
admin.site.register(Conversation)
admin.site.register(Message)
