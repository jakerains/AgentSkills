# Offline Data — IndexedDB, Background Sync, and Offline Patterns

## Overview

For offline-capable PWAs, the Cache API handles asset caching, but structured data (user content, form submissions, application state) requires IndexedDB. This guide covers storing data offline and syncing when connectivity returns.

## IndexedDB with `idb`

The `idb` library provides a clean Promise-based wrapper over the IndexedDB API.

### Install

```bash
npm install idb
```

### Database setup

```ts
// lib/db.ts
import { openDB, type IDBPDatabase } from "idb";

interface AppDB {
  posts: {
    key: string;
    value: {
      id: string;
      title: string;
      body: string;
      synced: boolean;
      updatedAt: number;
    };
    indexes: { "by-synced": boolean };
  };
  syncQueue: {
    key: number;
    value: {
      id?: number;
      url: string;
      method: string;
      body: string;
      timestamp: number;
    };
  };
}

let dbPromise: Promise<IDBPDatabase<AppDB>> | null = null;

export function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<AppDB>("my-app", 1, {
      upgrade(db) {
        // Posts store
        const postStore = db.createObjectStore("posts", { keyPath: "id" });
        postStore.createIndex("by-synced", "synced");

        // Sync queue for offline mutations
        db.createObjectStore("syncQueue", {
          keyPath: "id",
          autoIncrement: true,
        });
      },
    });
  }
  return dbPromise;
}
```

### CRUD operations

```ts
// lib/db.ts (continued)

export async function getPosts() {
  const db = await getDB();
  return db.getAll("posts");
}

export async function getPost(id: string) {
  const db = await getDB();
  return db.get("posts", id);
}

export async function savePost(post: AppDB["posts"]["value"]) {
  const db = await getDB();
  await db.put("posts", { ...post, updatedAt: Date.now() });
}

export async function deletePost(id: string) {
  const db = await getDB();
  await db.delete("posts", id);
}

export async function getUnsyncedPosts() {
  const db = await getDB();
  return db.getAllFromIndex("posts", "by-synced", false);
}
```

### React hook for IndexedDB data

```tsx
// hooks/useIndexedDB.ts
"use client";

import { useState, useEffect, useCallback } from "react";

export function useIndexedDB<T>(
  fetcher: () => Promise<T>,
  deps: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      const result = await fetcher();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { data, loading, error, refresh };
}

// Usage:
// const { data: posts, refresh } = useIndexedDB(() => getPosts());
```

## Offline Mutation Queue

When the user performs actions while offline, queue them for later sync.

### Queue operations

```ts
// lib/sync-queue.ts
import { getDB } from "./db";

export async function queueRequest(url: string, method: string, body: any) {
  const db = await getDB();
  await db.add("syncQueue", {
    url,
    method,
    body: JSON.stringify(body),
    timestamp: Date.now(),
  });
}

export async function getQueuedRequests() {
  const db = await getDB();
  return db.getAll("syncQueue");
}

export async function removeFromQueue(id: number) {
  const db = await getDB();
  await db.delete("syncQueue", id);
}

export async function processQueue() {
  const requests = await getQueuedRequests();

  for (const req of requests) {
    try {
      const response = await fetch(req.url, {
        method: req.method,
        headers: { "Content-Type": "application/json" },
        body: req.body,
      });

      if (response.ok) {
        await removeFromQueue(req.id!);
      }
    } catch {
      // Still offline — stop processing
      break;
    }
  }
}
```

### Trigger sync on reconnect

```tsx
// hooks/useOfflineSync.ts
"use client";

import { useEffect } from "react";
import { processQueue } from "@/lib/sync-queue";

export function useOfflineSync() {
  useEffect(() => {
    // Process queue when coming back online
    const handleOnline = () => processQueue();

    window.addEventListener("online", handleOnline);

    // Also process on mount (in case we're already online)
    if (navigator.onLine) processQueue();

    return () => window.removeEventListener("online", handleOnline);
  }, []);
}
```

## Background Sync API

Background Sync lets the service worker retry requests even after the page is closed.

### Register sync event

```ts
// In client code
async function savePostOffline(post: any) {
  await queueRequest("/api/posts", "POST", post);

  // Request background sync
  const reg = await navigator.serviceWorker.ready;
  if ("sync" in reg) {
    await reg.sync.register("sync-posts");
  }
}
```

