#!/usr/bin/env python3
"""
Create local one-time macOS schedules for interactive agent commands.

This script is intentionally macOS-first:
- launchd owns the time trigger
- a .command file owns the visible terminal session
- open -a Warp opens the command in Warp when requested
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import pathlib
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
from typing import Iterable


HOME = pathlib.Path.home()
BASE_DIR = HOME / ".local" / "share" / "prompt-scheduler"
COMMANDS_DIR = BASE_DIR / "commands"
WRAPPERS_DIR = BASE_DIR / "wrappers"
LOGS_DIR = HOME / "Library" / "Logs" / "prompt-scheduler"
LAUNCH_AGENTS_DIR = HOME / "Library" / "LaunchAgents"


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=check)


def ensure_macos() -> None:
    if sys.platform != "darwin":
        raise SystemExit("prompt_scheduler.py currently supports macOS launchd scheduling only.")
    for binary in ("launchctl", "open"):
        if shutil.which(binary) is None:
            raise SystemExit(f"Required macOS command not found: {binary}")


def ensure_dirs() -> None:
    for directory in (COMMANDS_DIR, WRAPPERS_DIR, LOGS_DIR, LAUNCH_AGENTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def slugify(parts: Iterable[str]) -> str:
    raw = "-".join(part for part in parts if part).strip().lower()
    tokens = [token for token in re.split(r"[^a-z0-9]+", raw) if token]
    deduped: list[str] = []
    for token in tokens:
        if token not in deduped:
            deduped.append(token)
    slug = "-".join(deduped)
    return slug or "scheduled-prompt"


def parse_local_datetime(value: str, now: dt.datetime | None = None) -> dt.datetime:
    now = now or dt.datetime.now().astimezone()
    text = value.strip()

    time_only = re.fullmatch(r"(\d{1,2}):(\d{2})(?:\s*([ap]m))?", text, flags=re.I)
    if time_only:
        hour = int(time_only.group(1))
        minute = int(time_only.group(2))
        suffix = (time_only.group(3) or "").lower()
        if suffix == "pm" and hour != 12:
            hour += 12
        if suffix == "am" and hour == 12:
            hour = 0
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += dt.timedelta(days=1)
        return candidate

    normalized = text.replace("T", " ")
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%m/%d/%Y %H:%M",
        "%m/%d/%y %H:%M",
    ]
    for fmt in formats:
        try:
            parsed = dt.datetime.strptime(normalized, fmt)
            return parsed.replace(tzinfo=now.tzinfo)
        except ValueError:
            pass

    raise SystemExit(
        f"Could not parse --at {value!r}. Use HH:MM or YYYY-MM-DD HH:MM in local system time."
    )


def quote_zsh(value: str) -> str:
    return shlex.quote(value)


def label_for(name: str, tags: list[str]) -> str:
    return f"local.prompt-scheduler.{slugify([*tags, name])}"


def paths_for(label: str) -> dict[str, pathlib.Path]:
    short = label.removeprefix("local.prompt-scheduler.")
    return {
        "command": COMMANDS_DIR / f"{short}.command",
        "wrapper": WRAPPERS_DIR / f"{short}.zsh",
        "plist": LAUNCH_AGENTS_DIR / f"{label}.plist",
        "log": LOGS_DIR / f"{short}.log",
        "err_log": LOGS_DIR / f"{short}.err.log",
    }


def write_command_file(
    *,
    command_path: pathlib.Path,
    command: str,
    cwd: pathlib.Path,
) -> None:
    cwd = cwd.expanduser().resolve()
    if not cwd.exists() or not cwd.is_dir():
        raise SystemExit(f"Working directory does not exist: {cwd}")

    content = "\n".join(
        [
            "#!/bin/zsh",
            f"cd {quote_zsh(str(cwd))} || exit 1",
            f"exec /bin/zsh -lic {quote_zsh(command)}",
            "",
        ]
    )
    command_path.write_text(content)
    command_path.chmod(0o755)


def write_wrapper(
    *,
    wrapper_path: pathlib.Path,
    plist_path: pathlib.Path,
    command_path: pathlib.Path,
    log_path: pathlib.Path,
    app: str,
) -> None:
    open_line = f"/usr/bin/open -a {quote_zsh(app)} \"$CMD_FILE\""
    content = "\n".join(
        [
            "#!/bin/zsh",
            f"LOG={quote_zsh(str(log_path))}",
            f"PLIST={quote_zsh(str(plist_path))}",
            f"CMD_FILE={quote_zsh(str(command_path))}",
            "",
            "{",
            "  /bin/date",
            '  /bin/echo "Opening command file in app: $CMD_FILE"',
            f"  {open_line}",
            "  STATUS=$?",
            '  /bin/echo "open exited with status: $STATUS"',
            "  /bin/sleep 5",
            '  /bin/launchctl bootout "gui/$(/usr/bin/id -u)" "$PLIST" >/dev/null 2>&1',
            '  /bin/rm -f "$PLIST"',
            '  /bin/echo "Cleaned up one-time LaunchAgent plist."',
            '} >> "$LOG" 2>&1',
            "",
        ]
    )
    wrapper_path.write_text(content)
    wrapper_path.chmod(0o755)


def write_plist(
    *,
    plist_path: pathlib.Path,
    label: str,
    wrapper_path: pathlib.Path,
    run_at: dt.datetime,
    log_path: pathlib.Path,
    err_log_path: pathlib.Path,
) -> None:
    plist = {
        "Label": label,
        "ProgramArguments": ["/bin/zsh", str(wrapper_path)],
        "StartCalendarInterval": {
            "Month": run_at.month,
            "Day": run_at.day,
            "Hour": run_at.hour,
            "Minute": run_at.minute,
        },
        "StandardOutPath": str(log_path),
        "StandardErrorPath": str(err_log_path),
    }
    with plist_path.open("wb") as f:
        plistlib.dump(plist, f)
    plist_path.chmod(0o644)


def bootstrap_plist(plist_path: pathlib.Path, label: str) -> None:
    uid = os.getuid()
    run(["/bin/launchctl", "bootout", f"gui/{uid}", str(plist_path)], check=False)
    run(["/bin/launchctl", "bootstrap", f"gui/{uid}", str(plist_path)])


def launchctl_print(label: str) -> str:
    uid = os.getuid()
    result = run(["/bin/launchctl", "print", f"gui/{uid}/{label}"], check=False)
    return (result.stdout or "") + (result.stderr or "")


def print_summary(label: str, paths: dict[str, pathlib.Path], run_at: dt.datetime | None = None) -> None:
    if run_at:
        print(f"Scheduled local time: {run_at.strftime('%Y-%m-%d %H:%M %Z%z')}")
    print(f"Label: {label}")
    for key in ("command", "wrapper", "plist", "log", "err_log"):
        print(f"{key}: {paths[key]}")
    print()
    print("launchctl:")
    status = launchctl_print(label)
    keep = ("state =", "runs =", "last exit code", "path =", "program =", "stdout path", "stderr path")
    for line in status.splitlines():
        if any(item in line for item in keep) or '"Minute"' in line or '"Hour"' in line or '"Day"' in line or '"Month"' in line:
            print(line)


def command_exists(command: str) -> None:
    try:
        first = shlex.split(command)[0]
    except (IndexError, ValueError):
        return
    if "/" in first:
        return
    probe = f"command -v {quote_zsh(first)} || type {quote_zsh(first)}"
    result = run(["/bin/zsh", "-lic", probe], check=False)
    if result.returncode != 0:
        print(f"Warning: {first!r} was not found in an interactive zsh shell.", file=sys.stderr)


def schedule(args: argparse.Namespace) -> None:
    ensure_macos()
    ensure_dirs()
    run_at = parse_local_datetime(args.at)
    now = dt.datetime.now().astimezone()
    if run_at <= now:
        raise SystemExit(f"Refusing to schedule a time in the past: {run_at.isoformat()}")
    if not args.skip_command_check:
        command_exists(args.command)

    label = args.label or label_for(args.name, args.tag)
    paths = paths_for(label)
    write_command_file(command_path=paths["command"], command=args.command, cwd=pathlib.Path(args.cwd))
    write_wrapper(
        wrapper_path=paths["wrapper"],
        plist_path=paths["plist"],
        command_path=paths["command"],
        log_path=paths["log"],
        app=args.app,
    )
    write_plist(
        plist_path=paths["plist"],
        label=label,
        wrapper_path=paths["wrapper"],
        run_at=run_at,
        log_path=paths["log"],
        err_log_path=paths["err_log"],
    )
    run(["/usr/bin/plutil", "-lint", str(paths["plist"])])
    bootstrap_plist(paths["plist"], label)
    print_summary(label, paths, run_at)


def command_file(args: argparse.Namespace) -> None:
    ensure_macos()
    ensure_dirs()
    if not args.skip_command_check:
        command_exists(args.command)
    label = args.label or label_for(args.name, args.tag)
    paths = paths_for(label)
    write_command_file(command_path=paths["command"], command=args.command, cwd=pathlib.Path(args.cwd))
    print(f"command: {paths['command']}")
    if args.open_now:
        run(["/usr/bin/open", "-a", args.app, str(paths["command"])])
        print(f"Opened in {args.app}.")


def verify(args: argparse.Namespace) -> None:
    ensure_macos()
    paths = paths_for(args.label)
    print_summary(args.label, paths)
    print()
    print("permissions:")
    for key, path in paths.items():
        exists = path.exists()
        mode = oct(path.stat().st_mode & 0o777) if exists else "missing"
        print(f"{key}: {mode} {path}")
    print(f"logs_dir_writable: {os.access(LOGS_DIR, os.W_OK)} {LOGS_DIR}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Schedule local macOS agent prompts with launchd.")
    sub = parser.add_subparsers(dest="command_name", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--name", required=True, help="Human-readable job name.")
    common.add_argument("--tag", action="append", default=[], help="Tracking tag. Can be repeated.")
    common.add_argument("--label", help="Explicit launchd label. Defaults to local.prompt-scheduler.<tags-name>.")
    common.add_argument("--cwd", default=os.getcwd(), help="Working directory for the command.")
    common.add_argument("--app", default="Warp", help="macOS app to open the .command file with.")
    common.add_argument("--command", required=True, help="Exact shell command to run later.")
    common.add_argument("--skip-command-check", action="store_true", help="Skip interactive zsh command lookup.")

    schedule_parser = sub.add_parser("schedule", parents=[common], help="Create and load a one-time LaunchAgent.")
    schedule_parser.add_argument("--at", required=True, help="Local time: HH:MM or YYYY-MM-DD HH:MM.")
    schedule_parser.set_defaults(func=schedule)

    command_parser = sub.add_parser("command-file", parents=[common], help="Create a .command file, optionally open it now.")
    command_parser.add_argument("--open-now", action="store_true", help="Open the generated .command file immediately.")
    command_parser.set_defaults(func=command_file)

    verify_parser = sub.add_parser("verify", help="Verify a loaded job by label.")
    verify_parser.add_argument("--label", required=True)
    verify_parser.set_defaults(func=verify)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
