# Driver.js Theming & Styling

Two levers, usually combined: (1) add a class with `popoverClass` and write CSS, and (2) override CSS variables. For anything the classes can't reach, mutate the DOM in `onPopoverRender`.

## Applying a custom class

```js
// Globally — every popover in this instance gets the class
const driverObj = driver({ popoverClass: "my-theme" });

// Per step — only this step's popover
driver({
  steps: [
    { element: "#el", popover: { title: "T", description: "D", popoverClass: "danger-theme" } },
  ],
});
```

## Popover classes

Style these in conjunction with your `popoverClass` (e.g. `.driver-popover.my-theme .driver-popover-title`).

```css
.driver-popover {}                 /* popover wrapper */
.driver-popover-arrow {}           /* arrow pointing at the highlighted element */

/* ACTUAL rendered side/align after viewport-flipping (may differ from what you configured) */
.driver-popover-side-top {}
.driver-popover-side-right {}
.driver-popover-side-bottom {}
.driver-popover-side-left {}
.driver-popover-align-start {}
.driver-popover-align-center {}
.driver-popover-align-end {}

.driver-popover-title {}
.driver-popover-description {}
.driver-popover-close-btn {}       /* top-right close (×) */

.driver-popover-footer {}          /* footer holding progress + nav buttons */
.driver-popover-progress-text {}
.driver-popover-prev-btn {}
.driver-popover-next-btn {}

/* Shared footer button look. Built-in prev/next carry it; add it to your own custom buttons
   (created in onPopoverRender) to inherit the default styling, or leave it off to style yourself. */
.driver-popover-footer-btn {}

/* The next button on the last step, acting as "Done" */
.driver-popover-next-btn.driver-popover-done-btn {}
```

**Arrow color gotcha:** the arrow is a CSS-border triangle. When you change the popover background, set the matching border color per side, e.g. for a bottom-placed popover: `.driver-popover-arrow { border-bottom-color: <bg>; }`. Repeat for the sides you actually use (`border-top-color`, `border-left-color`, `border-right-color`).

## Page / overlay / element state classes

```css
/* Added to <body> while the driver is: */
.driver-active {}   /* active */
.driver-fade {}     /* animated */
.driver-simple {}   /* not animated */

.driver-overlay {}          /* the SVG lightbox/overlay over the page */
.driver-active-element {}   /* the currently highlighted element itself */
```

Use `body.driver-active` to, say, hide a floating chat widget during a tour, or `.driver-active-element` to add a glow to the spotlighted element.

## Custom font

The popover font stack defaults to:
```
"Helvetica Neue", Inter, ui-sans-serif, "Apple Color Emoji", Helvetica, Arial, sans-serif;
```
Override the inherited `--driver-popover-font-family` anywhere above the popover (`:root`, `body`, or a `popoverClass`). It applies to title, description, buttons, and progress text at once.

```css
:root { --driver-popover-font-family: "Inter", sans-serif; }
```

## Dark mode

Because state classes live on `<body>` and popover classes are stable, a media query is enough — no JS:

```css
@media (prefers-color-scheme: dark) {
  .driver-popover {
    background-color: #1f2937;
    color: #f9fafb;
  }
  .driver-popover-title { color: #fff; }
  .driver-popover-description { color: #d1d5db; }
  .driver-popover-arrow { border-bottom-color: #1f2937; } /* match the side(s) you use */
  .driver-popover-next-btn,
  .driver-popover-prev-btn {
    background: #374151;
    color: #f9fafb;
    text-shadow: none;
  }
}
```

Prefer a class-based toggle? Scope the same rules under `html.dark .driver-popover { ... }`.

## Modifying the popover DOM — `onPopoverRender`

For markup the classes can't express (extra buttons, images, a progress bar), mutate the DOM after render. The hook gets a `PopoverDOM` with live element references:

```ts
type PopoverDOM = {
  wrapper: HTMLElement;
  arrow: HTMLElement;
  title: HTMLElement;
  description: HTMLElement;
  footer: HTMLElement;
  progress: HTMLElement;
  previousButton: HTMLElement;
  nextButton: HTMLElement;
  closeButton: HTMLElement;
  footerButtons: HTMLElement;
};
```

```js
driver({
  onPopoverRender: (popover, { config, state }) => {
    const skip = document.createElement("button");
    skip.innerText = "Skip tour";
    skip.className = "driver-popover-footer-btn"; // inherit default button look
    skip.addEventListener("click", () => driverObj.destroy());
    popover.footerButtons.appendChild(skip);
  },
});
```

## Styling hints (beacons)

Hint **popovers** are ordinary Driver.js popovers — every class above applies unchanged.

Hint **beacons** read two CSS variables. Set them globally, or scope them per beacon via a hint's `beacon.className`:

```css
.driver-hint {
  --driver-hint-size: 32px;    /* beacon diameter */
  --driver-hint-color: #e11d48;/* beacon color */
}

/* Scoped to one beacon via { beacon: { className: "danger-beacon" } } */
.danger-beacon {
  --driver-hint-color: #dc2626;
  --driver-hint-size: 40px;
}
```

Disable the pulse per beacon with `beacon: { animate: false }` (it also auto-pauses for users who prefer reduced motion). The optional hint dimming overlay is configured on the `hints()` config (`overlay`, `overlayColor`, `overlayOpacity`) — see `references/configuration.md`.
