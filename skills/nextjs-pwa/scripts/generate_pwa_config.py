#!/usr/bin/env python3
"""Generate PWA configuration files for a Next.js project.

Usage:
    python generate_pwa_config.py <project-name> --approach serwist|manual [--push] [--offline]

Examples:
    python generate_pwa_config.py my-app --approach serwist
    python generate_pwa_config.py my-app --approach manual --push --offline
"""

import argparse
import os
import sys
import textwrap


def write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created {path}")


def generate_manifest(project_name: str, base: str) -> None:
    content = textwrap.dedent(f'''\
        import type {{ MetadataRoute }} from "next";

        export default function manifest(): MetadataRoute.Manifest {{
          return {{
            name: "{project_name}",
            short_name: "{project_name[:12]}",
            description: "A Progressive Web App built with Next.js",
            start_url: "/",
            display: "standalone",
            background_color: "#ffffff",
            theme_color: "#000000",
            icons: [
              {{ src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" }},
              {{ src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" }},
              {{
                src: "/icons/icon-maskable-512.png",
                sizes: "512x512",
                type: "image/png",
                purpose: "maskable",
              }},
            ],
          }};
        }}
    ''')
    write_file(os.path.join(base, "app", "manifest.ts"), content)


def generate_offline_page(base: str) -> None:
    content = textwrap.dedent('''\
        export default function OfflinePage() {
          return (
            <main style={{ textAlign: "center", padding: "4rem 1rem" }}>
              <h1>You are offline</h1>
              <p>Check your internet connection and try again.</p>
              <button onClick={() => window.location.reload()}>Retry</button>
            </main>
          );
        }
    ''')
    write_file(os.path.join(base, "app", "offline", "page.tsx"), content)


def generate_serwist_sw(base: str, push: bool) -> None:
    push_handlers = ""
    if push:
        push_handlers = textwrap.dedent('''

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
        ''')

    content = textwrap.dedent(f'''\
        import {{ defaultCache }} from "@serwist/next/worker";
        import type {{ PrecacheEntry, SerwistGlobalConfig }} from "serwist";
        import {{ Serwist }} from "serwist";

        declare global {{
          interface WorkerGlobalScope extends SerwistGlobalConfig {{
            __SW_MANIFEST: (PrecacheEntry | string)[] | undefined;
          }}
        }}

        declare const self: ServiceWorkerGlobalScope;

        const serwist = new Serwist({{
          precacheEntries: self.__SW_MANIFEST,
          skipWaiting: true,
          clientsClaim: true,
          navigationPreload: true,
          runtimeCaching: defaultCache,
          fallbacks: {{
            entries: [
              {{
                url: "/offline",
                matcher({{ request }}) {{
                  return request.destination === "document";
                }},
              }},
            ],
          }},
        }});
        {push_handlers}
        serwist.addEventListeners();
    ''')
    write_file(os.path.join(base, "app", "sw.ts"), content)


def generate_serwist_config(base: str) -> None:
    content = textwrap.dedent('''\
        import withSerwist from "@serwist/next";
        import type { NextConfig } from "next";

        const nextConfig: NextConfig = {
          // Your existing Next.js config here
        };

        export default withSerwist({
          swSrc: "app/sw.ts",
          swDest: "public/sw.js",
          disable: process.env.NODE_ENV === "development",
        })(nextConfig);
    ''')
    write_file(os.path.join(base, "next.config.ts"), content)


