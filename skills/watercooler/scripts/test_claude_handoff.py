#!/usr/bin/env python3
"""Behavioral tests. All Claude calls are fixtures; no live messages are sent."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import uuid

import claude_handoff as bridge


SID = "11111111-1111-4111-8111-111111111111"
SID2 = "22222222-2222-4222-8222-222222222222"
THREAD = "33333333-3333-4333-8333-333333333333"


def local(name="claude test", sid=SID, project="/tmp/project-a", live=True):
    return {"kind": "local", "name": name, "session_id": sid,
            "cwd": str(Path(project).resolve()), "live": live,
            "pid": 100 if live else None, "status": "idle" if live else "stopped"}


def result(data, code=0):
    return subprocess.CompletedProcess([], code, json.dumps(data), "")


def tool_result(data, tool_id="tool-send-1"):
    return {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": tool_id}]}, "tool_use_result": data}


class ResolveTests(unittest.TestCase):
    def test_name_with_spaces_across_folders(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]):
            self.assertEqual(bridge.resolve_target("claude test")["session_id"], SID)

    def test_duplicate_name_requires_identity(self):
        rows = [local(), local(sid=SID2, project="/tmp/project-b")]
        with patch.object(bridge, "cli_sessions", return_value=rows):
            with self.assertRaisesRegex(bridge.HandoffError, "Ambiguous"):
                bridge.resolve_target("claude test")
            self.assertEqual(bridge.resolve_target("claude test", "/tmp/project-b")["session_id"], SID2)
            self.assertEqual(bridge.resolve_target(SID)["session_id"], SID)
            # Even an exact UUID cannot disambiguate native live name lookup.
            with self.assertRaisesRegex(bridge.HandoffError, "unique session name"):
                bridge.ensure_live_target(rows[0])

    def test_never_fuzzy_selects(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]):
            with self.assertRaisesRegex(bridge.HandoffError, "No exact"):
                bridge.resolve_target("claude")

    def test_cloud_url_validation_prevents_new_task_description(self):
        target = bridge.cloud_target("claude.ai/code/session_ABC?from=cli")
        self.assertEqual(target["session_id"], "session_ABC")
        self.assertIsNone(bridge.cloud_target("fix the login bug"))
        for value in ["https://evil.test/code/session_ABC", "https://claude.ai/code/fix-this",
                      "https://claude.ai/code/session_ABC/extra", "https://claude.ai@evil.test/code/session_ABC"]:
            with self.subTest(value=value), self.assertRaises(bridge.HandoffError):
                bridge.cloud_target(value)

    def test_unlisted_stopped_id_needs_explicit_resume_and_directory(self):
        with patch.object(bridge, "cli_sessions", return_value=[]):
            with self.assertRaises(bridge.HandoffError):
                bridge.resolve_target(SID)
            with self.assertRaises(bridge.HandoffError):
                bridge.resolve_target(SID, "/tmp/project-a")
            target = bridge.resolve_target(SID, "/tmp/project-a", allow_unknown_id=True)
            self.assertFalse(target["live"])

    def test_cli_live_state_depends_on_pid_not_job_state(self):
        data = [{"sessionId": SID, "name": "working", "cwd": "/tmp/a", "state": "blocked", "pid": 42},
                {"sessionId": SID2, "name": "stopped", "cwd": "/tmp/b", "state": "blocked"}]
        with patch.object(bridge, "run_cli", return_value=result(data)) as run:
            rows = bridge.cli_sessions()
        self.assertTrue(rows[0]["live"])
        self.assertFalse(rows[1]["live"])
        self.assertEqual(run.call_args.args[0], ["agents", "--json", "--all"])

    def test_sdk_history_merges_without_losing_live_pid(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]), \
             patch.object(bridge, "history_sessions", return_value=[local(live=False), local(sid=SID2, live=False)]):
            rows = bridge.all_sessions(True)
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0]["live"])

    def test_corrupt_discovery_fails_closed(self):
        with patch.object(bridge, "run_cli", return_value=result({"error": "offline"})):
            with self.assertRaises(bridge.HandoffError):
                bridge.cli_sessions()


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / "guard.json"
        self.message = "literal $HOME `touch injected` $(echo nope)\nsecond line"
        self.target = local()
        bridge.write_json(self.config, {"target": self.target, "message": self.message, "message_id": SID})

    def call_guard(self, incoming=None, rows=None):
        event = {"tool_name": "SendMessage", "tool_use_id": "tool-send-1", "tool_input": incoming or
                 {"to": "claude test", "message": self.message}}
        stdout = io.StringIO()
        with patch.object(bridge, "cli_sessions", return_value=rows if rows is not None else [self.target]), \
             patch("sys.stdin", io.StringIO(json.dumps(event))), contextlib.redirect_stdout(stdout):
            bridge.guard(str(self.config))
        return json.loads(stdout.getvalue())["hookSpecificOutput"]

    def test_literal_payload_and_one_send_only(self):
        allowed = self.call_guard({"to": "claude test", "message": self.message,
                                   "notify_when_idle": True, "recipient": "wrong target", "type": "broadcast"})
        self.assertEqual(allowed["permissionDecision"], "allow")
        self.assertEqual(allowed["updatedInput"]["message"], self.message)
        self.assertEqual(set(allowed["updatedInput"]), {"to", "message", "summary"})
        self.assertEqual(self.call_guard()["permissionDecision"], "deny")

    def test_wrong_destination_denied_before_attempt(self):
        self.assertEqual(self.call_guard({"to": "other", "message": self.message})["permissionDecision"], "deny")
        self.assertFalse(self.config.with_suffix(".attempt.json").exists())

    def test_changed_body_denied(self):
        self.assertEqual(self.call_guard({"to": "claude test", "message": "summarized"})["permissionDecision"], "deny")

    def test_renamed_restarted_or_disappeared_target_denied(self):
        for rows in [[], [dict(self.target, name="new name")], [dict(self.target, pid=999)]]:
            with self.subTest(rows=rows):
                self.assertEqual(self.call_guard(rows=rows)["permissionDecision"], "deny")


class ReceiptTests(unittest.TestCase):
    def test_courier_prose_is_not_delivery_evidence(self):
        events = [{"type": "result", "result": "Sent successfully!", "subtype": "success"}]
        self.assertEqual(bridge.courier_receipt(events, {"tool_use_id": "tool-send-1"})["status"], "uncertain")

    def test_tool_ack_is_not_receiver_completion(self):
        events = [tool_result({"success": True, "msg_id": SID2, "message": "sent to peer"})]
        self.assertEqual(bridge.courier_receipt(events, {"tool_use_id": "tool-send-1"})["status"], "sent")

    def test_unrelated_tool_result_is_not_evidence(self):
        events = [tool_result({"success": True, "msg_id": SID2}, "other-tool-id")]
        self.assertEqual(bridge.courier_receipt(events, {"tool_use_id": "tool-send-1"})["status"], "uncertain")

    def test_missing_guard_with_native_success_is_uncertain(self):
        events = [tool_result({"success": True, "msg_id": SID2})]
        self.assertEqual(bridge.courier_receipt(events, None)["status"], "uncertain")

    def test_interrupted_unguarded_send_is_uncertain(self):
        events = [{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "SendMessage", "input": {"to": "claude test"}}]}}]
        self.assertEqual(bridge.courier_receipt(events, None)["status"], "uncertain")

    def test_ack_explicitly_marks_receiver_unconfirmed(self):
        events = [tool_result({"success": True, "msg_id": SID2})]
        receipt = bridge.courier_receipt(events, {"tool_use_id": "tool-send-1"})
        self.assertEqual(receipt["receiver_delivery"], "unconfirmed")

    def test_held_and_refused(self):
        for message, expected in [("Message held for approval", "held"), ("Session refuses messages", "refused")]:
            events = [tool_result({"success": False, "message": message})]
            self.assertEqual(bridge.courier_receipt(events, {"tool_use_id": "tool-send-1"})["status"], expected)

    def test_cloud_checks_target_and_uses_stdin(self):
        target = bridge.cloud_target("session_ABC")
        text = "two\nlines $(no shell evaluation)"
        with patch.object(bridge, "run_cli", return_value=result({"ok": True, "session_id": "cse_ABC", "url": "https://claude.ai/code/session_ABC"})) as run:
            self.assertEqual(bridge.send_cloud(target, text, 30)["status"], "queued")
        self.assertEqual(run.call_args.args[0], ["-p", "--cloud", "session_ABC", "--output-format", "json"])
        self.assertEqual(run.call_args.kwargs["text_input"], text)
        self.assertNotIn(text, run.call_args.args[0])
        with patch.object(bridge, "run_cli", return_value=result({"ok": True, "session_id": "session_OTHER"})):
            self.assertEqual(bridge.send_cloud(target, text, 30)["status"], "uncertain")

    def test_cloud_rejection_and_unstructured_error(self):
        target = bridge.cloud_target("session_ABC")
        with patch.object(bridge, "run_cli", return_value=result({"ok": False, "error": "archived"}, 1)):
            self.assertEqual(bridge.send_cloud(target, "hello", 30)["status"], "refused")
        with patch.object(bridge, "run_cli", return_value=subprocess.CompletedProcess([], 1, "", "policy disabled")):
            self.assertEqual(bridge.send_cloud(target, "hello", 30)["status"], "uncertain")
        with patch.object(bridge, "run_cli", return_value=result([])):
            self.assertEqual(bridge.send_cloud(target, "hello", 30)["status"], "uncertain")


class SendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = patch.dict(os.environ, {"CLAUDE_ADVISOR_STATE_DIR": self.tmp.name, "CODEX_THREAD_ID": THREAD})
        self.env.start()
        self.addCleanup(self.env.stop)

    def args(self, *extra):
        return bridge.parser().parse_args(["send", "--to", "claude test", "--message", "findings", *extra])

    def test_dry_run_has_no_writes_or_delivery(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]), patch.object(bridge, "send_live") as live:
            receipt = bridge.send(self.args("--dry-run"))
        self.assertEqual(receipt["status"], "prepared")
        live.assert_not_called()
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [])

    def test_exact_repeat_sends_once(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]), \
             patch.object(bridge, "send_live", return_value={"status": "sent"}) as live:
            one = bridge.send(self.args())
            two = bridge.send(self.args())
        self.assertEqual(live.call_count, 1)
        self.assertEqual(one["message_id"], two["message_id"])
        self.assertTrue(two["deduplicated"])
        self.assertEqual(Path(one["receipt_path"]).stat().st_mode & 0o777, 0o600)

    def test_uncertain_delivery_cannot_be_retried_implicitly(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]), \
             patch.object(bridge, "send_live", side_effect=bridge.HandoffError("lost connection")) as live:
            one = bridge.send(self.args())
            two = bridge.send(self.args())
        self.assertEqual(live.call_count, 1)
        self.assertEqual(one["status"], "uncertain")
        self.assertEqual(two["status"], "uncertain")

    def test_stopping_session_does_not_bypass_dedup(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]), \
             patch.object(bridge, "send_live", return_value={"status": "uncertain"}):
            first = bridge.send(self.args())
        with patch.object(bridge, "cli_sessions", return_value=[local(live=False)]), \
             patch.object(bridge, "resume_local") as resume:
            second = bridge.send(self.args("--resume"))
        self.assertEqual(first["message_id"], second["message_id"])
        resume.assert_not_called()

    def test_caller_message_id_cannot_be_reused_for_other_content(self):
        args = self.args("--message-id", SID)
        with patch.object(bridge, "cli_sessions", return_value=[local()]), \
             patch.object(bridge, "send_live", return_value={"status": "sent"}):
            bridge.send(args)
            args.message = "different"
            with self.assertRaisesRegex(bridge.HandoffError, "different content"):
                bridge.send(args)

    def test_stopped_session_requires_resume(self):
        with patch.object(bridge, "cli_sessions", return_value=[local(live=False)]), \
             patch.object(bridge, "resume_local") as resume:
            with self.assertRaisesRegex(bridge.HandoffError, "stopped"):
                bridge.send(self.args())
        resume.assert_not_called()

    def test_busy_target_lock_prevents_parallel_send(self):
        target = local()
        lock = bridge.state_root() / "locks" / (bridge.digest([bridge.config_scope(), "local", SID]) + ".lock")
        lock.mkdir(parents=True)
        with patch.object(bridge, "cli_sessions", return_value=[target]), patch.object(bridge, "send_live") as live:
            receipt = bridge.send(self.args())
        self.assertEqual(receipt["status"], "not_sent")
        self.assertTrue(lock.is_dir())
        live.assert_not_called()

    def test_resume_never_runs_on_live_target(self):
        with patch.object(bridge, "cli_sessions", return_value=[local()]), patch.object(bridge, "run_cli") as run:
            with self.assertRaisesRegex(bridge.HandoffError, "live"):
                bridge.resume_local(local(), "body", 30)
        run.assert_not_called()

    def test_resume_never_broadens_an_advisor(self):
        with patch.object(bridge, "run_cli") as run:
            with self.assertRaisesRegex(bridge.HandoffError, "read-only advisor"):
                bridge.resume_local(local(name="claude-advisor:opus:review", live=False), "body", 30)
            state = bridge.state_root().parent / "threads" / "project" / "opus" / "review.json"
            bridge.write_json(state, {"session_id": SID})
            with self.assertRaisesRegex(bridge.HandoffError, "read-only advisor"):
                bridge.resume_local(local(name=None, live=False), "body", 30)
        run.assert_not_called()

    def test_resume_runs_in_target_directory_without_model_override(self):
        target = local(project=self.tmp.name, live=False)
        data = {"session_id": SID, "subtype": "success", "is_error": False, "result": "answer"}
        with patch.object(bridge, "cli_sessions", return_value=[]), patch.object(bridge, "run_cli", return_value=result(data)) as run:
            receipt = bridge.resume_local(target, "body", 30)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(run.call_args.kwargs["cwd"], str(Path(self.tmp.name).resolve()))
        self.assertNotIn("--model", run.call_args.args[0])
        self.assertNotIn("--dangerously-skip-permissions", run.call_args.args[0])

    def test_wrong_resume_session_is_never_success(self):
        target = local(project=self.tmp.name, live=False)
        data = {"session_id": SID2, "subtype": "success", "is_error": False}
        with patch.object(bridge, "cli_sessions", return_value=[]), patch.object(bridge, "run_cli", return_value=result(data)):
            self.assertEqual(bridge.resume_local(target, "body", 30)["status"], "uncertain")

    def test_bindings_are_scoped_and_cannot_silently_retarget(self):
        first = bridge.binding_path("partner")
        bridge.write_json(first, {"target": local()}, exclusive=True)
        with self.assertRaises(FileExistsError):
            bridge.write_json(first, {"target": local(sid=SID2)}, exclusive=True)
        with patch.dict(os.environ, {"CODEX_THREAD_ID": SID2}):
            self.assertNotEqual(first, bridge.binding_path("partner"))

    def test_no_automatic_return_without_request(self):
        no_reply = bridge.envelope("body", SID)
        self.assertNotIn("Return task:", no_reply)
        self.assertIn("not owner approval", no_reply)
        reply = bridge.envelope("body", SID, bridge.codex_id("codex://threads/" + THREAD))
        self.assertIn("Return task: " + THREAD, reply)
        self.assertIn("one reply", reply)


@unittest.skipUnless(os.name == "posix", "advisory bash wrappers require a POSIX shell")
class AdvisorRegressionTests(unittest.TestCase):
    def test_existing_wrapper_start_resume_and_live_collision(self):
        import shutil
        if not shutil.which("jq") or not shutil.which("bash"):
            self.skipTest("bash and jq required")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fake = root / "bin"
            fake.mkdir()
            cli = fake / "claude"
            cli.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
with open(os.environ["CALL_LOG"], "a") as out:
    out.write(json.dumps(args) + "\\n")
sid = "11111111-1111-4111-8111-111111111111"
if args[:2] == ["agents", "--json"]:
    print(json.dumps([{"sessionId": sid, "pid": 42}] if Path(os.environ["LIVE_FLAG"]).exists() else []))
else:
    print(json.dumps({"type":"result", "subtype":"success", "is_error":False,
        "session_id":sid, "modelUsage":{"claude-opus-5":{}}, "result":"# Recommendation\\nFixture report."}))
''')
            cli.chmod(0o755)
            env = dict(os.environ, PATH=str(fake) + os.pathsep + os.environ["PATH"],
                       CLAUDE_ADVISOR_STATE_DIR=str(root / "state"), OPUS_ADVISOR_DIR=str(root / "reports"),
                       CALL_LOG=str(root / "calls.jsonl"), LIVE_FLAG=str(root / "live"))
            script = Path(__file__).parent / "consult-opus.sh"
            cmd = ["bash", str(script.resolve()), "--thread", "regression", "Fixture prompt"]
            first = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            calls = [json.loads(s) for s in (root / "calls.jsonl").read_text().splitlines()]
            consultations = [a for a in calls if a[0] == "-p"]
            self.assertEqual(len(consultations), 2)
            self.assertIn("--resume", consultations[1])
            for args in consultations:
                self.assertEqual(args[args.index("--tools") + 1], "Read,Grep,Glob")
                self.assertEqual(json.loads(args[args.index("--settings") + 1])["crossSessionInbound"], "refuse")
                self.assertIn("--restricted", args)
            (root / "live").touch()
            third = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
            self.assertNotEqual(third.returncode, 0)
            self.assertIn("already live", third.stderr)
            calls = [json.loads(s) for s in (root / "calls.jsonl").read_text().splitlines()]
            self.assertEqual(sum(a[0] == "-p" for a in calls), 2)


if __name__ == "__main__":
    unittest.main()
