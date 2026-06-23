# BoringRate — Session Notes
_Last updated: 2026-06-22 (Opus 4.8)_

## This session (2026-06-23, Opus 4.8) — shipped

- **Deepened auto's partial offsets** (State Farm/Progressive/Farmers). These were
  the 3 partially-tuned nationals in `STATE_CARRIER_ADJ`. `gen_auto_offset_fill.py`
  fills MISSING states only (hand-tuned values untouched) with a per-carrier linear
  model fit to each carrier's own existing cloud: State Farm `max(0.84,0.85+0.40·
  (pct-0.5))` (cheap floor, loads priciest), Progressive `1.04-0.22·pct` (mid in
  cheap states, cheapest in pricey), Farmers `0.91+0.04·(pct-0.5)` (mild agent
  loading). Filled 14/31/46 → **State Farm 50/51, Progressive 48/51, Farmers 51/51;
  offset coverage 80.5%→93.3%** (666/714). Synced auto ledger + baselined.
  Cascaded to static rankings (`gen_state_rankings.js --export --states --metros`).
  Idempotent generator; sweep 526/526.
  CONSISTENCY CHECK (`verify_offset_consistency.py`, permanent): compares the
  model's cheapest-5/state vs article/state-rankings.html. CORRECTION to an earlier
  overstatement — that page is ALSO in-house editorial data, not external ground
  truth, so this measures cross-surface AGREEMENT, not accuracy. Nationals-only the
  Progressive steepen (0.90flat→1.04-0.22·pct) improved overlap 94.5→98%, BUT on
  the FULL active roster the tool actually shows (nationals + STATE_LOCAL_CARRIERS
  regionals) agreement is only **47.8%**: the tool surfaces low-base regionals
  (Erie/Auto-Owners/Farm Bureau/Shelter/NJM/Amica/AAA) in the top-5 while the
  editorial page lists big nationals (USAA/Root/Progressive/GEICO/State Farm).
  → OPEN STRUCTURAL QUESTION (human call): is the tool over-weighting regionals or
  is the editorial page under-listing them? Offset tuning barely moves this.
  NEXT: decide source-of-truth on the regionals-vs-nationals roster gap; NAIC grade
  verification; cross-product bundling guide.

## This session (2026-06-22, Opus 4.8) — shipped

- **Renters/home carrier-by-state offset pass** (closes the auto-parity gap).
  Both tools had NO per-state carrier variation — every national carrier kept the
  same relative rank in all 51 states (only the state avg scaled the board). Added
  auto's modeled cost-responsiveness tilt (`STATE_CARRIER_ADJ`) to renters/home
  `index.html` via `gen_product_offsets.py`: agent carriers load high-cost states
  (k>0), value/direct hold the line (k<0); applied in estimatePremium as
  `base × stateM`. Regionals (footprint `states:` array) excluded — base already
  state-appropriate, same rule as auto. **738 renters cells** (16 nationals × 48
  states) + **600 home cells** (13 × 48). Ledger tracking: extended
  `audit_rates.py scan_rh` to scan offsets; synced + baselined
  (renters 814 atoms, home 679, all fresh 2026-06-22 → next checkpoint 2026-07-22).
  Verified `verify_offsets.js` (rankings reorder MT↔LA / HI↔CO, Allstate ranks
  worse in pricier states, 0 JS errors); full sweep 526/526. Docs: RATE_METHODOLOGY
  §6 checkbox + §7.
- **State-page cascade (offset + stale-roster fix).** Folded the new offset into
  the STATIC state ranking pages and killed the documented roster-drift in one
  pass. `gen_renters_rankings.js`: grabs `STATE_CARRIER_ADJ` + ranks
  `avg×base×offset` (already read live roster/avgs). `gen_home_state_pages.py`:
  STOPPED hardcoding `STATES`/`CARRIERS` (old 12-carrier list was the drift
  source) — now parses HOME_STATE_DATA/HOME_CARRIERS(28)/STATE_CARRIER_ADJ live
  from home/index.html + ranks `avg×base×offset`. Regenerated all 51 renters +
  51 home state pages. Static pages now match the tool order by construction.
  Verified: verify_home_state.js (0 JS errors), renters LA leads w/ value
  carriers, sweep 526/526.
  NEXT: deepen auto partial offsets (State Farm/Progressive/Farmers); NAIC grade
  verification; cross-product bundling guide.

## This session (2026-06-17, Opus 4.8) — shipped

- **Auto carrier roster expanded toward 20/state** (locals + nationals). +2
  nationals (Kemper, National General) shown everywhere; +30 real regionals.
  STATE_LOCAL_CARRIERS rebuilt from per-carrier state footprints, capped at the
  6 best regionals/state. Most states now show 20; thin states real-only
  (AK 15, HI 17, MT 16, NM 15, WY 17 — no filler). Zero dead CTAs; sweep 526/526.
  NEXT: same footprint-driven expansion for renters/home (their bases/grades
  need their own pass).
- **Auto rate verification ledger** (`rate_audit.json` + `audit_rates.py`).
  Scans all 136 auto rate atoms (85 carrier base/grade/stability + 51 state
  averages). Integrity SLA: re-verify every atom at least every 30 days.
  Stores a value snapshot per atom -> detects DRIFT (code changed, not
  re-verified) and STALE (>30d). `--check` exits 1 if anything needs attention
  (CI/cron-ready). Baselined 2026-06-17 -> **next checkpoint due 2026-07-17.**
  Workflow: `audit_rates.py` (check) -> re-verify flagged atoms against source
  -> `audit_rates.py --mark <id> --source <url>` (or `--mark-all` after a full
  pass). `--sync` adds/removes atoms when the roster changes.
- **Rate methodology documented + first verification pass** (`RATE_METHODOLOGY.md`).
  Full formula, layer-by-layer source map (sourceable vs modeled), the `/2`
  display calibration finding, and a repeatable monthly process. Ledger now
  tracks the 157 documented STATE_CARRIER_ADJ offsets too (293 atoms) +
  `--coverage` report. KEY FINDINGS / open decisions:
  (a) carrier-by-state gap — only 22% of national carrier×state cells have a
  documented offset; 9 nationals (Allstate, Liberty Mutual, Nationwide,
  Travelers, Safeco, The Hartford, Root, Kemper, National General) use the
  national base in ALL states;
  (b) state averages reconciled vs ValuePenguin 2026-06-16 (national matches,
  but 11 states >20% off — CO is −48% and almost certainly wrong);
  (c) `/2` calibration makes displayed prices ~half full-coverage average, and
  `state_rankings.json` uses un-halved math — needs reconciliation.
  NEXT BATCH: NAIC complaint ratios for CS grades.
- **Rate corrections + per-vehicle consistency (3-part).**
  (1) Fixed 11 state averages >20% off vs ValuePenguin (CO 1706->3264, MI
  4724->3120 cross-checked, GA/CA/MA/FL/NY/WY/IA/KS/HI).
  (2) Closed the carrier-by-state gap: modeled cost-responsiveness offsets for
  the 9 untuned nationals -> STATE_CARRIER_ADJ coverage 22%->80.5% (711 atoms).
  (3) Removed the legacy `/2` in index.html so auto is per-vehicle like
  renters/home; regenerated state_rankings.json (gen_state_rankings.js --export),
  state+metro article tables (--states/--metros), rate-change pages
  (gen_rate_tracker.py), and synced STATE_DATA in coverage.html +
  article/state-rankings.html (STATES array + embedded rates + MAX_PRICE 4612).
  All state-avg sources now agree; CA tool median $2,628 ≈ published $2,652.
  526/526 sweep clean. See RATE_METHODOLOGY.md (action items checked off).
  NEXT: deepen partial offsets (State Farm/Progressive/Farmers); NAIC grade
  verification; replicate per-vehicle + offset passes for renters/home.

## This session (2026-06-16d, Opus 4.8) — shipped

- **Coverage calculator UX rebuild (home + renters).** User flagged the home tool
  as confusing; root cause = the renters/home tools used a simpler engine than the
  auto tool. Rebuilt BOTH (renters shares the engine):
  per-card PRICE-IMPACT chips with exact deltas (totalWith/deltaVs helper);
  inline expand/collapse 'What is this?' (no page jump) + removed the redundant
  bottom primer; previously-locked coverages now adjustable (home: Other
  Structures 10/20% + Loss of Use 20/30%; renters: Loss of Use 20/30%); ⓘ tooltips
  on every input; sticky premium box now has a ZIP entry + Compare CTA; ZIP
  auto-fills across profile/bottom/sticky and carries selections to the rate tool.
  Also fixed the clipped ZIP placeholder (110px->150px) on all 3 coverage tools.
  jsdom: 0 JS errors; full sweep 526/526. (Auto coverage.html already had deltas/
  inline-expand — all 3 now consistent.)

## This session (2026-06-16c, Opus 4.8) — shipped

- **Guide/FAQ parity across all 3 products.** Renters cluster -> 6 guides
  (worth-it, covers, does-it-cover, required, how-much-needed, cost). Home cluster
  -> 5 guides (how-much-needed [rebuild cost/80% rule], covers, does-it-cover,
  required [mortgage/HO-6], cost). Built by gen_renters_faq.py / gen_home_faq.py
  (config-driven). Each: product two-tile CTA + FAQPage JSON-LD. Wired via new
  'Renters guides' / 'Home guides' nav subsections (single-source partial +
  build_nav.py) + sitemap + tool contextual links.
  MILESTONE: every product (auto/renters/home) now has rate tool + coverage tool +
  article tree + guide cluster. 526 pages, 0 JS errors.
  NEXT: cross-product BUNDLING guide (now that all 3 have content it can link them);
  optional home metro tree / renters metro de-dup; per-product 'cheapest for' if
  demand warrants.

## This session (2026-06-16b, Opus 4.8) — shipped

- **Auto: discounts guide** (`/article/car-insurance-discounts.html`) — last clean
  auto FAQ gap. Auto is now considered complete for the funnel (methodology page
  already solid at 2.3k words; remaining ideas — bundling, per-state minimums,
  minor-ticket factor — are defer/low-value).
- **RENTERS guides STARTED** (renters had tools, zero content). `gen_renters_faq.py`
  built the first 3: is-renters-insurance-worth-it, what-does-renters-insurance-
  cover, does-renters-insurance-cover (scenario long-tail). Renters two-tile CTA
  (-> /renters/ + /renters/coverage.html), FAQPage JSON-LD. Wired via new "Renters
  guides" nav subsection (single-source) + sitemap + renters-tool link.
  NEXT for renters: is-renters-insurance-required, how-much-do-i-need (complement
  the calc), cost/by-state angle; then HOME guides (also zero content); then a
  cross-product bundling guide. All 518 pages 0 JS errors.

## This session (2026-06-16, Opus 4.8) — shipped

- **FAQ / high-intent content cluster (6 auto articles).** Tool-driving FAQ pages,
  all funneling to the ZIP tool, via reusable generators:
  - `cost-of-not-shopping-car-insurance` (interactive estimator; ~$550 spread from
    OUR model) — `gen_hidden_cost.py`
  - `how-to-switch-car-insurance`, `does-car-insurance-follow-the-car-or-driver`,
    `how-long-does-an-accident-stay-on-your-insurance`, `does-car-insurance-cover`,
    `driving-without-car-insurance` — `gen_faq_articles.py` (config-driven, easy to
    extend). Each has FAQPage JSON-LD + two-tile CTA.
  All wired via the single-source guides panel (edit `partials/nav-mega.html` →
  `build_nav.py`), article hub cards, + sitemap. 514/514 pages 0 JS errors.
  OPEN FAQ ideas: renters/home FAQ equivalents; "does it cover" deep-dives.

## This session (2026-06-15, Opus 4.8) — shipped

- **NAV: single-source mega menu + regrouped Guides.** Extracted the hamburger
  mega menu to `partials/nav-mega.html`; `build_nav.py` stamps it into all 506
  pages (idempotent). Future nav edits = edit partial + run build_nav.py (nav
  stays in static HTML for SEO). Unified 7 drifted nav variants -> 1. Guides panel
  regrouped into subsections: Cheapest for… / How-to guides / Data & tools (incl.
  the 5 new high-intent pages). 0 JS errors. See [[boringrate-nav-singlesource]].


- **HIGH-INTENT "cheapest for [situation]" articles + model alignment.** Built 5
  ranking-led pages (`article/cheapest-car-insurance-*`): young-drivers, after-
  accident, after-dui (SR-22), bad-credit, seniors. Each leads with **top-3 +
  bottom-3** (bottom-3 = "you're likely overpaying → shop"), a ZIP CTA carrying
  `?sit=<situation>`, and honest how-to-save content. Top/bottom computed from the
  LIVE model (`gen_situation_articles.py` parses index.html), so article and tool
  align directionally (article = national avg, tool = ZIP-specific). MODEL/TOOL
  changes: added directional per-carrier `accident` factor to the 12 standard
  carriers + applied in estimatePremium + "At-fault accident" refine toggle;
  tool now reads `?sit=young|senior|credit|lapse|sr22|accident` (SR-22/DUI already
  routed to CARRIERS_NONSTANDARD). Did NOT overwrite existing guides (caught a slug
  collision with article/young-drivers.html, restored it; new pages use distinct
  cheapest-* slugs + cross-link the guides). Linked from article hub + sitemap.
  jsdom: 506/506 pages 0 errors. OPEN: add the 5 to the global nav res-guides
  panel (500-page migration, optional); renters/home situation pages later.
- **CONTENT: de-duplicated auto metro pages (66 of 95).** Audit flagged the 95
  auto metros as the near-duplicate thin-content risk (~600 words, tight range,
  template + name/number swap). NOTE: the COMPARE pages (81) looked thin by word
  count but are actually strong (interactive "who wins" profile tool + 11-row
  real-data table) — NOT rebuilt. For metros, added a real per-metro section "How
  <Metro> compares to other <State> metros" (rank in state, % vs state avg, linked
  sibling table) via gen_metro_compare.js — model data only, adds metro↔metro
  internal links. 66 multi-metro-state metros enriched; the 29 single-metro states
  have no siblings (not a duplicate risk). OPEN follow-ups: same treatment for
  renters metros (83); optional noindex/prune of any genuinely low-demand metro
  (needs demand judgment — user call, not blanket).
- **FIX: dropdown nav broken on desktop (351 article pages).** A malformed
  `@media(max-width:900px){nav.primary` that never closed trapped the ENTIRE
  dropdown stylesheet inside the mobile breakpoint — so on desktop the Tools/
  Product panels rendered open + unstyled (links run together). Pulled the base
  dropdown CSS to top level, wrapped only mobile-hide rules in the media query.
  Verified 0 brace imbalances / 0 malformed openers / 0 JS errors. Pre-existing;
  the added coverage links exposed it.
- **UX: promoted paired tool CTA to the top of SEO pages.** State/metro (248):
  under the ranking table + removed redundant inline ZIP form. Carrier (147):
  after the TLDR. Compare/guides (88): top of article-body. Now every SEO page
  shows both tools high, value-first. (move_ctas_up.py; 2 link-directory hubs
  keep it low.)

- **QA pass — funnel to the two tools.** (a) Added the two-tile paired CTA to 85
  high-intent AUTO pages that had no in-body tool CTA: ~68 carrier compare pages,
  6 guides, 10 rate-change trackers, 3 hubs (`insert_tool_tiles.py`, self-contained
  inline-ZIP). Every article-tree page (494) now surfaces both tools in-body.
  (b) Fixed a PRE-EXISTING JS bug: auto ZIP-redirect + email scripts called
  `.addEventListener` on `zipBarForm`/`embedZipForm`/`articleEmail*`/`rankingsBody`
  with no null guard, throwing on pages lacking those elements (compare, state-
  rankings, hubs) and killing the rest of that script block. Guarded all attach
  points site-wide. (c) Full jsdom sweep `qa_sweep.js`: **501/501 pages 0 JS
  errors**; `qa_funnel.py`: no dead tool links, every content page links both tools.
- **UX: paired two-tool CTA replaces the dark zip-embed box (409 article pages).**
  User feedback: the dark `zip-embed` CTA was "not very inviting to click," and the
  coverage tool was a buried text link while the rate tool got a big visual CTA.
  Replaced site-wide (`migrate_tool_ctas.py`) with a light **two-tile module**
  (`.tooltiles`): a "Compare rates" tile with a working ZIP box + a "Coverage
  calculator" tile with "Help me choose my coverage options →". Product-aware
  (auto/renters/home coverage URLs); ZIP form keeps `embedZipForm`/`embedZipInput`
  so the existing per-page redirect is unchanged. Dark box now gone sitewide.
  Picked via a rendered preview (`cta-preview.html`, git-ignored, local only — the
  user couldn't judge from ASCII). jsdom-verified: 0 JS errors. See
  [[boringrate-cta-tiles]]. NOTE: other dark CTAs still exist intentionally (rate-
  tool hero, coverage-tool bottom-cta) — not flagged by the user.


- **NEW: renters coverage calculator (`/renters/coverage.html`)** — pushed/live.
  Coverage tool was auto-only; this is the renters counterpart (user picked
  "approach A": purpose-built renters engine reusing the auto tool's design
  system, not a line-by-line clone of the intricate auto engine). Inputs:
  personal-property + assets sliders, deductible / bundle / high-value-items
  pills, ZIP. 6 coverage cards (Personal Property C, Liability E, Loss of Use D,
  Medical Payments F, Replacement Cost, Scheduled Items) with recommendations
  that respond to assets/valuables. Live premium off real renters state averages
  (national $168/yr, `RENTERS_STATE_DATA`); CTAs carry ZIP → `/renters/`.
  Built by `build_renters_coverage.py` (surgical body/script/JSON-LD swap,
  preserves `ZIP3_TO_STATE`). jsdom-verified `verify_renters_cov.js`: 0 JS
  errors, 6 cards, ZIP→state, premium responds to every input. Wired from the
  renters rate tool (below-fold contextual link) + sitemap.
- **HOME PRODUCT — completed this session (user: "build the home product, then
  global nav discoverability").**
  - Home RATE tool (`/home/index.html`) already existed from a prior session
    (HOME_STATE_DATA, HOME_CARRIERS, ZIP ranking, in sitemap). Verified working
    (`verify_home_tool.js`): 0 JS errors, 10 ranking rows, ZIP→state.
  - NEW: home COVERAGE calculator (`/home/coverage.html`) — built via
    `build_home_coverage.py` (adapts the clean renters coverage scaffold). 8
    cards: Dwelling A, Other Structures B (auto 10%), Personal Property C (auto
    50%, RCV toggle), Loss of Use D (auto 30%), Liability E, Medical Payments F,
    Water Backup endorsement, Scheduled Items + flood/earthquake-not-covered
    primer. Live premium off home state avgs (national $1,915). CTA→/home/.
    `verify_home_cov.js`: 0 errors, 8 cards, responds to every input. Wired from
    home rate tool + sitemap.
  - GLOBAL NAV discoverability (`migrate_nav_discoverability.py`, 438 pages,
    idempotent): Product dropdown now lists Auto/Renters/**Home** (un-dimmed the
    151 "Home soon" pages); Tools dropdown + mega-menu Tools section now list all
    three coverage calculators (Auto/Renters/Home). Footer per-product columns
    left untouched. jsdom-verified across sample pages.
  - **Net: both highest-value tools (rate comparison + coverage) now exist and
    are reachable from every page for all three products (auto/renters/home).**
- **HOME ARTICLE TREE (SEO) — completed this session (user: "home article tree
  for SEO").**
  - 51 `home/state/*.html` pages (`gen_home_state_pages.py`) — pre-rendered
    cheapest-carrier ranking + ZIP CTA→/home/, TLDR, avg-cost / cheapest /
    rate-drivers / requirements sections, FAQ + FAQPage/Breadcrumb/Article
    JSON-LD. Differentiated per state by catastrophe profile (RISK map:
    hurricanes/tornado-hail/wildfire/etc.) so pages are genuinely distinct, not
    thin. Reuses the renters state-page scaffold for exact CSS/nav/footer parity.
  - 12 `home/carrier/*.html` reviews (`gen_home_carrier_pages.py`) — per-carrier
    content from HOME_CARRIERS metadata (est cost vs national, NAIC ratio,
    strength grade, availability, about/who-for, 3+3 pros-cons, bottom line),
    each linking 15 state pages + the coverage calc.
  - WIRING: home tool below-fold state grid now links the 51 pages; +63 sitemap
    entries (51 state + 12 carrier); site-wide **Home Insurance mega-nav
    section** on 501 pages (mirrors Renters section — links tool, coverage calc,
    12 carriers, 51 states from every page → internal-link equity for indexing).
  - All jsdom-verified, 0 JS errors. Rankings are baked at generation time
    (re-run the gen scripts to refresh if HOME_CARRIERS/averages change).
  - NEXT / still open (user-scope, do NOT do unprompted): home METRO pages (auto
    + renters have them; skipped for home as lower-value per quality-over-quantity
    — revisit if metro home-insurance queries matter); a dedicated home rankings
    hub page; refreshing the baked rankings if the home model changes.

---
_Earlier (2026-06-11):_

## This session (2026-06-11, Opus 4.8) — shipped

All 3 pending tasks DONE + bug fixes + conversion + SEO. **All commits pushed to
origin/main (auto-deploys to boringrate.com via GitHub Pages).** Later batch
(newest first): broken-link fixes (404s); sitemap +14 missing pages (home tool,
AAA compares); Twitter Card tags on 415 pages + 16 og:image backfills; reverse
cross-sell (renters+home → auto); quote-domain trim (csaa-insurance.aaa.com →
aaa.com); uniform quote-CTA box width (`min-width` border-box, fixes ragged
right edge). Earlier batch:

- **renters articles: sticky mobile CTA parity (147 pages)** — extended the
  sticky CTA to the renters article tree (`renters/{state,metro,carrier}/`);
  `patch_article_sticky_cta.py` now handles both trees (renters fallback
  `/renters/`, own label format).
- **tool: absolute `$X/yr est.` premium per rank row (auto/home/renters)** —
  rows previously showed only "Save $X vs median"; since the median moves with
  the profile, profile changes looked invisible. Added a per-row absolute
  premium (`.rank-premium`) so changes are legible. The model DOES vary
  (3-4x swings, reorderings) — see [[boringrate-rate-model]]. Rates are MODELED
  client-side (`base × stateAvg × sensitivities`), not live-quoted.
- **tool: ZIP submit clears `demo` + lands on personalization CTA** — the
  `zipForm` submit handler added `.active` but never removed `.demo`, so
  `.result.demo .refine-zip-row` / `.refine` stayed `display:none` and the ZIP
  chip + "Add Personalization" CTA were hidden after a real ZIP. Now removes
  demo, scrolls to `#refineZipRow` (scroll-margin-top:84px clears sticky header).
- **article: sticky mobile CTA strip (263 auto pages)** — Task #2.
- **auto: cross-sell renters after results** — Task #3 (`#crossSellRenters`).
- **article: activate Home nav link (263 pages)** — Task #1.

## How to resume (read this first when you come back)

You will likely restart Claude Code with `--dangerously-skip-permissions` and lose chat history. When you re-open:

1. Say: **"Read SESSION_NOTES.md and CLAUDE.md, then continue the three pending tasks."**
2. The three pending tasks are listed under **Pending — execute next** below.
3. The strategic roadmap and user preferences are below that.

## What we shipped this session (in commit order, newest at top)

Run `git log --oneline -40` to see all commits. Highlights:

### Auto page (index.html)
- New headline: **"Best Auto Insurance Rates *in your ZIP*."** + subhead "No calls. No spam. No selling your info."
- Trust line: "Editorial · Updated quarterly from state DOI rate filings & NAIC complaint indices."
- **California demo example** on first load (no profile, no ?zip) — boots an example CA ranking + dark editorial callout: "EXAMPLE ONLY · Enter ZIP above ↑ to see rates."
- **Persistent ZIP confirmation chip** "SHOWING BEST RATES IN 80132" (dynamic) above refine bar
- **Inline personalization progress bar** next to ZIP chip — 4 fields (Own, Vehicles, Age, Credit). Default 1/4 (Credit preset "Good"). Goes **green at 4/4** ("Fully Personalized").
- **Refine bar collapsed by default**. Prominent trigger button: "Add Personalization Here for More Accurate Rates ↓". Click expands, text swaps to "Personalize Your Profile ↑", arrow flips. Two-way toggle.
- Inside refine: Home / Vehicles / Age / Coverage chips + Coverage Calculator CTA above the Min/Std/Premium chips + "Add Specific Coverage Selections" sub-toggle ("Coverage choice can swing rate ~30%") for liability/deductible drawer.
- **Quote CTAs**: `Save $300 / @ geico.com →` format. Domain extracted from CARRIER_LINKS via `quoteDomain()` helper.
- **Removed**: scrolling rate-ticker, "Boring Rank: Quote First" decorative header, redundant rank-table-label, hidden state-banner/personalization in demo mode.

### Renters page (renters/index.html)
- Full parity with Auto: headline, hero, trust line, ZIP chip, inline personalization bar, collapsed refine trigger, @-domain CTAs, California demo example.
- Refine fields: Property coverage, Deductible, Bundle w/auto, Prior claims.

### Home page (home/index.html)
- Full parity with Auto + Renters.
- **Critical bug fix**: mobile rank-row 2-row grid (was collapsing invisibly on <600px — same bug Renters had previously been fixed for).
- Refine fields: Dwelling coverage slider, Deductible, Bundle w/auto, Prior claims.

### Articles
- **Carrier mentions hyperlinked** — first occurrence of each carrier name in body text wrapped in `<a class="ca-link" href="/article/carrier/{slug}.html">`. 3,087 mentions across 222 files via `patch_carrier_links.py`. Editorial accent-red underline style.

## Pending — execute next

All three signed-off tasks are DONE (see "This session" above). The sticky CTA
ended up scroll-to-own-form (honest: reader's real ZIP) rather than a fake
representative ZIP, and the cross-sell carries the entered ZIP into
`/renters/?zip=`. Implementation differs slightly from the original sketch below
but achieves the same goals.

Open follow-ups (not yet signed off):
- **Cross-sell the other direction** — renters→auto, and a home cross-sell.
  Currently only auto results surface renters.
- **Decide rate-display philosophy** — we now show absolute `$X/yr est.`
  alongside "Save $X vs median". If the user prefers one or the other, easy to
  adjust in each `renderRanking` (search `rank-premium`).

## Mobile rank-row streamline (2026-06-11)

Mobile-only (auto ≤800px, home/renters ≤600px); **desktop untouched**. Rows now
show: carrier name + tagline, Rate Stability score (with an inline "Rate
Stability" label via `.rank-stability::after`, since the column header is
desktop-only), and the rate/quote box (`$X/yr est.` + Save/quote). Hidden on
mobile: `.rank-grade` (Customer Service), `.rank-review-link` (BoringRate
Research), `.rank-cb` (Compare), and `.rank-mark` (NAIC, renters/home only).
Quote box is `min-width:0` on mobile so carrier names keep room.

Follow-up fixes (after first phone review): quote box is now fixed 144px +
ellipsis (was content-sized → ragged + bled past the row); Compare/grade/mark
hidden with `!important` (a base `.rank-cb` rule and a 480px research re-show
sat after the media block and were overriding the plain hides); "BoringRate
Research" text link replaced by a compact **(i) circle inline next to the
carrier name** (all viewports — user said the icon "captures enough"); long
names now wrap. Note: home rows never had a Research link or Compare box.

**Two judgment calls to confirm on a phone:**
1. NAIC quality mark hidden on mobile — stability is the single mobile quality
   signal (auto's NAIC lived in the removed grade's tooltip, so this keeps the 3
   pages consistent). Un-hide `.rank-mark` in the mobile blocks if you want it back.
2. "Rate Stability header" was implemented as a per-row inline label, not a
   single header at the top of the list.
3. The (i) icon replaced the Research text link on DESKTOP too. If you want the
   desktop text back, gate `.rank-review-icon` styles to the mobile media query.

## Pre-rendered state/metro rankings (2026-06-12) — SEO "best rates in [X]" play, DONE

`gen_state_rankings.js` (Node, evals the model from index.html) injects an indexable
static "Cheapest carriers in [State/Metro]" ranked table into every state + metro
article — Google reads the real rankings → matches "best rates in [state]" intent →
the page ranks, and the existing ZIP CTA drops users into the live JS tool. Same
model: state avg × carrier base × STATE_CARRIER_ADJ (× METRO_CARRIER_ADJ for metros).
Idempotent (markers `<!-- state-rankings-start/end -->`); re-run to refresh.
- `node gen_state_rankings.js --states` (51) · `--metros` (95) · or `TN CO ...`.
- Live on **all 51 states + 95 metros = 146 pages**, verified 0 JS errors
  (`node verify_states.js`). User approved: "do it the way Google rewards, don't
  overthink, I love the JS tool, just get users there."

## Rate-tracker pages redesigned + QA clean (2026-06-15)
- Tracker per-state pages were "sparse/ugly" (single-filing pages = 1-row table). Rebuilt:
  data-driven headline + "shop for a better rate" CTA → embedded cheapest-carriers
  ranking + ZIP entry box (→ /?zip=) → sourced filing detail → "are you getting it" callout.
- `node gen_state_rankings.js --export` → `state_rankings.json` (consumed by gen_rate_tracker.py).
  `render()` uses lambda re.sub replacements (HTML has `\d` in ZIP onsubmit — string repl broke).
- 9 deep tracker states (CA/FL/GA/LA/NV/SC/TN/TX) + hub 50-state table + State Farm $4.6B note.
- **RESOLVED user decision:** per-row delta wording = **"−$X vs avg"** (confirmed 2026-06-15; memory updated).
- Full QA pass clean: verify_rate.js / verify_states.js / verify_funnel.js all 0 JS errors.
- STILL pending user: prominent on-homepage tracker link (currently nav + footer only).

## Rankings — to top + ZIP box + renters parity (2026-06-13/14)
- Rankings now injected at the TOP of every state+metro article (first thing after
  the headline) — `gen_state_rankings.js` strips+re-inserts at top.
- Ranking block CTA is a real **ZIP entry box** (input+button) that redirects to the
  tool: `/?zip=` (auto state+metro) / `/renters/?zip=` (renters). Inline onsubmit (no
  CSP). Was an anchor "red box".
- **Renters parity**: `gen_renters_rankings.js` → "Cheapest renters carriers in [State]"
  on all 51 renters/state pages (avg×base, carrier availability filter).
- Refine trigger CTA → **"Edit Personal Profile"** (accordion, text left/chevron right).
- 80132/80133 → Colorado Springs via `ZIP5_METRO` override in index.html lookupZip.
- Note: jsdom prints a benign stderr "addEventListener null" for article bottom
  scripts (present pre-change, browser-works) — error-listener count is 0; ignore.

## Results UI tweaks from user feedback (2026-06-12)
- Top of results: compact **"Avg rate in [ZIP]: $X/yr"** banner (was a big dark
  "Median rate" block — user: too big). Light paper-deep bar, 16px.
- Per-row delta: **"−$X vs avg" / "+$X vs avg"** (was "Save $X" — user: unclear what
  it's vs). All 3 tool pages.
- Removed the redundant `rank-table-label` bar above the rank list (was stacking with
  the new banner) to kill the growing gap between the ZIP CTA and the rankings.
- PENDING USER: confirm the "vs avg" wording + compact banner look on a phone.

## Rate-change tracker (2026-06-12) — new traffic play, IN PROGRESS

Tracks who raised/cut auto rates by state + the "are you actually getting the new
rate?" angle. **Data discipline: every entry has a real source + URL; nothing invented.**
- `rate_changes.json` — `changes[]` (carrier-level filings, each sourced) +
  `statewide_2026` (Insurify projected avg for 49 states+DC, one source) + `_meta`
  (national + $5B State Farm dividend callout).
- `gen_rate_tracker.py` — builds the hub (`article/rate-changes/index.html`: national
  context, dividend callout, deep-state links, full 50-state projection table) + a
  rich per-state page for each state with carrier-level data. FAQPage+Breadcrumb schema.
- Linked from each covered state's article + sitemap + **Guides nav site-wide**
  (`patch_nav_tracker.py`, 418 pages).
- **Verify: `node verify_rate.js`** (jsdom, scans all rate pages; 0 JS errors expected).

**Deep states so far (5):** NV (8 increases, Review-Journal/NV DOI), LA (Progressive
-6.6%/-4%, LA DOI), CA (State Farm -6.2% + $5B dividend, SF newsroom), TX (State Farm
-4.1%, SF newsroom), FL (top-5 cuts -8/-10%, WFLX Mar 2026). **Hub table covers all
states** via Insurify projection.

**To add a state:** research via WebSearch (+ WebFetch where allowed; SERFF/many DOI
sites are 403-blocked to bots), add sourced rows to `changes[]`, run
`python3 gen_rate_tracker.py`, add sitemap + a state-page callout. ONLY publish
figures you can date to 2026 + attribute (excluded CA Mercury/GEICO +6.9% — traced to
2023-25; excluded FL dividend-per-state specifics — unverified in-source).

**Pending/ideas:** more states (LA has more cuts to add — Farm Bureau -11.8%, Allstate
-7.6%, Encompass -15%, need source verify); the email "your carrier filed a change"
trigger; quarterly freshness refresh; footer link. **Data note:** CA state article says
"+6.1% projected 2026" but Insurify says +1.0% — pre-existing source discrepancy, not
yet reconciled.

## Metro page expansion (2026-06-12)

Two generators added:
- `gen_metro_page.py` — `build_page(cfg)` builds one metro page from the
  `article/metro/atlanta.html` template (state-base × metro-offset; see
  [[boringrate-metro-model]]). Full SEO (title/meta/OG/Twitter/canonical,
  FAQPage+BreadcrumbList schema, sticky CTA). `STATE` dict mirrors STATE_DATA.
- `gen_metros_batch.py` — adds a list of metros: generates pages **and** wires the
  tool (`METRO_NAMES`, `METRO_CARRIER_ADJ` via a carrier `SPREAD` around the offset,
  `ZIP_PREFIX_METRO` add/reassign), sitemap, and state-page links. Re-runnable.
  **To add more metros: append to `METROS` (slug, name, state, offset, key, zips) and
  run `python3 gen_metros_batch.py`.** ZIP reassign is replace-all (a dup "374" key
  bit us once — JS last-wins).

Done so far: 84 → 95 metros. Colorado Springs (pilot) + batch of 11 (Grand Rapids,
Reno, Worcester, Allentown, Savannah, Pensacola, Asheville, Lexington; splits:
Dayton←Cincinnati, Akron←Cleveland, Chattanooga←Nashville).

**Still deferred: nav mega-menu** lists all metros and is duplicated across 410+
pages — new metros aren't in it yet (reachable via state links + sitemap). Worth a
batch patch (like `patch_article_sticky_cta.py`) for internal-link SEO. Offsets are
directional; offset moves price level only, NOT carrier ranking.

Note: state coverage is COMPLETE (930/930 ZIP3 prefixes → no national-fallback bug).
ZIP→metro is ~543/930 (rest legitimately state-only/rural).

## Analytics event layer (built 2026-06-11 — connect a vendor to go live)

A vendor-agnostic `window.track(name, props)` is defined in `<head>` of all three
tool pages (`index.html`, `home/index.html`, `renters/index.html`). It buffers
events in `window.brEvents` and **sends nowhere** until a transport is wired.

**To connect tomorrow:** uncomment ONE line in the `track()` transport block (same
in all 3 files):
- Plausible: add their `<script>` to `<head>`, then `window.plausible(name, {props: ev.props})`
- GA4: add gtag snippet, then `window.gtag("event", name, ev.props)`
- Supabase: POST `ev` to an `events` table (reuse existing supabase client)

Debug now: set `window.BR_DEBUG = true` in console to see events log; inspect
`window.brEvents`.

**Events already firing** (props in braces): `zip_submitted` {zip, product, source:
form|url}, `refine_expanded` {product}, `quote_clicked` {carrier, product, href},
`email_signup` {product}, `cross_sell_clicked` {from, to, href}, `demo_cta_clicked`
{product}. `product` is auto|home|renters. Article zip-bar searches redirect to the
tool and fire `zip_submitted` with `source:url`.

## Strategic roadmap (after these three)

### Tier 1 — Measurement (user said they'd set up tomorrow)
- **Analytics** — Plausible is the brand-aligned pick ($9/mo, no cookies, fits the boringrate "no tracking" promise). GA4 is free but hypocritical for this site. Or: first-party Supabase events table — write events ourselves, query manually.
- Events to track: ZIP submitted, refine expanded, Get Quote clicked (by carrier + state + product), email signup, demo banner CTA click.

### Tier 2 — Conversion lifts
- Already addressed: Quote-on-domain CTAs, sticky mobile article CTA, cross-sell. Once shipped tonight.

### Tier 3 — Trust / authority
- **Carrier monochrome wordmarks** in rank rows (~3-4 hours; need to gather/optimize ~25 SVGs).

### Tier 4 — Hygiene
- Move ~17 `patch_*.py` scripts into `/scripts/`
- Clean unused CSS: `.kicker`, `.coverage-nudge` (unused after recent edits)
- Remove hidden HTML: `boring-rank-header`, `rank-table-label` elements (CSS-hidden, can be deleted)

## Critical rules (from CLAUDE.md — also memorized)

**Never replace an entire `<script>...</script>` block** when patching. The pattern in old `patch_hamburger_js.py` wiped widespread JS across 66+ pages because pages had unique JS co-located in the same block as the targeted marker. Required git extraction from `41fb75c` to recover.

**Safe pattern:** Insert a *new* `<script>` block before the marker, or use surgical Edit tool replacements that don't touch existing block boundaries.

Style blocks are safer to surgically edit, but still — when in doubt, insert a new `<style>` block rather than rewrite an existing one.

## User preferences I've learned

- **Honest critique > hedged feedback.** "Don't holdback punches" was an explicit directive.
- **Concise responses.** No hedge language. State decisions directly.
- **Editorial tone preserved.** The boringrate brand is editorial, magazine-like, "boring on purpose." Avoid hype language ("Unlock!", "Save Big!").
- **CTA format**: `Save $X / @ domain.com →` (the @ symbol is the link signal).
- **Personalization bar**: 4 options not 5; Coverage tier excluded from count (it's an assumption, not a personalization).
- **Refine UX**: Trigger should STAY VISIBLE when expanded (the user pushed back when it disappeared on click).
- **Demo state**: shows California example on first load — refine bar hidden in demo mode, only the ZIP form + example callout + ranks visible.
- **Aggressive clutter trimming.** Removed rate ticker, decorative headers, redundant labels. User specifically called out "too many blocks before they see the actual ranks."
- Likes **product-named headlines** (e.g., "Best Auto Insurance Rates in your ZIP") over generic ones.
- **No new files unless necessary** — surgical edits to existing files preferred.
- **Commit per logical change** so changes are independently reversible via `git log` review.

## File map
| File | Purpose |
|---|---|
| `/home/knighttyler/boringrate/index.html` | Auto comparison (~5400 lines) |
| `/home/knighttyler/boringrate/renters/index.html` | Renters comparison (~1700 lines) |
| `/home/knighttyler/boringrate/home/index.html` | Home comparison (~1300 lines) |
| `/home/knighttyler/boringrate/article/state/*.html` | 50 state articles |
| `/home/knighttyler/boringrate/article/metro/*.html` | 80+ metro articles |
| `/home/knighttyler/boringrate/article/carrier/*.html` | ~30 carrier pages |
| `/home/knighttyler/boringrate/article/compare/*.html` | Head-to-head compare pages |
| `/home/knighttyler/boringrate/CLAUDE.md` | **Patch safety rules — read first** |
| `/home/knighttyler/boringrate/patch_carrier_links.py` | Recent reference for write-script patches |

## Git state at session end
- Branch: `main`
- Remote: `git@github.com:PyByKnight/boringrate.git`
- Auto-deployed via GitHub Pages on push (CNAME → boringrate.com)
- Latest commits (run `git log --oneline -8` for current state)
