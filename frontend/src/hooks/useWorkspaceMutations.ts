// frontend/src/hooks/useWorkspaceMutations.ts | AI-Control v0.0.1 | 14-10-2026 07:26(GMT-04:00)

"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import {
  OrganizationFormData,
  DepartmentFormData,
  ProjectFormData,
  SquadFormData,
} from "@/lib/validations/workspace-schemas";

export function useWorkspaceMutations() {
  const queryClient = useQueryClient();

  const invalidateWorkspaceData = () => {
    queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    queryClient.invalidateQueries({ queryKey: ["currentUser"] });
  };

  const createOrganization = useMutation({
    mutationFn: async (data: OrganizationFormData) => {
      const response = await api.post("/api/v1/workspaces/organizations/", data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Organização "${data.name}" criada com sucesso!`);
      invalidateWorkspaceData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.slug?.[0] ||
        error?.response?.data?.name?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao criar organização.";
      toast.error(detail);
    },
  });

  const createDepartment = useMutation({
    mutationFn: async (data: DepartmentFormData) => {
      const response = await api.post("/api/v1/workspaces/departments/", data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Departamento "${data.name}" (${data.code}) criado com sucesso!`);
      invalidateWorkspaceData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.code?.[0] ||
        error?.response?.data?.name?.[0] ||
        error?.response?.data?.organization_id?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao criar departamento.";
      toast.error(detail);
    },
  });

  const createProject = useMutation({
    mutationFn: async (data: ProjectFormData) => {
      const response = await api.post("/api/v1/workspaces/projects/", data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Projeto "${data.name}" criado com sucesso!`);
      invalidateWorkspaceData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.name?.[0] ||
        error?.response?.data?.slug?.[0] ||
        error?.response?.data?.organization_id?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao criar projeto.";
      toast.error(detail);
    },
  });

  const createSquad = useMutation({
    mutationFn: async (data: SquadFormData) => {
      const response = await api.post("/api/v1/workspaces/squads/", data);
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(`Squad "${data.name}" criada com sucesso!`);
      invalidateWorkspaceData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.project_id?.[0] ||
        error?.response?.data?.name?.[0] ||
        error?.response?.data?.slug?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao criar squad. Verifique o vínculo do projeto pai (Inviolabilidade P3).";
      toast.error(detail);
    },
  });

  return {
    createOrganization,
    createDepartment,
    createProject,
    createSquad,
  };
}
