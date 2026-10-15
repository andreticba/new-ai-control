// frontend/src/components/dashboard/WorkspaceStats.tsx | AI-Control v0.0.1 | 14-10-2026 16:32(GMT-04:00)
'use client';

import React from 'react';
import { Building2, Layers, FolderGit2, Users2 } from 'lucide-react';

export interface WorkspaceStatsProps {
  totalOrgs: number;
  totalDepts: number;
  totalProjects: number;
  totalSquads: number;
}

export const WorkspaceStats: React.FC<WorkspaceStatsProps> = ({
  totalOrgs,
  totalDepts,
  totalProjects,
  totalSquads,
}) => {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-xs font-medium uppercase tracking-wider">Organizações</span>
          <Building2 className="h-4 w-4 text-cyan-400" />
        </div>
        <div className="text-2xl font-bold text-white">{totalOrgs}</div>
        <p className="text-[11px] text-slate-500">Tenants vinculados</p>
      </div>

      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-xs font-medium uppercase tracking-wider">Departamentos</span>
          <Layers className="h-4 w-4 text-indigo-400" />
        </div>
        <div className="text-2xl font-bold text-white">{totalDepts}</div>
        <p className="text-[11px] text-slate-500">Unidades estruturais</p>
      </div>

      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-xs font-medium uppercase tracking-wider">Projetos</span>
          <FolderGit2 className="h-4 w-4 text-amber-400" />
        </div>
        <div className="text-2xl font-bold text-white">{totalProjects}</div>
        <p className="text-[11px] text-slate-500">Escopos de governança</p>
      </div>

      <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
        <div className="flex items-center justify-between text-slate-400">
          <span className="text-xs font-medium uppercase tracking-wider">Squads</span>
          <Users2 className="h-4 w-4 text-emerald-400" />
        </div>
        <div className="text-2xl font-bold text-white">{totalSquads}</div>
        <p className="text-[11px] text-slate-500">Equipes operacionais</p>
      </div>
    </div>
  );
};
