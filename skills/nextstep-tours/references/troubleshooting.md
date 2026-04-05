# NextStep Troubleshooting

Problem → Fix table for the issues that come up most often. Scan for your symptom; the fix is usually one line.

## Quick diagnostic

| Symptom | Likely cause | Jump to |
|---------|-------------|---------|
| Tour freezes after clicking Next on a step with `nextRoute` | Target element not mounted on new page | [Element not found after `nextRoute`](#element-not-found-after-nextroute) |
| Tour starts but no card appears | Custom card missing `return` or not a client component | [Card doesn't render](#card-doesnt-render) |
| Pages Router app throws `SyntaxError: Unexpected token 'export'` | ES module mismatch | [Pages Router ESM errors](#pages-router-esm-errors) |
| Tour card is dark-on-dark or invisible in dark mode | Theme provider is outside `NextStep` | [Dark mode broken](#dark-mode-broken) |
| Card is hidden behind a modal or overlay | App z-index exceeds NextStep's default | [Z-index conflicts](#z-index-conflicts) |
| Tour re-opens on every page load | `startNextStep` called in render or without a gate | [Tour re-fires](#tour-re-fires-on-every-mount) |
| Card appears in wrong position over scrollable content | Missing `NextStepViewport` | [Wrong position in scrollable](#wrong-position-in-scrollable-container) |
| Step never advances despite validation returning true | Custom card not calling `nextStep()` | [Step never advances](#step-never-advances) |
| Hydration mismatch warning when tour auto-starts | `startNextStep` during render | [Hydration mismatch](#hydration-mismatch) |
| Card pointer arrow missing | Custom card forgot to render `arrow` slot | [Missing arrow](#missing-arrow) |

---

## Element not found after `nextRoute`

**Symptom**: click Next on a step with `nextRoute: '/settings'`, page navigates, but the tour appears frozen. No next card.

**Cause**: NextStep navigates and then waits for the next step's `selector` to exist in the DOM. On async-rendered pages (data fetching, Suspense, lazy components), the selector may never appear before the page content mounts. NextStep waits forever.

**Fix**: render a placeholder element with the step's `id` at the top of the target page, before any async boundary:

```tsx
// app/settings/page.tsx
export default function SettingsPage() {
  return (
    <main>
      <div id="settings-header" aria-hidden="true" />
      <Suspense fallback={<Skeleton />}>
        <SettingsContent />
      </Suspense>
    </main>
  );
}
```

Now the `id` exists the moment navigation completes. Full pattern in `multi-page-tours.md`.

## Card doesn't render

**Symptom**: `startNextStep('foo')` fires, `isNextStepVisible` is `true`, but no card appears.

**Causes**:
1. Your custom card is not a client component. Add `'use client'` at the top of the card file.
2. Your card returns `null` or throws. Open the browser console — a render error will be logged.
3. The target element (`selector`) is not in the DOM. The overlay is present but the card has no anchor. Inspect with DevTools.

## Pages Router ESM errors

**Symptom**: running `next dev` throws something like `SyntaxError: Unexpected token 'export'` pointing at `node_modules/nextstepjs`.

**Cause**: `nextstepjs` ships as ES modules. Pages Router projects default to CommonJS.

**Fix**: update `next.config.js`:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    esmExternals: true,
  },
  transpilePackages: ['nextstepjs'],
};

export default nextConfig;
```

App Router projects don't hit this.

## Dark mode broken

**Symptom**: NextStep's default card is white-on-white or black-on-black when your app is in dark mode.

**Cause**: NextStep has no built-in dark mode. The default card uses fixed colors.

**Fix**: use a custom card. Place `<NextStep>` **inside** your theme provider so Tailwind's `dark:` classes (or your CSS variables) resolve correctly:

```tsx
<ThemeProvider>
  <NextStepProvider>
    <NextStep steps={tours} cardComponent={CustomCard}>
      {children}
    </NextStep>
  </NextStepProvider>
</ThemeProvider>
```

Full dark-mode card in `custom-card.md` and `assets/custom-card.tsx`.

## Z-index conflicts

**Symptom**: NextStep overlay dims the page but a modal or dropdown in your app appears *above* the dim, breaking the focus effect.

**Cause**: your modal uses a z-index ≥ NextStep's default `997`. Radix, MUI, and most design systems use values in the thousands.

**Fix**: raise NextStep's base z-index above your app's max:

```tsx
<NextStep steps={tours} overlayZIndex={100000}>
  {children}
</NextStep>
```

Check your design system's z-index scale and pick something above its topmost layer.

## Tour re-fires on every mount

**Symptom**: tour plays every time the user navigates or refreshes.

**Cause**: `startNextStep('welcome')` is called unconditionally inside a `useEffect` with no guard.

**Fix**: gate on a persisted flag:

```tsx
'use client';
import { useEffect } from 'react';
import { useNextStep } from 'nextstepjs';

export function AutoStart({ userId }: { userId: string }) {
  const { startNextStep } = useNextStep();
  useEffect(() => {
    const key = `onboarded:${userId}`;
    if (localStorage.getItem(key) === 'true') return;
    startNextStep('welcome');
    localStorage.setItem(key, 'true');
  }, [userId, startNextStep]);
  return null;
}
```

Better: persist to your backend so the flag follows the user across devices.

## Wrong position in scrollable container

**Symptom**: target element lives inside a `overflow: auto` container. The card positions at the viewport edge instead of near the element, or the container doesn't scroll into view.

**Cause**: default positioning uses `document.body` as the scroll root.

**Fix**: wrap the scrollable container with `<NextStepViewport id="...">` and set `viewportID` on the step. See `multi-page-tours.md`.

## Step never advances

**Symptom**: user clicks Next, validation passes (or you have no validation), but the step doesn't change.

**Cause**: your custom card is swallowing the click — probably calling `e.preventDefault()` without calling `nextStep()`, or the button's `onClick` wiring is broken.

**Fix**: verify your Next button's handler actually calls `nextStep()`:

```tsx
<button type="button" onClick={() => nextStep()}>Next</button>
```

If using a validation card, make sure the async branch that passes also calls `nextStep()`:

```tsx
const ok = await entry.validation();
if (ok) nextStep();  // ← don't forget this
else setError(entry.validationMessage);
```

## Hydration mismatch

**Symptom**: React logs `Warning: Text content did not match` or `Hydration failed` when the tour starts.

**Cause**: `startNextStep` is being called during render (e.g., at the top of a component function) so the server and client render different overlay state.

**Fix**: always call `startNextStep` from inside `useEffect` or an event handler. Never at the top level of a render function.

```tsx
// ❌ Wrong — runs during render
export function Shell() {
  const { startNextStep } = useNextStep();
  startNextStep('welcome');  // hydration mismatch
  return <div />;
}

// ✅ Right — effect or handler
export function Shell() {
  const { startNextStep } = useNextStep();
  useEffect(() => { startNextStep('welcome'); }, [startNextStep]);
  return <div />;
}
```

If you use React Strict Mode (the Next.js default) and see the tour auto-start twice in development, that's the double-invoke of effects — harmless, only fires once in production.

## Missing arrow

**Symptom**: card appears but has no little pointer arrow connecting it to the highlighted element.

**Cause**: your custom card forgot to render the `arrow` prop.

**Fix**: include `{arrow}` inside the card JSX, typically after the content block:

```tsx
<div className="card">
  <h3>{step.title}</h3>
  <p>{step.content}</p>
  {arrow}     {/* ← render this */}
  <footer>…</footer>
</div>
```

NextStep handles the arrow's positioning and styling internally — you just need to mount it.
