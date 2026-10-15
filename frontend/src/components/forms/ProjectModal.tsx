// frontend/src/components/forms/ProjectModal.tsx | AI-Control v0.0.1 | 14-10-2026 07:26(GMT-04:00)

"use client";

import React, { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { useWorkspaceMutations } from "@/hooks/useWorkspaceMutations";
import {
  projectSchema,
  ProjectFormData,
} from "@/lib/validations/workspace-schemas";
import { FolderGit2, Loader2 } from "lucide-react";

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  organizationId?: string;
  organizations?: Array<{ id: string; name: string }>;
}

export const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  organizationId,
  organizations = [],
}) => {
  const { createProject } = useWorkspaceMutations();
  const [formData, setFormData] = useState<Partial<ProjectFormData>>({
    organization_id: organizationId || "",
    name: "",
    slug: "",
    project_type: "DEVELOPMENT",
    status: "PLANNING",
    description: "",
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
    if (organizationId) {
      setFormData((prev) => ({ ...prev, organization_id: organizationId }));
    }
  }, [organizationId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = projectSchema.safeParse(formData);
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

    createProject.mutate(result.data, {
      onSuccess: () => {
        setFormData({
          organization_id: organizationId || "",
          name: "",
          slug: "",
          project_type: "DEVELOPMENT",
          status: "PLANNING",
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
      title="Novo Projeto"
      description="Inicie um novo projeto ou iniciativa dentro da estrutura organizacional."
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
            Nome do Projeto *
          </label>
          <input
            type="text"
            placeholder="Ex: Plataforma de Inteligência em Saúde"
            value={formData.name || ""}
            onChange={(e) => handleNameChange(e.target.value)}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Tipo de Projeto
            </label>
            <select
              value={formData.project_type || "DEVELOPMENT"}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  project_type: e.target.value as ProjectFormData["project_type"],
                })
              }
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
            >
              <option value="DEVELOPMENT">Desenvolvimento</option>
              <option value="RESEARCH">Pesquisa</option>
              <option value="OPERATIONAL">Operacional / Contínuo</option>
              <option value="CONSULTING">Consultoria</option>
              <option value="OTHER">Outro</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Status Inicial
            </label>
            <select
              value={formData.status || "PLANNING"}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  status: e.target.value as ProjectFormData["status"],
                })
              }
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
            >
              <option value="PLANNING">Planejamento</option>
              <option value="ACTIVE">Ativo</option>
              <option value="PAUSED">Pausado</option>
              <option value="COMPLETED">Concluído</option>
              <option value="CANCELLED">Cancelado</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center justify-between">
            <span>Slug / Identificador URL (opcional)</span>
            <span className="text-[10px] text-cyan-400 font-mono">Auto-gerado pelo nome</span>
          </label>
          <input
            type="text"
            placeholder="Ex: plataf-saude (auto-gerado se vazio)"
            value={formData.slug || ""}
            onChange={(e) => handleSlugChange(e.target.value)}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.slug && <p className="mt-1 text-xs text-rose-400">{errors.slug}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Descrição (opcional)
          </label>
          <textarea
            rows={2}
            placeholder="Objetivos e escopo do projeto..."
            value={formData.description || ""}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
        </div>

        <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onClose}
            disabled={createProject.isPending}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800/70 hover:bg-slate-800 rounded-xl transition-all"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={createProject.isPending}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50"
          >
            {createProject.isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Criando...
              </>
            ) : (
              <>
                <FolderGit2 className="w-3.5 h-3.5" />
                Criar Projeto
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
