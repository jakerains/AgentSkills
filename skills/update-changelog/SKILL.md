---
name: update-changelog
description: "Automate changelog management, version bumping, and release tracking. Sets up a changelog system (CHANGELOG.md, UI modal, version display) if none exists, or updates an existing one. Use when: updating changelog, bumping version, creating release entry, setting up changelog, adding version display, managing semver, commit and push workflow. Triggers on: changelog, version bump, release notes, semver, CHANGELOG.md, release entry, what's new, patch/minor/major bump, commit and push, update the changelog, release, new version."
---

# Version Changelog

Dual-mode skill for changelog lifecycle management. Detects existing systems and adapts.

## Quick Reference

| Task | Mode | Details |
|------|------|---------|
| First-time setup | Setup | Read [setup-workflow.md](references/setup-workflow.md) |
| Update existing changelog | Update | Inline below (the hot path) |
| CHANGELOG.md format | Reference | Read [changelog-format-spec.md](references/changelog-format-spec.md) |
| UI components | Reference | Read [ui-component-guide.md](references/ui-component-guide.md) |
| Detection algorithm | Reference | Read [detection-logic.md](references/detection-logic.md) |
| Parse CHANGELOG.md → JSON | Script | Run [parse-changelog.sh](scripts/parse-changelog.sh) |

---

## Detection Phase

Run these checks BEFORE choosing a mode. All are read-only.

### 1. Version source

Check in order, use the first match:
- `package.json` → read `"version"` field (Node/JS projects)
- `pyproject.toml` → read `version` under `[project]` or `[tool.poetry]`
- `Cargo.toml` → read `version` under `[package]`
- `VERSION` file at project root (plain text)
- If none found: will create during setup

### 2. Changelog files

Check for existing changelog data:
- `CHANGELOG.md` at project root
- `docs/CHANGELOG.md`
- `lib/changelog-data.tsx` or `lib/changelog-data.ts`
- `lib/changelog-data.json` or `changelog.json`
- Any file matching glob `**/changelog-data.*`

### 3. Framework detection (for UI setup)

- `next.config.*` or `package.json` containing `"next"` → Next.js
- `package.json` containing `"react"` → React (non-Next)
- `package.json` containing `"vue"` or `nuxt.config.*` → Vue/Nuxt
- `package.json` containing `"svelte"` → SvelteKit
- None of the above → CLI/backend project (skip UI components)

### 4. Existing UI components

- Grep for `changelog` in `components/`, `src/components/`, `app/`
- Check for version display patterns: grep for `getCurrentVersion`, `packageJson.version`, `APP_VERSION`

### Mode Selection

```
IF no CHANGELOG.md found AND no structured data file found:
  → SETUP MODE (read references/setup-workflow.md)
ELSE:
  → UPDATE MODE (continue below)
```

---

## Setup Mode (Summary)

Read [references/setup-workflow.md](references/setup-workflow.md) for the complete setup workflow.

**High-level steps:**

