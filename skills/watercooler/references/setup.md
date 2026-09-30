# Setup and verification

## Skill-only direct mode

Install this one source package in both agents through the skills CLI when the
owner requests installation. Installing the skill does not install Claude, Codex,
their credentials, service binaries, hooks, or a login item. Direct messages use
Python 3.10+ and authenticated agent CLIs. Advice additionally uses bash and jq.
The guarded Claude courier and agreement locks target macOS/Linux; native Windows
is not qualified. The Codex queue command must exist in the installed CLI.

## Optional service without the app

The existing WaterCooler repository is a separate runtime dependency. Use an
owner-supplied checkout; this skill does not assume a public distribution or
auto-download a binary. On the development machine the runtime lives in
`/Users/jakerains/Projects/WaterCooler`; that path is not portable to other users.

Build and inspect its commands from that checkout on a supported macOS/Swift
toolchain; its design currently targets macOS 26+ and Swift tools 6.2+:

```bash
swift build --package-path Packages/WaterCoolerKit
Packages/WaterCoolerKit/.build/debug/wc-server --real-transports
```

The foreground server persists tickets and serves the CLI. `--real-transports`
is essential: the development default uses no-op transports. Keep the server
running during collaboration; the app can host the same service if preferred.
Expose the built `watercooler` binary on PATH through an owner-authorized setup.
Do not silently register a background/login service.

Hooks must register the native sessions and observe their turns. The runtime's
installer merges and backs up configuration. Preview each harness first using
the actual absolute built CLI, hook script, and **this skill's directory**:

```bash
Packages/WaterCoolerKit/.build/debug/wc-server install --harness claude \
  --cli '/absolute/runtime/Packages/WaterCoolerKit/.build/debug/watercooler' \
  --hook-script '/absolute/runtime/Adapters/hooks/wc-hook.sh' \
  --skill-dir '/absolute/AgentSkills/skills/watercooler' --dry-run
# Repeat for --harness codex. Apply only within an explicit installation request.
```

The current runtime installer can replace its own older WaterCooler adapter;
passing this skill directory selects the unified edition. Do not manually forge
Codex hook trust. The owner must review/trust/enable the installed hooks through
Codex `/hooks`; installation alone is not readiness. Then run the service Doctor
and confirm identities in both native conversations.

Live Claude push and stopped-session resume are optional room settings. The
service defaults do not guarantee immediate wake-up. Enable those behaviors only
within the owner's requested setup, using the runtime's supported settings/API.
Never start a second resume of a live target. This source package does not
implement remote pairing or remove receiver permission boundaries.

## Evidence and validation

The reused Claude transport was qualified on macOS against Claude 2.1.263. The
WaterCooler runtime's September 9 acceptance record used Claude 2.1.266/Codex
0.153.4; queue-and-resume round trips passed, while its live interactive courier
remained a manual check. Do not present that historical evidence as qualification
of new versions or an installed user's environment. Current local CLI help on
September 29 exposes Claude 2.1.284 messaging/discovery flags and Codex 0.157.0
queue with exact session names.

Run deterministic tests without messaging real work sessions:

```bash
python3 -m unittest discover -s "$SKILL_DIR/scripts" -p 'test_*.py'
python3 "$SKILL_DIR/scripts/watercooler.py" doctor
```

For runtime qualification, use its isolated acceptance harness and disposable
native sessions. Require a receiver-generated marker returned to the sender.
Sender receipts, fixture tests, hook capture, and actual completed work establish
different facts. Keep live test messages away from unrelated owner conversations.

Official interfaces: [Claude hooks](https://code.claude.com/docs/en/hooks),
[Claude cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging),
[Codex plugin hook trust](https://developers.openai.com/plugins/build/plugins).
