---
name: jake-speak
description: Explain technical work, product or system behavior, repo changes, decisions, findings, and concepts to Jake in plain English. Use when Jake types /jake-speak, says "Jake Speak", "explain this in Jake Speak", "Jake Speak recap", "plain-English version", "for me", "non-technical recap", or asks for the high-level human version of work just done. Preserve real product names, feature names, status, outcomes, risks, and important numbers while leaving out code mechanics. Can also create an optional standalone visual HTML recap saved outside the repo, usually on Jake's Desktop.
---

# Jake Speak

Explain the thing the way you would to a smart product-minded collaborator who
understands the goal and the stakes, but does not want the implementation
plumbing. Jake Speak is not "dumbed down." It is the product story, the
decision story, and the status story with the code mechanics removed.

## Core Promise

- Lead with what changed, what it means, and why it matters.
- Keep real names: products, features, visible surfaces, companies, people,
  dates, status labels, and important numbers.
- Drop mechanics: file paths, function names, table names, build tools,
  packages, API routes, schemas, and framework internals unless Jake asks for
  them or they are the actual user-facing thing.
- Translate unavoidable technical nouns into their human role:
  "the login provider," "the place that stores recordings," "the background
  job runner," "the hosted page."
- Be candid about certainty. Separate what is verified, what is likely, and
  what still needs checking.
- Keep consequences visible: who benefits, what risk is lower, what workflow is
  easier, what remains blocked, and what is now safe to do next.

## Workflow

1. Identify the subject from context. Ask only if the thing to explain is truly
   unclear.
2. For recaps, cover the actual work: goal, findings, decisions, shipped or
   changed pieces, verification, open risks, and where things stand. Skip noisy
   terminal details unless they explain a meaningful outcome.
3. If the explanation depends on current repo/runtime state and the state is not
   already known, check it before making claims.
4. Draft 2-6 short sections, each with one idea and one useful heading.
5. Render the answer as boxed cards in a single fenced block. Add only a short
   intro or outro if it helps.

## Card Format

Use one code fence so the line-art stays aligned. Stack one card per section
with a blank line between cards. Keep body lines around 58 characters so they
survive narrow terminals. Use a small emoji/icon when it fits; use plain words
instead if the environment may render emoji poorly.

```text
┏━━━  💰  1 · WILL THIS GET EXPENSIVE AS WE GROW?  ━━━━━━━━━━━━━
┃
┃   Verdict: nothing here looks like a time bomb.
┃   The platform is built in a way that should keep
┃   costs predictable as usage grows.
┃
┃      • lesson videos are the main thing to watch
┃      • everything else is cheap or already bounded
┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

For recaps, finish with a compact status card when it helps the whole answer
land at a glance:

```text
┌─────────────────────────────────────────────────────────────┐
│  📍  WHERE THINGS STAND                                      │
│                                                             │
│   ● Main thing ............. done and verified              │
│   ● Secondary thing ........ built, not live yet            │
│   ● Open question .......... waiting on a decision          │
└─────────────────────────────────────────────────────────────┘
```

## Voice Examples

Engineer-speak:
"Added a companion_threads table, moved mintToken server-side, and bumped
max_duration_seconds."

Jake Speak:
"We gave El a place to save conversations so they survive a reload, moved the
agent's ID somewhere private because exposing it was a security risk, and let
voice sessions run longer."

Engineer-speak:
"The webhook was firing, but the auth middleware rejected the request before the
handler ran."

Jake Speak:
"The outside service was knocking on the right door, but our gatekeeper was
turning it away before the app could respond."

## Optional Visual HTML

Create a visual HTML recap only when Jake asks for it, when the recap is
substantial enough to be reused, or when a polished artifact would clearly help.
For tiny explanations, skip the offer.

When creating HTML:

- Save a self-contained `.html` file outside any git repo. Default to
  `~/Desktop/<short-slug>-recap.html`.
- Never save it in the project tree, `.notes/`, docs folders, or any other
  versioned location unless Jake explicitly asks.
- Never stage or commit the HTML recap.
- Make zero external requests. Inline CSS and JavaScript. Use system fonts and
  emoji by default.
- If an image would genuinely improve the recap, generate or use a local image
  only after it is useful to the artifact, then embed it as a data URI so the
  page remains a single portable file.
- Confirm the absolute path after saving and say that it stayed outside the
  repo.

Use `assets/recap-template.html` as the starting point. Replace the placeholder
title, TL;DR, stat chips, section cards, and status rows with the same Jake
Speak content from the boxed cards.
