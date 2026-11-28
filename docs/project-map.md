# Project map

## Repository

Personal agent skills library (`skills/`), installable via `npx skills add jakerains/AgentSkills`.

## Top-level layout

- `skills/` — one directory per skill; each has a required `SKILL.md`
- `docs/` — project changelog and structure notes
- `README.md` — skill catalog and install commands
- `CLAUDE.md` / `AGENTS.md` — skill-creation guidance for coding agents
- `.claude-plugin/` — marketplace metadata

## Skills

### watercooler

Shared Claude Code ↔ Codex messaging and collaboration skill:

- One-off sends via bundled Python helpers and authenticated local CLIs
- Persistent tickets, inboxes, results, and completion tracking via the WaterCooler service
- Bundled restricted advisor wrappers for read-only Claude second opinions

See `skills/watercooler/SKILL.md`.

### codex-handoff

Directional handoff bridge for **Claude Code → an existing Codex Desktop task**:

- Claude composes a provenance-labelled handoff only after an explicit user request
- `scripts/send_to_codex.py` validates a task UUID or `codex://threads/...` link
- The helper calls the installed `codex queue` command without shell-evaluating text
- Receiving Codex tasks interpret `[Claude handoff]` through the user's global `AGENTS.md`

See `skills/codex-handoff/SKILL.md`.
