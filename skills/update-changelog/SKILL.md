---
name: update-changelog
description: "Automate changelog management, version bumping, release entries, and explicit prerelease/tag/publish workflows. Sets up a changelog system (CHANGELOG.md, UI modal, version display) if none exists, or updates an existing one. Use when: updating changelog, bumping version, creating release entry, promoting [Unreleased], handling alpha/beta/rc prerelease versions, setting up changelog, adding version display, managing semver. Use tag/GitHub Release instructions only when the user explicitly asks to tag, publish, or create a GitHub Release. Triggers on: changelog, version bump, release notes, semver, CHANGELOG.md, release entry, what's new, patch/minor/major/prerelease bump, alpha, beta, rc, tag release, GitHub Release, update the changelog, release, new version."
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
| Explicit tags and GitHub Releases | Publish | Available only when the user asks to tag/publish |

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

# Branch context
git branch --show-current
```

Read the existing changelog file(s) to find the **last documented version** and its **date**.

If a structured data file exists (e.g., `lib/changelog-data.tsx`), read it to understand the entry format:
- Does it use JSX/ReactNode for `content`? (e.g., `<div className="prose">...</div>`)
- Does it use markdown strings for `content`?
- Does it use a different structure entirely?

**Store the detected format.** New entries MUST match the existing format exactly.

Check branch workflow context before drafting:
- **Branch**: Keep ordinary changelog/version bumps on the branch that contains the code being documented. If the user explicitly asks for an official stable release, recommend `main`. If the intent is unclear and writing on the current branch could be surprising, ask before writing.
- **Deploy coupling**: Only when the user asks for an official stable release, look for `.github/workflows/`, `vercel.json`, `netlify.toml`, `fly.toml`, `render.yaml`, `railway.json`, or package scripts that imply deploy on `main`. If `main` auto-deploys, warn during approval: "Committing this release on main may ship vX.Y.Z to production."

Do not inspect, mention, offer, or prepare git tags, pushed tags, or GitHub Releases unless the user explicitly asks to tag, publish, create a GitHub Release, or work on a prerelease track.

If the user explicitly asks for a prerelease track, inspect existing tags only to find the next alpha/beta/rc number:

```bash
git tag --list --sort=-v:refname | head -40
```

If the user explicitly asks to tag, push tags, publish, or create a GitHub Release, run the publish checks:

```bash
git tag --list --sort=-v:refname | head -40
git remote -v
command -v gh >/dev/null && gh auth status
```

For explicit publish/tag requests, detect tag style with `git tag --list`: use `vX.Y.Z` if existing tags use a `v` prefix, `X.Y.Z` if they do not, and ask/recommend `vX.Y.Z` if there are no tags.

### Step 2: Assess scope

Analyze ALL changes since the last changelog entry. This includes:
- Commits since the last entry's date
- Any uncommitted/staged changes in the working tree
- Any populated `[Unreleased]` section
- Files changed, features added, bugs fixed

Categorize. **Default to patch.** Only escalate to minor when there is clearly a new, user-facing capability worth announcing. When torn between patch and minor, choose patch.

- **Patch** (x.x.**+1**) — the default, and most releases land here. Use for:
  - Bug fixes, typo fixes, copy tweaks
  - Dependency updates, config adjustments, build tooling changes
  - Refactors, cleanup, internal code changes with no user-visible behavior change
  - Small UI tweaks, style/layout polish, accessibility fixes
  - Performance improvements that don't change behavior
  - New internal helpers, small extensions of existing features
  - Docs, tests, CI changes
- **Minor** (x.**+1**.0) — reserved for genuinely notable new capability. Requires ALL of:
  - A new user-facing feature, page, workflow, integration, or public API surface
  - Something a user would reasonably see in release notes and say "oh, that's new"
  - Not just an extension or polish of an existing feature
  - Examples that qualify: a brand-new page/route, a new integration with a third-party service, a new public API endpoint, a new major UI surface (modal/panel/tool) that didn't exist before
  - Examples that do NOT qualify (these are patches): adding a button to an existing page, new config option, new CLI flag, new variant of an existing component, extending an existing feature, small new helper function
- **Major** (**+1**.0.0) — breaking changes, API redesigns, major rewrites. Rare. Never pick this without explicit user direction.

**Tiebreaker:** If the change feels "meh, it's just more of what we already do" → patch. If you find yourself justifying why it's minor → it's probably patch.

### Step 3: Determine new version

Calculate the new version number based on the scope assessment. **Remember: patch is the default. Only pick minor if the Step 2 criteria for minor are clearly met.**

Pre-release handling:
- Stable releases are the default. Do not create `-alpha`, `-beta`, or `-rc` versions unless the user asks or the current version is already a pre-release.
- For feature branches, use prerelease versions when the user wants to version a track before merging to `main` without bumping the official stable line.
- If current version is stable and the user asks for an alpha/beta/rc track, choose the next base version from the normal patch/minor/major assessment, then append the requested label and `.1`. Example: `1.4.2` + patch beta track → `1.4.3-beta.1`; `1.4.2` + minor beta track → `1.5.0-beta.1`.
- If a matching prerelease already exists for the same base and label, increment the numeric suffix: `1.5.0-beta.1` → `1.5.0-beta.2`.
- If switching labels on the same base, start the new label at `.1` unless matching tags or changelog entries show a higher number: `1.5.0-alpha.3` → `1.5.0-beta.1`.
- If current version is `1.2.0-rc.1` and the user says it is ready for the official release, recommend finalizing to `1.2.0`.
- For `0.x` projects, still use semver shape: patch for fixes, minor for new user-facing capability, major only by explicit direction.

Present your recommendation with rationale. If you picked minor, explicitly justify which Step 2 minor-criterion the change meets — if you can't point to one cleanly, downgrade to patch before presenting.

```
Current version: 1.15.7
Recommended bump: patch → 1.15.8
Reason: Bug fixes and small UI tweaks, no new user-facing capability
```

Or, for a minor bump:
```
Current version: 1.15.7
Recommended bump: minor → 1.16.0
Reason: Adds new /reports page (new user-facing surface) — qualifies as minor under Step 2 criteria
```

Or, for an explicit feature-branch beta track:
```
Current version: 1.15.7
Recommended bump: patch prerelease → 1.15.8-beta.1
Reason: User requested a beta track on the feature branch before merging to main; base bump is patch because the changes extend existing behavior
```

The user may override your recommendation. Accept their choice.

### Step 4: Draft the changelog entry

Draft entries for ALL detected changelog targets:

**A. CHANGELOG.md entry** (always):

```markdown
## [X.Y.Z] - Month DD, YYYY

