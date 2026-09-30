#!/usr/bin/env python3
"""Bound an owner-authorized WaterCooler service exchange to two exact sessions.

Local agreements are bookkeeping, not authentication or permission grants.
Requires Python 3.10+ and POSIX file locks (macOS/Linux).
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

import claude_handoff as transport
import watercooler as wc


def participant():
    current = wc.source()
    if current["harness"] == "terminal" or not transport.UUID_RE.fullmatch(current["session_id"]):
        raise transport.HandoffError("Run agreement commands in an exact Claude or Codex session.")
    return {"harness": current["harness"], "session_id": current["session_id"].lower(),
            "config_scope": current["codex_home"] if current["harness"] == "codex" else current["claude_config_dir"]}


def key(person):
    return person["harness"] + ":" + person["session_id"]


def path_for(identifier):
    if not transport.UUID_RE.fullmatch(identifier):
        raise transport.HandoffError("Agreement ID must be a UUID.")
    return wc.state_root() / "agreements" / (identifier.lower() + ".json")


@contextmanager
def locked(identifier):
    path = path_for(identifier)
    transport.private_dir(path.parent)
    with path.with_suffix(".lock").open("a") as lock:
        os.chmod(lock.name, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        agreement = json.loads(path.read_text())
        try:
            yield agreement
        finally:
            transport.write_json(path, agreement)


def assert_member(agreement, person):
    member = next((p for p in agreement["participants"] if key(p) == key(person)), None)
    if member is None or member["config_scope"] != person["config_scope"]:
        raise transport.HandoffError("This session/configuration is not a participant in that agreement.")


def assert_open(agreement):
    if agreement["closed_at"] is not None:
        raise transport.HandoffError("The collaboration is closed.")
    if time.time() >= agreement["expires_at"]:
        raise transport.HandoffError("The collaboration expired. Owner authorization is needed for a new agreement.")


def native(arguments):
    binary = shutil.which("watercooler")
    if not binary:
        raise transport.HandoffError("WaterCooler service CLI is unavailable. No direct-send fallback is allowed.")
    result = subprocess.run([binary, *arguments, "--json"], text=True, capture_output=True, timeout=45)
    if result.returncode:
        raise transport.HandoffError((result.stderr or result.stdout or "Service command failed").strip())
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise transport.HandoffError("Unexpected service receipt; inspect the ticket before retrying.")
    return data


def create(args):
    person = participant()
    peer = {"harness": args.peer_harness, "session_id": args.peer_session.lower(),
            "config_scope": str(Path(args.peer_config).expanduser().resolve())}
    if peer["harness"] == person["harness"] or not transport.UUID_RE.fullmatch(peer["session_id"]):
        raise transport.HandoffError("Select an exact session UUID in the other harness.")
    if not args.objective.strip() or not args.scope.strip() or args.minutes < 1 or args.max_messages < 1:
        raise transport.HandoffError("Provide objective, allowed scope, positive duration, and positive message limit.")
    identifier = str(uuid.uuid4())
    agreement = {"schema_version": 1, "id": identifier, "participants": [person, peer],
                 "accepted_by": [key(person)], "objective": args.objective, "scope": args.scope,
                 "created_at": time.time(), "expires_at": time.time() + args.minutes * 60,
                 "max_messages": args.max_messages, "exchanges": [], "chains": [], "closed_at": None}
    transport.write_json(path_for(identifier), agreement, exclusive=True)
    return agreement


def manage(args):
    person = participant()
    with locked(args.agreement) as agreement:
        assert_member(agreement, person)
        if args.action == "close":
            agreement["closed_at"] = time.time()
        elif args.action == "join":
            assert_open(agreement)
            if key(person) not in agreement["accepted_by"]:
                agreement["accepted_by"].append(key(person))
        return agreement.copy()


def exchange(args):
    person = participant()
    body = transport.read_message(args)
    # Holding the lock through the service call bounds concurrent sends. Reserve
    # and persist before spawning: an interrupted send consumes a slot and is
    # uncertain rather than automatically replayed.
    with locked(args.agreement) as agreement:
        assert_member(agreement, person)
        assert_open(agreement)
        if set(agreement["accepted_by"]) != {key(p) for p in agreement["participants"]}:
            raise transport.HandoffError("Both participants must join under direct owner authorization before exchanging work.")
        if len(agreement["exchanges"]) >= agreement["max_messages"]:
            raise transport.HandoffError("The agreement's message limit is reached.")
        if any(e["status"] == "uncertain" for e in agreement["exchanges"]):
            raise transport.HandoffError("An earlier exchange is uncertain. Inspect it before authorizing a new agreement.")
        peer = next(p for p in agreement["participants"] if key(p) != key(person))
        if args.action == "reply":
            data = native(["show", args.ticket])
            ticket = data.get("ticket", data)
            sender, receiver = ticket["from"], ticket["to"]
            if (sender.get("sessionId") != peer["session_id"] or sender.get("harness") != peer["harness"] or
                    receiver.get("sessionId") != person["session_id"] or receiver.get("harness") != person["harness"] or
                    ticket["chainId"] not in agreement["chains"]):
                raise transport.HandoffError("Ticket is outside this agreement's participants or chains.")
            command = ["reply", args.ticket, "--message", body]
        else:
            if not args.title or not args.title.strip():
                raise transport.HandoffError("A post requires --title.")
            command = ["post", "--to", key(peer), "--title", args.title, "--message", body, "--reply",
                       "--ttl", str(max(1, int(agreement["expires_at"] - time.time()))) + "s"]
        record = {"id": str(uuid.uuid4()), "source": key(person), "at": time.time(), "status": "uncertain"}
        agreement["exchanges"].append(record)
        transport.write_json(path_for(args.agreement), agreement)
        try:
            result = native(command)
            ticket = result.get("ticket", result)
            if not ticket.get("id") or not ticket.get("chainId"):
                raise transport.HandoffError("Service receipt lacks ticket identity; inspect before retrying.")
            record.update(status="recorded", ticket_id=ticket["id"], receipt=result)
            if ticket["chainId"] not in agreement["chains"]:
                agreement["chains"].append(ticket["chainId"])
        except (OSError, ValueError, KeyError, subprocess.TimeoutExpired, transport.HandoffError) as exc:
            record["detail"] = str(exc)
            raise transport.HandoffError("Exchange stopped; its slot is reserved. Inspect agreement and service ticket before any new send: " + str(exc)) from exc
        return record.copy()


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    new = sub.add_parser("create")
    new.add_argument("--peer-harness", choices=("claude", "codex"), required=True)
    new.add_argument("--peer-session", required=True)
    new.add_argument("--peer-config", required=True, help="Exact peer CLAUDE_CONFIG_DIR or CODEX_HOME")
    new.add_argument("--objective", required=True)
    new.add_argument("--scope", required=True, help="Owner-authorized actions and boundaries")
    new.add_argument("--minutes", type=int, default=120)
    new.add_argument("--max-messages", type=int, default=6)
    for action in ("join", "status", "close", "post", "reply"):
        command = sub.add_parser(action)
        command.add_argument("agreement")
        if action in {"post", "reply"}:
            if action == "post":
                command.add_argument("--title", required=True)
            else:
                command.add_argument("ticket")
            content = command.add_mutually_exclusive_group()
            content.add_argument("--message")
            content.add_argument("--file")
    return p


def main(argv=None):
    os.umask(0o077)
    args = parser().parse_args(argv)
    try:
        result = create(args) if args.action == "create" else exchange(args) if args.action in {"post", "reply"} else manage(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (transport.HandoffError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
