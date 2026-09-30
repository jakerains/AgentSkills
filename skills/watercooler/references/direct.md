# Direct messages

Use `scripts/watercooler.py send` for one message without a service. The two
destinations have different native delivery semantics.

| Destination | Transport | Meaning of success |
| --- | --- | --- |
| Existing Codex UUID, deep link, or exact name | `codex queue --thread … --message …` | Queued; reading and completion unknown |
| Live local Claude session | Restricted Claude courier using native SendMessage | Native send acknowledged; receiver may hold/refuse it |
| Stopped local Claude session | Explicit `claude -p --resume <UUID>` | One turn finished; inspect result and denied tools |
| Existing Claude cloud ID/URL | `claude -p --cloud <existing-id>` | Queued; no result in the receipt |

Exact Codex names are supported by the installed CLI 0.157.0. Prefer UUIDs for
durable pairings because a display name can change. Native queue resolves names;
the helper never fuzzy-matches or picks a recent chat. Check capabilities with
`doctor` on other versions.

## Claude discovery and bindings

```bash
python3 "$SKILL_DIR/scripts/watercooler.py" claude list
python3 "$SKILL_DIR/scripts/watercooler.py" claude inspect --to 'claude test'
python3 "$SKILL_DIR/scripts/watercooler.py" claude bind partner --to 'claude test'
python3 "$SKILL_DIR/scripts/watercooler.py" claude send --binding partner --file handoff.md
python3 "$SKILL_DIR/scripts/watercooler.py" claude bindings
```

Bindings store an exact UUID and are scoped to the source Codex task, project,
and Claude configuration. The bundled Claude adapter retains the existing
ClaudeAdvisor state namespace so earlier bindings, receipts, and read-only advisor
ownership remain recognizable. Advisory conversations must use the consultation
wrappers rather than an ordinary worker resume.

Discovery uses supported `claude agents --json --all` across local project folders.
For older history, the optional official `claude-agent-sdk` supplies
`list_sessions()` via `--history`; do not parse private transcripts for discovery.
An unlisted stopped UUID requires a known target project and explicit `--resume`.

The live courier exposes only SendMessage. Its hook checks exact destination
identity and literal message before allowing one send. The bundled adapter
conservatively refuses duplicate live names; current native Claude supports
disambiguating addresses, but this adapter has not qualified that extension.
Never use raw sockets or concurrent resume to bypass that refusal.

```bash
python3 "$SKILL_DIR/scripts/watercooler.py" send --to claude \
  --target '<UUID>' --project '/absolute/target/project' --resume --file handoff.md
```

Headless resume is an execution, not a mailbox. Current Claude documentation says
print-mode resume uses the permission mode of a new print run, with conditional
plan-mode restoration. The helper denies unattended permission prompts; it does
not promise that the previous interactive permission mode will be restored.
Never resume an advisor or permission-sensitive worker on assumptions about saved
permissions. Review target configuration and returned denials.

## Replies, receipts, and recovery

For an owner-requested single reply, supply the exact other-harness return UUID:

```bash
python3 "$SKILL_DIR/scripts/watercooler.py" send --to codex \
  --target '<Codex UUID>' --reply-to '<Claude UUID>' --file findings.md
python3 "$SKILL_DIR/scripts/watercooler.py" receipt --to codex '<message UUID>'
python3 "$SKILL_DIR/scripts/watercooler.py" receipt --to claude '<message UUID>'
```

Use the supplied return destination only within authorization already established
by the owner in the receiving session. Include the original ID in the response
body; let the return send receive its own message ID. Do not reuse the incoming ID
as the return receipt ID. A courier is temporary and is not the return endpoint.

Codex receipts live under `WaterCoolerSkill/receipts` in platform private state;
`WATERCOOLER_SKILL_STATE_DIR` overrides this for tests. Claude receipts retain
`ClaudeAdvisor/handoffs`; `CLAUDE_ADVISOR_STATE_DIR` overrides that root.
Identical sends reuse their receipt. `--new-message` intentionally creates another
message and must never be used as uncertain-delivery recovery. A crash during a
reserved send reports `uncertain`; inspect the target before deciding what to do.

Local helpers address sessions on this computer/configuration. Ordinary Claude.ai
chats and Claude Desktop history are separate surfaces. Native Claude Remote
Control can reach eligible sessions elsewhere, but this helper does not promise
remote discovery. Explicit existing cloud URLs use the separate cloud transport.

Authoritative behavior: [Claude messaging](https://code.claude.com/docs/en/cross-session-messaging),
[session inventory](https://code.claude.com/docs/en/agent-view#list-sessions-as-json),
[resume permissions](https://code.claude.com/docs/en/sessions#permission-mode-on-resume).
