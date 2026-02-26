#!/usr/bin/env bash
set -euo pipefail

matches="$(security find-identity -v -p codesigning | awk '/Developer ID Application:/ {print}')"

if [[ -z "${matches}" ]]; then
  echo "No Developer ID Application identities found."
  exit 1
fi

echo "Developer ID Application identities:"
echo "${matches}"

action_line="$(echo "${matches}" | head -n1 | sed -E 's/^[[:space:]]*[0-9]+\)[[:space:]]*//')"
sha="$(echo "${action_line}" | awk '{print $1}')"
name="$(echo "${action_line}" | sed -E 's/^[A-Fa-f0-9]{40}[[:space:]]+"(.*)"$/\1/')"
team_id="$(echo "${name}" | sed -nE 's/.*\(([A-Z0-9]{10})\)$/\1/p')"

echo
echo "Suggested exports:"
echo "export MACOS_APP_SIGN_IDENTITY=\"${name}\""
if [[ -n "${team_id}" ]]; then
  echo "export MACOS_TEAM_ID=\"${team_id}\""
fi
echo
echo "If cert name is ambiguous, use SHA-1 directly:"
echo "export MACOS_APP_SIGN_IDENTITY=\"${sha}\""
