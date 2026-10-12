// frontend/next.config.ts | AI-Control v0.0.1 | 12-10-2026 09:40(GMT-04:00)

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: [
    "127.0.0.1",
    "localhost",
  ],
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
