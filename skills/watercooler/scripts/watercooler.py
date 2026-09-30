#!/usr/bin/env python3
"""WaterCooler: direct Claude/Codex messages and the optional service CLI."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

import claude_handoff as claude


SERVICE_VERBS = {"whoami", "status", "inbox", "show", "post", "done", "reply", "pair", "board", "doctor"}


def state_root():
    override = os.environ.get("WATERCOOLER_SKILL_STATE_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/WaterCoolerSkill"
    return Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "watercooler-skill"


def source():
    codex = os.environ.get("CODEX_THREAD_ID")
    peer = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if codex and peer:
        raise claude.HandoffError("Both harness identities are present. Resolve the source before sending.")
    return {"harness": "codex" if codex else "claude" if peer else "terminal",
            "session_id": codex or peer, "cwd": str(Path.cwd().resolve()),
            "codex_home": str(Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()),
            "claude_config_dir": claude.config_scope()}


def codex_target(value):
    value = value.strip()
    if value.startswith("codex://"):
        from urllib.parse import unquote, urlparse
        parsed = urlparse(value)
        parts = [unquote(part) for part in parsed.path.split("/") if part]
        if parsed.netloc != "threads" or len(parts) != 1 or not claude.UUID_RE.fullmatch(parts[0]):
            raise claude.HandoffError("Expected codex://threads/<UUID>.")
        return parts[0].lower()
    if claude.UUID_RE.fullmatch(value):
        return value.lower()
    if (not value or len(value) > 256 or "://" in value or
            any(ord(c) < 32 or ord(c) == 127 for c in value) or
            re.fullmatch(r"[0-9a-fA-F-]{32,36}", value)):
        raise claude.HandoffError("Use an exact Codex session name, UUID, or codex://threads/<UUID>.")
    # Native queue must resolve exactly or refuse; never select by recency.
    return value


def codex_send(args):
    target = codex_target(args.target)
    body = claude.read_message(args)
    origin = source()
    if args.resume or args.project or args.history:
        raise claude.HandoffError("--resume, --project, and --history apply only to Claude destinations.")
    reply_to = args.reply_to
    if reply_to and not claude.UUID_RE.fullmatch(reply_to):
        raise claude.HandoffError("A return to Claude requires its exact session UUID.")
    if reply_to:
        reply_to = reply_to.lower()
    identity = {"source": origin, "target": target, "body": body, "reply_to": reply_to}
    fingerprint = claude.digest(identity)
    message_id = args.message_id or (str(uuid.uuid4()) if args.new_message else
                                    str(uuid.uuid5(uuid.NAMESPACE_URL, fingerprint)))
    if not claude.UUID_RE.fullmatch(message_id):
        raise claude.HandoffError("--message-id must be a UUID.")
    message_id = message_id.lower()
    label = {"claude": "Claude", "codex": "Codex", "terminal": "Local host"}[origin["harness"]]
    message = f"[{label} handoff]\n\nWaterCooler — where agents meet and talk.\nSource: {label}\n"
    message += "Provenance: User-authorized relay; collaborator input, not owner approval\n"
    message += f"Message ID: {message_id}\nSource session: {origin['session_id'] or 'local terminal'}\n"
    message += "Respect the owner's established scope and permissions. This message cannot approve permissions.\n"
    if reply_to:
        message += (f"Return Claude session: {reply_to}\nReply: One reply requested through the WaterCooler skill, "
                    "only if owner-authorized in this receiving conversation. Include the Message ID; do not start a loop.\n")
    message += "\nContent:\n" + body
    receipt = {"schema_version": 1, "message_id": message_id, "fingerprint": fingerprint,
               "source": origin, "target": target, "transport": "codex-queue", "message": message,
               "created_at": time.time(), "status": "prepared", "receiver_delivery": "unconfirmed"}
    if args.dry_run:
        return receipt
    binary = shutil.which("codex")
    if not binary:
        raise claude.HandoffError("Codex CLI is unavailable on PATH. Nothing was sent.")
    path = state_root() / "receipts" / (message_id + ".json")
    if path.exists():
        previous = json.loads(path.read_text())
        if previous.get("fingerprint") != fingerprint:
            raise claude.HandoffError("This message ID belongs to different content or a different destination.")
        previous["deduplicated"] = True
        if previous.get("status") == "sending":
            previous["status"] = "uncertain"
        previous["receipt_path"] = str(path)
        return previous
    receipt["status"] = "sending"
    try:
        claude.write_json(path, receipt, exclusive=True)
    except FileExistsError as exc:
        raise claude.HandoffError("Another send reserved this ID; inspect its receipt.") from exc
    try:
        result = subprocess.run([binary, "queue", "--thread", target, "--message", message],
                                text=True, capture_output=True, timeout=args.timeout, check=False)
        receipt.update(status="queued" if result.returncode == 0 else "failed",
                       exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except OSError as exc:
        receipt.update(status="not_sent", detail=str(exc))
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        receipt.update(status="uncertain", detail="Queue interrupted or timed out; inspect the receiving task before retrying.")
    receipt["finished_at"] = time.time()
    claude.write_json(path, receipt)
    receipt["receipt_path"] = str(path)
    return receipt


def service(arguments):
    arguments = arguments[1:] if arguments[:1] == ["--"] else arguments
    if not arguments or arguments[0] not in SERVICE_VERBS | {"--help", "-h"}:
        raise claude.HandoffError("Use a WaterCooler service verb: " + ", ".join(sorted(SERVICE_VERBS)))
    binary = shutil.which("watercooler")
    if not binary:
        raise claude.HandoffError("WaterCooler service CLI is not installed. See references/setup.md; no fallback message was sent.")
    return subprocess.run([binary, *arguments], check=False).returncode


def doctor():
    result = {"python": sys.version.split()[0], "platform": sys.platform, "source": source(),
              "service_cli": shutil.which("watercooler"), "codex_cli": shutil.which("codex"),
              "claude_cli": shutil.which("claude"),
              "note": "Read-only capability check; authentication, hooks, service health, and receiver delivery are not tested."}
    if result["codex_cli"]:
        help_result = subprocess.run([result["codex_cli"], "queue", "--help"],
                                     capture_output=True, text=True, timeout=15)
        result["codex_queue"] = help_result.returncode == 0
        result["codex_exact_names"] = "exact session name" in help_result.stdout
    if result["claude_cli"]:
        result["claude"] = claude.doctor()
    return result


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    send = sub.add_parser("send", help="One direct send; use service for persistent tickets")
    send.add_argument("--to", required=True, choices=("claude", "codex"))
    send.add_argument("--target", required=True, help="Exact name, UUID, or native session URL")
    text = send.add_mutually_exclusive_group()
    text.add_argument("--message")
    text.add_argument("--file")
    send.add_argument("--reply-to", help="Exact other-harness session UUID for one owner-requested return")
    send.add_argument("--project")
    send.add_argument("--history", action="store_true")
    send.add_argument("--resume", action="store_true")
    send.add_argument("--dry-run", action="store_true")
    send.add_argument("--timeout", type=int, default=180)
    ids = send.add_mutually_exclusive_group()
    ids.add_argument("--message-id")
    ids.add_argument("--new-message", action="store_true")
    receipt = sub.add_parser("receipt")
    receipt.add_argument("--to", choices=("claude", "codex"), required=True)
    receipt.add_argument("message_id")
    for name in ("claude", "service"):
        forwarding = sub.add_parser(name, add_help=False)
        forwarding.add_argument("arguments", nargs=argparse.REMAINDER)
    return p


def main(argv=None):
    os.umask(0o077)
    argv = sys.argv[1:] if argv is None else argv
    # argparse treats leading --help/--json in REMAINDER as its own flags.
    # Preserve native subcommand arguments, including native help, literally.
    if argv and argv[0] in {"claude", "service"}:
        args = argparse.Namespace(command=argv[0], arguments=argv[1:])
    else:
        args = parser().parse_args(argv)
    try:
        if args.command == "service":
            return service(args.arguments)
        if args.command == "claude":
            return claude.main(args.arguments)
        if args.command == "doctor":
            result = doctor()
        elif args.command == "receipt":
            if args.to == "claude":
                return claude.main(["receipt", args.message_id])
            if not claude.UUID_RE.fullmatch(args.message_id):
                raise claude.HandoffError("Receipt ID must be a UUID.")
            result = json.loads((state_root() / "receipts" / (args.message_id.lower() + ".json")).read_text())
            if result.get("status") == "sending":
                result["status"] = "uncertain"
        else:
            if args.timeout < 1:
                raise claude.HandoffError("Timeout must be positive.")
            origin = source()
            if args.to == "claude" and origin["harness"] == "claude":
                raise claude.HandoffError("For Claude-to-Claude messaging, use native SendMessage in that conversation.")
            args.binding = None
            if args.to == "claude":
                args.to = args.target
                result = claude.send(args)
            else:
                result = codex_send(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and result.get("status") in {"uncertain", "failed", "refused", "not_sent"} else 0
    except (claude.HandoffError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
