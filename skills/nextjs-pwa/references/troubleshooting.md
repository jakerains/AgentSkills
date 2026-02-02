# PWA Troubleshooting Guide

## Service Worker Not Updating

### Symptoms
- Old content showing after deploy
- Console shows old SW version
- Changes not reflected even after refresh

### Fixes

1. **Add `skipWaiting: true`** to your Serwist config or call `self.skipWaiting()` in the install event
2. **Hard refresh:** Shift+Cmd+R (Mac) or Shift+Ctrl+R (Windows)
3. **Clear SW in DevTools:** Application → Service Workers → Unregister
4. **Check "Update on reload"** in DevTools → Application → Service Workers during development
5. **Verify disable in dev:**
```ts
withSerwist({
  disable: process.env.NODE_ENV === "development",
})
```

### Why it happens
By default, a new SW waits until all tabs using the old SW are closed. `skipWaiting` bypasses this but may cause issues if the new SW is incompatible with cached assets from the old version.

---

## App Not Installable

### Lighthouse says "Web app manifest does not meet the installability requirements"

**Checklist:**
- [ ] HTTPS (or localhost for dev)
- [ ] Valid manifest with required fields: `name`, `icons`, `start_url`, `display`
- [ ] At least one icon ≥192x192 and one ≥512x512
- [ ] `display` is `standalone`, `fullscreen`, or `minimal-ui`
- [ ] Registered service worker with a `fetch` event handler
- [ ] The SW `fetch` handler returns a 200 OK while offline (for the start URL)

**Quick diagnostic in console:**
```js
// Check manifest
const res = await fetch('/manifest.webmanifest');
const manifest = await res.json();
console.log(manifest);

// Check SW
const reg = await navigator.serviceWorker.getRegistration();
console.log('SW:', reg?.active?.scriptURL);
```

### `beforeinstallprompt` not firing

- Only fires on Chrome, Edge, and Samsung Internet
- Does NOT fire on Firefox or Safari (they have their own install mechanisms)
- Only fires over HTTPS
- Only fires once per page load — if dismissed, won't fire again for a while
- Check DevTools → Application → Manifest for installability status

---

## Stale Cache After Deploy

### Symptoms
- Users see old version after deploy
- Only new visitors get the update
- Hard refresh fixes it temporarily

### Fixes

**With Serwist:** Content-hashed filenames handle this automatically. The new build generates new filenames, and Serwist precaches them.

**With manual SW:** Bump the cache version:
```js
const CACHE_VERSION = "v2"; // was "v1"
const CACHE_NAME = `app-${CACHE_VERSION}`;
```

**Nuclear option — clear all caches:**
```js
// In your app (not SW)
async function clearAllCaches() {
  const keys = await caches.keys();
  await Promise.all(keys.map(k => caches.delete(k)));
  const reg = await navigator.serviceWorker.getRegistration();
  await reg?.unregister();
  window.location.reload();
}
```

---

## SW Works in Dev but Fails in Production

### Common causes

1. **Different base paths:** Check if your app uses `basePath` in Next.js config — the SW scope must account for it
2. **CDN stripping headers:** Some CDNs modify the `Service-Worker-Allowed` header
3. **CORS issues:** SW can only cache same-origin requests by default. Cross-origin requires `{mode: "cors"}` and proper CORS headers
4. **Middleware conflicts:** Next.js middleware can interfere with SW requests. Exclude the SW path:
```ts
// middleware.ts
export const config = {
  matcher: ["/((?!sw\\.js|workbox-.*).*)"],
};
```

---

## Lighthouse PWA Audit Failures

### "Does not register a service worker that controls page and start_url"

- SW must be registered and active
- SW must have a `fetch` event listener
- Check `navigator.serviceWorker.controller` is not null

### "Current page does not respond with a 200 when offline"

- The SW must return a valid response for the current page while offline
- Add an offline fallback or precache the page
- Test: DevTools → Network → Offline → Reload

### "Does not redirect HTTP traffic to HTTPS"

