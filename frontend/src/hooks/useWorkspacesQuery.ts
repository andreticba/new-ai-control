// frontend/src/hooks/useWorkspacesQuery.ts | AI-Control v0.0.1 | 14-10-2026 16:26(GMT-04:00)
'use client';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { WorkspaceTree } from '@/types/auth';

export const WORKSPACES_QUERY_KEY = ['workspaces'] as const;

export function useWorkspacesQuery() {
  return useQuery({
    queryKey: WORKSPACES_QUERY_KEY,
    queryFn: async (): Promise<WorkspaceTree> => {
      const response = await api.get<WorkspaceTree>('/api/v1/workspaces/');
      return response.data;
    },
    staleTime: 60 * 1000,
  });
}
