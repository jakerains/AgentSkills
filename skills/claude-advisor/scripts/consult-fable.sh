#!/usr/bin/env bash
# Explicit Fable 5.1 frontier-advisory lane. This wrapper never selects another model.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/consult-claude-model.sh" fable "$@"
