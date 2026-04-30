#!/usr/bin/env python3
"""Quick heuristic checker for Kain-style X drafts.

Usage:
    echo "Oh snap. This looks rad." | ./scripts/check_draft.py
    ./scripts/check_draft.py draft.txt

The script does not decide quality. It catches obvious anti-patterns before a
draft is handed back.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


CORPORATE_WORDS = {
    "leverage",
    "empower",
    "synergy",
    "best-in-class",
    "fast-paced",
    "transformative",
    "seamless integration",
}

KAIN_MARKERS = {
    "wait",
    "woah",
    "woaahhh",
    "uhhhh",
    "oh snap",
    "haha",
    "lol",
    "love",
    "rules",
    "rad",
    "sick",
    "crazy",
    "wild",
    "dig it",
    "quality of life",
    "build cool things",
    "make cool things",
    "real world",
    "insane unlock",
    "full stop",
    "sir..",
    "codex",
    "browser",
    "button",
    "claude",
    "openai",
    "warp",
    "firecrawl",
    "elevenlabs",
    "mcp",
    "cli",
    "surface",
    "harness",
    "computer use",
    "api",
    "pricing",
    "phone",
    "server",
    "desktop app",
    "workflow",
    "tokens",
    "context",
    "model",
    "agents",
    "imagegen",
    "benchmarkmaxxing",
    "tokenmaxxing",
}


def read_input() -> str:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).read_text()
    return sys.stdin.read()


def main() -> int:
    text = read_input().strip()
    if not text:
        print("No draft supplied.")
        return 1

    lowered = text.lower()
    warnings: list[str] = []

    if len(text) > 280:
        warnings.append(f"Over 280 chars ({len(text)}). Fine for a thread, long for a Kain tweet.")

    hashtags = re.findall(r"#\w+", text)
    if len(hashtags) > 2:
        warnings.append(f"Hashtag-heavy ({len(hashtags)}). Kain usually uses 0-1.")

    exclamations = text.count("!")
    if exclamations > 4:
        warnings.append(f"Very shouty ({exclamations} exclamation points). Keep the chaos intentional.")

    corporate_hits = sorted(word for word in CORPORATE_WORDS if word in lowered)
    if "unlock" in lowered and "insane unlock" not in lowered:
        corporate_hits.append("unlock")
    if corporate_hits:
        warnings.append("Corporate wording detected: " + ", ".join(corporate_hits))

    marker_hits = sorted(marker for marker in KAIN_MARKERS if marker in lowered)
    if not marker_hits:
        warnings.append("No obvious Kain markers. Add a reaction, product noun, or operator detail.")

    long_lines = [line for line in text.splitlines() if len(line) > 150]
    if long_lines:
        warnings.append("Long line detected. Kain usually works in shorter bursts.")

    if warnings:
        print("Potential issues:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("No obvious off-voice flags.")

    if marker_hits:
        print("Detected Kain markers: " + ", ".join(marker_hits[:8]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
