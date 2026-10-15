// frontend/src/components/dashboard/ProjectsSection.tsx | AI-Control v0.0.1 | 14-10-2026 16:32(GMT-04:00)
'use client';

import React from 'react';
import { FolderGit2, Plus, Users2 } from 'lucide-react';
import { ProjectNode } from '@/types/auth';
import { DrawerMemberItem } from '@/components/members/TeamDrawer';
import { MembershipScope } from '@/components/members/MemberAllocationModal';

export interface ProjectsSectionProps {
  projects: ProjectNode[];
  canManageThisOrg: boolean;
  isPlatformSuperadmin: boolean;
  onOpenNewProjectModal: () => void;
  onOpenNewSquadModal: (projectId: string) => void;
  onOpenTeamDrawer: (
    title: string,
    subtitle: string,
    scope: MembershipScope,
    targetId: string,
    targetName: string,
    members: DrawerMemberItem[]
  ) => void;
}

export const ProjectsSection: React.FC<ProjectsSectionProps> = ({
  projects,
  canManageThisOrg,
  isPlatformSuperadmin,
  onOpenNewProjectModal,
  onOpenNewSquadModal,
  onOpenTeamDrawer,
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <FolderGit2 className="h-3.5 w-3.5 text-amber-400" />
          Projetos e Squads com Containment Rule
        </div>
        <button
          onClick={onOpenNewProjectModal}
          disabled={!isPlatformSuperadmin && !canManageThisOrg}
          title={
            !isPlatformSuperadmin && !canManageThisOrg
              ? 'Permissão insuficiente (exige org.manage)'
              : 'Cadastrar Projeto'
          }
          className={`px-2.5 py-1 rounded-lg border text-xs font-medium flex items-center gap-1 transition-all ${
            !isPlatformSuperadmin && !canManageThisOrg
              ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed opacity-50'
              : 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border-amber-500/30 cursor-pointer'
          }`}
        >
          <Plus className="h-3.5 w-3.5" />
          Novo Projeto
        </button>
      </div>

      {projects && projects.length > 0 ? (
        <div className="space-y-4">
          {projects.map((proj) => {
            const canManageThisProject =
              isPlatformSuperadmin ||
              canManageThisOrg ||
              proj.role === 'project_lead' ||
              proj.role === 'project_manager';

            return (
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
                      <span className="text-slate-200 font-semibold">{proj.role || 'Membro'}</span>
                      {proj.job_title && (
                        <>
                          {' '}• Rótulo: <span className="text-cyan-300">{proj.job_title}</span>
                        </>
                      )}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() =>
                        onOpenTeamDrawer(
                          proj.name,
                          'Membros Alocados no Projeto',
                          'PROJECT',
                          proj.id,
                          proj.name,
                          [
                            {
                              id: `proj-mem-${proj.id}`,
                              name: 'Colaborador do Projeto',
                              role: proj.role,
                              job_title: proj.job_title,
                              is_active: true,
                            },
                          ]
                        )
                      }
                      className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 border border-slate-700 text-[11px] font-medium flex items-center gap-1 transition-all cursor-pointer"
                      title="Ver Membros do Projeto"
                    >
                      <Users2 className="h-3 w-3 text-amber-400" />
                      Time
                    </button>
                    <button
                      onClick={() => onOpenNewSquadModal(proj.id)}
                      disabled={!canManageThisProject}
                      title={
                        !canManageThisProject
                          ? 'Permissão insuficiente (exige project.manage ou org.manage)'
                          : 'Criar Squad'
                      }
                      className={`px-2 py-1 rounded-lg border text-[11px] font-medium flex items-center gap-1 transition-all ${
                        !canManageThisProject
                          ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed opacity-50'
                          : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border-emerald-500/30 cursor-pointer'
                      }`}
                    >
                      <Plus className="h-3 w-3" />
                      Squad
                    </button>
                    <span className="self-start sm:self-auto px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-300 font-mono">
                      {proj.squads?.length || 0} Squads
                    </span>
                  </div>
                </div>

                {/* Nested Squads (Containment Rule) */}
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
                            <div className="flex items-center gap-1.5">
                              <button
                                onClick={() =>
                                  onOpenTeamDrawer(
                                    squad.name,
                                    'Membros da Squad Multidisciplinar',
                                    'SQUAD',
                                    squad.id,
                                    squad.name,
                                    [
                                      {
                                        id: `squad-mem-${squad.id}`,
                                        name: 'Executor da Squad',
                                        role: squad.role,
                                        job_title: squad.job_title,
                                        is_active: true,
                                      },
                                    ]
                                  )
                                }
                                className="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono flex items-center gap-1 cursor-pointer"
                              >
                                <Users2 className="h-2.5 w-2.5 text-emerald-400" />
                                Time
                              </button>
                              <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono">
                                {squad.role || 'Membro'}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between text-[11px] text-slate-400">
                            <span>
                              Slug: <code className="text-slate-300 font-mono">{squad.slug}</code>
                            </span>
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
            );
          })}
        </div>
      ) : (
        <div className="p-8 rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 text-center space-y-2">
          <p className="text-xs text-slate-500">Nenhum projeto cadastrado nesta organização.</p>
        </div>
      )}
    </div>
  );
};
