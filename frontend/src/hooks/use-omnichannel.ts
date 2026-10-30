// frontend/src/hooks/use-omnichannel.ts | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:53:00(GMT-04:00)

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { toast } from 'sonner';
import {
  OmnichannelConversation,
  OmnichannelMessage,
  CopilotDraft,
  ConversationFilterTab,
} from '@/types/omnichannel';

export const OMNICHANNEL_KEYS = {
  all: ['omnichannel'] as const,
  conversations: (filterTab?: ConversationFilterTab, search?: string) =>
    [...OMNICHANNEL_KEYS.all, 'conversations', filterTab || 'all', search || ''] as const,
  conversation: (id?: string | null) => [...OMNICHANNEL_KEYS.all, 'conversation', id] as const,
  messages: (conversationId?: string | null) =>
    [...OMNICHANNEL_KEYS.all, 'messages', conversationId] as const,
  drafts: (conversationId?: string | null) =>
    [...OMNICHANNEL_KEYS.all, 'drafts', conversationId] as const,
};

export function useOmnichannel(activeConversationId?: string | null) {
  const queryClient = useQueryClient();

  // 1. Listar conversas com filtros e busca
  const useConversationsList = (filterTab: ConversationFilterTab = 'all', search: string = '') => {
    return useQuery<OmnichannelConversation[]>({
      queryKey: OMNICHANNEL_KEYS.conversations(filterTab, search),
      queryFn: async () => {
        const params: Record<string, string> = {};
        if (filterTab && filterTab !== 'all') params.filter = filterTab;
        if (search && search.trim()) params.search = search.trim();

        const res = await api.get('/api/v1/omnichannel/conversations/', { params });
        const data = res.data;
        return Array.isArray(data) ? data : data.results || [];
      },
      refetchInterval: 15000, // Fallback leve se WebSocket oscilar
    });
  };

  // 2. Timeline de mensagens da conversa ativa
  const useActiveMessages = (conversationId?: string | null) => {
    return useQuery<OmnichannelMessage[]>({
      queryKey: OMNICHANNEL_KEYS.messages(conversationId),
      queryFn: async () => {
        if (!conversationId) return [];
        const res = await api.get(`/api/v1/omnichannel/conversations/${conversationId}/messages/`);
        const data = res.data;
        return Array.isArray(data) ? data : data.results || [];
      },
      enabled: !!conversationId,
    });
  };

  // 3. Drafts de Copiloto pendentes para a conversa
  const useActiveDrafts = (conversationId?: string | null) => {
    return useQuery<CopilotDraft[]>({
      queryKey: OMNICHANNEL_KEYS.drafts(conversationId),
      queryFn: async () => {
        if (!conversationId) return [];
        const res = await api.get('/api/v1/omnichannel/copilot-drafts/');
        const data = res.data;
        const allDrafts: CopilotDraft[] = Array.isArray(data) ? data : data.results || [];
        return allDrafts.filter(
          (d) => d.conversation_id === conversationId && d.status === 'PENDING'
        );
      },
      enabled: !!conversationId,
    });
  };

  // 4. Mutação: Assumir atendimento (Takeover)
  const takeoverMutation = useMutation({
    mutationFn: async (conversationId: string) => {
      const res = await api.post(`/api/v1/omnichannel/conversations/${conversationId}/takeover/`);
      return res.data;
    },
    onSuccess: (_, conversationId) => {
      toast.success('Atendimento assumido com sucesso. IA silenciada.');
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
    onError: (err: any) => {
      toast.error('Erro ao assumir atendimento: ' + (err?.response?.data?.error || err.message));
    },
  });

  // 5. Mutação: Devolver atendimento para IA
  const returnToAiMutation = useMutation({
    mutationFn: async (conversationId: string) => {
      const res = await api.post(`/api/v1/omnichannel/conversations/${conversationId}/return-to-ai/`);
      return res.data;
    },
    onSuccess: (_, conversationId) => {
      toast.info('Atendimento devolvido para a IA.');
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
    onError: (err: any) => {
      toast.error('Erro ao devolver para IA: ' + (err?.response?.data?.error || err.message));
    },
  });

  // 6. Mutação: Marcar conversa como lida
  const markReadMutation = useMutation({
    mutationFn: async (conversationId: string) => {
      const res = await api.post(`/api/v1/omnichannel/conversations/${conversationId}/mark-read/`);
      return res.data;
    },
    onMutate: async (conversationId: string) => {
      // Atualização otimista imediata no cache de listas de conversas
      queryClient.setQueriesData({ queryKey: [...OMNICHANNEL_KEYS.all, 'conversations'] }, (old: any) => {
        if (!old || !Array.isArray(old)) return old;
        return old.map((conv: OmnichannelConversation) => {
          if (conv.id === conversationId) {
            return { ...conv, unread_count: 0 };
          }
          return conv;
        });
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
    onError: () => {
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
  });

  // 7. Mutação: Enviar mensagem outbound manual
  const sendMessageMutation = useMutation({
    mutationFn: async (payload: {
      conversation_id: string;
      content: string;
      quoted_message_id?: string | null;
      media_type?: string;
      media_url?: string;
    }) => {
      const res = await api.post('/api/v1/omnichannel/messages/', payload);
      return res.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: OMNICHANNEL_KEYS.messages(variables.conversation_id),
      });
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
    onError: (err: any) => {
      toast.error('Falha no envio da mensagem: ' + (err?.response?.data?.error || err.message));
    },
  });

  // 8. Mutação: Aprovar sugestão do Copiloto
  const approveDraftMutation = useMutation({
    mutationFn: async ({
      draftId,
      editedContent,
    }: {
      draftId: string;
      editedContent?: string;
    }) => {
      const res = await api.post(`/api/v1/omnichannel/copilot-drafts/${draftId}/approve/`, {
        edited_content: editedContent,
      });
      return res.data;
    },
    onSuccess: () => {
      toast.success('Sugestão aprovada e enviada via WhatsApp!');
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
    onError: (err: any) => {
      toast.error('Erro ao aprovar sugestão: ' + (err?.response?.data?.error || err.message));
    },
  });

  // 9. Mutação: Descartar sugestão do Copiloto
  const discardDraftMutation = useMutation({
    mutationFn: async (draftId: string) => {
      const res = await api.post(`/api/v1/omnichannel/copilot-drafts/${draftId}/discard/`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
    },
  });

  return {
    useConversationsList,
    useActiveMessages,
    useActiveDrafts,
    takeoverMutation,
    returnToAiMutation,
    markReadMutation,
    sendMessageMutation,
    approveDraftMutation,
    discardDraftMutation,
  };
}
