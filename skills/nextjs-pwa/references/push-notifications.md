# Push Notifications — Complete Guide

## Overview

Web push notifications allow your PWA to send messages to users even when the app isn't open. The flow:

1. Client subscribes to push via the Push API
2. Subscription endpoint is sent to your server
3. Server sends push messages via web-push protocol (VAPID)
4. Service worker receives push events and shows notifications

## Prerequisites

- HTTPS (required for Push API)
- Registered service worker
- User grants notification permission
- VAPID keys generated

## Step 1: Generate VAPID Keys

```bash
npx web-push generate-vapid-keys
```

Output:
```
Public Key:  BLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Private Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Store these as environment variables:
```env
NEXT_PUBLIC_VAPID_PUBLIC_KEY=BLxxxxxx...
VAPID_PRIVATE_KEY=xxxxxxxx...
VAPID_SUBJECT=mailto:your@email.com
```

## Step 2: Client-Side Subscription

### Request permission and subscribe

```tsx
"use client";

import { useState, useEffect } from "react";

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64);
  const array = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) {
    array[i] = raw.charCodeAt(i);
  }
  return array;
}

export function PushNotificationManager() {
  const [isSupported, setIsSupported] = useState(false);
  const [subscription, setSubscription] = useState<PushSubscription | null>(null);
  const [permission, setPermission] = useState<NotificationPermission>("default");

  useEffect(() => {
    if ("serviceWorker" in navigator && "PushManager" in window) {
      setIsSupported(true);
      setPermission(Notification.permission);

      // Check existing subscription
      navigator.serviceWorker.ready.then((reg) => {
        reg.pushManager.getSubscription().then(setSubscription);
      });
    }
  }, []);

  async function subscribe() {
    const perm = await Notification.requestPermission();
    setPermission(perm);
    if (perm !== "granted") return;

    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!
      ),
    });

    setSubscription(sub);

    // Send subscription to server
    await fetch("/api/push/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(sub.toJSON()),
    });
  }

  async function unsubscribe() {
    if (subscription) {
      await subscription.unsubscribe();

      // Notify server
      await fetch("/api/push/unsubscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
      });

      setSubscription(null);
    }
  }

  if (!isSupported) return <p>Push notifications not supported</p>;

  return (
    <div>
      {permission === "denied" && <p>Notifications blocked. Enable in browser settings.</p>}
      {!subscription ? (
        <button onClick={subscribe}>Enable Notifications</button>
      ) : (
        <button onClick={unsubscribe}>Disable Notifications</button>
      )}
    </div>
  );
}
```

## Step 3: Service Worker Push Handler

```ts
// In your sw.ts or sw.js

self.addEventListener("push", (event) => {
  if (!event.data) return;

  const data = event.data.json();

  const options: NotificationOptions = {
    body: data.body,
    icon: data.icon || "/icons/icon-192.png",
    badge: data.badge || "/icons/icon-72.png",
    image: data.image,        // Large image below the notification
    tag: data.tag || "default", // Group notifications with same tag
    renotify: data.renotify || false, // Vibrate again for same tag
    requireInteraction: data.requireInteraction || false,
    silent: data.silent || false,
    data: {
      url: data.url || "/",   // URL to open on click
      ...data.data,
    },
    actions: data.actions || [],
    // Example actions:
    // actions: [
    //   { action: "open", title: "Open" },
    //   { action: "dismiss", title: "Dismiss" },
    // ],
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Handle notification click
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const action = event.action; // Which action button was clicked
  const url = event.notification.data?.url || "/";

  if (action === "dismiss") return;

  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((clients) => {
      // Try to focus an existing window
      for (const client of clients) {
        if (client.url === url && "focus" in client) {
          return client.focus();
        }
      }
      // Open new window
      return self.clients.openWindow(url);
    })
  );
});

// Handle notification close (dismissed without clicking)
self.addEventListener("notificationclose", (event) => {
  // Optional: track dismissals
  console.log("Notification dismissed:", event.notification.tag);
});
```

## Step 4: Server-Side Sending

### Install web-push

```bash
npm install web-push
```

### API route: Subscribe

```ts
// app/api/push/subscribe/route.ts
import { NextRequest, NextResponse } from "next/server";

// In production, store subscriptions in a database
const subscriptions: Map<string, PushSubscription> = new Map();

export async function POST(request: NextRequest) {
  const subscription = await request.json();
  subscriptions.set(subscription.endpoint, subscription);
  return NextResponse.json({ success: true });
}
```

### API route: Send notification

```ts
// app/api/push/send/route.ts
import { NextRequest, NextResponse } from "next/server";
import webpush from "web-push";

