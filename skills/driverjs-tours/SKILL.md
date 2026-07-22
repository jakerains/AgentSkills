---
name: driverjs-tours
description: Build product tours, onboarding walkthroughs, feature spotlights, and pulsing feature hints with Driver.js — the lightweight, dependency-free JS library. Use whenever adding a guided tour, onboarding flow, coach marks, highlight overlay, "what's new" callout, interactive click-through walkthrough, or beacon/hint UI to any web app (vanilla JS, React, Next.js, Vue, Svelte, Angular), and when styling or theming Driver.js popovers, overlays, and hints to match a brand. Triggers include driver.js, driverjs, product tour, onboarding tour, guided tour, walkthrough, feature highlight, spotlight, coach marks, tooltip tour, feature hints, beacons, "show users around", "highlight this element", driverObj.drive(), driverObj.highlight(), popover styling, overlay dimming. Prefer this skill over hand-rolling tooltips or reaching for heavier tour libraries when the goal is a focused, overlay-based highlight or step-through.
---

# Driver.js Tours & Hints

Driver.js is a ~5kb, dependency-free library that dims the page, cuts a spotlight around a target element, and shows a popover next to it. Use it for **product tours** (multi-step walkthroughs), **single-element highlights** (spotlight one thing), and **hints** (pulsing beacons that open a popover on click, with no overlay by default).

## Two entry points — import only what you use

| Feature | Import | CSS | Factory |
|---|---|---|---|
| Tours + single highlights | `import { driver } from "driver.js"` | `driver.js/dist/driver.css` | `driver(config)` |
| Hints (pulsing beacons) | `import { hints } from "driver.js/hints"` | `driver.js/dist/hints.css` | `hints(config)` |

Hints ship as a separate bundle so tour-only apps never load them. Never import `hints` unless the task actually needs beacons.

## Install

```bash
npm install driver.js
```

CDN (globals `window.driver.js.driver` and `window.driverHints.hints`):

```html
<script src="https://cdn.jsdelivr.net/npm/driver.js@latest/dist/driver.js.iife.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@latest/dist/driver.css" />
```

For production, prefer `npm install` (bundled, versioned). If you must use the CDN, pin an exact version instead of `@latest` and add Subresource Integrity — e.g. `<script src="https://cdn.jsdelivr.net/npm/driver.js@1.4.0/dist/driver.js.iife.js" integrity="sha384-…" crossorigin="anonymous"></script>` (grab the current hash from the jsDelivr "SRI" panel for the exact file).

## Quick start

**Multi-step tour** — pass a `steps` array, then call `.drive()`:

```js
import { driver } from "driver.js";
import "driver.js/dist/driver.css";

const driverObj = driver({
  showProgress: true,
  steps: [
    { element: ".page-header", popover: { title: "Header", description: "Your title lives here." } },
    { element: "#new-btn",      popover: { title: "Create", description: "Start something new.", side: "left", align: "start" } },
    { element: ".sidebar",      popover: { title: "Navigate", description: "Jump between sections." } },
    { popover: { title: "You're set!", description: "That's the tour — enjoy." } }, // no element = centered step
  ],
});

driverObj.drive();
```

**Single highlight** — one element, no buttons by default:

```js
const driverObj = driver();
driverObj.highlight({
  element: "#some-element",
  popover: { title: "Heads up", description: "This is the thing." },
});
```

Key facts that shape correct usage:
- **A step with no `element` is a valid, intentional centered popover** (great for intro/outro). It is never treated as "missing."
- **`element` accepts** a CSS selector string, a live `Element`, or a `() => Element` function.
- **The popover auto-flips** to fit the viewport, so your `side`/`align` are a preference, not a guarantee.
- **Each `driver()` / `hints()` call is an independent instance.** Multiple can coexist on one page without interfering. Always keep a reference (`driverObj`) so you can call `.destroy()`, `.moveNext()`, etc.

## The config options you reach for most

Set these at the driver level (whole tour) or override per step / per popover.

```js
driver({
  animate: true,            // animated stage transitions (default true)
  overlayColor: "black",    // backdrop color
  overlayOpacity: 0.5,      // backdrop opacity
  smoothScroll: false,      // smooth-scroll to each element
  allowClose: true,         // click backdrop / press Esc to exit — set false to force completion
  allowKeyboardControl: true,
  stagePadding: 10,         // gap between element and the cutout edge
  stageRadius: 5,           // corner radius of the cutout
  showProgress: false,      // "1 of 4" text
  progressText: "{{current}} of {{total}}",
  showButtons: ["next", "previous", "close"], // which footer buttons appear
  nextBtnText: "Next", prevBtnText: "Back", doneBtnText: "Done",
  popoverClass: "my-theme", // custom class on every popover (for styling)
  disableActiveInteraction: false, // true = block clicks on the highlighted element
});
```

