# Plaud CLI — full reference

Source: `@plaud-ai/cli` on npm. Companion to the MCP server (see `mcp.md`). Token store is `~/.plaud/tokens.json` (distinct from the MCP's `~/.plaud/tokens-mcp.json`).

## Contents

1. Install
2. Authentication
3. Browse
4. Search
5. Read a recording
6. Utility
7. Output fields
8. Exit codes & stdout/stderr
9. Config file
10. Environment variables
11. Upgrade / uninstall

---

## 1. Install

```bash
npm install -g @plaud-ai/cli
```

Requires Node.js ≥ 20 and a Plaud account.

## 2. Authentication

```bash
plaud login    # opens browser; tokens saved automatically to ~/.plaud/tokens.json
plaud logout   # revokes authorization and clears tokens
plaud me       # prints account details
```

If `login` cannot open a browser (remote/headless machine), copy the URL it prints and open it elsewhere. Tokens refresh automatically on subsequent commands.

## 3. Browse

```bash
plaud files                         # page 1 of recordings, 20 per page
plaud files --page 2 --page-size 50
plaud recent                        # last 7 days
plaud recent --days 30              # last 30 days
plaud today                         # today only
```

`plaud files` options:

| Option | Description | Default |
|--------|-------------|---------|
| `-p, --page` | Page number, 1–1000 | `1` |
| `-s, --page-size` | Items per page, 10–100 | `20` |

## 4. Search

```bash
plaud search <keyword>
plaud search "weekly" --from 2026-04-01 --to 2026-04-30
plaud search "onboarding" --max 10
```

Client-side, case-insensitive keyword match against recording names. Scans up to the 500 most recent recordings.

| Option | Description |
|--------|-------------|
| `--from <YYYY-MM-DD>` | Start of date range (inclusive) |
| `--to <YYYY-MM-DD>` | End of date range (inclusive) |
| `--max <n>` | Max results to display (default `50`) |

## 5. Read a recording

```bash
plaud file <id>                          # full metadata + availability flags
plaud audio <id>                         # 24-hour signed URL for the audio
plaud transcript <id>                    # timestamped transcript
plaud transcript <id> -o transcript.txt  # save to file
plaud summary <id>                       # AI summary (Markdown)
plaud summary <id> -o summary.md         # save to file
```

`plaud audio` URLs are temporary — don't cache them past 24 hours; re-run `plaud audio <id>` to refresh.

## 6. Utility

```bash
plaud version    # installed version + build info
plaud update     # check for newer version, print upgrade command
```

## 7. Output fields

`plaud files` / `plaud file <id>`:

| Field | Description |
|-------|-------------|
| `id` | Unique recording ID — use this in other commands |
| `name` | Recording name |
| `created_at` | Creation time (ISO 8601) |
| `duration` | Length of the recording |

Additional fields in `plaud file <id>` only:

| Field | Description |
|-------|-------------|
| `start_at` | Recording start time (ISO 8601) |
| `serial_number` | Device serial number |
| `audio` | Whether audio is available for download |
| `transcript` | Whether a transcript is available |
| `summary` | Whether an AI summary is available |

## 8. Exit codes & stdout/stderr

Errors go to **stderr**, results to **stdout**. Pipe-safe:

```bash
plaud transcript abc123 | grep -i "action item"
plaud files --page 1 | head
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Invalid arguments or unknown error |
| `2` | Authentication failed — run `plaud login` |
| `3` | Network error — check connection |
| `4` | Request timed out |

Use these in scripts:

```bash
plaud files >/dev/null
if [ $? -eq 2 ]; then plaud login && plaud files; fi
```

## 9. Config file

Optional file at `~/.plaud/cli.yaml`. Only set what you need to override:

```yaml
api_base: "https://platform.plaud.ai/developer/api"
timeout: 30000   # milliseconds
```

Tokens at `~/.plaud/tokens.json` are managed automatically — do not edit by hand.

## 10. Environment variables

Override config file and defaults:

| Variable | Purpose |
|----------|---------|
| `PLAUD_API_BASE` | Override the API base URL |
| `PLAUD_CLIENT_ID` / `PLAUD_CLI_CLIENT_ID` | OAuth client ID |
| `PLAUD_CLIENT_SECRET` | OAuth client secret |
| `PLAUD_AUTH_URL` | Authorization endpoint |
| `PLAUD_TOKEN_URL` | Token exchange endpoint |
| `PLAUD_REFRESH_URL` | Token refresh endpoint |

## 11. Upgrade / uninstall

```bash
npm install -g @plaud-ai/cli@latest
# or
plaud update      # check first
```

Uninstall:

```bash
npm uninstall -g @plaud-ai/cli
rm -rf ~/.plaud   # removes BOTH CLI and MCP tokens — only if you want a clean wipe
```
