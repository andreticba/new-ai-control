// frontend/src/components/dashboard/DepartmentCard.tsx | AI-Control v0.0.1 | 14-10-2026 16:32(GMT-04:00)
'use client';

import React from 'react';
import { Layers, Plus } from 'lucide-react';
import { DepartmentNode } from '@/types/auth';

export interface DepartmentCardProps {
  departments: DepartmentNode[];
  canManageOrg: boolean;
  onOpenNewDeptModal: () => void;
}

export const DepartmentCard: React.FC<DepartmentCardProps> = ({
  departments,
  canManageOrg,
  onOpenNewDeptModal,
}) => {
  return (
    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Layers className="h-3.5 w-3.5 text-indigo-400" />
          Departamentos ({departments?.length || 0})
        </span>
        <button
          onClick={onOpenNewDeptModal}
          disabled={!canManageOrg}
          title={!canManageOrg ? 'Permissão insuficiente (exige org.manage)' : 'Cadastrar Departamento'}
          className={`px-2 py-1 rounded-lg border text-[11px] font-medium flex items-center gap-1 transition-all ${
            !canManageOrg
              ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed opacity-50'
              : 'bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border-indigo-500/30 cursor-pointer'
          }`}
        >
          <Plus className="h-3 w-3" />
          Depto
        </button>
      </div>

      <div className="space-y-2">
        {departments && departments.length > 0 ? (
          departments.map((dept) => (
            <div
              key={dept.id}
              className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs hover:border-slate-700 transition-colors"
            >
              <span className="text-slate-200 font-medium truncate max-w-[180px]">
                {dept.name}
              </span>
              <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-mono text-[10px]">
                {dept.code}
              </span>
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-500 italic">Nenhum departamento cadastrado.</p>
        )}
      </div>
    </div>
  );
};
