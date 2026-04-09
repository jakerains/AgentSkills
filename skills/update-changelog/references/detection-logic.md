# Detection Logic

Complete detection algorithm for determining project state and choosing the correct mode.

## Table of Contents
- [Version Source Detection](#version-source-detection)
- [Changelog File Detection](#changelog-file-detection)
- [Framework Detection](#framework-detection)
- [UI Component Detection](#ui-component-detection)
- [Mode Decision Matrix](#mode-decision-matrix)
- [Format Detection for Existing Data Files](#format-detection-for-existing-data-files)

---

## Version Source Detection

Check in priority order. Use the first match.

| Priority | File | How to read version |
|----------|------|---------------------|
| 1 | `package.json` | `jq -r '.version'` or read JSON, find `"version"` field |
| 2 | `pyproject.toml` | Look under `[project]` → `version` or `[tool.poetry]` → `version` |
| 3 | `Cargo.toml` | Look under `[package]` → `version` |
| 4 | `VERSION` | Plain text file, entire content is the version string |
| 5 | `setup.cfg` | Look under `[metadata]` → `version` |

If none found, the project has no version tracking. Setup mode will create `package.json` (for JS projects) or `VERSION` (for others).

---

## Changelog File Detection

Search for these files using glob patterns:

### Markdown changelogs
```
CHANGELOG.md
changelog.md
docs/CHANGELOG.md
docs/changelog.md
```

### Structured data files
```
lib/changelog-data.tsx
lib/changelog-data.ts
lib/changelog-data.json
src/lib/changelog-data.tsx
src/lib/changelog-data.ts
src/changelog-data.*
changelog.json
changelog-data.*
```

### Broad search (if nothing found above)
```
**/changelog*
**/CHANGELOG*
```

Ignore matches in `node_modules/`, `.next/`, `dist/`, `build/`, `.git/`.

---

## Framework Detection

Detect the project's UI framework to determine which components to create.

### Next.js
Positive signals (any one is sufficient):
- `next.config.js`, `next.config.mjs`, `next.config.ts` exists
- `package.json` has `"next"` in `dependencies` or `devDependencies`
- `app/` directory with `layout.tsx` or `page.tsx`

Sub-detection for App Router vs Pages Router:
- `app/layout.tsx` → App Router
- `pages/_app.tsx` → Pages Router

### React (non-Next)
- `package.json` has `"react"` but no `"next"`
- `src/App.tsx` or `src/App.jsx` exists

### Vue / Nuxt
- `nuxt.config.ts` or `nuxt.config.js` → Nuxt
- `package.json` has `"vue"` → Vue

### SvelteKit
- `svelte.config.js` exists
- `package.json` has `"@sveltejs/kit"`

### No UI framework
- None of the above match
- This is a CLI, library, or backend project
- Skip UI component creation entirely

---

## UI Component Detection

If a UI framework is detected, check for existing changelog-related components.

### Search patterns
```bash
# Grep for changelog-related components
grep -rl "changelog" components/ src/components/ app/ src/app/ 2>/dev/null

# Grep for version display patterns
grep -rl "getCurrentVersion\|packageJson\.version\|APP_VERSION\|getVersion" components/ src/components/ lib/ src/lib/ 2>/dev/null
```

### What to look for
- Existing changelog page route (e.g., `app/changelog/page.tsx`)
- Existing changelog component (e.g., `components/ui/changelog.tsx`)
- Existing version display in sidebar/footer/settings
- Existing `getCurrentVersion()` helper

If existing UI components are found, setup mode should NOT recreate them. Instead, note their existence and adapt the update workflow to work with them.

---

## Mode Decision Matrix

| CHANGELOG.md exists? | Structured data exists? | Mode | Notes |
|----------------------|------------------------|------|-------|
| No | No | **Setup** | Full setup: create everything |
| Yes | No | **Update** | Update CHANGELOG.md only (offer to create structured data) |
| No | Yes | **Update** | Update data file, create CHANGELOG.md as additional target |
| Yes | Yes | **Update** | Dual-write to both |

---

## Format Detection for Existing Data Files

When a structured data file is found, read it to determine entry format.

### TSX with JSX content
Indicators:
- File extension is `.tsx`
- Content field uses JSX: `content: (<div ...>...</div>)`
- Imports React or uses JSX syntax
- Look for patterns like `className="prose"`

Entry template to match:
```tsx
{
  version: "X.Y.Z",
  title: "vX.Y.Z: Title",
  date: "Month DD, YYYY",
  excerpt: "Summary.",
  content: (
    <div className="prose dark:prose-invert prose-sm">
      ...
    </div>
  ),
}
```

### TS with markdown strings
Indicators:
- File extension is `.ts` (not `.tsx`)
- Content field is a string: `content: "### Added\n..."`
- No JSX imports

### JSON
Indicators:
- File extension is `.json`
- Standard JSON structure with string values

### Custom formats
If the format doesn't match any of the above, read at least 3 entries and replicate the exact pattern. Pay attention to:
- Field names and order
- Content encoding (JSX, markdown string, HTML string, array of objects)
- Indentation style (tabs vs spaces, indent width)
- Quote style (single vs double)
- Trailing commas
