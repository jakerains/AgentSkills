# Manual Service Worker — No Dependencies

## Overview

This guide covers writing a service worker from scratch without Serwist, Workbox, or any other library. Use this approach when:

- You need zero dependencies
- You're using `output: "export"` (static export)
- You want full control over caching behavior
- Your PWA needs are minimal (just installable + basic offline)

## Project Structure

```
app/
├── manifest.ts                    # Web app manifest
├── components/
│   └── ServiceWorkerRegistration.tsx  # SW registration component
├── offline/
│   └── page.tsx                   # Offline fallback page
└── layout.tsx                     # Root layout
public/
└── sw.js                          # Service worker (plain JS)
```

## Registration

### Basic registration

```tsx
// app/components/ServiceWorkerRegistration.tsx
"use client";

import { useEffect } from "react";

export function ServiceWorkerRegistration() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker
        .register("/sw.js", { scope: "/" })
        .then((reg) => {
          console.log("SW registered:", reg.scope);
        })
        .catch((err) => {
          console.error("SW registration failed:", err);
        });
    }
  }, []);

  return null;
}
```

### Registration with update detection

```tsx
"use client";

import { useEffect, useState } from "react";

export function ServiceWorkerRegistration() {
  const [updateAvailable, setUpdateAvailable] = useState(false);

  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;

    navigator.serviceWorker.register("/sw.js").then((reg) => {
      // Check for updates periodically
      setInterval(() => reg.update(), 60 * 60 * 1000); // every hour

      reg.addEventListener("updatefound", () => {
        const newWorker = reg.installing;
        if (!newWorker) return;

        newWorker.addEventListener("statechange", () => {
          if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
            // New SW installed but waiting — show update prompt
            setUpdateAvailable(true);
          }
        });
      });
    });

    // Handle controller change (new SW took over)
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      window.location.reload();
    });
  }, []);

  if (!updateAvailable) return null;

  return (
    <div style={{
      position: "fixed",
      bottom: "16px",
      right: "16px",
      padding: "12px 20px",
      background: "#1a1a1a",
      color: "#fff",
      borderRadius: "8px",
      zIndex: 9999,
      display: "flex",
      gap: "12px",
      alignItems: "center",
    }}>
      <span>Update available</span>
      <button
        onClick={() => {
          navigator.serviceWorker.ready.then((reg) => {
            reg.waiting?.postMessage({ type: "SKIP_WAITING" });
          });
        }}
        style={{
          background: "#fff",
          color: "#1a1a1a",
          border: "none",
          padding: "6px 12px",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Reload
      </button>
    </div>
  );
}
```

## Complete Service Worker

```js
// public/sw.js

const CACHE_VERSION = "v1";
const CACHE_NAME = `app-${CACHE_VERSION}`;

// Assets to precache on install
const PRECACHE_URLS = [
  "/",
  "/offline",
];

// ============ Install ============
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ============ Activate ============
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ============ Message handling ============
self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

// ============ Fetch ============
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle GET requests from same origin
  if (request.method !== "GET") return;
  if (url.origin !== self.location.origin) return;

  // Choose strategy based on request type
  if (request.mode === "navigate") {
    event.respondWith(networkFirstWithFallback(request));
  } else if (isStaticAsset(request)) {
    event.respondWith(cacheFirst(request));
  } else if (url.pathname.startsWith("/api/")) {
    event.respondWith(networkFirst(request));
  } else {
    event.respondWith(staleWhileRevalidate(request));
  }
});

// ============ Strategies ============

// Network First — try network, fall back to cache
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return (await caches.match(request)) || new Response("Offline", { status: 503 });
  }
}

// Network First with offline page fallback (for navigation)
async function networkFirstWithFallback(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || (await caches.match("/offline")) || new Response("Offline", { status: 503 });
  }
}

// Cache First — check cache, fall back to network
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response("", { status: 408 });
  }
}

// Stale While Revalidate — return cache, update in background
async function staleWhileRevalidate(request) {
  const cached = await caches.match(request);

  const fetchPromise = fetch(request)
    .then((response) => {
      if (response.ok) {
        const cache = caches.open(CACHE_NAME);
        cache.then((c) => c.put(request, response.clone()));
      }
      return response;
    })
    .catch(() => null);

  return cached || (await fetchPromise) || new Response("", { status: 408 });
}

// ============ Helpers ============

function isStaticAsset(request) {
  const dest = request.destination;
  return (
    dest === "style" ||
    dest === "script" ||
    dest === "image" ||
    dest === "font" ||
    dest === "audio" ||
    dest === "video"
  );
}
```

## Cache Versioning

When you deploy new content, update `CACHE_VERSION`:

```js
const CACHE_VERSION = "v2"; // bumped from "v1"
```

On activate, old caches are deleted automatically (see the activate handler above).

For content-hashed assets (like Next.js build output), cache versioning is less important since filenames change on update.

## Scope

### Default scope

A SW at `/sw.js` has scope `/` — it controls all pages on the origin.

### Custom scope

```tsx
navigator.serviceWorker.register("/sw.js", { scope: "/app/" });
```

This SW only controls pages under `/app/`.

### Scope restrictions

- SW can only control pages at or below its location
- `/js/sw.js` can only control `/js/*` by default
- To extend scope, the server must send `Service-Worker-Allowed: /` header

### Next.js scope with basePath

If your Next.js app uses `basePath: "/myapp"`:

```tsx
navigator.serviceWorker.register("/myapp/sw.js", { scope: "/myapp/" });
```

And place `sw.js` in `public/` — Next.js serves it at `/myapp/sw.js`.

## Adding Push Notifications

Add these handlers to your `sw.js`:

```js
// Push event
self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : { title: "Notification" };

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body || "",
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-72.png",
      tag: data.tag || "default",
      data: { url: data.url || "/" },
    })
  );
});

// Notification click
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      const url = event.notification.data?.url || "/";
      for (const client of clients) {
        if (client.url === url && "focus" in client) {
          return client.focus();
        }
      }
      return self.clients.openWindow(url);
    })
  );
});
```

## Static Export Considerations

When using `output: "export"`:

1. No server — all files are static HTML/JS/CSS
2. SW must be in `public/sw.js` (no build step compilation)
3. Precache the actual HTML files:

```js
const PRECACHE_URLS = [
  "/",
  "/index.html",
  "/about.html",
  "/offline.html",
];
```

4. Navigation handling should check for `.html` suffix:

```js
if (request.mode === "navigate") {
  event.respondWith(
    fetch(request).catch(async () => {
      // Try with .html suffix
      const htmlUrl = request.url.endsWith("/")
        ? request.url + "index.html"
        : request.url + ".html";
      const cached = await caches.match(htmlUrl);
      return cached || caches.match("/offline.html");
    })
  );
}
```

## Debugging

### Check SW status

```js
// In browser console
navigator.serviceWorker.getRegistration().then(console.log);
```

### Force update

```js
navigator.serviceWorker.getRegistration().then((reg) => reg?.update());
```

### Unregister

```js
navigator.serviceWorker.getRegistration().then((reg) => reg?.unregister());
```

### Clear all caches

```js
caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
```
