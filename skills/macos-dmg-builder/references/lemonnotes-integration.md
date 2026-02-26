# LemonNotes Integration Notes

## Project Paths
- Repo root: `/Users/jakerains/Projects/LemonNotes`
- Release script: `scripts/macos-release.sh`
- Notary setup script: `scripts/macos-notary-setup.sh`
- Make targets:
  - `make macos-notary-setup`
  - `make macos-release`

## Current Defaults
- App name: `LemonNotes`
- Scheme: `LemonNotesMac`
- Release artifact directory: `macos/.release/output`
- Notary profile name: `LemonNotesApp-Notarize`
- Team ID default: `47347VQHQV`

## Operational Commands
- Configure credentials:
  - `make macos-notary-setup`
- Build signed/notarized release:
  - `make macos-release`
- Verify output quickly:
  - `ls -lh macos/.release/output`
  - `shasum -a 256 macos/.release/output/LemonNotes-macOS.dmg`

## Practical Notes
- Run from repo root so Make targets resolve local scripts.
- If DMG signing fails due to duplicate cert names, ensure script resolves signing identity to SHA-1.
- If capture permissions appear denied after enabling in macOS settings, quit/reopen app and refresh sources.
