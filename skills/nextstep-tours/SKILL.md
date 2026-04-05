---
name: nextstep-tours
description: "Build product tours, onboarding flows, and interactive tutorials/lessons in Next.js with NextStep v2 (nextstepjs). Use when adding guided tours, walkthroughs, onboarding overlays, feature callouts, interactive lessons, or gated step-by-step tutorials to a Next.js App Router or Pages Router app. Covers NextStepProvider setup, multi-tour configuration, DOM-anchored and modal steps, multi-page tours with nextRoute/prevRoute, NextStepViewport for scrollable containers, custom card components, validation-gated progression, dark mode, analytics callbacks, and localization. Triggers: nextstep, nextstepjs, product tour, onboarding, walkthrough, guided tour, feature tour, tutorial overlay, interactive lesson, step-by-step guide, useNextStep, NextStepProvider, NextStepViewport, CardComponentProps."
---

# NextStep Tours Skill

Build product tours, onboarding flows, and — most importantly — **interactive tutorials** with NextStep v2 (`nextstepjs`) in Next.js. This skill makes the action-gated lesson pattern the default rather than generic welcome popups.

## Quick Reference

| Task | Approach | Reference |
|------|----------|-----------|
| Install & wire provider | 3-step Quick Start | this file |
| Define a tour | `Tour` / `Step` schema | this file |
| Multi-page tour | `nextRoute` / `prevRoute` | references/multi-page-tours.md |
| Scrollable container | `NextStepViewport` | references/multi-page-tours.md |
| Custom card UI | `cardComponent` prop | references/custom-card.md |
| **Gate progress on user action** | **Custom card + validation registry** | **references/tutorial-authoring.md** |
| Full props & types | `NextStep` / `Step` / `CardComponentProps` | references/api-reference.md |
| Element not found, SSR, z-index | Troubleshooting table | references/troubleshooting.md |

**Core principle**: A tour that just shows tooltips teaches nothing. A tutorial that *requires the user to perform each action before advancing* teaches. Reach for the validation-gated pattern whenever the word "tutorial" or "lesson" appears.

---

## Install

```bash
npm i nextstepjs motion
# or: pnpm add nextstepjs motion / yarn add nextstepjs motion / bun add nextstepjs motion
```

`motion` is the peer dependency (the library formerly known as Framer Motion, used for step transitions).

**Pages Router users only**: if you hit ES module errors at runtime, see `references/troubleshooting.md` for the `next.config.js` fix.

---

## Minimal Working Example (App Router)

Three files. Drop-in ready.

### 1. `lib/tours.ts`

```ts
import type { Tour } from 'nextstepjs';

export const tours: Tour[] = [
  {
    tour: 'welcome',
    steps: [
      {
        icon: '👋',
        title: 'Welcome',
        content: "Let's take a quick look around.",
        selector: '#welcome-banner',
        side: 'bottom',
        showControls: true,
        showSkip: true,
        pointerPadding: 10,
        pointerRadius: 8,
      },
      {
        icon: '🧭',
        title: 'Navigation',
        content: 'Your main nav lives here.',
        selector: '#main-nav',
        side: 'right',
        showControls: true,
        showSkip: true,
      },
      {
        icon: '🎉',
        title: 'All set',
        content: "You're ready. Explore freely.",
        showControls: true,
      },
    ],
  },
];
```

### 2. `app/layout.tsx`

```tsx
import { NextStepProvider, NextStep } from 'nextstepjs';
import { tours } from '@/lib/tours';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <NextStepProvider>
          <NextStep steps={tours}>
            {children}
          </NextStep>
        </NextStepProvider>
      </body>
    </html>
  );
}
```

### 3. `components/start-tour-button.tsx` (client component that triggers the tour)

```tsx
'use client';
import { useNextStep } from 'nextstepjs';

export function StartTourButton() {
  const { startNextStep } = useNextStep();
  return <button onClick={() => startNextStep('welcome')}>Take a tour</button>;
}
```

Render `<StartTourButton />` anywhere inside the provider tree. Add `id="welcome-banner"` and `id="main-nav"` to the elements the steps target.

---

## The `Step` Shape

All props a single step supports — required ones first, optional below. Source of truth for every example in this skill.

