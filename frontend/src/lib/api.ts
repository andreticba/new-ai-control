// frontend/src/lib/api.ts | AI-Control v0.0.1 | 12-10-2026 09:55(GMT-04:00)

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { store } from '@/store';
import { logout, setCredentials, STORAGE_KEYS } from '@/store/authSlice';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor: Injeta token Bearer
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    let token = store.getState().auth.accessToken;

    if (!token && typeof window !== 'undefined') {
      token = localStorage.getItem(STORAGE_KEYS.ACCESS);
    }

    if (token) {
      config.headers.set('Authorization', `Bearer ${token}`);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Renovação transparente e fila assíncrona isRefreshing
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (!originalRequest) {
      return Promise.reject(error);
    }

    const isAuthRoute =
      originalRequest.url?.includes('/api/v1/auth/token/') ||
      originalRequest.url?.includes('/api/v1/auth/token/refresh/');

    if (error.response?.status === 401 && !isAuthRoute) {
      if (originalRequest._retry) {
        store.dispatch(logout());
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.set('Authorization', `Bearer ${token}`);
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      let refreshToken = store.getState().auth.refreshToken;
      if (!refreshToken && typeof window !== 'undefined') {
        refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH);
      }

      if (!refreshToken) {
        isRefreshing = false;
        processQueue(error, null);
        store.dispatch(logout());
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      try {
        const refreshResponse = await axios.post(`${API_BASE_URL}/api/v1/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = refreshResponse.data.access;
        const newRefreshToken = refreshResponse.data.refresh || refreshToken;

        store.dispatch(
          setCredentials({
            accessToken: newAccessToken,
            refreshToken: newRefreshToken,
            user: store.getState().auth.user || undefined,
          })
        );

        processQueue(null, newAccessToken);
        originalRequest.headers.set('Authorization', `Bearer ${newAccessToken}`);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        store.dispatch(logout());
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
