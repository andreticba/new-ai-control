// frontend/src/types/auth.ts | AI-Control v0.0.1 | 12-10-2026 09:55(GMT-04:00)

export interface PrimaryOrganization {
  id: string;
  name: string;
  slug: string;
}

export interface OrganizationMembershipDetail {
  organization_id: string;
  organization_name: string;
  organization_slug: string;
  role: string;
  job_title: string | null;
  is_active: boolean;
}

export interface ProjectMembershipDetail {
  project_id: string;
  project_name: string;
  project_slug: string;
  role: string;
  job_title: string | null;
  is_active: boolean;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  primary_organization: PrimaryOrganization | null;
  platform_role: string;
  organization_memberships: OrganizationMembershipDetail[];
  project_memberships: ProjectMembershipDetail[];
}

export interface SquadNode {
  id: string;
  name: string;
  slug: string;
  role: string;
  job_title: string | null;
}

export interface ProjectNode {
  id: string;
  name: string;
  slug: string;
  role: string;
  job_title: string | null;
  squads: SquadNode[];
}

export interface DepartmentNode {
  id: string;
  name: string;
  slug: string;
  code: string;
}

export interface OrganizationNode {
  id: string;
  name: string;
  slug: string;
  role: string;
  job_title: string | null;
  departments: DepartmentNode[];
  projects: ProjectNode[];
}

export interface WorkspaceTree {
  workspaces?: OrganizationNode[];
  organizations?: OrganizationNode[];
}
