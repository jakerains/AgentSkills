# Tutorial Authoring — Interactive Lessons with NextStep

This file is the core of the skill. NextStep can do generic "welcome tours", but its real power is for **interactive tutorials** — step-by-step lessons that require the user to perform each action before advancing. This pattern turns a tour into a teacher.

## Table of Contents

- [Why Action-Gated Lessons](#why-action-gated-lessons)
- [The Validation Registry Pattern](#the-validation-registry-pattern)
- [Four Validator Archetypes](#four-validator-archetypes)
- [Pacing & Content Rules](#pacing--content-rules)
- [Progression Design](#progression-design)
- [Resume-Later](#resume-later)
- [Analytics Taxonomy](#analytics-taxonomy)
- [Localization](#localization)

## Why Action-Gated Lessons

A tour with only Next buttons teaches as much as a book the user flips through without reading. If users can spam Next, they will. A real tutorial gates Next on *did the user actually do the thing*:

- "Type your name" → Next only works if the input has ≥3 chars.
- "Click Save" → Next only works if `localStorage.getItem('clicked-save') === 'true'`.
- "Create a project" → Next only works if `GET /api/projects` now returns `length > 0`.

NextStep implements this through custom card components. The card intercepts the Next click, runs a validator, and either calls `nextStep()` on success or shows an inline error on failure.

## The Validation Registry Pattern

Separate *where you check* (the card) from *what you check* (the registry). This keeps steps declarative and makes validators testable.

### 1. Define the registry

A typed map keyed by `[tourName][stepIndex]`:

```ts
// lib/validation-registry.ts
export interface ValidationStep {
  validation: () => boolean | Promise<boolean>;
  validationMessage: string;
}

export interface ValidationTour {
  [stepIndex: number]: ValidationStep;
}

export interface ValidationConfig {
  [tourName: string]: ValidationTour;
}

export const validationRegistry: ValidationConfig = {
  'create-first-project': {
    0: {
      validation: () => {
        const input = document.getElementById('project-name') as HTMLInputElement | null;
        return !!input && input.value.trim().length >= 3;
      },
      validationMessage: 'Enter a project name (at least 3 characters).',
    },
    1: {
      validation: async () => {
        const res = await fetch('/api/projects');
        const data: { projects: unknown[] } = await res.json();
        return data.projects.length > 0;
      },
      validationMessage: 'Create your first project to continue.',
    },
  },
};
```

### 2. Build a card that consults the registry

```tsx
'use client';

import { useState } from 'react';
import type { CardComponentProps } from 'nextstepjs';
import { useNextStep } from 'nextstepjs';
import { validationRegistry } from '@/lib/validation-registry';

export function ValidationCard({
  step,
  currentStep,
  totalSteps,
  nextStep,
  prevStep,
  skipTour,
  arrow,
}: CardComponentProps) {
  const { currentTour } = useNextStep();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const entry = currentTour ? validationRegistry[currentTour]?.[currentStep] : undefined;

  const handleNext = async () => {
    setError(null);
    if (!entry) {
      nextStep();
      return;
    }
    setBusy(true);
    try {
      const ok = await entry.validation();
      if (ok) {
        nextStep();
      } else {
        setError(entry.validationMessage);
      }
    } finally {
      setBusy(false);
    }
  };

  const isLast = currentStep === totalSteps - 1;
  const isFirst = currentStep === 0;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="w-[360px] rounded-xl border border-neutral-200 bg-white p-5 shadow-xl dark:border-neutral-800 dark:bg-neutral-900"
    >
      <header className="mb-3 flex items-center gap-3">
        {step.icon && <span className="text-2xl">{step.icon}</span>}
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">{step.title}</h3>
      </header>

      <div className="mb-3 text-sm text-neutral-700 dark:text-neutral-300">{step.content}</div>

      {error && (
        <div
          role="alert"
          className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {arrow}

      <footer className="mt-4 flex items-center justify-between">
        <span className="text-xs text-neutral-500 dark:text-neutral-400">
          Step {currentStep + 1} of {totalSteps}
        </span>
        <div className="flex gap-2">
          {step.showSkip && (
            <button type="button" onClick={skipTour} className="px-3 py-1.5 text-sm text-neutral-600 dark:text-neutral-400">
              Skip
            </button>
          )}
          {step.showControls && !isFirst && (
            <button type="button" onClick={prevStep} className="rounded-md border px-3 py-1.5 text-sm dark:border-neutral-700">
              Back
            </button>
          )}
          {step.showControls && (
            <button
              type="button"
              onClick={handleNext}
              disabled={busy}
              className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50 dark:bg-neutral-100 dark:text-neutral-900"
            >
              {busy ? 'Checking…' : isLast ? 'Finish' : 'Next'}
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}
```

### 3. Wire it up

```tsx
<NextStep steps={tours} cardComponent={ValidationCard}>
  {children}
</NextStep>
```

That's the whole pattern. Steps stay declarative; validators live in one file; the card handles the async dance and error display.

## Four Validator Archetypes

### 1. Input validation (sync)

```ts
validation: () => {
  const input = document.getElementById('username') as HTMLInputElement | null;
  return !!input && input.value.trim().length >= 3;
},
validationMessage: 'Enter a username with at least 3 characters.',
```

Use for form fields, textareas, file uploads. Always null-check the element — users can advance past a step whose target isn't rendered yet.

### 2. Click-tracking (sync, with cooperating component)

```ts
// in the registry
validation: () => localStorage.getItem('tutorial:save-clicked') === 'true',
validationMessage: 'Click the Save button to continue.',
```

```tsx
// in your Save button
const handleSave = async () => {
  localStorage.setItem('tutorial:save-clicked', 'true');
  await actuallySave();
};
```

Better than listening to DOM events because it survives re-renders. Clear the flag in `onComplete`/`onSkip` so replaying the tutorial works:

```tsx
<NextStep
  onComplete={() => localStorage.removeItem('tutorial:save-clicked')}
  onSkip={() => localStorage.removeItem('tutorial:save-clicked')}
  /* … */
/>
```

### 3. Async API check

```ts
validation: async () => {
  try {
    const res = await fetch('/api/projects', { cache: 'no-store' });
    const data: { projects: unknown[] } = await res.json();
    return data.projects.length > 0;
  } catch {
    return false;
  }
},
validationMessage: 'Create a project before moving on.',
```

Wrap in try/catch — a network blip should not escape the validator as an unhandled rejection. The card's `busy` state shows a "Checking…" label during the request.

### 4. Viewport / capability gate

```ts
validation: () => window.innerWidth >= 1024,
validationMessage: 'Open this lesson on a wider screen (≥1024px).',
```

Use for steps that require desktop layouts, camera permissions, `matchMedia('(prefers-reduced-motion)')`, or any environmental precondition. Cheap and synchronous.

## Pacing & Content Rules

- **One concept per step.** If you need "and" or "also" to describe the step, split it.
- **Content ≤ 20 words.** The target element is the teacher; the card is a label.
- **Use `icon` for affect, not decoration.** A `✏️` next to "Type your name" signals what to do without words.
- **Don't narrate navigation.** "Now click Next to learn about Y" is filler. The Next button is visible.
- **Avoid rhetorical questions.** "Want to see something cool?" forces a No from the user's mental model.
- **Use imperative verbs.** "Click Save" not "You can click Save here".

## Progression Design

**Linear vs branching**: NextStep tours are linear. For branching lessons (novice vs expert paths), define **two separate `Tour` objects** and pick one at start time:

```tsx
const { startNextStep } = useNextStep();
const tourName = user.hasUsedBefore ? 'expert-path' : 'novice-path';
useEffect(() => { startNextStep(tourName); }, [tourName, startNextStep]);
```

**Resume vs restart**: if a user skips mid-tour, don't auto-restart on next login. Use `onSkip` to set a "skipped" flag and offer a `<ResumeLessonButton />` instead of auto-triggering.

**Completion gates**: use `onComplete` to unlock features, award badges, or dismiss the tutorial permanently. Never rely on local state alone — persist to your backend.

## Resume-Later

Pair `onStepChange` (to save progress) with `setCurrentStep(index, delay)` (to jump back) on mount:

```tsx
'use client';
import { useEffect } from 'react';
import { NextStep, NextStepProvider, useNextStep } from 'nextstepjs';

function Resumer({ tourName }: { tourName: string }) {
  const { startNextStep, setCurrentStep } = useNextStep();
  useEffect(() => {
    const saved = localStorage.getItem(`lesson:${tourName}:step`);
    if (saved !== null) {
      startNextStep(tourName);
      setCurrentStep(Number(saved), 400); // delay lets the DOM settle
    }
  }, [tourName, startNextStep, setCurrentStep]);
  return null;
}

export function LessonShell({ children, tourName }: { children: React.ReactNode; tourName: string }) {
  return (
    <NextStepProvider>
      <NextStep
        steps={tours}
        onStepChange={(step, name) => {
          if (name) localStorage.setItem(`lesson:${name}:step`, String(step));
        }}
        onComplete={(name) => {
          if (name) localStorage.removeItem(`lesson:${name}:step`);
        }}
      >
        <Resumer tourName={tourName} />
        {children}
      </NextStep>
    </NextStepProvider>
  );
}
```

The `400`ms delay on `setCurrentStep` matters — on first mount the DOM may still be hydrating, and jumping to a step whose selector isn't yet in the tree will fail silently.

## Analytics Taxonomy

Recommended event names and payloads:

| Event | When | Payload |
|-------|------|---------|
| `tour_started` | `onStart` | `{ tourName }` |
| `tour_step_viewed` | `onStepChange` | `{ tourName, step }` |
| `tour_step_failed_validation` | inside the validation card, on `entry.validation()` returning false | `{ tourName, step, validationMessage }` |
| `tour_skipped` | `onSkip` | `{ tourName, step }` |
| `tour_completed` | `onComplete` | `{ tourName }` |

Track `tour_step_failed_validation` with the step index — it's the single most valuable signal for improving a tutorial. Any step with a high fail count is either poorly worded, has a broken validator, or is genuinely a bad user experience.

## Localization

NextStep has no built-in i18n. Generate `tours` inside a hook that reads your translation context:

```tsx
'use client';
import { useTranslation } from 'react-i18next';
import type { Tour } from 'nextstepjs';

export function useLocalizedTours(): Tour[] {
  const { t } = useTranslation('tours');
  return [
    {
      tour: 'welcome',
      steps: [
        {
          icon: '👋',
          title: t('welcome.step1.title'),
          content: t('welcome.step1.content'),
          selector: '#welcome-banner',
          side: 'bottom',
          showControls: true,
          showSkip: true,
        },
        {
          icon: '🎉',
          title: t('welcome.step2.title'),
          content: t('welcome.step2.content'),
          selector: '#main-nav',
          side: 'right',
          showControls: true,
          showSkip: true,
        },
      ],
    },
  ];
}

// Then in your shell component:
function Shell({ children }: { children: React.ReactNode }) {
  const tours = useLocalizedTours();
  return (
    <NextStepProvider>
      <NextStep steps={tours}>{children}</NextStep>
    </NextStepProvider>
  );
}
```

When the locale changes, the hook re-runs, new step content flows into `NextStep`, and the active step's card re-renders with the new translations. Validators live outside the localized steps, so they don't need to change.
