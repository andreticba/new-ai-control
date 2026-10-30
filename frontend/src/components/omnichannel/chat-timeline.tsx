// frontend/src/components/omnichannel/chat-timeline.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:55:00(GMT-04:00)

'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  Check,
  CheckCheck,
  Clock,
  AlertCircle,
  Bot,
  Reply,
  Play,
  Pause,
  FileText,
  Sparkles,
} from 'lucide-react';
import { OmnichannelMessage, OmnichannelConversation } from '@/types/omnichannel';

interface ChatTimelineProps {
  messages: OmnichannelMessage[];
  conversation: OmnichannelConversation;
  onReplyMessage: (message: OmnichannelMessage) => void;
  isLoading?: boolean;
}

export function ChatTimeline({
  messages,
  conversation,
  onReplyMessage,
  isLoading,
}: ChatTimelineProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [playingAudioId, setPlayingAudioId] = useState<string | null>(null);

  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const formatMessageTime = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const renderStatusTicks = (status: string) => {
    switch (status) {
      case 'READ':
        return (
          <span title="Lida">
            <CheckCheck className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          </span>
        );
      case 'DELIVERED':
        return (
          <span title="Entregue">
            <CheckCheck className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          </span>
        );
      case 'SENT':
        return (
          <span title="Enviada">
            <Check className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          </span>
        );
      case 'FAILED':
        return (
          <span title="Falha no envio">
            <AlertCircle className="w-3.5 h-3.5 text-rose-500 shrink-0" />
          </span>
        );
      default:
        return (
          <span title="Pendente">
            <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          </span>
        );
    }
  };

  return (
    <div
      ref={scrollContainerRef}
      className="flex-1 overflow-y-auto p-4 space-y-3 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] bg-slate-950"
    >
      {isLoading ? (
        <div className="flex items-center justify-center h-full text-slate-500 text-xs">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mr-2" />
          Carregando mensagens...
        </div>
      ) : messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 gap-2">
          <div className="w-12 h-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-400">
            💬
          </div>
          <p className="text-xs">Nenhuma mensagem registrada nesta conversa.</p>
        </div>
      ) : (
        messages.map((msg) => {
          const isInbound = msg.direction === 'INBOUND';
          const isAi = msg.sent_by_ai;

          return (
            <div
              key={msg.id}
              className={`flex items-end gap-1.5 group ${
                isInbound ? 'justify-start' : 'justify-end'
              }`}
            >
              {/* Botão de Citar / Responder (Aparece no hover) */}
              {isInbound && (
                <button
                  onClick={() => onReplyMessage(msg)}
                  title="Responder a esta mensagem"
                  className="opacity-0 group-hover:opacity-100 p-1 rounded-full text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
                >
                  <Reply className="w-3.5 h-3.5" />
                </button>
              )}

              {/* Balão da Mensagem */}
              <div
                className={`max-w-[78%] md:max-w-[65%] rounded-2xl px-3.5 py-2 text-xs shadow-md relative leading-relaxed ${
                  isInbound
                    ? 'bg-slate-800 text-slate-100 rounded-bl-sm border border-slate-700/60'
                    : isAi
                    ? 'bg-gradient-to-br from-emerald-950/90 to-teal-950/90 text-emerald-100 rounded-br-sm border border-emerald-500/40 shadow-emerald-950/20'
                    : 'bg-emerald-900/80 text-white rounded-br-sm border border-emerald-700/50'
                }`}
              >
                {/* Header de Atendente ou IA */}
                {!isInbound && (
                  <div className="flex items-center gap-1 text-[10px] font-semibold mb-1 pb-1 border-b border-white/10">
                    {isAi ? (
                      <span className="flex items-center gap-1 text-cyan-300">
                        <Sparkles className="w-3 h-3 text-cyan-400" />
                        Assistente IA (Autônomo)
                      </span>
                    ) : (
                      <span className="text-emerald-300">
                        {msg.sender_name || 'Atendente'}
                      </span>
                    )}
                  </div>
                )}

                {/* Mensagem Citada (Reply To) */}
                {msg.quoted_message && (
                  <div className="mb-2 p-2 rounded bg-black/30 border-l-2 border-emerald-400 text-[10px] text-slate-300 truncate">
                    <span className="font-semibold block text-emerald-400 mb-0.5">Mensagem citada:</span>
                    <span>{msg.quoted_message.content}</span>
                  </div>
                )}

                {/* Conteúdo de Mídia (Áudio, Imagem ou Documento) */}
                {msg.media_type === 'image' && msg.media_url && (
                  <div className="mb-2 rounded-lg overflow-hidden border border-slate-700">
                    <img
                      src={msg.media_url}
                      alt="Anexo de imagem"
                      className="max-h-60 w-auto object-cover rounded"
                    />
                  </div>
                )}

                {msg.media_type === 'audio' && (
                  <div className="mb-2 p-2 rounded-lg bg-black/20 flex items-center gap-2">
                    <button
                      onClick={() =>
                        setPlayingAudioId(playingAudioId === msg.id ? null : msg.id)
                      }
                      className="w-8 h-8 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center shrink-0 shadow"
                    >
                      {playingAudioId === msg.id ? (
                        <Pause className="w-4 h-4 fill-current" />
                      ) : (
                        <Play className="w-4 h-4 fill-current ml-0.5" />
                      )}
                    </button>
                    <div className="flex-1">
                      <div className="h-1 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-emerald-400 ${
                            playingAudioId === msg.id ? 'w-2/3 animate-pulse' : 'w-0'
                          }`}
                        />
                      </div>
                      <span className="text-[10px] text-slate-400 mt-1 block">
                        {msg.media_duration ? `${msg.media_duration}s` : 'Áudio PTT'}
                      </span>
                    </div>
                  </div>
                )}

                {msg.media_type === 'document' && (
                  <div className="mb-2 p-2 rounded-lg bg-black/20 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-cyan-400 shrink-0" />
                    <span className="text-[11px] truncate">{msg.content || 'Documento Anexo'}</span>
                  </div>
                )}

                {/* Texto da Mensagem */}
                <p className="whitespace-pre-wrap break-words">{msg.content}</p>

                {/* Footer: Hora + Ticks */}
                <div className="flex items-center justify-end gap-1 mt-1 text-[10px] text-slate-400/80">
                  <span>{formatMessageTime(msg.timestamp)}</span>
                  {!isInbound && renderStatusTicks(msg.delivery_status)}
                </div>
              </div>

              {/* Botão de Citar / Responder para Outbound */}
              {!isInbound && (
                <button
                  onClick={() => onReplyMessage(msg)}
                  title="Responder a esta mensagem"
                  className="opacity-0 group-hover:opacity-100 p-1 rounded-full text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
                >
                  <Reply className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
