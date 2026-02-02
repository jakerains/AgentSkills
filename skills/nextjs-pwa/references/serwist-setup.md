# Serwist Setup — Deep Dive

## What is Serwist?

Serwist is the actively maintained successor to `next-pwa`. It wraps Workbox with first-class Next.js App Router support, TypeScript service workers, and automatic precaching.

## Installation

```bash
npm install @serwist/next && npm install -D serwist
```

**Package roles:**
- `@serwist/next` — Next.js plugin (wraps next.config.ts)
- `serwist` — Core library + SW utilities (dev dependency since it's only used in the SW build)

## Project Structure

```
app/
├── manifest.ts          # Web app manifest (native Next.js)
├── sw.ts                # Service worker source (compiled by Serwist)
├── layout.tsx
└── page.tsx
next.config.ts           # Wraps config with withSerwist
public/
└── sw.js                # Generated output (gitignore this)
```

Add to `.gitignore`:
```
public/sw.js
public/sw.js.map
public/swe-worker-*.js
```

## next.config.ts — Full Options

```ts
import withSerwist from "@serwist/next";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // your config
};

export default withSerwist({
  // Required
  swSrc: "app/sw.ts",           // SW source file
  swDest: "public/sw.js",       // Build output

  // Development
  disable: process.env.NODE_ENV === "development",

  // Optional
  swUrl: "/sw.js",               // URL path to serve SW
  scope: "/",                    // SW scope
  reloadOnOnline: true,          // Auto-reload when back online
  cacheOnFrontEndNav: true,      // Cache client-side navigations

  // Precaching
  additionalPrecacheEntries: [
    "/offline",
    "/fallback-image.png",
  ],

  // Injection point (advanced)
  injectionPoint: "self.__SW_MANIFEST",
})(nextConfig);
```

## Service Worker — Full Template

```ts
import { defaultCache } from "@serwist/next/worker";
import type { PrecacheEntry, SerwistGlobalConfig } from "serwist";
import { Serwist } from "serwist";

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
  }
}

declare const self: ServiceWorkerGlobalScope;

const serwist = new Serwist({
  // Precache entries injected at build time
  precacheEntries: self.__SW_MANIFEST,

  // Activate immediately without waiting for tabs to close
  skipWaiting: true,

  // Take control of all open pages immediately
  clientsClaim: true,

  // Enable Navigation Preload for faster navigations
  navigationPreload: true,

  // Runtime caching rules
  runtimeCaching: defaultCache,

  // Offline fallback
  fallbacks: {
    entries: [
      {
        url: "/offline",
        matcher({ request }) {
          return request.destination === "document";
        },
      },
    ],
  },
});

serwist.addEventListeners();
```

## Custom Runtime Caching Routes

Override or extend `defaultCache` with your own routes:

```ts
import { defaultCache } from "@serwist/next/worker";
import {
  CacheFirst,
  NetworkFirst,
  StaleWhileRevalidate,
  ExpirationPlugin,
  CacheableResponsePlugin,
} from "serwist";

const runtimeCaching = [
  ...defaultCache,

  // API with network-first strategy
  {
    urlPattern: /\/api\/.*/i,
    handler: new NetworkFirst({
      cacheName: "api-cache",
      networkTimeoutSeconds: 10,
      plugins: [
        new ExpirationPlugin({
          maxEntries: 50,
          maxAgeSeconds: 5 * 60, // 5 minutes
        }),
      ],
    }),
  },

  // Images with cache-first and expiration
  {
    urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif|ico)$/i,
    handler: new CacheFirst({
      cacheName: "image-cache",
      plugins: [
        new CacheableResponsePlugin({ statuses: [0, 200] }),
        new ExpirationPlugin({
          maxEntries: 100,
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
        }),
      ],
    }),
  },

  // Google Fonts stylesheets
  {
    urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
    handler: new StaleWhileRevalidate({
      cacheName: "google-fonts-stylesheets",
    }),
  },

  // Google Fonts webfont files
  {
    urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
    handler: new CacheFirst({
      cacheName: "google-fonts-webfonts",
      plugins: [
        new CacheableResponsePlugin({ statuses: [0, 200] }),
        new ExpirationPlugin({
          maxEntries: 30,
          maxAgeSeconds: 365 * 24 * 60 * 60, // 1 year
        }),
      ],
    }),
  },

  // Third-party CDN assets
  {
    urlPattern: /^https:\/\/cdn\..*/i,
    handler: new StaleWhileRevalidate({
      cacheName: "cdn-cache",
      plugins: [
        new ExpirationPlugin({
          maxEntries: 50,
          maxAgeSeconds: 24 * 60 * 60, // 1 day
        }),
      ],
    }),
  },
];
```

## Precaching

Serwist automatically precaches Next.js build output (JS, CSS chunks). To add custom URLs:

```ts
// In next.config.ts
withSerwist({
  swSrc: "app/sw.ts",
  swDest: "public/sw.js",
  additionalPrecacheEntries: [
    "/offline",
    "/icons/icon-192.png",
    "/icons/icon-512.png",
  ],
})
```

Or in the SW itself:

```ts
const serwist = new Serwist({
  precacheEntries: [
    ...(self.__SW_MANIFEST ?? []),
    { url: "/custom-page", revision: "v1" },
  ],
});
```

## Migration from next-pwa

### Package swap

```bash
npm uninstall next-pwa
npm install @serwist/next && npm install -D serwist
```

### Config migration

**Before (next-pwa):**
```js
const withPWA = require("next-pwa")({
  dest: "public",
  disable: process.env.NODE_ENV === "development",
  runtimeCaching: [...],
});

module.exports = withPWA({ /* nextConfig */ });
```

**After (Serwist):**
```ts
import withSerwist from "@serwist/next";

export default withSerwist({
  swSrc: "app/sw.ts",
  swDest: "public/sw.js",
  disable: process.env.NODE_ENV === "development",
})({ /* nextConfig */ });
```

### Key differences

| next-pwa | Serwist |
|----------|---------|
| Auto-generates SW from config | You write SW source in TypeScript |
| `runtimeCaching` in next.config | `runtimeCaching` in sw.ts |
| CommonJS config | ESM / TypeScript |
| Workbox config passthrough | Serwist API (wraps Workbox) |
| Pages Router focus | App Router first |

### Runtime caching migration

next-pwa runtime caching entries map directly to Serwist:

```ts
// next-pwa style (in config)
{ urlPattern: /\.(?:png|jpg)$/, handler: "CacheFirst" }

// Serwist style (in sw.ts)
import { CacheFirst } from "serwist";
{ urlPattern: /\.(?:png|jpg)$/, handler: new CacheFirst({ cacheName: "images" }) }
```

## TypeScript Support

Serwist SWs are written in TypeScript. The build step compiles them. No extra tsconfig needed — Serwist handles compilation.

Type the SW global scope:

```ts
declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
  }
}

declare const self: ServiceWorkerGlobalScope;
```

## Debugging

```ts
// In sw.ts — log precache entries
console.log("Precache manifest:", self.__SW_MANIFEST);

// Check SW status in browser
navigator.serviceWorker.getRegistration().then(console.log);
```

DevTools → Application → Service Workers shows:
- Active SW version
- Cache storage contents
- SW console logs

## Common Patterns

### Skip waiting with user prompt

```ts
// In sw.ts
self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

// In client code
function onUpdateReady() {
  if (confirm("New version available. Reload?")) {
    navigator.serviceWorker.controller?.postMessage({ type: "SKIP_WAITING" });
    window.location.reload();
  }
}
```

### Exclude routes from SW

```ts
// Don't cache auth-related routes
{
  urlPattern: /\/api\/auth\/.*/i,
  handler: new NetworkOnly(),
}
```

### Cache POST responses (rare)

Serwist/Workbox only caches GET by default. For POST caching, use a custom plugin or IndexedDB.