**Two newer options that solve most real-world tour problems** — see `references/recipes.md` for full examples:
- `advanceOnClick: true` — clicking the highlighted element advances the tour (like pressing Next). The element's own click still fires. This is how you build tours users drive *by using the product*.
- `waitForElement: 5000` — wait up to N ms for a step's element to appear before falling back. Essential when a click opens a modal/dropdown whose target is rendered on demand. Also `skipMissingElement: true` to skip absent targets instead of showing the centered fallback.

## Driving the tour programmatically

```js
driverObj.drive();          // start at step 0
driverObj.drive(3);         // start at step 3
driverObj.moveNext();
driverObj.movePrevious();
driverObj.moveTo(2);
driverObj.getActiveIndex(); // current step index
driverObj.isActive();
driverObj.refresh();        // recompute after layout change
driverObj.setSteps([...]);  // swap steps
driverObj.destroy();        // tear down
```

Full method list: `references/api-reference.md`.

## Lifecycle hooks (analytics, gating, cleanup)

Every hook receives `(element, step, { config, state, driver, index })`:

```js
driver({
  onHighlightStarted: (el, step, { index }) => track("tour_step_view", { index }),
  onDestroyStarted: () => {                    // fires when user tries to exit
    if (!driverObj.hasNextStep() || confirm("Leave the tour?")) driverObj.destroy();
    // Overriding this hook means YOU must call destroy() to actually exit.
  },
  onDestroyed: () => localStorage.setItem("tour_done", "1"),
});
```

Override `onNextClick` / `onPrevClick` (driver- or step-level) to take full control of navigation — but then *you* must call `moveNext()`/`movePrevious()`. `onDoneClick` fires on the last step's button and, when provided, suppresses the automatic teardown so you control it. Details in `references/configuration.md`.

## Framework integration

Driver.js is framework-agnostic (it works on the real DOM). The universal rule: **create the instance after the target elements are mounted, and `destroy()` on unmount.** See `references/framework-integration.md` for copy-paste React/Next.js `useEffect` hooks, a `useDriver` wrapper, Vue `onMounted`, Svelte `onMount`, and Angular `ngAfterViewInit` patterns, plus SSR guidance (Driver.js touches `document`, so guard it).

## Styling & theming

Two ways to theme, often combined:
1. **Add a class** via `popoverClass` (globally or per step) and write CSS against `.driver-popover` and friends.
2. **Override CSS variables** like `--driver-popover-font-family`.

Minimal brand example:

```css
.driver-popover.my-theme {
  background: #1e293b;
  color: #f8fafc;
  border-radius: 12px;
}
.driver-popover.my-theme .driver-popover-title { font-size: 16px; }
.driver-popover.my-theme .driver-popover-arrow { border-bottom-color: #1e293b; }
```

The complete class list (popover parts, arrow, footer buttons, active-element, overlay, body state classes), the `onPopoverRender` DOM-injection hook, dark-mode patterns, and hint/beacon styling variables (`--driver-hint-size`, `--driver-hint-color`) are in `references/theming.md`.

## Feature hints (beacons)

When the task is "draw attention to a few things without blocking the page," use hints, not a tour:

```js
import { hints } from "driver.js/hints";
import "driver.js/dist/hints.css";

const productHints = hints({
  hints: [
    { element: "#export-btn", popover: { title: "Export", description: "Download as CSV or PDF." } },
    { element: "#summary",    popover: { title: "Auto summary", description: "Written from your numbers." } },
  ],
});
productHints.show();   // mount the beacons
```

Beacons persist, open on click, and can be dismissed (`productHints.dismiss("id")`) and restored. Full API and the optional dimming overlay: `references/api-reference.md` and `references/theming.md`.

## References — load on demand

- **`references/configuration.md`** — every `Config`, `Popover`, `DriveStep`, `HintsConfig`, `DriverHint`, and `State` field with exact types and defaults. Read when you need an option not covered above.
- **`references/api-reference.md`** — full method list for `driver()` and `hints()` instances.
- **`references/theming.md`** — all CSS classes/variables, `onPopoverRender`, dark mode, hint styling.
- **`references/recipes.md`** — ready-to-adapt patterns: interactive/click-driven tours, multi-page (resumable) tours, confirm-on-exit, prevent-exit, custom progress, async/manual navigation, popover positioning, and hints workflows.
- **`references/framework-integration.md`** — React/Next.js, Vue, Svelte, Angular wiring + SSR guards.
