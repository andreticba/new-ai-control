// frontend/src/hooks/useAuth.ts | AI-Control v0.0.1 | 14-10-2026 16:26(GMT-04:00)
'use client';

import { useAppSelector, useAppDispatch } from '@/store';
import { logout as reduxLogout } from '@/store/authSlice';
import { useRouter } from 'next/navigation';

export function useAuth() {
  const dispatch = useAppDispatch();
  const router = useRouter();
  const { user, isAuthenticated, isInitialized } = useAppSelector((state) => state.auth);

  const logout = () => {
    dispatch(reduxLogout());
    router.push('/login');
  };

  return {
    user,
    isAuthenticated,
    isInitialized,
    logout,
  };
}
