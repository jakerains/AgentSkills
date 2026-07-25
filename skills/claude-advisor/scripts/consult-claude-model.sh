#!/usr/bin/env bash
# Internal hardened runner. Public callers use consult-opus.sh or consult-fable.sh.

set -euo pipefail

if ! command -v claude >/dev/null 2>&1; then
  cat >&2 <<'ERR'
claude-advisor: error — the `claude` CLI was not found on PATH.

Install Claude Code and ensure `claude` is on PATH, then retry. This skill does not
install or configure Claude Code itself.
ERR
  exit 127
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "claude-advisor: error — jq is required to verify the responding model and extract the report." >&2
  exit 127
fi

if [ "$#" -lt 1 ]; then
  echo "claude-advisor: internal error — no model lane was supplied." >&2
  exit 2
fi

MODEL="$1"
shift

case "$MODEL" in
  opus)
    DISPLAY_NAME="Opus"
    LANE_NAME="general expert review and synthesis"
    LANE_INSTRUCTION="Act as a rigorous general expert advisor. Determine the strongest answer, whether that requires adversarially reviewing an existing candidate or synthesizing a recommendation from unsettled evidence. Pressure-test assumptions, seek counterexamples and failure modes, identify contradictions and hidden coupling, weigh human and technical outcomes, distinguish blockers from preferences, and recommend the highest-value corrections or direction."
    OUTDIR="${OPUS_ADVISOR_DIR:-docs/opus}"
    REPORT_PREFIX="advisory"
    ;;
  fable)
    DISPLAY_NAME="Fable"
    LANE_NAME="frontier synthesis"
    LANE_INSTRUCTION="Use unusually deep, integrative synthesis for this exceptional and genuinely unsettled question. Reconcile competing system models, subtle human or technical outcomes, ambiguous high-stakes judgment, and consequential tradeoffs. Look across the relevant system, expose the assumptions behind plausible alternatives, and focus the extra depth on what could materially change the decision."
    OUTDIR="${FABLE_ADVISOR_DIR:-docs/fable}"
    REPORT_PREFIX="advisory"
    ;;
  *)
    echo "claude-advisor: internal error — unsupported model lane: $MODEL" >&2
    exit 2
    ;;
esac

PROMPT="$*"
if [ "$#" -eq 0 ] || [ -z "${PROMPT//[[:space:]]/}" ]; then
  cat >&2 <<ERR
usage: consult-${MODEL}.sh "<advisor prompt>"

Pass one focused prompt describing the substantive judgment, artifact, decision,
bug, design, or plan you want ${DISPLAY_NAME} to examine. Include the intended
human or technical outcome, the relevant files, and explicit out-of-scope topics.
ERR
  exit 2
fi

read -r -d '' FIXED_INSTRUCTION <<EOF || true
You are an independent, read-only senior staff-level advisor operating in the ${DISPLAY_NAME} ${LANE_NAME} lane.

${LANE_INSTRUCTION}

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
- Prioritize the substantive judgment requested: content, learning, product, strategy, design, architecture, technical behavior, debugging, or tradeoffs.
- Do not substitute a routine procedural audit for that judgment. Treat hashes, approval records, release gates, reviewer assignments, paperwork freshness, checklist completion, and other mechanically decidable compliance details as out of scope unless the advisory request explicitly asks for them or they materially change safety, correctness, human experience, or the substantive decision.

Return exactly one self-contained Markdown report using this structure:

# Recommendation

## Reasoning

## Risks and Unknowns

## Suggested Next Steps
EOF

FULL_PROMPT="${FIXED_INSTRUCTION}

--- ADVISORY REQUEST ---

${PROMPT}"

REPORT="${OUTDIR}/${REPORT_PREFIX}-$(date +%Y%m%d-%H%M%S)-$$.md"
REPORT_TMP="$(mktemp)"
JSON_TMP="$(mktemp)"

cleanup() {
  if [ -n "${REPORT_TMP:-}" ]; then rm -f "$REPORT_TMP"; fi
  if [ -n "${JSON_TMP:-}" ]; then rm -f "$JSON_TMP"; fi
}
trap cleanup EXIT INT TERM

# MODEL is restricted by the closed case statement. Both names are rolling Claude
# Code aliases; there is intentionally no fallback model.
if claude -p "$FULL_PROMPT" \
     --model "$MODEL" \
     --output-format json \
     --no-session-persistence \
     --strict-mcp-config \
     --mcp-config '{"mcpServers":{}}' \
     --tools 'Read,Grep,Glob' \
     --allowedTools Read Grep Glob \
     --disallowedTools Bash BashOutput KillShell Edit Write NotebookEdit WebFetch WebSearch Task Workflow SlashCommand TodoWrite \
     > "$JSON_TMP"
then
  if ! jq -e '.type == "result" and .subtype == "success" and .is_error == false and (.result | type == "string" and length > 0)' "$JSON_TMP" >/dev/null; then
    printf 'claude-advisor: %s returned an invalid or empty structured result; treat the consultation as unavailable.\n' "$DISPLAY_NAME" >&2
    exit 1
  fi

  if ! jq -e --arg prefix "claude-${MODEL}-" '.modelUsage | keys | any(startswith($prefix))' "$JSON_TMP" >/dev/null; then
    printf 'claude-advisor: model verification failed; requested %s but the structured response did not identify a matching model. No report was accepted.\n' "$MODEL" >&2
    exit 1
  fi
  RESOLVED_MODEL="$(jq -r --arg prefix "claude-${MODEL}-" '.modelUsage | keys | map(select(startswith($prefix))) | first' "$JSON_TMP")"

  jq -r '.result' "$JSON_TMP" > "$REPORT_TMP"
  if [ ! -s "$REPORT_TMP" ]; then
    printf 'claude-advisor: %s returned an empty report; treat the consultation as unavailable.\n' "$DISPLAY_NAME" >&2
    exit 1
  fi

  cat "$REPORT_TMP"
  if mkdir -p "$OUTDIR" && mv "$REPORT_TMP" "$REPORT"; then
    REPORT_TMP=""
    printf 'claude-advisor: verified %s (%s) %s report saved to %s\n' "$DISPLAY_NAME" "$RESOLVED_MODEL" "$LANE_NAME" "$REPORT" >&2
  else
    SURVIVING_REPORT="$REPORT_TMP"
    REPORT_TMP=""
    printf 'claude-advisor: warning — the verified %s report was delivered above but could not be saved to %s. The temporary report remains at %s.\n' "$DISPLAY_NAME" "$REPORT" "$SURVIVING_REPORT" >&2
  fi
else
  status=$?
  printf 'claude-advisor: the %s consultation failed (claude exited %s); no report was written.\n' "$DISPLAY_NAME" "$status" >&2
  exit "$status"
fi
