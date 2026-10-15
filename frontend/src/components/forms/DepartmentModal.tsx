// frontend/src/components/forms/DepartmentModal.tsx | AI-Control v0.0.1 | 14-10-2026 07:26(GMT-04:00)

"use client";

import React, { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { useWorkspaceMutations } from "@/hooks/useWorkspaceMutations";
import {
  departmentSchema,
  DepartmentFormData,
} from "@/lib/validations/workspace-schemas";
import { Briefcase, Loader2 } from "lucide-react";

interface DepartmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  organizationId?: string;
  organizations?: Array<{ id: string; name: string }>;
}

export const DepartmentModal: React.FC<DepartmentModalProps> = ({
  isOpen,
  onClose,
  organizationId,
  organizations = [],
}) => {
  const { createDepartment } = useWorkspaceMutations();
  const [formData, setFormData] = useState<Partial<DepartmentFormData>>({
    organization_id: organizationId || "",
    name: "",
    code: "",
    description: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isCodeManuallyEdited, setIsCodeManuallyEdited] = useState(false);

  const generateCodeFromName = (name: string): string => {
    const clean = name.trim();
    if (!clean) return "";
    const words = clean
      .split(/\s+/)
      .filter((w) => !["de", "da", "do", "das", "dos", "e", "em", "para"].includes(w.toLowerCase()));
    if (words.length > 1) {
      return words.map((w) => w[0]).join("").toUpperCase().slice(0, 5);
    }
    return clean.replace(/[^a-zA-Z0-9]/g, "").slice(0, 4).toUpperCase();
  };

  const handleNameChange = (val: string) => {
    setFormData((prev) => {
      const updated = { ...prev, name: val };
      if (!isCodeManuallyEdited || !prev.code) {
        updated.code = generateCodeFromName(val);
      }
      return updated;
    });
  };

  const handleCodeChange = (val: string) => {
    setIsCodeManuallyEdited(true);
    setFormData((prev) => ({ ...prev, code: val.toUpperCase() }));
  };

  useEffect(() => {
    if (organizationId) {
      setFormData((prev) => ({ ...prev, organization_id: organizationId }));
    }
  }, [organizationId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = departmentSchema.safeParse(formData);
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

    createDepartment.mutate(result.data, {
      onSuccess: () => {
        setFormData({
          organization_id: organizationId || "",
          name: "",
          code: "",
          description: "",
        });
        onClose();
      },
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Novo Departamento"
      description="Cadastre uma unidade fixa do organograma para esta organização."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {(!organizationId || organizations.length > 1) && (
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Organização *
            </label>
            <select
              value={formData.organization_id || ""}
              onChange={(e) => setFormData({ ...formData, organization_id: e.target.value })}
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
            >
              <option value="">Selecione uma organização</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
            {errors.organization_id && (
              <p className="mt-1 text-xs text-rose-400">{errors.organization_id}</p>
            )}
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Nome do Departamento *
          </label>
          <input
            type="text"
            placeholder="Ex: Departamento de Engenharia e TI"
            value={formData.name || ""}
            onChange={(e) => handleNameChange(e.target.value)}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center justify-between">
            <span>Código / Sigla Departamental *</span>
            <span className="text-[10px] text-cyan-400 font-mono">Auto-sugerido pelo nome</span>
          </label>
          <input
            type="text"
            placeholder="Ex: TI, ENG, DCOMP, RH"
            value={formData.code || ""}
            onChange={(e) => handleCodeChange(e.target.value)}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 uppercase focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.code && <p className="mt-1 text-xs text-rose-400">{errors.code}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Descrição (opcional)
          </label>
          <textarea
            rows={2}
            placeholder="Breve descrição da missão deste departamento..."
            value={formData.description || ""}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.description && <p className="mt-1 text-xs text-rose-400">{errors.description}</p>}
        </div>

        <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onClose}
            disabled={createDepartment.isPending}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800/70 hover:bg-slate-800 rounded-xl transition-all"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={createDepartment.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50"
          >
            {createDepartment.isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Criando...
              </>
            ) : (
              <>
                <Briefcase className="w-3.5 h-3.5" />
                Criar Departamento
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