1. **Create `CHANGELOG.md`** at project root using [Keep a Changelog](https://keepachangelog.com) format. Populate with initial entry using detected version (or `1.0.0`).
2. **Create structured data file** (web projects only): `lib/changelog-data.ts` with typed entries. Use the template from [assets/changelog-data-template.ts](assets/changelog-data-template.ts).
3. **Create UI components** (React/Next.js only):
   - Changelog modal — adapt [assets/changelog-modal.tsx](assets/changelog-modal.tsx)
   - Version trigger — adapt [assets/changelog-trigger.tsx](assets/changelog-trigger.tsx)
   - Changelog page route (optional)
4. **Wire version helper**: `getCurrentVersion()` reads from `package.json`.
5. **Ask user** where to place the version trigger (footer, sidebar, header, settings).
6. **Commit**: `chore: set up changelog system (vX.Y.Z)` — stage only the new files.

After setup, immediately offer to run Update Mode if there are existing changes to document.

---

## Update Mode

This is the primary workflow. Follow every step in order.

### Step 1: Read current state

```bash
# Current version
cat package.json | jq -r '.version'

# Recent commits (adjust depth as needed)
git log --oneline -20

# What's changed since last entry
git diff --stat
git status
```

Read the existing changelog file(s) to find the **last documented version** and its **date**.

If a structured data file exists (e.g., `lib/changelog-data.tsx`), read it to understand the entry format:
- Does it use JSX/ReactNode for `content`? (e.g., `<div className="prose">...</div>`)
- Does it use markdown strings for `content`?
- Does it use a different structure entirely?

**Store the detected format.** New entries MUST match the existing format exactly.

### Step 2: Assess scope

Analyze ALL changes since the last changelog entry. This includes:
- Commits since the last entry's date
- Any uncommitted/staged changes in the working tree
- Files changed, features added, bugs fixed

Categorize:
- **Patch** (x.x.**+1**): bug fixes, dependency updates, small tweaks, typos, style changes, config adjustments
- **Minor** (x.**+1**.0): new features, new API endpoints, new UI components, meaningful new functionality, new integrations
- **Major** (**+1**.0.0): breaking changes, API redesigns, major rewrites (rare — user usually specifies)

### Step 3: Determine new version

Calculate the new version number based on the scope assessment.

Present your recommendation with rationale:
```
Current version: 1.15.7
Recommended bump: patch → 1.15.8
Reason: Bug fixes and small UI tweaks, no new features
```

The user may override your recommendation. Accept their choice.

### Step 4: Draft the changelog entry

Draft entries for ALL detected changelog targets:

**A. CHANGELOG.md entry** (always):

```markdown
## [X.Y.Z] - Month DD, YYYY

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description
```

Use only the categories that apply: Added, Changed, Deprecated, Removed, Fixed, Security.

**B. Structured data file entry** (if one exists):

Match the EXACT format of existing entries. Examples:

For TSX with JSX content (like LemonNotes `lib/changelog-data.tsx`):
```tsx
{
  version: "X.Y.Z",
  title: "vX.Y.Z: Brief Title",
  date: "Month DD, YYYY",
  excerpt: "One-sentence summary.",
  content: (
    <div className="prose dark:prose-invert prose-sm">
      <h3>Section</h3>
      <ul>
        <li>Change description</li>
      </ul>
    </div>
  ),
},
```

For TS with markdown strings:
```ts
{
  version: "X.Y.Z",
  title: "vX.Y.Z: Brief Title",
  date: "Month DD, YYYY",
  excerpt: "One-sentence summary.",
  content: "### Added\n- Feature description\n\n### Fixed\n- Bug fix",
},
```

### Step 5: Present for approval

**CRITICAL: This is a hard stop. Do NOT proceed without explicit user approval.**

Show the user:
1. **Version bump**: `current → proposed` (with bump type)
2. **CHANGELOG.md entry**: full formatted text
3. **Structured data entry**: full formatted entry (if applicable)
4. **Files to be modified**: list every file that will change

Ask: "Does this look good? Any changes?"

Wait for the user to explicitly approve (e.g., "looks good", "approved", "go", "yes", "do it").

If the user requests changes, revise and present again. Loop until approved.

### Step 6: Write changes

After approval, execute ALL writes:

**A. Bump version in version source file:**
- `package.json`: update the `"version"` field
- Other files: update the version string in the appropriate location

**B. Prepend to CHANGELOG.md:**
- Add the new entry immediately after the `# Changelog` header (or after any intro text)
- Keep the `[Unreleased]` section if one exists (just add the new version below it)
- Preserve all existing entries unchanged

**C. Update structured data file (if exists):**
- Add the new entry to the TOP of the releases array
- Match exact formatting and indentation of existing entries
- Do not modify any existing entries

### Step 7: Commit

```bash
# Stage only the modified files — be explicit
git add package.json CHANGELOG.md <structured-data-file-if-exists> <any-other-changed-source-files>

# Commit with version in message
git commit -m "release: vX.Y.Z — <brief title describing the changes>"
```

Include any source code files that were part of the changes being documented (i.e., if this is a "commit and push" workflow where you also wrote code, stage those files too).

### Step 8: Done

Report what was written:
- Version bumped: `old → new`
- Files modified: list
- Commit hash: show it

**STOP HERE. Do not push. Do not ask to push. Do not suggest pushing. The workflow is complete.**

---

## Execution Rules

These rules are non-negotiable. Follow them exactly.

### Never push
- Do NOT run `git push`
- Do NOT ask "should I push?"
- Do NOT suggest pushing
- Do NOT mention pushing
- The workflow ends at the commit

### Date accuracy
- ALWAYS verify the actual current date before writing entries
- NEVER copy dates from previous entries
- NEVER assume the year — check it
- Format: `Month DD, YYYY` (e.g., `April 9, 2026`)

### Format fidelity
- When updating an existing structured data file, match the EXACT format of existing entries
- Same indentation, same quote style, same field order, same content structure
- If existing entries use JSX with `className="prose dark:prose-invert prose-sm"`, use that exact pattern
- If existing entries use markdown strings, use markdown strings
- Read at least 2 existing entries to confirm the pattern before drafting

### Commit message format
- Pattern: `release: vX.Y.Z — <brief description>`
- The description should summarize the most notable change(s)
- Examples:
  - `release: v1.15.8 — fix audio upload timeout & improve error messages`
  - `release: v1.16.0 — add project grouping & bulk actions`
  - `release: v2.0.0 — redesign API with breaking schema changes`

### Version in structured data must match package.json
- After bumping, verify the version string is identical in ALL locations
- `package.json`, `CHANGELOG.md`, and the structured data file must all agree

### Dual-write guarantee
- If BOTH `CHANGELOG.md` and a structured data file exist, BOTH must be updated
- Never update one without the other
- If only `CHANGELOG.md` exists, that's fine — just update it

---

## Handling Edge Cases

### "Commit and push" user intent
When a user says "commit and push" in a project with this skill installed, treat it as an Update Mode trigger. The "push" part is ignored — this skill NEVER pushes.

### No changes to document
If `git log` shows no commits since the last changelog entry and there are no uncommitted changes, inform the user: "No changes found since the last changelog entry (vX.Y.Z on Date). Nothing to update."

### Version mismatch
If `package.json` version differs from the latest CHANGELOG.md version, flag it:
"package.json is at vX.Y.Z but the latest changelog entry is vA.B.C. Which should I use as the base?"

### Multiple structured data files
If both a `.tsx` and `.json` changelog data file exist, update both. Ask the user which is canonical if unclear.

### Non-JS projects
For Python, Rust, Go, or other projects without `package.json`:
- Bump version in the appropriate file (`pyproject.toml`, `Cargo.toml`, `VERSION`)
- Skip structured data file and UI component steps
- CHANGELOG.md is the only changelog target