### Handle in service worker

```ts
// In sw.ts
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-posts") {
    event.waitUntil(processSyncQueue());
  }
});

async function processSyncQueue() {
  const db = await getDB();
  const requests = await db.getAll("syncQueue");

  for (const req of requests) {
    try {
      const response = await fetch(req.url, {
        method: req.method,
        headers: { "Content-Type": "application/json" },
        body: req.body,
      });

      if (response.ok) {
        await db.delete("syncQueue", req.id);
      }
    } catch {
      // Will retry on next sync event
      throw new Error("Sync failed — will retry");
    }
  }
}
```

### Browser support

| Browser | Background Sync |
|---------|----------------|
| Chrome | Yes |
| Edge | Yes |
| Firefox | No |
| Safari | No |
| Samsung | Yes |

**Fallback for unsupported browsers:** Use the `useOfflineSync` hook above to process the queue when the page is open and online.

## Offline Detection

### React hook

```tsx
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
    () => true // SSR assumes online
  );
}
```

### Offline indicator component

```tsx
"use client";

import { useOnlineStatus } from "@/hooks/useOnlineStatus";

export function OfflineIndicator() {
  const isOnline = useOnlineStatus();

  if (isOnline) return null;

  return (
    <div
      role="alert"
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        padding: "8px 16px",
        backgroundColor: "#f59e0b",
        color: "#000",
        textAlign: "center",
        zIndex: 9999,
      }}
    >
      You are offline. Changes will sync when you reconnect.
    </div>
  );
}
```

## Offline Fallback Content

### Offline page

```tsx
// app/offline/page.tsx
export default function OfflinePage() {
  return (
    <main style={{ textAlign: "center", padding: "4rem 1rem" }}>
      <h1>You are offline</h1>
      <p>Check your internet connection and try again.</p>
      <button onClick={() => window.location.reload()}>Retry</button>
    </main>
  );
}
```

### Conditional rendering

```tsx
"use client";

import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { useIndexedDB } from "@/hooks/useIndexedDB";
import { getPosts } from "@/lib/db";

export function PostList() {
  const isOnline = useOnlineStatus();
  const { data: cachedPosts } = useIndexedDB(() => getPosts());

  if (!isOnline && cachedPosts) {
    return (
      <div>
        <p>Showing cached data (offline)</p>
        {cachedPosts.map((post) => (
          <article key={post.id}>{post.title}</article>
        ))}
      </div>
    );
  }

  // ... online rendering with live data
}
```

## Data Sync Patterns

### Optimistic updates

```ts
async function createPost(post: Post) {
  // 1. Save to IndexedDB immediately (optimistic)
  await savePost({ ...post, synced: false });

  // 2. Try to sync with server
  try {
    const response = await fetch("/api/posts", {
      method: "POST",
      body: JSON.stringify(post),
    });

    if (response.ok) {
      await savePost({ ...post, synced: true });
    }
  } catch {
    // Offline — queue for later
    await queueRequest("/api/posts", "POST", post);
  }
}
```

### Last-write-wins conflict resolution

```ts
async function syncPosts() {
  const localPosts = await getUnsyncedPosts();
  const serverPosts = await fetch("/api/posts").then((r) => r.json());

  for (const local of localPosts) {
    const server = serverPosts.find((s: any) => s.id === local.id);

    if (!server || local.updatedAt > server.updatedAt) {
      // Local is newer — push to server
      await fetch(`/api/posts/${local.id}`, {
        method: "PUT",
        body: JSON.stringify(local),
      });
    } else {
      // Server is newer — update local
      await savePost({ ...server, synced: true });
    }
  }
}
```

## Storage Limits

| Browser | IndexedDB Limit |
|---------|----------------|
| Chrome | ~60% of free disk (per origin) |
| Firefox | ~50% of free disk (per origin) |
| Safari/iOS | ~1GB (but evicted aggressively under pressure) |

Check available storage:

```ts
const { usage, quota } = await navigator.storage.estimate();
console.log(`Using ${(usage! / 1e6).toFixed(1)}MB of ${(quota! / 1e6).toFixed(1)}MB`);
```

Request persistent storage (reduces eviction risk):

```ts
if (navigator.storage?.persist) {
  const persisted = await navigator.storage.persist();
  console.log(`Persistent storage granted: ${persisted}`);
}
```
