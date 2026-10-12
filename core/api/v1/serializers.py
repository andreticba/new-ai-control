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
