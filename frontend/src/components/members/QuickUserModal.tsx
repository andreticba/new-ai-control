// frontend/src/components/members/QuickUserModal.tsx | AI-Control v0.0.1 | 14-10-2026 07:41(GMT-04:00)

"use client";

import React, { useState } from "react";
import { Modal } from "@/components/ui/Modal";
import { quickOnboardSchema, QuickOnboardFormData } from "@/lib/validations/membership-schemas";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { UserPlus, Loader2, ShieldCheck } from "lucide-react";

interface QuickUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUserCreated?: (user: { id: number; username: string; full_name: string; email: string }) => void;
}

export const QuickUserModal: React.FC<QuickUserModalProps> = ({
  isOpen,
  onClose,
  onUserCreated,
}) => {
  const [formData, setFormData] = useState<Partial<QuickOnboardFormData>>({
    username: "",
    email: "",
    full_name: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isPending, setIsPending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = quickOnboardSchema.safeParse(formData);
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

    try {
      setIsPending(true);
      const response = await api.post("/api/v1/users/quick-onboard/", result.data);
      const createdUser = response.data;
      toast.success(
        `Colaborador "${createdUser.full_name}" admitido com Blind Indexing LGPD!`
      );
      if (onUserCreated) {
        onUserCreated(createdUser);
      }
      setFormData({ username: "", email: "", full_name: "" });
      onClose();
    } catch (error: any) {
      const detail =
        error?.response?.data?.username?.[0] ||
        error?.response?.data?.email?.[0] ||
        error?.response?.data?.detail ||
        "Falha ao realizar admissão do colaborador.";
      toast.error(detail);
      if (error?.response?.data?.username) {
        setErrors((prev) => ({ ...prev, username: error.response.data.username[0] }));
      }
      if (error?.response?.data?.email) {
        setErrors((prev) => ({ ...prev, email: error.response.data.email[0] }));
      }
    } finally {
      setIsPending(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Admissão Imediata de Colaborador"
      description="Cadastre um novo usuário com Blind Indexing criptográfico para alocação direta em equipes."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-800/60 text-xs text-indigo-300 flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
          <span>
            <strong>Proteção LGPD & Blind Indexing (P07):</strong> O nome completo e os dados sensíveis são criptografados no banco e tokens determinísticos de busca cega são gerados automaticamente.
          </span>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Nome Completo do Colaborador *
          </label>
          <input
            type="text"
            placeholder="Ex: Dra. Mariana Vasconcelos"
            value={formData.full_name || ""}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.full_name && <p className="mt-1 text-xs text-rose-400">{errors.full_name}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Nome de Usuário (Username) *
          </label>
          <input
            type="text"
            placeholder="Ex: mariana.vasconcelos"
            value={formData.username || ""}
            onChange={(e) => setFormData({ ...formData, username: e.target.value.toLowerCase() })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.username && <p className="mt-1 text-xs text-rose-400">{errors.username}</p>}
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            E-mail Corporativo *
          </label>
          <input
            type="email"
            placeholder="Ex: mariana@hospitaldemo.org"
            value={formData.email || ""}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
          />
          {errors.email && <p className="mt-1 text-xs text-rose-400">{errors.email}</p>}
        </div>

        <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800/70 hover:bg-slate-800 rounded-xl transition-all"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isPending}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50"
          >
            {isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Cadastrando...
              </>
            ) : (
              <>
                <UserPlus className="w-3.5 h-3.5" />
                Admitir Colaborador
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
