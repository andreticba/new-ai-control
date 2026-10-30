// frontend/src/components/omnichannel/contact-drawer.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:56:00(GMT-04:00)

'use client';

import React from 'react';
import { X, ShieldCheck, Tag, Building, Clock, Lock, Sparkles, User, FileText } from 'lucide-react';
import { OmnichannelConversation } from '@/types/omnichannel';

interface ContactDrawerProps {
  conversation: OmnichannelConversation | null;
  isOpen: boolean;
  onClose: () => void;
  width?: number;
}

export function ContactDrawer({ conversation, isOpen, onClose, width }: ContactDrawerProps) {
  if (!isOpen || !conversation) return null;

  const getInitials = (name: string) => {
    if (!name) return '??';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'CLIENT':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">Cliente Ativo</span>;
      case 'PROSPECT':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/40">Prospect</span>;
      case 'CUSTOMER_LEAD':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">Lead de Cliente</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700">Lead da Plataforma</span>;
    }
  };

  return (
    <div
      style={{ width: width ? `${width}px` : undefined }}
      className={`${width ? '' : 'w-80'} border-l border-slate-800 bg-slate-900/95 backdrop-blur flex flex-col h-full shrink-0 select-none animate-in slide-in-from-right duration-200`}
    >
      {/* Top Header */}
      <div className="p-3.5 border-b border-slate-800 flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-100 flex items-center gap-1.5">
          <User className="w-3.5 h-3.5 text-emerald-400" />
          Perfil do Contato & CRM
        </h3>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Conteúdo com Scroll */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs text-slate-300">
        {/* Identidade do Contato */}
        <div className="flex flex-col items-center text-center gap-2 pb-4 border-b border-slate-800">
          {conversation.contact.avatar_url ? (
            <img
              src={conversation.contact.avatar_url}
              alt={conversation.contact.display_name}
              className="w-16 h-16 rounded-full object-cover ring-2 ring-emerald-500/40 shadow-lg"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-800 flex items-center justify-center text-lg font-bold text-white shadow-lg">
              {getInitials(conversation.contact.display_name)}
            </div>
          )}

          <div className="flex flex-col items-center">
            <h4 className="font-bold text-sm text-slate-100">{conversation.contact.display_name}</h4>
            <div className="mt-1">{getStatusBadge(conversation.contact.status)}</div>
          </div>
        </div>

        {/* Blindagem de PII (Alerta LGPD) */}
        <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 flex items-start gap-2.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          <div className="flex flex-col gap-1">
            <span className="font-semibold text-[11px] text-slate-200">Privacidade Garantida (LGPD)</span>
            <p className="text-[10px] text-slate-400 leading-normal">
              Número de telefone e dados sensíveis mantidos criptografados em repouso e ocultos na interface para mitigação de riscos de vazamento.
            </p>
          </div>
        </div>

        {/* Detalhes da Conversa */}
        <div className="space-y-2.5">
          <span className="font-bold text-[11px] text-slate-400 uppercase tracking-wider block">
            Informações do Canal
          </span>

          <div className="space-y-2 bg-slate-950/60 p-3 rounded-xl border border-slate-800/60">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Canal:</span>
              <span className="font-medium text-slate-200">{conversation.channel_type}</span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Instância:</span>
              <span className="font-mono text-[11px] text-emerald-400">
                {conversation.instance_name || 'ai_control_default'}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400">Status Atual:</span>
              <span
                className={`font-semibold ${
                  conversation.status === 'ACTIVE_AI'
                    ? 'text-cyan-400'
                    : conversation.status === 'ACTIVE_HUMAN'
                    ? 'text-amber-400'
                    : 'text-slate-500'
                }`}
              >
                {conversation.status === 'ACTIVE_AI'
                  ? 'IA Autônoma'
                  : conversation.status === 'ACTIVE_HUMAN'
                  ? 'Atendente Humano'
                  : 'Fechada'}
              </span>
            </div>
          </div>
        </div>

        {/* Tags de CRM */}
        <div className="space-y-2">
          <span className="font-bold text-[11px] text-slate-400 uppercase tracking-wider block">
            Classificação & Tags
          </span>
          <div className="flex flex-wrap gap-1.5">
            {conversation.tags && conversation.tags.length > 0 ? (
              conversation.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-300 border border-slate-700"
                >
                  <Tag className="w-2.5 h-2.5 text-slate-400" />
                  {tag}
                </span>
              ))
            ) : (
              <span className="text-slate-500 text-[11px]">Nenhuma tag atribuída.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
