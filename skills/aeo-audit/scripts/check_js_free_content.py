#!/usr/bin/env python3
"""Compare raw HTML (no JS execution) against expected phrases.

Use this to check whether pricing, feature limits, or other critical copy is
present in the initial HTML response that simple crawlers see.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse


class _VisibleTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript") and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self._chunks.append(text)

    def text(self) -> str:
        return " ".join(self._chunks)


def fetch(url: str, timeout: float) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"invalid URL: {url!r}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "aeo-audit-check_js_free_content/1.0 (+stdlib urllib)"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            body = resp.read().decode(charset, errors="replace")
            return resp.geturl(), body
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} fetching {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch {url}: {exc.reason}") from exc


def extract_text(html: str) -> str:
    parser = _VisibleTextExtractor()
    parser.feed(html)
    parser.close()
    return re.sub(r"\s+", " ", parser.text()).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that expected phrases appear in raw HTML without JS."
    )
    parser.add_argument("url", help="Page URL to fetch")
    parser.add_argument(
        "--expect",
        action="append",
        default=[],
        metavar="PHRASE",
        help="Phrase that must appear in visible text (repeatable)",
    )
    parser.add_argument(
        "--expect-html",
        action="append",
        default=[],
        metavar="PHRASE",
        help="Phrase that must appear in raw HTML source (repeatable)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds (default: 20)",
    )
    parser.add_argument(
        "--show-excerpt",
        action="store_true",
        help="Print a short excerpt of extracted visible text",
    )
    args = parser.parse_args(argv)

    if not args.expect and not args.expect_html:
        print(
            "error: provide at least one --expect or --expect-html phrase",
            file=sys.stderr,
        )
        return 2

    try:
        final_url, html = fetch(args.url, args.timeout)
        visible = extract_text(html)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"URL: {final_url}")
    print(f"HTML bytes (decoded chars): {len(html)}")
    print(f"Visible text chars: {len(visible)}")
    if args.show_excerpt:
        excerpt = visible[:400] + ("…" if len(visible) > 400 else "")
        print(f"Excerpt: {excerpt}")
    print()

    failures = 0
    for phrase in args.expect:
        found = phrase.lower() in visible.lower()
        status = "FOUND" if found else "MISSING"
        print(f"[visible] {status}: {phrase!r}")
        if not found:
            failures += 1
    for phrase in args.expect_html:
        found = phrase.lower() in html.lower()
        status = "FOUND" if found else "MISSING"
        print(f"[html]    {status}: {phrase!r}")
        if not found:
            failures += 1

    print()
    if failures:
        print(
            f"FAIL: {failures} phrase(s) missing from the non-JS response. "
            "Content may be client-rendered only."
        )
        return 1
    print("PASS: all phrases present in the raw response.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
