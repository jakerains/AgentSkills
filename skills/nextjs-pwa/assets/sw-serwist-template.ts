import { defaultCache } from "@serwist/next/worker";
import type { PrecacheEntry, SerwistGlobalConfig } from "serwist";
import { CacheFirst, NetworkFirst, Serwist, StaleWhileRevalidate } from "serwist";

declare global {
  interface WorkerGlobalScope extends SerwistGlobalConfig {
    __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
  }
}

declare const self: ServiceWorkerGlobalScope;

const serwist = new Serwist({
  precacheEntries: self.__SW_MANIFEST,
  skipWaiting: true,
  clientsClaim: true,
  navigationPreload: true,
  runtimeCaching: [
    // Use Serwist defaults as a base
    ...defaultCache,

    // Example: Cache API responses with Network First
    {
      urlPattern: /^https:\/\/api\.example\.com\/.*/i,
      handler: new NetworkFirst({
        cacheName: "api-cache",
        networkTimeoutSeconds: 10,
        plugins: [],
      }),
    },

    // Example: Cache images with Cache First
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif)$/i,
      handler: new CacheFirst({
        cacheName: "image-cache",
        plugins: [],
      }),
    },

    // Example: Cache fonts with Stale While Revalidate
    {
      urlPattern: /\.(?:woff|woff2|ttf|otf|eot)$/i,
      handler: new StaleWhileRevalidate({
        cacheName: "font-cache",
      }),
    },
  ],

  // Offline fallback — serve this when navigation fails
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

// Handle push notifications
self.addEventListener("push", (event) => {
  const data = event.data?.json() ?? {
    title: "Notification",
    body: "You have a new notification",
  };

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-72.png",
      tag: data.tag ?? "default",
      data: data.data,
    })
  );
});

// Handle notification clicks
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const targetUrl = event.notification.data?.url ?? "/";

  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      for (const client of clients) {
        if (client.url === targetUrl && "focus" in client) {
          return client.focus();
        }
      }
      return self.clients.openWindow(targetUrl);
    })
  );
});

serwist.addEventListeners();
