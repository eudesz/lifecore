/** @type {import('next').NextConfig} */
const NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN = process.env.NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN || 'http://127.0.0.1:8000'

const nextConfig = {
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  async rewrites() {
    return [
      { source: '/api/agents/v2/:path*', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/agents/v2/:path*` },
      { source: '/api/prompts/:path*', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/prompts/:path*` },
      { source: '/api/lifecore/:path*', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/lifecore/:path*` },
      { source: '/api/lifecore/conditions/list', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/lifecore/conditions/list` },
      { source: '/api/doctor-link', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/doctor-link` },
      { source: '/api/reports/:path*', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/reports/:path*` },
      { source: '/api/users/:path*', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/api/users/:path*` },
      { source: '/d/:token', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/d/:token` },
      { source: '/d/chat/:token', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/d/chat/:token` },
      { source: '/d/ask/:token', destination: `${NEXT_PUBLIC_PLATFORM_BACKEND_ORIGIN}/d/ask/:token` }
    ]
  }
}

module.exports = nextConfig