def generate_manual_sw(base: str, push: bool) -> None:
    push_handlers = ""
    if push:
        push_handlers = textwrap.dedent('''
        // ------- Push Notifications -------
        self.addEventListener("push", (event) => {
          const data = event.data ? event.data.json() : { title: "Notification" };

          event.waitUntil(
            self.registration.showNotification(data.title, {
              body: data.body || "",
              icon: "/icons/icon-192.png",
              badge: "/icons/icon-72.png",
              tag: data.tag || "default",
              data: data.data,
            })
          );
        });

        self.addEventListener("notificationclick", (event) => {
          event.notification.close();
          const targetUrl = event.notification.data?.url || "/";

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
        ''')

    content = textwrap.dedent(f'''\
        const CACHE_VERSION = "v1";
        const CACHE_NAME = `app-${{CACHE_VERSION}}`;

        const PRECACHE_URLS = ["/", "/offline"];

        self.addEventListener("install", (event) => {{
          event.waitUntil(
            caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
          );
          self.skipWaiting();
        }});

        self.addEventListener("activate", (event) => {{
          event.waitUntil(
            caches.keys().then((keys) =>
              Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
              )
            )
          );
          self.clients.claim();
        }});

        self.addEventListener("fetch", (event) => {{
          const {{ request }} = event;
          const url = new URL(request.url);

          if (request.method !== "GET") return;
          if (url.origin !== self.location.origin) return;

          if (request.mode === "navigate") {{
            event.respondWith(
              fetch(request)
                .then((response) => {{
                  const clone = response.clone();
                  caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                  return response;
                }})
                .catch(() => caches.match("/offline"))
            );
            return;
          }}

          event.respondWith(
            caches.match(request).then((cached) => cached || fetch(request))
          );
        }});
        {push_handlers}
    ''')
    write_file(os.path.join(base, "public", "sw.js"), content)


def generate_sw_registration(base: str) -> None:
    content = textwrap.dedent('''\
        "use client";

        import { useEffect } from "react";

        export function ServiceWorkerRegistration() {
          useEffect(() => {
            if ("serviceWorker" in navigator) {
              navigator.serviceWorker.register("/sw.js").catch((err) => {
                console.error("SW registration failed:", err);
              });
            }
          }, []);

          return null;
        }
    ''')
    write_file(
        os.path.join(base, "app", "components", "ServiceWorkerRegistration.tsx"),
        content,
    )


def generate_online_hook(base: str) -> None:
    content = textwrap.dedent('''\
        "use client";

        import { useSyncExternalStore } from "react";

        function subscribe(callback: () => void) {
          window.addEventListener("online", callback);
          window.addEventListener("offline", callback);
          return () => {
            window.removeEventListener("online", callback);
            window.removeEventListener("offline", callback);
          };
        }

        export function useOnlineStatus() {
          return useSyncExternalStore(
            subscribe,
            () => navigator.onLine,
            () => true
          );
        }
    ''')
    write_file(os.path.join(base, "hooks", "useOnlineStatus.ts"), content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate PWA configuration for a Next.js project"
    )
    parser.add_argument("project_name", help="Project name")
    parser.add_argument(
        "--approach",
        choices=["serwist", "manual"],
        required=True,
        help="PWA approach: serwist (recommended) or manual (no deps)",
    )
    parser.add_argument(
        "--push", action="store_true", help="Include push notification handlers"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Include offline page and online status hook",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory (default: current directory)",
    )

    args = parser.parse_args()
    base = os.path.abspath(args.output)

    print(f"\nGenerating PWA config for '{args.project_name}' ({args.approach} approach)")
    print(f"Output directory: {base}\n")

    # Always generate manifest
    generate_manifest(args.project_name, base)

    # Approach-specific files
    if args.approach == "serwist":
        generate_serwist_sw(base, push=args.push)
        generate_serwist_config(base)
        print(f"\n  Install dependencies:")
        print(f"    npm install @serwist/next && npm install -D serwist")
    else:
        generate_manual_sw(base, push=args.push)
        generate_sw_registration(base)

    # Optional features
    if args.offline:
        generate_offline_page(base)
        generate_online_hook(base)

    if args.push:
        print(f"\n  Generate VAPID keys:")
        print(f"    npx web-push generate-vapid-keys")
        print(f"\n  Add to .env:")
        print(f"    NEXT_PUBLIC_VAPID_PUBLIC_KEY=...")
        print(f"    VAPID_PRIVATE_KEY=...")
        print(f"    VAPID_SUBJECT=mailto:your@email.com")
        if args.approach == "serwist":
            print(f"\n  Install web-push for server-side:")
            print(f"    npm install web-push")

    print(f"\nDone! Files generated successfully.")


if __name__ == "__main__":
    main()
