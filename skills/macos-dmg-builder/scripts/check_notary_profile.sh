#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-${MACOS_NOTARY_PROFILE:-${NOTARY_PROFILE:-}}}"

if [[ -z "${PROFILE}" ]]; then
  echo "Usage: $0 <notary-profile>"
  echo "Or set MACOS_NOTARY_PROFILE."
  exit 1
fi

if xcrun notarytool history --keychain-profile "${PROFILE}" --output-format json >/dev/null 2>&1; then
  echo "Notary profile '${PROFILE}' is configured and valid."
  exit 0
fi

echo "Notary profile '${PROFILE}' is missing or invalid."
exit 2