webpush.setVapidDetails(
  process.env.VAPID_SUBJECT!,           // mailto:your@email.com
  process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!,
  process.env.VAPID_PRIVATE_KEY!
);

export async function POST(request: NextRequest) {
  const { subscription, payload } = await request.json();

  try {
    await webpush.sendNotification(
      subscription,
      JSON.stringify({
        title: payload.title,
        body: payload.body,
        icon: payload.icon,
        url: payload.url,
        tag: payload.tag,
      })
    );
    return NextResponse.json({ success: true });
  } catch (error: any) {
    // Handle expired subscriptions
    if (error.statusCode === 410 || error.statusCode === 404) {
      // Remove subscription from database
      return NextResponse.json({ error: "Subscription expired" }, { status: 410 });
    }
    return NextResponse.json({ error: "Failed to send" }, { status: 500 });
  }
}
```

### Send to all subscribers

```ts
// app/api/push/broadcast/route.ts
import webpush from "web-push";

export async function POST(request: NextRequest) {
  const { title, body, url } = await request.json();
  const payload = JSON.stringify({ title, body, url });

  // Get all subscriptions from your database
  const subscriptions = await getSubscriptionsFromDB();

  const results = await Promise.allSettled(
    subscriptions.map((sub) => webpush.sendNotification(sub, payload))
  );

  // Clean up expired subscriptions
  const expired = results
    .map((r, i) => (r.status === "rejected" ? i : -1))
    .filter((i) => i >= 0);

  return NextResponse.json({
    sent: results.filter((r) => r.status === "fulfilled").length,
    failed: expired.length,
  });
}
```

## Notification Options Reference

```ts
{
  body: "Notification text",
  icon: "/icon-192.png",             // Small icon (64x64 recommended)
  badge: "/badge-72.png",            // Monochrome icon for status bar (Android)
  image: "/hero.jpg",                // Large image displayed in notification
  tag: "message-group-1",            // Replace notifications with same tag
  renotify: true,                    // Vibrate again when replacing
  requireInteraction: false,         // Keep visible until user interacts
  silent: false,                     // No sound/vibration
  timestamp: Date.now(),             // When the event occurred
  vibrate: [200, 100, 200],          // Vibration pattern (ms)
  dir: "auto",                       // Text direction: auto | ltr | rtl
  lang: "en",                        // Language
  data: { url: "/messages/123" },    // Custom data for click handler
  actions: [                         // Action buttons (max 2 on most platforms)
    { action: "reply", title: "Reply", icon: "/reply.png" },
    { action: "archive", title: "Archive", icon: "/archive.png" },
  ],
}
```

## Browser Support Matrix

| Feature | Chrome | Firefox | Safari | Edge | Samsung |
|---------|--------|---------|--------|------|---------|
| Push API | Yes | Yes | iOS 16.4+ | Yes | Yes |
| Notification actions | Yes | No | No | Yes | Yes |
| Notification image | Yes (Android) | No | No | Yes | Yes |
| Badge icon | Yes (Android) | No | No | Yes | Yes |
| Silent push | Yes | Yes | No | Yes | Yes |
| Background push | Yes | Yes | Limited | Yes | Yes |

## iOS/Safari Considerations

- Push requires the app to be added to home screen (iOS 16.4+)
- Must request permission from a user gesture (button click)
- No notification actions support
- No badge/image support
- Push delivery may be delayed by iOS power management
- See references/ios-quirks.md for full details

## Best Practices

### Permission UX

1. **Don't ask immediately** — users dismiss permission prompts they don't understand
2. **Explain the value first** — show a custom UI explaining what notifications they'll receive
3. **Ask on relevant actions** — "Want to be notified when your order ships?" > generic "Enable notifications"
4. **Respect denial** — if permission is denied, don't keep asking. Show how to re-enable in settings

### Payload structure

Keep payloads under 4KB (browser limit varies, but 4KB is safe across all browsers).

```ts
// Good — small, actionable
{ title: "New message", body: "Alice: Hey, are you free?", url: "/chat/alice" }

// Bad — too much data
{ title: "...", body: "...", fullMessage: "...(2KB of text)..." }
```

### Error handling

Always handle expired/invalid subscriptions:
```ts
try {
  await webpush.sendNotification(sub, payload);
} catch (err) {
  if (err.statusCode === 404 || err.statusCode === 410) {
    await removeSubscription(sub.endpoint);
  }
}
```

### Rate limiting

- Don't spam users
- Batch updates (e.g., "5 new messages" vs 5 separate notifications)
- Use `tag` to replace rather than stack notifications
- Respect quiet hours (implement server-side)
