// use-column-resize.ts | AI-Control Omnichannel v0.6.0 | 20-10-2026 23:49:00(GMT-04:00)
import { useState, useEffect, useCallback, useRef } from 'react';

export interface UseColumnResizeOptions {
  /** Chave única para persistência no localStorage */
  storageKey: string;
  /** Largura padrão inicial em pixels se não houver valor em cache */
  defaultWidth: number;
  /** Limite inferior de segurança em pixels */
  minWidth: number;
  /** Limite superior de segurança em pixels */
  maxWidth: number;
  /**
   * Direção de arraste:
   * - 'left': O cálculo da largura é (clientX - offset). Indicado para colunas alinhadas à esquerda (ex: Sidebar).
   * - 'right': O cálculo da largura é (window.innerWidth - clientX). Indicado para drawers ancorados à direita.
   */
  direction?: 'left' | 'right';
  /** Offset horizontal da barra de navegação/dock (ex: 56px para a dock lateral) */
  offset?: number;
}

export interface UseColumnResizeReturn {
  /** Largura corrente da coluna em pixels */
  width: number;
  /** Flag booleana indicando se o usuário está arrastando a divisória ativamente */
  isDragging: boolean;
  /** Handler para o evento onMouseDown da divisória */
  startDragging: (e: React.MouseEvent) => void;
  /** Redefine a largura para o valor padrão de fábrica */
  resetWidth: () => void;
}

export function useColumnResize({
  storageKey,
  defaultWidth,
  minWidth,
  maxWidth,
  direction = 'left',
  offset = 0,
}: UseColumnResizeOptions): UseColumnResizeReturn {
  const [width, setWidth] = useState<number>(defaultWidth);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const isDraggingRef = useRef<boolean>(false);

  // Carrega a largura salva no localStorage no mount do cliente
  useEffect(() => {
    try {
      const savedWidth = localStorage.getItem(storageKey);
      if (savedWidth !== null) {
        const parsed = Number(savedWidth);
        if (!isNaN(parsed) && parsed >= minWidth && parsed <= maxWidth) {
          setWidth(parsed);
        }
      }
    } catch {
      // Falha segura se localStorage estiver desativado ou inacessível
    }
  }, [storageKey, minWidth, maxWidth]);

  const startDragging = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    isDraggingRef.current = true;
  }, []);

  const resetWidth = useCallback(() => {
    setWidth(defaultWidth);
    try {
      localStorage.setItem(storageKey, String(defaultWidth));
    } catch {
      // Ignora erro de gravação
    }
  }, [defaultWidth, storageKey]);

  useEffect(() => {
    if (!isDragging) return;

    // Bloqueia a seleção acidental de texto durante o arraste
    const originalUserSelect = document.body.style.userSelect;
    const originalCursor = document.body.style.cursor;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;

      let newWidth: number;
      if (direction === 'right') {
        newWidth = window.innerWidth - e.clientX;
      } else {
        newWidth = e.clientX - offset;
      }

      // Aplica clamping estrito nos limites definidos
      const clampedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
      setWidth(clampedWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      isDraggingRef.current = false;
      document.body.style.userSelect = originalUserSelect;
      document.body.style.cursor = originalCursor;

      // Persiste o valor final no localStorage
      setWidth((currentWidth) => {
        try {
          localStorage.setItem(storageKey, String(currentWidth));
        } catch {
          // Ignora erro de gravação
        }
        return currentWidth;
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      document.body.style.userSelect = originalUserSelect;
      document.body.style.cursor = originalCursor;
    };
  }, [isDragging, direction, offset, minWidth, maxWidth, storageKey]);

  return {
    width,
    isDragging,
    startDragging,
    resetWidth,
  };
}
