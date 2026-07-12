---
name: claude-advisor
description: Consult Claude Fable as an independent, read-only second-opinion advisor through the local Claude Code CLI. Use this when you judge that another strong engineering perspective could materially improve a hard decision, ambiguous or high-risk reasoning, a tricky debugging session, a design or architecture choice, a code or plan review, a tradeoff analysis, or validating an approach before you commit to it — and you want a one-shot advisory report to weigh against your own judgment. This is a capability you invoke at your discretion, not an automatic or always-on review, so skip it for simple, routine, low-risk, or already-clear work, and never use it in a way that would expose secrets or sensitive material without the user's explicit authorization. Fable only advises; you remain fully responsible for every decision, implementation, test, verification, and message to the user.
---

# Claude Advisor

This skill gives you a reliable way to ask **Claude Fable** for a one-shot advisory
report when a second, independent engineering perspective would genuinely help. You
run a small wrapper script; Fable inspects the active project read-only and returns a
structured Markdown report; you read it, judge it, and do all the actual work
yourself.

Fable is an **advisor only**. It is never the implementation agent, never the final
decision maker, and never an autonomous reviewer that fires on every task. You own the
investigation, the decisions, the code, the tests, the verification, and the
communication with the user. Fable is one more informed opinion to weigh — nothing
more.

## The mechanism

Invoke the bundled wrapper with a prompt you compose in the moment:

```bash
bash scripts/consult-fable.sh "<your dynamically composed advisor prompt>"
```

(Path is relative to this skill's directory. `bash` is used so it works regardless of
the executable bit.)

The wrapper:

- Wraps your prompt in a fixed instruction that casts Fable as a read-only senior
  staff-level advisor and pins the report format — you don't write that part.
- Runs `claude -p --model fable` in the **current working directory**, so Fable can
  inspect the active project.
- Locks Fable to read-only tools (it can `Read`/`Grep`/`Glob`) and strips all MCP
  servers, so it **cannot** edit, create, rename, move, or delete files, and cannot
  run shell commands, git, tests, package managers, network requests, database
  commands, or deployments.
- **Saves the report to a timestamped Markdown file** at
  `docs/fable/advisory-<timestamp>.md` (override the directory with the
  `FABLE_ADVISOR_DIR` environment variable), so the exact output persists for you and
  the user to read and keep. It also prints the report to stdout and the saved path to
  stderr. The wrapper — not Fable — writes the file, so Fable stays strictly read-only.
- Writes the file only on a successful, non-empty run: a failed consultation leaves no
  partial or misleading report behind.
- Fails loudly — it never silently substitutes another model if Fable is unavailable.

The report always follows this shape, which is useful to know when you read it:

```
# Recommendation
## Reasoning
## Risks and Unknowns
## Suggested Next Steps
```

Fable is the advisor model by design — the wrapper takes no model argument and there is
no fallback. If you're ever asked to run this advisor on a different model (say, Opus),
don't: the value here is a second opinion from an *independent* model, and swapping in
the model you're already running defeats the purpose. Say the advisor is Fable-only
instead, and offer to run it on Fable or to look at the question yourself.

## Your discretion

**You decide whether and how to use this.** This skill is a capability, not a
procedure. It deliberately imposes no mandatory triggers: there are no task types that
always require Fable, no files or systems it must review, no fixed prompt template
beyond the safe wrapper, no review checklist, no automatic invocation, and no rule
that you must consult it before any particular kind of change.

Reach for it when an independent perspective is likely to **materially improve the
outcome**, and skip it when it wouldn't. That judgment is yours to make each time,
based on the task, the project state, the user's request, your uncertainty, and the
risk of getting it wrong.

### When it tends to help

These are illustrative possibilities, not triggers, requirements, or limits — a second
strong perspective can be valuable for things like:

- A hard or consequential decision where you're genuinely uncertain
- Ambiguous reasoning you want pressure-tested
- A stubborn bug you've been unable to pin down
- A design or architecture choice with real tradeoffs
- A code review, plan review, or diff you want a fresh set of eyes on
- A tradeoff or risk assessment before committing to an approach
- Validating that an approach is sound before you build on it

