# Plaud workflows — cookbook

Recipes that combine the CLI, the MCP, or both. For inside-MCP workflows that the Plaud MCP's own skills already handle (`plaud-browse`, `plaud-find`, `plaud-read`, `plaud-digest`, `plaud-followup`, `plaud-export`), let those skills do the work — this file focuses on what they can't do.

## Contents

1. Bulk-export every transcript in a date range
2. Date-range digest — choosing CLI vs MCP
3. Exit-code-aware re-auth in scripts
4. Cross-surface: MCP find → CLI audio download
5. Headless / CI usage

---

## 1. Bulk-export every transcript in a date range

The MCP can summarize across recordings but can't write a directory of files. The CLI can.

```bash
# Export every March 2026 transcript to ./transcripts/
mkdir -p transcripts
plaud search "" --from 2026-03-01 --to 2026-03-31 --max 500 \
  | awk '/^id:/{print $2}' \
  | while read id; do
      plaud transcript "$id" -o "transcripts/${id}.txt"
    done
```

The exact stdout shape of `plaud search` may evolve — confirm with `plaud search "" --from <date> --to <date>` once and adjust the `awk` selector if needed (the `id` field is always present, but the formatting line may differ across versions).

For summaries instead of transcripts, swap `plaud transcript ... -o ...txt` for `plaud summary ... -o ...md`.

## 2. Date-range digest — choosing CLI vs MCP

Same intent, two surfaces:

| Approach | When to pick it |
|----------|-----------------|
| **MCP** — ask the AI client *"summarize last week's recordings"* | User is already in an AI client conversation; they want a synthesized digest, not raw files. The MCP's built-in `plaud-digest` skill handles it. |
| **CLI** — `plaud search "" --from <date> --to <date>` then feed transcripts into your own LLM call | You want the digest as a build-time artifact (CI, cron, weekly Slack post), or you want to control the synthesis prompt yourself. |

The CLI gives you the IDs and transcripts; what you do with them (LLM call, regex, push to webhook) is yours.

## 3. Exit-code-aware re-auth in scripts

The CLI's exit code 2 means "auth expired, re-login." Use it to make scripts self-healing:

```bash
run_plaud() {
  plaud "$@"
  local code=$?
  if [ $code -eq 2 ]; then
    plaud login || return 1
    plaud "$@"
  else
    return $code
  fi
}

run_plaud files --page 1
```

Note: `plaud login` opens a browser, so this pattern only fits interactive shells. For unattended cron, prefer `PLAUD_*` env-var auth or rotate tokens out-of-band.

## 4. Cross-surface: MCP find → CLI audio download

Sometimes you want the AI client to *find* the recording (semantic match on name + date), then a shell tool to *fetch* the audio (the MCP returns the `presigned_url` but doesn't pipe binary into your shell).

Inside the AI client (MCP):

> "Find the recording from Tuesday afternoon — it's the one with 'pricing' in the name. Give me its ID."

Then in the terminal:

```bash
ID="<paste-from-mcp>"
URL=$(plaud audio "$ID")
curl -L -o recording.mp3 "$URL"
```

The signed URL expires in 24 hours, so re-run `plaud audio` if it goes stale.

## 5. Headless / CI usage

For CI machines without a browser:

1. On a workstation, sign in once: `plaud login`. Copy `~/.plaud/tokens.json` to the CI machine (secret store, not the repo).
2. In CI, restore the file to `~/.plaud/tokens.json` and run `plaud me` to verify.
3. If the refresh URL is non-default, set `PLAUD_REFRESH_URL` and friends in CI env vars (see `cli.md` §10).

For one-off remote machines, `plaud login` prints a URL — open it in your local browser, complete OAuth, the callback lands on the remote on port 8199 (SSH-forward it: `ssh -L 8199:localhost:8199 user@host`).
