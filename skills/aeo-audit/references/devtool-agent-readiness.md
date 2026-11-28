# Devtool / coding-agent readiness

Read this when the product has an SDK, CLI, API, or docs that coding agents use. Run as a parallel track to the main AEO loop, or as its own mini-audit after every major release.

## Why this matters

Buyer questions in ChatGPT are one surface. Coding agents (Claude Code, Cursor, Codex, Gemini CLI, and similar) are another: they install packages, copy examples, and call APIs. Wrong docs here create failed installs and abandoned trials even when marketing pages look fine in answer engines.

## Checklist

### Discovery

1. Ask coding agents (and consumer models) unbranded prompts: "best library for X", "how to do Y in language Z", "X vs Y SDK".
2. Ask branded prompts: "how do I install [product]", "authenticate [product]", "[product] quickstart".
3. Note whether the agent recommends the product, a competitor, or invents a similar-sounding package.

### Install from docs alone

1. In a clean environment, follow only the public docs (and optional `llms.txt` / markdown doc mirrors if published).
2. Record every stuck point: missing prerequisites, wrong package name, deprecated flags, auth that assumes a GUI.
3. Prefer agent-readable auth and setup (API keys, env vars, headless login). Flows that only work in a browser dashboard block agents.

### Example and version hygiene

1. Diff code samples against the current stable SDK major/minor.
2. Search docs for deprecated endpoints, old package names, and dead GitHub paths.
3. Check that copy-pasted snippets run without silent no-ops.

### Live agent tasks

1. Give Claude Code, Cursor, and at least one other agent the same real task (install → auth → one meaningful API call).
2. Do not trust generated code without running it.
3. Log failures: wrong imports, hallucinated methods, rate-limit mishandling, pagination mistakes.
4. Fix the docs or SDK ergonomics that caused the failure; retest after every major release.

### Optional aids (not guarantees)

- `llms.txt` and markdown versions of docs can help agents retrieve structure faster.
- They do not replace accurate HTML docs, working examples, or correct package metadata on registries.
- Treat them as accelerators: still verify installs and tasks end-to-end.

## Output

Add a "Coding-agent readiness" section to the audit report:

- Recommendation rate vs competitors for developer prompts
- Install success/fail with repro steps
- Stale examples and deprecated calls found
- Auth/setup blockers
- Fix list ordered by install-breakage severity