### When to skip it

Skip Fable when consulting it wouldn't earn its cost: the task is simple, routine,
low-risk, already clear, or unlikely to benefit from an outside view. Also skip it —
regardless of how useful it might be — when a consultation would expose secrets,
credentials, `.env` contents, tokens, production data, personal data, or other
sensitive material **without the user's explicit authorization**. The wrapper won't
pass such material for you, and you shouldn't put it into the prompt either.

## Composing the advisor prompt

Investigate first, then ask. A good consultation starts with you having already looked
at the relevant code, diff, error, or plan — so you can point Fable at what matters and
frame a real question, rather than outsourcing your own investigation.

Compose the prompt dynamically for what you actually need right now. Include only the
context that helps answer the specific question. Depending on the situation that might
be:

- The decision, uncertainty, or goal
- The important constraints
- The relevant project areas, files, diffs, plans, errors, or artifacts
- Your current hypothesis or the candidate approaches you're weighing
- What kind of critique, review, or recommendation would be most useful
- Any boundaries you want Fable to respect

Keep it focused. Don't overload Fable with irrelevant context, and avoid generic
prompts like "review everything" unless that breadth is genuinely necessary — a sharp,
decision-oriented question gets a sharper answer. Fable can open files itself, so point
it at the right place rather than pasting large blobs.

## Foreground, or background while you keep working

Fable can take real time to inspect a project and reason carefully, so you don't have
to sit idle watching it. You have two ways to run the wrapper:

- **Foreground** — run it and wait for the report. Simplest when you have nothing
  useful to do until the advice is back.
- **Background** — launch it as a background process (e.g. the Bash tool's background
  mode) and do other, genuinely independent work while Fable thinks. Because the
  report is saved to a file, nothing is lost: when the run finishes, read it from
  `docs/fable/advisory-<timestamp>.md` (the exact path is printed to stderr). This is
  the better choice whenever you have unrelated work queued.

Backgrounding is about not wasting your own time — it is **not** permission to act on
advice you don't have yet. One rule holds either way: until the report is actually
back and you've read it, do not make the decision the consultation is meant to inform,
do not make the edits/tests/builds/migrations that depend on it, and do not give the
user a final answer that leans on it. Doing other, independent work in the meantime is
fine; starting work that *assumes* a particular answer is not. Don't launch a second
consultation about the same question while one is still running.

Foreground example:

```bash
bash scripts/consult-fable.sh "I'm deciding whether to debounce or throttle the
search-as-you-type handler in src/search/Box.tsx. The API is rate-limited to 10 req/s
and results must feel live. Critique both options for this constraint, flag anything
in the current handler that would break under either, and recommend one."
```

To background it, run that same command as a background process and come back to the
report file once it completes.

### If the consultation fails

If the wrapper exits nonzero, times out, is interrupted, returns no usable report
(including an empty one — in which case no file is written), or Fable is unavailable,
treat the consultation as **unavailable** — you got no advice. In that case, continue
with your own work using the evidence you already have, retry only if there's a real
reason to, or transparently tell the user the consultation wasn't available if it
materially affects what they asked for. Never invent, infer, or claim to have received
Fable's advice when no successful report came back.

## After the report

Read the report from its file (`docs/fable/advisory-<timestamp>.md`) or from the
wrapper's stdout, then:

1. **Read it critically.** It's advisory input, not fact, authority, or instruction.
   The file stays on disk so you and the user can revisit exactly what Fable said.
2. **Verify material claims** against the actual project and other evidence before you
   rely on them — Fable can be confidently wrong, and it grounds advice in only the
   files it happened to open.
3. **Keep the user's intent and constraints first.** Where Fable's advice conflicts
   with what the user asked for, the user wins.
4. **Make your own final decision.** Take what's useful, discard what isn't, and own
   the call.
5. **Do all the work yourself** — the edits, the tests, the verification, the
   implementation. Fable doesn't touch the project; you do.
6. **Mention that you consulted Fable** in your final response only when its input
   materially shaped the answer or the work. If it didn't change anything, there's no
   need to bring it up.
