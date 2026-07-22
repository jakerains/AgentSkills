# Driver.js Recipes

Copy-and-adapt patterns for real tours. Each is self-contained. All assume:

```js
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
```

## Table of contents
- [Interactive / click-driven tour](#interactive--click-driven-tour)
- [Waiting for on-demand elements (modals, dropdowns)](#waiting-for-on-demand-elements)
- [Multi-page / resumable tour](#multi-page--resumable-tour)
- [Confirm on exit](#confirm-on-exit)
- [Prevent exit until complete](#prevent-exit-until-complete)
- [Custom progress text](#custom-progress-text)
- [Async / fully manual navigation](#async--fully-manual-navigation)
- [Popover positioning](#popover-positioning)
- [Run the tour only once](#run-the-tour-only-once)
- [Hints workflow](#hints-workflow)

---

## Interactive / click-driven tour

Let the user advance by *using the product* — clicking the highlighted element instead of a Next button. `advanceOnClick` fires the advance; the element's own click still runs.

```js
const driverObj = driver({
  advanceOnClick: true,
  showProgress: true,
  steps: [
    { element: "#pick-plan",     popover: { title: "Pick a Plan", description: "Click the highlighted card to continue." } },
    { element: "#billing-toggle",popover: { title: "Billing", description: "Clicking advances the tour; the toggle still flips." } },
    { element: "#checkout-btn",  popover: { title: "Checkout", description: "Clicking the last element ends the tour." } },
  ],
});
driverObj.drive();
```

**Tip:** to make the element the *only* way forward, hide the next button on that step: `popover: { showButtons: ["close"] }`. Note `advanceOnClick` has no effect on steps where `disableActiveInteraction` blocks the click.

---

## Waiting for on-demand elements

Click-driven steps often open a modal/dropdown whose target doesn't exist yet. `waitForElement` holds the current step until the element appears (up to the timeout).

```js
const driverObj = driver({
  steps: [
    {
      element: "#open-modal-btn",
      advanceOnClick: true,
      popover: {
        title: "Open the Modal",
        description: "Clicking this opens the modal and moves the tour on.",
        showButtons: ["close"],
      },
    },
    {
      element: "#modal-confirm",   // rendered on demand
      waitForElement: 5000,        // wait up to 5s; stay on the previous step meanwhile
      popover: { title: "Confirm", description: "This step appeared once the modal rendered." },
    },
  ],
});
driverObj.drive();
```

If the element never appears, the wait times out into the usual missing-element behavior: the centered fallback popover, or a skip when `skipMissingElement: true`.

---

## Multi-page / resumable tour

A driver instance lives within one page. For tours that cross a navigation, treat the tour as **resumable**: persist the step to resume at, let the app navigate normally, and start a fresh tour from the saved step on the next page.

```js
const TOUR_KEY = "app-tour-step";

export function createTour() {
  let isNavigating = false;

  const driverObj = driver({
    steps: [
      { element: "#reports-nav", popover: { title: "Reports", description: "Your reports live here." } },
      {
        element: "#settings-link",
        advanceOnClick: true, // clicking the link continues the tour AND navigates
        popover: {
          title: "Open Settings",
          description: "Click this link to continue on the settings page.",
          showButtons: ["close"],
          onNextClick: () => {
            // Next step lives on another page: save where to resume and tear down.
            // The link's own navigation still happens.
            isNavigating = true;
            localStorage.setItem(TOUR_KEY, "2");
            driverObj.destroy();
          },
        },
      },
      // Steps on the settings page. waitForElement absorbs the client-side route render delay.
      { element: "#profile-form",  waitForElement: 5000, popover: { title: "Your Profile", description: "Update your details here." } },
      { element: "#save-settings", popover: { title: "Save", description: "Don't forget to save your changes." } },
    ],
    onDestroyed: () => {
      // Finished or exited: clear saved progress. Skipped for the hand-off destroy above.
      if (!isNavigating) localStorage.removeItem(TOUR_KEY);
    },
  });

  return driverObj;
}
```

Resume on every page load (or router mount hook):

```js
const savedStep = localStorage.getItem(TOUR_KEY);
if (savedStep !== null) createTour().drive(Number(savedStep));
```

Notes:
- The explicit `destroy()` in the hand-off matters for SPAs, where the old page's tour would otherwise linger on screen.
- Prefer computing the resume index (`driverObj.getActiveIndex() + 1`) or storing a step **id** rather than a hardcoded index, so reordering steps doesn't break saved progress.

---

## Confirm on exit

Use `onDestroyStarted` to intercept exit attempts. **You must call `destroy()` yourself** once you override it.

```js
const driverObj = driver({
  showProgress: true,
  steps: [ /* ... */ ],
  onDestroyStarted: () => {
    if (!driverObj.hasNextStep() || confirm("Are you sure you want to exit the tour?")) {
      driverObj.destroy();
    }
  },
});
driverObj.drive();
```

---

## Prevent exit until complete

Force completion by disabling all the exit affordances.

```js
const driverObj = driver({
  showProgress: true,
  allowClose: false, // no backdrop-click / Esc exit
  steps: [ /* ... */ ],
});
driverObj.drive();
```

For an even harder lock, also drop the close button: `showButtons: ["next", "previous"]`.

---

## Custom progress text

```js
driver({
  showProgress: true,
  progressText: "Step {{current}} of {{total}}",
  // or per popover:
  steps: [
    { element: "#a", popover: { title: "A", description: "…", showProgress: true, progressText: "{{current}}/{{total}}" } },
  ],
});
```

---

## Async / fully manual navigation

When you need to run async work (fetch, await an animation) between steps, override `onNextClick`/`onPrevClick` and drive navigation yourself.

```js
const driverObj = driver({
  steps: [
    {
      element: "#step-1",
      popover: {
        title: "Step 1",
        description: "We'll load data before moving on.",
        onNextClick: async () => {
          await loadNextSectionData();     // your async work
          driverObj.moveNext();            // YOU advance — the button no longer does
        },
      },
    },
    { element: "#step-2", popover: { title: "Step 2", description: "Loaded." } },
  ],
});
driverObj.drive();
```

---

## Popover positioning

`side` picks which side of the element (`top`/`right`/`bottom`/`left`, default `bottom`); `align` positions along it (`start`/`center`/`end`, default `start`). The popover auto-flips to stay in the viewport, so treat these as preferences.

```js
driver().highlight({
  element: "#left-start",
  popover: { title: "Title", description: "Description", side: "left", align: "start" },
});
```

---

## Run the tour only once

```js
const driverObj = driver({
  steps: [ /* ... */ ],
  onDestroyed: () => localStorage.setItem("onboarding_tour_done", "1"),
});

if (!localStorage.getItem("onboarding_tour_done")) {
  driverObj.drive();
}
```

For per-account gating, swap `localStorage` for a value you fetch from your backend / user record.

---

## Hints workflow

Non-blocking beacons that open on click. Separate import.

```js
import { hints } from "driver.js/hints";
import "driver.js/dist/hints.css";

const productHints = hints({
  buttonText: "Got it",
  hints: [
    { id: "export",  element: "#export-btn", popover: { title: "Export", description: "Download as CSV or PDF." } },
    { id: "summary", element: "#summary",    beacon: { side: "right", align: "center" },
      popover: { title: "Auto summary", description: "Written from your numbers." } },
  ],
  onDismiss: (el, hint) => {
    // persist so it doesn't come back next visit
    const seen = JSON.parse(localStorage.getItem("hints_seen") || "[]");
    localStorage.setItem("hints_seen", JSON.stringify([...new Set([...seen, hint.id])]));
  },
});

productHints.show();

// Re-hide already-seen beacons on load:
JSON.parse(localStorage.getItem("hints_seen") || "[]").forEach((id) => productHints.dismiss(id));
```

Add `overlay: true` to the config to dim the page and spotlight the element while a hint is open (see `references/configuration.md`).
