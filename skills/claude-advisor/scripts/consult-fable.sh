#!/usr/bin/env bash
#
# consult-fable.sh — one-shot, read-only advisory consultation with Claude Fable.
#
# The calling agent composes an advisor prompt dynamically and passes it here as a
# single argument. This wrapper wraps that prompt in a fixed read-only advisor
# instruction, invokes Claude Code (`claude -p --model fable`) in the current
# working directory with the narrowest practical permissions, saves Fable's Markdown
# report to a timestamped file, and also echoes it to stdout.
#
# Usage:
#   consult-fable.sh "<advisor prompt>"
#
# Output:
#   The report is written to  $FABLE_ADVISOR_DIR/advisory-<timestamp>.md
#   (default dir: docs/fable, relative to the current working directory) so it
#   persists for you and the user to read and keep. The exact path is printed to
#   stderr; the pure report is printed to stdout.
#
# Backgrounding:
#   The wrapper runs to completion, but the CALLER may run this invocation in the
#   background and do other, unrelated work while Fable thinks — then read the
#   report file once it finishes. It writes no file until Fable succeeds, so a
#   background run either leaves a complete report or none at all.
#
# Fable is an advisor only. It is locked to read-only tools: it cannot edit, create,
# rename, move, or delete files, and cannot run shell commands, git, tests, package
# managers, network requests, or deployments. Enforcement is via Claude Code's own
# permission system (a deny rule always overrides any ambient allow) plus stripping
# all MCP servers, not merely by instructing the model to behave. The wrapper — not
# Fable — writes the report file, so Fable stays strictly read-only.
#
# Contract:
#   - Exits 127 if the `claude` CLI is not on PATH.
#   - Exits 2 if no advisor prompt is supplied.
#   - Never falls back to another model if Fable is unavailable — it fails clearly
#     and propagates Claude Code's own nonzero exit code instead.
#   - On success, writes one self-contained Markdown report to the file and stdout.
#   - On failure or an empty report, writes NO file and exits nonzero.

set -euo pipefail

# --- 1. Confirm the Claude CLI is available -------------------------------------
if ! command -v claude >/dev/null 2>&1; then
  cat >&2 <<'ERR'
consult-fable.sh: error — the `claude` CLI was not found on PATH.

This skill consults Claude Fable through the local Claude Code CLI. Install Claude
Code and ensure `claude` is on PATH, then retry. This wrapper does not install or
configure anything itself.
ERR
  exit 127
fi

# --- 2. Require a non-empty advisor prompt --------------------------------------
# Join all positional arguments; agents normally pass one quoted prompt, but a
# multi-argument invocation is tolerated by concatenating with spaces.
PROMPT="$*"
if [ "$#" -eq 0 ] || [ -z "${PROMPT//[[:space:]]/}" ]; then
  cat >&2 <<'ERR'
usage: consult-fable.sh "<advisor prompt>"

Pass one dynamically composed advisor prompt describing the decision, code area,
diff, plan, bug, or design you want Fable to examine — plus the context and
constraints Fable needs. Keep it focused on the specific question; do not dump
irrelevant context or ask Fable to "review everything" unless that breadth is
genuinely necessary.

Example:

  consult-fable.sh "I'm deciding how to make the job worker in
  src/queue/worker.ts resilient to transient DB failures. I'm leaning toward
  exponential backoff with a max of 5 retries over a fixed 5s delay, because
  bursts are common. Constraints: jobs must run at-least-once and are idempotent.
  Critique this choice, flag failure modes I may be missing, and note anything in
  the current retry code that would undermine it."

The report is saved to docs/fable/advisory-<timestamp>.md (override the directory
with the FABLE_ADVISOR_DIR environment variable).
ERR
  exit 2
fi

# --- 3. Fixed read-only advisor instruction -------------------------------------
# Wraps every consultation. Establishes Fable's role, its hard constraints, and the
# exact report structure. The dynamic request is appended after this block.
read -r -d '' FIXED_INSTRUCTION <<'EOF' || true
You are an independent, read-only senior staff-level engineering advisor.

You are being consulted by another agent that retains full responsibility for investigation, decisions, implementation, validation, testing, and user communication.

Inspect only the active project and only the files necessary to answer the advisory request.

Hard constraints:
- Do not modify, create, delete, rename, move, format, stage, commit, or otherwise change any file.
- Do not run shell commands, tests, package managers, git commands, network requests, database commands, or deployments.
- Do not reveal or reproduce secrets, credentials, tokens, or environment-variable values if encountered.
- Do not ask follow-up questions.
- Do not attempt to implement changes.
- Do not assume the advisory request is correct; identify weak assumptions or missing considerations when relevant.
- Ground advice in observed project evidence whenever possible and clearly distinguish observations, inferences, and assumptions.
- Give useful, direct guidance that is proportionate to the question asked.

Return exactly one self-contained Markdown report using this structure:

# Recommendation

## Reasoning

## Risks and Unknowns

## Suggested Next Steps
EOF

FULL_PROMPT="${FIXED_INSTRUCTION}

--- ADVISORY REQUEST ---

${PROMPT}"

# --- 4. Consult Fable, then persist the report ----------------------------------
# Runs in the current working directory so Fable can inspect the active project.
# --model fable is required; there is intentionally no --fallback-model, so an
# unavailable Fable fails loudly rather than quietly answering as another model.
#
# Permissions (defense in depth):
#   --strict-mcp-config + empty --mcp-config
#                     ignore every MCP server the user has configured, so no MCP
#                     tool reaches Fable at all. This is essential: MCP tools are an
#                     open set inherited from the user's config (this machine has
#                     mutating ones like database run_sql and file delete), and a
#                     name-based deny list cannot enumerate them. Stripping MCP at
#                     the config level closes that hole entirely.
#   --allowedTools    auto-approves only read-only inspection tools.
#   --disallowedTools explicitly denies every modifying, executing, networking, or
#                     delegating built-in tool. A deny rule overrides any allow the
#                     user's own settings.json might grant, so this backstops the
#                     built-in tool surface even under permissive ambient settings.
#
# Output is captured to a temp file first and only moved into place on a successful,
# non-empty run — so a failed or backgrounded consultation never leaves a partial or
# misleading report behind.
OUTDIR="${FABLE_ADVISOR_DIR:-docs/fable}"
REPORT="${OUTDIR}/advisory-$(date +%Y%m%d-%H%M%S).md"
TMP="$(mktemp)"

if claude -p "$FULL_PROMPT" \
     --model fable \
     --strict-mcp-config \
     --mcp-config '{"mcpServers":{}}' \
     --allowedTools Read Grep Glob \
     --disallowedTools Bash Edit Write NotebookEdit WebFetch WebSearch Task Workflow \
     > "$TMP"
then
  if [ -s "$TMP" ]; then
    mkdir -p "$OUTDIR"
    mv "$TMP" "$REPORT"
    printf 'consult-fable.sh: Fable advisory report saved to %s\n' "$REPORT" >&2
    cat "$REPORT"
  else
    rm -f "$TMP"
    echo "consult-fable.sh: Fable returned an empty report; treat the consultation as unavailable." >&2
    exit 1
  fi
else
  status=$?
  rm -f "$TMP"
  echo "consult-fable.sh: the Fable consultation failed (claude exited ${status}); no report was written." >&2
  exit "$status"
fi
