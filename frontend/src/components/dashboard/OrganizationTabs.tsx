// frontend/src/components/dashboard/OrganizationTabs.tsx | AI-Control v0.0.1 | 14-10-2026 16:32(GMT-04:00)
'use client';

import React from 'react';
import { Building2, Plus } from 'lucide-react';
import { OrganizationNode } from '@/types/auth';

export interface OrganizationTabsProps {
  organizations: OrganizationNode[];
  selectedIndex: number;
  canManageOrg: boolean;
  onSelectIndex: (index: number) => void;
  onOpenNewOrgModal: () => void;
}

export const OrganizationTabs: React.FC<OrganizationTabsProps> = ({
  organizations,
  selectedIndex,
  canManageOrg,
  onSelectIndex,
  onOpenNewOrgModal,
}) => {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-1">
      {organizations.map((org, idx) => (
        <button
          key={org.id}
          onClick={() => onSelectIndex(idx)}
          className={`px-4 py-2.5 rounded-xl border text-xs font-medium transition-all flex items-center gap-2 cursor-pointer ${
            selectedIndex === idx
              ? 'bg-cyan-500/15 border-cyan-500/50 text-cyan-300 shadow-md shadow-cyan-500/10'
              : 'bg-slate-900/70 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <Building2 className="h-3.5 w-3.5" />
          <span>{org.name}</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
            {org.slug}
          </span>
        </button>
      ))}

      <button
        onClick={onOpenNewOrgModal}
        disabled={!canManageOrg}
        className={`px-3 py-2.5 rounded-xl border border-dashed text-xs font-medium transition-all flex items-center gap-1.5 ${
          !canManageOrg
            ? 'border-slate-800 text-slate-600 cursor-not-allowed opacity-50'
            : 'border-slate-700 bg-slate-900/40 hover:border-cyan-500/50 hover:text-cyan-300 text-slate-400 cursor-pointer'
        }`}
        title={!canManageOrg ? 'Permissão insuficiente (exige org.manage)' : 'Cadastrar Nova Organização'}
      >
        <Plus className="h-3.5 w-3.5" />
        <span>Nova Org</span>
      </button>
    </div>
  );
};
