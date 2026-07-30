# Framework Integration

Driver.js operates on the real DOM, so it drops into any framework. Two rules cover almost everything:

1. **Create the instance after the target elements are mounted.** A tour referencing `#sidebar` fails silently (centered fallback) if it runs before the sidebar renders. Kick it off from a mount effect, an explicit "Start tour" button, or after data has loaded.
2. **`destroy()` on unmount.** Otherwise a route change can leave a stuck overlay, and the instance leaks listeners.

Import CSS once, near your app root (or in the component). Bundlers resolve `import "driver.js/dist/driver.css"`.

---

## React / Next.js

### One-off tour in a component

```jsx
import { useEffect, useRef } from "react";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";

export function Dashboard() {
  const driverRef = useRef(null);

  useEffect(() => {
    driverRef.current = driver({
      showProgress: true,
      steps: [
        { element: "#new-btn",  popover: { title: "Create", description: "Start something new." } },
        { element: "#sidebar",  popover: { title: "Navigate", description: "Jump around here." } },
      ],
    });
    // Start after mount. Guard so it only runs once per user if you like.
    driverRef.current.drive();

    return () => driverRef.current?.destroy(); // cleanup on unmount
  }, []);

  return (/* ... your UI with #new-btn and #sidebar ... */);
}
```

### Trigger from a button (more common for "Take a tour")

```jsx
function useTour(steps) {
  const ref = useRef(null);
  useEffect(() => {
    ref.current = driver({ showProgress: true, steps });
    return () => ref.current?.destroy();
  }, [steps]);
  return () => ref.current?.drive();
}

function HelpButton() {
  const startTour = useTour([
    { element: "#search", popover: { title: "Search", description: "Find anything fast." } },
  ]);
  return <button onClick={startTour}>Take a tour</button>;
}
```

### Next.js (App Router) — client component + SSR guard

Driver.js touches `document`, so it must run on the client only.

```jsx
"use client"; // REQUIRED — Driver.js is browser-only

import { useEffect } from "react";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";

export default function Tour() {
  useEffect(() => {
    const d = driver({ steps: [/* ... */] });
    d.drive();
    return () => d.destroy();
  }, []);
  return null;
}
```

Notes:
- Never call `driver()` at module top level in a file that can be imported on the server — construct it inside `useEffect`/an event handler.
- Targeting elements from *other* components? Ensure they've rendered. If a target mounts asynchronously, use `waitForElement` on that step (see `references/recipes.md`).
- Refs (`ref={el}`) work as `element` values too: `element: () => myRef.current`.

---

## Vue 3

```vue
<script setup>
import { onMounted, onBeforeUnmount } from "vue";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";

let driverObj;

onMounted(() => {
  driverObj = driver({
    showProgress: true,
    steps: [
      { element: "#new-btn", popover: { title: "Create", description: "Start something new." } },
    ],
  });
  driverObj.drive();
});

onBeforeUnmount(() => driverObj?.destroy());
</script>
```

For a button trigger, construct `driverObj` in `onMounted` and call `driverObj.drive()` from a `@click` handler. Template refs work as targets: `element: () => myTemplateRef.value`.

---

## Svelte

```svelte
<script>
  import { onMount } from "svelte";
  import { driver } from "driver.js";
  import "driver.js/dist/driver.css";

  let driverObj;

  onMount(() => {
    driverObj = driver({ steps: [ /* ... */ ] });
    driverObj.drive();
    return () => driverObj.destroy(); // onMount cleanup runs on unmount
  });
</script>
```

---

## Angular

```ts
import { AfterViewInit, OnDestroy, Component } from "@angular/core";
import { driver, Driver } from "driver.js";
import "driver.js/dist/driver.css";

@Component({ /* ... */ })
export class DashboardComponent implements AfterViewInit, OnDestroy {
  private driverObj?: Driver;

  ngAfterViewInit() {
    this.driverObj = driver({ steps: [ /* ... */ ] });
    this.driverObj.drive();
  }

  ngOnDestroy() {
    this.driverObj?.destroy();
  }
}
```

Use `AfterViewInit` (not `OnInit`) so the view's DOM exists before the tour references it.

---

## SSR / static generation (general)

Any SSR framework (Next.js, Nuxt, SvelteKit, Astro) renders on the server where `window`/`document` don't exist. Keep every Driver.js call in client-only lifecycle:

- Construct inside mount effects / event handlers, never at import time.
- In frameworks with explicit client directives, mark the component client-side (`"use client"`, `client:only`, etc.).
- The CSS `import` is safe on the server (it's handled by the bundler), but the `driver()`/`hints()` calls are not.

---

## Persisting "seen" state across sessions

Framework-agnostic: gate `.drive()` on a flag.

```js
if (!localStorage.getItem("tour_v1_done")) {
  driver({ steps, onDestroyed: () => localStorage.setItem("tour_v1_done", "1") }).drive();
}
```

Bump the flag name (`tour_v2_done`) when you materially change the tour so returning users see the new version. For per-user gating, store the flag on the user record server-side instead.
