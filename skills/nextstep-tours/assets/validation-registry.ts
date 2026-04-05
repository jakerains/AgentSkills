// Validation registry for NextStep action-gated tutorials.
//
// The registry separates "what to check" (validators) from "where to check" (the card).
// It is keyed by [tourName][stepIndex] so a single card can handle any tour.
//
// Drop this file at `lib/validation-registry.ts`, then import it from your custom card
// (see `validation-card.tsx`) and pair with a tours file that references these step indexes.

export interface ValidationStep {
  /** Sync or async predicate. Resolve to true to allow Next; false to show the message. */
  validation: () => boolean | Promise<boolean>;
  /** Shown in the card when validation fails. Keep to one sentence. */
  validationMessage: string;
}

export interface ValidationTour {
  [stepIndex: number]: ValidationStep;
}

export interface ValidationConfig {
  [tourName: string]: ValidationTour;
}

/**
 * Three validator archetypes covering the common cases:
 *
 *   step 0 — DOM input check (sync)
 *   step 1 — async API check
 *   step 2 — viewport / capability gate (sync)
 *
 * For click-tracking, see the alternate example at the bottom of this file.
 */
export const validationRegistry: ValidationConfig = {
  'first-project-lesson': {
    // Step 0: user must type a project name (≥ 3 chars)
    0: {
      validation: () => {
        const input = document.getElementById('project-name') as HTMLInputElement | null;
        return !!input && input.value.trim().length >= 3;
      },
      validationMessage: 'Enter a project name (at least 3 characters).',
    },

    // Step 1: user must create a project — verify via the API
    1: {
      validation: async () => {
        try {
          const res = await fetch('/api/projects', { cache: 'no-store' });
          if (!res.ok) return false;
          const data: { projects: unknown[] } = await res.json();
          return Array.isArray(data.projects) && data.projects.length > 0;
        } catch {
          return false;
        }
      },
      validationMessage: 'Create your first project to continue.',
    },

    // Step 2: viewport gate — wider screens only for the final review step
    2: {
      validation: () => window.innerWidth >= 1024,
      validationMessage: 'Open this lesson on a wider screen (≥1024px).',
    },
  },
};

export default validationRegistry;

// ─────────────────────────────────────────────────────────────────────────────
// Click-tracking validator (bonus archetype)
//
// In the Save button's handler, set a localStorage flag:
//
//   const handleSave = async () => {
//     localStorage.setItem('tutorial:save-clicked', 'true');
//     await actuallySave();
//   };
//
// Then in the registry:
//
//   1: {
//     validation: () => localStorage.getItem('tutorial:save-clicked') === 'true',
//     validationMessage: 'Click the Save button to continue.',
//   },
//
// Clear the flag on tour completion or skip to allow re-running:
//
//   <NextStep
//     onComplete={() => localStorage.removeItem('tutorial:save-clicked')}
//     onSkip={() => localStorage.removeItem('tutorial:save-clicked')}
//     …
//   />
// ─────────────────────────────────────────────────────────────────────────────
