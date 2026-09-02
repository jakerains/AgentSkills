#!/usr/bin/env python3
"""Queue one explicit Claude handoff into an existing local Codex task."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


THREAD_ID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


class HandoffError(RuntimeError):
    """A user-actionable handoff failure."""


def normalize_thread_target(value: str) -> str:
    """Return a validated Codex task UUID from a UUID or codex:// deep link."""

    target = value.strip()
    if not target:
        raise HandoffError("Codex task target is empty.")

    parsed = urlparse(target)
    if parsed.scheme:
        if parsed.scheme.lower() != "codex" or parsed.netloc.lower() != "threads":
            raise HandoffError(
                "Expected a Codex task UUID or codex://threads/<uuid> deep link."
            )
        path_parts = [unquote(part) for part in parsed.path.split("/") if part]
        if len(path_parts) != 1:
            raise HandoffError(
                "Codex deep link must identify exactly one task UUID."
            )
        target = path_parts[0]

    if not THREAD_ID_RE.fullmatch(target):
        raise HandoffError(
            "Expected a Codex task UUID or codex://threads/<uuid> deep link."
        )

    return target.lower()


def read_message(args: argparse.Namespace) -> str:
    """Read the handoff text from one explicit input source."""

    if args.message is not None:
        message = args.message
    elif args.file is not None:
        try:
            message = Path(args.file).read_text(encoding="utf-8")
        except OSError as exc:
            raise HandoffError(f"Could not read handoff file: {exc}") from exc
    else:
        if sys.stdin.isatty():
            raise HandoffError(
                "No handoff text was supplied. Pass --message, --file, or pipe text on stdin."
            )
        message = sys.stdin.read()

    if not message.strip():
        raise HandoffError("Handoff text is empty.")

    return message


def queue_message(thread_id: str, message: str) -> subprocess.CompletedProcess[str]:
    """Invoke the local Codex CLI without shell interpolation."""

    codex_bin = shutil.which("codex")
    if codex_bin is None:
        raise HandoffError("Codex CLI is unavailable on PATH.")

    try:
        result = subprocess.run(
            [codex_bin, "queue", "--thread", thread_id, "--message", message],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise HandoffError(
            "Codex queue timed out. Delivery is uncertain; inspect the task before retrying."
        ) from exc
    except OSError as exc:
        raise HandoffError(f"Could not invoke Codex CLI: {exc}") from exc

    if result.returncode != 0:
        details = (result.stderr or result.stdout or "Unknown Codex CLI error").strip()
        raise HandoffError(f"Codex did not queue the handoff: {details}")

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Queue one explicit handoff into an existing Codex Desktop task."
    )
    parser.add_argument(
        "--thread",
        required=True,
        help="Codex task UUID or codex://threads/<uuid> deep link",
    )
    message_source = parser.add_mutually_exclusive_group()
    message_source.add_argument("--message", help="Short handoff text")
    message_source.add_argument("--file", help="UTF-8 text file containing the handoff")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the normalized request without queuing it",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        thread_id = normalize_thread_target(args.thread)
        message = read_message(args)

        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "dry-run",
                        "threadId": thread_id,
                        "message": message,
                    },
                    ensure_ascii=False,
                )
            )
            return 0

        result = queue_message(thread_id, message)
        payload: dict[str, str] = {"status": "queued", "threadId": thread_id}
        if result.stdout.strip():
            payload["codexOutput"] = result.stdout.strip()
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except HandoffError as exc:
        print(f"codex-handoff: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
