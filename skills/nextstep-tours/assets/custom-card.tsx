// Paste-ready custom card for NextStep tours.
// Tailwind CSS + dark mode, accessible, exercises every CardComponentProps field.
//
// Usage:
//   import { NextStep, NextStepProvider } from 'nextstepjs';
//   import { CustomCard } from '@/components/custom-card';
//   <NextStep steps={tours} cardComponent={CustomCard}>{children}</NextStep>
//
// Notes:
// - `'use client'` is required — NextStep cards mount in the browser.
// - `{arrow}` must be rendered inside the card so the pointer anchors correctly.
// - `step.showControls` and `step.showSkip` are NOT honored by the default card code path
//   when you provide a custom card — you must read them yourself, as done below.

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
        {step.icon && <span className="text-2xl" aria-hidden="true">{step.icon}</span>}
        <h3
          id="nextstep-card-title"
          className="text-lg font-semibold text-neutral-900 dark:text-neutral-100"
        >
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
              autoFocus
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
