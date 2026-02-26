#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:-macos/.release/output}"
APP_NAME="${2:-LemonNotes}"
DMG_NAME="${3:-LemonNotes-macOS.dmg}"

APP_PATH="${OUTPUT_DIR}/${APP_NAME}.app"
DMG_PATH="${OUTPUT_DIR}/${DMG_NAME}"

if [[ ! -d "${APP_PATH}" ]]; then
  echo "Missing app bundle: ${APP_PATH}"
  exit 1
fi

if [[ ! -f "${DMG_PATH}" ]]; then
  echo "Missing DMG: ${DMG_PATH}"
  exit 1
fi

echo "Verifying app signature..."
codesign --verify --deep --strict --verbose=2 "${APP_PATH}"

echo "Verifying DMG signature..."
codesign --verify --verbose=2 "${DMG_PATH}"

echo "Validating stapled tickets..."
xcrun stapler validate "${APP_PATH}"
xcrun stapler validate "${DMG_PATH}"

echo "SHA256:"
shasum -a 256 "${DMG_PATH}"

echo "Artifacts verified:"
echo "  App: ${APP_PATH}"
echo "  DMG: ${DMG_PATH}"
