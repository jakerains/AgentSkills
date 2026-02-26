#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TEMPLATE_DIR="${SKILL_DIR}/assets/templates"

REPO_ROOT="$(pwd)"
FORCE=0
APPLY_MAKEFILE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_ROOT="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --apply-makefile)
      APPLY_MAKEFILE=1
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

mkdir -p "${REPO_ROOT}/scripts"

copy_template() {
  local src="$1"
  local dest="$2"

  if [[ -f "${dest}" && "${FORCE}" -ne 1 ]]; then
    echo "Skipping existing file: ${dest}"
    return
  fi

  cp "${src}" "${dest}"
  chmod +x "${dest}"
  echo "Wrote: ${dest}"
}

copy_template "${TEMPLATE_DIR}/macos-release.sh.template" "${REPO_ROOT}/scripts/macos-release.sh"
copy_template "${TEMPLATE_DIR}/macos-notary-setup.sh.template" "${REPO_ROOT}/scripts/macos-notary-setup.sh"

if [[ "${APPLY_MAKEFILE}" -eq 1 ]]; then
  if [[ ! -f "${REPO_ROOT}/Makefile" ]]; then
    echo "Makefile not found at ${REPO_ROOT}/Makefile; skipping Makefile update."
  else
    if grep -qE '^macos-release:' "${REPO_ROOT}/Makefile"; then
      echo "Makefile already contains macos-release target."
    else
      {
        echo
        echo "# macOS release automation"
        cat "${TEMPLATE_DIR}/makefile-snippet.mk"
      } >> "${REPO_ROOT}/Makefile"
      echo "Appended macOS release targets to Makefile."
    fi
  fi
else
  echo
  echo "To add Makefile targets, append this snippet:"
  echo "---------------------------------------------"
  cat "${TEMPLATE_DIR}/makefile-snippet.mk"
  echo "---------------------------------------------"
fi
