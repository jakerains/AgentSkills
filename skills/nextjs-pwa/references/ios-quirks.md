# iOS/Safari PWA Quirks and Workarounds

## Overview

iOS Safari has limited PWA support compared to Chrome/Android. This document covers all the key differences, limitations, and workarounds.

## Installation

### No `beforeinstallprompt`

iOS does not fire the `beforeinstallprompt` event. You need to detect iOS and show manual instructions.

```tsx
"use client";

import { useState, useEffect } from "react";

function isIOS(): boolean {
  if (typeof navigator === "undefined") return false;
  return /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as any).MSStream;
}

function isInStandaloneMode(): boolean {
  if (typeof window === "undefined") return false;
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    (navigator as any).standalone === true
  );
}

export function IOSInstallPrompt() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    setShow(isIOS() && !isInStandaloneMode());
  }, []);

  if (!show) return null;

  return (
    <div style={{
      position: "fixed",
      bottom: 0,
      left: 0,
      right: 0,
      padding: "16px",
      backgroundColor: "#f8f9fa",
      borderTop: "1px solid #dee2e6",
      textAlign: "center",
      zIndex: 9999,
    }}>
      <p>
        Install this app: tap{" "}
        <span style={{ fontSize: "1.2em" }}>⎙</span> Share then{" "}
        <strong>Add to Home Screen</strong>
      </p>
      <button onClick={() => setShow(false)}>Dismiss</button>
    </div>
  );
}
```

## Push Notifications (iOS 16.4+)

### Requirements
- App MUST be added to home screen first
- Permission must be requested from a user gesture (button click)
- Cannot request permission from page load
- User must be on iOS 16.4 or later

### Detection

```ts
function supportsPushOnIOS(): boolean {
  if (!isIOS()) return true; // Not iOS, assume supported
  const match = navigator.userAgent.match(/OS (\d+)_/);
  if (!match) return false;
  return parseInt(match[1], 10) >= 16;
}

function isRunningAsApp(): boolean {
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    (navigator as any).standalone === true
  );
}

// Push only works if: iOS 16.4+ AND running as installed app
function canUsePushOnIOS(): boolean {
  return supportsPushOnIOS() && isRunningAsApp();
}
```

### Limitations
- No notification actions (buttons)
- No notification images
- No badge icons
- No silent push
- Delivery may be delayed by iOS power management
- No background push when app is not in recent apps

## Storage and Cache Eviction

### iOS storage limits
- ~50MB per origin for Cache API
- ~1GB for IndexedDB (but evicted under storage pressure)
- iOS aggressively evicts data for sites not used recently (~7 days)

### Mitigations

1. **Request persistent storage** (may not work on iOS, but worth trying):
```ts
if (navigator.storage?.persist) {
  await navigator.storage.persist();
}
```

2. **Keep the app lightweight** — stay well under 50MB total cache
3. **Rebuild caches on activation** — assume caches may be evicted:
```ts
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CRITICAL_URLS);
    })
  );
});
```

4. **Store critical data in IndexedDB** — it's less aggressively evicted than Cache API

## No Background Sync

iOS Safari does not support the Background Sync API. The service worker cannot process queued requests after the page is closed.

### Workaround

Process the sync queue when the app is opened:

```tsx
"use client";

import { useEffect } from "react";
import { processQueue } from "@/lib/sync-queue";

export function IOSSyncOnFocus() {
  useEffect(() => {
    const handleFocus = () => {
      if (navigator.onLine) processQueue();
    };

    window.addEventListener("focus", handleFocus);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible" && navigator.onLine) {
        processQueue();
      }
    });

    return () => {
      window.removeEventListener("focus", handleFocus);
    };
  }, []);

  return null;
}
```

## Viewport and Safe Areas

### Status bar and notch handling

```tsx
// app/layout.tsx
export const metadata = {
  other: {
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "black-translucent",
  },
};
```

### Safe area insets

```css
/* Handle notch/Dynamic Island on iOS */
body {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Or for specific elements */
.bottom-nav {
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}
```

### Viewport meta tag

```tsx
// app/layout.tsx
export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  viewportFit: "cover", // Required for safe-area-inset to work
};
```

## Splash Screens

iOS generates splash screens from the manifest, but you can also use Apple-specific meta tags for more control.

### Using manifest (recommended)

The manifest `background_color` and `icons` are used. Works for most cases.

### Apple-specific splash images

For pixel-perfect splash screens, use `apple-touch-startup-image` links:

```tsx
// app/layout.tsx
export const metadata = {
  other: {
    "apple-mobile-web-app-capable": "yes",
  },
};
```

```html
<!-- In <head> — add for each device size -->
<link
  rel="apple-touch-startup-image"
  media="(device-width: 430px) and (device-height: 932px) and (-webkit-device-pixel-ratio: 3)"
  href="/splash/iPhone_15_Pro_Max.png"
/>
```

This is tedious — use a generator tool or just rely on the manifest approach.

## Apple Touch Icon

Always provide an apple-touch-icon for the home screen:

```tsx
// app/layout.tsx
export const metadata = {
  icons: {
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180" },
    ],
  },
};
```

The icon should be 180x180px, PNG, no transparency (iOS adds its own mask).

## Navigation Gestures

### Swipe-back gesture

In standalone mode, iOS allows swipe-from-edge to go back. This can conflict with your app's gestures.

```css
/* Disable overscroll bounce (may help with gesture conflicts) */
html, body {
  overscroll-behavior: none;
}
```

### Pull-to-refresh

Safari shows a pull-to-refresh animation in standalone mode. Disable if unwanted:

```css
body {
  overscroll-behavior-y: none;
}
```

## Audio/Video

### Autoplay restrictions
- Audio/video won't autoplay without user interaction
- Web Audio API requires a user gesture to resume AudioContext
- This applies in both Safari and standalone mode

### Media session
iOS supports limited Media Session API in standalone mode:
```ts
navigator.mediaSession.metadata = new MediaMetadata({
  title: "Song Title",
  artist: "Artist",
  artwork: [{ src: "/album-art.jpg", sizes: "512x512", type: "image/jpeg" }],
});
```

## Debugging on iOS

### Safari Web Inspector

1. On iPhone: Settings → Safari → Advanced → Web Inspector: ON
2. Connect iPhone to Mac via USB
3. On Mac: Safari → Develop → [Your iPhone] → [Your PWA]

### Standalone mode debugging

When the PWA is running as a standalone app:
1. The app appears under the device name in Safari's Develop menu
2. You can inspect, console.log, and debug as normal
3. Note: standalone mode doesn't show the URL bar, so check `window.location` in console

## Feature Support Summary

| Feature | iOS Safari | Chrome Android |
|---------|-----------|----------------|
| Install prompt | Manual | `beforeinstallprompt` |
| Push notifications | 16.4+ (home screen only) | Yes |
| Background sync | No | Yes |
| Periodic background sync | No | Yes |
| Cache storage | ~50MB | ~60% disk |
| IndexedDB | ~1GB (evictable) | ~60% disk |
| Notification actions | No | Yes |
| Badge API | No | Yes |
| Web Share API | Yes | Yes |
| Web Share Target | No | Yes |
| Geolocation (background) | No | Limited |
| Persistent storage | Limited | Yes |
