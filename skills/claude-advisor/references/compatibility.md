# Compatibility and evidence

Checked against Claude Code 2.1.263 on macOS on 2026-09-06. Feature-detect with the
helper's `doctor` command; version alone does not prove login, provider support,
organization policy or a target's inbound settings.

| Capability | Interface and boundary |
| --- | --- |
| Local inventory | `claude agents --json --all`; full UUID, name, cwd and live PID |
| Live local send | Native SendMessage through a restricted, guarded courier; no raw socket protocol |
| Stopped local turn | `claude -p --resume <UUID> --output-format json`; executes work |
| Existing cloud queue | `claude -p --cloud <id> --output-format json`; queue receipt only |
| Historical name lookup | Optional official Python Agent SDK `list_sessions()` |
| Persistent advisory work | Existing restricted Opus/Fable wrappers and six-report bindings |

Python helpers require Python 3.10+. Live courier hooks are supported by this
implementation on macOS/Linux, including Linux under WSL; native Windows is not
qualified. Pure inventory and cloud queue use portable subprocess arguments.
Advisory wrappers additionally require bash and jq.

Cross-session messaging requires Claude Code 2.1.224+ on macOS/Linux and 2.1.234+
on native Windows; same-machine third-party-provider support requires 2.1.248+.
Restricted mode and other helper flags also need to exist in the installed CLI.

No promise is made that every chat called "Claude" is discoverable: ordinary
Claude.ai chats, Claude Desktop chat history, cloud sessions by local display name,
other computers and other operating-system accounts are separate surfaces.
MCP channels require receiver setup and are not part of this skill's transport.

Live macOS checks confirmed cross-directory lookup and guarded delivery to an
isolated background session; that receiver echoed the message ID and unique marker.
An installed-path send to a name containing spaces passed from a different folder,
and headless continuation of a stopped test conversation returned the same session
ID and its requested marker. An identical installed-path send reused its receipt
without a second courier invocation.
Separate hold/refuse test receivers confirmed that SendMessage's immediate success
receipt does not establish receiver delivery. Preserve the explicit unconfirmed
receiver status rather than trusting the courier's final prose.

## Authoritative references

- [Sessions](https://code.claude.com/docs/en/sessions): headless continuation and the
  warning that concurrent resumes can interleave a transcript.
- [Agent view JSON inventory](https://code.claude.com/docs/en/agent-view#list-sessions-as-json):
  live PID versus background state; discovery across folders.
- [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging):
  ListAgents/SendMessage, name lookup, receiver permissions, held/refused delivery.
- [Cloud follow-ups](https://code.claude.com/docs/en/claude-code-on-the-web#send-follow-ups-from-the-cli):
  existing-session queue syntax and structured acknowledgements.
- [Python Agent SDK](https://code.claude.com/docs/en/agent-sdk/python#list_sessions):
  supported metadata lookup rather than internal transcript parsing.
- [Channels](https://code.claude.com/docs/en/channels): optional configured push events,
  not a universal ID-based sender.
- [Hooks](https://code.claude.com/docs/en/hooks): PreToolUse decisions and updatedInput.

## Validation

Run the bundled deterministic tests without contacting any Claude session:

```bash
python3 -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py' -v
bash -n "$SKILL_DIR/scripts/consult-claude-model.sh"
python3 "$SKILL_DIR/scripts/claude_handoff.py" doctor
```

Use disposable Claude sessions to qualify live delivery and stopped-session resume
on a new CLI/platform. Confirm a unique marker in the receiver's own output; a
passing dry run or sender receipt alone is not receiver proof. Do not send test
messages to an owner's real working conversations. Cloud transport fixtures verify
parsing and invocation, but cannot establish live account delivery without a
designated cloud test session.
