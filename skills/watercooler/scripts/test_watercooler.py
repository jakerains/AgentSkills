#!/usr/bin/env python3
"""Direct dispatch and agreement behavior with mocked native services only."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import watercooler as wc
import collaboration as collab


CLAUDE_ID = "11111111-1111-4111-8111-111111111111"
CODEX_ID = "22222222-2222-4222-8222-222222222222"
TICKET_ID = "33333333-3333-4333-8333-333333333333"
CHAIN_ID = "44444444-4444-4444-8444-444444444444"


class DirectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {"WATERCOOLER_SKILL_STATE_DIR": self.temp.name,
                                          "CLAUDE_CODE_SESSION_ID": CLAUDE_ID,
                                          "CODEX_THREAD_ID": ""})
        self.env.start()
        self.addCleanup(self.env.stop)

    def args(self, *extra):
        return wc.parser().parse_args(["send", "--to", "codex", "--target", "API review",
                                       "--message", 'Literal $(touch nope) `text`\nSecond line', *extra])

    def test_literals_provenance_and_duplicate_reservation(self):
        with patch.object(wc.shutil, "which", return_value="/fake/codex"), patch.object(wc.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "queued", "")
            first = wc.codex_send(self.args())
            second = wc.codex_send(self.args())
            self.assertEqual(first["status"], "queued")
            self.assertTrue(second["deduplicated"])
            self.assertEqual(run.call_count, 1)
            argv = run.call_args.args[0]
            self.assertEqual(argv[:4], ["/fake/codex", "queue", "--thread", "API review"])
            self.assertIn('Literal $(touch nope) `text`\nSecond line', argv[-1])
            self.assertIn("[Claude handoff]", argv[-1])
            self.assertIn("not owner approval", argv[-1])
            self.assertEqual(first["receiver_delivery"], "unconfirmed")
            self.assertEqual(Path(first["receipt_path"]).stat().st_mode & 0o777, 0o600)

    def test_timeout_is_not_replayed(self):
        with patch.object(wc.shutil, "which", return_value="/fake/codex"), patch.object(wc.subprocess, "run") as run:
            run.side_effect = subprocess.TimeoutExpired("codex", 1)
            self.assertEqual(wc.codex_send(self.args())["status"], "uncertain")
            self.assertEqual(wc.codex_send(self.args())["status"], "uncertain")
            self.assertEqual(run.call_count, 1)

    def test_id_cannot_be_reused_for_different_payload(self):
        with patch.object(wc.shutil, "which", return_value="/fake/codex"), patch.object(wc.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 0, "", "")
            wc.codex_send(self.args("--message-id", TICKET_ID))
            changed = self.args("--message-id", TICKET_ID)
            changed.target = CODEX_ID
            with self.assertRaisesRegex(wc.claude.HandoffError, "different"):
                wc.codex_send(changed)

    def test_dry_run_does_not_touch_transport_or_state(self):
        with patch.object(wc.subprocess, "run") as run:
            result = wc.codex_send(self.args("--dry-run", "--reply-to", CLAUDE_ID))
            self.assertEqual(result["status"], "prepared")
            self.assertIn("Return Claude session: " + CLAUDE_ID, result["message"])
            run.assert_not_called()
            self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_target_validation(self):
        self.assertEqual(wc.codex_target("codex://threads/" + CODEX_ID + "?view=review"), CODEX_ID)
        self.assertEqual(wc.codex_target("session with spaces"), "session with spaces")
        for value in ("", "https://evil.test", "codex://threads/nope", "bad\nname"):
            with self.subTest(value=value), self.assertRaises(wc.claude.HandoffError):
                wc.codex_target(value)

    def test_service_passthrough_preserves_failure_and_literal_arguments(self):
        with patch.object(wc.shutil, "which", return_value="/fake/watercooler"), patch.object(wc.subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess([], 4)
            self.assertEqual(wc.service(["post", "--message", "$(literal)"]), 4)
            self.assertEqual(run.call_args.args[0], ["/fake/watercooler", "post", "--message", "$(literal)"])
        with patch.object(wc.shutil, "which", return_value=None):
            with self.assertRaisesRegex(wc.claude.HandoffError, "not installed"):
                wc.service(["inbox"])

    def test_same_skill_routes_claude(self):
        with patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": "", "CODEX_THREAD_ID": CODEX_ID}), \
                patch.object(wc.claude, "send", return_value={"status": "prepared"}) as send, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wc.main(["send", "--to", "claude", "--target", "claude test", "--message", "hi", "--dry-run"]), 0)
            self.assertEqual(send.call_args.args[0].to, "claude test")

    def test_native_help_is_forwarded(self):
        with patch.object(wc, "service", return_value=0) as forward:
            self.assertEqual(wc.main(["service", "--help"]), 0)
            forward.assert_called_once_with(["--help"])


class AgreementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.codex_config = str(Path(self.temp.name, "codex").resolve())
        self.claude_config = str(Path(self.temp.name, "claude").resolve())
        self.env = patch.dict(os.environ, {"WATERCOOLER_SKILL_STATE_DIR": self.temp.name,
                                          "CODEX_HOME": self.codex_config, "CLAUDE_CONFIG_DIR": self.claude_config,
                                          "CODEX_THREAD_ID": CODEX_ID, "CLAUDE_CODE_SESSION_ID": ""})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.agreement = collab.create(collab.parser().parse_args([
            "create", "--peer-harness", "claude", "--peer-session", CLAUDE_ID,
            "--peer-config", self.claude_config, "--objective", "Verify parser",
            "--scope", "Both inspect; only Codex edits", "--max-messages", "2"]))
        self.identifier = self.agreement["id"]

    def join(self):
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "", "CLAUDE_CODE_SESSION_ID": CLAUDE_ID}):
            return collab.manage(collab.parser().parse_args(["join", self.identifier]))

    def post(self):
        return collab.exchange(collab.parser().parse_args(["post", self.identifier, "--title", "Review", "--message", "Review parser"]))

    def receipt(self):
        return {"ticket": {"id": TICKET_ID, "chainId": CHAIN_ID, "state": "posted"}}

    def test_both_join_and_exact_target(self):
        with patch.object(collab, "native") as send:
            with self.assertRaisesRegex(wc.claude.HandoffError, "Both participants"):
                self.post()
            send.assert_not_called()
            self.join()
            send.return_value = self.receipt()
            result = self.post()
            self.assertEqual(result["status"], "recorded")
            self.assertEqual(send.call_args.args[0][:3], ["post", "--to", "claude:" + CLAUDE_ID])

    def test_identity_and_config_scope(self):
        with patch.dict(os.environ, {"CODEX_HOME": self.temp.name + "/different"}):
            with self.assertRaisesRegex(wc.claude.HandoffError, "not a participant"):
                collab.manage(collab.parser().parse_args(["join", self.identifier]))

    def test_message_limit_expiry_and_close(self):
        self.join()
        with patch.object(collab, "native", return_value=self.receipt()) as send:
            self.post()
            self.post()
            with self.assertRaisesRegex(wc.claude.HandoffError, "limit"):
                self.post()
            self.assertEqual(send.call_count, 2)
        with collab.locked(self.identifier) as agreement:
            agreement["expires_at"] = 0
        with self.assertRaisesRegex(wc.claude.HandoffError, "expired"):
            self.post()
        collab.manage(collab.parser().parse_args(["close", self.identifier]))
        with self.assertRaisesRegex(wc.claude.HandoffError, "closed"):
            self.post()

    def test_uncertain_exchange_is_persisted_and_blocks_further_sends(self):
        self.join()
        with patch.object(collab, "native", side_effect=subprocess.TimeoutExpired("watercooler", 45)) as send:
            with self.assertRaisesRegex(wc.claude.HandoffError, "reserved"):
                self.post()
            with self.assertRaisesRegex(wc.claude.HandoffError, "earlier exchange"):
                self.post()
            self.assertEqual(send.call_count, 1)
        stored = json.loads(collab.path_for(self.identifier).read_text())
        self.assertEqual(stored["exchanges"][0]["status"], "uncertain")

    def test_reply_rejects_unrelated_chain_before_send(self):
        self.join()
        ticket = {"id": TICKET_ID, "chainId": CHAIN_ID,
                  "from": {"harness": "codex", "sessionId": CODEX_ID},
                  "to": {"harness": "claude", "sessionId": CLAUDE_ID}}
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "", "CLAUDE_CODE_SESSION_ID": CLAUDE_ID}), \
                patch.object(collab, "native", return_value=ticket) as send:
            with self.assertRaisesRegex(wc.claude.HandoffError, "outside"):
                collab.exchange(collab.parser().parse_args(["reply", self.identifier, TICKET_ID, "--message", "Question"]))
            self.assertEqual(send.call_count, 1)

    def test_reply_accepts_recorded_chain_and_exact_peer(self):
        self.join()
        with patch.object(collab, "native", return_value=self.receipt()):
            self.post()
        ticket = {"id": TICKET_ID, "chainId": CHAIN_ID,
                  "from": {"harness": "codex", "sessionId": CODEX_ID},
                  "to": {"harness": "claude", "sessionId": CLAUDE_ID}}
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "", "CLAUDE_CODE_SESSION_ID": CLAUDE_ID}), \
                patch.object(collab, "native", side_effect=[ticket, self.receipt()]) as send:
            collab.exchange(collab.parser().parse_args(["reply", self.identifier, TICKET_ID, "--message", "Question"]))
            self.assertEqual(send.call_args.args[0], ["reply", TICKET_ID, "--message", "Question"])


if __name__ == "__main__":
    unittest.main()
