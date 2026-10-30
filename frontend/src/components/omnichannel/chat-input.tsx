// frontend/src/components/omnichannel/chat-input.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:55:00(GMT-04:00)

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, X, CornerDownLeft, Smile } from 'lucide-react';
import { OmnichannelMessage } from '@/types/omnichannel';

interface ChatInputProps {
  onSendMessage: (content: string, quotedMessageId?: string | null) => Promise<unknown> | void;
  isSending?: boolean;
  replyingTo?: OmnichannelMessage | null;
  onCancelReply?: () => void;
  insertedText?: string;
}

export function ChatInput({
  onSendMessage,
  isSending,
  replyingTo,
  onCancelReply,
  insertedText,
}: ChatInputProps) {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Se o Copiloto inserir texto no campo
  useEffect(() => {
    if (insertedText) {
      setContent(insertedText);
      textareaRef.current?.focus();
    }
  }, [insertedText]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const textToSend = content.trim();
    if (!textToSend || isSending) return;

    try {
      await onSendMessage(textToSend, replyingTo?.id || null);
      setContent('');
      if (onCancelReply) onCancelReply();

      // Redefine altura do textarea
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch {
      // D2 / SC-007: Falha atômica. Preserva o texto digitado na caixa de entrada
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setContent(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <div className="p-3 border-t border-slate-800 bg-slate-900/90 backdrop-blur shrink-0 select-none">
      {/* Visualização de Resposta / Citação (Quoted Message) */}
      {replyingTo && (
        <div className="mb-2 p-2 rounded-lg bg-slate-800/80 border-l-4 border-emerald-500 flex items-center justify-between text-xs animate-in fade-in">
          <div className="min-w-0 flex flex-col">
            <span className="font-semibold text-emerald-400 text-[10px]">
              Respondendo a {replyingTo.direction === 'INBOUND' ? 'Cliente' : 'Atendente'}
            </span>
            <span className="text-slate-300 truncate">{replyingTo.content}</span>
          </div>
          <button
            onClick={onCancelReply}
            className="p-1 rounded text-slate-400 hover:text-slate-200 transition"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Caixa de Digitação */}
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <button
          type="button"
          title="Anexar arquivo ou mídia"
          className="p-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition shrink-0"
        >
          <Paperclip className="w-4 h-4" />
        </button>

        <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 focus-within:border-emerald-500 focus-within:ring-1 focus-within:ring-emerald-500 transition">
          <textarea
            ref={textareaRef}
            rows={1}
            value={content}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Digite uma mensagem... (Enter para enviar, Shift+Enter para quebra)"
            className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none resize-none max-h-32 leading-relaxed"
          />
        </div>

        <button
          type="submit"
          disabled={!content.trim() || isSending}
          className="p-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition disabled:opacity-40 disabled:hover:bg-emerald-500 shrink-0 shadow"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
