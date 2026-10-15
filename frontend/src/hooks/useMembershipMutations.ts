// frontend/src/hooks/useMembershipMutations.ts | AI-Control v0.0.1 | 14-10-2026 07:34(GMT-04:00)

"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import {
  OrganizationMembershipFormData,
  ProjectMembershipFormData,
  SquadMembershipFormData,
} from "@/lib/validations/membership-schemas";

export function useMembershipMutations() {
  const queryClient = useQueryClient();

  const invalidateData = () => {
    queryClient.invalidateQueries({ queryKey: ["workspaces"] });
    queryClient.invalidateQueries({ queryKey: ["currentUser"] });
  };

  const allocateOrgMember = useMutation({
    mutationFn: async (data: OrganizationMembershipFormData) => {
      const response = await api.post("/api/v1/workspaces/memberships/organization/", data);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Membro vinculado à organização com sucesso!");
      invalidateData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.user_id?.[0] ||
        error?.response?.data?.role_id?.[0] ||
        error?.response?.data?.department_id?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao vincular membro na organização.";
      toast.error(detail);
    },
  });

  const allocateProjectMember = useMutation({
    mutationFn: async (data: ProjectMembershipFormData) => {
      const response = await api.post("/api/v1/workspaces/memberships/project/", data);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Membro alocado no projeto com sucesso!");
      invalidateData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.user_id?.[0] ||
        error?.response?.data?.role_id?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao alocar membro no projeto. Verifique se o usuário já possui vínculo na organização (P3).";
      toast.error(detail);
    },
  });

  const allocateSquadMember = useMutation({
    mutationFn: async (data: SquadMembershipFormData) => {
      const response = await api.post("/api/v1/workspaces/memberships/squad/", data);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Membro alocado na squad com sucesso!");
      invalidateData();
    },
    onError: (error: any) => {
      const detail =
        error?.response?.data?.user_id?.[0] ||
        error?.response?.data?.role_id?.[0] ||
        error?.response?.data?.detail ||
        "Erro ao alocar membro na squad. O usuário deve possuir vínculo ativo no projeto pai (Validação Contínua P3).";
      toast.error(detail);
    },
  });

  return {
    allocateOrgMember,
    allocateProjectMember,
    allocateSquadMember,
  };
}
