---
name: claude-advisor
description: Consult Claude from Codex or the ChatGPT desktop app via local Claude Code (`claude -p`). Every consultation creates or resumes a named, bounded, read-only advisory thread tied to the current Codex conversation, project, and model lane, with MCP stripped and a Terminal resume command for direct follow-up. Default to the rolling Opus 5 lane for substantive second opinions, adversarial review, synthesis, debugging, architecture, product or strategy, content and learning quality, creative judgment, and tradeoffs. Reserve pinned Fable 5.1 for explicit requests or rare frontier questions where the premium model is likely to change a consequential answer. Requires authenticated Claude Code on PATH plus jq. Use neither lane for routine deterministic verification. Claude only advises; Codex remains responsible for decisions and actions.
---

# Claude Advisor

Consult one of two Claude models through a persistent, named, bounded conversation
grounded in read-only inspection of the active project:

- **Opus is the default general expert.** Use it for almost all substantive advisory
  work, including work that previously might have gone to Fable.
- **Fable is a rare frontier escalation.** Use it only when explicitly requested or
  when an unusually hard, consequential question is still genuinely unsettled and the
  premium is likely to change the answer.

Both models are advisors only. You own the investigation, decisions, edits, tests,
verification, and communication with the user.

## Host, prerequisites, and how it works

This skill is designed to run **inside Codex** — including the **ChatGPT desktop app**
Codex / work surface — where the host agent can shell out to local tools. It is a
cross-vendor bridge: an OpenAI-side agent asks Claude for a second opinion. It is
**not** meant as Claude-consulting-itself inside a Claude Code session.

**Prerequisite:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) must
be installed locally, authenticated, and available as `claude` on `PATH`. Also
requires `jq`. The skill does not install or configure Claude Code.

### The `claude -p` bridge

The wrappers do not open an interactive Claude TUI. They call Claude Code's
non-interactive **print mode** (`claude -p`):

```text
Codex / ChatGPT desktop agent
  → bash scripts/consult-opus.sh | consult-fable.sh
    → scripts/consult-claude-model.sh
      → claude -p "<full prompt>" --model opus|claude-fable-5-1 --output-format json ...
        ↳ first turn creates a session; later turns use --resume <session-id>
        → verified Markdown report on stdout + saved under docs/opus/ or docs/fable/
```

Each `claude -p` process handles one prompt and returns one result. The runner always
records Claude's returned session ID in a named binding and explicitly resumes it on
later consultations from the same Codex conversation, project directory, and model
lane. The hardened runner then:

1. Builds a fixed read-only advisor instruction plus your advisory request.
2. Invokes `claude -p` with the rolling `opus` alias or pinned
   `claude-fable-5-1` model ID.
3. Uses Claude restricted mode, exposes only `Read`, `Grep`, and `Glob`, denies
   modifying/executing/network/delegating tools, and strips MCP servers.
4. Parses the JSON response, verifies `modelUsage` matches the requested family, and
   extracts the Markdown report.
5. Prints the report to stdout and saves it under `docs/opus/` or `docs/fable/`.

If `claude` is missing, auth fails, the model is unavailable, or verification fails,
treat the consultation as unavailable — do not invent advice or silently switch lanes.

## Choose the advisor lane

Choose one lane deliberately before writing the prompt. Never ask one lane to imitate
the other, and never allow automatic fallback between them.

### Opus 5: default general expert

Use Opus for nearly every substantive consultation where an independent perspective
could materially improve the result. Opus is no longer limited to critique of an
existing candidate; it is also the normal choice for difficult synthesis and human
judgment.

Typical uses include:

- Adversarial review of a plan, diff, implementation, architecture, or design
- Pressure-testing assumptions, counterexamples, failure modes, and hidden coupling
- Debugging and root-cause analysis when the path is uncertain
- Comparing system models or implementation approaches
- Product direction, strategy, user experience, positioning, and tradeoffs
- Content, curriculum, learning design, assessment, narrative, and transfer
- Creative or technical coherence across a large artifact
- Synthesizing a strong first recommendation when no candidate answer exists yet

If the user asks for an adversarial review, second opinion, red team, critique, deep
review, synthesis, or general Claude advisor without naming a model, choose Opus.

The Opus wrapper passes `--model opus`. In Claude Code, `opus` is a rolling alias for
the latest Opus model; as of this update it resolves to `claude-opus-5`. Keep the alias
instead of pinning `claude-opus-5` so future Opus upgrades flow through automatically.
The hardened runner verifies that the response came from the Opus model family before
accepting it.

### Fable 5.1: rare frontier escalation

Fable is the exceptional, premium lane—not the default for content, strategy,
learning, creativity, or synthesis. Use it only when:

- The user explicitly asks for Fable; or
- The question is exceptionally difficult and consequential, remains genuinely
  unsettled after serious local investigation, and there is a concrete reason to
  expect Fable's extra capacity to materially change the decision.

