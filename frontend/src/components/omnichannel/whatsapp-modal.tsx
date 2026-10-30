// frontend/src/components/omnichannel/whatsapp-modal.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:52:00(GMT-04:00)
'use client';

import React, { useEffect, useRef } from 'react';
import {
  QrCode,
  Wifi,
  WifiOff,
  RefreshCw,
  LogOut,
  X,
  CheckCircle2,
  Smartphone,
} from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useWhatsAppInstance } from '@/hooks/use-whatsapp-instance';

interface WhatsAppModalProps {
  isOpen: boolean;
  onClose: () => void;
  orgId?: string;
  onConnectionChange?: (connected: boolean) => void;
}

export function WhatsAppConnectionModal({
  isOpen,
  onClose,
  orgId,
  onConnectionChange,
}: WhatsAppModalProps) {
  const queryClient = useQueryClient();
  const {
    status,
    isLoading,
    isDisconnecting,
    refreshStatus,
    generateQrCode,
    disconnectInstance,
  } = useWhatsAppInstance(orgId);

  const hadQrCodeRef = useRef<boolean>(false);

  // Rastreia se o modal exibiu ativamente um QR Code para pareamento
  useEffect(() => {
    if (isOpen) {
      if (status.qrCodeBase64) {
        hadQrCodeRef.current = true;
      }
    } else {
      hadQrCodeRef.current = false;
    }
  }, [isOpen, status.qrCodeBase64]);

  // Sincroniza o estado de conexão com o layout pai se houve mudança
  useEffect(() => {
    if (onConnectionChange) {
      onConnectionChange(status.connected);
    }
  }, [status.connected, onConnectionChange]);

  // Auto-fechamento APENAS se o usuário estava escaneando um QR Code e o pareamento acabou de ser concluído
  useEffect(() => {
    if (isOpen && status.connected && hadQrCodeRef.current) {
      const timer = setTimeout(() => {
        hadQrCodeRef.current = false;
        onClose();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [status.connected, isOpen, onClose]);

  // Atualiza o status e mantém polling reativo a cada 3s apenas enquanto desconectado
  useEffect(() => {
    if (!isOpen) return;

    refreshStatus();

    if (!status.connected) {
      const interval = setInterval(() => {
        refreshStatus();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isOpen, status.connected, refreshStatus]);

  const handleDisconnect = async () => {
    if (!window.confirm('Deseja realmente desconectar a instância do WhatsApp desta organização?')) {
      return;
    }
    const success = await disconnectInstance();
    if (success && onConnectionChange) {
      onConnectionChange(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header do Modal */}
        <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Conexão do WhatsApp</h3>
              <p className="text-[11px] text-slate-400 font-mono">
                Instância: {status.instanceName || 'ai_control_default'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Conteúdo Principal */}
        <div className="p-6 flex flex-col items-center text-center space-y-5">
          {/* Badge de Status */}
          <div
            className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border ${
              status.connected
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}
          >
            {status.connected ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-emerald-400" />
                <span>WhatsApp Conectado e Operacional</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-amber-400" />
                <span>Aguardando Conexão / Pareamento</span>
              </>
            )}
          </div>

          {/* Renderização Condicional: Conectado vs Desconectado */}
          {status.connected ? (
            <div className="w-full py-4 space-y-4">
              <div className="w-20 h-20 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-inner">
                <CheckCircle2 className="w-10 h-10" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-slate-200">
                  Instância pareada via Evolution API
                </p>
                <p className="text-xs text-slate-400 max-w-xs mx-auto">
                  As mensagens estão sendo recebidas e enviadas normalmente com isolamento por organização.
                </p>
              </div>

              {/* Botão de Desconexão */}
              <button
                onClick={handleDisconnect}
                disabled={isDisconnecting}
                className="w-full mt-2 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs font-semibold transition active:scale-98 disabled:opacity-50"
              >
                <LogOut className="w-4 h-4" />
                {isDisconnecting ? 'Desconectando...' : 'Desconectar WhatsApp'}
              </button>
            </div>
          ) : (
            <div className="w-full space-y-4">
              {/* Box do QR Code */}
              <div className="w-64 h-64 mx-auto p-3 rounded-2xl bg-white border border-slate-700 flex items-center justify-center shadow-lg relative">
                {isLoading ? (
                  <div className="flex flex-col items-center gap-2 text-slate-700">
                    <RefreshCw className="w-8 h-8 animate-spin text-emerald-600" />
                    <span className="text-xs font-medium">Carregando QR Code...</span>
                  </div>
                ) : status.qrCodeBase64 ? (
                  <img
                    src={
                      status.qrCodeBase64.startsWith('data:image')
                        ? status.qrCodeBase64
                        : `data:image/png;base64,${status.qrCodeBase64}`
                    }
                    alt="WhatsApp QR Code"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="flex flex-col items-center gap-2 text-slate-500 p-4">
                    <QrCode className="w-12 h-12 stroke-[1.5] text-slate-400" />
                    <span className="text-xs font-medium">Clique abaixo para gerar o QR Code</span>
                  </div>
                )}
              </div>

              {/* Instruções de Escaneamento */}
              <div className="text-left bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 space-y-1.5 text-xs text-slate-400 font-sans">
                <p className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-cyan-400" />
                  Como conectar:
                </p>
                <ol className="list-decimal list-inside space-y-1 text-[11px] leading-relaxed">
                  <li>Abra o WhatsApp no seu smartphone</li>
                  <li>Toque em <span className="text-slate-200">Aparelhos Conectados</span></li>
                  <li>Aponte a câmera para o QR Code acima</li>
                </ol>
              </div>

              {/* Botões de Ação */}
              <div className="flex items-center gap-2.5 pt-1">
                <button
                  onClick={generateQrCode}
                  disabled={isLoading}
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-600/20 transition active:scale-98 disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                  {status.qrCodeBase64 ? 'Atualizar QR Code' : 'Gerar QR Code'}
                </button>
                <button
                  onClick={refreshStatus}
                  disabled={isLoading}
                  title="Checar status de conexão"
                  className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
