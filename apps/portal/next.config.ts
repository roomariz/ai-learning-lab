import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // WSL2 optimizations to prevent build hangs
  experimental: {
    // Reduces file system pressure in WSL
    optimizePackageImports: ["clsx"],
  },
  // Disable problematic features in WSL environment
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 5,
  },
};

export default nextConfig;
