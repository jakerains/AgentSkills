# NextStep v2 API Reference

Authoritative reference for every public export of `nextstepjs` v2. Use this file when you need the exact type, default, or signature for a prop.

## Exports

All imports come from the main entry point `'nextstepjs'`:

| Export | Kind | Purpose |
|--------|------|---------|
| `NextStepProvider` | Component | Context provider. Wrap your app root with it. |
| `NextStep` | Component | Main tour engine. Accepts `steps`, `cardComponent`, callbacks, and overlay props. |
| `NextStepViewport` | Component | Scoping container for tours that target elements inside a scrollable area. |
| `useNextStep` | Hook | Programmatic tour control (start/stop/jump/introspect). |
| `Tour` | Type | `{ tour: string; steps: Step[] }` |
| `Step` | Type | Single step definition (see table below). |
| `CardComponentProps` | Type | Props passed to your custom `cardComponent`. |
| `NavigationAdapter` | Type | Routing adapter interface (the Next.js adapter is bundled by default). |

## `NextStep` Props

The main component. Wraps your app content and renders the tour overlay.

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `React.ReactNode` | — | Your website or application content. |
| `steps` | `Tour[]` | — | Array of Tour objects defining each tour. |
| `navigationAdapter` | `NavigationAdapter` | Next.js adapter | Optional. Router adapter for navigation. |
| `showNextStep` | `boolean` | — | Controls visibility of the onboarding overlay. |
| `shadowRgb` | `string` | `"0, 0, 0"` | RGB values for the shadow color surrounding the target area. |
| `shadowOpacity` | `string` | `"0.2"` | Opacity value for the shadow surrounding the target area. |
| `cardComponent` | `React.ComponentType<CardComponentProps>` | built-in card | Custom card component to replace the default one. |
| `cardTransition` | `Transition` (from `motion`) | `{ ease: 'anticipate', duration: 0.6 }` | Framer Motion / motion transition object for step transitions. |
| `onStart` | `(tourName?: string \| null) => void` | — | Fires when a tour starts. |
| `onStepChange` | `(step: number, tourName?: string \| null) => void` | — | Fires on every step change (next, prev, jump). |
| `onComplete` | `(tourName?: string \| null) => void` | — | Fires when the user finishes the last step. |
| `onSkip` | `(step: number, tourName?: string \| null) => void` | — | Fires when the user clicks Skip. |
| `clickThroughOverlay` | `boolean` | `false` | If true, overlay background passes clicks through to the page. |
| `disableConsoleLogs` | `boolean` | `false` | Suppress NextStep's internal console logs. |
| `scrollToTop` | `boolean` | `true` | Scroll to the top when the tour starts. |
| `noInViewScroll` | `boolean` | `false` | If true, never auto-scroll to target when it is already visible. |
| `overlayZIndex` | `number` | `997` | Base z-index for overlay elements. Raise if your app uses higher z-indices (e.g., MUI modals). |

## `Step` Object

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `icon` | `React.ReactNode \| string \| null` | yes | Icon or element shown alongside the title. Emoji strings work. |
| `title` | `string` | yes | Heading for the step. |
| `content` | `React.ReactNode` | yes | Body of the step (string or JSX). |
| `selector` | `string` | no | CSS `#id` of the target. Omit for a centered modal step. |
| `side` | `'top' \| 'bottom' \| 'left' \| 'right' \| 'top-left' \| 'top-right' \| 'bottom-left' \| 'bottom-right' \| 'left-top' \| 'left-bottom' \| 'right-top' \| 'right-bottom'` | no | Where the card appears relative to the selector. |
| `showControls` | `boolean` | no | Show Next/Prev buttons **in the default card**. Custom cards must honor this manually. |
| `showSkip` | `boolean` | no | Show Skip button **in the default card**. Custom cards must honor this manually. |
| `blockKeyboardControl` | `boolean` | no | Disable ←/→/Esc for this step. Use on input-focused steps. |
| `pointerPadding` | `number` | no | Padding (px) around the keyhole highlight. |
| `pointerRadius` | `number` | no | Border-radius (px) of the keyhole highlight. |
| `nextRoute` | `string` | no | Route pushed when the user clicks Next. |
| `prevRoute` | `string` | no | Route pushed when the user clicks Prev. |
| `viewportID` | `string` | no | Id of a `<NextStepViewport>` ancestor; positions relative to that container. |
| `disableInteraction` | `boolean` | no | Block clicks/hover on the highlighted element. Useful for view-only steps. |

