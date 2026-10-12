// frontend/src/lib/utils.ts | AI-Control v0.0.1 | 12-10-2026 09:55(GMT-04:00)

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
