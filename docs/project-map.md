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

### claude-advisor

Cross-vendor advisor bridge for **Codex / ChatGPT desktop**:

- Host agent runs bundled bash wrappers
- Wrappers invoke local Claude Code via `claude -p` (print / non-interactive mode)
- Lanes: `consult-opus.sh` (default) and `consult-fable.sh` (rare frontier)
- Shared runner: `scripts/consult-claude-model.sh`
- Reports saved under `docs/opus/` or `docs/fable/` in the active project

See `skills/claude-advisor/SKILL.md`.
