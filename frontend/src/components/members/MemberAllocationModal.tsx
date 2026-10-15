// frontend/src/components/members/MemberAllocationModal.tsx | AI-Control v0.0.1 | 15-10-2026 07:47(GMT-04:00)
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Modal } from '@/components/ui/Modal';
import { useMembershipMutations } from '@/hooks/useMembershipMutations';
import { api } from '@/lib/api';
import {
  UserCheck,
  Loader2,
  ShieldAlert,
  Search,
  User as UserIcon,
  X,
  Building2,
  Briefcase,
  Shield,
  Layers,
} from 'lucide-react';

export type MembershipScope = 'ORGANIZATION' | 'PROJECT' | 'SQUAD';

interface UserSearchResult {
  id: number;
  username: string;
  email: string;
  full_name: string;
}

interface RoleOption {
  id: string;
  slug: string;
  name: string;
  scope: string;
  level: number;
  description: string;
}

interface JobTitleOption {
  id: string;
  slug: string;
  name: string;
  level: string;
  category: string;
}

interface MemberAllocationModalProps {
  isOpen: boolean;
  onClose: () => void;
  scope: MembershipScope;
  targetId: string;
  targetName: string;
  departments?: Array<{ id: string; name: string; code: string }>;
  onOpenQuickUserModal?: () => void;
}

