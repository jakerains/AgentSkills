---
name: plaud
description: Install and use Plaud's voice-recording API surfaces — the Plaud CLI (@plaud-ai/cli) for terminal/scripted access and the Plaud MCP server (@plaud-ai/mcp) for conversational access from Claude Code, Claude Desktop, Cursor, Windsurf, Codex, VS Code, Zed, Claude Web, and ChatGPT. Triggers on mentions of Plaud, voice memos, meeting recordings, transcripts, summaries, AI notes, action items from a recording, or wiring an AI client into a Plaud account. Use when the user wants to search recordings, read transcripts, generate summaries, bulk export, draft follow-ups from a meeting, or troubleshoot Plaud install/auth.
---

# Plaud

Plaud ships two agent-facing surfaces from one vendor and one account:

- **`@plaud-ai/cli`** — terminal, scriptable, pipeable.
- **`@plaud-ai/mcp`** — Model Context Protocol server that auto-installs into Claude Code, Claude Desktop, Codex, Cursor/Windsurf/VS Code/Zed, plus an HTTP variant for Claude Web and ChatGPT.

Both authenticate via OAuth in the browser. Both live under `~/.plaud/` but use separate token files (`tokens.json` for CLI, `tokens-mcp.json` for MCP), so they can coexist.

## Skill structure

```
plaud/
├── SKILL.md              ← Router + install + quick reference (this file)
└── references/
    ├── cli.md            ← Full CLI command reference + config + env vars + exit codes
    ├── mcp.md            ← Full MCP install per client + manual JSON + HTTP variant + tool inventory
    ├── workflows.md      ← Cookbook: bulk export, date-range digest, cross-surface recipes
    └── troubleshooting.md ← Auth, token refresh, install, MCP "server disconnected"
```

## Choose a surface

| User intent | Use |
|-------------|-----|
| "Summarize Tuesday's standup" / "draft follow-up from this meeting" — conversational, inside an AI client | **MCP** |
| "Bulk-export every transcript from April to .txt files" — shell pipeline, cron, scripted | **CLI** |
| Working in Claude Web or ChatGPT (no local install possible) | **MCP via HTTP** (`https://mcp.plaud.ai/mcp`) |
| Headless / remote / CI machine | **CLI** with `PLAUD_*` env vars |
| Want both | Install both — they share auth but use separate token files |

When in doubt: if the agent should call Plaud on the user's behalf inside an AI client → MCP. If a shell script or human in a terminal needs the data → CLI.

## Install — MCP

Run once. The installer detects local AI clients, writes config, and opens the browser for OAuth:

```bash
npx -y @plaud-ai/mcp@latest install
```

Then **fully restart** the AI client (close and reopen the window — for Claude Code, exit and start a new `claude` session). Flags:

- `--yes` — auto-configure all detected clients, no prompts
- `--no-login` — skip browser sign-in (for remote/headless machines)

For clients not auto-detected, add this manually to their MCP config:

```json
{ "mcpServers": { "plaud": { "command": "npx", "args": ["-y", "@plaud-ai/mcp@latest"] } } }
```

For Claude Web / ChatGPT Web (HTTP variant): see `references/mcp.md`. Note: HTTP requests pass recording data through Plaud's US-hosted MCP server in transit.

The installer also loads Plaud's own built-in skills (`plaud-browse`, `plaud-find`, `plaud-read`, `plaud-digest`, `plaud-followup`, `plaud-export`) into Claude Code. **This skill defers to those for the in-MCP execution playbooks** — do not re-implement their logic here.

## Install — CLI

```bash
npm install -g @plaud-ai/cli
plaud login          # opens browser for OAuth
plaud me             # confirm sign-in
```

Requires Node.js ≥ 20.

## Quick reference

| Task | CLI command | MCP tool |
|------|-------------|----------|
| Sign in | `plaud login` | `login` |
| Whoami | `plaud me` | `get_current_user` |
| List recordings | `plaud files` / `plaud recent` / `plaud today` | `list_files` |
| Search by keyword | `plaud search "Q2"` | `list_files` with `query` |
| Filter by date | `plaud search ... --from 2026-04-01 --to 2026-04-30` | `list_files` with `date_from` / `date_to` |
| Get one recording | `plaud file <id>` | `get_file` |
| Audio download URL (24h) | `plaud audio <id>` | `get_file` → `presigned_url` |
| Transcript | `plaud transcript <id>` | `get_transcript` |
| AI summary | `plaud summary <id>` | `get_note` |
| Sign out | `plaud logout` | `logout` |

Pipe-friendly: CLI errors go to **stderr**, results go to **stdout**. `plaud transcript <id> -o file.txt` or `plaud summary <id> -o file.md` write to disk.

## Deep references

| Read when… | File |
|------------|------|
| Need a full flag table, exit codes, config file, or `PLAUD_*` env vars | `references/cli.md` |
| Setting up MCP in a non-default client, or using the HTTP variant in Claude Web / ChatGPT | `references/mcp.md` |
| Writing a shell pipeline, scheduled job, or cross-surface workflow | `references/workflows.md` |
| Auth errors, token refresh, "command not found", MCP "Server disconnected", Claude Code plugin reset | `references/troubleshooting.md` |

## Upgrade / uninstall

```bash
# CLI
npm install -g @plaud-ai/cli@latest
plaud update                          # check for new version

# MCP
npm install -g @plaud-ai/mcp@latest
# Claude Code only — also run:
npx -y @plaud-ai/mcp clean-plugin
# then inside Claude Code:
/plugin install plaud

# Full uninstall
plaud-mcp unsetup                     # for Claude Desktop
claude mcp remove plaud --scope user  # for Claude Code
npm uninstall -g @plaud-ai/cli @plaud-ai/mcp
rm -rf ~/.plaud
```

See `references/troubleshooting.md` for the Codex Desktop unsetup command and other client-specific cleanup.
