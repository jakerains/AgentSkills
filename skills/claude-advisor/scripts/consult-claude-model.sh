#!/usr/bin/env bash
# Internal hardened runner. Public callers use consult-opus.sh or consult-fable.sh.

set -euo pipefail
umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=claude-advisor-state.sh
source "$SCRIPT_DIR/claude-advisor-state.sh"

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

MODE="oneshot"
THREAD_NAME=""
SOURCE_THREAD_NAME=""

case "${1:-}" in
  --start-thread)
    [ "$#" -ge 3 ] || {
      printf 'usage: consult-%s.sh --start-thread <name> "<advisor prompt>"\n' "$MODEL" >&2
      exit 2
    }
    MODE="start"
    THREAD_NAME="$2"
    shift 2
    ;;
  --continue-thread)
    [ "$#" -ge 3 ] || {
      printf 'usage: consult-%s.sh --continue-thread <name> "<advisor prompt>"\n' "$MODEL" >&2
      exit 2
    }
    MODE="continue"
    THREAD_NAME="$2"
    shift 2
    ;;
  --fork-thread)
    [ "$#" -ge 4 ] || {
      printf 'usage: consult-%s.sh --fork-thread <source-name> <new-name> "<advisor prompt>"\n' "$MODEL" >&2
      exit 2
    }
    MODE="fork"
    SOURCE_THREAD_NAME="$2"
    THREAD_NAME="$3"
    shift 3
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

STATE_FILE=""
SOURCE_STATE_FILE=""
SESSION_ID=""
PARENT_REPORT=""
TURN_NUMBER=0
MAX_THREAD_TURNS="${CLAUDE_ADVISOR_MAX_THREAD_TURNS:-6}"

if [[ ! "$MAX_THREAD_TURNS" =~ ^[1-9][0-9]*$ ]]; then
  printf 'claude-advisor: CLAUDE_ADVISOR_MAX_THREAD_TURNS must be a positive integer.\n' >&2
  exit 2
fi

REPORT_TMP=""
JSON_TMP=""
STATE_TMP=""

cleanup() {
  advisor_release_lock
  if [ -n "${REPORT_TMP:-}" ]; then rm -f "$REPORT_TMP"; fi
  if [ -n "${JSON_TMP:-}" ]; then rm -f "$JSON_TMP"; fi
  if [ -n "${STATE_TMP:-}" ]; then rm -f "$STATE_TMP"; fi
}
trap cleanup EXIT INT TERM

case "$MODE" in
  start)
    advisor_validate_thread_name "$THREAD_NAME"
    STATE_FILE="$(advisor_thread_file "$MODEL" "$THREAD_NAME")"
    advisor_acquire_lock "$STATE_FILE"
    advisor_recover_thread_state "$STATE_FILE"
    if [ -e "$STATE_FILE" ]; then
      printf 'claude-advisor: thread %s/%s already exists for this project; use --continue-thread or choose a new name.\n' "$MODEL" "$THREAD_NAME" >&2
      exit 1
    fi
    TURN_NUMBER=1
    ;;
  continue)
    advisor_validate_thread_name "$THREAD_NAME"
    STATE_FILE="$(advisor_thread_file "$MODEL" "$THREAD_NAME")"
    advisor_acquire_lock "$STATE_FILE"
    advisor_recover_thread_state "$STATE_FILE"
    advisor_require_state_file "$STATE_FILE"
    if [ "$(jq -r '.status' "$STATE_FILE")" != "active" ]; then
      printf 'claude-advisor: thread %s/%s is closed; start a new thread or fork it under a new name.\n' "$MODEL" "$THREAD_NAME" >&2
      exit 1
    fi
    prior_turn_count="$(jq -r '.turn_count' "$STATE_FILE")"
    if [ "$prior_turn_count" -ge "$MAX_THREAD_TURNS" ]; then
      printf 'claude-advisor: thread %s/%s reached its %s-turn budget; close it or fork/start a new bounded thread.\n' "$MODEL" "$THREAD_NAME" "$MAX_THREAD_TURNS" >&2
      exit 1
    fi
    SESSION_ID="$(jq -r '.session_id' "$STATE_FILE")"
    PARENT_REPORT="$(jq -r '.last_report // ""' "$STATE_FILE")"
    TURN_NUMBER=$((prior_turn_count + 1))
    ;;
  fork)
    advisor_validate_thread_name "$SOURCE_THREAD_NAME"
    advisor_validate_thread_name "$THREAD_NAME"
    SOURCE_STATE_FILE="$(advisor_thread_file "$MODEL" "$SOURCE_THREAD_NAME")"
    STATE_FILE="$(advisor_thread_file "$MODEL" "$THREAD_NAME")"
    advisor_acquire_lock "$STATE_FILE"
    advisor_acquire_lock "$SOURCE_STATE_FILE"
    advisor_recover_thread_state "$STATE_FILE"
    advisor_recover_thread_state "$SOURCE_STATE_FILE"
    advisor_require_state_file "$SOURCE_STATE_FILE"
    if [ -e "$STATE_FILE" ]; then
      printf 'claude-advisor: target thread %s/%s already exists; choose a new name.\n' "$MODEL" "$THREAD_NAME" >&2
      exit 1
    fi
    SESSION_ID="$(jq -r '.session_id' "$SOURCE_STATE_FILE")"
    PARENT_REPORT="$(jq -r '.last_report // ""' "$SOURCE_STATE_FILE")"
    TURN_NUMBER=1
    ;;
