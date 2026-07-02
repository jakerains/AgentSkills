---
name: prompt-scheduler
description: Schedule local AI agent terminal prompts to run later from the user's machine. Use whenever the user wants to run a Claude, Codex, Warp agent, or other terminal command at a specific local time, especially when usage limits reset, a laptop must run the job locally, a command must open in Warp, or the prompt needs tags/names for tracking. Creates macOS launchd one-time jobs, Warp .command launchers, logs, verification steps, and cleanup based on the system's current local time.
---

# prompt-scheduler

Schedule a one-time local agent prompt or terminal command from the user's machine, with a bias toward the macOS + Warp workflow that keeps interactive Claude/Codex sessions visible.

## Default workflow

1. **Confirm the scheduling intent from the prompt.**
   - Extract the exact command to run. Preserve quoting exactly when the user gives a command.
   - Extract the target time and timezone. Use the system's current local time as the default reference.
   - Extract the working directory. If the user says "this repo", "current directory", or leaves it implicit, use the active shell `pwd`.
   - Extract optional tags such as `fable`, `content`, `enterprise`, `codex`, or `resume`; tags become stable job names, file names, and labels.
2. **Choose the run surface.**
   - Use `--app Warp` by default when the command is interactive or the user wants to see it in Warp.
   - Use direct launchd execution only for non-interactive commands that do not need a terminal UI.
   - Do not schedule cloud agents when the user says it must run locally, depends on local usage limits, or needs the local filesystem/session.
3. **Use the bundled script for setup.**
   - Run `scripts/prompt_scheduler.py schedule ...` from this skill directory.
   - The script creates missing local folders, writes an executable `.command` file, writes a launchd wrapper, installs a one-time LaunchAgent, loads it with `launchctl`, and prints a verification summary.
4. **Verify before handing off.**
   - Confirm `launchctl` shows `state = not running`, `runs = 0`, and the expected calendar interval.
   - Confirm the `.command` file and wrapper are executable.
   - Confirm log directories are writable.
5. **Explain the practical nuance.**
   - Opening in Warp via `.command` is reliable for a visible interactive session.
   - It will open a Warp tab/window, not inject into the exact already-open conversation block.
   - The machine must be awake and logged in for GUI app opening. If the user already uses Amphetamine or another keep-awake tool, mention that this satisfies the wake requirement.

## Scheduling command

From the skill directory:

```bash
python3 scripts/prompt_scheduler.py schedule \
  --name "Fable Content Resume" \
  --tag fable \
  --tag content \
  --at "2026-07-02 03:45" \
  --cwd "/Users/jakerains/projects/elevenlabsacademy" \
  --app Warp \
  --command 'claude-me-yolo --worktree content --resume "Fable Content" "resume"'
```

For a same-day or next-day local time, the script accepts `HH:MM` and resolves it against the system clock:

```bash
python3 scripts/prompt_scheduler.py schedule \
  --name "Enterprise Resume" \
  --tag enterprise \
  --at "03:45" \
  --cwd "$PWD" \
  --app Warp \
  --command 'claude-yolo --worktree enterprise --resume "Enterprise" "lets do option 1"'
```

If `HH:MM` is earlier than or equal to the current local time, the script schedules it for tomorrow. If the user says "tonight" or gives a date, resolve that explicitly before running the script.

## Verification command

Use the label printed by the scheduler:

```bash
python3 scripts/prompt_scheduler.py verify --label local.prompt-scheduler.fable-content-resume
```

The verification summary should show:

- the LaunchAgent is loaded
- `state = not running`
- `runs = 0` before the scheduled time
- plist syntax is valid
- command and wrapper files are executable
- log directory is writable

## Testing a Warp handoff

If the user wants proof that Warp will open, create a separate immediate test command rather than firing the real scheduled job. Use a different `--name` and pass `--open-now`:

```bash
python3 scripts/prompt_scheduler.py command-file \
  --name "Enterprise Resume Test" \
  --tag enterprise \
  --cwd "$PWD" \
  --app Warp \
  --command 'claude-yolo --worktree enterprise --resume "Enterprise" "lets do option 1"' \
  --open-now
```

This mirrors the scheduled `.command` path but does not install a LaunchAgent.

## Safety rules

- Never run the user's scheduled command as a test unless they explicitly ask for an immediate trigger.
- Preserve secrets: do not print env vars or inline secret values in command examples.
- Keep generated files under user-local locations:
  - command files: `~/.local/share/prompt-scheduler/commands/`
  - wrappers: `~/.local/share/prompt-scheduler/wrappers/`
  - logs: `~/Library/Logs/prompt-scheduler/`
  - LaunchAgents: `~/Library/LaunchAgents/`
- Use one-time launchd jobs for specific dates/times. The wrapper unloads and removes its plist after opening the command.
- Do not force recurring behavior unless the user asks for recurrence.
- Do not commit changes unless the user explicitly asks.

## Troubleshooting

- If a Warp launch configuration URI fails to visibly open, switch to the `.command` method. Opening `.command` files with `open -a Warp` is the preferred path for interactive sessions.
- If `open -a Warp` fails, confirm Warp is installed with `osascript -e 'id of application "Warp"'`.
- If launchd shows `runs = 0` after the scheduled time, check whether the Mac was awake and logged into the user session.
- If the terminal opens but the command is missing, remember `.command` files run `/bin/zsh -lic`, so aliases/functions from the user's login shell should load; still verify the command with `/bin/zsh -lic 'command -v COMMAND || type COMMAND'` when in doubt.
- If the user needs Linux support, use systemd user timers or `at`; this bundled script is intentionally macOS-first because it targets local Warp + launchd.
