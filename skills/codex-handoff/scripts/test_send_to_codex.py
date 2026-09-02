#!/usr/bin/env python3
"""Deterministic tests for send_to_codex.py; no live message is queued."""

from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("send_to_codex.py")
SPEC = importlib.util.spec_from_file_location("send_to_codex", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

THREAD_ID = "123e4567-e89b-12d3-a456-426614174000"


class NormalizeThreadTargetTests(unittest.TestCase):
    def test_accepts_raw_uuid(self) -> None:
        self.assertEqual(MODULE.normalize_thread_target(THREAD_ID), THREAD_ID)

    def test_accepts_deep_link_with_query(self) -> None:
        link = f"codex://threads/{THREAD_ID}?host=local"
        self.assertEqual(MODULE.normalize_thread_target(link), THREAD_ID)

    def test_rejects_non_codex_url(self) -> None:
        with self.assertRaises(MODULE.HandoffError):
            MODULE.normalize_thread_target(f"https://example.com/{THREAD_ID}")

    def test_rejects_extra_path_segments(self) -> None:
        with self.assertRaises(MODULE.HandoffError):
            MODULE.normalize_thread_target(f"codex://threads/{THREAD_ID}/extra")


class QueueMessageTests(unittest.TestCase):
    @mock.patch.object(MODULE.shutil, "which", return_value="/usr/local/bin/codex")
    @mock.patch.object(MODULE.subprocess, "run")
    def test_queues_as_argument_vector_without_a_shell(
        self,
        run: mock.Mock,
        _which: mock.Mock,
    ) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="queued\n", stderr=""
        )
        message = "[Claude handoff]\n\nOutcome:\nNo shell expansion: $HOME `pwd`."

        MODULE.queue_message(THREAD_ID, message)

        run.assert_called_once_with(
            [
                "/usr/local/bin/codex",
                "queue",
                "--thread",
                THREAD_ID,
                "--message",
                message,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

    @mock.patch.object(MODULE.shutil, "which", return_value="/usr/local/bin/codex")
    @mock.patch.object(MODULE.subprocess, "run")
    def test_surfaces_a_clear_queue_failure(
        self,
        run: mock.Mock,
        _which: mock.Mock,
    ) -> None:
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="no rollout found"
        )

        with self.assertRaisesRegex(MODULE.HandoffError, "no rollout found"):
            MODULE.queue_message(THREAD_ID, "handoff")


if __name__ == "__main__":
    unittest.main()
