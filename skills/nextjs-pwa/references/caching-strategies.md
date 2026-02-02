# Caching Strategies — Complete Guide

## Overview

Service workers intercept fetch requests and decide how to respond. The 5 standard caching strategies determine whether to serve from cache, network, or both.

## Strategy 1: Cache First (Cache Falling Back to Network)

**Best for:** Static assets that rarely change — images, fonts, icons, JS/CSS bundles with content hashes.

**Flow:** Check cache → if hit, return cached → if miss, fetch from network → cache response → return

### Serwist

```ts
import { CacheFirst, ExpirationPlugin, CacheableResponsePlugin } from "serwist";

{
  urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif|ico)$/i,
  handler: new CacheFirst({
    cacheName: "images",
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({
        maxEntries: 100,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
    ],
  }),
}
```

### Manual SW

```js
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  if (response.ok) {
    cache.put(request, response.clone());
  }
  return response;
}
```

### When to use
- Images, fonts, icons
- Versioned JS/CSS bundles (filename includes hash)
- Any asset with immutable cache headers
- Third-party library files (CDN)

### When NOT to use
- API responses that change frequently
- HTML pages (users would see stale content)
- Auth tokens or session data

---

## Strategy 2: Network First (Network Falling Back to Cache)

**Best for:** Dynamic content that should be fresh — HTML pages, API responses.

**Flow:** Fetch from network → if success, cache + return → if fail, return cached (or offline fallback)

### Serwist

```ts
import { NetworkFirst, ExpirationPlugin } from "serwist";

{
  urlPattern: /\/api\/.*/i,
  handler: new NetworkFirst({
    cacheName: "api-responses",
    networkTimeoutSeconds: 10,
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 5 * 60, // 5 minutes
      }),
    ],
  }),
}
```

### Manual SW

```js
async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    return cached || new Response("Offline", { status: 503 });
  }
}
```

### Network timeout variant

```js
async function networkFirstWithTimeout(request, cacheName, timeoutMs = 3000) {
  const cache = await caches.open(cacheName);

  const timeoutPromise = new Promise((resolve) =>
    setTimeout(() => resolve(null), timeoutMs)
  );

  const networkPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });

  const response = await Promise.race([networkPromise, timeoutPromise]);
  return response || (await cache.match(request));
}
```

### When to use
- HTML pages (navigation)
- API data that changes often
- User-specific content (dashboards, feeds)
- Search results

---

## Strategy 3: Stale While Revalidate (SWR)

**Best for:** Content where showing slightly stale data is acceptable while fetching fresh data in the background.

**Flow:** Return cached immediately → fetch from network in background → update cache for next request

### Serwist

```ts
import { StaleWhileRevalidate, ExpirationPlugin } from "serwist";

{
  urlPattern: /\.(?:js|css)$/i,
  handler: new StaleWhileRevalidate({
    cacheName: "static-resources",
    plugins: [
      new ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 24 * 60 * 60, // 1 day
      }),
    ],
  }),
}
```

### Manual SW

```js
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);

  // Always fetch in background to update cache
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  });

  // Return cached immediately, or wait for network
  return cached || fetchPromise;
}
```

### When to use
- CSS/JS that changes occasionally
- Avatars, profile images
- Semi-static data (config, feature flags)
- Google Fonts stylesheets

---

## Strategy 4: Network Only

**Best for:** Requests that must always go to the network — no caching.

### Serwist

```ts
import { NetworkOnly } from "serwist";

{
  urlPattern: /\/api\/auth\/.*/i,
  handler: new NetworkOnly(),
}
```

### Manual SW

```js
// Simply don't handle these in the fetch listener
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Skip auth routes entirely — let them pass through
  if (url.pathname.startsWith("/api/auth/")) return;

  // ... handle other requests
});
```

### When to use
- Authentication endpoints
- Payment processing
- Real-time data (WebSocket upgrades)
- Analytics/tracking requests

---

## Strategy 5: Cache Only

**Best for:** Content that was precached during install and never needs network.

### Serwist

```ts
import { CacheOnly } from "serwist";

{
  urlPattern: /\/precached\/.*/i,
  handler: new CacheOnly(),
}
```

### Manual SW

```js
async function cacheOnly(request) {
  return caches.match(request);
}
```

### When to use
- Precached app shell assets
- Offline-first content that never changes
- Embedded assets (icons, logos)

---

## Strategy Selection Guide

| Content Type | Strategy | Reason |
|-------------|----------|--------|
| HTML pages | Network First | Always show fresh content, fall back to cache |
| JS/CSS bundles (hashed) | Cache First | Hash changes on update, safe to cache forever |
| JS/CSS bundles (unhashed) | Stale While Revalidate | Show cached, update in background |
| Images | Cache First | Rarely change, save bandwidth |
| Fonts | Cache First | Never change after initial load |
| API (read) | Network First or SWR | Depends on freshness requirements |
| API (write) | Network Only | Must reach server |
| Auth endpoints | Network Only | Security-critical |
| Third-party CDN | Stale While Revalidate | Usually versioned but good to refresh |
| User avatars | Stale While Revalidate | Show cached, update eventually |

## Cache Expiration

Always set expiration to prevent unbounded cache growth:

```ts
import { ExpirationPlugin } from "serwist";

new ExpirationPlugin({
  maxEntries: 100,        // Max items in cache
  maxAgeSeconds: 7 * 24 * 60 * 60,  // 7 days
  purgeOnQuotaError: true, // Delete this cache if storage is full
})
```

## Cache Quotas

Browsers limit cache storage (varies by browser):
- Chrome: ~60% of free disk space (per origin)
- Firefox: ~50% of free disk space (per origin)
- Safari/iOS: ~50MB evicted aggressively

Use `navigator.storage.estimate()` to check:

```ts
const { usage, quota } = await navigator.storage.estimate();
console.log(`Using ${usage} of ${quota} bytes`);
```

Request persistent storage to reduce eviction risk:

```ts
if (navigator.storage?.persist) {
  const granted = await navigator.storage.persist();
  console.log(`Persistent storage: ${granted}`);
}
```

## Combining Strategies

A typical PWA uses multiple strategies together:

```ts
const runtimeCaching = [
  // Pages: Network First
  {
    urlPattern: ({ request }) => request.mode === "navigate",
    handler: new NetworkFirst({ cacheName: "pages" }),
  },

  // Static assets: Cache First
  {
    urlPattern: /\.(?:js|css|png|jpg|svg|woff2)$/i,
    handler: new CacheFirst({ cacheName: "assets" }),
  },

  // API: Network First with timeout
  {
    urlPattern: /\/api\/.*/i,
    handler: new NetworkFirst({
      cacheName: "api",
      networkTimeoutSeconds: 5,
    }),
  },

  // Everything else: SWR
  {
    urlPattern: /.*/i,
    handler: new StaleWhileRevalidate({ cacheName: "fallback" }),
  },
];
```
