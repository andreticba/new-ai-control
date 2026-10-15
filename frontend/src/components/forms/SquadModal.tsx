// frontend/src/components/forms/SquadModal.tsx | AI-Control v0.0.1 | 14-10-2026 07:27(GMT-04:00)

"use client";

import React, { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { useWorkspaceMutations } from "@/hooks/useWorkspaceMutations";
import {
  squadSchema,
  SquadFormData,
} from "@/lib/validations/workspace-schemas";
import { Users2, Loader2, AlertCircle } from "lucide-react";

interface SquadModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId?: string;
  projects?: Array<{ id: string; name: string }>;
}

export const SquadModal: React.FC<SquadModalProps> = ({
  isOpen,
  onClose,
  projectId,
  projects = [],
}) => {
  const { createSquad } = useWorkspaceMutations();
  const [formData, setFormData] = useState<Partial<SquadFormData>>({
    project_id: projectId || "",
    name: "",
    slug: "",
    mission: "",
    is_active: true,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSlugManuallyEdited, setIsSlugManuallyEdited] = useState(false);

  const slugify = (text: string) => {
    return text
      .toLowerCase()
      .trim()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  };

  const handleNameChange = (val: string) => {
    setFormData((prev) => {
      const updated = { ...prev, name: val };
      if (!isSlugManuallyEdited || !prev.slug) {
        updated.slug = slugify(val);
      }
      return updated;
    });
  };

  const handleSlugChange = (val: string) => {
    setIsSlugManuallyEdited(true);
    setFormData((prev) => ({ ...prev, slug: slugify(val) }));
  };

  useEffect(() => {
    if (projectId) {
      setFormData((prev) => ({ ...prev, project_id: projectId }));
    }
  }, [projectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = squadSchema.safeParse(formData);
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

    createSquad.mutate(result.data, {
      onSuccess: () => {
        setFormData({
          project_id: projectId || "",
          name: "",
          slug: "",
          mission: "",
          is_active: true,
        });
        onClose();
      },
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Nova Squad Multidisciplinar"
      description="Crie uma squad de execução ágil subordinada obrigatoriamente a um Projeto pai (Regra P3)."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {(!projectId || projects.length > 1) && (
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center justify-between">
              <span>Projeto Pai Obrigatório (P3) *</span>
              <span className="text-[10px] text-cyan-400 font-mono">Inviolabilidade P3</span>
            </label>
            <select
              value={formData.project_id || ""}
              onChange={(e) => setFormData({ ...formData, project_id: e.target.value })}
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
            >
              <option value="">Selecione o projeto pai</option>
              {projects.map((proj) => (
                <option key={proj.id} value={proj.id}>
                  {proj.name}
                </option>
              ))}
            </select>
            {errors.project_id && (
              <p className="mt-1 text-xs text-rose-400 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                {errors.project_id}
              </p>
            )}
          </div>
        )}

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Nome da Squad *
          </label>
          <input
            type="text"
            placeholder="Ex: Squad Engenharia de Dados & IA"
            value={formData.name || ""}
            onChange={(e) => handleNameChange(e.target.value)}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center justify-between">
            <span>Slug / Identificador URL (opcional)</span>
            <span className="text-[10px] text-cyan-400 font-mono">Auto-gerado pelo nome</span>
          </label>
          <input
            type="text"
            placeholder="Ex: squad-dados-ia (auto-gerado se vazio)"
            value={formData.slug || ""}
            onChange={(e) => handleSlugChange(e.target.value)}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.slug && <p className="mt-1 text-xs text-rose-400">{errors.slug}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Missão da Squad (opcional)
          </label>
          <textarea
            rows={2}
            placeholder="Qual a missão e entrega central deste time?"
            value={formData.mission || ""}
            onChange={(e) => setFormData({ ...formData, mission: e.target.value })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
        </div>

        <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onClose}
            disabled={createSquad.isPending}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800/70 hover:bg-slate-800 rounded-xl transition-all"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={createSquad.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50"
          >
            {createSquad.isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Criando...
              </>
            ) : (
              <>
                <Users2 className="w-3.5 h-3.5" />
                Criar Squad
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
