// frontend/src/lib/get-query-client.ts | AI-Control v0.0.1 | 14-10-2026 16:25(GMT-04:00)
import { isServer, QueryClient } from '@tanstack/react-query';

function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        gcTime: 5 * 60 * 1000,
        retry: (failureCount, error: any) => {
          // Não retenta falhas definitivas de autenticação ou autorização
          if (error?.response?.status === 401 || error?.response?.status === 403) {
            return false;
          }
          return failureCount < 1;
        },
        refetchOnWindowFocus: false,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined = undefined;

export function getQueryClient(): QueryClient {
  if (isServer) {
    // No servidor (SSR): sempre instancia um novo cliente por requisição (Isolamento Multi-Tenant)
    return makeQueryClient();
  } else {
    // No navegador: mantém e reaproveita uma instância única estável
    if (!browserQueryClient) {
      browserQueryClient = makeQueryClient();
    }
    return browserQueryClient;
  }
}
