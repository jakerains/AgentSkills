// Drop into `app/layout.tsx` (App Router) — or adapt to `pages/_app.tsx` (Pages Router).
//
// What this gives you:
// - NextStepProvider + NextStep wrapped around your app
// - Custom card component with dark mode support
// - All four lifecycle callbacks wired into an `analytics` module
// - Overlay tuning defaults that work with most modern UI libraries
//
// Requires:
// - `npm i nextstepjs motion`
// - `lib/tours.ts` exporting a `tours: Tour[]` array (see `tours.ts` in this folder)
// - `components/custom-card.tsx` exporting `CustomCard` (see `custom-card.tsx` in this folder)
// - `lib/analytics.ts` exporting a `track(event, payload)` function — replace with your analytics SDK

'use client';

import { NextStep, NextStepProvider } from 'nextstepjs';
import type { ReactNode } from 'react';
import { tours } from '@/lib/tours';
import { CustomCard } from '@/components/custom-card';
import { track } from '@/lib/analytics';

export function NextStepShell({ children }: { children: ReactNode }) {
  return (
    <NextStepProvider>
      <NextStep
        steps={tours}
        cardComponent={CustomCard}
        // Overlay: slightly darker than default, raised z-index to sit above Radix/MUI modals
        shadowRgb="15, 23, 42"
        shadowOpacity="0.55"
        overlayZIndex={10000}
        // Transition: snappier than the default anticipate/600ms
        cardTransition={{ ease: 'easeOut', duration: 0.35 }}
        // Lifecycle → analytics
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

// If you're in App Router and want NextStepShell to be your root layout, wrap it like this:
//
//   // app/layout.tsx
//   import { NextStepShell } from '@/components/nextstep-shell';
//
//   export default function RootLayout({ children }: { children: React.ReactNode }) {
//     return (
//       <html lang="en">
//         <body>
//           <NextStepShell>{children}</NextStepShell>
//         </body>
//       </html>
//     );
//   }
//
// Place `<NextStepShell>` *inside* your theme provider if you use one, so Tailwind `dark:` classes
// in CustomCard respond to the active theme.
