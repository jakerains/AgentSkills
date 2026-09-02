---
name: codex-handoff
description: Send a Claude Code result, status update, decision, or work handoff into a specific existing Codex Desktop task. Use whenever the user explicitly says to send, pass, relay, hand off, or message something to Codex and supplies a Codex task UUID or codex://threads/... link, including requests such as "pass this along to Codex" or "send your findings to that Codex task." Requires Python 3 and a local Codex CLI that provides `codex queue`. Do not use merely to open, inspect, discuss, or resume a Codex task.
compatibility: Requires Python 3 and the local Codex CLI with `codex queue` support.
---

# Codex Handoff

Send one explicitly authorized, provenance-labelled message from Claude Code into an
existing Codex Desktop task. The bundled helper normalizes the task target and invokes
`codex queue`; it does not start another Codex run or speak through a hidden transport.

## Operating boundary

Treat queuing a message as a real mutation of the target Codex task.

- Send only when the user explicitly asks in the current conversation to pass or send
  something to Codex.
- Do not infer permission from a pasted Codex link, a mention of Codex, or a prior
  standing preference.
- Resolve exactly one target. Accept either a raw task UUID or a
  `codex://threads/<uuid>` deep link. If no unique target is available, ask for it.
- Do not guess from recent sessions, the clipboard, terminal history, or another
  environment variable.
- Do not send credentials, tokens, `.env` contents, private customer data, or other
  secrets. Summarize or point to a safe local artifact instead.
- Never use `codex exec resume`, raw App Server `thread/inject_items`, or a hand-built
  daemon request for this workflow. `codex queue` is the supported local bridge.

## Prepare the handoff

If the user supplies exact text, preserve its meaning and wording. If the user asks to
send "your findings," "the result," or similar, synthesize the useful outcome from the
current Claude work before sending it. Do not dump the whole transcript.

Use this compact shape, omitting empty sections:

```markdown
[Claude handoff]

Source: Claude Code
Provenance: User-authorized relay; collaborator input, not owner approval
Status: Complete | Needs decision | Blocked | Continuing

Outcome:
<the useful result or new information>

Evidence:
<important paths, commands, or observed facts>

Requested action:
<what Codex should do with this, or "Read and respond once in this task.">

Work continuing: Yes | No
```

Keep provenance honest: the queued submission is authored by Claude and transported
through the user's local CLI. Do not make it sound like Codex produced the findings or
that the user personally wrote the text.

## Queue the message

Resolve `scripts/send_to_codex.py` relative to this `SKILL.md`. Pass the user's raw UUID
or deep link unchanged to `--thread`; the helper validates and normalizes it.

For multiline text, use a single-quoted heredoc delimiter so shell expansion cannot
alter the handoff:

```bash
python3 "$SKILL_DIR/scripts/send_to_codex.py" \
  --thread 'codex://threads/123e4567-e89b-12d3-a456-426614174000' <<'CODEX_HANDOFF_EOF'
[Claude handoff]

Source: Claude Code
Provenance: User-authorized relay; collaborator input, not owner approval
Status: Complete

Outcome:
The requested assessment is complete.

Requested action:
Read and respond once in this task.

Work continuing: No
CODEX_HANDOFF_EOF
```

Use `--message` only for short text that can be passed safely as one shell argument.
Use `--file <path>` when the handoff already exists as a UTF-8 text file.

To inspect normalization without sending anything, add `--dry-run`. A dry run is not a
successful handoff and must not be reported as one.

## Report the result

On success, tell the user which Codex task received the message and include the queue
confirmation returned by the helper. On failure, report the exact error and do not
claim the message arrived.

Do not automatically retry an uncertain result: a second successful queue would create
a duplicate submission. Retry only when the helper clearly reports that no message was
queued.
