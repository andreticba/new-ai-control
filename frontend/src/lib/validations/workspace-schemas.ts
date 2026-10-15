// frontend/src/lib/validations/workspace-schemas.ts | AI-Control v0.0.1 | 14-10-2026 07:22(GMT-04:00)

import { z } from "zod";

export const OrganizationTypeEnum = z.enum([
  "HEALTHCARE",
  "UNIVERSITY",
  "COMPANY",
  "NGO",
  "GOVERNMENT",
  "INDIVIDUAL",
  "OTHER",
]);

export const ProjectTypeEnum = z.enum([
  "RESEARCH",
  "DEVELOPMENT",
  "OPERATIONAL",
  "CONSULTING",
  "OTHER",
]);

export const ProjectStatusEnum = z.enum([
  "PLANNING",
  "ACTIVE",
  "PAUSED",
  "COMPLETED",
  "CANCELLED",
]);

export const slugRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export const organizationSchema = z.object({
  name: z
    .string()
    .min(2, "Nome da organização deve conter pelo menos 2 caracteres")
    .max(255, "Nome não pode exceder 255 caracteres"),
  slug: z
    .string()
    .regex(slugRegex, "Slug deve conter apenas letras minúsculas, números e hífens")
    .max(255, "Slug não pode exceder 255 caracteres")
    .optional()
    .or(z.literal("")),
  org_type: OrganizationTypeEnum.default("COMPANY"),
  is_active: z.boolean().default(true),
});

export const departmentSchema = z.object({
  organization_id: z.string().uuid("Selecione uma organização válida"),
  name: z
    .string()
    .min(2, "Nome do departamento deve conter pelo menos 2 caracteres")
    .max(255, "Nome não pode exceder 255 caracteres"),
  code: z
    .string()
    .min(2, "Código deve conter no mínimo 2 caracteres")
    .max(50, "Código não pode exceder 50 caracteres")
    .regex(/^[A-Z0-9_-]+$/, "Código deve conter apenas letras maiúsculas, números, _ ou -"),
  description: z.string().max(1000, "Descrição não pode exceder 1000 caracteres").optional().or(z.literal("")),
});

export const projectSchema = z.object({
  organization_id: z.string().uuid("Selecione uma organização válida"),
  name: z
    .string()
    .min(2, "Nome do projeto deve conter pelo menos 2 caracteres")
    .max(255, "Nome não pode exceder 255 caracteres"),
  slug: z
    .string()
    .regex(slugRegex, "Slug deve conter apenas letras minúsculas, números e hífens")
    .max(255, "Slug não pode exceder 255 caracteres")
    .optional()
    .or(z.literal("")),
  project_type: ProjectTypeEnum.default("DEVELOPMENT"),
  status: ProjectStatusEnum.default("PLANNING"),
  description: z.string().max(2000, "Descrição não pode exceder 2000 caracteres").optional().or(z.literal("")),
});

export const squadSchema = z.object({
  project_id: z.string().uuid("Squad exige vinculação a um projeto pai obrigatório (Inviolabilidade P3)"),
  name: z
    .string()
    .min(2, "Nome da squad deve conter pelo menos 2 caracteres")
    .max(255, "Nome não pode exceder 255 caracteres"),
  slug: z
    .string()
    .regex(slugRegex, "Slug deve conter apenas letras minúsculas, números e hífens")
    .max(255, "Slug não pode exceder 255 caracteres")
    .optional()
    .or(z.literal("")),
  mission: z.string().max(1000, "Missão não pode exceder 1000 caracteres").optional().or(z.literal("")),
  is_active: z.boolean().default(true),
});

export type OrganizationFormData = z.infer<typeof organizationSchema>;
export type DepartmentFormData = z.infer<typeof departmentSchema>;
export type ProjectFormData = z.infer<typeof projectSchema>;
export type SquadFormData = z.infer<typeof squadSchema>;
