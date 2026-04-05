# Custom Card Components

Replacing NextStep's default card is how you get branded tours, dark-mode support, validation gates, and accessible step UIs. This file covers the full pattern end to end.

## Contract

A custom card is any React component that accepts `CardComponentProps` and returns JSX. Pass it to `NextStep` via the `cardComponent` prop:

```tsx
import { NextStep, NextStepProvider } from 'nextstepjs';
import { CustomCard } from './custom-card';

<NextStepProvider>
  <NextStep steps={tours} cardComponent={CustomCard}>
    {children}
  </NextStep>
</NextStepProvider>
```

Your card **must** be a client component — add `'use client'` at the top. It must also render the `arrow` slot (an SVG element NextStep injects so the pointer anchors correctly) somewhere inside the card.

## Props received

```ts
type CardComponentProps = {
  step: Step;                   // the active step definition
  currentStep: number;          // 0-indexed pointer
  totalSteps: number;           // total steps in the active tour
  nextStep: () => void;         // advance
  prevStep: () => void;         // go back
  skipTour: () => void;         // exit and fire onSkip
  arrow: React.ReactNode;       // the SVG pointer — MUST render this
};
```

Things that are **not** in the props but that you often want:
- The active tour name → call `useNextStep()` inside the card and read `currentTour`.
- Validation logic → read from a validation registry keyed by `[currentTour][currentStep]` (see `tutorial-authoring.md`).
- Dark-mode state → use your app's theme provider or CSS variables; NextStep doesn't supply this.

## Full paste-ready card (Tailwind + dark mode)

```tsx
'use client';

import type { CardComponentProps } from 'nextstepjs';

export function CustomCard({
  step,
  currentStep,
  totalSteps,
  nextStep,
  prevStep,
  skipTour,
  arrow,
}: CardComponentProps) {
  const isFirst = currentStep === 0;
  const isLast = currentStep === totalSteps - 1;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="nextstep-card-title"
      className="w-[360px] rounded-xl border border-neutral-200 bg-white p-5 shadow-xl dark:border-neutral-800 dark:bg-neutral-900"
    >
      <header className="mb-3 flex items-center gap-3">
        {step.icon && <span className="text-2xl">{step.icon}</span>}
        <h3 id="nextstep-card-title" className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
          {step.title}
        </h3>
      </header>

      <div className="mb-4 text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
        {step.content}
      </div>

      {arrow}

      <footer className="mt-5 flex items-center justify-between">
        <span className="text-xs text-neutral-500 dark:text-neutral-400">
          Step {currentStep + 1} of {totalSteps}
        </span>

        <div className="flex items-center gap-2">
          {step.showSkip && (
            <button
              type="button"
              onClick={skipTour}
              className="rounded-md px-3 py-1.5 text-sm text-neutral-600 hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
            >
              Skip
            </button>
          )}
          {step.showControls && !isFirst && (
            <button
              type="button"
              onClick={prevStep}
              className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-200 dark:hover:bg-neutral-800"
            >
              Back
            </button>
          )}
          {step.showControls && (
            <button
              type="button"
              onClick={nextStep}
              className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-800 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-200"
            >
              {isLast ? 'Finish' : 'Next'}
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}
```

## The `arrow` slot

`arrow` is an SVG element NextStep renders so the card's pointer visually connects to the highlighted element. **Render it inside your card**, typically after the content but before the footer. It positions itself automatically — you don't need to style it.

If you forget to render `arrow`, the tour still works but the pointer is missing, which hurts users' ability to map the card to its target.

## Overlay tuning (passed to `<NextStep>`, not the card)

These tune the dim overlay that surrounds the highlighted element. They are `NextStep` props, not step or card props:

| Prop | Type | Default | Purpose |
|------|------|---------|---------|
| `shadowRgb` | `string` | `"0, 0, 0"` | RGB triplet for the overlay color. `"76, 29, 149"` = purple, `"0, 0, 255"` = blue. |
| `shadowOpacity` | `string` | `"0.2"` | Overlay opacity (0–1). Higher = darker dim. |
| `overlayZIndex` | `number` | `997` | Base z-index. Raise above your app's topmost modal if the overlay hides behind modals. |
| `clickThroughOverlay` | `boolean` | `false` | If true, clicks outside the highlight fall through to the page. Usually keep false. |

Example:
```tsx
<NextStep
  steps={tours}
  cardComponent={CustomCard}
  shadowRgb="15, 23, 42"    // slate-900
  shadowOpacity="0.55"      // more opaque for dramatic focus
  overlayZIndex={10000}     // above any MUI/Radix modals
>
  {children}
</NextStep>
```

## Pointer (keyhole) tuning (per-step)

These live on each `Step` and control the highlighted-element "keyhole":

| Prop | Type | Purpose |
|------|------|---------|
| `pointerPadding` | `number` | Px of space between the element and the keyhole edge. Larger = more "breathing room". |
| `pointerRadius` | `number` | Border-radius of the keyhole. Match your button/card radius for a seamless look. |

## Accessibility

Default NextStep cards are minimal. A production-quality card should:

- Wrap the card in `role="dialog"` + `aria-modal="true"` + `aria-labelledby` pointing to the title element (as in the paste-ready example above).
- Ensure focus moves into the card when it appears — use `autoFocus` on the primary button or a `ref` + `.focus()` in a `useEffect`.
- Respect `step.blockKeyboardControl`: when true, don't bind your own keyboard shortcuts either.
- Provide visible text for every button (no icon-only unless paired with `aria-label`).
- Maintain sufficient contrast in both light and dark themes — the example uses `neutral-900` on `white` and `neutral-100` on `neutral-900`, both > 4.5:1.

## Dark mode integration

NextStep has no built-in dark mode. For dark mode to "just work":

1. Place `<NextStep>` **inside** your theme provider, not outside it.
2. Use CSS variables or Tailwind `dark:` classes inside your custom card that respond to the app's theme class (`class="dark"` on `<html>`).
3. The default card does not support dark mode — always use a custom card if dark mode matters.

See `assets/custom-card.tsx` for the drop-in version of the component above.
