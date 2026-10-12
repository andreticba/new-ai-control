// frontend/src/components/Navbar.tsx | AI-Control v0.0.1 | 12-10-2026 10:00(GMT-04:00)
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import {
  ShieldCheck,
  Building2,
  LogOut,
  User as UserIcon,
  ChevronDown,
  Activity,
} from 'lucide-react';
import { useAppDispatch, useAppSelector } from '@/store';
import { logout } from '@/store/authSlice';

export function Navbar() {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    toast.info('Sessão encerrada com sucesso.');
    router.push('/login');
  };

  const getInitials = (name?: string) => {
    if (!name) return 'AI';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Platform Identity */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/20">
              <ShieldCheck className="h-5 w-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
                AI-Control
                <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  v0.0.1
                </span>
              </span>
            </div>
          </div>

          {/* Active Tenant / Organization Indicator */}
          {user?.primary_organization && (
            <div className="hidden md:flex items-center gap-2 pl-4 border-l border-slate-800">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs">
                <Building2 className="h-3.5 w-3.5 text-cyan-400" />
                <span className="text-slate-300 font-medium truncate max-w-[200px]">
                  {user.primary_organization.name}
                </span>
                <span className="px-1.5 py-0.2 rounded text-[10px] bg-slate-800 text-slate-400 font-mono">
                  {user.primary_organization.slug}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Gateway Status & User Controls */}
        <div className="flex items-center gap-3">
          {/* Status Badge */}
          <div className="hidden lg:flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-400">
            <Activity className="h-3 w-3 animate-pulse" />
            <span>Gateway Síncrono Conectado</span>
          </div>

          {/* User Profile Mini Bar */}
          <div className="flex items-center gap-3 pl-3 border-l border-slate-800/80">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-700 flex items-center justify-center text-xs font-semibold text-cyan-300 shadow-inner">
                {getInitials(user?.full_name)}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-semibold text-white truncate max-w-[150px]">
                  {user?.full_name || user?.username || 'Usuário'}
                </div>
                <div className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
                  <span>@{user?.username}</span>
                  <span className="text-slate-600">•</span>
                  <span className="text-cyan-400/90">{user?.platform_role}</span>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              title="Encerrar Sessão (Logout)"
              className="p-2 rounded-lg bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500/40 text-slate-400 hover:text-red-400 transition-all cursor-pointer"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