esac

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
- On a resumed or forked thread, reassess the evidence independently. Do not endorse the consulting agent's accumulated framing merely because it has been repeated across turns.
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

if [ "$MODE" = "oneshot" ]; then
  REPORT="${OUTDIR}/${REPORT_PREFIX}-$(date +%Y%m%d-%H%M%S)-$$.md"
else
  REPORT="${OUTDIR}/${REPORT_PREFIX}-${THREAD_NAME}-turn-$(printf '%02d' "$TURN_NUMBER")-$(date +%Y%m%d-%H%M%S)-$$.md"
fi
REPORT_TMP="$(mktemp)"
JSON_TMP="$(mktemp)"
STATE_TMP="$(mktemp)"

# MODEL is restricted by the closed case statement. Both names are rolling Claude
# Code aliases; there is intentionally no fallback model.
CLAUDE_ARGS=(
  -p "$FULL_PROMPT"
  --model "$MODEL"
  --output-format json
  --restricted
  --strict-mcp-config
  --mcp-config '{"mcpServers":{}}'
  --tools 'Read,Grep,Glob'
  --allowedTools Read Grep Glob
  --disallowedTools Bash BashOutput KillShell Edit Write NotebookEdit WebFetch WebSearch Task Workflow SlashCommand TodoWrite
)

case "$MODE" in
  oneshot)
    CLAUDE_ARGS+=(--no-session-persistence)
    ;;
  start)
    CLAUDE_ARGS+=(--name "claude-advisor:${MODEL}:${THREAD_NAME}")
    ;;
  continue)
    CLAUDE_ARGS+=(--resume "$SESSION_ID")
    ;;
  fork)
    CLAUDE_ARGS+=(--resume "$SESSION_ID" --fork-session --name "claude-advisor:${MODEL}:${THREAD_NAME}")
    ;;
esac

