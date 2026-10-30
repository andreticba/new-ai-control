// frontend/src/hooks/use-window-focus-and-notification.ts | AI-Control Omnichannel v0.6.0 | 24-10-2026 20:10:00(GMT-04:00)

import { useState, useEffect, useRef, useCallback } from 'react';

export interface UseWindowFocusAndNotificationReturn {
  isWindowFocused: boolean;
  notifyNewMessage: (count?: number, preview?: string) => void;
  resetNotificationTitle: () => void;
  requestNotificationPermission: () => Promise<void>;
}

export function useWindowFocusAndNotification(): UseWindowFocusAndNotificationReturn {
  const [isWindowFocused, setIsWindowFocused] = useState<boolean>(() => {
    if (typeof document !== 'undefined') {
      return document.hasFocus() && !document.hidden;
    }
    return true;
  });

  const originalTitleRef = useRef<string>('AI-Control');

  useEffect(() => {
    if (typeof document === 'undefined') return;

    if (document.title && !document.title.startsWith('(')) {
      originalTitleRef.current = document.title;
    }

    const handleFocus = () => {
      setIsWindowFocused(true);
      if (typeof document !== 'undefined') {
        document.title = originalTitleRef.current;
      }
    };

    const handleBlur = () => {
      setIsWindowFocused(false);
    };

    const handleVisibilityChange = () => {
      const focused = !document.hidden && document.hasFocus();
      setIsWindowFocused(focused);
      if (focused) {
        document.title = originalTitleRef.current;
      }
    };

    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      if (typeof document !== 'undefined') {
        document.title = originalTitleRef.current;
      }
    };
  }, []);

  const notifyNewMessage = useCallback((count?: number, preview?: string) => {
    if (typeof window === 'undefined') return;

    // Alerta primário na aba e barra de tarefas do SO
    const prefix = count && count > 0 ? `(${count}) ` : '(Nova) ';
    document.title = `${prefix}Nova mensagem - ${originalTitleRef.current}`;

    // Alerta secundário desktop via Web Notification API
    if ('Notification' in window && Notification.permission === 'granted') {
      try {
        new Notification('WhatsApp - Nova Mensagem', {
          body: preview ? preview.slice(0, 100) : 'Você recebeu uma nova mensagem no Omnichannel.',
          icon: '/favicon.ico',
        });
      } catch (e) {
        console.warn('[useWindowFocusAndNotification] Falha ao disparar Notification:', e);
      }
    }
  }, []);

  const resetNotificationTitle = useCallback(() => {
    if (typeof document !== 'undefined') {
      document.title = originalTitleRef.current;
    }
  }, []);

  const requestNotificationPermission = useCallback(async () => {
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
      try {
        await Notification.requestPermission();
      } catch (e) {
        console.warn('[useWindowFocusAndNotification] Falha ao solicitar permissão de notificação:', e);
      }
    }
  }, []);

  return {
    isWindowFocused,
    notifyNewMessage,
    resetNotificationTitle,
    requestNotificationPermission,
  };
}
