import type { Tour } from 'nextstepjs';

/**
 * Representative multi-tour definition.
 *
 * - `welcome`    — 3-step onboarding tour, unanchored intro + anchored stops.
 * - `features`   — 2-step cross-page tour demonstrating `nextRoute`.
 * - `first-project-lesson` — 3-step gated lesson; pair with `validation-card.tsx` + `validation-registry.ts`.
 *
 * Copy this file to your app (e.g. `lib/tours.ts`), then adjust selectors (`#...`) to match real element ids.
 * Every step's selector must resolve to an element that is actually rendered at the moment the step shows.
 */
export const tours: Tour[] = [
  {
    tour: 'welcome',
    steps: [
      {
        icon: '👋',
        title: 'Welcome aboard',
        content: "This 60-second tour shows you the essentials.",
        showControls: true,
        showSkip: true,
      },
      {
        icon: '🧭',
        title: 'Your navigation',
        content: 'Everything lives behind this sidebar.',
        selector: '#main-nav',
        side: 'right',
        showControls: true,
        showSkip: true,
        pointerPadding: 10,
        pointerRadius: 8,
      },
      {
        icon: '🎉',
        title: "You're set",
        content: 'Explore freely. You can restart the tour from the help menu.',
        showControls: true,
      },
    ],
  },

  {
    tour: 'features',
    steps: [
      {
        icon: '📊',
        title: 'Dashboard metrics',
        content: 'This summary updates in real time.',
        selector: '#dashboard-summary',
        side: 'bottom',
        showControls: true,
        showSkip: true,
        pointerPadding: 10,
        pointerRadius: 8,
        nextRoute: '/settings',
      },
      {
        icon: '⚙️',
        title: 'Fine-tune here',
        content: 'Every preference lives on this page.',
        selector: '#settings-header',
        side: 'bottom',
        showControls: true,
        showSkip: true,
        prevRoute: '/',
      },
    ],
  },

  {
    tour: 'first-project-lesson',
    steps: [
      {
        icon: '✏️',
        title: 'Name your project',
        content: 'Type a project name (at least 3 characters).',
        selector: '#project-name',
        side: 'bottom',
        showControls: true,
        showSkip: true,
        blockKeyboardControl: true,
      },
      {
        icon: '💾',
        title: 'Save it',
        content: 'Click Save to create your first project.',
        selector: '#save-project-button',
        side: 'top',
        showControls: true,
        showSkip: true,
      },
      {
        icon: '🚀',
        title: 'Nice work',
        content: 'Your project is live. Explore it on the dashboard.',
        selector: '#project-list',
        side: 'left',
        showControls: true,
        showSkip: true,
      },
    ],
  },
];

export default tours;
