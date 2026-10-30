// column-splitter.tsx | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:51:00(GMT-04:00)
'use client';

import React from 'react';

export interface ColumnSplitterProps {
  isDragging: boolean;
  onMouseDown: (e: React.MouseEvent) => void;
  title?: string;
  theme?: 'cyan' | 'emerald';
}

export function ColumnSplitter({
  isDragging,
  onMouseDown,
  title = 'Arraste para redimensionar a coluna',
  theme = 'cyan',
}: ColumnSplitterProps) {
  const activeStyles =
    theme === 'emerald'
      ? 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.8)] w-2'
      : 'bg-cyan-500 shadow-[0_0_12px_rgba(6,182,212,0.8)] w-2';

  const hoverStyles =
    theme === 'emerald'
      ? 'hover:bg-emerald-500/50'
      : 'hover:bg-cyan-500/50';

  const gripHoverStyles =
    theme === 'emerald'
      ? 'group-hover:bg-emerald-300'
      : 'group-hover:bg-cyan-300';

  return (
    <div
      onMouseDown={onMouseDown}
      role="separator"
      aria-orientation="vertical"
      tabIndex={0}
      className={`w-1.5 hover:w-2 cursor-col-resize flex items-center justify-center shrink-0 z-20 group transition-all select-none ${
        isDragging
          ? activeStyles
          : `${hoverStyles} bg-slate-800/40`
      }`}
      title={title}
    >
      <div
        className={`w-0.5 h-6 rounded-full bg-slate-600 ${gripHoverStyles} opacity-60 group-hover:opacity-100 transition`}
      />
    </div>
  );
}
