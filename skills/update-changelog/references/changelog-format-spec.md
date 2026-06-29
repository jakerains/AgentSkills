# CHANGELOG.md Format Specification

Based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - January 15, 2026

### Added
- New feature A
- New feature B

### Changed
- Updated behavior of X

### Fixed
- Bug in Y component

## [1.1.0] - December 1, 2025

### Added
- Initial feature set
```

## Entry Format

Each version entry:

```markdown
## [X.Y.Z] - Month DD, YYYY
```

- Version in square brackets
- Date in `Month DD, YYYY` format (e.g., `April 9, 2026`)
- Entries ordered newest-first (latest at top)

## Change Categories

Use only the categories that apply. Omit empty categories.

| Category | When to use |
|----------|-------------|
| **Added** | New features, new endpoints, new components |
| **Changed** | Changes to existing functionality, behavior modifications |
| **Deprecated** | Features that will be removed in future versions |
| **Removed** | Features removed in this version |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability patches, security improvements |

## Writing Guidelines

- Start each item with a verb: "Add", "Fix", "Update", "Remove", "Improve"
- Be specific: "Fix audio upload timeout on files > 50MB" not "Fix upload bug"
- Group related changes under the same category
- Keep items to one line when possible
- Reference issue/PR numbers if available: "Fix login redirect (#142)"
- Use short commit refs only when they add useful navigation: "Fix migration ordering (a1b2c3d)"
- Use backticks for code references: "Update `generateNotes()` to use streaming"

## Unreleased Section

The `[Unreleased]` section is optional. It tracks changes that haven't been released yet.

When creating a new version entry:
- Move relevant populated items from `[Unreleased]` into the new version section
- Leave a fresh empty `## [Unreleased]` section above the new version
- Do not duplicate items that are already covered by commit-derived release notes

## Pre-release Versions

Stable releases are the default. Use pre-release identifiers only when requested or when continuing an existing pre-release track.

Common examples:
- `1.2.0-alpha.1` for early testing
- `1.2.0-beta.1` for broader testing
- `1.2.0-rc.1` for release candidates

For feature branches, prerelease versions let the branch carry versioned release notes without bumping the official stable line on `main`.

Choose the base version first, then append the prerelease label:
- Stable `1.4.2` + patch beta track → `1.4.3-beta.1`
- Stable `1.4.2` + minor beta track → `1.5.0-beta.1`
- Existing `1.5.0-beta.1` continuing beta → `1.5.0-beta.2`
- Existing `1.5.0-alpha.3` moving to beta → `1.5.0-beta.1`

When finalizing, drop the prerelease suffix from the selected base: `1.5.0-beta.4` → `1.5.0`.

## Tag and Release Notes

Only discuss or create tags and GitHub Releases when the user explicitly asks to tag, publish, or create a GitHub Release.

Match the repository's existing tag convention:
- Existing `v1.2.3` tags → use `vX.Y.Z`
- Existing `1.2.3` tags → use `X.Y.Z`
- No tags → ask, recommend `vX.Y.Z`

For prerelease tags, include the full prerelease version: `v1.2.0-beta.1` or `1.2.0-beta.1`, matching the repository's tag prefix convention.

For GitHub Releases, use the new changelog entry as release notes. Prefer `gh release create <tag> --notes-file <file>` so the public release matches `CHANGELOG.md`.

## Semantic Versioning Quick Reference

| Bump | When | Example |
|------|------|---------|
| **Patch** (x.x.+1) | Bug fixes, docs, deps, small tweaks | 1.2.3 → 1.2.4 |
| **Minor** (x.+1.0) | New features, backwards-compatible additions | 1.2.3 → 1.3.0 |
| **Major** (+1.0.0) | Breaking changes, API redesigns | 1.2.3 → 2.0.0 |
