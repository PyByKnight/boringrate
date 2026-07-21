# BoringRate — Session Notes
_Last updated: 2026-07-21 (Opus 4.8)_

## ▶▶ RESUME HERE (2026-07-21) — NEXT PULL DECIDED: AUTO in PA → IL → OH
Owner is pulling filings; strategic decision made: **pull AUTO for the big markets we have HOME but no AUTO
for — PA, OH, IL** (top-10 auto markets currently missing; completes the auto+home twin on carrier pages;
hardens the new auto stability, only 11 carriers gated). **Start with PENNSYLVANIA** (prior-approval →
cleanest "Overall % Rate Impact" to parse), then IL, then OH.
- **Pipeline is READY, zero prep:** OH/PA/IL auto state pages + metros already exist; the auto tracker
  auto-generates a state page for any state it sees in the data; 0 existing auto rows for all three (net-new).
- **Afternoon flow:** parse jackets → add rows to BOTH `serff_filings.json` (ledger→rollup/carrier/stability/
  cites) AND `rate_changes.json` (curated tracker layer) [same pattern as the FL reconciliation] → run
  **`./rebuild.sh auto`** → review `git diff` → commit → push. Scale filter: top-10 family / ±3% / ≥10k
  vehicles (entity map in SERFF_RUNBOOK.md). Watch: PA nationals crossing the ≥3-state stability gate.
- **Coverage now:** AUTO = CA FL GA NV NY SC TN TX (8) · HOME = CA IL LA NJ NY OH PA TX (8) · both = CA NY TX.

## This session (2026-07-19→21, Opus 4.8) — AUTO stability + FL reconcile + carrier filings + analytics + rebuild.sh
_Shipped & pushed (main): auto filing-derived stability (AUTO_STABILITY_ADJ), FL press↔ledger reconcile,
home distinct-state gate backport, per-carrier SERFF filing-record sections (25 pages), Plausible coverage
+ durable generator wiring, Layer-3 verified secondary citations (5 guides), and `rebuild.sh` cascade runner.
Details in the dated blocks below._

## This session (2026-07-19, Opus 4.8) — AUTO filing-derived rate-stability + FL press↔ledger reconciliation
No new DOI pull (owner away from machine) → work off data on hand. Fable consult picked the two moves.
- **AUTO RATE-STABILITY (filing-derived) SHIPPED** — the auto tool's static `stability` (1-5) was
  marketing-set and CONTRADICTED the ledger (American Family scored 4/5 "stable" while filing +6.8%
  GA/SC/TN; Progressive 2/5 "volatile" while cutting −2.1% across 6 states). Twin of the home fix:
  **`gen_auto_stability.py`** injects `AUTO_STABILITY_ADJ` into index.html between GENERATED markers;
  peer-relative band of (carrier mean overall_pct − peer median), coverage-GATED, frequency-guarded.
  New `carrierStab(c)` helper (mirrors home) routed through all 4 read sites (bestRec ×2 + render +
  rec filter). Adjusted 5: **State Farm 4→5, Progressive 2→3** (cutters rewarded), **American Family
  4→2, Amica Mutual 5→4, Allstate 3→2** (raisers penalized). Tooltip appends "Based on this carrier's
  recent rate filings." for adjusted carriers. Behavioral test (node) ALL PASS; qa 582/0; prose 0 drift.
  - **★ FIXED A LATENT BUG inherited from gen_home_stability.py:** the coverage gate counted FILINGS,
    not DISTINCT STATES (docstring says states). Country Financial slipped through on 3 CA-only filings
    → boosted 4→5 wrongly. Auto now gates on `len(distinct states) >= 3` (Country Financial correctly
    drops). **gen_home_stability.py still has the filing-count gate — backport the distinct-state fix.**
  - **BORDERLINE (flag):** Allstate 3→2 — +1.7% mean, raised in exactly 50% of filings (band −1, guard
    fires only below 0.5 so it stands). Defensible (peer-relative, net raiser) but the softest call.
- **FL PRESS↔LEDGER RECONCILIATION** (bigger than Fable scoped — 4 rows, not just Progressive). One
  WFLX "FL top-5 cutting 8%" (Mar 2026) FORECAST seeded 4 press rows the ledger contradicts:
  State Farm −10% (ledger 0% flat 26-027524), Progressive −8% (ledger **+3.8%** 25-048862 — opposite
  direction!), GEICO −8% (ledger 0% flat 26-020774), Allstate −8% (no ledger filing). Owner approved
  FULL reconcile: rewrote Progressive→+3.8% increase; removed SF/GEICO (filed flat, not changes) +
  Allstate (discredited source, unbacked); ADDED Liberty Mutual −7.9% real cut (26-014714, was missing).
  USAA −7% kept (separate FLOIR Jan-2026 cut, not contradicted). Both new rows now auto-cite their SERFF
  # via serff_match. Cascade: gen_rate_tracker + gen_filing_highlights + gen_press_page regenerated.
- **FILES:** new `gen_auto_stability.py`; edited index.html (helper + ADJ block + 4 read sites),
  rate_changes.json (FL), regen'd article/rate-changes/{index,florida}.html, article/state/florida.html,
  press/index.html. Working tree DIRTY — NOT committed yet (owner to approve; 2 logical commits: FL fix,
  auto stability). apply_filed_changes.py confirmed a NO-OP this session (backfilled filings pre-anchor).
- **BACKPORT DONE** (commit 9d14271e): gen_home_stability.py now gates on distinct states too. Output
  byte-identical (no current home false positive — the bug was latent there; 0 home carriers have ≥3
  filings in <3 states). Both stability generators now consistent.
