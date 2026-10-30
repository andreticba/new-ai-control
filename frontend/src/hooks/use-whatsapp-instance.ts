// use-whatsapp-instance.ts | AI-Control Omnichannel v0.6.0 | 22-10-2026 21:50:00(GMT-04:00)
import { useCallback, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { toast } from 'sonner';

export interface WhatsAppInstanceStatus {
  instanceName: string;
  state: 'open' | 'connecting' | 'close' | 'unknown';
  connected: boolean;
  qrCodeBase64: string | null;
}

export interface UseWhatsAppInstanceReturn {
  status: WhatsAppInstanceStatus;
  isLoading: boolean;
  isDisconnecting: boolean;
  /** Consulta o status atual da instância e atualiza o estado */
  refreshStatus: () => Promise<void>;
  /** Gera um novo QR Code para pareamento */
  generateQrCode: () => Promise<void>;
  /** Desconecta (logout) a instância da Evolution API */
  disconnectInstance: () => Promise<boolean>;
}

export const WHATSAPP_INSTANCE_KEY = ['whatsapp-instance'];

export function useWhatsAppInstance(orgId?: string): UseWhatsAppInstanceReturn {
  const queryClient = useQueryClient();
  const queryKey = ['whatsapp-instance', orgId || 'default'];
  const [isDisconnecting, setIsDisconnecting] = useState<boolean>(false);
  const [isGeneratingQr, setIsGeneratingQr] = useState<boolean>(false);

  const { data: status = {
    instanceName: '',
    state: 'unknown',
    connected: false,
    qrCodeBase64: null,
  }, isLoading } = useQuery<WhatsAppInstanceStatus>({
    queryKey,
    queryFn: async () => {
      const params = orgId ? { org_id: orgId } : {};
      const res = await api.get('/api/v1/omnichannel/instance/', { params });
      return {
        instanceName: res.data.instance_name || '',
        state: res.data.state || 'close',
        connected: Boolean(res.data.connected),
        qrCodeBase64: res.data.qrcode_base64 || null,
      };
    },
    staleTime: 5000,
    refetchOnWindowFocus: true,
  });

  const refreshStatus = useCallback(async () => {
    await queryClient.invalidateQueries({ queryKey: WHATSAPP_INSTANCE_KEY });
  }, [queryClient]);

  const generateQrCode = useCallback(async () => {
    try {
      setIsGeneratingQr(true);
      const params = orgId ? { org_id: orgId } : {};
      const res = await api.post('/api/v1/omnichannel/instance/', {}, { params });
      const connected = Boolean(res.data.connected);
      const qrCode = res.data.qrcode_base64 || null;

      const newStatus: WhatsAppInstanceStatus = {
        instanceName: res.data.instance_name || '',
        state: res.data.state || (connected ? 'open' : 'connecting'),
        connected,
        qrCodeBase64: qrCode,
      };

      queryClient.setQueryData(queryKey, newStatus);
      queryClient.setQueriesData({ queryKey: WHATSAPP_INSTANCE_KEY }, newStatus);

      if (qrCode) {
        toast.info('Novo QR Code gerado. Escaneie pelo WhatsApp.');
      } else if (connected) {
        toast.success('WhatsApp já está conectado!');
      }
    } catch (err: any) {
      const errorMsg = err?.response?.data?.error || err?.message || 'Falha ao gerar QR Code';
      toast.error(`Erro ao gerar QR Code: ${errorMsg}`);
    } finally {
      setIsGeneratingQr(false);
    }
  }, [orgId, queryClient, queryKey]);

  const disconnectInstance = useCallback(async (): Promise<boolean> => {
    try {
      setIsDisconnecting(true);
      const params = orgId ? { org_id: orgId } : {};
      await api.delete('/api/v1/omnichannel/instance/', { params });
      const closedStatus: WhatsAppInstanceStatus = {
        instanceName: '',
        state: 'close',
        connected: false,
        qrCodeBase64: null,
      };
      queryClient.setQueryData(queryKey, closedStatus);
      queryClient.setQueriesData({ queryKey: WHATSAPP_INSTANCE_KEY }, closedStatus);
      await queryClient.invalidateQueries({ queryKey: WHATSAPP_INSTANCE_KEY });
      toast.success('WhatsApp desconectado com sucesso.');
      return true;
    } catch (err: any) {
      const errorMsg = err?.response?.data?.error || err?.message || 'Falha ao desconectar';
      toast.error(`Erro ao desconectar WhatsApp: ${errorMsg}`);
      return false;
    } finally {
      setIsDisconnecting(false);
    }
  }, [orgId, queryClient, queryKey]);

  return {
    status,
    isLoading: isLoading || isGeneratingQr,
    isDisconnecting,
    refreshStatus,
    generateQrCode,
    disconnectInstance,
  };
}