### Added
- Add new feature description

### Changed
- Update changed behavior description

### Fixed
- Fix bug description
```

Use only the categories that apply: Added, Changed, Deprecated, Removed, Fixed, Security.

If `CHANGELOG.md` has populated `[Unreleased]` items, promote relevant items into the new version entry and leave a fresh empty `## [Unreleased]` above it.

Add traceability only when it helps:
- Prefer issue/PR refs when available: `Fix login redirect (#142)`.
- Use short commit refs only for hard-to-trace changes or when no PR/issue exists: `Fix migration ordering (a1b2c3d)`.
- Do not clutter every line with hashes if the release commit already groups the work clearly.

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
5. **Branch/deploy context**: branch note and any main auto-deploy warning, only when relevant
6. **Publish context**: only if the user explicitly asked for tags, pushed tags, or GitHub Releases

Use this friendly approval shape:

```markdown
I found changes since vX.Y.Z and recommend a patch bump to vX.Y.Z.

Branch context:
- Branch: feature/example

Proposed changelog:

## [X.Y.Z] - Month DD, YYYY

### Fixed
- Fix ...

Files I will modify:
- package.json
- CHANGELOG.md

Reply "approved" to write and commit this release, or tell me what to change.
```

Keep it compact. Omit sections that do not apply, like structured data when there is no structured data file. Do not include tag style, GitHub Release readiness, or publish options unless the user explicitly asked for them.

Wait for the user to explicitly approve (e.g., "looks good", "approved", "go", "yes", "do it").

If the user requests changes, revise and present again. Loop until approved.

### Step 6: Write changes

After approval, execute ALL writes:

**A. Bump version in version source file:**
- `package.json`: update the `"version"` field
- Other files: update the version string in the appropriate location

