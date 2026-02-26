# Onboarding Playbook (Step-by-Step)

Use this checklist at the start of every new project or machine.

## 1) Interview (Required Inputs)
Collect these values before running release commands:

1. Repo root path (absolute)
2. App name
3. Xcode scheme
4. Bundle identifier
5. Artifact output directory
6. Apple Developer Team ID
7. Apple ID for notarization
8. Notary Keychain profile name
9. Preferred signing identity (name or SHA-1 hash)

If a value is unknown:
- Ask one focused question.
- Offer likely defaults discovered from project files.
- Confirm before writing scripts or running notarization commands.

## 2) Detect Existing Automation
From repo root, check:
- `scripts/macos-release.sh`
- `scripts/macos-notary-setup.sh`
- `Makefile` targets: `macos-release`, `macos-notary-setup`

If missing, scaffold:
```bash
/Users/jakerains/.agents/skills/macos-dmg-builder/scripts/scaffold_release_pipeline.sh --repo "<repo-root>" --apply-makefile
```

## 3) Run Preflight
Run tool and credential checks:
```bash
/Users/jakerains/.agents/skills/macos-dmg-builder/scripts/preflight_release_env.sh --profile "<notary-profile>"
```

Expected outcome:
- Required CLI tools found
- At least one valid `Developer ID Application` identity
- Optional profile validity check passes (if profile provided)

## 4) Configure Notary Profile
If profile does not exist:
```bash
/Users/jakerains/.agents/skills/macos-dmg-builder/scripts/setup_notary_profile.sh "<profile-name>"
```

Then verify:
```bash
/Users/jakerains/.agents/skills/macos-dmg-builder/scripts/check_notary_profile.sh "<profile-name>"
```

## 5) Build + Notarize Release
From repo root:
```bash
make macos-release
```

## 6) Validate Artifacts
```bash
/Users/jakerains/.agents/skills/macos-dmg-builder/scripts/verify_release_artifacts.sh
```

Report:
- Output artifact paths
- Stapler validation result for `.app` and `.dmg`
- SHA256 for `.dmg`

## 7) Failure Recovery
- Identity ambiguity:
  - Use SHA-1 from `security find-identity -v -p codesigning`
- Missing notary profile:
  - Re-run setup script, then check script
- Unknown release failure:
  - `bash -x scripts/macos-release.sh`
  - Resume from the first failing phase