if claude "${CLAUDE_ARGS[@]}" > "$JSON_TMP"
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

  if [ "$MODE" != "oneshot" ] && ! jq -e '.session_id | type == "string" and length > 0' "$JSON_TMP" >/dev/null; then
    printf 'claude-advisor: %s did not return a resumable session ID; no named-thread state or report was accepted.\n' "$DISPLAY_NAME" >&2
    exit 1
  fi

  jq -r '.result' "$JSON_TMP" > "$REPORT_TMP"
  if [ ! -s "$REPORT_TMP" ]; then
    printf 'claude-advisor: %s returned an empty report; treat the consultation as unavailable.\n' "$DISPLAY_NAME" >&2
    exit 1
  fi

  if [ "$MODE" != "oneshot" ]; then
    NEW_SESSION_ID="$(jq -r '.session_id' "$JSON_TMP")"
    project_path="$(advisor_project_path)"
    {
      printf '\n\n---\n\n## Claude Advisor Thread\n\n'
      printf -- '- Advisor binding: `%s/%s`\n' "$MODEL" "$THREAD_NAME"
      printf -- '- Turn: `%s` of `%s` maximum\n' "$TURN_NUMBER" "$MAX_THREAD_TURNS"
      printf -- '- Claude session ID: `%s`\n\n' "$NEW_SESSION_ID"
      printf '**Private local metadata:** remove this footer before committing, publishing, or sharing the report.\n\n'
      printf 'Resume the same native Claude conversation in Terminal:\n\n```bash\n'
      printf 'cd %q && claude --resume %q\n' "$project_path" "$NEW_SESSION_ID"
      printf '```\n\n'
      printf 'That direct Terminal session uses its own interactive permissions, and its turns are not saved as advisor reports or counted in this binding. To preserve the advisor lane'
      printf ' and reapply its read-only restrictions, continue through the wrapper:\n\n```bash\n'
      printf 'cd %q && bash %q --continue-thread %q '\
        "$project_path" "$SCRIPT_DIR/consult-${MODEL}.sh" "$THREAD_NAME"
      printf '%s\n' "'<focused follow-up>'"
      printf '```\n\nDo not resume this session from Terminal while an advisor wrapper turn is running.\n'
    } >> "$REPORT_TMP"
  fi

  RECOVERY_FILE=""
  if [ "$MODE" != "oneshot" ]; then
    now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    if [ "$MODE" = "continue" ]; then
      jq \
        --arg now "$now" \
        --arg session_id "$NEW_SESSION_ID" \
        --arg report "$REPORT" \
        --arg parent "$PARENT_REPORT" \
        --argjson turn "$TURN_NUMBER" \
        '.session_id = $session_id
         | .turn_count = $turn
         | .last_report = $report
         | .updated_at = $now
         | .turns += [{turn: $turn, at: $now, report: $report, parent_report: (if $parent == "" then null else $parent end)}]' \
        "$STATE_FILE" > "$STATE_TMP"
    else
      jq -n \
        --arg model "$MODEL" \
        --arg name "$THREAD_NAME" \
        --arg project_path "$project_path" \
        --arg session_id "$NEW_SESSION_ID" \
        --arg report "$REPORT" \
        --arg parent "$PARENT_REPORT" \
        --arg source_thread "$SOURCE_THREAD_NAME" \
        --arg now "$now" \
        '{schema_version: 1, model: $model, name: $name, project_path: $project_path,
          session_id: $session_id, status: "active", turn_count: 1,
          created_at: $now, updated_at: $now, last_report: $report,
          forked_from: (if $source_thread == "" then null else $source_thread end),
          turns: [{turn: 1, at: $now, report: $report,
                   parent_report: (if $parent == "" then null else $parent end)}]}' > "$STATE_TMP"
    fi
    RECOVERY_FILE="${STATE_FILE}.recovery.json"
    advisor_atomic_write_json "$RECOVERY_FILE" "$STATE_TMP"
  fi

  if mkdir -p "$OUTDIR" && mv "$REPORT_TMP" "$REPORT"; then
    REPORT_TMP=""
    if [ "$MODE" != "oneshot" ]; then
      if ! advisor_atomic_write_json "$STATE_FILE" "$STATE_TMP"; then
        cat "$REPORT"
        printf 'claude-advisor: warning — the verified report was saved, but binding state could not be advanced. Recovery will be attempted from %s on the next thread operation.\n' "$RECOVERY_FILE" >&2
        exit 1
      fi
      rm -f "$RECOVERY_FILE"
    fi
    cat "$REPORT"
    if [ "$MODE" = "oneshot" ]; then
      printf 'claude-advisor: verified %s (%s) %s report saved to %s\n' "$DISPLAY_NAME" "$RESOLVED_MODEL" "$LANE_NAME" "$REPORT" >&2
    else
      printf 'claude-advisor: verified %s (%s) thread %s turn %s/%s saved to %s\n' "$DISPLAY_NAME" "$RESOLVED_MODEL" "$THREAD_NAME" "$TURN_NUMBER" "$MAX_THREAD_TURNS" "$REPORT" >&2
    fi
  else
    if [ -n "$RECOVERY_FILE" ]; then rm -f "$RECOVERY_FILE"; fi
    SURVIVING_REPORT="$REPORT_TMP"
    REPORT_TMP=""
    cat "$SURVIVING_REPORT"
    printf 'claude-advisor: warning — the verified %s report was delivered above but could not be saved to %s. The temporary report remains at %s; named-thread state was not advanced.\n' "$DISPLAY_NAME" "$REPORT" "$SURVIVING_REPORT" >&2
    if [ "$MODE" != "oneshot" ]; then
      exit 1
    fi
  fi
else
  status=$?
  printf 'claude-advisor: the %s consultation failed (claude exited %s); no report was written.\n' "$DISPLAY_NAME" "$status" >&2
  exit "$status"
fi
