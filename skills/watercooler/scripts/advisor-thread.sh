#!/usr/bin/env bash
# Inspect or retire named Claude Advisor threads for the current project.

set -euo pipefail
umask 077

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=claude-advisor-state.sh
source "$SCRIPT_DIR/claude-advisor-state.sh"

usage() {
  cat >&2 <<'EOF'
usage:
  bash scripts/advisor-thread.sh list
  bash scripts/advisor-thread.sh show opus|fable <thread-name>
  bash scripts/advisor-thread.sh close opus|fable <thread-name>
  bash scripts/advisor-thread.sh unlock opus|fable <thread-name>

Commands operate only on threads bound to the current project directory. Closing a
thread retires the advisor binding without deleting Claude's native transcript.
Unlock only after an interrupted process left a stale lock and no turn is running.
EOF
  exit 2
}

COMMAND="${1:-}"
case "$COMMAND" in
  list)
    [ "$#" -eq 1 ] || usage
    found=0
    for model in opus fable; do
      thread_dir="$(advisor_thread_dir "$model")"
      [ -d "$thread_dir" ] || continue
      while IFS= read -r file; do
        [ -n "$file" ] || continue
        found=1
        jq -r '[.model, .name, .status, (.turn_count | tostring), .updated_at] | @tsv' "$file"
      done < <(find "$thread_dir" -maxdepth 1 -type f -name '*.json' ! -name '*.recovery.json' -print | sort)
    done
    if [ "$found" -eq 0 ]; then
      printf 'No named Claude Advisor threads are recorded for %s.\n' "$(advisor_project_path)"
    fi
    ;;
  show|close|unlock)
    [ "$#" -eq 3 ] || usage
    MODEL="$2"
    NAME="$3"
    case "$MODEL" in opus|fable) ;; *) usage ;; esac
    advisor_validate_thread_name "$NAME"
    STATE_FILE="$(advisor_thread_file "$MODEL" "$NAME")"
    if [ "$COMMAND" = "unlock" ]; then
      LOCK_DIR="${STATE_FILE}.lock"
      if [ ! -d "$LOCK_DIR" ]; then
        printf 'claude-advisor: no lock exists for %s/%s.\n' "$MODEL" "$NAME"
        exit 0
      fi
      owner_pid=""
      if [ -f "$LOCK_DIR/pid" ]; then
        owner_pid="$(sed -n '1p' "$LOCK_DIR/pid")"
      fi
      if [[ "$owner_pid" =~ ^[1-9][0-9]*$ ]] && kill -0 "$owner_pid" 2>/dev/null; then
        printf 'claude-advisor: refusing to unlock %s/%s because process %s is still running.\n' "$MODEL" "$NAME" "$owner_pid" >&2
        exit 1
      fi
      rm -f "$LOCK_DIR/pid"
      if ! rmdir "$LOCK_DIR"; then
        printf 'claude-advisor: could not clear lock safely; inspect it manually: %s\n' "$LOCK_DIR" >&2
        exit 1
      fi
      printf 'claude-advisor: cleared stale lock for %s/%s.\n' "$MODEL" "$NAME"
      exit 0
    fi
    if [ "$COMMAND" = "show" ]; then
      advisor_require_state_file "$STATE_FILE"
      jq . "$STATE_FILE"
      exit 0
    fi
    JSON_TMP=""
    cleanup() {
      advisor_release_lock
      if [ -n "${JSON_TMP:-}" ]; then rm -f "$JSON_TMP"; fi
    }
    trap cleanup EXIT INT TERM
    advisor_acquire_lock "$STATE_FILE"
    advisor_recover_thread_state "$STATE_FILE"
    advisor_require_state_file "$STATE_FILE"
    if [ "$(jq -r '.status' "$STATE_FILE")" = "closed" ]; then
      printf 'claude-advisor: thread %s/%s is already closed.\n' "$MODEL" "$NAME" >&2
      exit 0
    fi
    JSON_TMP="$(mktemp)"
    now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    jq --arg now "$now" '.status = "closed" | .closed_at = $now | .updated_at = $now' "$STATE_FILE" > "$JSON_TMP"
    advisor_atomic_write_json "$STATE_FILE" "$JSON_TMP"
    printf 'claude-advisor: closed %s thread %s for %s; Claude transcript was not deleted.\n' "$MODEL" "$NAME" "$(advisor_project_path)"
    ;;
  *)
    usage
    ;;
esac