```ts
type Step = {
  // ── Required ──────────────────────────────────────────────
  icon: React.ReactNode | string | null;  // emoji string, JSX, or null
  title: string;                           // step heading
  content: React.ReactNode;                // body (string or JSX)

  // ── Targeting ─────────────────────────────────────────────
  selector?: string;     // CSS #id of the element to anchor to. Omit for a centered modal step.
  side?: 'top' | 'bottom' | 'left' | 'right'
       | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
       | 'left-top' | 'left-bottom' | 'right-top' | 'right-bottom';

  // ── Pointer (the keyhole highlight) ───────────────────────
  pointerPadding?: number;   // px of breathing room around target
  pointerRadius?: number;    // border-radius of keyhole (px)

  // ── Default-card controls (ignored if using a custom card) ─
  showControls?: boolean;    // show Next / Prev buttons
  showSkip?: boolean;        // show Skip button

  // ── Behavior ──────────────────────────────────────────────
  blockKeyboardControl?: boolean;  // disable ←/→/Esc for this step (use on form-input steps)
  disableInteraction?: boolean;    // block clicks/hover on the highlighted element (view-only steps)

  // ── Multi-page routing ────────────────────────────────────
  nextRoute?: string;   // route to push when the user clicks Next
  prevRoute?: string;   // route to push when the user clicks Prev

  // ── Scrollable containers ─────────────────────────────────
  viewportID?: string;  // id of a <NextStepViewport> ancestor; positions relative to that container
};
```

**Gotcha**: `showControls` and `showSkip` only affect NextStep's **default** card. If you use a custom `cardComponent`, you must read `step.showControls` / `step.showSkip` yourself and render buttons accordingly (see `references/custom-card.md`).

---

## Step Patterns

### DOM-anchored (most common)

```ts
{
  icon: '⚙️',
  title: 'Settings live here',
  content: 'Click the gear to manage your account.',
  selector: '#settings-gear',
  side: 'left',
  showControls: true,
  showSkip: true,
}
```

### Unanchored modal (intro / outro)

```ts
// No `selector` → renders as a centered modal at the top of the document body.
{
  icon: '🎉',
  title: 'Welcome aboard',
  content: "This 60-second walkthrough will get you started.",
  showControls: true,
}
```

### Multi-page / routed step

```ts
// First page — Next pushes /settings, NextStep waits for #settings-header to mount before advancing.
{
  icon: '📄',
  title: 'Open settings',
  content: 'Click Next to head to the settings page.',
  selector: '#dashboard-header',
  side: 'bottom',
  showControls: true,
  nextRoute: '/settings',
}
```

### Viewport-confined step (inside a scrollable container)

```tsx
// Wrap the scrollable element:
<div className="overflow-auto max-h-[400px]">
  <NextStepViewport id="data-table">
    <table>
      <tr id="row-42">…</tr>
    </table>
  </NextStepViewport>
</div>
```

```ts
{
  icon: '🔍',
  title: 'Row 42',
  content: 'Scroll position is handled automatically inside the viewport.',
  selector: '#row-42',
  side: 'top',
  viewportID: 'data-table',
  showControls: true,
}
```

### **Action-gated tutorial step** (use for lessons)

A step that does not advance until the user performs a real action. Requires a custom card backed by a validation registry. See `references/tutorial-authoring.md` for the full pattern and `assets/validation-card.tsx` + `assets/validation-registry.ts` for drop-in code.

```ts
// The step itself looks normal:
{
  icon: '✏️',
  title: 'Type your username',
  content: 'Enter at least 3 characters in the field above.',
  selector: '#username-field',
  side: 'bottom',
  showControls: true,
  blockKeyboardControl: true,  // prevent accidental Esc while typing
}

// The magic lives in the validation registry — keyed by [tourName][stepIndex].
// See references/tutorial-authoring.md.
```

---

## The `useNextStep` Hook

Every method and property the hook returns. Import from `nextstepjs`; **must be called inside a `'use client'` component**.

```tsx
'use client';
import { useNextStep } from 'nextstepjs';

const {
  startNextStep,      // (tourName: string) => void — start a specific tour by id
  closeNextStep,      // () => void                  — exit the current tour
  currentTour,        // string | null               — id of the active tour, or null
  currentStep,        // number                      — 0-indexed step pointer
  setCurrentStep,     // (step: number, delay?: number) => void — jump to a step (optional ms delay)
  isNextStepVisible,  // boolean                     — is the overlay currently rendered
} = useNextStep();
```

### Start on user click

```tsx
'use client';
import { useNextStep } from 'nextstepjs';

export function HelpButton() {
  const { startNextStep } = useNextStep();
  return <button onClick={() => startNextStep('welcome')} aria-label="Start tour">Help</button>;
}
```

### Auto-start for first-time users only

```tsx
'use client';
import { useEffect } from 'react';
import { useNextStep } from 'nextstepjs';

export function OnboardingAutostart({ userId }: { userId: string }) {
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

Never call `startNextStep` during render — always inside `useEffect` or an event handler.

---

## Analytics & Lifecycle Callbacks

`NextStep` accepts four lifecycle props. Wire them into your analytics pipeline for funnel visibility.

```tsx
'use client';
import { NextStep, NextStepProvider } from 'nextstepjs';
import { tours } from '@/lib/tours';
import { track } from '@/lib/analytics';

