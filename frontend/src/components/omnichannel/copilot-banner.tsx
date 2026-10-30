// frontend/src/components/omnichannel/copilot-banner.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:55:00(GMT-04:00)

'use client';

import React from 'react';
import { Sparkles, Check, ArrowDownToLine, X, Zap } from 'lucide-react';
import { CopilotDraft } from '@/types/omnichannel';

interface CopilotBannerProps {
  draft: CopilotDraft | null;
  onApprove: (draftId: string) => void;
  onInsert: (content: string) => void;
  onDiscard: (draftId: string) => void;
  isApproving?: boolean;
}

export function CopilotBanner({
  draft,
  onApprove,
  onInsert,
  onDiscard,
  isApproving,
}: CopilotBannerProps) {
  if (!draft || draft.status !== 'PENDING') {
    return null;
  }

  return (
    <div className="mx-3 mb-2 p-3 rounded-xl bg-gradient-to-r from-emerald-950/80 via-slate-900/90 to-teal-950/80 border border-emerald-500/40 shadow-xl backdrop-blur-md animate-in fade-in slide-in-from-bottom-2 duration-200">
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
          <Sparkles className="w-4 h-4 animate-spin-slow text-emerald-300" />
          <span>Sugestão do Copiloto de IA</span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-900/60 text-emerald-300 border border-emerald-700/50">
            {draft.generated_by_model}
          </span>
          {draft.latency_ms > 0 && (
            <span className="flex items-center gap-0.5 text-[9px] text-slate-400 font-mono">
              <Zap className="w-2.5 h-2.5 text-amber-400" />
              {draft.latency_ms}ms
            </span>
          )}
        </div>

        <button
          onClick={() => onDiscard(draft.id)}
          title="Descartar sugestão"
          className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Texto Sugerido */}
      <p className="text-xs text-slate-200 mb-2.5 leading-relaxed bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
        {draft.suggested_content}
      </p>

      {/* Ações de 1-Clique */}
      <div className="flex items-center justify-end gap-2">
        <button
          onClick={() => onInsert(draft.suggested_content)}
          className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
        >
          <ArrowDownToLine className="w-3.5 h-3.5 text-cyan-400" />
          <span>Inserir no campo</span>
        </button>

        <button
          onClick={() => onApprove(draft.id)}
          disabled={isApproving}
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold text-slate-950 bg-emerald-400 hover:bg-emerald-300 transition shadow disabled:opacity-50"
        >
          <Check className="w-3.5 h-3.5 stroke-[2.5]" />
          <span>{isApproving ? 'Enviando...' : 'Aprovar e Enviar'}</span>
        </button>
      </div>
    </div>
  );
}
