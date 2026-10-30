// nav-rail.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:51:00(GMT-04:00)
'use client';

import React from 'react';
import Link from 'next/link';
import { Layers, MessageSquare, QrCode, LayoutDashboard } from 'lucide-react';

export interface NavRailProps {
  user: {
    email?: string;
    username?: string;
    full_name?: string;
  } | null;
  isWhatsAppConnected: boolean;
  onOpenWhatsAppModal: () => void;
  activeTab?: 'conversations' | 'settings';
}

export function NavRail({
  user,
  isWhatsAppConnected,
  onOpenWhatsAppModal,
  activeTab = 'conversations',
}: NavRailProps) {
  const getUserInitials = () => {
    if (user?.full_name) {
      const parts = user.full_name.trim().split(' ');
      if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
      }
      return user.full_name.slice(0, 2).toUpperCase();
    }
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    return user?.email?.slice(0, 2).toUpperCase() || 'AI';
  };

  return (
    <nav className="w-14 border-r border-slate-800/80 bg-slate-950 flex flex-col items-center justify-between py-3 shrink-0 z-40 select-none">
      {/* Seção Superior: Logo e Navegação Principal */}
      <div className="flex flex-col items-center gap-4 w-full">
        {/* Logo AI-Control */}
        <div
          className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/20"
          title="AI-Control Omnichannel"
        >
          <Layers className="h-5 w-5 text-white" />
        </div>

        <div className="w-8 h-px bg-slate-800" />

        {/* Botão de Conversas (Ativo) */}
        <button
          className={`w-10 h-10 rounded-xl flex items-center justify-center relative border shadow-sm transition group ${
            activeTab === 'conversations'
              ? 'bg-slate-800/90 text-cyan-400 border-slate-700/60'
              : 'text-slate-400 hover:text-white hover:bg-slate-800 border-transparent hover:border-slate-700'
          }`}
          title="Conversas em Andamento"
        >
          <MessageSquare className="h-5 w-5" />
          {activeTab === 'conversations' && (
            <span className="absolute left-0 top-2 bottom-2 w-1 bg-cyan-400 rounded-r" />
          )}
        </button>

        {/* Botão de Conexão WhatsApp / QR Code */}
        <button
          onClick={onOpenWhatsAppModal}
          className={`w-10 h-10 rounded-xl flex items-center justify-center relative border transition group ${
            isWhatsAppConnected
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
              : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-white hover:bg-slate-800'
          }`}
          title="Gerenciar Conexão WhatsApp & QR Code"
        >
          <QrCode className="h-5 w-5" />
          <span
            className={`absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full ring-2 ring-slate-950 ${
              isWhatsAppConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
            }`}
          />
        </button>
      </div>

      {/* Seção Inferior: Atalho Dashboard e Avatar do Usuário */}
      <div className="flex flex-col items-center gap-3 w-full">
        <Link
          href="/"
          className="w-10 h-10 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 border border-transparent hover:border-slate-700 flex items-center justify-center transition"
          title="Voltar ao Dashboard da Plataforma"
        >
          <LayoutDashboard className="h-5 w-5" />
        </Link>

        <div className="w-8 h-px bg-slate-800" />

        {/* Avatar do Usuário */}
        <div
          className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-200 cursor-default shadow-inner"
          title={user?.email || 'Usuário'}
        >
          {getUserInitials()}
        </div>
      </div>
    </nav>
  );
}
