#!/usr/bin/env python3
"""Fetch robots.txt and report allow/disallow rules for known AI and search bots.

Bot tokens verified against vendor docs (OpenAI, Anthropic, Perplexity, Google,
Apple, Common Crawl, Microsoft) as of the skill's last update. Re-check vendor
pages before treating this list as authoritative forever.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse


# robots.txt product tokens / user-agent family names commonly used in Allow/Disallow groups.
# Google-Extended and Applebot-Extended are control tokens (not always distinct HTTP UAs).
KNOWN_BOTS: tuple[tuple[str, str], ...] = (
    ("GPTBot", "OpenAI training crawl"),
    ("OAI-SearchBot", "OpenAI ChatGPT search indexing"),
    ("ChatGPT-User", "OpenAI user-triggered fetch (robots may not apply)"),
    ("ClaudeBot", "Anthropic training crawl"),
    ("Claude-SearchBot", "Anthropic search indexing"),
    ("Claude-User", "Anthropic user-triggered fetch"),
    ("PerplexityBot", "Perplexity search indexing"),
    ("Perplexity-User", "Perplexity user-triggered fetch (often ignores robots)"),
    ("Google-Extended", "Google Gemini training/grounding control token"),
    ("Googlebot", "Google web search crawl"),
    ("Bingbot", "Microsoft Bing crawl"),
    ("CCBot", "Common Crawl"),
    ("Applebot-Extended", "Apple AI / Apple Intelligence control token"),
)


@dataclass
class Rule:
    user_agent: str
    path: str
    allow: bool


def normalize_site(site: str) -> str:
    site = site.strip()
    if not site:
        raise ValueError("site URL is empty")
    if "://" not in site:
        site = "https://" + site
    parsed = urlparse(site)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"invalid site URL: {site!r}")
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_robots(site: str, timeout: float) -> tuple[str, str]:
    robots_url = urljoin(site.rstrip("/") + "/", "robots.txt")
    req = urllib.request.Request(
        robots_url,
        headers={"User-Agent": "aeo-audit-check_ai_crawlers/1.0 (+stdlib urllib)"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            body = resp.read().decode(charset, errors="replace")
            final_url = resp.geturl()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            f"HTTP {exc.code} fetching {robots_url}: {exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch {robots_url}: {exc.reason}") from exc
    return final_url, body


def parse_robots(text: str) -> list[tuple[list[str], list[Rule]]]:
    """Return list of (user_agent_list, rules) groups in file order."""
    groups: list[tuple[list[str], list[Rule]]] = []
    current_agents: list[str] = []
    current_rules: list[Rule] = []
    saw_agent = False

    def flush() -> None:
        nonlocal current_agents, current_rules, saw_agent
        if saw_agent:
            groups.append((current_agents, current_rules))
        current_agents = []
        current_rules = []
        saw_agent = False

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key_l = key.strip().lower()
        value = value.strip()
        if key_l == "user-agent":
            if current_rules and saw_agent:
                # New agent after rules starts a new group (common robots style).
                flush()
            current_agents.append(value)
            saw_agent = True
        elif key_l in ("allow", "disallow") and saw_agent:
            current_rules.append(
                Rule(user_agent="", path=value, allow=(key_l == "allow"))
            )
        elif key_l == "sitemap":
            continue
        elif key_l == "crawl-delay":
            continue
        else:
            # Unknown directive; ignore for allow/disallow reporting.
            continue
    flush()
    return groups


def matching_groups(
    groups: Iterable[tuple[list[str], list[Rule]]], bot: str
) -> list[list[Rule]]:
    bot_l = bot.lower()
    specific: list[list[Rule]] = []
    wildcard: list[list[Rule]] = []
    for agents, rules in groups:
        agents_l = [a.lower() for a in agents]
        if any(a == bot_l or bot_l in a or a in bot_l for a in agents_l):
            specific.append(rules)
        elif any(a == "*" for a in agents_l):
            wildcard.append(rules)
    return specific if specific else wildcard


def summarize_rules(rules: list[Rule]) -> str:
    if not rules:
        return "no explicit Allow/Disallow (effectively allow all for this group)"
    parts: list[str] = []
    for rule in rules:
        verb = "Allow" if rule.allow else "Disallow"
        path = rule.path if rule.path != "" else "(empty path)"
        parts.append(f"{verb}: {path}")
    return "; ".join(parts)


def path_blocked(rules: list[Rule], path: str = "/") -> bool:
    """True if path is disallowed; False if allowed (including no matching rule)."""
    if not rules:
        return False
    # Longest-matching-prefix among rules that apply to this path (RFC 9309-ish).
    best_len = -1
    best_allow = True
    for rule in rules:
        # Disallow with empty path means allow all.
        if rule.path == "" and not rule.allow:
            continue
        p = rule.path if rule.path != "" else "/"
        if path.startswith(p):
            if len(p) > best_len:
                best_len = len(p)
                best_allow = rule.allow
    return not best_allow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report robots.txt rules for known AI and search crawlers."
    )
    parser.add_argument(
        "site",
        help="Site origin or URL (e.g. https://example.com or example.com)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=20.0,
        help="HTTP timeout in seconds (default: 20)",
    )
    args = parser.parse_args(argv)

    try:
        site = normalize_site(args.site)
        robots_url, body = fetch_robots(site, args.timeout)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    groups = parse_robots(body)
    print(f"Site: {site}")
    print(f"robots.txt: {robots_url}")
    print(f"Groups parsed: {len(groups)}")
    print()
    print(f"{'Bot':<22} {'Root / blocked?':<16} Rules")
    print("-" * 88)

    for bot, purpose in KNOWN_BOTS:
        matched = matching_groups(groups, bot)
        if not matched:
            status = "no match"
            detail = "no matching or * group — crawlers typically treat as allow"
            blocked = False
        else:
            # Merge rules from all matching groups for display.
            merged: list[Rule] = []
            for rules in matched:
                merged.extend(rules)
            blocked_flag = path_blocked(merged, "/")
            status = "BLOCKED" if blocked_flag else "allowed"
            detail = f"{purpose}. {summarize_rules(merged)}"
        print(f"{bot:<22} {status:<16} {detail}")

    print()
    print(
        "Note: CDN/WAF policies can block bots even when robots.txt allows them. "
        "User-triggered fetchers may ignore robots.txt."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
