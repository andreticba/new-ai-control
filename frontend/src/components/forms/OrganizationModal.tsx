// frontend/src/components/forms/OrganizationModal.tsx | AI-Control v0.0.1 | 14-10-2026 07:26(GMT-04:00)

"use client";

import React, { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { useWorkspaceMutations } from "@/hooks/useWorkspaceMutations";
import {
  organizationSchema,
  OrganizationFormData,
} from "@/lib/validations/workspace-schemas";
import { Building2, Loader2 } from "lucide-react";

interface OrganizationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OrganizationModal: React.FC<OrganizationModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { createOrganization } = useWorkspaceMutations();
  const [formData, setFormData] = useState<Partial<OrganizationFormData>>({
    name: "",
    slug: "",
    org_type: "COMPANY",
    is_active: true,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = organizationSchema.safeParse(formData);
    if (!result.success) {
      const fieldErrors: Record<string, string> = {};
      result.error.errors.forEach((err) => {
        if (err.path[0]) {
          fieldErrors[err.path[0].toString()] = err.message;
        }
      });
      setErrors(fieldErrors);
      return;
    }

    createOrganization.mutate(result.data, {
      onSuccess: () => {
        setFormData({ name: "", slug: "", org_type: "COMPANY", is_active: true });
        onClose();
      },
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Nova Organização"
      description="Crie uma nova organização de primeiro nível para governança corporativa no AI-Control."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Nome da Organização *
          </label>
          <div className="relative">
            <input
              type="text"
              placeholder="Ex: ACME Healthcare Corp"
              value={formData.name || ""}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
            />
          </div>
          {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Slug / Identificador URL (opcional)
          </label>
          <input
            type="text"
            placeholder="Ex: acme-corp (auto-gerado se vazio)"
            value={formData.slug || ""}
            onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase() })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.slug && <p className="mt-1 text-xs text-rose-400">{errors.slug}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Tipo de Organização
          </label>
          <select
            value={formData.org_type || "COMPANY"}
            onChange={(e) =>
              setFormData({ ...formData, org_type: e.target.value as OrganizationFormData["org_type"] })
            }
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          >
            <option value="COMPANY">Empresa</option>
            <option value="HEALTHCARE">Clínica / Hospital / Saúde</option>
            <option value="UNIVERSITY">Instituição Acadêmica</option>
            <option value="GOVERNMENT">Governo / Setor Público</option>
            <option value="NGO">Terceiro Setor / ONG</option>
            <option value="INDIVIDUAL">Profissional Liberal</option>
            <option value="OTHER">Outro</option>
          </select>
        </div>

        <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onClose}
            disabled={createOrganization.isPending}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800/70 hover:bg-slate-800 rounded-xl transition-all"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={createOrganization.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50"
          >
            {createOrganization.isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Criando...
              </>
            ) : (
              <>
                <Building2 className="w-3.5 h-3.5" />
                Criar Organização
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
