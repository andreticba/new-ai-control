// omnichannel-header.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:51:00(GMT-04:00)
'use client';

import React from 'react';
import { Wifi, WifiOff, Smartphone } from 'lucide-react';

export interface OmnichannelHeaderProps {
  organizationName: string;
  isConnected: boolean; // WebSocket state
  isWhatsAppConnected: boolean;
  onOpenWhatsAppModal: () => void;
}

export function OmnichannelHeader({
  organizationName,
  isConnected,
  isWhatsAppConnected,
  onOpenWhatsAppModal,
}: OmnichannelHeaderProps) {
  return (
    <header className="h-12 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur px-4 flex items-center justify-between flex-shrink-0 z-30 select-none">
      <div className="flex items-center gap-3">
        <span className="text-xs font-bold text-white tracking-tight flex items-center gap-1.5">
          Omnichannel Inbox
          <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
            v0.6.0
          </span>
        </span>

        <div className="h-4 w-px bg-slate-800" />

        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <span className="text-slate-500">Org:</span>
          <span className="font-semibold text-slate-300">
            {organizationName || 'Organização Padrão'}
          </span>
        </div>
      </div>

      {/* Ações Rápidas de Conexão WhatsApp & Status WebSocket */}
      <div className="flex items-center gap-2.5">
        {/* Atalho Rápido para Conectar/Desconectar WhatsApp */}
        <button
          onClick={onOpenWhatsAppModal}
          className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-xs font-medium text-slate-300 transition"
          title="Abrir tela de QR Code e Desconexão do WhatsApp"
        >
          <Smartphone className="w-3.5 h-3.5 text-emerald-400" />
          <span>WhatsApp</span>
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              isWhatsAppConnected ? 'bg-emerald-400' : 'bg-amber-400'
            }`}
          />
        </button>

        {/* Indicador de Status WebSocket */}
        <div
          className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-mono border ${
            isConnected
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
          }`}
        >
          {isConnected ? (
            <>
              <Wifi className="h-3 w-3 animate-pulse" />
              <span>ONLINE</span>
            </>
          ) : (
            <>
              <WifiOff className="h-3 w-3" />
              <span>OFFLINE</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
