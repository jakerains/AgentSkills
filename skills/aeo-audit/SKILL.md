---
name: aeo-audit
description: "AEO, answer engine optimization, GEO, LLM visibility, getting recommended/cited by ChatGPT, Claude, Gemini, Perplexity, Google AI Overviews, AI share of voice, AI crawler access, agent-readable docs. Run a repeatable audit of how answer engines discover, cite, and recommend a product: buyer-question discovery, multi-model prompt testing, share-of-voice measurement, citation analysis, robots/CDN access checks, content and third-party corrections, plus coding-agent readiness. Use when auditing AI search visibility, fixing wrong AI answers about a product, or improving citations and recommendations."
---

# AEO audit

Run a repeatable **answer engine optimization (AEO)** audit: discover the buyer questions AI assistants answer, measure who gets mentioned/cited/recommended across models, fix technical and content gaps, then retest.

AI answers are nondeterministic. Sample the same prompt multiple times, store every run, and report ranges — not single-shot scores.

## Capabilities to use

Name capabilities, not one product's tool labels, so this works across agents:

| Need | Capability |
|------|------------|
| Find buyer questions, listicles, Reddit threads, docs | Web search |
| Read pages, robots.txt, docs, pricing | Fetch / HTTP GET |
| Run crawler checks, log greps, content probes | Shell |
| Confirm JS-dependent pages or live consumer UIs | Browser |
| Multi-model prompt runs when apps are unavailable | LLM API (optional) |
| Rankings / crawl / analytics (optional) | Third-party SEO or analytics APIs if the user already has access |

Optional data sources (use when available; fall back to manual runs + public pages otherwise): Search Console, Bing Webmaster, GA4, PostHog, Ahrefs, Semrush, Screaming Frog, DataForSEO, SerpAPI.

## Approval points

- **Do not** email authors, post on third-party sites, or open support tickets without the user sending them. Draft corrections and outreach; the user sends.
- Ask before spending paid API credits or writing to production analytics.
- Ask before changing live robots.txt, CDN/WAF bot rules, or production docs.

## Workflow

Copy the report skeleton from `assets/audit-report-template.md` at the start. Fill it as you go.

### 1. Scope and baseline

Capture:

- Product name, one-line description, category
- Primary competitors (5–10) and known lookalikes
- Personas, markets/locales, and languages
- Current goals (more citations, correct pricing, displace a competitor, coding-agent install success)

Record the audit date and the models/locales you will test.

### 2. Buyer-question discovery

Mine questions buyers ask **AI assistants**, not classic Google keyword lists:

- Sales calls, support tickets, onboarding FAQs
- Reddit, forums, review sites, comparison threads
- Split jargon (category slang) vs plain buyer language
- Segment by persona, budget, country, and use case

Cover patterns: `best X`, `X vs Y`, alternatives, pricing, "is X worth it", "X for [use case]".

Keep a running list of untracked competitors that appear in answers.

### 3. Prompt matrix

Build two matrices:

1. **Discovery (unbranded)** — score share of voice here. No brand name in the prompt.
2. **Branded** — run separately. Catch wrong prices, invented features, and confusion with another company. Do not fold branded results into the discovery score.

For each prompt record: persona, locale, intent bucket, and whether branded.

### 4. Multi-model testing

Run the matrix across consumer surfaces when possible: ChatGPT, Claude, Gemini, Perplexity, Google AI Overviews / AI Mode. Note that **API answers often differ from consumer apps**, and answers vary by country.

For each prompt × model × locale:

- Run at least 3 samples when stakes are high (share-of-voice claims, launch decisions)
- Store prompt, full answer, date/time, model/product surface, locale
- Mark mention / citation / recommendation separately (see step 5)

Rerun on a cadence (monthly or after major competitor or model changes).

### 5. Measurement

Track separately:

| Signal | Meaning |
|--------|---------|
| Mention | Brand named in the answer |
| Citation | A URL attributed / linked |
| Recommendation | Brand positioned as a fit / pick |

Also record position (1st pick vs buried), share of voice vs every competitor, questions where **nobody** is recommended, and newly discovered competitors.

**For scoring detail and SOV formulas**: see `references/measurement-and-citations.md`.

### 6. Citation analysis

Save every cited URL. Cluster by domain. Ask why the model trusts those pages:

- "Best X tools" listicles
- Reddit threads and YouTube videos
- G2 / Capterra / GitHub (often stale)
- Docs, blogs, comparison pages

Check that the company description, pricing, and feature claims are consistent everywhere that gets cited.

### 7. Technical access

Verify AI systems can actually fetch what they need:

1. `robots.txt` rules for major AI and search bots — run `scripts/check_ai_crawlers.py`
2. CDN / WAF bot blocking (for example Cloudflare AI bot policies) that can override robots.txt
3. Important content readable **without JavaScript** — run `scripts/check_js_free_content.py` when you have expected phrases
4. Server or CDN logs for AI bot user agents (optional: `scripts/grep_ai_bot_logs.py`)
5. Indexing, canonicals, dead URLs on cited pages
6. Pricing and feature limits present in crawler-readable HTML, not only in client-rendered widgets

### 8. Content fixes

Prioritize pages and sources that move answers:

- Pages built around real buyer questions from the matrix
- Honest competitor comparisons (models punish thin puff pieces)
- Original benchmarks or research worth citing
- Update stale prices, features, integrations
- Fix pages AI already cites but that do not lead to a recommendation of you
- Trace incorrect claims to their source pages
- Draft outreach to third-party sites (listicles, directories, GitHub READMEs) — **user sends**
- Keep product docs and changelogs current

### 9. Prioritize and ship

1. Tie gaps to business impact (lost demos, wrong pricing, competitor default)
2. Rank fixes: technical blockers → high-traffic question gaps → citation corrections → nice-to-haves
3. Write, review, ship
4. Rerun the original questions; compare ranges to baseline
5. Track AI referrals, signups, and demos when analytics exist
6. Repeat when competitors, pricing, or models change

### 10. Devtool / coding-agent readiness

If the product has an SDK, CLI, or API that coding agents install, run the separate checklist:

**Read when auditing developer tools**: `references/devtool-agent-readiness.md`

## Deliverable

Produce a filled `assets/audit-report-template.md` (or equivalent) with:

- Scope and cadence
- Prompt matrix
- Per-model results (with sample counts / ranges)
- Share-of-voice table
- Citation sources
- Technical findings
- Prioritized fix list with owners and status

## Scripts

| Script | When |
|--------|------|
| `scripts/check_ai_crawlers.py` | Step 7 — fetch `robots.txt` and report allow/disallow for known AI/search bots |
| `scripts/check_js_free_content.py` | Step 7 — compare raw HTML to expected phrases (JS-free readability) |
| `scripts/grep_ai_bot_logs.py` | Step 7 — scan access logs for AI bot user agents |

All scripts are stdlib-only Python. Run with `--help` for usage.
