// frontend/src/store/authSlice.ts | AI-Control v0.0.1 | 12-10-2026 09:55(GMT-04:00)

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UserProfile } from '@/types/auth';

export const STORAGE_KEYS = {
  ACCESS: '@ai-control:access_token',
  REFRESH: '@ai-control:refresh_token',
};

export interface AuthState {
  user: UserProfile | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
}

const initialState: AuthState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isInitialized: false,
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user?: UserProfile; accessToken: string; refreshToken: string }>
    ) => {
      const { user, accessToken, refreshToken } = action.payload;
      state.accessToken = accessToken;
      state.refreshToken = refreshToken;
      if (user) {
        state.user = user;
      }
      state.isAuthenticated = true;
      state.isInitialized = true;

      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEYS.ACCESS, accessToken);
        localStorage.setItem(STORAGE_KEYS.REFRESH, refreshToken);
      }
    },
    setUser: (state, action: PayloadAction<UserProfile>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.isInitialized = true;

      if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_KEYS.ACCESS);
        localStorage.removeItem(STORAGE_KEYS.REFRESH);
        sessionStorage.clear();
      }
    },
    initializeAuth: (
      state,
      action: PayloadAction<{ accessToken: string | null; refreshToken: string | null; user?: UserProfile | null }>
    ) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.user = action.payload.user || null;
      state.isAuthenticated = Boolean(action.payload.accessToken);
      state.isInitialized = true;
    },
  },
});

export const { setCredentials, setUser, logout, initializeAuth } = authSlice.actions;
export default authSlice.reducer;
