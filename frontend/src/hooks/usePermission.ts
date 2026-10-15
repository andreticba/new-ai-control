// frontend/src/hooks/usePermission.ts | AI-Control v0.0.1 | 14-10-2026 07:47(GMT-04:00)

"use client";

import { useAppSelector } from "@/store";

export function usePermission() {
  const { user } = useAppSelector((state) => state.auth);

  const isPlatformSuperadmin =
    user?.platform_role === "platform_superadmin" ||
    user?.platform_role === "platform_support";

  const canManageOrg = (orgRole?: string | null): boolean => {
    if (isPlatformSuperadmin) return true;
    if (!orgRole) return false;
    const managementRoles = ["org_admin", "org_manager", "org_supervisor"];
    return managementRoles.includes(orgRole.toLowerCase());
  };

  const canManageProject = (
    orgRole?: string | null,
    projectRole?: string | null
  ): boolean => {
    if (isPlatformSuperadmin) return true;
    if (canManageOrg(orgRole)) return true;
    if (!projectRole) return false;
    const managementRoles = ["project_lead", "project_manager"];
    return managementRoles.includes(projectRole.toLowerCase());
  };

  const canManageSquad = (
    orgRole?: string | null,
    projectRole?: string | null,
    squadRole?: string | null
  ): boolean => {
    if (isPlatformSuperadmin) return true;
    if (canManageOrg(orgRole)) return true;
    if (canManageProject(orgRole, projectRole)) return true;
    if (!squadRole) return false;
    const managementRoles = ["squad_lead", "squad_leader", "tech_lead", "scrum_master"];
    return managementRoles.includes(squadRole.toLowerCase());
  };

  return {
    isPlatformSuperadmin,
    canManageOrg,
    canManageProject,
    canManageSquad,
  };
}