**Card cutoff behavior** (per docs): if `side` is `right`/`left` and the card overflows the viewport, NextStep automatically switches to `top`. If `side` is `top`/`bottom` and the card overflows, it flips between top and bottom. No manual override needed in most cases.

## `Tour` Object

```ts
type Tour = {
  tour: string;   // unique identifier, used with startNextStep(name)
  steps: Step[];  // ordered list of steps
};
```

You can pass multiple `Tour` objects to `NextStep` — start any of them by name via `startNextStep('tourName')`.

## `useNextStep` Hook

```ts
const {
  startNextStep,      // (tourName: string) => void
  closeNextStep,      // () => void
  currentTour,        // string | null
  currentStep,        // number (0-indexed)
  setCurrentStep,     // (step: number, delay?: number) => void
  isNextStepVisible,  // boolean
} = useNextStep();
```

- `startNextStep(tourName)` — begin a specific tour. Per docs, if you omit the name it starts the first tour in the array; always pass the name explicitly for clarity.
- `closeNextStep()` — exit the current tour without completion callback.
- `setCurrentStep(step, delay?)` — jump to a step (0-indexed). Optional `delay` in milliseconds lets the DOM settle before the jump — useful on mount/hydration.
- `isNextStepVisible` — `true` while the overlay is rendered. Use to conditionally render tour-related UI.

Must be called inside a `'use client'` component.

## `CardComponentProps`

Props your custom card component receives when you pass it to `NextStep` via `cardComponent`:

```ts
type CardComponentProps = {
  step: Step;                   // the active step
  currentStep: number;          // 0-indexed step pointer
  totalSteps: number;           // total steps in the active tour
  nextStep: () => void;         // advance to the next step
  prevStep: () => void;         // go back one step
  skipTour: () => void;         // exit the tour (fires onSkip)
  arrow: React.ReactNode;       // SVG arrow pointer — render somewhere in your card
};
```

Your card is responsible for:
- Rendering `step.icon`, `step.title`, `step.content`
- Placing `arrow` somewhere inside the card so the pointer anchors correctly
- Honoring `step.showControls` and `step.showSkip` (the default-card flags don't reach here automatically)

## `NavigationAdapter` Interface

For Next.js, **you don't need this** — the adapter is bundled and auto-wired. Skip the rest of this section unless you're using NextStep outside of Next.js.

A custom adapter is authored as a **hook** that returns `{ navigate, location }`:

```ts
import type { NavigationAdapter } from 'nextstepjs';

// Hook that NextStep will call internally
function useCustomNavigationAdapter(): NavigationAdapter {
  const [location, setLocation] = useState(window.location.pathname);

  useEffect(() => {
    const handle = () => setLocation(window.location.pathname);
    window.addEventListener('popstate', handle);
    return () => window.removeEventListener('popstate', handle);
  }, []);

  const navigate = useCallback((to: string) => {
    window.history.pushState({}, '', to);
    setLocation(to);
  }, []);

  return { navigate, location };
}

// Pass the hook itself (not the result) to NextStep:
<NextStep steps={tours} navigationAdapter={useCustomNavigationAdapter}>
  {children}
</NextStep>
```

> **Docs inconsistency note**: NextStep's own API reference table lists `{ push, getCurrentPath }` as the adapter shape, but the routing page shows working code using `{ navigate, location }` as a hook. The hook-based shape above is what the actual example uses; treat the reference table as stale. For Next.js users this never matters — use the built-in adapter.

## v2 Migration Notes

NextStep 2.0 introduced a framework-agnostic routing system via `NavigationAdapter`. Each adapter is packaged separately to minimize bundle size. For Next.js users:

- The Next.js adapter is auto-bundled; no code change vs v1 for typical usage.
- `nextRoute` / `prevRoute` behavior is unchanged.
- `CardComponentProps` shape is unchanged.
- If you use a non-Next.js framework, import the matching adapter and pass it via `navigationAdapter`.

No breaking changes are documented for common App Router / Pages Router usage.
