// frontend/src/components/members/TeamDrawer.tsx | AI-Control v0.0.1 | 14-10-2026 07:35(GMT-04:00)

"use client";

import React, { useEffect, useCallback } from "react";
import { X, UserPlus, Users, Shield, Briefcase, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

export interface DrawerMemberItem {
  id: string;
  name: string;
  email?: string;
  role: string;
  job_title?: string | null;
  department?: string | null;
  is_active: boolean;
}

interface TeamDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle: string;
  members: DrawerMemberItem[];
  onAllocateClick: () => void;
}

export const TeamDrawer: React.FC<TeamDrawerProps> = ({
  isOpen,
  onClose,
  title,
  subtitle,
  members,
  onAllocateClick,
}) => {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 overflow-hidden animate-in fade-in duration-200"
    >
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Surface */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900/95 border-l border-slate-800 shadow-2xl backdrop-blur-2xl flex flex-col text-slate-100 animate-in slide-in-from-right duration-300">
          {/* Header */}
          <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-950/40">
            <div>
              <div className="flex items-center gap-2">
                <Users className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-white tracking-tight">{title}</h3>
              </div>
              <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors cursor-pointer"
              aria-label="Fechar painel"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Action Bar */}
          <div className="px-6 py-3.5 bg-slate-900/80 border-b border-slate-800/80 flex items-center justify-between">
            <span className="text-xs text-slate-400 font-mono">
              Total: <strong className="text-white">{members.length}</strong> membros
            </span>
            <button
              onClick={onAllocateClick}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-lg shadow-md shadow-cyan-950/40 transition-all cursor-pointer"
            >
              <UserPlus className="w-3.5 h-3.5" />
              Alocar Pessoa
            </button>
          </div>

          {/* Member List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-3">
            {members.length > 0 ? (
              members.map((member) => (
                <div
                  key={member.id}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-all space-y-2 group"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="text-xs font-semibold text-slate-100 group-hover:text-cyan-300 transition-colors">
                        {member.name}
                      </h4>
                      {member.email && (
                        <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                          {member.email}
                        </p>
                      )}
                    </div>
                    <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 text-[10px] font-mono shrink-0 flex items-center gap-1">
                      <Shield className="w-3 h-3" />
                      {member.role}
                    </span>
                  </div>

                  <div className="pt-2 border-t border-slate-850 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <Briefcase className="w-3 h-3 text-slate-500" />
                      {member.job_title || "Sem cargo definido"}
                    </span>
                    {member.department && (
                      <span className="font-mono text-indigo-400">
                        {member.department}
                      </span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="py-12 text-center text-slate-500 space-y-2">
                <Users className="w-8 h-8 mx-auto text-slate-600" />
                <p className="text-xs">Nenhum membro vinculado a esta unidade.</p>
                <button
                  onClick={onAllocateClick}
                  className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 underline cursor-pointer"
                >
                  Alocar o primeiro colaborador
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
