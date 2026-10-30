// frontend/src/components/omnichannel/conversation-list.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:54:00(GMT-04:00)

'use client';

import React, { useState } from 'react';
import { Search, Bot, User, Pin, Check, CheckCheck, Sparkles, Filter } from 'lucide-react';
import { OmnichannelConversation, ConversationFilterTab } from '@/types/omnichannel';

interface ConversationListProps {
  conversations: OmnichannelConversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  isLoading?: boolean;
  filterTab: ConversationFilterTab;
  onFilterChange: (tab: ConversationFilterTab) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export function ConversationList({
  conversations,
  activeConversationId,
  onSelectConversation,
  isLoading,
  filterTab,
  onFilterChange,
  searchQuery,
  onSearchChange,
}: ConversationListProps) {
  const tabs: { key: ConversationFilterTab; label: string }[] = [
    { key: 'all', label: 'Todas' },
    { key: 'unread', label: 'Não lidas' },
    { key: 'ai', label: 'Em IA' },
    { key: 'mine', label: 'Minhas' },
    { key: 'pinned', label: 'Fixadas' },
  ];

  const formatTimestamp = (isoString?: string | null) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const isToday =
      date.getDate() === now.getDate() &&
      date.getMonth() === now.getMonth() &&
      date.getFullYear() === now.getFullYear();

    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString([], { day: '2-digit', month: '2-digit' });
  };

  const getInitials = (name: string) => {
    if (!name) return '??';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800 select-none">
      {/* Top Header */}
      <div className="p-3 border-b border-slate-800 bg-slate-900/90 backdrop-blur flex flex-col gap-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold tracking-tight text-slate-100 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              Conversas
            </h2>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
              {conversations.length}
            </span>
          </div>
        </div>

        {/* Campo de Busca */}
        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar por contato ou assunto..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 transition"
          />
        </div>

        {/* Abas de Filtro */}
        <div className="flex items-center gap-1 overflow-x-auto pb-0.5 no-scrollbar text-xs">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => onFilterChange(tab.key)}
              className={`px-2.5 py-1 rounded-full whitespace-nowrap font-medium transition ${
                filterTab === tab.key
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800 hover:text-slate-300 border border-transparent'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Conversas (Scrollável O(1)) */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/40">
        {isLoading ? (
          <div className="p-8 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
            <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            Carregando conversas...
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
            <Filter className="w-8 h-8 text-slate-600 stroke-[1.5]" />
            Nenhuma conversa encontrada neste filtro.
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = activeConversationId === conv.id;
            const isAi = conv.status === 'ACTIVE_AI';
            const isHuman = conv.status === 'ACTIVE_HUMAN';

            return (
              <div
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`p-3 cursor-pointer transition flex items-start gap-3 group relative ${
                  isActive
                    ? 'bg-slate-800/80 border-l-4 border-emerald-500 pl-2'
                    : 'hover:bg-slate-800/40'
                }`}
              >
                {/* Avatar / Foto de Perfil */}
                <div className="relative shrink-0">
                  {conv.contact.avatar_url ? (
                    <img
                      src={conv.contact.avatar_url}
                      alt={conv.contact.display_name}
                      className="w-11 h-11 rounded-full object-cover ring-1 ring-slate-700"
                    />
                  ) : (
                    <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-800 flex items-center justify-center text-xs font-bold text-white shadow-inner">
                      {getInitials(conv.contact.display_name)}
                    </div>
                  )}

                  {/* Indicador de Status (IA vs Humano) */}
                  <span
                    title={isAi ? 'Atendimento por IA' : 'Atendimento Humano'}
                    className={`absolute -bottom-0.5 -right-0.5 w-4 h-4 rounded-full flex items-center justify-center ring-2 ring-slate-900 ${
                      isAi
                        ? 'bg-cyan-500 text-slate-950'
                        : isHuman
                        ? 'bg-amber-500 text-slate-950'
                        : 'bg-slate-600 text-slate-300'
                    }`}
                  >
                    {isAi ? <Bot className="w-2.5 h-2.5" /> : <User className="w-2.5 h-2.5" />}
                  </span>
                </div>

                {/* Conteúdo Central */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-1 mb-0.5">
                    <span className="font-semibold text-xs text-slate-100 truncate group-hover:text-emerald-400 transition">
                      {conv.contact.display_name}
                    </span>
                    <span className="text-[10px] text-slate-500 shrink-0 font-medium">
                      {formatTimestamp(conv.last_message?.timestamp || conv.updated_at)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs text-slate-400 truncate flex items-center gap-1 font-normal">
                      {conv.last_message?.direction === 'OUTBOUND' && (
                        conv.last_message.delivery_status === 'READ' ? (
                          <CheckCheck className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        ) : conv.last_message.delivery_status === 'DELIVERED' ? (
                          <CheckCheck className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        ) : (
                          <Check className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        )
                      )}
                      <span>
                        {conv.last_message?.content || 'Nova conversa iniciada'}
                      </span>
                    </p>

                    <div className="flex items-center gap-1 shrink-0">
                      {conv.is_pinned && <Pin className="w-3 h-3 text-amber-400 rotate-45" />}
                      {conv.unread_count > 0 && (
                        <span className="px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-emerald-500 text-slate-950 shadow-sm animate-pulse">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Tags */}
                  {conv.tags && conv.tags.length > 0 && (
                    <div className="flex items-center gap-1 mt-1.5 overflow-hidden">
                      {conv.tags.slice(0, 2).map((t, i) => (
                        <span
                          key={i}
                          className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/60"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
