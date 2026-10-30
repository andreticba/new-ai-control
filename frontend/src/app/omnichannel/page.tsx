// frontend/src/app/omnichannel/page.tsx | AI-Control Omnichannel v0.6.0 | 21-10-2026 00:12:00(GMT-04:00)
'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { MessageSquare } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useOmnichannel } from '@/hooks/use-omnichannel';
import { useOmnichannelSocket } from '@/hooks/use-omnichannel-socket';
import { useColumnResize } from '@/hooks/use-column-resize';
import {
  NavRail, OmnichannelHeader, ColumnSplitter, ConversationList,
  ChatHeader, ChatTimeline, ChatInput, CopilotBanner, ContactDrawer, WhatsAppConnectionModal,
} from '@/components/omnichannel';
import { useWhatsAppInstance } from '@/hooks/use-whatsapp-instance';
import { useWindowFocusAndNotification } from '@/hooks/use-window-focus-and-notification';
import type { OmnichannelMessage, ConversationFilterTab } from '@/types/omnichannel';

export default function OmnichannelPage() {
  const router = useRouter();
  const { user, isAuthenticated, isInitialized } = useAuth();
  const orgId = user?.primary_organization?.id;
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTab, setFilterTab] = useState<ConversationFilterTab>('all');
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [replyingTo, setReplyingTo] = useState<OmnichannelMessage | null>(null);
  const [insertedText, setInsertedText] = useState('');
  const [isWhatsAppModalOpen, setIsWhatsAppModalOpen] = useState(false);
  const { status: whatsAppStatus } = useWhatsAppInstance(orgId);
  const isWhatsAppConnected = whatsAppStatus.connected;
  const sidebar = useColumnResize({ storageKey: 'omnichannel_sidebar_width', defaultWidth: 340, minWidth: 240, maxWidth: 600, direction: 'left', offset: 56 });
  const drawer = useColumnResize({ storageKey: 'omnichannel_drawer_width', defaultWidth: 340, minWidth: 260, maxWidth: 650, direction: 'right' });
  const { isConnected } = useOmnichannelSocket({ organizationId: orgId, activeConversationId: selectedConversationId });
  const { isWindowFocused, notifyNewMessage, requestNotificationPermission } = useWindowFocusAndNotification();
  const { useConversationsList, useActiveMessages, useActiveDrafts, takeoverMutation, returnToAiMutation, sendMessageMutation, approveDraftMutation, discardDraftMutation, markReadMutation } = useOmnichannel(selectedConversationId);
  const { data: conversations = [], isLoading: isLoadingConversations } = useConversationsList(filterTab, searchQuery);
  const activeConversation = conversations.find((c) => c.id === selectedConversationId) || null;
  const { data: messages = [], isLoading: isLoadingMessages } = useActiveMessages(selectedConversationId);
  const { data: activeDrafts = [] } = useActiveDrafts(selectedConversationId);
  const activeDraft = activeDrafts.length > 0 ? activeDrafts[0] : null;

  const readDelayTimerRef = useRef<NodeJS.Timeout | null>(null);

  const handleOpenWhatsAppModal = useCallback(() => setIsWhatsAppModalOpen(true), []);
  const handleCloseWhatsAppModal = useCallback(() => setIsWhatsAppModalOpen(false), []);

  useEffect(() => { if (isInitialized && !isAuthenticated) router.push('/login'); }, [isInitialized, isAuthenticated, router]);

  // Solicita permissão de notificações discretamente na montagem
  useEffect(() => {
    requestNotificationPermission();
  }, [requestNotificationPermission]);

  // Alerta na barra de tarefas / aba quando o foco estiver fora da tela e houver mensagens não lidas
  const totalUnread = conversations.reduce((acc, c) => acc + (c.unread_count || 0), 0);
  useEffect(() => {
    if (!isWindowFocused && totalUnread > 0) {
      notifyNewMessage(totalUnread, activeConversation?.last_message?.content);
    }
  }, [isWindowFocused, totalUnread, notifyNewMessage, activeConversation?.last_message?.content]);

  // Gestão de leitura com delay perceptivo de 1.5s acoplado ao foco ativo da janela
  useEffect(() => {
    if (readDelayTimerRef.current) {
      clearTimeout(readDelayTimerRef.current);
      readDelayTimerRef.current = null;
    }

    if (activeConversation && activeConversation.unread_count > 0 && isWindowFocused) {
      readDelayTimerRef.current = setTimeout(() => {
        markReadMutation.mutate(activeConversation.id);
        readDelayTimerRef.current = null;
      }, 1500);
    }

    return () => {
      if (readDelayTimerRef.current) {
        clearTimeout(readDelayTimerRef.current);
        readDelayTimerRef.current = null;
      }
    };
  }, [activeConversation?.id, activeConversation?.unread_count, isWindowFocused]);

  return (
    <div className="h-dvh w-screen overflow-hidden flex bg-slate-950 text-slate-100 font-sans antialiased">
      <NavRail user={user} isWhatsAppConnected={isWhatsAppConnected} onOpenWhatsAppModal={handleOpenWhatsAppModal} />
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        <OmnichannelHeader organizationName={user?.primary_organization?.name || 'Organização Padrão'} isConnected={isConnected} isWhatsAppConnected={isWhatsAppConnected} onOpenWhatsAppModal={handleOpenWhatsAppModal} />
        <div className="flex-1 flex overflow-hidden min-h-0 relative">
          <aside style={{ width: `${sidebar.width}px` }} className="border-r border-slate-800 bg-slate-900/40 flex flex-col shrink-0 h-full overflow-hidden select-none">
            <ConversationList conversations={conversations} activeConversationId={selectedConversationId} onSelectConversation={(id) => { setSelectedConversationId(id); setReplyingTo(null); setInsertedText(''); }} isLoading={isLoadingConversations} filterTab={filterTab} onFilterChange={setFilterTab} searchQuery={searchQuery} onSearchChange={setSearchQuery} />
          </aside>
          <ColumnSplitter isDragging={sidebar.isDragging} onMouseDown={sidebar.startDragging} theme="cyan" />
          <main className="flex-1 flex flex-col h-full overflow-hidden min-w-0 bg-slate-950/60 relative">
            {activeConversation ? (
              <>
                <ChatHeader conversation={activeConversation} onTakeover={() => takeoverMutation.mutate(activeConversation.id)} onReturnToAi={() => returnToAiMutation.mutate(activeConversation.id)} isTakeoverPending={takeoverMutation.isPending} isReturnPending={returnToAiMutation.isPending} onToggleDrawer={() => setIsDrawerOpen((prev) => !prev)} isDrawerOpen={isDrawerOpen} />
                <CopilotBanner draft={activeDraft} onApprove={(id) => approveDraftMutation.mutate({ draftId: id })} onInsert={setInsertedText} onDiscard={(id) => discardDraftMutation.mutate(id)} isApproving={approveDraftMutation.isPending} />
                <ChatTimeline messages={messages} conversation={activeConversation} onReplyMessage={setReplyingTo} isLoading={isLoadingMessages} />
                <ChatInput
                  onSendMessage={async (content, quotedId) => {
                    await sendMessageMutation.mutateAsync({
                      conversation_id: activeConversation.id,
                      content,
                      quoted_message_id: quotedId,
                    });
                    setReplyingTo(null);
                    setInsertedText('');
                  }}
                  isSending={sendMessageMutation.isPending}
                  replyingTo={replyingTo}
                  onCancelReply={() => setReplyingTo(null)}
                  insertedText={insertedText}
                />
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center select-none">
                <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mb-4 text-slate-500 shadow-inner"><MessageSquare className="w-8 h-8 opacity-40 text-cyan-400" /></div>
                <h3 className="text-base font-semibold text-slate-200 mb-1">Nenhuma conversa selecionada</h3>
                <p className="text-xs text-slate-500 max-w-sm">Selecione um contato na lista lateral para iniciar o monitoramento em tempo real.</p>
              </div>
            )}
          </main>
          {isDrawerOpen && activeConversation && (
            <>
              <ColumnSplitter isDragging={drawer.isDragging} onMouseDown={drawer.startDragging} theme="emerald" />
              <ContactDrawer conversation={activeConversation} isOpen={isDrawerOpen} onClose={() => setIsDrawerOpen(false)} width={drawer.width} />
            </>
          )}
        </div>
      </div>
      <WhatsAppConnectionModal isOpen={isWhatsAppModalOpen} onClose={handleCloseWhatsAppModal} orgId={orgId} />
    </div>
  );
}
