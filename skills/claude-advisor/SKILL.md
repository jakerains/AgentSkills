---
name: claude-advisor
description: Consult Claude for a second opinion or send a result, finding, update, or work handoff to a specific existing Claude Code conversation from Codex or another local host agent. Use for requests such as "send this to Claude chat 'claude test'", "pass these findings to Claude", "tell the Claude session named X", "continue that Claude conversation", or "ask Claude for a review"; no explicit skill tag is needed. Resolve named local sessions across project folders, bind exact destinations, message running sessions, explicitly resume stopped sessions, or queue to an existing Claude cloud URL. Keep ordinary advice read-only with persistent Opus or explicitly requested Fable sessions. Requires authenticated Claude Code; Python 3.10+ for handoffs, bash and jq for advice. Sending requires user authorization and a unique destination; a mention or pasted link alone is not a send request.
---

# Claude Advisor and Handoff

Use two distinct modes: get bounded read-only advice, or relay authorized work to
an existing Claude conversation. Codex owns its decisions; a receiving Claude
conversation retains its own owner instructions and permissions.

## Route the request

| User intent | Action |
| --- | --- |
| "Ask Claude to review this approach" | Consult the read-only advisor, default Opus |
| "Send this over to Claude chat 'claude test'" | Resolve that exact name and hand off |
| "Pass the findings to this Claude URL" | Queue one message into that existing cloud session |
| "Continue that stopped Claude conversation with these findings" | Resolve it, then explicitly resume and run one turn |
| "Connect this task to Claude session X" | Bind the exact destination for later use; do not send yet |
| "What Claude sessions are running?" | List/inspect only |

Infer "this", "these findings", and similar content from the current task. Prepare
the useful result before sending it. Carry forward the user's established scope
and target. Do not ask for approval again when the request already authorizes the
handoff. Ask only for missing content or a destination that cannot be uniquely
resolved. A vague request for advice is not authorization to message unrelated
existing Claude sessions.

## Consult Claude

Read [references/advisory.md](references/advisory.md) for advisory model selection,
prompt composition, persistence, report handling, and failure behavior. Resolve
scripts relative to this skill's directory and run from the project being reviewed:

```bash
bash "$SKILL_DIR/scripts/consult-opus.sh" "<focused advisory question>"
# Only for an explicit Fable request or a justified frontier question:
bash "$SKILL_DIR/scripts/consult-fable.sh" "<focused advisory question>"
```

The existing wrapper commands and bindings remain compatible. Ordinary advice
uses restricted Read/Grep/Glob tools, no MCP, and refuses inbound peer messages.
Never broaden an advisor's permissions to make a handoff work. Skip model
consultation for mechanical tasks that local tools can settle.

## Resolve a handoff destination

Read [references/handoffs.md](references/handoffs.md) for delivery, receipts,
bindings, stopped-session history, and recovery. The Python helper requires
Python 3.10+ and an authenticated Claude Code CLI. Check capabilities when needed:

```bash
python3 "$SKILL_DIR/scripts/claude_handoff.py" doctor
python3 "$SKILL_DIR/scripts/claude_handoff.py" list
python3 "$SKILL_DIR/scripts/claude_handoff.py" inspect --to 'claude test'
```

Discovery uses `claude agents --json --all` across local project folders, not the
current folder alone. Names containing spaces work. Match exact names or UUIDs;
use `--project '/path/to/project'` to distinguish duplicate records. Do not select
the newest, fuzzy-match silently, or confuse background job IDs with session UUIDs.
If two **live** sessions still have the same name, have the owner rename one:
Claude's native SendMessage lookup uses names, not full session UUIDs.

For an unlisted older session, use `--history` with the optional official
`claude-agent-sdk` package, or an explicit UUID and project directory. Local discovery
does not search other computers. For cloud sessions, accept an explicit
`https://claude.ai/code/<id>` URL or `session_...`/`cse_...` ID. Never substitute a
local session for a remote destination.

## Send one handoff

Prepare a compact body with Outcome, Evidence, Requested action, and Work continuing
when useful, matching the shape of the reciprocal `codex-handoff` skill. Preserve
the user's exact wording when they supply a message. Keep secrets and unnecessary
private data out of the message; local artifact paths do not transfer files.

```bash
python3 "$SKILL_DIR/scripts/claude_handoff.py" send --to 'claude test' <<'HANDOFF_EOF'
Outcome:
<useful findings or prepared work>

Evidence:
<relevant paths and observations>

Requested action:
<bounded next step in the receiving conversation>

Work continuing: No
HANDOFF_EOF
```

The helper adds `[Codex handoff]`, source provenance, a message ID, and the
receiving authority boundary. Use `--file` for a prepared UTF-8 file, `--message`
for short text, or `--dry-run` to inspect without sending. Pass arguments as data;
never interpolate handoff text into shell code.

- **Live local:** a restricted Opus courier can only send one exact message. A
  PreToolUse hook checks the target identity and literal content immediately before
  allowing SendMessage. It cannot read project files or execute the handoff itself.
- **Stopped local:** use `--resume` only when continuing/running that conversation
  is within the user's request. This executes a turn; it is not a passive queue.
- **Cloud:** use the explicit existing target; the helper queues and exits.
- **Return once:** add `--reply-to '<Codex task UUID>'` only when the user requested
  a reply back. The receiver can use `codex-handoff` if installed and permitted.

Do not stop, restart, fork, rename, change inbound settings, or grant permissions
to the destination just to deliver a message. Respect held/refused messages.
Never use concurrent `--resume` as a fallback for live messaging, write directly
into transcript files, or implement an undocumented socket protocol.

## Report the evidence

Use the helper's receipt, not a courier's claim that it sent something:

- `prepared`: dry run, nothing sent.
- `sent` / `queued`: transport acknowledged the handoff; receiver completion is unknown.
- `held`: receiving approval/settings are preventing immediate delivery.
- `completed`: a resumed headless turn finished; inspect its result and any denied tools.
- `refused` / `not_sent` / `failed`: report the actual limitation.
- `uncertain`: inspect the destination and receipt before any retry.

Receipts and bindings are private local state. Identical sends in the same source
task, project and target reuse an ID and do not automatically send again.
Use `--new-message` only for an intentionally new, repeated message, never to evade
an uncertain receipt. A source task UUID supplies return routing, not permission.

For verified capabilities, platform limits and test commands, read
[references/compatibility.md](references/compatibility.md).
