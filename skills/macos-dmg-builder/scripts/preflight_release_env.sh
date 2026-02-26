#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: preflight_release_env.sh [--profile <notary-profile>]

Checks:
  - Required CLIs exist
  - Developer ID Application signing identities are available
  - Optional notary profile can be queried
EOF
}

PROFILE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

echo "== macOS Release Preflight =="

MISSING=0
for cmd in xcodebuild xcodegen xcrun codesign hdiutil security; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "ok: $cmd"
  else
    echo "missing: $cmd"
    MISSING=1
  fi
done

if [[ "$MISSING" -ne 0 ]]; then
  echo ""
  echo "One or more required tools are missing." >&2
  exit 1
fi

echo ""
echo "== Signing Identities =="
IDENTITIES_RAW="$(security find-identity -v -p codesigning || true)"
DEV_ID_LINES="$(printf "%s\n" "$IDENTITIES_RAW" | grep "Developer ID Application" || true)"

if [[ -z "$DEV_ID_LINES" ]]; then
  echo "No 'Developer ID Application' identity found." >&2
  exit 1
fi

printf "%s\n" "$DEV_ID_LINES"
echo ""
echo "Tip: if duplicate names exist, sign using SHA-1 hash identity."

if [[ -n "$PROFILE" ]]; then
  echo ""
  echo "== Notary Profile Check =="
  if "$SCRIPT_DIR/check_notary_profile.sh" "$PROFILE" >/dev/null 2>&1; then
    echo "ok: profile '$PROFILE' is configured and queryable."
  else
    echo "profile check failed for '$PROFILE'." >&2
    echo "Run: $SCRIPT_DIR/setup_notary_profile.sh \"$PROFILE\"" >&2
    exit 1
  fi
else
  echo ""
  echo "No profile provided; skipping notary profile check."
  echo "Use --profile <name> to verify credentials."
fi

echo ""
echo "Preflight complete."
