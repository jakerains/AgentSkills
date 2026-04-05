# Multi-Page Tours & Viewports

NextStep tours can span multiple routes (`nextRoute`/`prevRoute`) and can be scoped to scrollable containers (`NextStepViewport`). Both are essential for real-world apps where the interesting stuff isn't on a single page.

## `nextRoute` / `prevRoute`

Add these to a step to make Next/Prev buttons navigate before showing the adjacent step:

```ts
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

### Lifecycle

When the user clicks Next on a step with `nextRoute`:

1. The Next.js navigation adapter pushes `/settings`.
2. NextStep waits until the selector of the **next** step is found in the DOM.
3. Once the selector exists, the next step renders.

Until step 3 completes, **the tour appears frozen**. This is the source of nearly every "my tour is broken" issue — the target element never appears, so the step never advances.

### The placeholder-anchor pattern

On async-rendered pages (pages that fetch data, use Suspense, or dynamically import components), the element the next step targets may not exist immediately after navigation. To avoid a stuck tour:

**Always render a minimal placeholder with the step's `id` before the async content resolves.**

```tsx
// app/settings/page.tsx
import { Suspense } from 'react';
import { SettingsContent } from './settings-content';

export default function SettingsPage() {
  return (
    <main>
      {/* Placeholder anchor for the NextStep step — always present, server-rendered */}
      <div id="settings-header" aria-hidden="true" />

      <Suspense fallback={<SettingsSkeleton />}>
        <SettingsContent />
      </Suspense>
    </main>
  );
}
```

Now `nextRoute: '/settings'` works reliably — the anchor exists immediately, so NextStep's wait loop resolves on the first tick.

**Alternative**: put the `id` on the `<main>` or layout element if the step can tolerate a slightly coarser anchor. The goal is simply that the id exists at the moment of navigation.

### Returning to a previous page

`prevRoute` mirrors `nextRoute`:

```ts
{
  icon: '🎉',
  title: 'Welcome to settings',
  content: 'Click Back to return.',
  selector: '#settings-header',
  side: 'bottom',
  showControls: true,
  prevRoute: '/dashboard',
}
```

Apply the same placeholder pattern on whatever page you navigate back to.

### Round-trip tours

A step can set **both** `nextRoute` and `prevRoute` to navigate away and back:

```ts
{
  icon: '❤️',
  title: 'Side quest',
  content: 'This step lives on the homepage.',
  selector: '#home-hero',
  side: 'bottom',
  showControls: true,
  prevRoute: '/docs',   // Prev returns to docs
  nextRoute: '/docs',   // Next also returns to docs (to the next step there)
}
```

This is useful for tutorials that need to show off something on a different route then return the user to their task.

## `NextStepViewport`

Default positioning uses `document.body`. That fails when your target lives inside a scrollable div — the card positions relative to the viewport edge, not the container, and scroll-into-view logic looks at the wrong scrollable element.

Wrap the scrollable container with `<NextStepViewport id="...">` and set `viewportID` on the step:

```tsx
import { NextStepViewport } from 'nextstepjs';

<div className="max-h-[400px] overflow-auto border">
  <NextStepViewport id="data-table">
    <table>
      {rows.map((row) => (
        <tr key={row.id} id={`row-${row.id}`}>
          {/* cells */}
        </tr>
      ))}
    </table>
  </NextStepViewport>
</div>
```

```ts
{
  icon: '🔍',
  title: 'Pinned row',
  content: 'This row highlights what needs your attention.',
  selector: '#row-42',
  side: 'top',
  viewportID: 'data-table',
  showControls: true,
}
```

NextStep will:
1. Position the card relative to the viewport container, not the document body.
2. Scroll the viewport so the target is visible.
3. Handle resize and partial-visibility edge cases automatically.

### When to use `NextStepViewport`

- Scrollable tables or data grids
- Form wizards with fixed-height sections
- Dashboard panels with independent scroll
- Code editors or text areas highlighting specific lines
- Modals that contain scrollable content

### When **not** to use it

- Page-level targets — use default positioning.
- Elements inside a container with `overflow: visible` — there's no clipping, so default positioning works fine.
- Elements that are already fully visible — no scroll management needed.

## Combining routing + viewports

Perfectly legal: a step can have both `nextRoute` and `viewportID`. NextStep navigates, waits for the selector, then positions the card inside the target viewport. The placeholder-anchor pattern still applies — just make sure the placeholder is inside the `<NextStepViewport>` wrapper on the target page.

## Custom navigation adapter (non-Next.js)

If you're using NextStep in a non-Next.js React app (React Router, Remix, plain React Router), see `references/api-reference.md` for the `NavigationAdapter` hook pattern. For Next.js users, the adapter is built-in and nothing more is needed.
