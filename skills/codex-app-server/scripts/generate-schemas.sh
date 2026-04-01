#!/usr/bin/env bash
set -euo pipefail

if ! command -v codex >/dev/null 2>&1; then
  echo "codex CLI not found on PATH" >&2
  exit 1
fi

OUT_DIR="${1:-./schemas}"
TS_DIR="$OUT_DIR/typescript"
JSON_SCHEMA_DIR="$OUT_DIR/json-schema"

mkdir -p "$TS_DIR" "$JSON_SCHEMA_DIR"

codex app-server generate-ts --out "$TS_DIR"
codex app-server generate-json-schema --out "$JSON_SCHEMA_DIR"

echo "Generated Codex App Server schemas in:"
echo "  $TS_DIR"
echo "  $JSON_SCHEMA_DIR"
