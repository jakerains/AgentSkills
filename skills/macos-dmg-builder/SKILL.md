---
name: macos-dmg-builder
description: Build, sign, notarize, and package native macOS apps into distributable DMGs. Use when users ask to ship a SwiftUI/AppKit/Xcode macOS app, set up notarytool credentials (Apple ID app-specific password + team ID), scaffold or run release scripts (`make macos-release`), or debug Developer ID/notarization failures.
---

# macOS DMG Builder

## Overview
Use this skill to create a repeatable macOS release pipeline with signed and notarized `.app` and `.dmg` artifacts.

Prefer existing project scripts first. If the project does not already have release automation, scaffold it from `assets/templates/` using the bundled script.

## Onboarding Walkthrough (Mandatory)
Before running release commands, collect or confirm these values. Do not skip this step.

1. `repo_root` (absolute path to target repo)
2. `app_name` (display name of the app in Finder/DMG)
3. `xcode_scheme` (build/archive scheme)
4. `bundle_id` (for entitlement/signing sanity checks)
5. `artifact_dir` (where `.app` and `.dmg` should be written)
6. `team_id` (Apple Developer Team ID)
7. `apple_id` (Apple ID used for notarization)
8. `notary_profile` (Keychain profile name for `notarytool`)
9. `signing_identity` preference (display name or SHA-1 hash)

If any required value is missing, ask focused questions before proceeding. Use defaults only when they are verifiably correct for the repo.

Onboarding defaults for LemonNotes:
- `repo_root`: `/Users/jakerains/Projects/LemonNotes`
- `app_name`: `LemonNotes`
- `xcode_scheme`: `LemonNotesMac`
- `artifact_dir`: `macos/.release/output`
- `team_id`: `47347VQHQV`
- `notary_profile`: `LemonNotesApp-Notarize`

Run preflight checks immediately after onboarding:
- `scripts/preflight_release_env.sh --profile <notary-profile>`

## Workflow

### 1) Detect existing release automation
1. Check for `scripts/macos-release.sh`.
2. Check for `scripts/macos-notary-setup.sh`.
3. Check `Makefile` for `macos-release` and `macos-notary-setup` targets.

### 2) If missing, scaffold release automation
1. Run `scripts/scaffold_release_pipeline.sh --repo <repo-root>`.
2. Add `--apply-makefile` to append targets automatically.
3. Add `--force` only when replacing existing scripts intentionally.

### 3) Configure notary profile (one-time per machine/profile)
1. Run `scripts/setup_notary_profile.sh`.
2. Default profile for LemonNotes is `LemonNotesApp-Notarize`.
3. Use app-specific password input securely (prompt or env var) and never print it in output.

### 4) Run release
1. Run `make macos-release` from repo root.
2. Confirm phases:
- archive
- app notarization/stapling
- DMG creation/signing
- DMG notarization/stapling

### 5) Verify and report
1. Run `scripts/verify_release_artifacts.sh`.
2. Report:
- output paths
- notarization/staple validation status
- SHA256 of DMG

## Credential and Security Rules
- Never echo app-specific passwords to terminal output.
- Prefer prompting interactively for secrets.
- If a user shares a password in chat, use it only for immediate setup and avoid repeating it.
- Prefer app-specific notary profiles (e.g., `LemonNotesApp-Notarize`) over reusing unrelated profile names.

## Troubleshooting Quick Fixes
- Duplicate Developer ID name ambiguity:
  - Resolve to SHA-1 with `security find-identity -v -p codesigning`.
  - Sign with hash identity, not display name.
- Profile not found:
  - Run `scripts/check_notary_profile.sh <profile>`.
  - Run `scripts/setup_notary_profile.sh` if missing.
- Release script exits unexpectedly:
  - Re-run with tracing: `bash -x scripts/macos-release.sh`.
  - Continue from first failing phase.

## LemonNotes Quick Path
1. Run onboarding checklist from `references/onboarding-playbook.md`.
2. Run `make macos-notary-setup`.
3. Run `make macos-release`.
4. Expect artifacts in `macos/.release/output`.

Read `references/lemonnotes-integration.md` for exact LemonNotes defaults and conventions.

## Resources
- `scripts/inspect_signing_identities.sh`: list usable Developer ID identities and suggested exports.
- `scripts/preflight_release_env.sh`: preflight check for tools, certs, and optional notary profile.
- `scripts/check_notary_profile.sh`: validate a notary profile from Keychain.
- `scripts/setup_notary_profile.sh`: create/update notary profile credentials.
- `scripts/scaffold_release_pipeline.sh`: install release/notary scripts into a repo.
- `scripts/verify_release_artifacts.sh`: validate signatures/staples and print DMG hash.
- `references/onboarding-playbook.md`: onboarding interview + zero-to-release checklist.
- `references/workflow.md`: generic release flow and checks.
- `references/lemonnotes-integration.md`: LemonNotes-specific defaults.
- `assets/templates/`: template scripts and Makefile snippet.