Examples can include a novel multi-domain synthesis with no stable candidate model, a
high-stakes decision with deep unresolved ambiguity, or an artifact whose intended
human outcome depends on unusually subtle judgment that Opus could not resolve.
Breadth, importance, or the presence of content work alone is not enough.

Do not run Opus first merely to create permission to use Fable. If Opus is clearly the
right lane, use Opus and stop. If Fable is clearly justified, use Fable directly.

**Tiebreaker:** choose Opus. Escalate to Fable only for a true edge case or an explicit
request.

The Fable wrapper passes the full `--model claude-fable-5-1` identifier and accepts a
report only when `modelUsage` identifies the Fable 5.1 family. Do not replace this pin
with the rolling `fable` alias: the explicit model ID prevents an older Fable response
from being accepted during the 5.1 transition. A pre-5.1 Fable session cannot silently
continue as 5.1; start a new binding if exact-model verification rejects it.

### Neither lane: mechanical work

Do not ask either model to audit routine process mechanics such as hashes, approval
records, release gates, reviewer assignments, paperwork freshness, checklist
completion, formatting, or commands that deterministic tooling can evaluate.

A broad request such as "run this by the Claude advisor" is not a request to audit
everything in scope. Infer the highest-value substantive question, select the lane,
and brief that model accordingly. Include procedural or governance analysis only when:

- The user explicitly asks for it.
- The procedure itself is the hard design problem.
- It materially changes safety, correctness, human experience, or the substantive
  decision.

## Run the consultation

Invoke exactly one bundled wrapper with a prompt composed for the current question:

```bash
# Default for substantive consultation; rolling alias currently resolves to Opus 5
bash scripts/consult-opus.sh "<your dynamically composed advisor prompt>"

# Rare frontier escalation
bash scripts/consult-fable.sh "<your dynamically composed advisor prompt>"
```

Those commands are persistent by default. In Codex or the ChatGPT desktop Codex work
surface, the runner derives a binding from `CODEX_THREAD_ID`. The first call starts a
Claude session; a later call from the same Codex conversation, exact project directory,
and model lane resumes that session automatically. Opus and Fable keep separate Claude
threads inside the same Codex conversation. Never infer or resume Claude's latest
unbound session.

### Persistent and explicitly named threads

Ordinary calls need no thread flags. Use `--thread` when the host does not expose
`CODEX_THREAD_ID`, when testing outside Codex, or when an explicit human-readable
binding is useful. It starts the binding if absent and resumes it when present:

```bash
# Automatic Codex-conversation binding: start on first use, resume afterward
bash scripts/consult-opus.sh "<advisor prompt or focused follow-up>"

# Explicit binding with the same start-or-resume behavior
bash scripts/consult-opus.sh --thread retry-review "<advisor prompt or follow-up>"

# Advanced lifecycle controls remain available
bash scripts/consult-opus.sh --start-thread retry-review "<initial prompt>"

bash scripts/consult-opus.sh --continue-thread retry-review "<focused follow-up>"

# Branch its prior context under a new binding and native Claude session
bash scripts/consult-opus.sh --fork-thread retry-review alternative-design \
  "Reassess the evidence under this alternative assumption."

# Inspect or retire bindings for the current project directory
bash scripts/advisor-thread.sh list
bash scripts/advisor-thread.sh show opus retry-review
bash scripts/advisor-thread.sh close opus retry-review
bash scripts/advisor-thread.sh unlock opus retry-review  # only after a stale-lock error
```

Thread names use 1–64 letters, digits, dots, underscores, or hyphens. Bindings are
scoped to the exact project directory and model lane, stored with private permissions
under the platform state directory, and advanced only after a verified report is
saved. Closing a binding does not delete Claude's native transcript.
If an interrupted process leaves a stale lock, the runner fails closed. Confirm that
no advisor or Terminal turn is active before using the explicit `unlock` command.

Threads default to six total reports. When that budget is reached, start a new
explicit binding or fork only when retaining prior evidence is genuinely useful.
`CLAUDE_ADVISOR_MAX_THREAD_TURNS` can set a different positive limit for an explicitly
authorized exceptional case; do not raise it merely for convenience. Long-lived
advisor conversations cost more context and can become anchored to the consulting
agent's framing.

Every report receives a runner-generated footer with its resolved model, Claude
session ID, and a ready-to-paste `claude --resume <session-id>` Terminal command. Directly
resuming in Claude uses that interactive session's permissions; it is not constrained
by this advisor wrapper, and those direct turns are not saved as advisor reports or
counted in the binding. Use the ordinary wrapper again or `--thread <name>` to preserve
the read-only lane, and never run a Terminal resume concurrently with a wrapper turn
on the same session.
Treat the footer and captured stdout as private local metadata: remove the footer
before committing, publishing, uploading, or otherwise sharing the report.

Paths are relative to this skill's directory. Use `bash` so the wrappers work
regardless of executable bits.

Both wrappers call one shared hardened runner, which shells out via `claude -p`.
That runner:

- Selects only the closed set `opus` or `fable`; public wrappers accept no model
  argument.
