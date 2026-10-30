// frontend/src/hooks/use-omnichannel-socket.ts | AI-Control Omnichannel v0.6.0 | 20-10-2026 19:54:00(GMT-04:00)

import { useEffect, useRef, useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { store } from '@/store';
import { STORAGE_KEYS } from '@/store/authSlice';
import { OMNICHANNEL_KEYS } from '@/hooks/use-omnichannel';
import { toast } from 'sonner';

interface UseOmnichannelSocketProps {
  organizationId?: string | null;
  activeConversationId?: string | null;
}

export function useOmnichannelSocket({
  organizationId,
  activeConversationId,
}: UseOmnichannelSocketProps) {
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const activeConversationIdRef = useRef(activeConversationId);
  activeConversationIdRef.current = activeConversationId;

  const connect = useCallback(() => {
    if (typeof window === 'undefined') return;

    let token = store.getState().auth.accessToken;
    if (!token) {
      token = localStorage.getItem(STORAGE_KEYS.ACCESS);
    }

    if (!token) {
      return;
    }

    // Resolve o endpoint do WebSocket apontando para o backend Daphne (porta 8000 por padrão)
    let wsHost = process.env.NEXT_PUBLIC_WS_URL;
    let wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    if (!wsHost) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      try {
        const parsedApi = new URL(apiUrl);
        wsProtocol = parsedApi.protocol === 'https:' ? 'wss:' : 'ws:';
        wsHost = parsedApi.host;
      } catch {
        wsHost = 'localhost:8000';
      }
    }
    
    // Constrói URL com token e organização
    const url = new URL(`${wsProtocol}//${wsHost}/ws/omnichannel/`);
    url.searchParams.set('token', token);
    if (organizationId) {
      url.searchParams.set('org_id', organizationId);
    }

    try {
      const ws = new WebSocket(url.toString());
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;

        // Inicia heartbeat periódico a cada 30 segundos
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event: eventType, data } = payload;

          if (eventType === 'pong') return;

          switch (eventType) {
            case 'conversation.message.new':
              if (data?.conversation_id) {
                queryClient.invalidateQueries({
                  queryKey: OMNICHANNEL_KEYS.messages(data.conversation_id),
                });
              }
              queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
              break;

            case 'conversation.message.status_updated':
              if (data?.conversation_id) {
                queryClient.setQueryData<any[]>(
                  OMNICHANNEL_KEYS.messages(data.conversation_id),
                  (old) => {
                    if (!old || !Array.isArray(old)) return old;
                    return old.map((m) => {
                      if (
                        (data.message_id && m.id === data.message_id) ||
                        (data.external_id && m.external_id === data.external_id)
                      ) {
                        return {
                          ...m,
                          delivery_status: data.delivery_status || m.delivery_status,
                          is_read: data.is_read !== undefined ? data.is_read : m.is_read,
                        };
                      }
                      return m;
                    });
                  }
                );
                queryClient.invalidateQueries({
                  queryKey: OMNICHANNEL_KEYS.messages(data.conversation_id),
                });
              }
              queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
              break;

            case 'copilot.draft.generated':
              if (data?.conversation_id) {
                queryClient.invalidateQueries({
                  queryKey: OMNICHANNEL_KEYS.drafts(data.conversation_id),
                });
                if (activeConversationIdRef.current === data.conversation_id) {
                  toast.info('💡 Nova sugestão do Copiloto de IA disponível!');
                }
              }
              break;

            case 'whatsapp.qrcode.updated':
            case 'qrcode.updated':
              if (data?.qrcode_base64) {
                queryClient.setQueriesData({ queryKey: ['whatsapp-instance'] }, (old: any) => {
                  if (!old) return old;
                  return {
                    ...old,
                    state: 'connecting',
                    connected: false,
                    qrCodeBase64: data.qrcode_base64,
                  };
                });
              }
              queryClient.invalidateQueries({ queryKey: ['whatsapp-instance'] });
              break;

            case 'whatsapp.connection.updated':
            case 'connection.update':
              if (data && typeof data.connected === 'boolean') {
                queryClient.setQueriesData({ queryKey: ['whatsapp-instance'] }, (old: any) => {
                  if (!old) return old;
                  return {
                    ...old,
                    state: data.state || (data.connected ? 'open' : 'close'),
                    connected: data.connected,
                    qrCodeBase64: data.connected ? null : old.qrCodeBase64,
                  };
                });
              }
              queryClient.invalidateQueries({ queryKey: ['whatsapp-instance'] });
              queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
              break;

            case 'conversation.status.updated':
              queryClient.invalidateQueries({ queryKey: OMNICHANNEL_KEYS.all });
              break;

            default:
              break;
          }
        } catch (e) {
          console.warn('[useOmnichannelSocket] Erro ao processar mensagem recebida:', e);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }

        // Não reconectar se fechado intencionalmente ou por não autorizado
        if (event.code === 4401 || event.code === 4403) {
          console.warn(`[useOmnichannelSocket] Conexão recusada com código ${event.code}.`);
          return;
        }

        // Exponential backoff: min 1s, max 10s
        const delay = Math.min(1000 * Math.pow(1.5, reconnectAttemptsRef.current), 10000);
        reconnectAttemptsRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, delay);
      };

      ws.onerror = () => {
        // O evento de erro do WebSocket não expõe detalhes sensíveis por segurança (W3C standard).
        // A desconexão e o reconnect backoff são orquestrados determinísticamente pelo ws.onclose.
        console.warn('[useOmnichannelSocket] Conexão WebSocket fechada ou backend indisponível. Aguardando reconexão...');
      };
    } catch (err) {
      console.error('[useOmnichannelSocket] Falha ao instanciar WebSocket:', err);
    }
  }, [organizationId, queryClient]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected };
}
