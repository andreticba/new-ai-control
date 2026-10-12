// frontend/src/app/layout.tsx | AI-Control v0.0.1 | 12-10-2026 10:00(GMT-04:00)

import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/components/Providers';

export const metadata: Metadata = {
  title: 'AI-Control — Multi-Tenant Autonomous Agent Governance',
  description: 'Enterprise AI Governance, RBAC 4-Tier, Omnichannel routing and Data Vault platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="min-h-screen bg-[#090d16] text-slate-100 antialiased selection:bg-cyan-500/20 selection:text-cyan-300">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