- Uses the rolling Claude Code `--model opus` alias or the pinned
  `--model claude-fable-5-1` identifier and requests structured JSON output.
- Verifies `modelUsage` identifies the selected Opus family or specifically the Fable
  5.1 family before accepting output.
- Adds a lane-specific instruction: broad expert review and synthesis for Opus, rare
  frontier synthesis for Fable.
- Runs in the current working directory so the advisor can inspect the active project.
- Runs in restricted mode, exposes only `Read`, `Grep`, and `Glob`, denies modifying,
  executing, networking, and delegating tools, and strips all MCP servers on every
  fresh, resumed, or forked turn.
- Saves reports as
  `docs/opus/advisory-<thread>-turn-<number>-<timestamp>-<pid>.md` or the matching
  path under `docs/fable/`. Override with `OPUS_ADVISOR_DIR` or `FABLE_ADVISOR_DIR`.
- Prints every successful verified report to stdout and its saved path to stderr.
- Writes no report for a failed, empty, or model-verification-failed run.
- Writes or advances no thread binding unless the response contains a valid
  session ID, passes model verification, and its report is saved.
- Never silently substitutes one model for the other.

The report always follows this shape:

```markdown
# Recommendation

## Reasoning

## Risks and Unknowns

## Suggested Next Steps
```

If a selected model is unavailable, that consultation is unavailable. Do not silently
rerun it on the other lane.

Do not run both models by default. Use both only when the user explicitly asks for two
perspectives or authorizes an unusually valuable comparison.

## Use discretion

This skill is a capability, not an automatic procedure. Reach for it when an
independent perspective is likely to materially improve the outcome. Skip it when the
task is simple, routine, low-risk, already clear, or mechanically decidable.

Also skip it when consultation would expose secrets, credentials, `.env` contents,
tokens, production data, personal data, or other sensitive material without the
user's explicit authorization. Do not put sensitive values into the prompt.

## Compose the advisor prompt

Investigate first. State the difficult judgment you want the advisor to improve, then
compose a focused prompt containing only useful context:

- The decision, uncertainty, or intended outcome
- Relevant constraints and source-of-truth files
- Your current hypothesis or candidate approaches, if any
- The kind of critique, synthesis, or recommendation that would help
- Explicitly settled or out-of-scope topics
- How findings should be ranked

Do not outsource your initial investigation or ask for a generic "review everything"
unless that breadth is necessary. Point the advisor at relevant files instead of
pasting large blobs.

For broad artifact reviews, explicitly define:

- The substantive lens: content, learning, product, strategy, design, architecture,
  technical behavior, or a deliberate combination
- The outcome the artifact should create for a learner, user, or system
- The implementation and source files containing the real experience
- Mechanically checked topics that are out of scope
- The decisive question the report must answer

Good framing:

> Evaluate whether the current five-lesson module teaches the intended capability,
> whether its exercises and assessment produce transfer, and whether its runtime
> design supports the learner experience. Rank content and technical findings. Ignore
> hashes, approval paperwork, and gate mechanics unless they directly change learner
> behavior.

Poor framing:

> Review these packages and tell me whether they are ready.

## Foreground or background

Either lane can take time:

- **Foreground:** run the wrapper and wait when the advice blocks further work.
- **Background:** launch it as a background process and do genuinely independent work,
  then read the exact saved report when it finishes.

Do not make the decision, perform dependent edits, or give a final answer that relies
on the consultation until the report has arrived and you have read it. Do not launch
a second consultation about the same question while one is running. This includes
opening the same named session directly in Claude Terminal during a wrapper turn.

Opus example:

```bash
bash scripts/consult-opus.sh "Review the proposed retry design in
src/queue/worker.ts. Determine whether it is the best approach, pressure-test the
idempotency assumptions, identify failure modes, and distinguish blockers from
optional hardening."
```

Fable edge-case example:

```bash
bash scripts/consult-fable.sh "We have three incompatible models for how this
cross-domain curriculum should produce durable behavior change, and local analysis
has not resolved the conflict. Synthesize the evidence in docs/research/ and
curriculum/, expose assumptions behind each model, and recommend the model most
likely to transfer under the stated constraints."
```

### If the consultation fails

Treat a nonzero exit, timeout, interruption, empty result, invalid structured output,
model-verification failure, or unavailable selected model as no consultation. Do not
switch lanes automatically or invent advice. Continue using available evidence, retry
only for a real reason, or tell the user it was unavailable when that materially
affects the task. If a named-thread resume fails, do not silently create a replacement
session under the same name; report the failure and let the caller choose a fresh name
or an intentional fork.

## After the report

1. Read it critically; it is advisory input, not authority.
2. Verify material claims against the project and other evidence.
3. Keep the user's intent and constraints first.
4. Make and own the final decision.
5. Perform all edits, tests, and verification yourself.
6. Keep incidental process observations from crowding out substantive findings.
7. Name the lane when its advice materially shapes the work.