export const MemberAllocationModal: React.FC<MemberAllocationModalProps> = ({
  isOpen,
  onClose,
  scope,
  targetId,
  targetName,
  departments = [],
  onOpenQuickUserModal,
}) => {
  const { allocateOrgMember, allocateProjectMember, allocateSquadMember } =
    useMembershipMutations();

  // Estados de busca de usuário
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState<UserSearchResult | null>(null);
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  // Estados dos catálogos dinâmicos
  const [roles, setRoles] = useState<RoleOption[]>([]);
  const [jobTitles, setJobTitles] = useState<JobTitleOption[]>([]);
  const [isLoadingCatalogs, setIsLoadingCatalogs] = useState(false);

  // Estados do formulário
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [selectedJobTitleId, setSelectedJobTitleId] = useState<string>('');
  const [selectedDepartmentId, setSelectedDepartmentId] = useState<string>('');
  const [isExternal, setIsExternal] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const isPending =
    allocateOrgMember.isPending ||
    allocateProjectMember.isPending ||
    allocateSquadMember.isPending;

  // Carrega catálogos de papéis e cargos ao abrir o modal
  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setIsLoadingCatalogs(true);

    Promise.all([
      api.get(`/api/v1/workspaces/catalog/roles/?scope=${scope}`),
      api.get(`/api/v1/workspaces/catalog/job-titles/?level=${scope}`),
    ])
      .then(([rolesRes, titlesRes]) => {
        if (!isMounted) return;
        const fetchedRoles: RoleOption[] = rolesRes.data.roles || [];
        const fetchedTitles: JobTitleOption[] = titlesRes.data.job_titles || [];
        setRoles(fetchedRoles);
        setJobTitles(fetchedTitles);

        if (fetchedRoles.length > 0 && !selectedRoleId) {
          // Seleciona um papel padrão coerente com o escopo
          const defaultRole =
            fetchedRoles.find((r) =>
              scope === 'ORGANIZATION'
                ? r.slug === 'org_member'
                : scope === 'PROJECT'
                ? r.slug === 'project_member'
                : r.slug === 'squad_member'
            ) || fetchedRoles[0];
          setSelectedRoleId(defaultRole.id);
        }
      })
      .catch((err) => {
        console.error('Erro ao carregar catálogos:', err);
      })
      .finally(() => {
        if (isMounted) setIsLoadingCatalogs(false);
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, scope]);

  // Busca de usuários com debounce
  useEffect(() => {
    if (!isOpen || selectedUser) return;

    const timer = setTimeout(() => {
      setIsSearching(true);
      api
        .get(`/api/v1/users/search/?q=${encodeURIComponent(searchQuery)}`)
        .then((res) => {
          setSearchResults(res.data.users || []);
        })
        .catch((err) => {
          console.error('Erro na busca de usuários:', err);
        })
        .finally(() => {
          setIsSearching(false);
        });
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery, isOpen, selectedUser]);

  // Fecha dropdown de busca ao clicar fora
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(e.target as Node)
      ) {
        setIsSearchOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectUser = (user: UserSearchResult) => {
    setSelectedUser(user);
    setSearchQuery('');
    setIsSearchOpen(false);
    setError(null);
  };

  const handleClearUser = () => {
    setSelectedUser(null);
    setSearchQuery('');
  };

  const resetForm = () => {
    setSelectedUser(null);
    setSearchQuery('');
    setSelectedRoleId(roles[0]?.id || '');
    setSelectedJobTitleId('');
    setSelectedDepartmentId('');
    setIsExternal(false);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedUser) {
      setError('Selecione um usuário para realizar a alocação.');
      return;
    }

    if (!selectedRoleId) {
      setError('Selecione o papel de acesso (Role) do membro.');
      return;
    }

    if (scope === 'ORGANIZATION') {
      allocateOrgMember.mutate(
        {
          organization_id: targetId,
          user_id: selectedUser.id,
          role_id: selectedRoleId,
          department_id: selectedDepartmentId || undefined,
          job_title_id: selectedJobTitleId || undefined,
          is_active: true,
        },
        {
          onSuccess: () => {
            resetForm();
            onClose();
          },
        }
      );
    } else if (scope === 'PROJECT') {
      allocateProjectMember.mutate(
        {
          project_id: targetId,
          user_id: selectedUser.id,
          role_id: selectedRoleId,
          job_title_id: selectedJobTitleId || undefined,
          is_external: isExternal,
          is_active: true,
        },
        {
          onSuccess: () => {
            resetForm();
            onClose();
          },
        }
      );
    } else if (scope === 'SQUAD') {
      allocateSquadMember.mutate(
        {
          squad_id: targetId,
          user_id: selectedUser.id,
          role_id: selectedRoleId,
          job_title_id: selectedJobTitleId || undefined,
          is_active: true,
        },
        {
          onSuccess: () => {
            resetForm();
            onClose();
          },
        }
      );
    }
  };

  const getScopeBadge = () => {
    switch (scope) {
      case 'ORGANIZATION':
        return { label: 'Organização', icon: Building2, color: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10' };
      case 'PROJECT':
        return { label: 'Projeto', icon: Briefcase, color: 'text-amber-400 border-amber-500/30 bg-amber-500/10' };
      case 'SQUAD':
        return { label: 'Squad', icon: UserCheck, color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10' };
    }
  };

  const badge = getScopeBadge();
  const ScopeIcon = badge.icon;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Alocar Membro — ${targetName}`}
      description="Selecione o colaborador, defina o papel e cargo de forma visual sem necessidade de códigos."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Banner do Escopo Alvo */}
        <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 rounded-full border text-[11px] font-medium flex items-center gap-1 ${badge.color}`}>
              <ScopeIcon className="w-3 h-3" />
              {badge.label}
            </span>
            <span className="font-semibold text-slate-200">{targetName}</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Governança 4-Tier</span>
        </div>

        {scope === 'SQUAD' && (
          <div className="p-3 rounded-xl bg-cyan-950/40 border border-cyan-800/60 text-xs text-cyan-300 flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              <strong>Inviolabilidade P3 Contínua:</strong> O usuário precisa possuir vínculo ativo pré-existente no projeto pai desta squad.
            </span>
          </div>
        )}

        {/* 1. Seleção de Usuário com Busca Autocomplete */}
        <div ref={searchContainerRef} className="space-y-1.5 relative">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-medium text-slate-300 flex items-center gap-1.5">
              <UserIcon className="w-3.5 h-3.5 text-cyan-400" />
              Colaborador *
            </label>
            {onOpenQuickUserModal && (
              <button
                type="button"
                onClick={onOpenQuickUserModal}
                className="text-[11px] text-cyan-400 hover:text-cyan-300 underline underline-offset-2 transition-colors cursor-pointer"
              >
                + Admissão Rápida (Novo Usuário)
              </button>
            )}
          </div>

          {selectedUser ? (
            <div className="p-3 rounded-xl bg-slate-900 border border-cyan-500/40 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-300 font-bold text-xs uppercase">
                  {selectedUser.full_name.charAt(0) || selectedUser.username.charAt(0)}
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white tracking-tight">
                    {selectedUser.full_name}
                  </h4>
                  <p className="text-[11px] text-slate-400 flex items-center gap-2">
                    <span className="font-mono text-cyan-400">@{selectedUser.username}</span>
                    {selectedUser.email && (
                      <>
                        <span>•</span>
                        <span>{selectedUser.email}</span>
                      </>
                    )}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleClearUser}
                className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1 transition-all cursor-pointer"
                title="Trocar usuário"
              >
                <X className="w-3 h-3 text-rose-400" />
                <span>Trocar</span>
              </button>
            </div>
          ) : (
            <div className="relative">
              <div className="relative">
                <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Buscar por nome, usuário (@username) ou e-mail..."
                  value={searchQuery}
                  onFocus={() => setIsSearchOpen(true)}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setIsSearchOpen(true);
                  }}
                  className="w-full bg-slate-950/70 border border-slate-800 rounded-xl pl-9 pr-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500"
                />
                {isSearching && (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin absolute right-3.5 top-1/2 -translate-y-1/2" />
                )}
              </div>

              {/* Dropdown com resultados da busca */}
              {isSearchOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 max-h-56 overflow-y-auto bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 divide-y divide-slate-800">
                  {searchResults.length > 0 ? (
                    searchResults.map((user) => (
                      <button
                        key={user.id}
                        type="button"
                        onClick={() => handleSelectUser(user)}
                        className="w-full text-left p-2.5 hover:bg-slate-800/80 transition-colors flex items-center justify-between group cursor-pointer"
                      >
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-slate-800 group-hover:bg-cyan-500/20 text-slate-300 group-hover:text-cyan-300 flex items-center justify-center text-xs font-semibold uppercase transition-colors">
                            {user.full_name.charAt(0) || user.username.charAt(0)}
                          </div>
                          <div>
                            <span className="text-xs font-medium text-slate-100 group-hover:text-white block">
                              {user.full_name}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              @{user.username} {user.email && `(${user.email})`}
                            </span>
                          </div>
                        </div>
                        <span className="text-[11px] text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity font-medium">
                          Selecionar
                        </span>
                      </button>
                    ))
                  ) : (
                    <div className="p-4 text-center text-xs text-slate-500">
                      {isSearching
                        ? 'Pesquisando na base de usuários...'
                        : 'Nenhum usuário encontrado. Use a Admissão Rápida acima para cadastrar.'}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* 2. Seleção de Papel (Role) */}
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            Papel de Acesso (Role) *
          </label>
          <select
            value={selectedRoleId}
            onChange={(e) => setSelectedRoleId(e.target.value)}
            disabled={isLoadingCatalogs}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 cursor-pointer disabled:opacity-50"
          >
            {roles.length === 0 && <option value="">Carregando papéis...</option>}
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.slug})
              </option>
            ))}
          </select>
          {roles.length > 0 && selectedRoleId && (
            <p className="mt-1 text-[11px] text-slate-400 italic">
              {roles.find((r) => r.id === selectedRoleId)?.description || 'Papel regulado por RBAC 4-Tier.'}
            </p>
          )}
        </div>

        {/* 3. Seleção de Cargo / Job Title (opcional) */}
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
            <Briefcase className="w-3.5 h-3.5 text-amber-400" />
            Cargo / Job Title (Opcional)
          </label>
          <select
            value={selectedJobTitleId}
            onChange={(e) => setSelectedJobTitleId(e.target.value)}
            disabled={isLoadingCatalogs}
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 cursor-pointer disabled:opacity-50"
          >
            <option value="">(Nenhum / Não especificado)</option>
            {jobTitles.map((jt) => (
              <option key={jt.id} value={jt.id}>
                {jt.name} [{jt.category}]
              </option>
            ))}
          </select>
          <p className="mt-1 text-[11px] text-slate-500">
            Rótulo profissional para identificação de equipe (não altera permissões).
          </p>
        </div>

        {/* 4. Seleção de Departamento (Apenas no escopo ORGANIZATION) */}
        {scope === 'ORGANIZATION' && (
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              Lotação Departamental (Opcional)
            </label>
            <select
              value={selectedDepartmentId}
              onChange={(e) => setSelectedDepartmentId(e.target.value)}
              className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 cursor-pointer"
            >
              <option value="">(Nenhum departamento vinculado)</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.code})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* 5. Colaborador Externo (Apenas no escopo PROJECT) */}
        {scope === 'PROJECT' && (
          <div className="flex items-center gap-2 pt-1">
            <input
              type="checkbox"
              id="isExternalCheck"
              checked={isExternal}
              onChange={(e) => setIsExternal(e.target.checked)}
              className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500/50 cursor-pointer"
            />
            <label htmlFor="isExternalCheck" className="text-xs text-slate-300 cursor-pointer">
              Colaborador Externo (Exige papel com permissão convidado)
            </label>
          </div>
        )}

        {error && <p className="text-xs text-rose-400 font-medium">{error}</p>}

        <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800/80">
          <button
            type="button"
            onClick={onClose}
            disabled={isPending}
            className="px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800/70 hover:bg-slate-800 rounded-xl transition-all cursor-pointer"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isPending || !selectedUser}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl shadow-lg shadow-cyan-950/50 transition-all disabled:opacity-50 cursor-pointer"
          >
            {isPending ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Alocando...
              </>
            ) : (
              <>
                <UserCheck className="w-3.5 h-3.5" />
                Alocar Membro
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};
