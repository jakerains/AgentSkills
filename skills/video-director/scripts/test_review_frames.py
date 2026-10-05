#!/usr/bin/env python3
"""Behavior checks using lossless fixtures with known pixels and presentation times."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).with_name("review_frames.py")


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Needs FFmpeg and ffprobe")
class ReviewFramesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="video-director-test-")
        cls.root = Path(cls.temp.name)
        cls.colors = [(10 + 20 * i, 30 + 10 * i, 50 + 5 * i) for i in range(10)]
        for i, color in enumerate(cls.colors):
            Image.new("RGB", (96, 64), color).save(cls.root / f"image-{i:02d}.png")
        cls.cfr = cls.root / "CFR source with spaces.mkv"
        cls.encode(["-framerate", "10", "-i", str(cls.root / "image-%02d.png"),
                    "-c:v", "ffv1", "-pix_fmt", "bgr0", str(cls.cfr)])
        concat = cls.root / "vfr-input.txt"
        concat.write_text("".join(f"file 'image-{i:02d}.png'\nduration {duration}\n"
                                   for i, duration in enumerate([0.04, 0.24, 0.08, 0.12]))
                          + "file 'image-03.png'\n", encoding="utf-8")
        cls.vfr = cls.root / "VFR source.mkv"
        cls.encode(["-f", "concat", "-safe", "0", "-i", str(concat), "-fps_mode", "vfr",
                    "-c:v", "ffv1", "-pix_fmt", "bgr0", str(cls.vfr)])

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    @staticmethod
    def encode(args):
        subprocess.run(["ffmpeg", "-v", "error", *args], check=True, capture_output=True)

    def capture(self, source, output, *args):
        return subprocess.run([sys.executable, str(SCRIPT), str(source), "--out", str(output), *args],
                              capture_output=True, text=True)

    def assert_pixels(self, output, manifest, color_indices):
        for record in manifest["frames"]:
            with Image.open(output / record["path"]) as frame:
                self.assertEqual(frame.size, (96, 64))
                self.assertEqual(frame.getpixel((20, 20)), self.colors[color_indices[record["frame"]]])

    def test_cfr_exact_content_strips_and_fingerprint(self):
        output = self.root / "cfr review"
        result = self.capture(self.cfr, output, "--times", "0.11,0.62", "--strip-at", "0.4", "--radius", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual([r["frame"] for r in manifest["frames"]], [0, 1, 3, 4, 5, 6, 9])
        self.assertEqual(manifest["source_sha256"], hashlib.sha256(self.cfr.read_bytes()).hexdigest())
        self.assertEqual(manifest["strips"][0]["frames"], [3, 4, 5])
        self.assertEqual([r["frame"] for r in manifest["requested_samples"]], [1, 6])
        self.assert_pixels(output, manifest, list(range(10)))
        for name in ["contact-sheet.png", "strip-00.png"]:
            with Image.open(output / name) as sheet:
                sheet.verify()

    def test_vfr_uses_actual_timestamps(self):
        output = self.root / "vfr review"
        result = self.capture(self.vfr, output, "--times", "0.15,0.17", "--strip-at", "0.36", "--radius", "1")
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual([r["frame"] for r in manifest["requested_samples"]], [1, 2])
        actual = [r["seconds"] for r in manifest["frames"]]
        self.assertEqual(len(actual), 5)
        for timestamp, expected in zip(actual, [0, 0.04, 0.28, 0.36, 0.48]):
            self.assertAlmostEqual(timestamp, expected, places=5)
        self.assert_pixels(output, manifest, [0, 1, 2, 3, 3])

    def test_existing_evidence_is_preserved(self):
        output = self.root / "existing"
        output.mkdir()
        marker = output / "owner-note.txt"
        marker.write_text("Preserve this evidence.")
        result = self.capture(self.cfr, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)
        self.assertEqual(marker.read_text(), "Preserve this evidence.")
        self.assertEqual(list(output.iterdir()), [marker])

    def test_invalid_times_leave_no_candidate(self):
        for index, times in enumerate(["nan", "inf", "-1", "bad", "99"]):
            output = self.root / f"invalid-{index}"
            with self.subTest(times=times):
                result = self.capture(self.cfr, output, "--times", times)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())

    def test_default_sampling_includes_real_endpoints(self):
        output = self.root / "default review"
        result = self.capture(self.cfr, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual([r["frame"] for r in manifest["frames"]], list(range(10)))
        self.assert_pixels(output, manifest, list(range(10)))


if __name__ == "__main__":
    unittest.main()
