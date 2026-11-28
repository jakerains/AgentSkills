# Measurement and citation analysis

Read this during audit steps 5–6 when scoring answers or clustering cited sources.

## Scoring rules

For each prompt × model × sample:

1. **Mention** — brand string (or clear alias) appears in the answer text.
2. **Citation** — a URL, domain, or named source is attributed to that brand (or the answer links a page about it).
3. **Recommendation** — the answer positions the brand as a pick, fit, or default for the asker's need. Passing mentions and "also consider" lists count as weaker recommendations; mark strength: primary / secondary / pass.

Do not collapse these into one "visibility" number without saying how you weighted them.

## Share of voice (discovery prompts only)

For a fixed prompt set P and competitor set C (include the audited brand):

- Per model: for each prompt, note which brands in C were **recommended** (primary or secondary).
- SOV for brand B = (prompts where B was recommended) / (prompts where any brand in C was recommended).
- Also report mention-SOV and citation-SOV the same way.
- Report **ranges** across samples (min–max or mean ± spread), not a single run.

Exclude branded prompts from discovery SOV. Report branded accuracy separately (correct price, correct features, correct company identity).

## Position

When multiple products are listed, record ordinal position (1 = first named pick). Presence without position understates leaders who always appear first.

## Nobody recommended

Flag prompts where the model refuses to pick, gives generic advice only, or says it cannot recommend. Those are content opportunities, not failures of measurement.

## Untracked competitors

Any brand that appears in ≥2 answers but was not in the original competitor set joins C for the next cadence. Update the matrix instead of ignoring them.

## Citation clustering

Group every cited URL by registrable domain. For each top domain note:

- Content type (listicle, docs, Reddit, YouTube, review directory, GitHub, news)
- Recency cues (dates, version numbers, changelog stamps)
- Whether the page favors a competitor, is neutral, or is outdated
- Whether your brand description there matches your current site

Prioritize correcting high-frequency domains before writing new owned content.

## Optional vendor data

If the user has Search Console, Bing Webmaster, GA4/PostHog, or SEO platforms (Ahrefs, Semrush, DataForSEO, SerpAPI):

- Use them for query volume, referring pages, and crawl anomalies
- Still validate recommendations with live multi-model samples — rankings ≠ AI recommendations

When those tools are absent, rely on stored prompt runs, manual citation lists, and public pages.