**B. Prepend to CHANGELOG.md:**
- Add the new entry immediately after the `# Changelog` header (or after any intro text)
- If `[Unreleased]` exists, keep it above the new version entry and make it empty after promoting released items
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

### Step 8: Finish or handle explicit publish request

Report what was written:
- Version bumped: `old → new`
- Files modified: list
- Commit hash: show it

If the user did not explicitly ask for tags, pushed tags, or a GitHub Release, stop here. Do not mention publish actions.

If the user explicitly asked for publish actions, offer only the publish actions that are actually available:
- **Annotated local tag**: `git tag -a <tag> -m "<tag>"`
- **Push tag**: `git push origin <tag>`
- **GitHub Release**: `gh release create <tag> --notes-file <release-notes-file>`

Use the detected tag style. If there are no existing tags and the user has not chosen a style yet, ask before tagging and recommend `vX.Y.Z`. For prerelease versions, include the prerelease identifier in the tag, such as `v1.15.8-beta.1`.

For GitHub Releases, first verify the tag exists on the remote; create and push the annotated tag after approval if needed. Then write release notes from the new changelog entry to a temporary file and pass it with `--notes-file`. Use `--notes-from-tag` only when the tag message is intentionally the release notes.

Use this post-commit shape:

```markdown
Release commit created: abc1234

Available publish actions:
- Create annotated local tag vX.Y.Z
- Push tag vX.Y.Z to origin
- Create GitHub Release from the changelog notes

I will not publish anything unless you explicitly approve those actions.
```

If some actions are unavailable, say why in the same list: `Create GitHub Release: unavailable because gh is not authenticated`.

**Hard stop:** Do not create tags, push tags, or create GitHub Releases until the user explicitly approves those publish actions after the commit.

### Step 9: Done

After finishing the release commit, and after any explicitly requested and approved publish actions, report:
- Tag created/pushed, if any
- GitHub Release URL, if created
- Anything skipped because tooling/auth was unavailable

---

## Execution Rules

These rules are non-negotiable. Follow them exactly.

### Publish only on explicit request and approval
- Do NOT push commits as part of this skill
- Do NOT mention, create, or offer git tags unless the user explicitly asks for tagging/publishing
- Do NOT mention, push, or offer pushed tags unless the user explicitly asks for tagging/publishing
- Do NOT mention, create, or offer GitHub Releases unless the user explicitly asks for GitHub Releases/publishing
- The default workflow stops after the release commit

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
When a user says "commit and push" in a project with this skill installed, treat it as an Update Mode trigger. Commit the changelog/version only after approval. Do not push commits, and do not bring up tags or GitHub Releases unless the user explicitly requested them.

### No changes to document
If `git log` shows no commits since the last changelog entry and there are no uncommitted changes, inform the user: "No changes found since the last changelog entry (vX.Y.Z on Date). Nothing to update."

### Version mismatch
If `package.json` version differs from the latest CHANGELOG.md version, flag it:
"package.json is at vX.Y.Z but the latest changelog entry is vA.B.C. Which should I use as the base?"

### Multiple structured data files
If both a `.tsx` and `.json` changelog data file exist, update both. Ask the user which is canonical if unclear.

### Pre-release ambiguity
If the user requests a pre-release but does not specify the label, ask whether to use `alpha`, `beta`, or `rc`. If a pre-release label already exists, continue that label by default.

### Feature-branch prerelease track
When the user asks to version a feature branch without bumping the official release line:
- Recommend `alpha` for early/private testing, `beta` for broader testing before merge, and `rc` only when the feature is expected to become the next stable release.
- Keep the prerelease bump on the feature branch unless the user explicitly says otherwise.
- Use changelog/version entries like `X.Y.Z-beta.N`; if creating a git tag was explicitly requested, use the same full prerelease version in the tag, such as `vX.Y.Z-beta.N`.
- Do not treat a prerelease changelog entry as the official stable release. When the branch merges and the user asks to finalize, convert the chosen prerelease base to stable, e.g. `1.8.0-beta.4` → `1.8.0`.

### Non-JS projects
For Python, Rust, Go, or other projects without `package.json`:
- Bump version in the appropriate file (`pyproject.toml`, `Cargo.toml`, `VERSION`)
- Skip structured data file and UI component steps
- CHANGELOG.md is the only changelog target
