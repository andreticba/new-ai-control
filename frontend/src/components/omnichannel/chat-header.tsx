// frontend/src/components/omnichannel/chat-header.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:54:00(GMT-04:00)

'use client';

import React from 'react';
import { ArrowLeft, Bot, User, ShieldCheck, UserCheck, BotOff, Sidebar, MoreVertical } from 'lucide-react';
import { OmnichannelConversation } from '@/types/omnichannel';

interface ChatHeaderProps {
  conversation: OmnichannelConversation;
  onTakeover: () => void;
  onReturnToAi: () => void;
  isTakeoverPending?: boolean;
  isReturnPending?: boolean;
  onToggleDrawer: () => void;
  isDrawerOpen?: boolean;
  onBack?: () => void;
}

export function ChatHeader({
  conversation,
  onTakeover,
  onReturnToAi,
  isTakeoverPending,
  isReturnPending,
  onToggleDrawer,
  isDrawerOpen,
  onBack,
}: ChatHeaderProps) {
  const isAi = conversation.status === 'ACTIVE_AI';
  const isHuman = conversation.status === 'ACTIVE_HUMAN';

  const getInitials = (name: string) => {
    if (!name) return '??';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="h-14 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-3 flex items-center justify-between shrink-0 select-none">
      <div className="flex items-center gap-2.5 min-w-0">
        {/* Botão Voltar (Mobile) */}
        {onBack && (
          <button
            onClick={onBack}
            className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
        )}

        {/* Avatar */}
        <div className="relative shrink-0 cursor-pointer" onClick={onToggleDrawer}>
          {conversation.contact.avatar_url ? (
            <img
              src={conversation.contact.avatar_url}
              alt={conversation.contact.display_name}
              className="w-9 h-9 rounded-full object-cover ring-1 ring-slate-700"
            />
          ) : (
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-800 flex items-center justify-center text-xs font-bold text-white shadow-inner">
              {getInitials(conversation.contact.display_name)}
            </div>
          )}
          <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-slate-900" />
        </div>

        {/* Nome do Contato e Status (Zero Telefone Exposto) */}
        <div className="min-w-0 flex flex-col">
          <div className="flex items-center gap-2">
            <h3
              onClick={onToggleDrawer}
              className="text-xs font-bold text-slate-100 truncate cursor-pointer hover:text-emerald-400 transition"
            >
              {conversation.contact.display_name}
            </h3>
            <span
              title="Identidade protegida por criptografia e blind indexing (LGPD)"
              className="flex items-center gap-0.5 text-[10px] text-emerald-400 font-medium bg-emerald-950/60 border border-emerald-800/40 px-1.5 py-0.2 rounded-full"
            >
              <ShieldCheck className="w-3 h-3" />
              LGPD
            </span>
          </div>

          <div className="flex items-center gap-2 text-[10px] text-slate-400">
            {isAi ? (
              <span className="flex items-center gap-1 text-cyan-400">
                <Bot className="w-3 h-3" /> Atendimento Autônomo por IA
              </span>
            ) : isHuman ? (
              <span className="flex items-center gap-1 text-amber-400">
                <UserCheck className="w-3 h-3" /> Atendimento Humano Ativo
              </span>
            ) : (
              <span className="text-slate-500">Conversa Encerrada</span>
            )}
          </div>
        </div>
      </div>

      {/* Ações do Header (Takeover / Devolver IA / Drawer) */}
      <div className="flex items-center gap-2 shrink-0">
        {isAi ? (
          <button
            onClick={onTakeover}
            disabled={isTakeoverPending}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-slate-950 transition disabled:opacity-50 shadow-sm"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Assumir Atendimento</span>
          </button>
        ) : isHuman ? (
          <button
            onClick={onReturnToAi}
            disabled={isReturnPending}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 transition disabled:opacity-50 shadow-sm"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Devolver para IA</span>
          </button>
        ) : null}

        {/* Botão de Abrir Drawer de CRM */}
        <button
          onClick={onToggleDrawer}
          title="Ver perfil e CRM do contato"
          className={`p-2 rounded-lg text-xs border transition ${
            isDrawerOpen
              ? 'bg-slate-800 text-emerald-400 border-slate-700'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800 border-transparent'
          }`}
        >
          <Sidebar className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
