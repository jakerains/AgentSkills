# macOS Release Workflow

## 1) Preflight
- Confirm `xcodebuild`, `xcodegen`, `xcrun`, `codesign`, `hdiutil` are installed.
- Confirm a valid Developer ID Application certificate exists.
- Confirm notary profile exists and can be queried with:
  - `xcrun notarytool history --keychain-profile <profile> --output-format json`

## 2) Signing Identity
- List available identities:
  - `security find-identity -v -p codesigning`
- If duplicate names exist, use SHA-1 identity hashes to avoid ambiguity.

## 3) Notary Profile
- Create/update credentials:
  - `xcrun notarytool store-credentials "<profile>" --apple-id "<apple-id>" --team-id "<team-id>" --password "<app-specific-password>"`
- Use profile names tied to the app or org, not unrelated app names.

## 4) Build and Package
- Archive app in Release with hardened runtime and manual signing.
- Export or copy `.app` from archive output.
- Verify app signature:
  - `codesign --verify --deep --strict --verbose=2 <App>.app`

## 5) Notarize App
- Zip app with `ditto -c -k --keepParent`.
- Submit zip to notary service:
  - `xcrun notarytool submit <App>.zip --keychain-profile <profile> --wait`
- Staple and validate app:
  - `xcrun stapler staple <App>.app`
  - `xcrun stapler validate <App>.app`

## 6) Build and Sign DMG
- Create DMG with app and `/Applications` symlink.
- Sign DMG:
  - `codesign --force --timestamp --options runtime --sign <identity> <App>.dmg`
- Verify signature:
  - `codesign --verify --verbose=2 <App>.dmg`

## 7) Notarize DMG
- Submit DMG:
  - `xcrun notarytool submit <App>.dmg --keychain-profile <profile> --wait`
- Staple and validate DMG:
  - `xcrun stapler staple <App>.dmg`
  - `xcrun stapler validate <App>.dmg`

## 8) Final Reporting
- Output artifact paths.
- Provide DMG SHA256:
  - `shasum -a 256 <App>.dmg`
- Include any warnings and remediation.

## Common Errors
- `... ambiguous (matches ...)` during signing:
  - Use SHA-1 identity hash from `security find-identity`.
- `No Keychain password item found for profile`:
  - Run `store-credentials` for that profile.
- Notary stuck in progress or intermittent failures:
  - Retry submission and keep submission ID in logs.
