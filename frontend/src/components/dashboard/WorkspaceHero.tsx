// frontend/src/components/dashboard/WorkspaceHero.tsx | AI-Control v0.0.1 | 14-10-2026 16:32(GMT-04:00)
'use client';

import React from 'react';
import { ShieldCheck, RefreshCw, Code2 } from 'lucide-react';
import { UserProfile } from '@/types/auth';

export interface WorkspaceHeroProps {
  user: UserProfile | null;
  loading: boolean;
  showJsonInspector: boolean;
  onRefresh: () => void;
  onToggleJsonInspector: () => void;
}

export const WorkspaceHero: React.FC<WorkspaceHeroProps> = ({
  user,
  loading,
  showJsonInspector,
  onRefresh,
  onToggleJsonInspector,
}) => {
  return (
    <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 p-6 md:p-8 overflow-hidden shadow-2xl">
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 text-xs font-medium flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5" />
              Blind Indexing Decoded
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 text-xs font-medium">
              RBAC 4-Tier Ativo
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            {user?.full_name || user?.username}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 flex items-center gap-2">
            <span>
              Identificador: <code className="text-cyan-300 font-mono">@{user?.username}</code>
            </span>
            <span>•</span>
            <span>
              E-mail: <span className="text-slate-300">{user?.email || 'N/A'}</span>
            </span>
            <span>•</span>
            <span>
              Plataforma: <span className="text-indigo-300 font-semibold">{user?.platform_role}</span>
            </span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onRefresh}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-200 flex items-center gap-2 transition-all cursor-pointer"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            Atualizar Árvore
          </button>

          <button
            onClick={onToggleJsonInspector}
            className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-cyan-400 flex items-center gap-2 transition-all cursor-pointer font-mono"
          >
            <Code2 className="h-3.5 w-3.5" />
            {showJsonInspector ? 'Ocultar JSON' : 'Inspecionar REST'}
          </button>
        </div>
      </div>
    </div>
  );
};
