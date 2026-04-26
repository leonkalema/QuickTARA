---
name: search-engine-optimization
description: Conducts technical and content SEO to increase organic visibility and qualified traffic. Use when auditing indexability/crawlability, improving on-page SEO, adding structured data, planning topic clusters, optimizing Core Web Vitals, or measuring with Search Console/GA4. Produces prioritized fixes, content briefs, internal linking plans, and guardrails to prevent regressions.
license: Complete terms in LICENSE.txt
---

# Search Engine Optimization

## Principles
- Users first, matched to intent; sustainable wins over hacks.
- Measure → prioritize → ship small, high-impact improvements.
- Technical foundations before content amplification.
- Avoid duplication and cannibalization; build topical authority.

## Instructions

### Step 1: Define goals and baseline
- KPIs: impressions, clicks, CTR, avg position (GSC), sessions and conversions (GA4).
- Identify priority templates (home, category, article/product, landing pages).
- Snapshot current titles/meta, headings, CWV, schema, sitemaps, internal links.

### Step 2: Technical SEO
- Indexability: robots.txt, `noindex`, canonical tags, redirect chains/loops, 404/410.
- Site structure: clean URLs, breadcrumbs, logical hierarchy, avoid thin/faceted traps.
- Canonicalization: self-referential canonicals; consolidate parameters/UTMs.
- Pagination: rel=next/prev deprecated—prefer keyset pagination + canonical to the primary list.
- Internationalization: hreflang per locale, x-default; consistent canonical/hreflang pairs.
- JavaScript rendering: ensure SSR/prerender for critical content or dynamic rendering.
- Media: descriptive filenames/alt text; responsive images (`srcset`, `sizes`); lazy-load below the fold.
- Sitemaps: separate XML sitemaps per type; keep sizes <50k URLs/50MB; reference in `sitemap_index.xml` and robots.txt.

### Step 3: Core Web Vitals (CWV) and performance
- Focus on LCP, CLS, INP.
- Improve LCP: responsive images, preconnect/preload critical resources, serve optimized hero media, reduce server TTFB.
- Reduce CLS: reserve space for images/ads; avoid layout shifts on font/ads.
- Improve INP: reduce JS bloat, avoid long tasks; defer non-critical scripts; split bundles.
- Measure with Lighthouse, PageSpeed Insights, and CrUX; track p75 field data.

### Step 4: On-page optimization
- Titles: unique, intent-aligned, benefit-led; avoid truncation; include primary keyword naturally.
- Meta descriptions: compelling summaries; drive CTR; avoid duplication.
- Headings: one H1, logical H2/H3 structure; cover related subtopics and FAQs.
- Content quality: satisfy search intent fully; add unique insights, data, visuals; avoid fluff.
- Internal links: descriptive anchors; link hubs↔spokes; surface orphan pages.

### Step 5: Structured data (JSON-LD)
- Apply relevant schemas (e.g., Organization, BreadcrumbList, Article/NewsArticle, Product, FAQPage, HowTo, WebSite/SearchAction).
- Validate with Rich Results Test; keep data consistent with page content.

### Step 6: Content strategy and topic clusters
- Research: query variants, People Also Ask, competitors, SERP features.
- Map search intents to pages; avoid multiple pages targeting the same primary term.
- Build hub (pillar) pages with spoke articles; plan internal linking.

### Step 7: Measurement and reporting
- GSC: coverage, queries/pages, CTR opportunities, sitemaps, manual actions.
- GA4: landing pages, engagement, conversions; attribution sanity checks.
- Track rankings for target terms; annotate releases/tests; report monthly.

### Step 8: Guardrails and deployment checks
- Preflight: robots.txt, sitemaps present, canonicals correct, no accidental `noindex`.
- Redirect maps for URL changes; monitor 404s/soft-404s; alert on 5xx.
- CWV budgets in CI; structured data validation; title/meta linting for duplicates.

## Checklists

### Page-level checklist
- Unique title/meta; single H1; structured subheads.
- Primary query and synonyms present naturally; answers intent.
- Internal links to hub/spokes; images with alt and compression.

### Technical checklist
- 200 status for canonical URL; canonical/self-consistent.
- In sitemap; not blocked by robots; no conflicting `noindex`.
- Hreflang pairs valid (if multilingual); pagination/canonicalization sane.

### Structured data checklist
- Appropriate type present; required/recommended fields filled.
- No mismatches with visible content; validated without errors.

### CWV checklist
- LCP < 2.5s; CLS < 0.1; INP < 200ms (p75 field data goals).
- Fonts: `font-display: swap`; critical CSS; minimal render-blocking JS.

## Patterns
- Hub-and-spoke topic clusters to build topical authority.
- Programmatic SEO with templates (ensure uniqueness + quality safeguards).
- Faceted navigation control: canonical to unfiltered, block crawl of explosive combinations.
- Content decay watchlist: refresh declining winners.

## Troubleshooting
- Sudden traffic drop: check robots.txt, `noindex`, 5xx spikes, DNS/cert issues, manual actions.
- Duplicate content: consolidate with canonical and redirects; merge/refresh cannibalized pages.
- JS-only content not indexed: add SSR/prerender; ensure content in initial HTML.
- Soft-404s: improve content depth/unique value; ensure correct status codes.
