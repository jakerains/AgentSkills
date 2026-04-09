# UI Component Guide

Templates and guidance for changelog UI components in React/Next.js projects.

## Table of Contents
- [Component Overview](#component-overview)
- [Changelog Modal](#changelog-modal)
- [Version Trigger](#version-trigger)
- [Changelog Page](#changelog-page)
- [Adapting to Existing Projects](#adapting-to-existing-projects)
- [Content Rendering](#content-rendering)

---

## Component Overview

The changelog UI consists of three optional pieces:

| Component | Purpose | Required? |
|-----------|---------|-----------|
| Changelog Modal | Dialog showing changelog entries | Recommended |
| Version Trigger | `vX.Y.Z` badge that opens the modal | Recommended |
| Changelog Page | Full `/changelog` route | Optional |

Asset templates are in `assets/`. Adapt them to match the project's conventions.

---

## Changelog Modal

See [assets/changelog-modal.tsx](../assets/changelog-modal.tsx) for the full template.

**Key behaviors:**
- Opens via trigger click or programmatic open
- Scrollable list of all changelog entries
- Each entry shows version, date, and content
- Latest version highlighted or shown first
- Responsive (works on mobile)
- Accessible (focus trap, escape to close)

**Adaptation points:**
- **Dialog primitive**: Use the project's existing dialog (shadcn Dialog, Radix, MUI Modal, Headless UI Dialog, native `<dialog>`)
- **Styling**: Match the project's styling system (Tailwind, CSS modules, styled-components)
- **Content rendering**: Depends on data format (see Content Rendering below)

---

## Version Trigger

See [assets/changelog-trigger.tsx](../assets/changelog-trigger.tsx) for the full template.

**Key behaviors:**
- Shows current version: `vX.Y.Z`
- Subtle styling — should not dominate the UI
- On click: opens changelog modal OR navigates to changelog page
- Tooltip on hover: "View changelog" or similar

**Placement options:**
- Sidebar footer (most common for apps)
- Page footer (for content sites)
- Settings page (for apps with settings)
- Header area (less common)

---

## Changelog Page

For Next.js App Router, create a simple page:

```tsx
// app/changelog/page.tsx (or app/(main)/changelog/page.tsx)
export const metadata = {
  title: "Changelog | AppName",
  description: "See what's new.",
}

export default function ChangelogPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-2xl px-4 py-12">
        <h1 className="text-3xl font-bold mb-8">Changelog</h1>
        {/* Render changelog entries inline (not in a modal) */}
      </div>
    </div>
  )
}
```

This is optional. Many projects use modal-only. Ask the user which they prefer.

---

## Adapting to Existing Projects

When a project already has changelog UI components:

1. **Do NOT recreate them.** Use what exists.
2. **Identify the data source** the existing components import from.
3. **Update the data source** in the update workflow.
4. If the existing components need changes (e.g., to support a new field), modify them minimally.

Common existing patterns:
- LemonNotes style: `changelogReleases` array in `lib/changelog-data.tsx` with JSX content
- JSON-driven: `changelog.json` parsed in a component
- CMS-driven: API endpoint returning changelog entries (skill updates the source data, not the API)

---

## Content Rendering

How to render the `content` field depends on its format in the data file:

### JSX content (ReactNode)
Direct render — no processing needed:
```tsx
<div>{entry.content}</div>
```

### Markdown string
Use a markdown renderer like `react-markdown`:
```tsx
import ReactMarkdown from "react-markdown"

<div className="prose dark:prose-invert prose-sm">
  <ReactMarkdown>{entry.content}</ReactMarkdown>
</div>
```

Or use the project's existing markdown renderer if one is installed.

### HTML string
Use a sanitization library like DOMPurify to safely render HTML content:
```tsx
import DOMPurify from "dompurify"

<div
  className="prose dark:prose-invert prose-sm"
  // Sanitize with DOMPurify before rendering
/>
```

Always sanitize HTML content before rendering, even for trusted sources like changelog entries.
