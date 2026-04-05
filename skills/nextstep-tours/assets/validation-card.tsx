// Validation-gated card for NextStep interactive tutorials.
//
// Variant of `custom-card.tsx` that consults a validation registry before advancing.
// If the registry has no entry for the current step, it behaves like a normal card.
// If the entry's validator resolves to false, the card displays the error message
// and does NOT call nextStep(). The user must fix the condition and click Next again.
//
// Usage:
//   import { NextStep, NextStepProvider } from 'nextstepjs';
//   import { ValidationCard } from '@/components/validation-card';
//   <NextStep steps={tours} cardComponent={ValidationCard}>{children}</NextStep>
//
// Pair with `validation-registry.ts` — edit that file to change validation rules,
// not this one.

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
    } catch {
      setError(entry.validationMessage);
    } finally {
      setBusy(false);
    }
  };

  // Clear stale errors whenever the user goes back
  const handlePrev = () => {
    setError(null);
    prevStep();
  };

  const isFirst = currentStep === 0;
  const isLast = currentStep === totalSteps - 1;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="nextstep-card-title"
      className="w-[380px] rounded-xl border border-neutral-200 bg-white p-5 shadow-xl dark:border-neutral-800 dark:bg-neutral-900"
    >
      <header className="mb-3 flex items-center gap-3">
        {step.icon && <span className="text-2xl" aria-hidden="true">{step.icon}</span>}
        <h3
          id="nextstep-card-title"
          className="text-lg font-semibold text-neutral-900 dark:text-neutral-100"
        >
          {step.title}
        </h3>
      </header>

      <div className="mb-3 text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
        {step.content}
      </div>

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
              onClick={handlePrev}
              className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-200 dark:hover:bg-neutral-800"
            >
              Back
            </button>
          )}

          {step.showControls && (
            <button
              type="button"
              onClick={handleNext}
              disabled={busy}
              className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-neutral-100 dark:text-neutral-900 dark:hover:bg-neutral-200"
            >
              {busy ? 'Checking…' : isLast ? 'Finish' : 'Next'}
            </button>
          )}
        </div>
      </footer>
    </div>
  );
}
