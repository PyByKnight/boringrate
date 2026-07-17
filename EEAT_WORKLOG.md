# E-E-A-T Credibility Work — Autonomous Session Log
_Started 2026-07-16 (Opus 4.8). Owner out ~1hr. Directive: run EEAT up through Fable, make optimal
improvements from data we've ALREADY primary-sourced, create notes on where to add data for better
source docs. FLAG for owner return (do NOT execute blind): (a) any new SERFF strategy; (b) mass
insertion of primary-source links across rate-change pages / articles._

## Ground truth captured before starting (what exists)
- `methodology.html` — strong plain-English sourcing page (names SERFF, regulator rate comparisons, secondary aggregator cross-checks; dated changes). Good Trust signal.
- `/press/` — journalist page: national summary, who's cutting/raising, how-we-source, "how to cite BoringRate" line, contact email. Figures link primary sources.
- `/rate-filings/` — national roll-up TABLE; EACH ROW links its primary source (SERFF tracking # + DOI portal). Best-cited/most-citable asset.
- Per-state rate-change trackers + home metro pages, all filing-driven.

## Gaps identified
- NO named author, NO About page. Bylines = generic "BoringRate Editorial · June 2026" → weakest signal for Experience + Expertise.
- Article-level citation thin: guides ASSERT claims, some link /rate-filings/, but rarely cite the specific primary filing/regulator INLINE where the claim is made. Strong citation lives on /press/ + /rate-filings/, not where search traffic lands.

## Plan (to refine with Fable)
1. Retry Fable consult (hit transient 529).
2. Execute the SAFE, clearly-good improvements (About/how-we-work org page draft, methodology/sources hardening) — no mass per-page edits.
3. Write NOTES on where to add data for better source docs (extra SERFF fields, per-filing permalinks, etc.).
4. Prepare (NOT run) the two flagged categories as ready plans for owner return.

## Architecture notes (verified)
- Nav is single-source: `partials/nav-top.html` + `partials/nav-mega.html` → `build_nav.py` stamps every .html that already has nav markers. A NEW page cloned from methodology.html inherits nav + stays in sync. SAFE.
- Footer is per-page INLINE (not single-sourced). Footer "About" + "Editorial standards" links BOTH currently point to `/methodology.html` (not broken, just suboptimal). Retargeting them = 581-page mass edit → FLAG as follow-up, do NOT run blind (patch-safety).
- Page shell to clone: methodology.html (head styles + `<header class="top">` nav + `.prose` article + minimal footer + 2 nav scripts).

## Progress log
- [t0] Captured ground truth; created this log; Fable 529'd twice → launched as background retry.
- [t1] Verified build_nav + footer architecture. Building 2 additive trust pages: /about.html + /editorial-standards.html via a gen_trust_pages.py (clones methodology shell). Then wire into nav partial + build_nav + sitemap. Writing NOTES docs in parallel.
