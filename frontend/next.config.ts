import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*/",
        destination: `${BACKEND_URL}/api/:path*/`, // Proxy to Backend
      },
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`, // Proxy to Backend
      },
      {
        source: "/accounts/:path*/",
        destination: `${BACKEND_URL}/accounts/:path*/`, // Proxy to Backend Allauth
      },
      {
        source: "/accounts/:path*",
        destination: `${BACKEND_URL}/accounts/:path*`, // Proxy to Backend Allauth
      },
      {
        source: "/static/:path*/",
        destination: `${BACKEND_URL}/static/:path*/`, // Proxy for django static files
      },
      {
        source: "/static/:path*",
        destination: `${BACKEND_URL}/static/:path*`, // Proxy for django static files
      },
      {
        source: "/media/:path*/",
        destination: `${BACKEND_URL}/media/:path*/`, // Proxy for django media files
      },
      {
        source: "/media/:path*",
        destination: `${BACKEND_URL}/media/:path*`, // Proxy for django media files
      }
    ];
  },
};

export default nextConfig;
