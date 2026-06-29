# Plaud troubleshooting

Quick lookup for the common failure modes. Symptoms first.

## CLI — `plaud: command not found`

Reopen your terminal so the new `PATH` from `npm install -g` takes effect. If still missing, confirm `npm install -g @plaud-ai/cli` completed without errors. On managed Node setups (nvm, asdf), confirm the global install landed in the same Node version your shell is using.

## CLI — `npx` returns `E404` for `@plaud-ai/cli`

Stale npm cache. Clear and retry:

```bash
npm cache clean --force
npm install -g @plaud-ai/cli@latest
```

## Auth — `401` / "Not authenticated"

The fast path:

- **CLI:** run `plaud login` and retry the command.
- **MCP in an AI client:** ask the client *"log me into Plaud"* — it calls the MCP `login` tool which opens the browser.

If `login` itself fails, jump to "Token refresh errors" below.

## Token refresh errors

Tokens at `~/.plaud/tokens.json` (CLI) and `~/.plaud/tokens-mcp.json` (MCP) are managed automatically. If refresh fails repeatedly, delete the relevant file and sign in again:

```bash
# CLI
rm ~/.plaud/tokens.json && plaud login

# MCP
rm ~/.plaud/tokens-mcp.json
# then in your AI client, ask: "log me into Plaud"
```

Don't delete `~/.plaud/` itself unless you want both surfaces wiped at once.

## Browser doesn't open during sign-in

The `login` flow prints a URL. Copy it and open in any browser. The OAuth callback lands on `http://localhost:8199` — for remote machines, SSH-forward that port first:

```bash
ssh -L 8199:localhost:8199 user@host
```

## MCP — Plaud tools don't appear after install

Common cause: the client wasn't fully restarted. Closing the window is usually not enough.

- **Claude Code:** exit the `claude` session and start a new one.
- **Claude Desktop:** ⌘Q (or File → Quit), then reopen.
- **Codex Desktop:** Quit, then reopen.
- **Cursor / Windsurf / VS Code / Zed:** use each client's full reload command.

## MCP — `--yes` mode said "no local clients configured"

The installer didn't detect any supported AI clients on this machine. Either install a local client first (Claude Desktop, Claude Code, Codex Desktop, Cursor, Windsurf, VS Code, or Zed), or drop the `--yes` flag to get the interactive guide that walks through HTTP setup for Claude Web / ChatGPT Web.

## MCP — "Server disconnected" in Claude Desktop

Re-run setup:

```bash
plaud-mcp unsetup
plaud-mcp setup
```

Then quit and reopen Claude Desktop.

## MCP — Claude Code: version didn't update after `npm install -g @plaud-ai/mcp@latest`

The plugin needs to be reset:

```bash
npx -y @plaud-ai/mcp clean-plugin
```

Then inside Claude Code:

```
/plugin install plaud
```

Restart the `claude` session.

## MCP — Codex Desktop cleanup

```bash
plaud-mcp unsetup codex
```

## Wipe everything

If you want to remove all Plaud state on the machine:

```bash
# CLI
npm uninstall -g @plaud-ai/cli

# MCP (run client-specific unsetup first — see above)
npm uninstall -g @plaud-ai/mcp

# Local data — removes BOTH surfaces' tokens
rm -rf ~/.plaud
```