export function NextStepShell({ children }: { children: React.ReactNode }) {
  return (
    <NextStepProvider>
      <NextStep
        steps={tours}
        onStart={(tourName) => track('tour_started', { tourName })}
        onStepChange={(step, tourName) => track('tour_step_viewed', { tourName, step })}
        onComplete={(tourName) => track('tour_completed', { tourName })}
        onSkip={(step, tourName) => track('tour_skipped', { tourName, step })}
      >
        {children}
      </NextStep>
    </NextStepProvider>
  );
}
```

Use `onComplete` to persist a "tutorialDone" flag so the tour never auto-replays. Use `onSkip` with the step index to learn *where* users abandon — that's your tutorial's weakest link.

---

## Designing Tutorials vs. Welcome Tours

The difference between a forgettable popup parade and a real lesson:

- **Gate progression on action, not clicks.** If the user can spam Next without doing the thing, they will. Use a custom card + validation registry (`references/tutorial-authoring.md`) so "Next" actually requires the user to complete the step's task.
- **One sentence per step.** The UI is the teacher; the card is just the label. If content needs more than one sentence, split the step.
- **Always include `showSkip: true`.** People who know the product hate tours. Let them out instantly.
- **Set `blockKeyboardControl: true` on input steps.** Prevents accidental Esc-to-dismiss while the user is typing into a field the step is highlighting.
- **Use `disableInteraction: true` for view-only steps.** Stops the user from clicking the highlighted thing when you want them to *read* about it, not activate it.
- **Multi-page lessons need placeholder anchors.** If step N+1 lives on `/settings` and that page fetches data async, render a minimal placeholder element with the step's `id` *before* the fetch resolves — otherwise `nextRoute` navigates but the step never appears. Details in `references/multi-page-tours.md`.
- **Branch with separate tours, not conditional steps.** For novice-vs-expert paths, define two `Tour` objects and pick which one to `startNextStep()` based on user state. One tour = one linear flow.
- **Resume with `setCurrentStep(index, delay)`.** On mount, read a persisted step index from `localStorage` and jump there with a small delay to let the DOM settle. Pair with `onStepChange` to save progress.
- **Write analytics events per step, not per tour.** `tour_step_viewed` + `step_failed_validation` tells you which specific step is frustrating users. `tour_completed` alone doesn't.
- **Localize by generating steps inside a hook.** NextStep has no built-in i18n; wrap your `tours` definition in a function that accepts `t()` from your i18n library and regenerates when locale changes.

Deeper coverage of each principle, with the full validation registry pattern and 4 real validator archetypes, is in `references/tutorial-authoring.md`.

---

## Copy-Paste Starters

Drop-in files in `assets/`:

- **`assets/provider-layout.tsx`** — complete App Router `layout.tsx` wrapping children in `NextStepProvider` + `NextStep` with a custom card, callbacks, and all overlay props set to sensible defaults.
- **`assets/tours.ts`** — representative multi-tour file: one welcome tour, one feature tour with `nextRoute`, one gated-lesson tour paired with the validation registry.
- **`assets/custom-card.tsx`** — Tailwind + dark-mode aware card, exercises every `CardComponentProps` field.
- **`assets/validation-card.tsx`** — variant that reads from `validation-registry.ts`, awaits the validator, shows inline error on fail.
- **`assets/validation-registry.ts`** — typed `[tourName][stepIndex]` map with three real validator archetypes (DOM input, async fetch, viewport size).

Copy the files, wire the imports, and adjust selectors/IDs to match your app.

---

## References

- **`references/api-reference.md`** — Every prop on `NextStep`, `Step`, `Tour`, `CardComponentProps`, and `NavigationAdapter`, with types, defaults, and the full exports list. Read this when you need the authoritative signature for any prop.
- **`references/custom-card.md`** — Full paste-ready Tailwind + dark-mode card, the `arrow` slot, overlay tuning (`shadowRgb`, `shadowOpacity`, `overlayZIndex`, `clickThroughOverlay`), pointer styling, and accessibility notes.
- **`references/multi-page-tours.md`** — `nextRoute`/`prevRoute` lifecycle, the placeholder-anchor pattern for async pages, `NextStepViewport` for scrollable containers, and when a custom `navigationAdapter` is needed.
- **`references/tutorial-authoring.md`** — The differentiating content. Validation registry pattern with four validator archetypes (input, click-tracked, async API, viewport gate), pacing rules, branching strategy, resume-later with `localStorage` + `setCurrentStep`, analytics taxonomy, and localization via `getLocalizedSteps()`.
- **`references/troubleshooting.md`** — Problem → Fix table covering element-not-found timing, Pages Router ESM errors, dark mode scope, tour re-firing, z-index conflicts, Strict Mode double-invoke, and hydration.
