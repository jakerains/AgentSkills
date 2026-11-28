# AEO audit report

| Field | Value |
|-------|-------|
| Product | |
| Category | |
| Audit date | |
| Locales | |
| Models / surfaces tested | |
| Samples per prompt | |
| Analyst | |
| Next cadence | |

## 1. Scope and baseline

**Product one-liner:**

**Personas:**

**Markets:**

**Competitors (initial):**

**Goals:**

## 2. Prompt matrix

| ID | Prompt | Branded? | Persona | Locale | Intent bucket |
|----|--------|----------|---------|--------|---------------|
| P01 | | no | | | best-of |
| P02 | | no | | | vs |
| P03 | | yes | | | pricing |

## 3. Per-model results

Record ranges across samples. Legend: M = mention, C = citation, R = recommendation (primary/secondary/none).

### Model: _

| Prompt ID | Samples | Mention rate | Citation rate | Rec. rate | Typical position | Notes |
|-----------|---------|--------------|---------------|-----------|------------------|-------|
| P01 | 3 | 2/3 | 1/3 | 1/3 primary | 2 | |

### Branded accuracy

| Prompt ID | Model | Wrong price? | Invented features? | Confused with | Notes |
|-----------|-------|--------------|--------------------|---------------|-------|
| | | | | | |

## 4. Share of voice (discovery prompts only)

| Brand | Mention SOV | Citation SOV | Recommendation SOV | Notes |
|-------|-------------|--------------|--------------------|-------|
| (you) | | | | |
| Competitor A | | | | |
| Competitor B | | | | |
| Untracked: _ | | | | |

Questions where nobody was recommended:

## 5. Citation sources

| Domain | Type | # cites | Favors | Freshness | Action |
|--------|------|---------|--------|-----------|--------|
| | listicle | | | | |

## 6. Technical findings

| Check | Result | Evidence | Severity |
|-------|--------|----------|----------|
| robots.txt AI bots | | `check_ai_crawlers.py` output | |
| CDN/WAF bot policy | | | |
| JS-free critical content | | `check_js_free_content.py` | |
| AI bot log activity | | | |
| Canonicals / dead URLs | | | |
| Pricing crawler-readable | | | |

## 7. Coding-agent readiness (if applicable)

| Check | Pass? | Notes |
|-------|-------|-------|
| Agents recommend product | | |
| Clean install from docs | | |
| Examples match current SDK | | |
| Auth works headless | | |
| Live task succeeds | | |

## 8. Prioritized fix list

| Priority | Gap | Impact | Fix | Owner | Status |
|----------|-----|--------|-----|-------|--------|
| P0 | | | | | |
| P1 | | | | | |
| P2 | | | | | |

## 9. Retest log

| Date | What changed | Prompts rerun | SOV / accuracy delta |
|------|--------------|---------------|----------------------|
| | | | |

## Assumptions and limits

- AI answers vary by run, locale, and product surface; treat scores as ranges.
- API results may not match consumer apps.
- Optional SEO/analytics tools were: [used / not available].
