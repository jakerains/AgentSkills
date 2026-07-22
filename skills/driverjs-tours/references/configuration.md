# Driver.js Configuration Reference

Exact fields, types, and defaults for every configuration object. Source: driver.js official docs (v1.4+ / current). Config, steps, and state belong to the specific `driver()` instance you set them on — instances never share state.

## Table of contents
- [Driver Config](#driver-config) — top-level `driver({...})` options
- [Popover](#popover) — the tooltip shown per step
- [DriveStep](#drivestep) — one step in the `steps` array (or the `highlight()` arg)
- [HintsConfig](#hintsconfig) — top-level `hints({...})` options
- [DriverHint](#driverhint) — one hint (beacon + popover)
- [State](#state) — read via `getState()`, also passed to hooks
- [Hook signature notes](#hook-signature-notes)

---

## Driver Config

Passed to `driver(config)` or `driverObj.setConfig(config)`.

```ts
type Config = {
  steps?: DriveStep[];              // steps for a product tour

  animate?: boolean;                // animate transitions (default: true)
  duration?: number;                // transition/fade duration in ms; only when animate=true (default: 400)
  overlayColor?: string;            // backdrop color (default: "black")
  overlayOpacity?: number;          // backdrop opacity (default: 0.5)
  smoothScroll?: boolean;           // smooth-scroll to the element (default: false)

  allowClose?: boolean;             // allow closing by clicking backdrop / Esc (default: true)
  allowScroll?: boolean;            // allow page scroll while active; false locks body scroll (default: true)
  allowKeyboardControl?: boolean;   // arrow keys / Esc navigation (default: true)

  // What happens when the overlay backdrop is clicked (default: "close")
  overlayClickBehavior?: "close" | "nextStep"
    | ((element: Element | undefined, step: DriveStep, options: HookOptions) => void);

  stagePadding?: number;            // gap between element and cutout (default: 10)
  stageRadius?: number;             // corner radius of the cutout (default: 5)

  disableActiveInteraction?: boolean; // block clicks on the highlighted element (default: false); also per-step

  advanceOnClick?: boolean;         // clicking the highlighted element advances the tour (default: false); also per-step
                                    // element's own click still runs; onNextClick/onDoneClick still apply;
                                    // no effect when disableActiveInteraction blocks the click.

  skipMissingElement?: boolean;     // skip a step whose specified element is missing, instead of the centered
                                    // fallback popover (default: false); also per-step. Steps with NO element
                                    // are intentional centered steps and are never skipped.

  waitForElement?: number;          // wait up to N ms for a step's element to appear before treating it as
                                    // missing (default: 0 = off); also per-step. Current step stays highlighted
                                    // while waiting. Use when the next target is rendered on demand.

  popoverClass?: string;            // custom class on every popover
  popoverOffset?: number;           // distance between popover and element (default: 10)

  showButtons?: AllowedButtons[];   // buttons to show; default ["next","previous","close"] for tours, [] for highlight
  disableButtons?: AllowedButtons[];// buttons to render disabled

  showProgress?: boolean;           // show progress text (default: false)
  progressText?: string;            // template, placeholders {{current}} {{total}} (default: "{{current}} of {{total}}")

  nextBtnText?: string;
  prevBtnText?: string;
  doneBtnText?: string;             // used on the last step

  // Hooks — see "Hook signature notes" below for the shared signature
  onPopoverRender?: (popover: PopoverDOM, options: HookOptions) => void;
  onHighlightStarted?: HookFn;      // before an element is highlighted
  onHighlighted?: HookFn;           // after highlighted
  onDeselected?: HookFn;            // when a step is left (index points at the step being moved TO)
  onDestroyStarted?: HookFn;        // user tries to exit — you must call destroy() yourself if you override it
  onDestroyed?: HookFn;             // after teardown
  onNextClick?: HookFn;             // override next navigation (you must call moveNext())
  onPrevClick?: HookFn;             // override prev navigation (you must call movePrevious())
  onCloseClick?: HookFn;            // close button clicked
  onDoneClick?: HookFn;             // last-step button; runs INSTEAD of onNextClick and suppresses auto-destroy
};

type AllowedButtons = "next" | "previous" | "close";
```

**Navigation-override caveat:** overriding `onNextClick`/`onPrevClick` disables the built-in button navigation for those directions — you become responsible for calling `driverObj.moveNext()` / `driverObj.movePrevious()`. These can be set at the driver level (all steps) or per step.

**`onDoneClick`:** lets you detect tour completion via the done button. When provided, Driver.js does **not** auto-destroy; call `driverObj.destroy()` yourself.

---

## Popover

The tooltip. Configure globally (rare), but usually per step via `step.popover`.

```ts
type Popover = {
  title?: string;                   // HTML allowed; omit either title or description to show only one
  description?: string;             // HTML allowed

  side?: "top" | "right" | "bottom" | "left";   // preferred side (default: "bottom"); auto-flips to fit viewport
  align?: "start" | "center" | "end";           // alignment along that side (default: "start")

  showButtons?: ("next" | "previous" | "close")[];
  disableButtons?: ("next" | "previous" | "close")[];
  nextBtnText?: string;
  prevBtnText?: string;
  doneBtnText?: string;

  showProgress?: boolean;
  progressText?: string;            // {{current}} / {{total}}

  popoverClass?: string;            // custom class for THIS popover (styling)

  onPopoverRender?: (popover: PopoverDOM, options: HookOptions) => void;
  onNextClick?: HookFn;
  onPrevClick?: HookFn;
  onCloseClick?: HookFn;
  onDoneClick?: HookFn;             // runs instead of onNextClick on the last step
};
```

---

## DriveStep

One entry in `steps`, or the single argument to `driverObj.highlight()`.

```ts
type DriveStep = {
  element?: Element | string | (() => Element);  // CSS selector (first match), live element, or a getter.
                                                 // Omit for an intentional centered step.
  popover?: Popover;

  disableActiveInteraction?: boolean;   // block clicks on this element (default: false)
  advanceOnClick?: boolean;             // clicking this element advances the tour (overrides driver-level)
  skipMissingElement?: boolean;         // skip this step if the element is missing (overrides driver-level)
  waitForElement?: number;              // wait up to N ms for this element (overrides driver-level)

  data?: Record<string, any>;           // arbitrary payload, available in hooks via step.data

  onDeselected?: HookFn;
  onHighlightStarted?: HookFn;
  onHighlighted?: HookFn;
};
```

---

## HintsConfig

Passed to `hints(config)` from the `driver.js/hints` entry.

```ts
type HintsConfig = {
  hints?: DriverHint[];

  beacon?: HintBeacon;              // beacon defaults for every hint; a hint's own beacon values win
  buttonText?: string;             // dismiss button text (default: "Got it")

  popoverClass?: string;
  popoverOffset?: number;

  // Optional dimming overlay: cuts out the hint's element like a tour step, anchors the popover to
  // the element, steps the open hint's beacon aside, and closes the hint when the dim is clicked.
  overlay?: boolean;               // (default: false)
  overlayColor?: string;           // (default: "#000")
  overlayOpacity?: number;         // (default: 0.7)

  // Hooks — receive (element, hint, { config, hints })
  onOpen?: (element: Element, hint: DriverHint, options: HintsHookOptions) => void;
  onDismiss?: (element: Element, hint: DriverHint, options: HintsHookOptions) => void;
  // Runs instead of dismissing when the built-in button is clicked. Call options.hints.dismiss(hint.id)
  // yourself to also remove the hint. Can be set per hint.
  onButtonClick?: (element: Element, hint: DriverHint, options: HintsHookOptions) => void;
};

type HintsHookOptions = { config: HintsConfig; hints: Hints };
```

---

## DriverHint

One entry of the `hints` array.

```ts
type DriverHint = {
  element: Element | string | (() => Element);  // required. Missing element → hint skipped, picked up on next show()
  id?: string;                                  // stable identity for open/dismiss/restore (defaults to index)

  beacon?: {
    side?: "top" | "right" | "bottom" | "left"; // edge the beacon sits on (default: "top")
    align?: "start" | "center" | "end";         // position along that edge (default: "end")
    offsetX?: number;                            // px nudge (+right/-left) (default: 0)
    offsetY?: number;                            // px nudge (+down/-up) (default: 0)
    animate?: boolean;                           // pulse; pauses for reduced-motion users (default: true)
    className?: string;                          // scope --driver-hint-size / --driver-hint-color to this beacon
  };

  popover?: {
    title?: string;
    description?: string;
    side?: "top" | "right" | "bottom" | "left";
    align?: "start" | "center" | "end";
    popoverClass?: string;
    showButton?: boolean;                        // show dismiss button (default: true)
    buttonText?: string;                         // overrides instance buttonText
    onButtonClick?: (element: Element, hint: DriverHint, options: HintsHookOptions) => void;
    onPopoverRender?: (popover: PopoverDOM, options: { hint: DriverHint; hints: Hints }) => void;
  };

  onOpen?: (element: Element, hint: DriverHint, options: HintsHookOptions) => void;   // takes precedence over instance-level
  onDismiss?: (element: Element, hint: DriverHint, options: HintsHookOptions) => void;

  data?: Record<string, any>;
};
```

---

## State

Read via `driverObj.getState()`; also passed to every hook as `options.state`.

```ts
type State = {
  isInitialized?: boolean;   // whether the driver is active
  activeIndex?: number;      // current step index (tour mode)
  activeElement?: Element;   // current highlighted element
  activeStep?: DriveStep;    // current step object
  previousElement?: Element;
  previousStep?: DriveStep;
  popover?: PopoverDOM;      // container, title, description, buttons, etc.
};
```

---

## Hook signature notes

The shared hook shape referenced above as `HookFn`:

```ts
type HookOptions = { config: Config; state: State; driver: Driver; index: number | undefined };
type HookFn = (element: Element | undefined, step: DriveStep, options: HookOptions) => void;
```

- `element` is `undefined` for centered (element-less) steps.
- `options.index` is the zero-based active step index (same as `getActiveIndex()`), or `undefined` when driving a single `highlight()` rather than a `steps` array.
- Inside `onDeselected` (fires for the step being *left* during a transition), `index` points at the step being **moved to**, not the one being deselected. Read the deselected step from the `step` argument.
