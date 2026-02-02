import withSerwist from "@serwist/next";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Your existing Next.js config here
};

const withPWA = withSerwist({
  // Source of the service worker (TypeScript supported)
  swSrc: "app/sw.ts",

  // Output destination in public/
  swDest: "public/sw.js",

  // Disable in development to avoid caching issues
  disable: process.env.NODE_ENV === "development",

  // Additional options:
  // swUrl: "/sw.js",                   // URL to serve SW from (default: /sw.js)
  // scope: "/",                         // SW scope (default: /)
  // reloadOnOnline: true,              // Reload page when back online
  // cacheOnFrontEndNav: true,          // Cache on client-side navigation
  // additionalPrecacheEntries: [],     // Extra URLs to precache
});

export default withPWA(nextConfig);
