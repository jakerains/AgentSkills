# Setup Workflow

Complete first-time setup for a changelog system. Run this when Detection Phase finds no existing CHANGELOG.md and no structured data file.

## Table of Contents
- [Phase A: Create CHANGELOG.md](#phase-a-create-changelogmd)
- [Phase B: Create Structured Data File](#phase-b-create-structured-data-file)
- [Phase C: Create UI Components](#phase-c-create-ui-components)
- [Phase D: Wire Version Helper](#phase-d-wire-version-helper)
- [Phase E: Place Version Trigger](#phase-e-place-version-trigger)
- [Phase F: Initial Commit](#phase-f-initial-commit)

---

## Phase A: Create CHANGELOG.md

Create `CHANGELOG.md` at the project root.

Use the [Keep a Changelog](https://keepachangelog.com) format. See [changelog-format-spec.md](changelog-format-spec.md) for the full specification.

**Template:**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [X.Y.Z] - Month DD, YYYY

### Added
- Initial changelog setup
- (list existing features worth noting)
```

Replace `X.Y.Z` with the version detected from `package.json` (or `1.0.0` if no version source exists).

For projects with existing history, optionally backfill a few key releases from `git log --oneline` or `git tag`. Keep it brief — 3-5 entries max.

---

## Phase B: Create Structured Data File

**Skip this phase for non-web projects (no UI framework detected).**

Create a TypeScript data file the UI can import.

### For new projects (no existing changelog data)

Use the template from [assets/changelog-data-template.ts](../assets/changelog-data-template.ts).

Place at `lib/changelog-data.ts` (or `src/lib/changelog-data.ts` if the project uses `src/`).

Key design: use **markdown strings** for the `content` field (not JSX). This keeps the file writable without JSX compilation and works with any markdown renderer.

### For projects that already have a structured data file

Do NOT create a new one. The existing file IS the structured data target. Just ensure CHANGELOG.md is also created (Phase A).

---

## Phase C: Create UI Components

**Skip this phase for non-web projects.**

Create two components, adapting the templates from `assets/`:

### 1. Changelog Modal

Adapt [assets/changelog-modal.tsx](../assets/changelog-modal.tsx).

**Placement:** `components/changelog-modal.tsx` (or matching project convention for component location).

**Dependencies to check/install:**
- If project uses shadcn/ui: use Dialog from `@/components/ui/dialog`
- If project uses another UI library: adapt to that library's dialog/modal
- If no UI library: create a simple modal with native HTML `<dialog>` or a div overlay

**Content rendering:**
- If data file uses markdown strings: install/use `react-markdown` or project's existing markdown renderer
- If data file uses JSX content: render directly

### 2. Version Trigger

Adapt [assets/changelog-trigger.tsx](../assets/changelog-trigger.tsx).

**Placement:** `components/changelog-trigger.tsx` (or matching project convention).

**Behavior:**
- Displays `vX.Y.Z` using `getCurrentVersion()`
- Clicking opens the changelog modal (or navigates to `/changelog` if a page route exists)
- Styled subtly — small text, muted color, hover effect

### 3. Changelog Page Route (Optional)

If the project uses App Router (Next.js), offer to create a dedicated page:

```
app/(main)/changelog/page.tsx   — or —
app/changelog/page.tsx
```

This is optional. Some projects prefer modal-only. Ask the user.

---

## Phase D: Wire Version Helper

Check if a version helper already exists (grep for `getCurrentVersion` or similar).

If not, add one to the structured data file:

```typescript
import packageJson from "@/package.json"  // or relative path

export function getCurrentVersion(): string {
  return packageJson.version
}
```

For projects importing `package.json` in TypeScript, ensure `tsconfig.json` has `resolveJsonModule: true` (it usually does).

---

## Phase E: Place Version Trigger

Ask the user where they want the version badge displayed. Common locations:

1. **App sidebar footer** — most common for dashboard-style apps
2. **Page footer** — for marketing/content sites
3. **Settings page** — for apps with a settings area
4. **Header/navbar** — less common but valid

Import and render the `ChangelogTrigger` component in the chosen location.

If unsure, recommend the sidebar footer for apps with sidebars, or the page footer otherwise.

---

## Phase F: Initial Commit

Stage only the newly created files:

```bash
git add CHANGELOG.md lib/changelog-data.ts components/changelog-modal.tsx components/changelog-trigger.tsx
# Add any other files created (page route, etc.)

git commit -m "chore: set up changelog system (vX.Y.Z)"
```

Adjust file paths to match what was actually created.

**Do NOT push. Do NOT ask to push.**

After committing, inform the user: "Changelog system is set up. Run the skill again anytime to add new entries."
