---
name: claude-advisor
description: Consult Claude through two explicit, independent, read-only advisor lanes. Default to Opus 5 for nearly every substantive second opinion, including adversarial review, difficult synthesis, debugging, architecture, product or strategy, content and learning quality, creative judgment, tradeoffs, or pressure-testing a plan or artifact. The Opus wrapper intentionally uses the rolling `opus` alias so it follows Anthropic's latest Opus release. Reserve Fable for rare frontier cases where the user explicitly requests it or the problem is exceptionally unsettled, consequential, and likely to benefit materially from the premium model. Use neither for routine procedural compliance or deterministic verification. The selected model only advises; you remain responsible for every decision and action.
---

# Claude Advisor

Consult one of two Claude models for a one-shot advisory report grounded in read-only
inspection of the active project:

- **Opus is the default general expert.** Use it for almost all substantive advisory
  work, including work that previously might have gone to Fable.
- **Fable is a rare frontier escalation.** Use it only when explicitly requested or
  when an unusually hard, consequential question is still genuinely unsettled and the
  premium is likely to change the answer.

Both models are advisors only. You own the investigation, decisions, edits, tests,
verification, and communication with the user.

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

### Fable: rare frontier escalation

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

Paths are relative to this skill's directory. Use `bash` so the wrappers work
regardless of executable bits.

Both wrappers use one shared hardened runner. It:

- Selects only the closed set `opus` or `fable`; public wrappers accept no model
  argument.
- Uses the rolling Claude Code aliases and requests structured JSON output.
- Verifies `modelUsage` identifies the selected model family before accepting output.
- Adds a lane-specific instruction: broad expert review and synthesis for Opus, rare
  frontier synthesis for Fable.
- Runs in the current working directory so the advisor can inspect the active project.
- Exposes only `Read`, `Grep`, and `Glob`, denies modifying, executing, networking, and
  delegating tools, and strips all MCP servers.
- Saves Opus reports to
  `docs/opus/advisory-<timestamp>-<pid>.md` and Fable reports to
  `docs/fable/advisory-<timestamp>-<pid>.md`. Override with `OPUS_ADVISOR_DIR` or
  `FABLE_ADVISOR_DIR`.
- Prints every successful verified report to stdout and its saved path to stderr.
- Writes no report for a failed, empty, or model-verification-failed run.
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
a second consultation about the same question while one is running.

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
affects the task.

## After the report

1. Read it critically; it is advisory input, not authority.
2. Verify material claims against the project and other evidence.
3. Keep the user's intent and constraints first.
4. Make and own the final decision.
5. Perform all edits, tests, and verification yourself.
6. Keep incidental process observations from crowding out substantive findings.
7. Name the lane when its advice materially shapes the work.
