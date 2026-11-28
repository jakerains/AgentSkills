#!/usr/bin/env python3
"""Scan access-log files for known AI / search bot user-agent substrings.

Reads local log files only (no network). Useful when CDN or origin logs are
exported to disk. Does not claim bot authenticity — anyone can spoof a UA.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


BOT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("GPTBot", re.compile(r"GPTBot", re.I)),
    ("OAI-SearchBot", re.compile(r"OAI-SearchBot", re.I)),
    ("ChatGPT-User", re.compile(r"ChatGPT-User", re.I)),
    ("ClaudeBot", re.compile(r"ClaudeBot", re.I)),
    ("Claude-SearchBot", re.compile(r"Claude-SearchBot", re.I)),
    ("Claude-User", re.compile(r"Claude-User", re.I)),
    ("PerplexityBot", re.compile(r"PerplexityBot", re.I)),
    ("Perplexity-User", re.compile(r"Perplexity-User", re.I)),
    ("Google-Extended", re.compile(r"Google-Extended", re.I)),
    ("Googlebot", re.compile(r"Googlebot", re.I)),
    ("Bingbot", re.compile(r"bingbot", re.I)),
    ("CCBot", re.compile(r"CCBot", re.I)),
    ("Applebot-Extended", re.compile(r"Applebot-Extended", re.I)),
    ("Applebot", re.compile(r"Applebot(?!-Extended)", re.I)),
)


def iter_lines(path: Path):
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                yield line.rstrip("\n")
    except OSError as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Count AI/search bot user agents in access log files."
    )
    parser.add_argument(
        "logs",
        nargs="+",
        type=Path,
        help="One or more access log file paths",
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=2,
        help="Example matching lines to print per bot (default: 2)",
    )
    args = parser.parse_args(argv)

    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = {name: [] for name, _ in BOT_PATTERNS}
    total_lines = 0

    for log_path in args.logs:
        if not log_path.is_file():
            print(f"error: not a file: {log_path}", file=sys.stderr)
            return 1
        try:
            for line in iter_lines(log_path):
                total_lines += 1
                for name, pattern in BOT_PATTERNS:
                    if pattern.search(line):
                        counts[name] += 1
                        if len(examples[name]) < args.examples:
                            examples[name].append(line[:300])
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    print(f"Files: {', '.join(str(p) for p in args.logs)}")
    print(f"Lines scanned: {total_lines}")
    print()
    print(f"{'Bot':<22} {'Hits':>8}")
    print("-" * 32)
    for name, _ in BOT_PATTERNS:
        print(f"{name:<22} {counts[name]:>8}")

    if args.examples > 0:
        print()
        for name, _ in BOT_PATTERNS:
            if examples[name]:
                print(f"## {name} examples")
                for ex in examples[name]:
                    print(f"  {ex}")
                print()

    print(
        "Note: user-agent strings can be spoofed. Prefer verifying against "
        "vendor-published IP ranges when making allow/block decisions."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
