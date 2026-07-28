# Changelog

## 2026-07-28

### claude-advisor

- Documented the intended host: **Codex** / the **ChatGPT desktop** work surface.
- Documented the hard prerequisite: local **Claude Code** with `claude` on `PATH` (plus `jq`).
- Explained the bridge mechanism: wrappers call Claude Code **print mode** (`claude -p`) for a one-shot JSON advisory result, then verify the model family and save the report.
- Updated README skill blurb and table summary to match.
