// frontend/src/app/page.tsx | AI-Control v0.0.1 | 14-10-2026 16:35(GMT-04:00)
'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Building2, Users2, Plus, Code2 } from 'lucide-react';

import { Navbar } from '@/components/Navbar';
import { useAuth } from '@/hooks/useAuth';
import { useWorkspacesQuery } from '@/hooks/useWorkspacesQuery';
import { usePermission } from '@/hooks/usePermission';

import { WorkspaceHero } from '@/components/dashboard/WorkspaceHero';
import { WorkspaceStats } from '@/components/dashboard/WorkspaceStats';
import { OrganizationTabs } from '@/components/dashboard/OrganizationTabs';
import { DepartmentCard } from '@/components/dashboard/DepartmentCard';
import { OmnichannelCard } from '@/components/dashboard/OmnichannelCard';
import { ProjectsSection } from '@/components/dashboard/ProjectsSection';

import { OrganizationModal } from '@/components/forms/OrganizationModal';
import { DepartmentModal } from '@/components/forms/DepartmentModal';
import { ProjectModal } from '@/components/forms/ProjectModal';
import { SquadModal } from '@/components/forms/SquadModal';
import { TeamDrawer, DrawerMemberItem } from '@/components/members/TeamDrawer';
import {
  MemberAllocationModal,
  MembershipScope,
} from '@/components/members/MemberAllocationModal';
import { QuickUserModal } from '@/components/members/QuickUserModal';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isInitialized } = useAuth();
  const { canManageOrg, isPlatformSuperadmin } = usePermission();
  const { data: workspaceData, isLoading, refetch } = useWorkspacesQuery();

  // Estados locais de controle de UI
  const [selectedOrgIndex, setSelectedOrgIndex] = useState(0);
  const [showJsonInspector, setShowJsonInspector] = useState(false);

  // Estados de controle dos Modais 4-Tier
  const [isOrgModalOpen, setIsOrgModalOpen] = useState(false);
  const [isDeptModalOpen, setIsDeptModalOpen] = useState(false);
  const [isProjModalOpen, setIsProjModalOpen] = useState(false);
  const [isSquadModalOpen, setIsSquadModalOpen] = useState(false);
  const [selectedProjectIdForSquad, setSelectedProjectIdForSquad] = useState<string | undefined>(
    undefined
  );

  // Estado do Modal de Onboarding Rápido LGPD
  const [isQuickUserModalOpen, setIsQuickUserModalOpen] = useState(false);

  // Estados do TeamDrawer e MemberAllocationModal
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerConfig, setDrawerConfig] = useState<{
    title: string;
    subtitle: string;
    scope: MembershipScope;
    targetId: string;
    targetName: string;
    members: DrawerMemberItem[];
  }>({
    title: '',
    subtitle: '',
    scope: 'ORGANIZATION',
    targetId: '',
    targetName: '',
    members: [],
  });

  const [isAllocationModalOpen, setIsAllocationModalOpen] = useState(false);
  const [allocationTarget, setAllocationTarget] = useState<{
    scope: MembershipScope;
    targetId: string;
    targetName: string;
  }>({
    scope: 'ORGANIZATION',
    targetId: '',
    targetName: '',
  });

  const openDrawer = (
    title: string,
    subtitle: string,
    scope: MembershipScope,
    targetId: string,
    targetName: string,
    members: DrawerMemberItem[]
  ) => {
    setDrawerConfig({ title, subtitle, scope, targetId, targetName, members });
    setIsDrawerOpen(true);
  };

  const openAllocationModal = (
    scope: MembershipScope,
    targetId: string,
    targetName: string
  ) => {
    setAllocationTarget({ scope, targetId, targetName });
    setIsAllocationModalOpen(true);
  };

  // Redireciona para /login caso a inicialização confirme ausência de sessão
  useEffect(() => {
    if (isInitialized && !isAuthenticated) {
      router.push('/login');
    }
  }, [isInitialized, isAuthenticated, router]);

  // Lista de organizações e tenant ativo
  const orgList = workspaceData?.workspaces || [];
  const activeOrg = orgList[selectedOrgIndex] || orgList[0] || null;

  // Métricas agregadas da topologia 4-Tier
  const totalOrgs = orgList.length;
  const totalDepts = orgList.reduce((acc, org) => acc + (org.departments?.length || 0), 0);
  const totalProjects = orgList.reduce((acc, org) => acc + (org.projects?.length || 0), 0);
  const totalSquads = orgList.reduce(
    (acc, org) =>
      acc + (org.projects?.reduce((pAcc, proj) => pAcc + (proj.squads?.length || 0), 0) || 0),
    0
  );

  const canManageThisOrg = isPlatformSuperadmin || canManageOrg(activeOrg?.role);

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Bloco Hero de Identidade Descriptografada & Status 4-Tier */}
        <WorkspaceHero
          user={user}
          loading={isLoading}
          showJsonInspector={showJsonInspector}
          onRefresh={() => refetch()}
          onToggleJsonInspector={() => setShowJsonInspector((prev) => !prev)}
        />

        {/* Grade de Estatísticas Topológicas */}
        <WorkspaceStats
          totalOrgs={totalOrgs}
          totalDepts={totalDepts}
          totalProjects={totalProjects}
          totalSquads={totalSquads}
        />

        {/* Inspecionador de Payload REST */}
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

        {/* Explorador de Hierarquia 4-Tier */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <Building2 className="h-5 w-5 text-cyan-400" />
              Hierarquia 4-Tier & Escopos Ativos
            </h2>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsOrgModalOpen(true)}
                disabled={!canManageThisOrg}
                title={!canManageThisOrg ? 'Permissão insuficiente (exige org.manage)' : 'Criar Organização'}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium text-white flex items-center gap-1.5 shadow-md shadow-cyan-950/40 transition-all ${
                  !canManageThisOrg
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed opacity-60'
                    : 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 cursor-pointer'
                }`}
              >
                <Plus className="h-3.5 w-3.5" />
                Nova Organização
              </button>
              <span className="hidden sm:inline text-xs text-slate-400">
                Visualização agregada sem cascata
              </span>
            </div>
          </div>

          {/* Abas de Organizações */}
          {orgList.length > 0 ? (
            <div className="space-y-6">
              <OrganizationTabs
                organizations={orgList}
                selectedIndex={selectedOrgIndex}
                canManageOrg={canManageThisOrg}
                onSelectIndex={setSelectedOrgIndex}
                onOpenNewOrgModal={() => setIsOrgModalOpen(true)}
              />

              {activeOrg && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Coluna Esquerda: Resumo Organizacional, Departamentos & Omnichannel */}
                  <div className="lg:col-span-4 space-y-6">
                    {/* Cartão de Vínculo Organizacional */}
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
                      <div className="pt-2 flex items-center gap-2">
                        <button
                          onClick={() =>
                            openDrawer(
                              activeOrg.name,
                              'Vínculos e Membros da Organização',
                              'ORGANIZATION',
                              activeOrg.id,
                              activeOrg.name,
                              [
                                {
                                  id: 'org-mem-1',
                                  name: user?.full_name || user?.username || 'Administrador',
                                  email: user?.email,
                                  role: activeOrg.role,
                                  job_title: activeOrg.job_title,
                                  is_active: true,
                                },
                              ]
                            )
                          }
                          className="w-full py-2 px-3 rounded-xl bg-slate-800/70 hover:bg-slate-800 text-xs font-medium text-slate-200 flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                        >
                          <Users2 className="h-3.5 w-3.5 text-cyan-400" />
                          Gerenciar Membros da Org
                        </button>
                      </div>
                    </div>

                    {/* Cartão de Departamentos */}
                    <DepartmentCard
                      departments={activeOrg.departments || []}
                      canManageOrg={canManageThisOrg}
                      onOpenNewDeptModal={() => setIsDeptModalOpen(true)}
                    />

                    {/* Demonstração de Roteamento Omnichannel */}
                    <OmnichannelCard orgSlug={activeOrg.slug} />
                  </div>

                  {/* Coluna Direita: Projetos e Squads com Containment Rule */}
                  <div className="lg:col-span-8 space-y-4">
                    <ProjectsSection
                      projects={activeOrg.projects || []}
                      canManageThisOrg={canManageThisOrg}
                      isPlatformSuperadmin={isPlatformSuperadmin}
                      onOpenNewProjectModal={() => setIsProjModalOpen(true)}
                      onOpenNewSquadModal={(projectId) => {
                        setSelectedProjectIdForSquad(projectId);
                        setIsSquadModalOpen(true);
                      }}
                      onOpenTeamDrawer={openDrawer}
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 text-center space-y-3">
              <Building2 className="h-10 w-10 text-slate-600 mx-auto" />
              <h3 className="text-sm font-semibold text-slate-300">Nenhum workspace encontrado</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Você ainda não possui vínculo com organizações ativas.
              </p>
              {isPlatformSuperadmin && (
                <button
                  onClick={() => setIsOrgModalOpen(true)}
                  className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-xs font-medium text-white transition-all cursor-pointer"
                >
                  Cadastrar Primeira Organização
                </button>
              )}
            </div>
          )}
        </div>

        {/* Montagem Condicional dos Modais 4-Tier */}
        {isOrgModalOpen && (
          <OrganizationModal
            isOpen={isOrgModalOpen}
            onClose={() => {
              setIsOrgModalOpen(false);
              refetch();
            }}
          />
        )}

        {isDeptModalOpen && activeOrg && (
          <DepartmentModal
            isOpen={isDeptModalOpen}
            organizationId={activeOrg.id}
            organizations={orgList.map((o) => ({ id: o.id, name: o.name }))}
            onClose={() => {
              setIsDeptModalOpen(false);
              refetch();
            }}
          />
        )}

        {isProjModalOpen && activeOrg && (
          <ProjectModal
            isOpen={isProjModalOpen}
            organizationId={activeOrg.id}
            organizations={orgList.map((o) => ({ id: o.id, name: o.name }))}
            onClose={() => {
              setIsProjModalOpen(false);
              refetch();
            }}
          />
        )}

        {isSquadModalOpen && (
          <SquadModal
            isOpen={isSquadModalOpen}
            projectId={selectedProjectIdForSquad || activeOrg?.projects?.[0]?.id}
            projects={activeOrg?.projects?.map((p) => ({ id: p.id, name: p.name })) || []}
            onClose={() => {
              setIsSquadModalOpen(false);
              refetch();
            }}
          />
        )}

        {/* Painel Retrátil de Gestão de Membros */}
        {isDrawerOpen && (
          <TeamDrawer
            isOpen={isDrawerOpen}
            onClose={() => setIsDrawerOpen(false)}
            title={drawerConfig.title}
            subtitle={drawerConfig.subtitle}
            members={drawerConfig.members}
            onAllocateClick={() => {
              setIsDrawerOpen(false);
              openAllocationModal(
                drawerConfig.scope,
                drawerConfig.targetId,
                drawerConfig.targetName
              );
            }}
          />
        )}

        {/* Modal de Alocação de Membros */}
        {isAllocationModalOpen && (
          <MemberAllocationModal
            isOpen={isAllocationModalOpen}
            onClose={() => {
              setIsAllocationModalOpen(false);
              refetch();
            }}
            scope={allocationTarget.scope}
            targetId={allocationTarget.targetId}
            targetName={allocationTarget.targetName}
            departments={activeOrg?.departments || []}
            onOpenQuickUserModal={() => setIsQuickUserModalOpen(true)}
          />
        )}

        {/* Modal de Onboarding Rápido LGPD */}
        {isQuickUserModalOpen && (
          <QuickUserModal
            isOpen={isQuickUserModalOpen}
            onClose={() => setIsQuickUserModalOpen(false)}
            onUserCreated={() => {
              refetch();
            }}
          />
        )}
      </main>
    </div>
  );
}
