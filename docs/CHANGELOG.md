# Changelog

## 2026-07-30

### driverjs-tours

- **Restored the skill.** All six files were deleted as collateral in `6ddaec9` ("Update Claude advisor and skill inventory") while the README section and `skills-lock.json` entry were left pointing at them. Recovered from `a4d1c87`.
- Verified the full content against the live driver.js docs at **v1.8.0** (current npm `latest`). The 1.5.0–1.8.0 additions — `advanceOnClick`, `waitForElement`, `skipMissingElement`, `data`, `allowScroll`, `onDoneClick`, `getNextStep`, the `index` hook option, `--driver-popover-font-family`, and the `driver-popover-footer-btn` / `done-btn` / `side-*` / `align-*` classes — were all already documented correctly.
- Added the hints CDN `<script>`/`<link>` tags, which the upstream installation page lists but the skill omitted.
- Repinned the Subresource Integrity example from `1.4.0` to `1.8.0` and strengthened the CDN warning: the upstream `@latest` tags are explicitly marked as not-for-production, with a note on why `@latest` defeats SRI.
- Stamped `references/configuration.md` as verified against v1.8.0 and noted the 1.7.0 per-instance config isolation fix.

### Repository

- Registered `driverjs-tours` in `.claude-plugin/marketplace.json` — it had a README entry but was **never** in the plugin manifest, so it did not surface to marketplace consumers. Now 19 plugins.
- `simplify` is also absent from `marketplace.json`, and **stays that way by design** — do not "fix" this. The skill is a portable clone of Claude Code's native `/simplify`, built for every *other* agent; Claude Code already has it built in. Since `marketplace.json` targets Claude Code specifically, `simplify` has no audience there. Its README entry and `npx skills add` install path remain the correct route for non-Claude agents.

## 2026-07-28

### claude-advisor

- Documented the intended host: **Codex** / the **ChatGPT desktop** work surface.
- Documented the hard prerequisite: local **Claude Code** with `claude` on `PATH` (plus `jq`).
- Explained the bridge mechanism: wrappers call Claude Code **print mode** (`claude -p`) for a one-shot JSON advisory result, then verify the model family and save the report.
- Updated README skill blurb and table summary to match.
- Refreshed `.claude-plugin/marketplace.json` description/tags (Opus default, Codex/ChatGPT host, `claude -p`).
