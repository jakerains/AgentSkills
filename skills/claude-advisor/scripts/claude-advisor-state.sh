#!/usr/bin/env bash
# Shared state helpers for named Claude Advisor threads.

ADVISOR_OWNED_LOCK_DIRS=()

advisor_project_path() {
  pwd -P
}

advisor_state_root() {
  if [ -n "${CLAUDE_ADVISOR_STATE_DIR:-}" ]; then
    printf '%s\n' "$CLAUDE_ADVISOR_STATE_DIR"
  elif [ "$(uname -s)" = "Darwin" ]; then
    printf '%s\n' "${HOME}/Library/Application Support/ClaudeAdvisor"
  else
    printf '%s\n' "${XDG_STATE_HOME:-${HOME}/.local/state}/claude-advisor"
  fi
}

advisor_validate_thread_name() {
  local name="${1:-}"
  if [[ ! "$name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]]; then
    printf 'claude-advisor: invalid thread name %q; use 1-64 letters, digits, dots, underscores, or hyphens, beginning with a letter or digit.\n' "$name" >&2
    return 2
  fi
}

advisor_project_key() {
  local project_path="${1:?project path required}"
  printf '%s' "$project_path" | shasum -a 256 | awk '{print $1}'
}

advisor_thread_dir() {
  local model="${1:?model required}"
  local project_path
  local project_key
  project_path="$(advisor_project_path)"
  project_key="$(advisor_project_key "$project_path")"
  printf '%s/threads/%s/%s\n' "$(advisor_state_root)" "$project_key" "$model"
}

advisor_thread_file() {
  local model="${1:?model required}"
  local name="${2:?thread name required}"
  printf '%s/%s.json\n' "$(advisor_thread_dir "$model")" "$name"
}

advisor_require_state_file() {
  local file="${1:?state file required}"
  if [ ! -f "$file" ]; then
    printf 'claude-advisor: named thread not found for this project: %s\n' "$file" >&2
    return 1
  fi
  if ! jq -e '.schema_version == 1 and (.session_id | type == "string" and length > 0)' "$file" >/dev/null 2>&1; then
    printf 'claude-advisor: named thread state is invalid: %s\n' "$file" >&2
    return 1
  fi
}

advisor_atomic_write_json() {
  local destination="${1:?destination required}"
  local source="${2:?source required}"
  local destination_dir
  local staged
  destination_dir="$(dirname "$destination")"
  mkdir -p "$destination_dir"
  chmod 700 "$destination_dir"
  staged="$(mktemp "${destination}.tmp.XXXXXX")"
  cp "$source" "$staged"
  chmod 600 "$staged"
  mv "$staged" "$destination"
}

advisor_acquire_lock() {
  local state_file="${1:?state file required}"
  local candidate_lock_dir
  local owner_pid=""
  candidate_lock_dir="${state_file}.lock"
  mkdir -p "$(dirname "$state_file")"
  chmod 700 "$(dirname "$state_file")"

  if mkdir "$candidate_lock_dir" 2>/dev/null; then
    printf '%s\n' "$$" > "$candidate_lock_dir/pid"
    chmod 600 "$candidate_lock_dir/pid"
    ADVISOR_OWNED_LOCK_DIRS[${#ADVISOR_OWNED_LOCK_DIRS[@]}]="$candidate_lock_dir"
    return 0
  fi

  if [ -f "$candidate_lock_dir/pid" ]; then
    owner_pid="$(sed -n '1p' "$candidate_lock_dir/pid")"
  fi
  if [[ "$owner_pid" =~ ^[1-9][0-9]*$ ]] && kill -0 "$owner_pid" 2>/dev/null; then
    printf 'claude-advisor: thread is already in use by process %s; wait for that turn to finish.\n' "$owner_pid" >&2
    return 1
  fi
  printf 'claude-advisor: stale or incomplete thread lock detected; after confirming no turn is running, clear it with advisor-thread.sh unlock: %s\n' "$candidate_lock_dir" >&2
  return 1
}

advisor_release_lock() {
  local lock_dir
  local owner_pid
  if [ "${#ADVISOR_OWNED_LOCK_DIRS[@]}" -eq 0 ]; then
    return 0
  fi
  for lock_dir in "${ADVISOR_OWNED_LOCK_DIRS[@]}"; do
    [ -d "$lock_dir" ] || continue
    owner_pid=""
    if [ -f "$lock_dir/pid" ]; then
      owner_pid="$(sed -n '1p' "$lock_dir/pid")"
    fi
    if [ "$owner_pid" = "$$" ]; then
      rm -f "$lock_dir/pid"
      rmdir "$lock_dir" 2>/dev/null || true
    fi
  done
  ADVISOR_OWNED_LOCK_DIRS=()
}

advisor_recover_thread_state() {
  local state_file="${1:?state file required}"
  local recovery_file="${state_file}.recovery.json"
  local report_path
  [ -f "$recovery_file" ] || return 0

  if ! jq -e '.schema_version == 1 and (.session_id | type == "string" and length > 0) and (.last_report | type == "string" and length > 0)' "$recovery_file" >/dev/null 2>&1; then
    printf 'claude-advisor: pending recovery record is invalid; inspect it before continuing: %s\n' "$recovery_file" >&2
    return 1
  fi
  report_path="$(jq -r '.last_report' "$recovery_file")"
  if [ ! -f "$report_path" ]; then
    printf 'claude-advisor: a prior turn was interrupted before its report was published; inspect the recovery record before continuing: %s\n' "$recovery_file" >&2
    return 1
  fi
  advisor_atomic_write_json "$state_file" "$recovery_file"
  rm -f "$recovery_file"
  printf 'claude-advisor: recovered named-thread state from the previously saved report: %s\n' "$report_path" >&2
}
