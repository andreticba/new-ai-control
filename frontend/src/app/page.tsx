// frontend/src/app/page.tsx | AI-Control v0.0.1 | 12-10-2026 10:00(GMT-04:00)
'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Building2,
  FolderGit2,
  Users2,
  Layers,
  ShieldCheck,
  Key,
  BadgeCheck,
  ChevronRight,
  Code2,
  RefreshCw,
  Sparkles,
  Bot,
  MessageSquareCode,
  Radio,
} from 'lucide-react';
import { useAppSelector } from '@/store';
import { Navbar } from '@/components/Navbar';
import api from '@/lib/api';
import { WorkspaceTree, OrganizationNode } from '@/types/auth';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isInitialized } = useAppSelector((state) => state.auth);

  const [workspaceData, setWorkspaceData] = useState<WorkspaceTree | null>(null);
  const [selectedOrgIndex, setSelectedOrgIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showJsonInspector, setShowJsonInspector] = useState(false);

  // Redireciona para /login caso a inicialização confirme ausência de sessão
  useEffect(() => {
    if (isInitialized && !isAuthenticated) {
      router.push('/login');
    }
  }, [isInitialized, isAuthenticated, router]);

  // Carrega árvore de workspaces (/api/v1/workspaces/)
  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/v1/workspaces/');
      setWorkspaceData(res.data);
    } catch (err) {
      console.error('Falha ao carregar workspaces:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadWorkspaces();
    }
  }, [isAuthenticated]);

  if (!isInitialized || (!isAuthenticated && !user)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#090d16] text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs font-mono tracking-wider">CARREGANDO AI-CONTROL HUD...</span>
        </div>
      </div>
    );
  }

  const orgList: OrganizationNode[] =
    workspaceData?.workspaces || workspaceData?.organizations || [];
  const activeOrg: OrganizationNode | undefined =
    orgList[selectedOrgIndex] || orgList[0];

  const totalDepts =
    orgList.reduce((acc, org) => acc + (org.departments?.length || 0), 0);
  const totalProjects =
    orgList.reduce((acc, org) => acc + (org.projects?.length || 0), 0);
  const totalSquads =
    orgList.reduce(
      (acc, org) =>
        acc +
        (org.projects?.reduce((pAcc, proj) => pAcc + (proj.squads?.length || 0), 0) || 0),
      0
    );

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section: Decrypted Identity & 4-Tier RBAC Status */}
        <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 p-6 md:p-8 overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 text-xs font-medium flex items-center gap-1.5">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  Blind Indexing Decoded
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 text-xs font-medium">
                  RBAC 4-Tier Ativo
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {user?.full_name || user?.username}
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 flex items-center gap-2">
                <span>Identificador: <code className="text-cyan-300 font-mono">@{user?.username}</code></span>
                <span>•</span>
                <span>E-mail: <span className="text-slate-300">{user?.email || 'N/A'}</span></span>
                <span>•</span>
                <span>Plataforma: <span className="text-indigo-300 font-semibold">{user?.platform_role}</span></span>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={loadWorkspaces}
                disabled={loading}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-200 flex items-center gap-2 transition-all cursor-pointer"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
                Atualizar Árvore
              </button>

              <button
                onClick={() => setShowJsonInspector(!showJsonInspector)}
                className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-cyan-400 flex items-center gap-2 transition-all cursor-pointer font-mono"
              >
                <Code2 className="h-3.5 w-3.5" />
                {showJsonInspector ? 'Ocultar JSON' : 'Inspecionar REST'}
              </button>
            </div>
          </div>
        </div>

        {/* Stats Grid: RBAC 4-Tier Topology */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium uppercase tracking-wider">Organizações</span>
              <Building2 className="h-4 w-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold text-white">
              {orgList.length}
            </div>
            <p className="text-[11px] text-slate-500">Tenants vinculados</p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium uppercase tracking-wider">Departamentos</span>
              <Layers className="h-4 w-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold text-white">{totalDepts}</div>
            <p className="text-[11px] text-slate-500">Unidades estruturais</p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium uppercase tracking-wider">Projetos</span>
              <FolderGit2 className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-white">{totalProjects}</div>
            <p className="text-[11px] text-slate-500">Escopos de governança</p>
          </div>

          <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-medium uppercase tracking-wider">Squads</span>
              <Users2 className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white">{totalSquads}</div>
            <p className="text-[11px] text-slate-500">Equipes operacionais</p>
          </div>
        </div>

        {/* JSON Inspector Modal/Collapse */}
        {showJsonInspector && (
          <div className="p-5 rounded-2xl bg-slate-950 border border-cyan-500/30 space-y-3">
            <div className="flex items-center justify-between">
              <div className="text-xs font-mono text-cyan-400 flex items-center gap-2">
                <Code2 className="h-4 w-4" />
                PAYLOAD SÍNCRONO: GET /api/v1/workspaces/ & /api/v1/users/me/
              </div>
              <span className="text-[10px] text-slate-500 font-mono">Formato Canônico OpenAPI 3.0</span>
            </div>
            <pre className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-[11px] text-emerald-300 font-mono overflow-x-auto max-h-72">
              {JSON.stringify({ user, workspaces: workspaceData }, null, 2)}
            </pre>
          </div>
        )}

        {/* Main Workspaces Explorer */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Building2 className="h-5 w-5 text-cyan-400" />
              Hierarquia 4-Tier & Escopos Ativos
            </h2>
            <span className="text-xs text-slate-400">
              Visualização agregada sem requisições em cascata
            </span>
          </div>

          {/* Org Selector Tabs */}
          {orgList.length > 0 ? (
            <div className="space-y-6">
              <div className="flex items-center gap-2 overflow-x-auto pb-1">
                {orgList.map((org, idx) => (
                  <button
                    key={org.id}
                    onClick={() => setSelectedOrgIndex(idx)}
                    className={`px-4 py-2.5 rounded-xl border text-xs font-medium transition-all flex items-center gap-2 cursor-pointer ${
                      selectedOrgIndex === idx
                        ? 'bg-cyan-500/15 border-cyan-500/50 text-cyan-300 shadow-md shadow-cyan-500/10'
                        : 'bg-slate-900/70 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                    }`}
                  >
                    <Building2 className="h-3.5 w-3.5" />
                    <span>{org.name}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      {org.slug}
                    </span>
                  </button>
                ))}
              </div>

              {activeOrg && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Left Column: Organization Summary & Departments */}
                  <div className="lg:col-span-4 space-y-6">
                    {/* Organization Membership Card */}
                    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                          Vínculo Organizacional
                        </span>
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[11px] font-mono">
                          {activeOrg.role}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white">{activeOrg.name}</h3>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">
                          ID: {activeOrg.id}
                        </p>
                      </div>
                      {activeOrg.job_title && (
                        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs flex items-center justify-between">
                          <span className="text-slate-400">Job Title:</span>
                          <span className="font-semibold text-slate-200">{activeOrg.job_title}</span>
                        </div>
                      )}
                    </div>

                    {/* Departments Card */}
                    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                          <Layers className="h-3.5 w-3.5 text-indigo-400" />
                          Departamentos ({activeOrg.departments?.length || 0})
                        </span>
                      </div>
                      <div className="space-y-2">
                        {activeOrg.departments?.length ? (
                          activeOrg.departments.map((dept) => (
                            <div
                              key={dept.id}
                              className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs hover:border-slate-700 transition-colors"
                            >
                              <span className="text-slate-200 font-medium truncate max-w-[180px]">
                                {dept.name}
                              </span>
                              <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 font-mono text-[10px]">
                                {dept.code}
                              </span>
                            </div>
                          ))
                        ) : (
                          <p className="text-xs text-slate-500 italic">Nenhum departamento cadastrado.</p>
                        )}
                      </div>
                    </div>

                    {/* Omnichannel Mock Preview (Demonstração Soft FK) */}
                    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                          <MessageSquareCode className="h-3.5 w-3.5 text-emerald-400" />
                          Omnichannel & Agentes IA
                        </span>
                        <Radio className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        Instância vinculada via Soft Foreign Key (<code className="text-cyan-300">organization_id</code>):
                      </p>
                      <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-xs space-y-1.5 font-mono">
                        <div className="flex justify-between text-slate-400">
                          <span>Instância:</span>
                          <span className="text-cyan-400">ai_control_{activeOrg.slug}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Status IA:</span>
                          <span className="text-emerald-400 font-semibold">ACTIVE_AI</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Roteamento:</span>
                          <span className="text-slate-200">5511000000001@example.org</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Projects & Nested Squads (Containment Rule) */}
                  <div className="lg:col-span-8 space-y-4">
                    <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                      <FolderGit2 className="h-3.5 w-3.5 text-amber-400" />
                      Projetos e Squads com Containment Rule
                    </div>

                    {activeOrg.projects && activeOrg.projects.length > 0 ? (
                      <div className="space-y-4">
                        {activeOrg.projects.map((proj) => (
                          <div
                            key={proj.id}
                            className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-5 hover:border-slate-700/80 transition-all"
                          >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <h4 className="text-base font-bold text-white tracking-tight">
                                    {proj.name}
                                  </h4>
                                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-[10px] font-mono">
                                    {proj.slug}
                                  </span>
                                </div>
                                <p className="text-xs text-slate-400">
                                  Papel no Projeto:{' '}
                                  <span className="text-slate-200 font-semibold">{proj.role}</span>
                                  {proj.job_title && (
                                    <> • Rótulo: <span className="text-cyan-300">{proj.job_title}</span></>
                                  )}
                                </p>
                              </div>

                              <span className="self-start sm:self-auto px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 font-mono">
                                {proj.squads?.length || 0} Squads Alocadas
                              </span>
                            </div>

                            {/* Nested Squads */}
                            <div className="pt-2 border-t border-slate-800/80 space-y-3">
                              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                                <Users2 className="h-3 w-3 text-emerald-400" />
                                Squads (Subordinadas ao Projeto)
                              </span>

                              {proj.squads && proj.squads.length > 0 ? (
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                  {proj.squads.map((squad) => (
                                    <div
                                      key={squad.id}
                                      className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 hover:border-emerald-500/40 transition-all space-y-2 group"
                                    >
                                      <div className="flex items-center justify-between">
                                        <span className="text-xs font-semibold text-slate-200 group-hover:text-emerald-300 transition-colors">
                                          {squad.name}
                                        </span>
                                        <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono">
                                          {squad.role}
                                        </span>
                                      </div>
                                      <div className="flex items-center justify-between text-[11px] text-slate-400">
                                        <span>Slug: <code className="text-slate-300 font-mono">{squad.slug}</code></span>
                                        {squad.job_title && (
                                          <span className="text-cyan-400 font-medium">
                                            {squad.job_title}
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-slate-500 italic">
                                  Nenhuma squad subordinada cadastrada para este projeto.
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center text-slate-400 space-y-2">
                        <FolderGit2 className="h-8 w-8 mx-auto text-slate-600" />
                        <p className="text-sm">Nenhum projeto alocado sob esta organização.</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center text-slate-400 space-y-2">
              <Building2 className="h-8 w-8 mx-auto text-slate-600" />
              <p className="text-sm">Nenhum workspace ativo encontrado para este usuário.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
