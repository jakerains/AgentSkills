# Plaud MCP — full reference

Source: `@plaud-ai/mcp` on npm + the hosted HTTP endpoint at `https://mcp.plaud.ai/mcp`. Token store is `~/.plaud/tokens-mcp.json` (distinct from the CLI's `~/.plaud/tokens.json`).

## Contents

1. Supported clients
2. Install (one command)
3. Install flags
4. Manual JSON config
5. HTTP variant (Claude Web, ChatGPT Web)
6. Tool inventory
7. `list_files` filtering
8. Built-in Plaud skills (auto-loaded)
9. Data fields
10. Upgrade / uninstall

---

## 1. Supported clients

| Client | Auto-configured | Restart required |
|--------|-----------------|------------------|
| Claude Desktop | ✓ | ⌘Q + reopen |
| Claude Code | ✓ | Exit + new `claude` session |
| Codex Desktop | ✓ | Quit + reopen |
| Cursor / Windsurf / VS Code / Zed | ✓ | Reload per client UI |
| Claude Web / ChatGPT Web | Interactive guide | No restart needed |

Prerequisites: Node.js ≥ 20, a Plaud account.

## 2. Install

```bash
npx -y @plaud-ai/mcp@latest install
```

This single command:

1. Detects installed AI clients on your machine
2. Writes the MCP config block to each one
3. Opens the browser for OAuth sign-in

After authorization, **fully restart** each affected client. For Claude Code: exit the terminal session and start a new `claude` session — reloading is not enough.

## 3. Install flags

| Flag | Behavior |
|------|----------|
| `--yes` | Auto-configure all detected local clients with no prompts |
| `--no-login` | Skip the browser sign-in step (useful on remote/headless machines) |

`--yes` without `--no-login` still opens the browser; combine both for fully unattended config.

## 4. Manual JSON config

For clients not auto-detected, paste into the client's MCP config:

```json
{
  "mcpServers": {
    "plaud": {
      "command": "npx",
      "args": ["-y", "@plaud-ai/mcp@latest"]
    }
  }
}
```

Then trigger sign-in by asking the AI client: *"log me into Plaud"* — the MCP's `login` tool runs an OAuth browser flow.

## 5. HTTP variant (Claude Web, ChatGPT Web)

Use when there's no local process to run the npm package (browser-only clients). Recording data passes through Plaud's US-hosted MCP server in transit (not persisted). Data handling: see [Plaud's privacy policy](https://plaud.ai/privacy).

### Claude Web

1. claude.ai → profile avatar → **Settings → Connectors**
2. **Add custom connector**
   - **Name** — `Plaud`
   - **Remote MCP server URL** — `https://mcp.plaud.ai/mcp`
3. Click **Add**, then **Authorize** when the Plaud page opens

### ChatGPT Web

1. chatgpt.com → profile avatar → **Settings → Apps → Advanced settings**
2. Toggle **Developer Mode** on
3. **Create app**
   - **Name** — `Plaud`
   - **MCP Server URL** — `https://mcp.plaud.ai/mcp`
   - **Authentication** — `OAuth`
4. Check **I understand and want to continue**, then **Create**
5. **Authorize** on the Plaud page

## 6. Tool inventory

Once connected, the AI client can call:

| Tool | Description |
|------|-------------|
| `login` | Opens browser for OAuth sign-in; blocks until callback or timeout |
| `logout` | Signs out and revokes authorization |
| `get_current_user` | Returns account details |
| `list_files` | Lists recordings; supports filters (see §7) |
| `get_file` | Full details for one recording, including `presigned_url`, `source_list`, `note_list` |
| `get_note` | AI-generated summary, action items, key topics for one recording |
| `get_transcript` | Full timestamped transcript with speaker labels |

## 7. `list_files` filtering

| Parameter | Description |
|-----------|-------------|
| `query` | Case-insensitive keyword match on recording name |
| `date_from` | Start date, `YYYY-MM-DD` |
| `date_to` | End date, `YYYY-MM-DD` |
| `page` / `page_size` | Pagination — **ignored when filters are set** |

Practical rule: if `query` or `date_*` is present, you get all matches (up to the server cap); otherwise you paginate.

## 8. Built-in Plaud skills (auto-loaded)

The installer also installs Plaud's own internal skills into Claude Code. They activate on natural-language intents and contain the actual execution playbooks — **don't duplicate them in this skill**:

| Skill | Triggers on phrases like… |
|-------|---------------------------|
| `plaud-browse` | "list my recordings", "show recent files" |
| `plaud-find` | "find the Weekly Sync", "the meeting from Monday" |
| `plaud-read` | "show the transcript", "summarize this recording" |
| `plaud-digest` | "weekly report", "what meetings did I have this week" |
| `plaud-followup` | "draft a follow-up email", "list the action items" |
| `plaud-export` | "save to Notion", "post to Slack" |

If a user request maps to one of these in an AI client that has the MCP installed, let those skills do the work. Use this skill for install, surface choice, CLI-only workflows, and cross-surface combinations.

## 9. Data fields

`list_files` and `get_file` return:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique recording ID |
| `name` | string | Recording name |
| `created_at` | string | Creation time (ISO 8601) |
| `start_at` | string | Recording start time (ISO 8601) |
| `duration` | number | Duration in **milliseconds** |
| `serial_number` | string | Device serial number |

`get_file` adds:

| Field | Type | Description |
|-------|------|-------------|
| `presigned_url` | string | Temporary audio download URL — **valid 24 hours** |
| `source_list` | array | Transcript segments with timestamps + speaker labels |
| `note_list` | array | AI-generated notes in Markdown |

Inside `source_list`, items with `data_type === "transaction"` carry transcript segments (the `data_content` is a JSON-encoded string). Inside `note_list`, items with `data_type === "auto_sum_note"` carry the summary (Markdown in `data_content`).

## 10. Upgrade / uninstall

Upgrade:

```bash
npm install -g @plaud-ai/mcp@latest
```

Then restart each AI client. For Claude Code specifically:

```bash
npx -y @plaud-ai/mcp clean-plugin
# then inside Claude Code:
/plugin install plaud
```

Uninstall, per client:

| Client | Cleanup command |
|--------|-----------------|
| Claude Desktop | `plaud-mcp unsetup` |
| Claude Code | `claude mcp remove plaud --scope user && npx -y @plaud-ai/mcp clean-plugin` |
| Codex Desktop | `plaud-mcp unsetup codex` |

Then remove the package and local data:

```bash
npm uninstall -g @plaud-ai/mcp
rm -rf ~/.plaud   # nukes BOTH CLI and MCP tokens — only if you want a clean wipe
```
