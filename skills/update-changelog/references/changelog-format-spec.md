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
- Use backticks for code references: "Update `generateNotes()` to use streaming"

## Unreleased Section

The `[Unreleased]` section is optional. It tracks changes that haven't been released yet.

When creating a new version entry, move relevant items from `[Unreleased]` into the new version section.

## Semantic Versioning Quick Reference

| Bump | When | Example |
|------|------|---------|
| **Patch** (x.x.+1) | Bug fixes, docs, deps, small tweaks | 1.2.3 → 1.2.4 |
| **Minor** (x.+1.0) | New features, backwards-compatible additions | 1.2.3 → 1.3.0 |
| **Major** (+1.0.0) | Breaking changes, API redesigns | 1.2.3 → 2.0.0 |
