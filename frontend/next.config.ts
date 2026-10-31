import type { NextConfig } from 'next';

const config: NextConfig = {
  reactStrictMode: true,
  // Dev only: Next blocks its dev resources (HMR socket, chunks) for any host but localhost, which broke the
  // app when opened as http://127.0.0.1:3000. Phones on the LAN add their address via NEXT_DEV_ORIGINS.
  allowedDevOrigins: ['127.0.0.1', ...(process.env.NEXT_DEV_ORIGINS?.split(',').filter(Boolean) ?? [])],
};

export default config;
