// frontend/src/components/Providers.tsx | AI-Control v0.0.1 | 12-10-2026 10:00(GMT-04:00)
'use client';

import React, { useEffect, useState } from 'react';
import { Provider } from 'react-redux';
import { Toaster } from 'sonner';
import { store } from '@/store';
import { initializeAuth, STORAGE_KEYS } from '@/store/authSlice';
import api from '@/lib/api';

function AuthHydrator({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS);
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH);

    if (accessToken && refreshToken) {
      // Hidrata tokens na store e valida usuário via /users/me/
      store.dispatch(
        initializeAuth({
          accessToken,
          refreshToken,
          user: null,
        })
      );

      api
        .get('/api/v1/users/me/')
        .then((res) => {
          store.dispatch(
            initializeAuth({
              accessToken,
              refreshToken,
              user: res.data,
            })
          );
        })
        .catch(() => {
          // Token expirado ou inválido; interceptor tentará refresh ou limpará
        })
        .finally(() => {
          setMounted(true);
        });
    } else {
      store.dispatch(
        initializeAuth({
          accessToken: null,
          refreshToken: null,
          user: null,
        })
      );
      setMounted(true);
    }
  }, []);

  return <>{children}</>;
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <AuthHydrator>
        {children}
        <Toaster
          position="top-right"
          theme="dark"
          richColors
          closeButton
          toastOptions={{
            style: {
              background: '#0f172a',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#f8fafc',
            },
          }}
        />
      </AuthHydrator>
    </Provider>
  );
}
