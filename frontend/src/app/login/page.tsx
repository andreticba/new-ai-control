// frontend/src/app/login/page.tsx | AI-Control v0.0.1 | 12-10-2026 10:00(GMT-04:00)
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { z } from 'zod';
import {
  ShieldCheck,
  Lock,
  User,
  ArrowRight,
  Sparkles,
  Building2,
  GraduationCap,
  KeyRound,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { useAppDispatch } from '@/store';
import { logout, setCredentials } from '@/store/authSlice';
import api from '@/lib/api';

const loginSchema = z.object({
  username: z.string().min(3, 'Nome de usuário deve ter no mínimo 3 caracteres'),
  password: z.string().min(4, 'Senha deve ter no mínimo 4 caracteres'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const dispatch = useAppDispatch();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Partial<Record<keyof LoginFormData, string>>>({});
  const [loading, setLoading] = useState(false);

  // Limpeza preventiva de sessões residuais ao montar a página de login (FR-009)
  useEffect(() => {
    dispatch(logout());
  }, [dispatch]);

  const handleQuickFill = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
    setErrors({});
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Validação com Zod
    const validation = loginSchema.safeParse({ username, password });
    if (!validation.success) {
      const fieldErrors: Partial<Record<keyof LoginFormData, string>> = {};
      validation.error.issues.forEach((err) => {
        const path = err.path[0] as keyof LoginFormData;
        fieldErrors[path] = err.message;
      });
      setErrors(fieldErrors);
      toast.error('Por favor, corrija os erros no formulário');
      return;
    }

    setLoading(true);
    const toastId = toast.loading('Autenticando credenciais no API Gateway...');

    try {
      // Step 1: Emissão do par de tokens JWT
      const tokenRes = await api.post('/api/v1/auth/token/', {
        username: validation.data.username,
        password: validation.data.password,
      });

      const { access, refresh } = tokenRes.data;

      // Step 2: Carregamento do perfil do usuário em /api/v1/users/me/
      toast.loading('Carregando governança e RBAC 4-Tier...', { id: toastId });
      const userRes = await api.get('/api/v1/users/me/', {
        headers: {
          Authorization: `Bearer ${access}`,
        },
      });

      const userProfile = userRes.data;

      // Armazena credenciais na store Redux e localStorage
      dispatch(
        setCredentials({
          accessToken: access,
          refreshToken: refresh,
          user: userProfile,
        })
      );

      toast.success(
        `Bem-vindo(a), ${userProfile.full_name || userProfile.username}!`,
        { id: toastId }
      );

      // Redireciona para o Dashboard Shell
      router.push('/');
    } catch (err: unknown) {
      let message = 'Falha na autenticação. Verifique usuário e senha.';
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
        if (axiosErr.response?.status === 401) {
          message = 'Credenciais inválidas. Usuário ou senha incorretos.';
        } else if (axiosErr.response?.data?.detail) {
          message = axiosErr.response.data.detail;
        }
      }
      toast.error(message, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 bg-[#090d16] overflow-hidden">
      {/* Dynamic Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-cyan-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative w-full max-w-4xl grid grid-cols-1 md:grid-cols-12 gap-8 items-center z-10">
        {/* Left Column: Brand & Security Overview */}
        <div className="md:col-span-5 space-y-6">
          <div className="flex items-center gap-3">
            <div className="h-11 w-11 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-cyan-500/25">
              <ShieldCheck className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                AI-Control
                <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  v0.0.1
                </span>
              </h1>
              <p className="text-xs text-slate-400">Autonomous Agent Governance & RBAC</p>
            </div>
          </div>

          <div className="space-y-3 text-sm text-slate-300">
            <p className="text-slate-400 text-sm leading-relaxed">
              Plataforma empresarial de controle multi-inquilino, provendo isolamento matricial 4-Tier,
              Blind Indexing e governança de agentes autônomos.
            </p>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5 text-cyan-400" />
                Destaques Arquiteturais
              </div>
              <ul className="text-xs text-slate-400 space-y-1.5">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  RBAC 4-Tier (Org → Dept → Projeto → Squad)
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  Blind Indexing at-rest com Cryptographic Vault
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  Autenticação JWT Stateless & Resilient Interceptors
                </li>
              </ul>
            </div>
          </div>

          {/* Quick Persona Fillers */}
          <div className="space-y-2 pt-2">
            <div className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
              <KeyRound className="h-3.5 w-3.5 text-amber-400" />
              Personas Canônicas de Demonstração:
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickFill('prof.ana', 'demo1234')}
                className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/40 text-left transition-all group"
              >
                <div className="flex items-center gap-1.5 text-xs font-semibold text-white group-hover:text-cyan-400">
                  <GraduationCap className="h-3.5 w-3.5 text-cyan-400" />
                  prof.ana
                </div>
                <div className="text-[11px] text-slate-400 truncate">UF Demo (Acadêmico)</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickFill('gerente.ti', 'demo1234')}
                className="p-2.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/40 text-left transition-all group"
              >
                <div className="flex items-center gap-1.5 text-xs font-semibold text-white group-hover:text-indigo-400">
                  <Building2 className="h-3.5 w-3.5 text-indigo-400" />
                  gerente.ti
                </div>
                <div className="text-[11px] text-slate-400 truncate">Empresa Demo (Corp)</div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Glassmorphism Login Card */}
        <div className="md:col-span-7">
          <div className="p-8 rounded-2xl bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl shadow-2xl shadow-black/60 relative">
            <div className="mb-6">
              <h2 className="text-xl font-bold text-white tracking-tight">Portal de Acesso</h2>
              <p className="text-xs text-slate-400 mt-1">
                Insira as credenciais de sua organização para autenticar no API Gateway.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5 text-slate-400" />
                  Usuário ou Operador
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Ex: prof.ana ou gerente.ti"
                    disabled={loading}
                    className={`w-full px-3.5 py-2.5 rounded-xl bg-slate-950/70 border ${
                      errors.username ? 'border-red-500/60' : 'border-slate-800 focus:border-cyan-500'
                    } text-sm text-white placeholder-slate-500 outline-none transition-all`}
                  />
                </div>
                {errors.username && (
                  <p className="text-xs text-red-400 mt-1">{errors.username}</p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <Lock className="h-3.5 w-3.5 text-slate-400" />
                  Senha de Acesso
                </label>
                <div className="relative">
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    disabled={loading}
                    className={`w-full px-3.5 py-2.5 rounded-xl bg-slate-950/70 border ${
                      errors.password ? 'border-red-500/60' : 'border-slate-800 focus:border-cyan-500'
                    } text-sm text-white placeholder-slate-500 outline-none transition-all`}
                  />
                </div>
                {errors.password && (
                  <p className="text-xs text-red-400 mt-1">{errors.password}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-medium text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed group cursor-pointer"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin text-white" />
                    Processando Two-Step Login...
                  </>
                ) : (
                  <>
                    Autenticar no Gateway
                    <ArrowRight className="h-4 w-4 text-cyan-200 group-hover:translate-x-0.5 transition-transform" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 pt-5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
              <span>Ambiente: Desenvolvimento / Homologação</span>
              <span className="font-mono text-cyan-400/80">POST /api/v1/auth/token/</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