- **CARRIER FILING-RECORD SECTIONS SHIPPED** (Fable's #2 — strongest byline-free E-E-A-T). New
  **`patch_carrier_filings.py`** injects a "<Carrier>'s recent rate filings" section into
  article/carrier/<slug>.html: a sourced cross-state table (Product/State/Change/Effective/SERFF #),
  auto+home combined, each row deep-linking the /rate-filings/ ledger anchor + state portal (shared
  filing_cite helpers → anchors agree with ledger/trackers). Prose summary computed from data
  ("State Farm filed 12 auto changes across 7 states, averaging −4.6% and 6 home across 6 states,
  +7.0%"). **25 of 38 pages patched** (those with ≥1 filing auto or home); the other 13 skipped — NO
  fabricated citations. Patch-safe: insert before first "<h2>Compare …", strip-then-reinsert idempotent
  (re-run refreshes after next pull). qa 582/0. Consistent with the tool (State Farm auto cutter / home
  raiser matches its stability scores).
- **ANALYTICS — CORRECTED THE RECORD + FIXED COVERAGE.** The "window.track buffers→nowhere" note was
  STALE. Plausible was already live: `window.track` calls `window.plausible()` and the pa-v2 site-ID
  script (`patch_plausible.py`, Jul 2) was on 466 pages incl. all 3 tools. The real gap: 114 home/renters
  CONTENT pages (home guides + home/state ×51 + home/metro ×28 + home/rate-changes + 9 renters + press +
  rate-filings) had NO snippet — the home/renters generators emit their own <head> without it, and
  patch_plausible.py hadn't been re-run since those pages were regenerated. **Fixed: re-ran
  patch_plausible.py → 114 patched, now 580/580 pages track.** qa 582/0.
- **CASCADE ADDITION:** patch_plausible.py + patch_carrier_filings.py must run as the LAST steps of any
  build/regen cascade (like build_nav / patch_metro_citations) — home/renters regens re-emit heads
  without the analytics snippet, and new filings should flow onto carrier pages.
- **DURABLE ANALYTICS FIX DONE.** New **`plausible_snippet.py`** = single source of the snippet
  (SCRIPT_ID + SNIPPET) + idempotent `ensure(html)` (inserts before first `</head>`, no-op if present
  or headless). Wired `ensure()` into the write path of all 7 head-emitting generators
  (gen_home_metro_page, gen_home_state_pages, gen_home_faq, gen_home_rate_tracker, gen_renters_faq,
  gen_press_page, gen_rate_filings_rollup) so the snippet is baked in at generation — survives a regen
  without needing patch_plausible.py re-run. patch_plausible.py refactored to import from the shared
  module (script id now defined ONCE). **Verified:** stripped the snippet from press + rate-filings,
  re-ran their generators → snippet restored BY THE GENERATOR (only benign date diff); pages restored to
  HEAD (no page churn in this commit — the fix is generator source; live pages already carry the snippet
  from the earlier patch commit). ensure() unit-tested; py_compile clean on all 8 files. patch_plausible
  stays as the belt-and-suspenders backstop + covers any hand-built pages.
- **LAYER-3 SECONDARY CITATIONS SHIPPED (5 live guides).** Added a REAL, WebFetch-VERIFIED authoritative
  secondary link to each shipped guide's muted Source note (appended after the form-language + "your
  carrier's form may differ"): renters-theft → III renters (theft + off-premises + flood-excluded);
  renters-water-damage → FEMA/NFIP floodsmart (flood is separate NFIP contents); does-car-insurance-cover
  → III auto-coverage-basics; home-required → CFPB (lenders require it, not statute); renters-required →
  Texas DOI ("isn't required by law… landlords may require it"). Every URL was FETCHED and confirmed to
  support its exact claim before use — `coverage_sources.draft.json` records the confirming quote + date
  in a new `url_verified` field per entry. **NO URLs fabricated.** 13 remaining entries stay `TODO`
  (their guides don't carry the Layer-3 form note yet — deferred per content-first). qa 582/0.
- **NEXT / DEFERRED:** (a) AUTO By-ZIP dispersion stays SKIPPED (low ROI); (b) Layer-3 guides 6–18
  (secondary URLs + form note) only if demand grows; (c) per-carrier filing-record + plausible both
  auto-flow via their cascade steps. Byline still owner-blocked.

## This session (2026-07-18b, Opus 4.8) — About de-monetized + Layer-2 metro citations + Layer-3 top-5 guides
Owner feedback: the /about.html editorial harped on monetization. Then: push it, do metro citations + Layer 3.
- **ABOUT DE-MONETIZED** (`gen_trust_pages.py` = source of truth; regenerated about.html): killed the run-on.
  Dropped the whole `§02 "How we're funded — and how we're not"` block (redundant with the callout + §04
  Editorial independence) → renumbered §03→02 … §06→05. Callout trimmed to one line ("no form routes your
  details to buyers … you can't buy your way up, best rates come first"), dropped "keep the lights on" +
  the double phone/email. §01 kept the lead-funnel contrast (sharpened "call and email you for weeks"). NO
  "we may monetize someday / paid agent placement" copy anymore. Mirrored page↔generator. Meta descriptions
  left as-is (concise SEO). **If editing about copy again, edit `gen_trust_pages.py` then run it — hand edits
  to about.html get overwritten on regen.**
- **LAYER-2 METRO CITATIONS SHIPPED (auto + home).** Metro figures are MODELED (state avg × offset), so NO
  inline SERFF # (would overclaim) — instead a muted "Sources & method" provenance line links the primary
  data. **Auto: 95/95** metros (12 via `gen_metro_page.py`/`gen_metros_batch.py`, **83 legacy pages via new
  `patch_metro_citations.py`** — those predate the generator; no live gen rebuilds them, so a patch is the
  safe path, insert-before-`<div class="article-email">`, strip-then-reinsert idempotent). **Home: 28/28**
  (wired the ledger link into the existing provenance line in `gen_home_metro_page.py`). Shared
  `build_sources_note()` in gen_metro_page.py = one canonical string for both build + patch.
  - **Ledger deep-link:** `gen_rate_filings_rollup.py` now reads `?state=XX&product=Auto|Home&dir=` and
    preselects the filters (metro/data pages link straight to their state's filings). Option values = state
    codes, matches data-state.
  - **Coverage-gated wording:** only the 8 auto-ledger states (CA/FL/GA/NV/NY/SC/TN/TX) get "the primary
    filings behind <state> rates" + `?state=XX`; uncovered-state metros link the national roll-up worded
    generically (no promise of filings we don't have). Tracker link only where the state tracker exists.
- **LAYER-3 TOP-5 GUIDE CITATIONS SHIPPED** (owner approved copy + Top-5 scope via GSC 28d impressions).
  Muted `<strong>Source:</strong>` note (13px, left-rule) inline under the answer, hand-edited per guide:
  theft (920 → ISO HO-4 / HO 00 04), renters-water-damage (196 → HO 00 04, flood excluded), does-car-
  insurance-cover (62 → ISO PP 00 01), home-required (58 → contractual/lender, NOT statutory), renters-
  required (39 → contractual/lease). **Form language is citation #1 (real, unfabricated); NO `.gov`/III/NAIC
  URLs were invented** — `coverage_sources.draft.json` still has `url:"TODO"` for all 18; secondary DOI/NAIC
  links deferred (would need real WebFetch verification). Each guide got the "your carrier's form may differ"
  caveat (itself a trust signal). qa_sweep 582/0, prose 0 drift.
- **STILL TODO after this:** (a) verify + add secondary .gov/NAIC/III URLs to the shipped Layer-3 guides
  (unfabricated only); (b) Layer-3 guides 6–18 if demand grows (defer per content-first); (c) named-founder
  byline still owner-deferred; (d) AUTO stability field; (e) next home states MI/GA/NC/TN; (f) FL Progressive
  tracker reconciliation.
- **SHIPPED / LIVE:** 4 logical commits on main, pushed (`597ce7bc..cd2cb866`) → GitHub Pages redeployed:
  `650e216f` about de-monetize · `4d441485` Layer-2 metro citations (128 files) · `0afe0e44` Layer-3 top-5
  guide citations · `cd2cb866` docs. Working tree clean. (IndexNow ping not sent — optional, not run.)

## ▶▶ CURRENT STATE / RESUME HERE (2026-07-16) — HOME primary-source build-out
**Home rate-filing backfill: 8 states** — CA, TX, LA, NY, PA, OH, IL, NJ — **132 filings** in
`serff_home_filings.json` (single source). Each state's pull: SERFF FA jackets (owner pulls full zips →
drop in `/home/knighttyler/`; I parse the "Company Rate Information" block / filing memo). Recipe +
triage pattern in the per-state blocks below. **Next clean home states: MI, GA, NC, TN** (FL deferred —
painful pull). Each new state auto-cascades through the pipeline below.

**Home tool subsystems built this arc (all live, all gated qa_sweep/prose):**
- **`HOME_DRIFT`** (`apply_home_filings.py`) — primary-source price drift: post-anchor filings (anchor
  `anchor_dates_home.json` = 2026-07-02) renormalized onto STATE_CARRIER_ADJ, WP/market-share weighted.
  Currently drifting **TX, PA, IL, NJ** (states with post-anchor movers). Pre-anchor filings = no-op
  (already in aggregator baseline; verified by data-as-of dates).
- **By-ZIP dispersion** (`max_pct`/`min_pct` on filings; `gen_home_rate_tracker.py`) — "the filed
  average is not your rate" column + callout + the `home/why-did-my-home-insurance-go-up.html` guide.
- **`HOME_METRO_OFFSET`** (`gen_home_metro_offsets.py`) — directional sub-state offsets (band = modeled
  catastrophe geography, dispersion corroborates; NOT scaled off it) → **28 home metro pages**
  (`gen_home_metro_page.py`).
- **`HOME_STABILITY_ADJ`** (`gen_home_stability.py`) — filing-derived rate-stability, peer-relative +
  coverage-gated (fixed USAA 5→3 raising-hard vs Nationwide 4→5 flat).
- Assets: `/rate-filings/` roll-up (253 rows), `/press/` journalist page, per-state auto+home trackers.

**Cascade after any pull → now a one-command runner: `./rebuild.sh [auto|home|all]`.** After the DATA
step by hand (add rows to serff_filings.json / serff_home_filings.json + new-state base entries/roster
states), run `./rebuild.sh` — it runs the full deterministic recompute + primary-source citations + nav
+ QA in the proven-idempotent order, incl. this session's additions (gen_auto_stability, patch_carrier_
filings, plausible-baked-in). VERIFIED 2026-07-20: ran on current data → all 21 steps green, qa 582/0,
prose 0 drift, every post-gen patch survived (only cosmetic date/lastmod diffs, restored). Still MANUAL
after: parse zips, add NEW page URLs to sitemap.xml, `git commit`, IndexNow ping, clear `~/*.zip` +
scratchpad (disk tight, 25G). The explicit ordered step list lives in rebuild.sh (self-documenting).

**DEFERRED / owner-directed next:**
- **ZIP↔territory mapping** (true ZIP-level rating): territory FACTORS extractable, but ZIP→territory
  MAPS are NOT in rate jackets (separate/ISO filings). Watch for them while pulling (SERFF_RUNBOOK note).
- **AUTO rollout:** same dispersion (max/min) + filing-derived stability for auto as we pull auto filings
  (auto tool has NO stability field yet → add one first). Auto dispersion display judged low priority.
- **Journalist play items 2 & 3:** PRESS_KIT.md + reporter response templates (item 1 /press/ shipped).

## This session (2026-07-16c, Opus 4.8) — E-E-A-T trust surfaces + citation plan (Fable consult)
Owner asked to run E-E-A-T / credibility up through Fable (the "where do we cite primary sources?"
question), then work autonomously ~1hr making SAFE improvements while FLAGGING (a) any new SERFF
strategy and (b) mass primary-source-link insertion across rate-change pages/articles.
- **DEPLOYED TO MAIN/LIVE (2026-07-16c, owner approved "add all" + "see it published"):** merged
  `eeat-trust-pages` → main, pushed (GitHub Pages). Live: `/about.html` (founder bio = 10-yr insurance
  & lead-gen insider + mission "we do the boring part so you don't have to"), `/editorial-standards.html`,
  footer "Editorial standards" retargeted (442 pages), **Layer 1** (rate-filings row anchors via
  `filing_cite.py`, 253 rows) + **Layer 2** (home rate-change trackers cite SERFF # inline, deep-linking
  the ledger row — 92 citations / 8 states). qa 582/0, prose 0 drift.
- **AUTO TRACKER Layer 2 DONE + LIVE (2026-07-16c):** `gen_rate_tracker.py` now joins rate_changes.json
  → serff_filings.json (signed-pct match ≤1.5pt via `serff_match()`) and cites SERFF # inline (42
  citations, CA/GA/NY/SC/TN/TX); NV/LA/FL kept press-sourced (no matching ledger filing — no fabricated
  #). Deep-links resolve to ledger anchors.
- **OWNER-FEEDBACK FIXES (2026-07-18, live):** (1) SERFF deep links expire (sessionExpired) → `filing_cite.portal_url()` now links the state SERFF Filing Access landing page (`/sfa/home/<ST>`), reader searches by the shown tracking #; TX/CA/FL direct links kept. (2) ledger row `scroll-margin-top:96px` + `:target` highlight so #anchor jumps clear the sticky header. (3) rate-change % standardized to 1 decimal. (4) ZIP placeholder → 'Enter ZIP' site-wide (13 gens + 562 pages). (5) About/editorial: team framing ('team of insurance insiders, decades in product/pricing/lead-gen'), monetization stance (may monetize someday via agent ad placement, never pay-for-ranking, best rates first), new opening line. No byline name (owner deferred).
- **STILL TODO (next rollout):** ~~metro pages (auto+home) citations~~ ✅ DONE 2026-07-18b;
  ~~Layer 3 guide citations~~ ✅ top-5 DONE 2026-07-18b (form-language only; secondary DOI/NAIC URLs still
  to verify — coverage_sources.draft.json `url:"TODO"`); the named byline (owner to supply real name +
  profile links for Person/Organization sameAs). AI-disclosure line still owner's call.
- _(orig shipped-on-branch note:)_ `/about.html` (who's behind BoringRate, independence/funding, sourcing, corrections)
  + `/editorial-standards.html` (sourcing hierarchy, independence, estimates-not-quotes, dated
  corrections policy + empty log, privacy). Both via **`gen_trust_pages.py`** (clones methodology
  shell), AboutPage/WebPage/Organization JSON-LD (validated). Filled the two dead-alias gaps (footer
  "About"/"Editorial standards" both pointed to methodology.html). Wired into single-source nav
  (build_nav stamped 580 pages) + sitemap. qa_sweep 582/0 JS, prose 0 drift. Named-founder byline left
  as an OWNER-FILL slot — did NOT invent a persona.
- **FABLE VERDICT — 3-layer citation pattern** (full writeup in **`EEAT_PLAN.md`**): (1) `/rate-filings/`
  = citation ledger, give every row a permalink anchor; (2) data pages (trackers/metros) cite inline at
  the number via GENERATORS (one template edit → all pages, patch-safe); (3) evergreen guides do NOT
  cite filings (overclaim) → cite ISO forms (HO 00 03 / PP 00 01), DOI bulletins, statute. Core insight:
  credibility currently lives on /press/ + /rate-filings/ where nobody lands; traffic lands on
  guides/trackers where credibility is thin — Layers 1–2 fix that inversion mechanically.
- **DATA-READINESS AUDIT (good news):** serff_filings.json (121) + serff_home_filings.json (132) carry
  `tracking` + `url` + `effective_new` on **100% of rows** (SERFF = deep links; CA = portal-home). →
  the citation system is a pure GENERATOR job with **no new SERFF capture needed**. Only genuinely-new
  data item = a small `coverage_sources.json` (ISO/DOI refs) for Layer 3.
- **▶ AWAITING OWNER (all in EEAT_PLAN.md §2/§5):** (A) ship real named-founder byline + real sameAs
  (strongly recommended — cheapest E-E-A-T win); (B) AI-disclosure line y/n; (C) approve footer 2-link
  retarget (581-page scoped sed); (D) green-light the 3-layer citation system + Layer-3 article scope.
  Merge/deploy the `eeat-trust-pages` branch after reviewing the About copy.

## This session (2026-07-16b, Opus 4.8) — NJ HOME backfill (8th state; regional-heavy, raising)
Parsed 20 NJ home filings → serff_home_filings.json 112→132 (NJ 20). NJ = prior-approval,
mutual/regional-dominated; the big nationals were QUIET (State Farm form/mobile only, USAA rule-only,
Travelers/Cincinnati form-only). Broadly RAISING: Andover +11.3%, Hanover +9.3%, Progressive +6.6%,
FMI/Franklin Mutual +6.5%, Chubb +6.1%, NJM +4.8% (dominant NJ writer), Mercury/Selective/Norfolk&Dedham/
Providence +5.0%, Narragansett Bay +3.5%, Cumberland +2.4%, Farmers +2.0%; **Palisades −8.0%** (cut).
Flat: Liberty +0.6% (130,883 PH), CSAA +0.6%, Harleysville −0.2%, Plymouth Rock 0%, Hartford 0%.
Amica (installment-fee filing) + US Coastal (no rate effect) skipped.
- Farmers +2.0% (eff 7/11/26) post-anchor → drifts NJ. **8 new NJ regional bases** (Plymouth Rock,
  Andover, Franklin Mutual, Cumberland, Narragansett Bay 1.5, Norfolk&Dedham 1.4, Providence, Palisades
  1.4 — coastal writers higher; NJ avg is low $1,033). Selective expanded to NJ+IL (IL add had been
  missed). Newark/Jersey City metro page (code nwj, band 0.16 → $1,132). tracker 16 raised / 1 cut;
  roll-up 233→253 rows, 13 states, 73 carriers; stability recomputed (peer median +2.8%). qa 580/0.

## This session (2026-07-16, Opus 4.8) — filing-derived RATE-STABILITY score + IL re-pull
- **IL re-pull:** the 8 partial IL downloads came back as full zips (jacket present) → added State Farm
  (0% — held its 1.5M-policy/$1.98B IL book FLAT while regionals hiked; +27.2% max by territory),
  USAA +12.3%, Selective +7.8%, Pekin −2.1% (+base); Nationwide & Travelers flat. Shelter + West Bend
  = no parseable CRI, deferred. IL 20 filings; tracker 10 raised / 3 cut; roll-up 233 rows.
- **★ FILING-DERIVED RATE-STABILITY (owner catch):** the tool's stability score (1-5) was STATIC and
  contradicted the filings — USAA scored 5/5 "most rate-stable" while raising home rates in **7/7 states
  (avg +9.2%)**. Built `gen_home_stability.py` → **`HOME_STABILITY_ADJ`**: pressure(c)=mean overall_pct
  across a carrier's filings; PEER-RELATIVE band of (pressure − peer_median); GATED on coverage (≥3
  states) so thin carriers keep their static score; frequency guard (only lower if raised in a majority,
  only raise if mostly held/cut) so one outlier can't swing it. Result (8 adjusted): **USAA 5→3,
  Progressive 3→1, State Farm 3→2, Cincinnati 4→3, Selective 4→3; Nationwide 4→5, Farmers 3→4, Liberty
  2→3.** Fixes the USAA/Nationwide inversion. Tooltip notes "Based on this carrier's recent rate filings."
  Wired via a `carrierStab(c)` helper through all 4 read sites (render + bestRec recommendation). Labelled
  as RECENT pressure (~1yr), not lifetime volatility. qa_sweep 578/0, prose 0 drift.
- **▶ NOTE — do the SAME for AUTO:** the auto tool (index.html) has **no stability field at all** (0
  `stability:` entries) — so auto needs a stability field ADDED to its roster first, then the same
  filing-derived computation from serff_filings.json (auto). Queue when we next touch auto.

## This session (2026-07-15, Opus 4.8) — HOME METRO PAGES (new SEO tier) + territory-sourcing note
- **26 home metro pages** (`gen_home_metro_page.py` → home/metro/<slug>.html) for the metros in our 6
  filed states — the home twin of the 95 auto metro pages, a content tier we didn't have. Each: metro
  avg = state avg × HOME_METRO_OFFSET, carrier ranking at metro level (order = state, prices scaled),
  per-metro home-catastrophe angle (METROS dict), "the metro average hides your ZIP" callout linking the
  tool + the dispersion guide, FAQPage + Breadcrumb JSON-LD, links to the state page + rate tracker.
  Verified: New Orleans $4,362 vs Baton Rouge $3,199; Houston $4,115 vs El Paso $2,880. In nav ("Home
  rates by metro") + sitemap (26 URLs). qa_sweep 576/0, prose 0 drift.
- **Runbook note added** (SERFF_RUNBOOK.md "While pulling: look for TERRITORY-DEFINITION sources") —
  as we pull rate changes, watch for the separate ZIP→territory map filing + BASE-RATES-by-peril weights
  that unlock true ZIP-level rating; same for auto.
- **NOTE for content growth:** home metro pages currently cover only the 6 filed states' metros (26).
  Expand as we pull more states (each new state's metros get offsets + pages). Auto dispersion rollout
  judged LOW priority (content-only, milder auto spreads, contested SEO) — parked.

## This session (2026-07-14c, Opus 4.8) — directional HOME metro offsets (sub-state granularity)
Investigated true ZIP-level rating from filings, then built the honest achievable version.
- **★ KEY FINDING — true ZIP rating is NOT extractable from rate-change filings.** Territorial
  relativities ARE standard and by-peril (wind/hail/water/fire/theft/liability), and the by-peril
  factor matrices ARE text-extractable for a subset (USAA, Selective, Chubb...). BUT the **ZIP→territory
  MAP is not in the rate jackets** — verified 0 real ZIPs in USAA/Selective/Chubb; carriers file rate
  changes against a SEPARATE, older territory-definition filing (often ISO-licensed). Also the factor
  matrices are flattened multi-column PDF tables — bespoke per-carrier parse (a naive regex gave 639
  phantom territories vs the real ~68). So: **territory FACTORS extractable, ZIP MAPS not** →
  ZIP-level pricing deferred. (The audit's "ZIP-level" flags were 5-digit factor-fragment false positives.)
- **Built instead: `HOME_METRO_OFFSET`** (gen_home_metro_offsets.py) — directional metro multiplier on
  state avg, `metro = 1 + risk_position(metro) × band(state)`. **band = MODELED from home-catastrophe
  geography, NOT scaled off filing dispersion** — because filing max/min is *change redistribution*, which
  ≠ level *gradient* (proof: OH median dispersion 40.8 ≫ LA 3.9, backwards from reality — OH carriers
  redistribute hard on ~0% filings; LA's coastal gradient is real but its +125% Allstate filing was
  image-only). Dispersion used only as CORROBORATION that big spread is real. 26 metros / 6 states:
  New Orleans 1.20 vs Baton Rouge 0.88; NYC 1.20 vs upstate 0.84; Houston 1.20 vs El Paso 0.84; OH tight
  0.99–1.04. LA/NY/PA/OH bands dispersion-corroborated; TX/CA modeled (no max/min captured yet).
- **Tool integration:** reused the auto tool's ZIP_PREFIX_METRO (product-agnostic) → home `lookupZip`
  now sets `homeMetro`; `estimatePremium` applies `× metroM`. Verified: New Orleans $3,385 / Baton Rouge
  $2,482 / rural LA $2,821 (State Farm). ZIP with no covered metro → 1.0 (state avg). qa_sweep 55x/0.
- **▶ DEFERRED / next (owner-directed): ZIP↔territory mappings.** To unlock true ZIP rating, source the
  ZIP→territory DEFINITION separately: (a) pull each carrier's territory-definition SERFF filing, or
  (b) ISO/DOI territory→ZIP tables (licensing/yield TBD). Then join to the by-peril territory factors
  (parser proven in concept) → composite offset = Σ(peril_loss_weight × territory_factor), weights from
  the filing's BASE RATES-by-peril block. **Do the SAME territory-factor + dispersion capture for AUTO
  as we pull auto filings** (auto jackets have the same Company Rate Information Max/Min block).
- **Also NEXT:** home metro PAGES (SEO tier, mirror gen_metro_page for home) now that offsets exist;
  roll By-ZIP dispersion display to AUTO trackers + /rate-filings/ roll-up.

## This session (2026-07-14b, Opus 4.8) — "By ZIP" dispersion framework (Fable idea #1) shipped
Consulted Fable on what else to extract from filings for content. Its #1: we READ the jacket's
Max %/Min % territory dispersion but never PERSISTED it — the single most on-thesis stat ("your
carrier filed +3%, your ZIP got +38%"). Piloted on OH, validated, rolled out.
- **New schema fields `max_pct`/`min_pct`** on serff_home_filings.json (widest by-territory spread from
  the "Company Rate Information" block; chunk the entity value rows [Ind,Rate,WPc,PH,WP,Max,Min]).
  Backfilled from scratchpad jackets: OH 18, LA 9, NY 7, PA 11 filings (TX/CA open-data have no
  dispersion field — stay blank, honest). **Dramatic:** LA Allstate +3.8% avg but up to **+125.3%** by
  ZIP; PA Progressive +0.9% but **+121.4%**; OH NJM +10% but **+76.5%**; four OH carriers filed "0%
  overall" while swinging +27% to −49%.
- **Display (gen_home_rate_tracker.py):** new "By ZIP" column (max/min range + "▲ wide" flag when
  worst territory ≥8pts over the average or range ≥15pts); "The filed average is not your rate" callout
  per state (pulls the biggest max + a 0%-overall poster child, incl. flat-but-wide filings that the
  |overall|≥0.5 tracker filter otherwise drops via a FLAT_WIDE pool); and **Fable #2** inline —
  "wanted +X%" muted note when the carrier's actuarial INDICATED change exceeds what it filed (file-and-
  use framing = "more increases queued"). Degrades gracefully where no data (TX/CA blank).
- **New consumer guide** `home/why-did-my-home-insurance-go-up.html` (gen_dispersion_guide.py) —
  data-driven hero examples (Allstate LA +125%, Progressive PA +121%...), "0% overall = redistribution"
  section, "wanted more than they filed" section, FAQPage on the "why did my rate go up if rates are
  flat" query cluster. Owner picked the consumer title (rejected the DOI-sounding one). In nav (Home
  guides) + sitemap. ZIP-tool + tracker CTAs.
- qa_sweep 550/0, prose 0 drift. **NEXT rollout: same By-ZIP treatment on the AUTO trackers + the
  /rate-filings/ roll-up + /press/ quarterly stat; auto jackets have the same Max/Min block.**

## This session (2026-07-14, Opus 4.8) — OH HOME backfill (6th state; mixed/softening market)
Owner pulled 23 OH home jackets; parsed → serff_home_filings.json 69→91 (OH 0→22). OH = mutual-heavy,
Nationwide's Columbus home turf.
- **OH is a MIXED/softening market** (great contrast to PA's broad rise): the big national shoppers'
  carriers are **cutting or flat** — Allstate −3%, Liberty −5%, Progressive/ASI −6%; Nationwide 0%
  (153,888 PH, held its home turf), Farmers 0%, American Family 0%, Auto-Owners −0.1% (141,511 PH),
  Cincinnati −0.01%, Amica 0% — while **USAA +15.8%** (105,620 PH, the big raiser) and OH regional
  mutuals raise: **Central +17.1%**, NJM +10%, Ohio Mutual +7.3%, Westfield +6.5%, Grange +5.7%
  (99,058 PH — OH is Grange's home base), Hartford +5.4%, Chubb +4.1%, Erie +2.3%, Motorists +2.0%;
  Celina −4% cutting. Tracker: 10 raised / 4 cut.
- **State Farm OH DEFERRED** — HO-50149 (SFMA-134927661) jacket is image/Excel-exhibit-only (no
  extractable %); the parseable HO-48693/HO-49422 weren't pulled. Coverage still strong (7 top carriers).
- **OH drift = correct no-op** (all OH movers effective ≤ 2026-07-02 anchor). HOME_DRIFT stays TX + PA.
- **4 new OH regional base entries** (book-avg ÷ OH avg $1,580): Motorists/Encova 1.15, Ohio Mutual 1.10,
  Central 1.05, Celina 0.88. **Expanded Grange (base 1.0→0.90, regrounded on its OH home book),
  Selective, Donegal to states:["OH","PA"]** (multi-state regionals — the earlier PA-only restriction
  was too narrow). Westfield/Cincinnati/NJM/Erie already had OH.
- Cascade: new home/rate-changes/ohio.html (10 raised / 4 cut) + hub; roll-up 190→212 rows, 11 states,
  63 carriers; press; OH highlights; sitemap; qa_sweep 549/0, prose 0 drift.
  **Home tracker: CA + TX + LA + NY + PA + OH.** NEXT: IL, or FL (painful).

## This session (2026-07-13f, Opus 4.8) — PA HOME backfill (5th state) + FIRST filing-driven drift beyond TX
Owner pulled 17 PA home jackets; parsed → serff_home_filings.json 53→69 (PA 0→16). PA home = the
**most fragmented market** (250 filings, Erie + a long tail of ~30 small mutuals).
- **PA is a RAISING market** (unlike NY's flat): **State Farm +6.3%** (raising here, flat in NY),
  USAA +6.2% (120,317 PH), **Erie +1.0%** (Exchange, PA's #1 home writer — 298,876 PH / $332M),
  Selective +8.5%, Cincinnati +3.8%, Grange +3.3%, Progressive/ASI +0.9%; **Farmers −10.0%** (FLEX,
  the notable cut). Flat: Liberty, Nationwide (203K PH), Chubb, Auto-Owners, Horace Mann, Donegal, CSAA.
  Allstate (ANAIC) = image/Excel-exhibit rate, not cleanly parseable → deferred.
- **★ PA is the 2nd state (after TX) with REAL applied drift** — USAA (+6.2%, eff 7/13/26) and Farmers
  (−10%, eff 7/10/26) are **post-anchor** (2026-07-02) → they drift. **Farmers ×0.854** (its cut ranks
  Farmers CHEAPER in PA — the tool now rewards the cutter from a primary filing), USAA ×1.007;
  written-premium weighted (USAA $150M ≫ Farmers $7.4M). Verified: PA ranking Erie #1 $747, Farmers
  drifted to #8 $1,009. **This is the whole thesis working end-to-end: a SERFF filing moved the tool.**
- **3 manual base entries** for aggregator-blind PA regionals (Selective 1.05, Grange 1.0, Donegal 0.92 —
  modeled mid-market priors; PA filings are small sub-programs w/ no clean book avg). states:["PA"].
- Cascade: new home/rate-changes/pennsylvania.html (7 raised / 2 cut) + hub; roll-up 174→190 rows,
  10 states; press; PA highlights on home/state/pennsylvania.html; sitemap; qa_sweep 548/0, prose 0 drift.
  **Home tracker: CA + TX + LA + NY + PA.** NEXT: OH / IL, or FL.

## This session (2026-07-13e, Opus 4.8) — NY HOME backfill (4th home state; restrained market)
Owner pulled 13 NY home SERFF jackets; parsed → serff_home_filings.json 42→53 (NY 0→11).
- **NY is a RESTRAINED home market** (unlike TX/CA/LA crisis) — the editorial through-line:
  **State Farm held its NY book FLAT (0.0%, ~1M policies / $1.1B)**, Nationwide 0%, Mercury 0%, Amica
  ~0% (windstorm restructure), Kingstone 0% (indicated 5.1% but revenue-neutral territory reshuffle),
  and **NY DFS DISAPPROVED Allstate's home increase** (AVPIC HO, ALSE-134868072; Travelers & Chubb
  filed form/rule only — no rate). **6 movers, all single-digit:** Liberty/Safeco +9.7% (16,190 PH),
  USAA +5.6% (90,145), NYCM +4.61% (55,258 / $96M — NY's top mutual), Preferred Mutual +4.5%,
  US Coastal +2.8% (coastal LI), Hartford +1.7%.
- **4 manual base entries for aggregator-blind NY regionals** (per the 07-13d runbook process):
  NYCM 1.15, Preferred Mutual 1.05, US Coastal 1.65, Kingstone 1.9. Bases = book-avg ÷ NY avg ($1,223),
  **tempered** (halve the excess over 1.0) because coastal regionals' books concentrate downstate/LI
  and overstate the standard-dwelling quote. NY ranking now: nationals cheapest, Preferred mid,
  NYCM upper-mid (raising → not cheap), US Coastal/Kingstone priciest (coastal specialty) — filing-consistent.
- **NY drift = correct no-op** (all 6 movers effective ≤ 2026-07-02 anchor → already in the aggregator
  baseline). Only TX still drifts. Utica EDGE (393 PH, +0.2%) skipped as immaterial; Palisades combined
  rate impact not cleanly parseable → deferred.
- Cascade: new home/rate-changes/new-york.html (6 raised / 0 cut) + hub; roll-up 163→174 rows; press
  refreshed; NY home-filing highlights injected into home/state/new-york.html; sitemap; qa_sweep 547/0,
  prose 0 drift. **Home tracker now covers CA + TX + LA + NY.**
- **NEXT home states:** PA / OH / IL (big markets, same SERFF-FA flow), or FL (painful). Each new
  state: pull → parse → add regional base entries → apply_home_filings.py --apply → cascade.

## This session (2026-07-13d, Opus 4.8) — home drift: regional base entries + market-share weighting
Follow-ups to the home drift engine (07-13c ↓):
- **Manual base entries for 2 aggregator-blind LA regionals** → HOME_CARRIERS (home/index.html):
  **Louisiana Farm Bureau** base 0.88 (cheap member mutual, cf. TX Farm Bureau 0.78; raising +14.75%
  so not rock-bottom) and **Allied Trust** base 1.2 (coastal specialty, SERFF book avg $4,632/policy ≈
  1.27× LA avg $3,635). Both `states:["LA"]`. Now in the LA ranking (LA Farm Bureau #4 $3,199 mid-pack;
  Allied Trust ~$4,362 pricey) — filing-consistent (raiser not cheap, cutter not shown cheap), and the
  drift engine can now rerank them as post-anchor filings land. LA/TX static pages regenerated.
- **PROCESS documented** (SERFF_RUNBOOK.md "HOME: add a manual base entry for each aggregator-blind
  regional you pull"): base = book-avg premium ÷ state avg; farm bureaus ~0.78–0.90, coastal specialty
  >1.1; then regen + `apply_home_filings.py --apply`. **Do this for every new home state's regionals.**
- **HOME MARKET-SHARE WEIGHTING** — `home_market_share.json` (NAIC 2024 homeowners multi-peril top-25,
  sourced Agency Checklists/NAIC + S&P: State Farm 18.21, Allstate 8.97, USAA 6.89, Liberty 6.14,
  Farmers 5.51, AmFam 4.99, Travelers 4.72, Chubb 2.54, Nationwide 2.16, Auto-Owners 1.99, Erie 1.93,
  Progressive 1.90, ...; floor 0.20). Wired into `apply_home_filings.py` F̄ as the weight when NO carrier
  has SERFF written_premium (CA/TX rows carry none) — was equal-weight. TX F̄ now market-share-weighted:
  Chubb ×1.024, Liberty ×0.993, Nationwide ×0.991 (Liberty's 6.14% share correctly outweighs Chubb's
  2.54%). qa_sweep 546/0, prose 0 drift. **Home is now the full auto-parity primary-source stack:
  anchor + coverage gate + renormalized drift + market-share F̄ + applied layer.**

## This session (2026-07-13c, Opus 4.8) — HOME DRIFT ENGINE built + APPLIED (tool now primary-sourced)
Owner directive: build a home drift engine that auto-updates rankings from a **prior baseline + new
filing data**, so the tool gets more primary-sourced as data accrues. Built the home twin of
`apply_filed_changes.py`, but as an **APPLIED separate layer** (auto's is dry-run/in-place).
- **`apply_home_filings.py`** — reads the home model from home/index.html (HOME_CARRIERS roster,
  STATE_CARRIER_ADJ, HOME_STATE_DATA avg) + serff_home_filings.json + **`anchor_dates_home.json`**
  (default 2026-07-02 = last home calibration). Math mirrors auto: F(s,c)=Π(1+pct/100) over
  **post-anchor** roster-carrier filings (pre-anchor already in the aggregator snapshot → skipped, no
  double-count); F̄=WP-weighted (else equal) mean; **DRIFT(s,c)=F/F̄** (shifts ordering not level);
  level=stateAvg×F̄ REPORTED only. Coverage gate ≥3 top home carriers. Modes: dry-run / `--emit`
  (home_drift.json sidecar) / `--apply`.
- **Architecture = SEPARATE `HOME_DRIFT` layer** (NOT in-place mutation of the aggregator-calibrated
  ADJ). home/index.html now: `m = base × STATE_CARRIER_ADJ × HOME_DRIFT` (two surgical edits:
  estimatePremium + a delimited `HOME_DRIFT` block after STATE_CARRIER_ADJ). Keeps the hand-calibrated
  prior intact + re-generatable; drift is resettable (bump anchor on recalibration → no double-count).
  **This is the [[boringrate-primary-source-architecture]] realized for home: prior + renormalized
  primary-source drift; more primary-sourced as filings land.**
- **APPLIED today: TX only** (correctly). Post-anchor TX roster movers → **Chubb ×1.021** (+2.9% filing),
  **Liberty Mutual ×0.990** (−0.2%), **Nationwide ×0.988** (−0.4%), renormalized F̄=1.008. Verified in
  the real calc: TX Chubb $5,329→$5,442, Nationwide $3,160→$3,124. **CA + LA = correct no-op** (all their
  filings pre-anchor 2026-07-02 → already in the aggregator baseline; drifting would double-count — same
  discipline that makes the auto engine a no-op on TN). Texas FAIR Plan −25% skipped (not in home roster).
- **Consistency kept:** made `gen_home_state_pages.py` drift-aware (multiplies HOME_DRIFT too) so the
  static home/state pages match the tool — regenerated (only texas.html changed; Nationwide $3,124 matches).
- **HOW IT GROWS:** each new home-filing pull → re-run `python3 apply_home_filings.py --apply` +
  `gen_home_state_pages.py` + `gen_home_filing_highlights.py`. As file-and-use filings post-date the
  2026-07-02 anchor, they drift in automatically. On the next aggregator recalibration, bump the anchor
  (reset). Per-state anchor override lets you tighten a deeply-pulled state to trust filings sooner.
- **LIMITATION:** only roster carriers drift; aggregator-blind LA regionals (LA Farm Bureau, Allied
  Trust, Cajun) have no base to tilt → need a manual base entry (the Germania-auto pattern) to rerank.
  No home market-share weights yet (auto has NAIC PPA); F̄ falls back to equal weight when WP is null.

## This session (2026-07-13b, Opus 4.8) — JOURNALIST PLAY shipped (item 1) + LA home backfill
- **✅ `/press/` landing page SHIPPED** (`gen_press_page.py`) — the journalist-facing rate-summary /
  authority landing. Data-driven from rate_changes.json (_meta national framing + curated feed) +
  serff_home_filings.json: national lede (auto softening, State Farm $5B dividend), who's cutting/raising
  auto, home crisis (TX/CA/LA), how-we-source, **how-to-cite** ("BoringRate, 2026 rate-filing analysis,
  [Month Year]"), contact (hello@boringrate.com). Every figure links its primary source. In nav (About +
  Data & tools) + sitemap (0.9). Chose **/press/** over /data/ (data reads as the /rate-filings/ table).
  **Items 2 (PRESS_KIT.md expert blurb) + 3 (reporter response templates) STILL TODO** — the reactive
  Qwoted/HARO signup is owner-only.
- **✅ `/rate-filings/` roll-up upgraded to a real research tool** — added **U.S. market-share column**
  (NAIC national auto share; home + sub-top-16 regionals show —; aliases Erie/Shelter) with numeric sort,
  and **fixed date sort to be chronological** (was sorting "Aug 2025" vs "Jul 2026" as strings). Sort JS
  now dataset-driven. Also fixed the table **clipping on the right** (moved from .wrap-narrow 720px →
  wide .wrap 1180px; prose capped 720, table capped 1000, overflow-x scroll on mobile).
- **✅ LA HOMEOWNERS BACKFILL — 3rd home state, FIRST via SERFF FA jackets** (owner pulled 16 ZIPs).
  serff_home_filings.json 29→42. **7 movers:** State Farm +9.7% (303,638 PH), USAA +9.2% (76,209),
  **Louisiana Farm Bureau +14.75%** (Home Choice; asked 17.76%), Allstate +3.8% (AVPIC $271M main book)
  + +1.6% (AIC closed book); **Allied Trust −2.3%** and **Hanover −1.8%** cutting. **6 held FLAT/0%**
  (Chubb Masterpiece, Farmers, Cajun, Gulf States, Hartford, SafePort — several "Rate/Rule"-typed filings
  that netted 0%, the documented trap; SafePort filed −7.5% indicated but took 0%). LA home broadly
  RISING like TX/CA; the big LA post-Ida specialty reciprocals (Cajun/Gulf States/SafePort) held flat.
  Cascade: new **home/rate-changes/louisiana.html** (5 raised / 2 cut) + hub; roll-up 150→163 rows; press
  refreshed; LA home-filing highlights injected into home/state/louisiana.html; sitemap; IndexNow 200;
  qa_sweep 546/0; prose 0 drift. **GEICO correctly OUT of home top-10; Nationwide absent (doesn't write LA home).**
- **NEXT home states (SERFF-FA, same workflow):** big markets NY/PA/OH/IL, or FL (painful, FL-only carriers).
  Reuse the LA recipe: TOI 4.0 Homeowners / 04.0000, Rate + Rate/Rule only, Closed-Approved, home top-10
  (GEICO out), drop ZIPs in /home/knighttyler/. Jacket "Company Rate Information" overall %-impact is the
  arbiter (not the filing-type column). **Still open from queued task:** PRESS_KIT.md + reporter templates.

## ▶▶ PRIOR NEXT-SESSION TASK (owner-queued 2026-07-13) — PROTOTYPE THE JOURNALIST PLAY (Fable #5)
_Item 1 (press page) DONE 07-13b ↑. Items 2 & 3 (expert kit + reporter templates) remain._
Owner is concurrently pulling **manual home rates** (SERFF-FA; TOI 4.0 Homeowners 04.0000; home top-10
GEICO-out — see recipe in 07-10 block) — process those when the zips drop. **In parallel, prototype the
journalist/authority play** (the passive-link lever; the `/rate-filings/` roll-up is the asset it points to).
Buildable pieces (Claude builds the on-site assets; OWNER does the Qwoted/HARO/Connectively signup +
responding to reporter requests — that part can't be automated):
1. ✅ **Press / Data landing page** — SHIPPED at `/press/` (see 07-13b block above).
2. **Expert-source kit** (short reusable blurb): who BoringRate is + what it can comment on (auto & home
   rate trends, who's raising/cutting by state, from primary filings) + roll-up link — for pasting into
   reactive journalist requests. Keep in-repo (e.g. PRESS_KIT.md) or on the press page.
3. **2–3 response templates** for common reporter queries (why premiums rose, state-specific increases,
   who's cutting). Data-backed, points to the roll-up + relevant tracker page.
Respect constraints: NO unprompted PR (this is REACTIVE — responding to requests only, owner's call to
draw that line), editorial/boring voice, no email capture. See [[boringrate-auto-first-longterm]] (auto
is the long game; this authority play compounds for BOTH products).

## ⚑ STRATEGY CLARIFICATION (owner, 2026-07-13, memorized [[boringrate-auto-first-longterm]])
**BoringRate is AUTO-FIRST long-term** (more volume, the real prize) — auto is just the hardest SEO
niche to acquire cold (NerdWallet/VP/Insurify own it). **Home/renters = the near-term WEDGE**
(winnable now at low authority) to build traffic + authority while auto climbs. Do NOT read Fable's
07-10 "pivot to rate-increase transparency / homeowner" as a change of identity — it's the acquirable
wedge, not the destination. Keep investing the auto moat (SERFF/tracker/tool) for the long game.

## This session (2026-07-13, Opus 4.8) — AUTONOMOUS: roll-up + home pipeline deepened (owner out)
Owner stepped out; directive: "continue to build home rates where automated, keep trucking, make a
site that supports the user." Did the on-instruction work, then wrapped (didn't over-build unsupervised).
- **✅ Fable #3 SHIPPED — national rate-filings roll-up = the citable/linkable asset.**
  `gen_rate_filings_rollup.py` → **`/rate-filings/`**: ONE sortable/filterable sheet of every captured
  auto+home filing (State/Product/Carrier/Change/Effective/Source), server-rendered rows (crawlable/
  citable) + vanilla-JS sort/filter, Dataset JSON-LD, journalist cite line. Each row links its primary
  source (SERFF tracking # + DOI portal). In nav + sitemap (priority 0.9). **150 rows, 8 states, 41
  carriers.** DISTINCT from per-state trackers (shopper pages) — this is the ONE journalist/researcher table.
- **✅ Home filing-highlights on home/state pages.** `gen_home_filing_highlights.py` (home twin of
  gen_filing_highlights) injects "who's cutting/raising home rates in [state]" into home/state/{ca,tx}.html
  (anchor `<!-- state-rankings-end -->`), links to the home tracker. Surfaces the crisis where home
  shoppers land (home = 44% of GSC demand).
- **✅ Home pipeline DEEPENED (Fable #2).** Confirmed via search: **TX + CA are the ONLY open-data
  rate-filing states** (all others SERFF-manual — MN/SD/SC/etc.). Re-scanned both for ALL material home
  movers (not just the first shortlist) — caught many missed. **serff_home_filings.json 12→29 rows.**
  CA adds Cincinnati +35%, Progressive/ASI +32%, Mercury +6.9%, Nat'l General. TX adds Progressive/ASI
  +18%, Foremost +17.2%, Amica +10.1%, Hartford +9.9%, Vault −29.7%, TX FAIR Plan −25%. TX home is a
  massive crisis market (70 carriers with material moves).
- All gates green throughout (prose 0 drift, qa_sweep 544/0, IndexNow 200). Everything on main.
- **WHAT NEEDS THE OWNER (on return):** (1) manual SERFF-FA home pulls for top states (LA clean / big
  markets; FL home = FLOIR painful + FL-only carriers) — auto pull recipe reused, TOI **4.0 Homeowners
  04.0000**, home top-10 (GEICO OUT). (2) Auto backfill PA/IL/OH still teed up. (3) Fable #5 decision:
  reactive journalist platforms (Qwoted/HARO) in/out. (4) Optional: extend home guide cluster
  (earthquake, personal-property, liability/umbrella) — proven format, deferred (not owner-directed).

## This session (2026-07-10, Opus 4.8) — Fable strategy review + home scenario cluster + monthly pricing
- **MONTHLY PRICING in the tool** (prototype, shipped): auto rankings now show $/mo primary + $/yr
  secondary ("$172/mo · $2,058/yr est."), median chip $/mo, savings CTA "−$X/yr vs avg" (annual =
  more motivating), coverage nudge relabeled "full-coverage estimates". Display-only ÷12 at render;
  compare tray + calculator + article prose LEFT ANNUAL on purpose (SEO/honesty). Data check: our
  $2,458/yr national = ~$205/mo per-vehicle FULL-COVERAGE, aligns w/ published; low-cost states
  (ME $122/mo, OH $144/mo) hit the "~$130-150" intuition.
- **FABLE VERDICT (GSC 7-day 07-10: 12,550 imp, pos 63.5 flat, ~8 clk/wk; HOME 44% / RENTERS 39% /
  AUTO 16% / TRACKER ~0% = 31 imp).** The reframe: **identity is "rate-increase transparency"
  (product-AGNOSTIC), not "auto" — the blindsided renewal shopper is now a HOMEOWNER. Same thesis,
  moat, skills; wrong noun.** Auto tracker will NEVER be SEO (ranks pos 1-8 but ~0 demand) — it's the
  only *defensible* asset though (renters/home = commodity NerdWallet outranks). Pos-63-flat at 6wks =
  **normal new-domain sandbox, fine-for-now, thrashing is the only way to lose**; health metric =
  impression growth, not position. Title-retarget already proved on-page exhausted → lever is
  authority/time + internal links.
- **Fable's ranked plan:** (1) ✅ SHIPPED home scenario-guide cluster; (2) port SERFF extraction to
  HOME filings (FL/CA/TX/LA crisis states), FREEZE auto tracker at 9; (3) build ONE national filings
  roll-up page = the designated citable/linkable asset (passive-link version of PR); (4) internal-link
  pass into the page-2 renters frontier (DC pos 19 first); (5) OWNER DECISION: rule reactive journalist
  platforms (Qwoted/HARO) in or out — only authority lever that compounds faster than time.
- **✅ Fable #1 DONE:** 6 home "does homeowners insurance cover X" guides (water-damage, roof-damage,
  mold, tree-damage, flood-damage, foundation) via gen_home_faq.py ARTICLES — proven renters-guide
  format, 600-820w, 4-5Q FAQPage, spun from + interlinked with the does-cover hub. Nav 535 pages,
  sitemap, IndexNow 200, prose 0 drift, qa_sweep 537/0. Could extend (sewer-backup, dog-bites, wind/hail).
- **✅ Fable #1 EXTENDED:** home cluster now 9 guides (+sewer-backup, +dog-bites, +wind/hail/storm).
- **✅ Fable #2 STARTED — home SERFF pipeline seeded** (`serff_home_filings.json`, SEPARATE file so the
  auto drift engine doesn't touch home rows). CA + TX home pulled AUTONOMOUSLY:
  - **CA home = CDI Excel** (same file as CA auto, LINE CODE "HOMEOWNERS MULTI-PERIL", 112 rows):
    Wawanesa +7%, USAA +6.9%, Farmers +1.5%; nationals thin (State Farm/Allstate paused CA home).
  - **TX home = data.texas.gov iubg-btfs** (state_type_of_insurance='Homeowners', 352 filings since
    2025-07). CRISIS market: **Texas Farm Bureau +29.8%, State Farm Lloyds +19.1%**, Allstate +8.7%,
    USAA +7.3%, Farmers +4.8%, Chubb +2.9%; Travelers −5%, Homeowners of America −4.9% cutting.
  - **GOTCHAS (reusable):** (1) TX home `percent_change` carries a **trailing `%`** — strip it before
    float() (auto did NOT); (2) TX home movers are mostly **status='Pending'** (file-and-use, future
    eff dates) = real upcoming changes, include them; (3) TX home writers use **"Lloyds" entities**
    (State Farm Lloyds, Allstate Texas Lloyd's, Farmers Lloyds of Texas). Home TOI on SERFF FA = **4.0
    Homeowners / 04.0000**; home top-10 ≠ auto (GEICO OUT — brokers home; regionals matter more).
  - **✅ HOME TRACKER DISPLAY BUILT:** `gen_home_rate_tracker.py` (reads serff_home_filings.json,
    |%|≥0.5) → `home/rate-changes/{index,texas,california}.html` — per-state "who raised/cut home rates"
    pages + hub, reactive angle, homeowners voice, FAQPage, ZIP CTA to /home/. In nav ("Home Rate Change
    Tracker") + sitemap. Home states plug in as pulled. DISTINCT from the national roll-up (Fable #3):
    tracker = per-state SHOPPER pages (SEO/conversion); roll-up = ONE citable JOURNALIST table (links).
  - **STILL NEXT:** national filings roll-up (Fable #3, the linkable asset); more home states (LA clean
    SERFF-FA / big markets user-driven; FL home = FLOIR painful + FL-only carriers). Optional: inject
    home filing-highlights into home/state/{ca,tx}.html (like auto gen_filing_highlights).
- **OPEN owner calls:** #5 journalist platforms (Qwoted/HARO) in/out? Build the home tracker display
  next, or keep pulling more home states first? Auto backfill PA/IL/OH still teed up if wanted.

## This session (2026-07-09, Opus 4.8) — NY published (9th tracker state, richest backfill)
Standard **SERFF Filing Access** (filingaccess.serff.com/sfa/home/NY) = the clean workflow FLOIR wasn't.
User pulled 13 jacket ZIPs (top-10 + Mercury/Farmers); Claude unzipped + parsed each **"Company Rate
Information"** block (label header then per-entity value rows: name, Indicated%, **RateImpact%**, WP-change,
policyholders, WP, Max%, Min%). Two block formats: the label-header table (GEICO/Progressive/etc) AND a
field-list variant (USAA/Farmers: "Field Name / Requested Change / Prior Value"); both carry a clean
filing-level **"Overall Percentage Rate Impact For This Filing"** line — use that as the reliable primary.
- **NY broadly RAISING 2026** → serff_filings.json NY 0→12; 7 movers published to new-york.html:
  Farmers +8.7%, Mercury +5.0%, Liberty +4.95%, NYCM +4.94%, **GEICO +4.9% (1.53M PH / $4.44B book, NY #1)**,
  Travelers +3.03%, Progressive +1.1%. **State Farm / USAA / Erie = 0% symbol/model-year filings**
  (drift_exclude, flagged NOT rate holds — same trap as FL); Allstate/Nationwide 0% genuine entity holds.
- Option (b) date curation: led with 2026-effective; GEICO/Farmers/Travelers noted as current in-force
  2025-set rates. verify_rate 0, prose 0 drift, qa_sweep 531/0, IndexNow 200. Drift no-op (movers
  pre-anchor or not-in-roster). NY zips (~40MB) deleted after extraction (data in backbone).
- **Richest state yet** (premium + policyholder counts on every mover) — SERFF FA jackets >> TX API / CA
  Excel / FL FLOIR for data quality. **Reuse for PA/IL/OH.**

## This session (2026-07-08, Opus 4.8) — FL FLOIR pull (painful) + top-10 target + automated-source scan
- **TOP-10 is now the sourcing/consistency target** (tool ranks up to 20). Added TOP10_DEFAULT +
  per-state TOP10_OVERRIDE + coverage reporting to apply_filed_changes.py; **drift GATE stays top-5**
  (≈60% market weight). Completed states were already near top-10: GA 10/10, TN 9/10, TX 9/10, SC 7/10.
  NOTE: coverage counts carriers with a ROW; a thoroughly-pulled-but-flat state (SC) reads low because
  0%/symbol filings aren't recorded — not a pull miss (offered to add SC flat-coverage rows; deferred).
- **AUTOMATED-SOURCE SCAN: only TX (API) + CA (Excel) are turnkey.** NY portal = health only; PA/WA =
  JS/AJAX (no static file); everyone else SERFF-only. Recorded in RESUME HERE. Don't re-hunt.
- **FL via FLOIR IRFS = WORST-CASE portal, deprioritize.** IRFS Advanced Search (P&C: LOB "Private
  Passenger Auto (192)" + TOI "Personal Auto (19.0)", Rates Only, Date Closed window) returns a 595-row
  INDEX but **no rate-% column** (that's L&H-only) and **downloads are email-gated**. Worse: the
  newest-filing-per-carrier is almost always a **0% symbol/rule update, NOT a rate revision** (the
  documented trap). Pulled top-10; parsed via serff_pdftext (stdlib; 28-29MB Progressive/Liberty took
  ~min in background). **Salvaged 2 real movers → serff_filings.json (FL 0→8): Liberty Mutual -7.9%
  (26-014714), Progressive +3.8% (25-048862).** 6 others confirmed 0% symbol (SF/GEICO/USAA/Nationwide/
  FLFarmBureau/Travelers, drift_exclude); Allstate image-only, Farmers no clean form.
- **OPEN — FL Progressive reconciliation:** filing shows +3.8% (closed 6/18/26) but the tracker's WFLX
  press entry says Progressive FL **-8%** (Mar 2026) = a trajectory (cut then small raise). **florida.html
  NOT updated** pending reconciliation (tool↔filing consistency rule). Liberty -7.9% is a clean new add
  when we do update the tracker.
- **NEXT: NY via standard SERFF Filing Access** (filingaccess.serff.com/sfa/home/NY) — the clean
  jacket-ZIP workflow that made TN/GA/SC/TX easy (Company Rate Information block = overall % + premium +
  PH), far better than FLOIR. Then PA/IL/OH same way. FL keeps its press-sourced tracker page.

## This session (2026-07-07b, Opus 4.8) — CA auto backfill via CDI open-data Excel (autonomous)
Scouted LA/FL/CA for open-data (per the runbook "check for an API first"). **CA is a WIN, no SERFF:**
- **CA CDI publishes a public downloadable Excel** — `insurance.ca.gov/0250-insurers/0800-rate-filings/
  0100-rate-filing-lists/rate-filing-approvals/upload/Approval-Closed-List-YTD-6-30-26.xlsx` (refreshed
  ~15 days after month-end; filename pattern rolls by period). 5,338 rows, **stdlib-parseable** (zipfile
  + xml.etree; empty cells are OMITTED so map by cell ref, not positional zip). Columns: FILE, NAME,
  GRP #, NAIC #, LINE TYPE (PERSONAL/COMMERCIAL), LINE CODE, PROGRAM, FILING TYPE, **% RATE CHNG REQ,
  % RATE CHNG APPVD**, STATUS, CLOSED DATE (Excel serial: `date(1899,12,30)+timedelta(days=n)`),
  SERFF #. Filter LINE TYPE=PERSONAL + LINE CODE contains AUTO (excl MOTORCYCLE) + STATUS=APPROVED.
  This is the CA analog to TX's data.texas.gov API — the repeatable monthly CA pull. Parser saved in
  chat history / scratchpad.
- **Published the movers** (RATE-type filings w/ non-zero approved %): **State Farm −6.2%**
  (SFMA-134750464, primary-sources the newsroom cut we'd been citing), **Travelers +4.5%/+3.1%**
  (Quantum Auto 2.0, 2 entities), **Wawanesa +6.01%** (CA-only regional). → serff_filings.json CA 0→4;
  rate_changes.json re-sourced State Farm + added Travelers (+3.8% avg) & Wawanesa (+6.0%);
  california.html 1→3 filings; state-page highlights (1 cut / 2 up) + filed-activity feed regenerated.
  verify_rate 0 errs, prose 0 drift, qa_sweep 530/0, IndexNow 200. Shipped to main (deploy branch).
- **LIMITATION:** GEICO/Progressive/Allstate/USAA CA filings are class/symbol filings w/ BLANK
  approved-% in the sheet (CA prior-approval regime files many rate actions without an overall-% summary)
  → CA stays **1/5 on the drift gate** (correct no-op; all CA moves pre-anchor anyway). To complete CA's
  top-5 for the gate would need the individual SERFF jackets (user pull) — deferred, low priority.
- **LA/FL are MANUAL:** LA rate-filing-search 403s bots; FL FLOIR IRFS has no export. User-driven.

## This session (2026-07-07, Opus 4.8) — GSC review: retarget verdict + next-guide mining
Fresh GSC pulls (7-day + 28-day, both dropped in `_gsc/`; 28-day in `_gsc/28d/`). Exploration phase,
CTR ~0 (expected at avg pos ~62), building.
- **7-day: 11,962 imp, pos 63.2. Product split (Pages.csv): home 51% / renters 38% / auto 8% /
  tracker ~0% (18 imp).** 28-day query demand (top-1000): home 9,443 imp ≈ renters 8,232 ≫ auto 1,470.
  **The wedge is home+renters content; auto + the whole SERFF tracker draw almost nothing from search**
  (tracker ranks pos 5.5 but 11 imp — ranks without demand). Tracker's value must come from
  credibility/conversion of the reactive shopper arriving some OTHER way, NOT search volume.
- **HOMEOWNERS RETARGET VERDICT: FLAT — thread CLOSED.** The 7/1 "cheapest homeowners [state]" title
  retarget (b33d2136) did NOT move rankings: cluster sits at pos **55.7 (7-day pure-post)** / **55.9
  (28-day)** vs the pre-retarget 30–85 spread centered ~55. Titles were the lever; titles didn't work.
  → **Do NOT replicate the retarget on the 51 renters state pages** (the gate the notes set is now
  answered NO). Stop the title-retarget thread entirely.
- **Renters near-win pages (NM pos 17.4 / DC 22.7 / NV 30.8 / WV 33.8, real imp) — dug in, no cheap
  lever.** On-page is already well-optimized (exact-ish titles, ~2k words, FAQPage schema). Two
  candidate levers both came up EMPTY: (a) title retarget = the proven-flat homeowners bet; (b)
  internal links = **already comprehensive** (every top renters guide links all 51 state pages, flat
  alphabetical grid — audited). **Constraint is external domain authority + time, not on-page.**
- **NEXT-GUIDE MINING (7-day, uncovered clusters).** Winner: **"does renters insurance cover theft
  from your car / car break-ins" — 123 imp, pos 93–95, uncovered dedicated targeting.** The theft-guide
  playbook (theft page spun from the does-cover hub = 920 imp, the site's #1 page); confusing
  renters-vs-auto scenario, perfect for the format. **SKIPPED: leaks/water-leaks (291 imp, bigger) —
  the `water-damage` guide ALREADY targets it** (title "…Water Damage? Leaks, Burst Pipes & Floods",
  H1 "slow leaks") yet ranks pos 80–96 → authority problem, a 2nd page would cannibalize. Home had no
  uncovered cluster (all home demand on existing state/cost pages).
- **Growth lever going forward: MORE renters/home demand-matched guides (theft-guide format), NOT
  on-page churn of existing pages.**
- **SHIPPED the car-theft guide** (0c6b501b): `renters/does-renters-insurance-cover-theft-from-car.html`
  via gen_renters_faq.py ARTICLES config — 1,212 words, 6-Q FAQPage schema on the exact queries, the
  renters-vs-auto split angle. Internal-authority links IN from the does-cover hub + the theft page
  (pos 56 / 920 imp). Added to nav-mega + build_nav (528 pages) + sitemap. qa_sweep 530/0, prose 0
  drift, IndexNow 200.
- **BRANCH CONSOLIDATED: `serff-primary-source-pipeline` was NOT an intentional fork — fast-forwarded
  `main` to it (0060b040→0c6b501b) and pushed. main = deploy branch. Going forward, work on `main`
  (the pipeline branch still exists, same commit; ignore or delete it).** The FF shipped this session's
  market-share drift fix + docs too — safe, the drift engine is dry-run and never writes index.html.
- Housekeeping: ~8 duplicate GSC export zips + several USAA-*.zip sitting in `/home/knighttyler/`
  (can be deleted).

## This session (2026-07-06e, Opus 4.8) — NAIC market share → fixes TX drift-weighting
Second 07-06c "NEXT leverage idea." **`market_share.json`** = NAIC 2024 PPA top-25 by direct
premiums written (share %), keyed by STATE_CARRIER_ADJ roster name, fully sourced (Agency Checklists
NAIC top-25 pub. 2025-03-17 + ValuePenguin/NAIC+S&P cross-check). Wired into `apply_filed_changes.py`
as a **Layer-B (cross-carrier F̄) weight fallback**:
- **The defect:** TX filings come from the TDI/Socrata open-data API (data.texas.gov) which carries
  NO written premium → every TX row `written_premium=null` → F̄ collapsed to an EQUAL-weighted mean
  (State Farm's 1.3M-book move == a tiny regional).
- **The fix (minimal blast radius):** a state uses market share ONLY when it has **no premium signal
  at all** (every participating carrier null = TX). States with ANY real SERFF WP (GA/SC/TN) keep the
  per-filing book weight **unchanged** — verified GA/SC/TN drift output **byte-identical**. KEY
  reasoning: a filing's captured WP is the actual sub-book it covers; market share would OVER-weight
  it (GA Allstate's +5.5% filing reports only **$2.1M** = a sub-program, NOT Allstate's full ~10% GA
  footprint — giving it national share inflated GA to +2.3%, wrong). So market share is a *fallback*
  for the no-signal case, not a replacement.
- TX now on the market-share path (`weight_basis=naic_market_share` in output + sidecar) but still a
  **no-op today** (all TX moves pre-anchor). Demonstrated the mechanism on TX's filings ignoring the
  anchor: equal-weight F̄=0.98896 vs market-share F̄=0.98791 — small here (TX broadly softening, big
  carriers balance: SF −3%/18.9% + Progressive −2.5%/16.7% down, GEICO +2%/11.6% offsets) but the
  read is now economically correct; a SF-cuts-hard/regionals-raise state would diverge a lot.
- `weight` + `weight_basis` now recorded per carrier in `proposed_adjustments.json` (untracked
  artifact). No index.html/page touch, no cascade. **De-minimis floor 0.20%** for sub-top-25
  regionals (Germania/Root/Donegal/National General/state Farm Bureaus). **Per-state override slots**
  (`states:{}`) documented but empty — populate when a regional that's top-5 IN-state but small
  nationally (TX/TN Farm Bureau) gets a POST-ANCHOR participating filing (none do yet).

## This session (2026-07-06d, Opus 4.8) — funnel instrumentation SHIPPED (Plausible)
Built the first of the 07-06c "NEXT leverage ideas" — end-to-end funnel telemetry on the auto tool
(5 commits, c691a31b..0060b040, on main + pipeline, pushed; qa_sweep 529 pages 0 JS errors). All
additive, safe insert pattern (no `<script>` block replaced). Events now wired in index.html:
- **`tool_entry`** + **`from`/`from_path`** on `zip_submitted` — `classifyReferrer()` reads
  `document.referrer` (ZIP forms navigate via `location.href`, so referrer = the content page they
  clicked "See rates" on) and buckets entry by landing-page type: home/state/metro/tracker/carrier/
  compare/guide/external/direct. Lets Plausible break the funnel down by which content page fed it.
- **`results_shown`** — fires ONCE per page load (`window.__resultsTracked` guard) when a ranking
  first renders; the funnel's middle step (entry → results → quote/agent). Props: state, metro, zip,
  carriers count.
- **`agent_clicked`** — the MONETIZATION-demand event (vetted-agent thesis, [[boringrate-positioning-thesis]]);
  fires on `.agent-card-link` clicks with agent name + geo. This is the "is agent referral worth
  building" signal.
- Added **state + zip + metro** to `quote_clicked`, `results_shown`, `agent_clicked` (agents are
  hyper-local) so every funnel event carries geo for breakdowns.
- Full event set now: zip_submitted, tool_entry, results_shown, quote_clicked, agent_clicked,
  cross_sell_clicked, refine_expanded, demo_cta_clicked, email_signup.
- **USER TODO in Plausible dashboard:** add the NEW event names as Goals (tool_entry, results_shown,
  agent_clicked) + ensure custom properties enabled, else they won't chart. quote_clicked-by-carrier
  and agent_clicked are the money metrics; from-breakdown on tool_entry answers "which content converts."
- **Instrumented AUTO only** (renters/home tools not yet). **Remaining 07-06c leverage ideas:** NAIC
  market share (1 day, also fixes TX drift-weighting); expand trackers to more GSC-demand states.

## ▶ RESUME HERE — SERFF state-filings backfill loop
**What we're doing:** pulling approved SERFF auto rate filings state-by-state, extracting the
overall % + premium + policyholders, and feeding them into the primary-source pipeline.
**TN + GA + SC + TX DONE (5/5). CA now partial (movers pulled autonomously via CDI Excel — see 07-07b).**
**Next states, by ROI:**
1. **LA / FL** — remaining tracked states, each own portal, both MANUAL (no open-data API):
   LA rate-filing-search is 403 bot-blocked → use LDI press releases / SERFF LA (user pull); FL = FLOIR
   IRFS search (irfssearch.floir.gov), no export → user pull. **CA is SOLVED autonomously** (07-07b).
   Always check for an open-data path first — TX API (07-06b) + CA Excel (07-07b) both beat clicking.
   **AUTOMATED-SOURCE SCAN DONE (07-08): TX + CA are the ONLY turnkey automated auto pulls.** NY's
   non-SERFF portal (myportal.dfs.ny.gov prior-approval) is HEALTH rate apps, not auto; PA/WA have own
   portals but JS/AJAX-driven (no static download, would need API reverse-engineering); IL/OH/WI/FL/LA/NV
   + rest are SERFF-only (403s bots). So everything past TX/CA is MANUAL SERFF — don't re-hunt. 3rd-party
   aggregators (rateauthority.org, AM Best State Rate Filings) exist but are secondary/paywalled = off-limits.
   **✅ NY DONE (07-09) — 9th tracker state, most complete (5/5 top-5, 10/10 top-10).** Standard SERFF FA
   jacket-ZIP workflow (clean, gave premium+PH). 12 backbone rows; published 7 movers to new-york.html.
   **NEXT big markets same workflow: PA, IL, OH** (filingaccess.serff.com/sfa/home/<ST>). Recipe below
   worked perfectly — reuse it.
2. **NV** — deprioritized (only 2 carriers; tracker already covered by press). Skip for now.
3. Then big markets (NY/PA/OH/IL SERFF) once the tracked 8 are done.

**The loop (per state, ~repeat of TN):**
1. Search SERFF FilingAccess (`https://filingaccess.serff.com/sfa/home/<ST>`, session-bound, no
   deep-links) → P&C → TOI **19.0001 Private Passenger Auto** → **Rate / Rate-Rule**, **Closed-Approved**,
   recent. Skip Form / Rule(UWG) / Motorcycle(19.0002) / RV(19.0003) / Withdrawn. Pull the newest
   "Multiple"/statewide rate/rule ZIP per carrier to `/home/knighttyler/<TRACKING>.zip`.
2. Extract: `unzip` to `/tmp/tn/`, run `python3 serff_pdftext.py <jacket>.pdf`, parse the **"Company
   Rate Information"** block (labels then values: Overall % Indicated / Overall % Rate Impact / WP
   Change / Policyholders / WP / Max / Min). One row per entity; multi-entity trackings suffixed -2/-3.
3. Append rows to `serff_filings.json` (guard on tracking #). Opportunistically grab `premium_as_of`
   + any UX modifier (→ `rate_modifiers.json`).
4. Roll up premium-weighted family headlines → `rate_changes.json` tracker (2026-only, |avg|≥0.5%),
   regenerate pages with `python3 gen_rate_tracker.py`.
5. When a state hits ≥3/5 top-5 coverage → it clears the drift gate; re-run `apply_filed_changes.py`.

**Key files:** `serff_filings.json` (data), `serff_pdftext.py` (extractor, no pip/poppler),
`apply_filed_changes.py` / `validate_drift.py` / `anchor_dates.json` (drift engine),
`BACKFILL_AND_NEXT_STEPS.md` (full advice), `MODIFIERS_PLAN.md`, `DRIFT_FINDINGS.md`.
**Open decision (not urgent):** Finding 2 — run drift plain vs `--reach-movers` (recommend the latter,
add a ±15% cap first). **Parked:** backward-validation → run FORWARD on next NerdWallet/MoneyGeek
refresh (drop `cheapest_by_state_next.json`).

## This session (2026-07-06c, Opus 4.8) — LEVERAGING the filings (content + tool + consistency)
Owner reframed the goal (memories: [[boringrate-positioning-thesis]], [[boringrate-tool-filing-consistency]]):
reputable rate-transparency source for the REACTIVE, blindsided-by-increase shopper; tool MUST agree
with filing callouts (reward cutters, penalize raisers); optional vetted-agent monetization; NO email
capture. Shipped three things (all live on main d3ad7208):
- **Consistency guard** `verify_filing_tool_consistency.py` — evaluates the TRUE full tool roster
  (nationals + regionals from LOCAL_CARRIER_DEFS; price = avg×base×STATE_CARRIER_ADJ; NOT the
  nationals-only state_rankings.json) vs. the compounded filed trajectory. Found NO "raiser shown
  cheap" problems (the core fear) and confirmed the aggregator-calibrated tool already AGREES with the
  independent filings on the nationals = validation win. Remaining flags are framing nuances
  (nationals cut-but-still-pricey; Farmers TX = Mid-Century/County-Mutual SUBSIDIARY, not mainline —
  a documented false-positive HARD flag).
- **Tool fix (B)** — one real inconsistency: **Germania** (TX-only regional, aggregator-BLIND) filed
  ~-16% but sat at full base 0.943 outside the cheap tier. Added STATE_CARRIER_ADJ.TX "Germania
  Insurance":0.90 → now #6 (cheaper than State Farm). KEY RULE: only manually nudge aggregator-BLIND
  regionals (their base is a guess, no double-count); aggregator-covered nationals stay on the gated
  drift path.
- **State-page module (A)** `gen_filing_highlights.py` — injects a "Who's cutting and raising rates in
  [State] right now" block (from rate_changes.json) into all 8 tracker-covered auto state pages,
  framed as DIRECTION + proof ("worth a quote"/"time to compare"), links to the cited tracker; tool
  stays the cheapest-for-you arbiter. Idempotent, after the rankings block.
- **Tool banners** — rewrote stale STATE_BANNERS for TN/GA/SC/TX (were all "up"; TN said "+32%" while
  our filings show cuts) to call out the filed cuts, consistent with the state pages. Pure data.
- `recent_filed_activity.json` + `gen_filed_activity.py` = the shared feed (respects drift_exclude).
  0 prose drift, 529 pages 0 JS, IndexNow pinged. **NEXT leverage ideas (owner-endorsed):** funnel
  instrumentation (tracker→tool→profile per page); NAIC market share (1 day, also fixes TX
  drift-weighting); expand trackers to more GSC-demand states (each = a state's reactive-shopper demand).

## This session (2026-07-06b, Opus 4.8) — TX backfill COMPLETE (via TDI open-data API)
- **TX is NOT SERFF — it's TDI open data on data.texas.gov, pulled ENTIRELY via Socrata API (no
  clicking).** Two datasets: `iubg-btfs` (Home+auto filing index, has state_type_of_insurance +
  serff_id, NO %) and `ittv-5xew` (all P&C, has `percent_change` + serff_id). Join on serff_id.
  Helper: `/tmp/soda.py` (urllib). Filter: `state_type_of_insurance='Personal Automobile'`,
  `received_date>='2025-07-01'`, `status='Closed'` (=effective; TX is file-and-use). **No PH/premium
  in the data** → TX serff_filings rows have null affected/written_premium; source = data.texas.gov.
- **12 rows added → serff_filings.json (TX 0→12; file 79→91). TX now 5/5 top-5, drift no-op** (all
  material moves pre-anchor). **TX is broadly SOFTENING:** State Farm -3.0% (SFMA-134710723; newsroom
  said ~-4%), Progressive -2.5%, Germania -7.9% (TX regional, ~-16% cumulative across 4 cuts),
  Mid-Century of Texas -10.1%, Farmers P&C -5.2%; USAA/Liberty/Safeco/Nationwide/Travelers FLAT; only
  GEICO +2.0% and Allstate (+2..+10% across entities in 2026, after a -11.4% cut in Aug 2025) raising.
  **Texas Farm Bureau (TX #1): NO in-window auto filing.**
- **DATA TRAPS caught:** Progressive's -4.5% (PRGS-134716883) is an **RV** filing (product "TX RV
  202201"), not PPA — real Progressive PPA is -2.5%. Allstate's Oct-2025 +9.x% filings are "Trailer"
  products (non-core). The `percent_change` string has leading whitespace — strip before float().
- **Tracker:** re-sourced State Farm to TDI + added GEICO/Progressive/Allstate/Germania/Farmers →
  texas.html 6 filings (verify_rate 0 errors). Sitemap texas.html + hub bumped to 2026-07-06.
- **Reusable: for TX, skip the SERFF click-through entirely — query the API.** State-lookup: many TX
  carriers write through a "<Carrier> Texas County Mutual" fronting entity (GEICO/Progressive/Allstate
  County Mutual etc.) — those are the real PPA filers.

## This session (2026-07-06, Opus 4.8) — SC SERFF backfill COMPLETE (top-5 closed, all flat)
- **SC top-5 now all SERFF-sourced → 5/5 GATE PASS, drift a clean no-op (F̄=1.0).** Pulled the 3
  missing majors (Progressive, GEICO, USAA) + Nationwide + Travelers (bonus). 6 coverage rows added
  → serff_filings.json (SC 6→12; file 73→79).
- **FINDING: every carrier in this pull held SC rates FLAT (0%).** Progressive = symbol addendum 0%;
  GEICO 057 = collision/comp symbol pages, multi-company overall 0% (per-vehicle max +32%/min -10% but
  net zero) + GEICO 129 = 0%; USAA V7-symbols 0% ($686M book, 182K PH) + USAA SafePilot 0%; Nationwide
  Mutual 0% (16,396 PH). **Travelers pulled but its two newest "Rate/Rule" filings are symbol-only**
  (Quantum 2.0 Set U / Quantum 1.0 Original symbols) — last real Travelers SC revision was eff
  12/30/2025, NOT pulled (bonus, skipped from data). **SC story: the big shoppers' carriers
  (GEICO/Progressive/USAA) are holding flat while State Farm −8.1% + Allstate −7.0% cut and small
  regionals (American National +19%, American Family +8.8%) raise.** Mirror of GA's mixed market.
- **No customer-facing change** — all 0%, so NO new tracker entries and south-carolina.html is
  unchanged (still 6 filings). Data-only update (backbone + coverage + drift gate). No sitemap/IndexNow.
- Lesson reinforced: "newest Rate/Rule" isn't always a rate move — GEICO/Travelers/USAA file frequent
  **symbol** revisions typed "Rate/Rule" that net to 0%. The jacket's "Company Rate Information" block
  (overall % rate impact) is the arbiter, not the filing-type column.

## This session (2026-07-05b, Opus 4.8) — GA SERFF backfill COMPLETE (top-5 closed)
- **GA top-5 now all SERFF-sourced.** User pulled the 5 missing majors via per-carrier "contains"
  substring searches (Company Name field is literal substring, NO regex/wildcards; GEICO cluster is
  all `GECC-` so no need for the `Government Employees` fallback). 13 rows added → serff_filings.json
  (GA 7→20; file 60→73). Extraction workflow unchanged (unzip → `serff_pdftext.py <jacket>.pdf` →
  "Company Rate Information" block).
- **Material moves:** **State Farm Mutual −3.0%** (2.07M PH, $3.39B, indicated +4.4% — primary-sources
  the newsroom cut we'd been citing; SFMA-134677514) + SF Fire&Cas −1.5%; **GEICO +4.6%** (176,619 PH,
  eff Aug-2025; GECC-134514872 — NOTE its filing-level rollup shows a STALE 5.4%, but the amended
  entity rows + matching $26.6M WP change confirm 4.6%); **Farmers Group P&C +5.0%** (small 5,185-PH
  Legacy book). **Flat/0%:** USAA full-limits (held flat, $1.28B book), Farmers Insurance Exchange FLEX,
  Nationwide (both entities, territory-neutral), GFBR main book (98,705 PH). State Farm Classic =
  new-program (no %, skipped). GA stays the **mixed market**: State Farm cutting, GEICO raising, USAA flat.
- **Tracker:** re-sourced State Farm to the SERFF filing + added GEICO +4.6% → georgia.html 9 filings
  (verify_rate 0 errors). Sitemap lastmod bumped to 2026-07-05.
- **DRIFT — GA is the first non-trivial run + surfaced a real defect.** With 5/5 coverage + several
  genuinely FUTURE-effective 2026 increases (Allstate eff 7/13, Liberty 8/31), the engine (which
  gates on **effective date > anchor**, not disposition) legitimately drifts them. BUT USAA's
  **+9.9% is MIN-LIMITS-only** (segment, not standard coverage) and was polluting the drift → a
  spurious **+6.1%** state-avg proposal. **Fix shipped:** added `drift_exclude` flag on the min-limits
  row (USAA-134985185) + engine now skips `drift_exclude` rows. After: GA level **+0.04%** (F̄=1.00042),
  a near-no-op with correct per-carrier reranking (Allstate/Liberty ADJ up, rest flat). Engine still
  NEVER writes index.html. **Takeaway for future states: flag any min-limits / segment-only filing
  `drift_exclude` at capture time.**

## ✅ DONE: TN SERFF backfill COMPLETE (2026-07-03) → see `TN_SERFF_WORKING.md`
All 18 TN filing zips parsed → `serff_filings.json` (**34 TN entity rows**, tracking-# keyed).
Rolled up to 11 TN tracker entries in `rate_changes.json` (premium-weighted family avgs) and
regenerated `article/rate-changes/tennessee.html` (3 raised, 8 cut). Extraction win: parse the
SERFF "Company Rate Information" block from `serff_pdftext.py` output — no visual reads needed.
Headlines: State Farm −10.7% then −6.8% (two cuts/yr, 1.3M book); Progressive −4.3% (444K
policyholders); American National asked +17.1%, got +8.0%; Safeco held flat despite −13.5%
indicated. Full results table + content angles in **TN_SERFF_WORKING.md**.
_Deferred (unchanged): `apply_filed_changes.py` rate-model feed; coverage_changes splits._

## This session (2026-07-04b, Opus 4.8) — autonomous heartbeat batch

- **First real `rate_modifiers.json` entry:** GEICO TN **homeowner discount** (Exhibit 5 of
  GECC-134888920) — factor table by coverage × Prior BI Tier; tiers A/B were cut ~-4.5%/-4.3% in
  this filing. Captured value + prior_value, dated + sourced. On-plan opportunistic capture.
- **Article updated:** `tennessee-rates-dropping.html` now includes GEICO -5.0% (table row + FAQ).
- **Engine completed:** `apply_filed_changes.py` gained `--reach-movers` (Finding 2 option b) —
  initializes a 1.0 ADJ entry for tracked carriers with post-anchor filings but no STATE_CARRIER_ADJ
  entry, so drift can reach them (proposes NEW entries for American Family, American National in TN).
  Off by default (conservative); still never writes index.html. Verified both modes.
- Queue for next heartbeat: 2nd article (indicated-vs-approved angle), more modifier captures,
  GA/SC readiness. Blocking dependency unchanged: 2nd dated aggregator snapshot for backward test.
- **2026-07-04b/c:** Tightened DRIFT_FINDINGS.md with the --reach-movers renormalization nuance.
  Modifier scan of all extracted TN attachments → only GEICO's Exhibit 5 (homeowner) exposes clean
  factor values (captured); Root RFD + GEICO/others hold factors in undelimited/image tables (not
  safely parseable — logged in MODIFIERS_PLAN.md "Scan log", NOT fabricated).
- **Backward-test snapshot: archive fetch BLOCKED.** web.archive.org and archive.ph both refused in
  this env; git history is same-day (2026-06-23 ×2). Found a usable older Wayback snapshot
  (2025-11-25) but can't fetch it here. Need user to grab it OR wait for next NerdWallet refresh.
  Wayback URL: web.archive.org/web/20251125175056/https://www.nerdwallet.com/insurance/auto/cheapest-car-insurance
- **2026-07-04d:** Quality pass on the drift scripts — simplified the coverage-gate (store roster
  names in `coverage[st]`, drop the convoluted `roster_name(x,None)` path), guarded `overall_pct`=None
  rows, added `base_tracking()` helper, `--help`, and an empty-parse guard in `load_model`. Output
  verified unchanged (TN 5/5, no-op); `--emit` writes `proposed_adjustments.json` (provenance sidecar).
- **2026-07-05:** User pasted the NerdWallet Nov-2025 archive. The per-state "cheapest by state"
  table is an interactive MAP widget that failed to render from Wayback (client-side exception) →
  per-state winners NOT captured, so the **backward-validation is still blocked**. BUT the national
  company medians came through and gave a real guardrail win: model base ordering
  (USAA<Travelers<GEICO<State Farm<Progressive) matches NerdWallet Nov-2025 full-cov ordering
  EXACTLY — **0 discordant pairs**. Saved as `cheapest_national_nov2025.json`. NOTE: this validates
  the base/prior LAYER, not the drift mechanism (that still needs per-state Nov-2025 data — try
  MoneyGeek's static by-state table, or NerdWallet per-state pages, for TN/GA/SC/NV).

- **2026-07-05 — backward test PARKED (decision).** Tried 3 sources for an older per-state ranking:
  NerdWallet current per-state = interactive map, won't render from archive; NerdWallet national =
  captured (base-order guardrail ✓) but no per-state; MoneyGeek = user landed on the "after an
  accident" page (wrong profile) dated 2026-05-30 (only ~3wk before anchor → no filing gap). Archive
  fetch blocked in-env. CONCLUSION: stop hunting historical snapshots. **Run the drift validation
  FORWARD on the next NerdWallet/MoneyGeek refresh** — drop that future by-state pull in as
  `cheapest_by_state_next.json` (per-state cheapest tier + snapshot_date) and re-run `validate_drift.py`;
  the harness is already built for it and the gap will contain real post-anchor filings. No archive
  needed. The base-layer guardrail (national ordering, 0 discordant pairs) already stands as the win
  from this exercise. Thread closed.

- **Heartbeat WOUND DOWN (honest call):** high-value autonomous queue is exhausted — everything left
  is blocked on either the user's 2025-11-25 Wayback paste (backward test) or a new SERFF pull
  (GA/SC coverage). Stopped rescheduling rather than manufacture busywork. Resume triggers: paste the
  Wayback data → build cheapest_by_state_prev.json + run convergence; or pull GA/SC majors.

## This session (2026-07-04, Opus 4.8) — drift engine built (steps 1 & 2)

- **Step 1 done:** `anchor_dates.json` (per-state `anchor_as_of`, default 2026-06-23).
- **Step 2 done:** `apply_filed_changes.py` (drift engine — parses model from index.html, F/F̄
  renormalization, coverage gate, provenance sidecar; NEVER edits index.html) + `validate_drift.py`
  (backward-test harness, currently PENDING a 2nd snapshot). Full write-up in `DRIFT_FINDINGS.md`.
- **Key finding:** engine is a correct **no-op on TN today** — 27/38 TN filings are pre-anchor
  (already in the 2026-06-23 snapshot), so drifting them would double-count. Reset discipline
  validated. Drift's value accrues as the anchor ages / for stale-snapshot states.
- **Design decision pending (Finding 2):** the real movers (Progressive, Shelter, Country Financial,
  American Family, American National) have no STATE_CARRIER_ADJ entry, so drift can't reach them.
  Recommend initializing 1.0 entries for tracked carriers (gated + capped). Not yet decided.
- **Critical path:** capture the NEXT NerdWallet/MoneyGeek snapshot WITH its date
  (`cheapest_by_state_next.json`) → unblocks the one true backward-validation test.
- User pulling **GEICO + TN Farm Bureau** filings (both already in TN ADJ) — if GEICO is
  post-anchor it becomes the first roster carrier to actually drift TN.
- **GEICO + TN Farm Bureau parsed (6 rows added, serff=60):** GEICO 099 (GECC-134888920)
  **-5.0%** (Indemnity+Marine, ~44.5K PH); GEICO 265A (134661271) 0% veh-factors; TN Farmers 2026
  (TNFA-134754677) **+0.13%** flat on a $1.07B/540,995-PH book; TN Farmers 2024 (133965333) +6.4%.
  GECC-134599128 = clerical (skipped); GECC-134029040 = 2024/400MB (skipped, pre-anchor).
  **All pre-anchor** → TN now **5/5 top-5 covered** and drift STILL a correct no-op (everything
  already in the 2026-06-23 snapshot). Strong validation: full coverage, zero double-count.
  GEICO -5.0% added to TN tracker (12 entries; SF -10.7% preserved), tennessee.html regenerated.
  NOTE: tennessee-rates-dropping.html article does NOT yet include GEICO (optional add).

## This session (2026-07-03b, Opus 4.8) — TN complete + architecture direction + article

- **TN SERFF backfill finished** (see DONE block above): 34 rows → serff_filings.json, 11 TN
  tracker entries, tennessee.html regenerated.
- **Direction set: go primary-source-driven** (SERFF as backbone; 3rd-party = re-zeroed prior +
  guardrail + validation). Fable's verdict captured in `boringrate-primary-source-architecture`
  memory: filings own the time-derivative (movement/ordering), never dollar levels; rate-manual
  bottom-up = tar pit; add per-state `anchor_as_of`; TN is the pilot but needs GEICO + TN Farm
  Bureau; next step = build `apply_filed_changes.py` + backward-validate on NV/GA/SC.
- **Modifier plan**: `MODIFIERS_PLAN.md` + empty `rate_modifiers.json` scaffold — opportunistic,
  dated, per-carrier UX-aligned modifiers; gated, deferred behind apply_filed_changes.py.
- **Briefing written**: `BACKFILL_AND_NEXT_STEPS.md` — data inventory, ranked backfill advice
  (TN→GA→SC; NV deprioritized), full next-steps.
- **New article**: `article/tennessee-rates-dropping.html` (cloned Florida template, TN content,
  every figure links to its SERFF tracking #). ⚠️ NOT yet linked from global nav — to add, edit
  `partials/nav-mega.html` + run `build_nav.py` (single-source; don't hand-edit per page).

## This session (2026-07-02d) — filings→tool design (Fable consult) + presentation data

- **DECISION: keep pulling states first, build `apply_filed_changes.py` later**
  (coverage gate keeps most states frozen until backfilled, so no rush).
- **Fable consult on how filings help the rate tool (full design in
  SERFF_RUNBOOK.md "Feeding filings into the rate tool"):** use filing %
  CHANGES as renormalized drift on STATE_CARRIER_ADJ — NOT filing dollar
  levels (book-blend, ±45-100% off a profile quote, dead for leveling). Key
  disciplines: premium-weight-average entities per family; renormalize drift to
  state mean (shifts ordering not level); RESET drift to 1 on every
  NerdWallet/MoneyGeek recalibration (else double-count); COVERAGE GATE (only
  apply drift once filings cover a state's top-5 carriers). Market-share
  reconstruction REJECTED as gold-plating (NAIC publishes it free if needed).
  Validate backward against next published refresh.
- **serff_filings.json now flags presentation_uses** (_meta) — which captured
  fields power customer-facing angles: coverage splits ("liability- vs
  repair-driven"), indicated-vs-approved ("carrier asked +24%, state approved
  -10%"), prior-revision (trajectory), new-vs-renewal dates ("shop before your
  renewal"), premium+count (scale/credibility). Keep capturing these per pull.

## This session (2026-07-02c, Opus 4.8) — SERFF GA backfill + zip/jacket workflow

- **GA backfilled (Oct 2025–Jul 2026): 8 filings, 6 newly primary-sourced.**
  254 GA filings → triaged to keeps: Travelers −10.1% (109k PH, −$40.8M, the
  big one), Progressive −4.1%, Amica +8.9% (19k), AmFam +7.5%, Allstate +5.5%,
  Donegal +5.0%, Liberty +3.4% (13k); +existing State Farm −3% (newsroom).
  Skips (all 0%/neutral or immaterial): GEICO, USAA, Farmers (FLEX "Decrease"
  but 0.0% impact), Nationwide, Mercury, Country, Auto-Owners (17 PH).
  **GA is a MIXED market** (shoppers' carriers cutting, agent/regional raising)
  vs NV's all-increase — good editorial contrast.
- **WORKFLOW BREAKTHROUGH (in runbook): zip → jacket PDF.** User clicks
  "Download Zip File", drops in ChromeOS Linux files (Chrome Downloads is NOT
  auto-shared to Linux — Files-app copy required); Claude unzips to
  `_serff/<STATE>/` (gitignored) and reads the `<TRACKING>.pdf` **jacket**,
  whose Disposition + Rate Information table has EVERYTHING (overall % impact,
  PH/vehicle count, both eff dates, disposition date, prior revision). No
  supporting-doc digging, no copy-paste. SERFF still 403s bots so the download
  stays human.
- **Triage refinements added to runbook:** "Rate/Rule" ≠ rate change (skip
  Neutral/0.000% even for big carriers); State Farm INS = billing filing;
  File-and-Use IS real (mixed states); big carriers hide in "Multiple" rows;
  "-G" tracking #s break the filingId deep link (row-click instead);
  "Approved as Amended" → trust the _REV/jacket number not the cover letter.

## This session (2026-07-02b, Fable 5) — SERFF pilot: tracker is now primary-sourced

- **User ran the first SERFF pull (Nevada) — the process works.** `SERFF_RUNBOOK.md`
  is the repeatable monthly loop (user pulls portals by hand — SERFF 403s bots,
  re-verified; Claude structures/publishes). NV June disposition window: 22
  filings → 3 real rate changes, all logged with the SERFF filing as the
  cited source (filingSummary.xhtml?filingId=<tracking digits>):
  Allstate F&C +7.971% (112k vehicles, renewals 8/10), Allstate Indemnity
  +6.706% (UM +47.4%!), Safeco +5.999% (renewals 7/17). NV page now 11 filings.
  - **Editorial through-line found in the filings: NV 2026 increases are pure
    liability/UM stories — BI +10-17%, comp/collision flat or NEGATIVE.** No
    aggregator has this; it came from reading the PC forms.
  - Noise patterns documented in runbook (symbol/model-year filings ~0%,
    "no rate effect" cover letters, PC form = fastest source of truth).
  - Table header Policyholders→"Affected" (filings count insured vehicles).
  - **USER DECISION: all 50 states + one-time backfill to Oct 2025 disposition
    dates** (captures Jan-2026-effective filings). Runbook has the phase plan +
    progress checklist — backfill the 8 tracker states first, then 12 big
    markets, then the rest, ~5/session. When user pastes PC-form data, log it
    (SERFF citation URL format in runbook), regen tracker, bump lastmod, push,
    ping IndexNow.

## This session (2026-07-02, Fable 5) — renters/home model calibration

- **RENTERS/HOME CALIBRATED vs PUBLISHED DATA (auto's playbook replicated).**
  User strategy call: content answering real queries + directionally-accurate
  rates; PR outreach deferred (memory: boringrate-strategy-content-first).
  - `build_reference_rh.py` → `cheapest_by_state_{renters,home}.json`:
    NerdWallet (renters 1/5/26, home 2/20/26) + MoneyGeek (Quadrant, home upd.
    7/1/26) cheapest-carrier-per-state, tier-scored (sources agree on in-roster
    #1 in only 20/51 renters, 4/51 home — worse than auto's 7/51).
  - `verify_model_accuracy_rh.py --product renters|home|all [--min]`: ranks
    avg×base×adj with footprint filter (same math as tools/static pages).
    USAA NOT excluded (unlike auto — MoneyGeek includes it).
  - **BEFORE: renters 57% top-5 (median rank 3), home 42% (median 6). AFTER:
    renters 93% (median 1, high-conf 19/20), home 89% (median 1, high-conf
    4/4)** via `calibrate_model_rh.py` (316dc05d): bases re-anchored to
    NerdWallet published national carrier avgs (base = rate/natl-avg, e.g.
    renters SF 1.00→0.73, Amica 1.08→0.78, Lemonade 0.52→0.78 up, Toggle
    0.58→0.85 + Assurant 0.72→1.00 — were fantasy-cheap #1-2 everywhere, never
    source-named; home Travelers 0.91→1.09, Allstate 1.15→1.09, USAA 0.72→0.78)
    + home-turf offsets on source-named states (SF home in 21 states @0.80 etc).
  - **DELIBERATE non-fixes (do NOT chase):** home Chubb stays 1.4 — MoneyGeek's
    ~12 Chubb wins are a $250k-dwelling-profile quirk (NW's $400k table never
    names Chubb); misses ME/MA/MN/WA accepted. MO home AAA + renters WI CSAA =
    footprint/roster gaps, not tunable. AK/SC renters at rank 6 = close enough.
  - Cascade: gen_renters_rankings.js + gen_home_state_pages.py (102 pages),
    audit_prose all 0 drift, ledgers synced + re-baselined w/ sources (renters
    824, home 702 atoms, next checkpoint 2026-08-01), sweep 528/528, offsets
    PASS. Renters metros have no carrier tables — no regen needed.
  - NOTE tool price LEVELS shifted with bases (e.g. renters Nationwide 0.95→
    1.28) — displayed $ estimates now track published carrier averages, not
    just ordering.

## This session (2026-07-01d, Fable 5) — tracker refresh + Plausible + Bing

- **RATE TRACKER JULY REFRESH (8698cc08).** GSC showed `article/rate-changes/` at
  **pos 4.5** — best-ranking content page on the site — but data untouched since
  6/12. Added 4 verified filings: LA Allstate North American −7.6% (10,746
  policyholders, eff 1/8/26) + LA Encompass/National General −15% (both via LDI
  11-13-25 press release — these were the "need source verify" items from 6/12,
  now verified); FL USAA −7% (FLOIR 1-28-26 PR, ~$125M/yr, replaced the older
  WFLX −8% estimate with the approved filing); FL AAA/Auto Club South −5% auto
  (AAA newsroom 6/15/26, eff 6/1 new + 8/1 renewals, 133k policyholders —
  freshest item available). WA searched, no verifiable 2026 approved filings →
  skipped (data discipline). Regenerated pages (FL now 6 filings, LA 5), bumped
  the 9 rate-changes sitemap lastmods to 2026-07-01. verify_rate.js 0 errors.
- **PLAUSIBLE WIRED (cbcfe1e6).** The "wire ONE transport tomorrow" comment sat
  since 6/11. All 3 tool pages now load `plausible.io/js/script.js` (defer,
  data-domain=boringrate.com) + official queue shim; `track()` forwards every
  event with props. Surgical exact-match block replace (asserted count==1 per
  file before write). Sweep 528/528 0 errors. 7/2: account created; swapped to
  the account-issued init-based snippet `pa-v219GyiG5lJT1bQSRxP_Z.js` (10fce7d2).
  Custom events need "Custom properties" enabled in Plausible site settings;
  add each event name as a Goal to see it on the dashboard. Script is on the
  3 TOOL pages only — article pages send nothing yet (optional batch patch).
- **INDEXNOW KEY LIVE (d2ad292f):** `/5fbfc5544ed64066bdc6a16dadf595fb.txt`.
  All 526 sitemap URLs submitted to api.indexnow.org (feeds Bing + DuckDuckGo).
  First ping got 403 SiteVerificationNotCompleted (their verification is async
  after key-file deploy); retried until accepted — see below for status.
  **USER: Bing Webmaster Tools signup is the remaining 5-min step:
  bing.com/webmasters → sign in → "Import from Google Search Console" → done
  (imports site + sitemap; no code changes needed).**
- Reporter/PR pitch drafts delivered in chat (RJ + WFLX reporters, SOS/Qwoted
  signups — note HARO/Connectively is DEAD since Dec 2024, don't recommend it).

## ⏭ NEXT SESSION — open follow-ups (read first; updated 2026-07-02, Fable→Opus handoff)

**Strategy (user, 2026-07-02, memorized):** content answering real GSC-demand
questions + directionally-accurate rates. NO PR/reporter outreach unprompted
(deferred until traffic).

1. **SERFF backfill (ongoing, user-driven — read SERFF_RUNBOOK.md).** All 50
   states + DC, window 10/1/2025→today, then monthly. NV + GA done. **Next: SC**,
   then TN/LA/FL/TX/CA, then big markets. Zip→jacket workflow (drop zip in Linux
   files → Claude reads the `<TRACKING>.pdf` jacket). Log to BOTH
   rate_changes.json + serff_filings.json (capture premium_as_of + coverage
   splits). **Then build `apply_filed_changes.py`** (design in runbook) once
   states cover their top-5 carriers — filing %-changes as renormalized drift,
   validate backward vs next NerdWallet refresh.
2. **Re-pull GSC ~7/8-7/15** (export lands in `_gsc/`, gitignored). Two calls:
   (a) did the "cheapest homeowners [state]" cluster (842 imp) climb after the
   7/1 title retarget (b33d2136)? If yes → replicate lead-with-intent titles
   on renters state pages — targets the ~250-imp "how much is renters
   insurance in [state]" cost cluster — + home carrier pages. If flat, the
   lever is authority/time; don't churn titles. (b) check whether the 7/2
   renters/home CALIBRATION (316dc05d — rankings changed on 102 state pages)
   moved anything. ALSO pull the Indexing/Coverage report (145/526 pages with
   impressions — still the biggest unknown).
3. **Content next (GSC-demand-backed, in order):** (a) FLOOD cost guide — AR
   flood queries (~24 imp) land on home pages that say "flood not covered";
   build off the home does-cover hub, gen_home_faq.py pattern. (b) "HOUSE
   insurance" synonym — ~40 "[state] house insurance rates" queries; home
   state pages never say "house insurance"; add one natural body/FAQ mention
   via gen_home_state_pages.py. (c) HOLD the renters state-page retarget until
   #2a answers.
4. **Plausible is LIVE sitewide** (526 pages, snippet pa-v219GyiG5lJT1bQSRxP_Z,
   account created 7/2). User still needs to add the 6 custom-event Goals +
   enable custom properties in the dashboard. Check events are arriving;
   quote_clicked by carrier is the money metric.
5. **Rate-accuracy tooling covers all 3 products now**: verify_model_accuracy.py
   (auto 91%) + verify_model_accuracy_rh.py (renters 93% / home 89% top-5;
   `--min` flag = CI-able gate). Deliberate non-fixes documented in the 07-02
   block — do NOT "fix" home Chubb (1.4) or chase the accepted misses.
6. **CI gates live** (prose-drift + js-sweep). After any rate edit:
   `python3 audit_prose.py` → `resync_prose.py`. After HTML/JS changes:
   `node qa_sweep.js`. After tracker edits: `node verify_rate.js` + bump
   sitemap lastmod + IndexNow ping (key 5fbfc5544ed64066bdc6a16dadf595fb.txt;
   POST snippet pattern in the 07-01d block).

_Full detail in the 2026-07-02b / 07-02 / 07-01d / 07-01c blocks below._

## This session (2026-07-01c, Opus 4.8) — GSC review + content

- **FIRST Google Search Console review** (export in `_gsc/`, gitignored; last 7 days
  6/23-6/29). Site is brand-new in Google's eyes: ~9,800 impressions, **5 clicks**,
  avg position ~59. **71.5% of impressions are page 6+** — this is a POSITION/domain-
  authority problem, not a content or CTR problem. Impressions ramping 288→2,000/day
  = healthy crawl/indexing. Don't panic about clicks; don't optimize titles/CTR yet
  (premature at pos 59).
  - **KEY STRATEGIC FINDING: auto is nearly invisible.** Top pages are ALL renters/
    home; auto (the biggest content investment) pulls almost no impressions —
    auto SEO is the most contested niche (NerdWallet/VP/Insurify own it). **Renters/
    home are the realistic near-term SEO wedge.** Weigh this before more auto content.
  - **3 near-win pages** (closest to page 1): renters/state/new-mexico (pos 17.5),
    is-renters-insurance-worth-it (pos 28), home/carrier/usaa (pos 24.5). Assessed
    on-page: **already well-optimized** (exact-match titles, good meta, 1.7-2.4k
    words, FAQ schema) — NM has 60 inbound links, USAA 70. Their only real lever is
    authority + time, NOT on-page churn. Left titles alone (no busywork).
  - OPEN (user's call): pull the GSC **Indexing/Coverage** report — only 145 of 526
    pages drew any impression in 7 days; need to know how many are actually indexed
    vs just not-yet-surfaced. Highest-leverage unknown.
- **NEW CONTENT: renters water-damage guide** (44f9335a, pushed). GSC showed a
  250-impression/wk water cluster stuck at pos 70-90 because the scenario hub gave
  water one paragraph. Built `renters/does-renters-insurance-cover-water-damage.html`
  (2.4k words, via gen_renters_faq.py ARTICLES config): covered vs not, the confusing
  ones (leak-from-above, water-vs-flood, carpet/ceiling, liability downstairs),
  first-hour steps, gap-closing add-ons; 6-Q FAQPage JSON-LD on the exact queries.
  Wired: scenario-hub + what-it-covers inbound links, links OUT to worth-it near-win
  page, "Water damage & leaks" in single-source renters nav (build_nav 525 pages) +
  sitemap. gen_renters_faq.py gained per-article read-time. JS sweep 527/527 0 errors.
- **NEW CONTENT: renters theft/burglary guide** (aa0015cb, pushed).
  `renters/does-renters-insurance-cover-theft.html` (2.3k words, gen_renters_faq):
  targets the real GSC theft cluster (burglary 86 / robbery 12 / mugging 9 / "is
  burglary covered" 8 = 106 imp, stuck pos 80-96). On/off-premises, deductible +
  sublimit traps, what's not covered, post-theft steps. Linked from scenario hub +
  links out to worth-it near-win. Nav (build_nav 526) + sitemap. JS 528/528.
  - **DID NOT build dog-bites** (was on the suggested list) — GSC shows 0 demand.
    Data-driven, not speculative. Both water + theft were spun off the does-cover
    scenario hub, which is the highest-impression renters guide.
- **RETARGET (DONE, b33d2136, pushed): "cheapest homeowners insurance [state]".**
  Confirmed the biggest cluster in GSC — **842 imp / 98 queries** (~every state) at
  pos 30-85. Diagnosis was right: the home/state pages ALREADY had cheapest body
  content (ranking table, two "cheapest carriers/companies" H2s, "what is the
  cheapest" FAQ) — that's why they surfaced — but <title>/<h1>/og/twitter/Article-
  headline all led with "Rates / average cost". Retargeted all 5 signals to lead
  with "Cheapest Homeowners Insurance in [State]" via gen_home_state_pages.py (51
  pages regenerated, NO url/nav/sitemap change). Meta now names the top-3 cheapest
  carriers but KEEPS the "is $X/year" phrase (audit_prose home guard depends on it);
  dek + body H2s keep the parallel "[state] home rates/avg cost" cluster. audit 0
  drift, JS 528/528. **This is a bet — re-check GSC positions in ~1-2 wks; if the
  cheapest cluster climbs, replicate the title/H1 lead-with-intent pass on renters
  state pages + home carrier pages.** See [[boringrate-cta-tiles]].
  NOTE the parallel "[state] home insurance rates / average cost" cluster is ALSO
  big (nebraska/SD/NM/kansas 30-35 imp each) — preserved in body, not sacrificed.

## This session (2026-07-01b, Opus 4.8) — shipped

- **PROSE DRIFT TOOLING GENERALIZED to all 3 products** (`audit_prose.py` +
  `resync_prose.py` now take `--product auto|renters|home|all`, default `all`).
  Previously auto-only; renters/home article prose had NO drift guard, so a
  renters/home rate edit could silently rot their state pages the way auto's
  CO 1706→3264 edit rotted 136 pages before the guard existed.
  - **audit_prose.py** (GUARD): recomputes each page's expected avg from that
    product's own model — `STATE_DATA`/`RENTERS_STATE_DATA`/`HOME_STATE_DATA`.
    Meta anchor `is $X/year` (renters/home) vs auto's comma-form `$X,XXX` heuristic.
    Now guards **298 pages** (auto 50 state + 95 metro; renters 51; home 51),
    all **0 drift**. Universal threshold `max(4%, $10)` reproduces auto's old
    results byte-for-byte (4%×$3k ≫ the old $40 floor). Kept every function
    resync imports (added optional args defaulting to auto) → auto path unchanged.
  - **resync_prose.py** (FIXER): same `--product`. Per-product national baseline =
    mean of that product's 51 avgs (auto $2,458 / renters $168 / home $1,863).
    Per-product plausibility bounds (renters ~$121-268 → floor $60; home ~$479 HI -
    $4.2k → floor $400, since HI home is genuinely $479).
  - **SCOPING DECISIONS (deliberate, documented in docstrings):**
    1. **Metros = AUTO-ONLY.** Only auto stores a per-metro offset
       (`METRO_CARRIER_ADJ`) in its own model; renters' 83 metro avgs were baked
       from offsets NOT in `renters/index.html`, so they're not recomputable from a
       single source (home has no metros).
    2. **resync does NOT flip bare "below/above the national average" prose** (no %).
       First cut had a bare-direction regex; dry-run caught it FLIPPING editorially-
       correct nuance: auto/alabama ($2,468 vs $2,458 nat, +0.4%) "just below" →
       "above" on a $10 gap; home/mississippi "well above" (catastrophe narrative) →
       "well below" by 1.3% (nonsense — the "well" intensity can't be recomputed).
       Removed it. Only the headline $ figure + formulaic `N% below/above` + auto
       stat-pill `&middot; ±N%` are synced. Bare direction words are editorial; a
       genuine sign flip is a human edit (audit still guards the number).
  - Applied one genuine fix surfaced by resync: **renters DC $200→$198** (18% not
    19%; page was stale by $2, under audit's tol). Only content change this session.
  - Committed + pushed (23b6bc9e tooling, 6abe8f61 DC content, 9834e718 docs).
    See [[boringrate-prose-drift-tooling]].
- **CI GATES ADDED (GitHub Actions — first CI in the repo).** Two workflows on
  push/PR to main:
  - `.github/workflows/prose-drift.yml` — runs `python3 audit_prose.py` (all 3
    products, stdlib-only ~0.14s). Fails if a rate was edited without resyncing
    prose. Pushed b5526ecf.
  - `.github/workflows/js-sweep.yml` — `npm ci && node qa_sweep.js` (jsdom, 526
    pages). Pushed 18467933. Needed `package.json`+lockfile (pinned **jsdom
    24.1.3**) and TWO qa_sweep.js fixes: (1) it was BLIND to hard errors — uncaught
    script exceptions route to jsdom's virtualConsole `jsdomError`, not
    `window.onerror`; now captures both (verified 0 across 526 real pages, but a
    broken probe page now trips it). (2) `process.exitCode=1` on any error so it can
    actually gate. `node_modules` gitignored.
  - NOTE: GitHub Pages here deploys "from branch" (independent of Actions), so these
    gates show a red X on drift/JS-error but do NOT hard-block the deploy. Switching
    to deploy-via-Actions would hard-block — deferred, user call.
  - VERIFY the runs are green: gh not installed locally → check the Actions tab (or
    `gh run list` if you have gh).

## This session (2026-06-30 → 07-01, Opus 4.8) — shipped

- **MOBILE UI FIXES (auto/renters/home tools).** Rec box: replaced the border+margin
  box with a full-width bordered box (margin 10px 0) + padding comp so the "THE
  BORING REC" tagline notches on the border and nothing bleeds/overlaps. Home
  mobile row-width: relocated the mobile rank `@media` block to AFTER the base
  rules (matched renters' working order) so desktop metrics stop leaking onto
  mobile. ZIP "See rates" button: added `flex:1 1 0;min-width:0;width:0` to
  `.zip-input` (Safari won't shrink a flex <input> otherwise). Personalization
  banner: was bleeding off-screen (150px bar + long text via 3 competing !important
  layers); mobile override shrinks bar to 56px + lets it wrap; THEN consolidated
  the 3 layers into ONE clean rule with ZERO !important (verified computed styles
  unchanged). All pushed.
- **RATE-DATA CENTRALIZATION / DRIFT FIX (the big one).** User found article prose
  averages had drifted from the model (Colorado Springs prose "$1,740" vs model
  ~$3,330; the tool + tables were current). Root cause: `gen_metro_page.py` (and
  batch/rate_tracker) hardcoded their OWN state-avg tables, so when STATE_DATA in
  index.html was corrected over time (e.g. CO 1706→3264) the prose went stale.
  NOTE: the tool showing $2,509 for a ZIP was NOT a bug — it was a SAVED localStorage
  profile; fresh/default tool = $1,802 = the article (all COVERAGE_MULT.standard &
  SHOP_MULT.web are 1.0, so tables already = tool default).
  - Sanity-checked biggest swings vs ValuePenguin FIRST: model state avgs match
    published full-coverage figures ~exactly (CO/MI/GA/CA/FL/NY exact) → model is
    right, prose was stale.
  - NEW TOOLING (single-source workflow): `audit_prose.py` = drift GUARD (recomputes
    every metro/state article avg from STATE_DATA + METRO_CARRIER_ADJ in index.html;
    exit 1 on drift, CI-ready). `resync_prose.py` = FIXER (surgical in-place number
    patch — NOT regeneration; regenerating from the stale atlanta template would
    reintroduce the old dark zip-embed CTA + drop injected sections). National
    baseline = mean of the 51 model state avgs ($2,458).
  - `gen_metro_page.py` now reads STATE_DATA + METRO_CARRIER_ADJ from index.html
    (no more hardcoded `_ST`); NATIONAL_AVG derived from the model.
  - Resynced 136 pages → audit_prose 0 drift, sweep 526/526. Also fixed a real
    collision: `por`(Portland OR) & `pme`(Portland ME) both slugified to "portland"
    (Maine's $1,490 was overwriting the OR page) → SLUG_OVERRIDE in audit_prose.py
    + gen_state_rankings.js. All pushed (a7f7e707).
  - SEO check: numbers are STATIC HTML (no client-side fetch), titles/H1 unchanged
    → no SEO harm; net positive (accuracy + consistency + freshness).
  WORKFLOW GOING FORWARD: change a rate in index.html → `python3 audit_prose.py`
  flags stale articles → `python3 resync_prose.py` + `node gen_metro_compare.js` +
  `node gen_state_rankings.js --states --metros --export` → audit_prose must go green.
  OPEN/NEXT: renters/home have their own prose pages that could use the same
  audit/resync treatment; consider a single `build_all` + CI gate on audit_prose.

## This session (2026-06-23, Opus 4.8) — shipped

- **MODEL CALIBRATION vs REAL data (the big one).** Pushed past "consistency" to
  actual accuracy. Built `cheapest_by_state.json` = published per-state cheapest
  carriers (NerdWallet, cross-checked ValuePenguin) — first real external ground
  truth in the repo. `verify_model_accuracy.py` scored the model against it:
  **before** the truly-cheapest carrier sat at median rank 9.5, in top-5 only 36%.
  Root cause: (1) national bases eyeballed wrong vs published averages (Travelers
  0.97 for real $173/$208=0.83; USAA 0.82→0.60; GEICO 0.80→0.90); (2) regionals had
  flat sub-national bases (0.65-0.82, under GEICO) + no offset → swept top-5, buried
  nationals. `calibrate_model.py` did the "full rebuild": re-anchored 8 national
  bases to published rate÷$208; lifted regional bases (American Family 0.76,
  Auto-Owners 0.82, Country Financial 0.85; rest rescaled→[0.90,1.00]); and gave
  REGIONALS per-state home-turf offsets (0.82 in their genuinely-cheapest states,
  into STATE_CARRIER_ADJ). **After: median rank 3.0, top-5 71%.** TX→Texas Farm
  Bureau #1, NJ→NJM #1, FL→Florida Farm Bureau top-3 (matches reality). Cascaded
  (gen_state_rankings --export/--states/--metros), ledger re-baselined (833 atoms),
  sweep 526/526, tool 0 JS errors.
- **Progressive flattened** (`flatten_progressive.py`): its earlier offset (tuned vs
  the in-house editorial page) fought real data — buried in IN/ME/NC. Dropped
  offsets, base 0.95→0.92, home-turf 0.82 in 6 real-#1 states → Progressive #1 in
  all 6; single-source top-5 71%→83%.
- **2nd source pulled + reference de-noised** (`build_reference.py`):
  cheapest_by_state.json now holds NerdWallet (full-cov) + MoneyGeek (min-cov) per
  state. KEY FINDING: the two agree on the in-roster #1 in only **7/51** — the
  single per-state #1 is basically methodology noise. So verify_model_accuracy.py
  now scores the in-roster cheap TIER (either source), not one #1. **Result: a real
  cheap-tier carrier in model top-5 = 89% (median best rank 2.0); high-confidence
  (both sources agree) 6/7.** Remaining misses were source-conflict/availability —
  left, not overfit.
- **CA GEICO offset fixed**: both sources say GEICO cheapest in CA but the model
  had a modeled 1.1 tilt (GEICO #9). Lowered to 0.9 → GEICO #2. **Top-5 89%→91%,
  high-confidence states 6/7→7/7 (100%).** Cascaded, sweep 526/526, ledger marked.
  NEXT: widen regional home-turf beyond #1 states (Erie/Auto-Owners footprint);
  NAIC grades; bundling guide.

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
