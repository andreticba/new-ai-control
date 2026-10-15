// frontend/src/components/dashboard/OmnichannelCard.tsx | AI-Control v0.0.1 | 14-10-2026 16:32(GMT-04:00)
'use client';

import React from 'react';
import { MessageSquareCode, Radio } from 'lucide-react';

export interface OmnichannelCardProps {
  orgSlug: string;
}

export const OmnichannelCard: React.FC<OmnichannelCardProps> = ({ orgSlug }) => {
  return (
    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <MessageSquareCode className="h-3.5 w-3.5 text-emerald-400" />
          Omnichannel & Agentes IA
        </span>
        <Radio className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
      </div>
      <p className="text-xs text-slate-400 leading-relaxed">
        Instância vinculada via Soft Foreign Key (<code className="text-cyan-300">organization_id</code>):
      </p>
      <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs space-y-1.5 font-mono">
        <div className="flex justify-between text-slate-400">
          <span>Instância:</span>
          <span className="text-cyan-400">ai_control_{orgSlug}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>Status IA:</span>
          <span className="text-emerald-400 font-semibold">ACTIVE_AI</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>Roteamento:</span>
          <span className="text-slate-200">5511000000001@example.org</span>
        </div>
      </div>
    </div>
  );
};