- Not a SW issue — configure HTTPS redirect on your server/hosting
- Vercel, Netlify, Cloudflare do this automatically

### "Manifest doesn't have a maskable icon"

Add a maskable icon to your manifest:
```ts
{ src: "/icon-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" }
```

Use https://maskable.app to test your maskable icons.

---

## Next.js-Specific Issues

### SW conflicts with Next.js routing

**Problem:** SW intercepts `_next/data/*.json` requests and serves stale data.

**Fix:** Use Serwist `defaultCache` which handles Next.js data requests correctly, or exclude them in manual SW:
```js
if (url.pathname.startsWith("/_next/data/")) {
  // Network First for data requests
  event.respondWith(networkFirst(event.request, "next-data"));
  return;
}
```

### SW conflicts with next.config.js rewrites

**Problem:** Rewrites redirect `/sw.js` to another path.

**Fix:** Add the SW to your rewrites exclusion or serve it directly:
```ts
// next.config.ts
const nextConfig = {
  async rewrites() {
    return {
      beforeFiles: [
        // Your rewrites
      ],
      // SW is served from public/ — not affected by rewrites
    };
  },
};
```

### ISR/SSG pages show stale content

**Problem:** Cached pages don't reflect ISR revalidation.

**Fix:** Use Network First for HTML navigations:
```ts
{
  urlPattern: ({ request }) => request.mode === "navigate",
  handler: new NetworkFirst({
    cacheName: "pages",
    networkTimeoutSeconds: 3,
  }),
}
```

### App Router streaming and SW

**Problem:** SW interferes with React Server Component streaming.

**Fix:** The Serwist `defaultCache` handles this correctly. If using manual SW, don't cache streaming responses — let them pass through:
```js
if (request.headers.get("RSC")) return; // Let RSC requests pass through
```

---

## Development Tips

### Disable SW in development

```ts
// next.config.ts
withSerwist({
  disable: process.env.NODE_ENV === "development",
})
```

### Quick SW reset in browser

1. DevTools → Application → Service Workers → Unregister
2. DevTools → Application → Clear Storage → Clear site data
3. Or in console: `navigator.serviceWorker.getRegistration().then(r => r?.unregister())`

### Test offline behavior

1. DevTools → Network tab → Throttling → Offline
2. Or DevTools → Application → Service Workers → Offline checkbox
3. Then reload the page

### Inspect cached content

DevTools → Application → Cache Storage → expand each cache to see entries

### Debug SW code

1. DevTools → Sources → Service Worker section
2. Add breakpoints in your SW code
3. Use `console.log` in SW — logs appear in the main console (with SW source tag)

---

## Browser-Specific Issues

### Safari/iOS

See references/ios-quirks.md for comprehensive Safari/iOS issues.

Key issues:
- No background sync support
- Push requires app added to home screen (iOS 16.4+)
- Aggressive cache eviction (~50MB limit)
- No `beforeinstallprompt` event

### Firefox

- Supports PWA install on Android but NOT on desktop
- SW scope is strict — no `Service-Worker-Allowed` header support
- Cache storage limited to ~50% of free disk

### Samsung Internet

- Good PWA support, similar to Chrome
- WebAPK install available
- Supports `beforeinstallprompt`

---

## Performance Debugging

### Measure cache hit rate

```js
// In SW
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        console.log("[Cache HIT]", event.request.url);
        return cached;
      }
      console.log("[Cache MISS]", event.request.url);
      return fetch(event.request);
    })
  );
});
```

### Check cache size

```js
async function getCacheSize() {
  const keys = await caches.keys();
  for (const key of keys) {
    const cache = await caches.open(key);
    const requests = await cache.keys();
    console.log(`${key}: ${requests.length} entries`);
  }
}
```

### Storage estimate

```js
const { usage, quota } = await navigator.storage.estimate();
console.log(`Storage: ${(usage / 1024 / 1024).toFixed(2)}MB / ${(quota / 1024 / 1024).toFixed(2)}MB`);
```
