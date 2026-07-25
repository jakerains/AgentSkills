#!/usr/bin/env bash
# Default Opus advisor lane. The rolling alias follows the latest Opus release.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/consult-claude-model.sh" opus "$@"
