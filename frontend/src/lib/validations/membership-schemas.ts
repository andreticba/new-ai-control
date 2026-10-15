// frontend/src/lib/validations/membership-schemas.ts | AI-Control v0.0.1 | 14-10-2026 07:22(GMT-04:00)

import { z } from "zod";

export const organizationMembershipSchema = z.object({
  organization_id: z.string().uuid("Selecione uma organização válida"),
  user_id: z.union([z.number().int().positive("ID de usuário inválido"), z.string().min(1, "Selecione um usuário")]),
  role_id: z.string().uuid("Selecione um papel de acesso válido"),
  job_title_id: z.string().uuid("Cargo inválido").optional().or(z.literal("")),
  department_id: z.string().uuid("Departamento inválido").optional().or(z.literal("")),
  is_active: z.boolean().default(true),
});

export const projectMembershipSchema = z.object({
  project_id: z.string().uuid("Selecione um projeto válido"),
  user_id: z.union([z.number().int().positive("ID de usuário inválido"), z.string().min(1, "Selecione um usuário")]),
  role_id: z.string().uuid("Selecione um papel de acesso válido"),
  job_title_id: z.string().uuid("Cargo inválido").optional().or(z.literal("")),
  is_external: z.boolean().default(false),
  is_active: z.boolean().default(true),
});

export const squadMembershipSchema = z.object({
  squad_id: z.string().uuid("Selecione uma squad válida"),
  user_id: z.union([z.number().int().positive("ID de usuário inválido"), z.string().min(1, "Selecione um usuário")]),
  role_id: z.string().uuid("Selecione um papel de acesso válido"),
  job_title_id: z.string().uuid("Cargo inválido").optional().or(z.literal("")),
  is_active: z.boolean().default(true),
});

export const quickOnboardSchema = z.object({
  username: z
    .string()
    .min(3, "Nome de usuário deve ter pelo menos 3 caracteres")
    .max(150, "Nome de usuário não pode exceder 150 caracteres")
    .regex(/^[\w.@+-]+$/, "Letras, números e os caracteres @/./+/-/_ apenas"),
  email: z
    .string()
    .email("Informe um endereço de e-mail corporativo válido")
    .max(254, "E-mail não pode exceder 254 caracteres"),
  full_name: z
    .string()
    .min(2, "Nome completo deve ter pelo menos 2 caracteres")
    .max(255, "Nome completo não pode exceder 255 caracteres"),
});

export type OrganizationMembershipFormData = z.infer<typeof organizationMembershipSchema>;
export type ProjectMembershipFormData = z.infer<typeof projectMembershipSchema>;
export type SquadMembershipFormData = z.infer<typeof squadMembershipSchema>;
export type QuickOnboardFormData = z.infer<typeof quickOnboardSchema>;
