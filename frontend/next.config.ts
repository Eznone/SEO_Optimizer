import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*", // Proxy to Backend
      },
      {
        source: "/accounts/:path*",
        destination: "http://127.0.0.1:8000/accounts/:path*", // Proxy to Backend Allauth
      },
      {
        source: "/static/:path*",
        destination: "http://127.0.0.1:8000/static/:path*", // Proxy for django static files
      }
    ];
  },
};

export default nextConfig;
