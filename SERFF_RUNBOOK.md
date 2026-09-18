# SERFF Rate-Filing Pull — Runbook

Goal: primary-source the rate-change tracker (`rate_changes.json`) from state
filing portals instead of news articles — ALL 50 states + DC (user decision
2026-07-02). One search per state pulls **every carrier at once** — you never
search carrier-by-carrier. Human-in-the-loop by design: these portals prohibit
bots.

## Phase 1 — one-time 2026 backfill (in progress)

Same search as the monthly loop but disposition window **10/1/2025 → today**
(filings effective Jan 2026 were approved Oct–Dec 2025 — a January window
would miss them). ~15–25 min/state once practiced. Order:
1. the 8 existing tracker states (NV done for June — backfill Oct–May only),
2. the 12 biggest remaining markets (NY PA OH IL MI NC VA WA AZ MA MO MN),
3. the rest, ~5 per session.

### Progress checklist (update as pulled; window covered in parens)
- [x] NV (Jun 2026 — still needs Oct 2025–May 2026 backfill)
- [x] GA (Oct 2025–Jul 2026 backfill done: 8 filings — Travelers −10.1%/109k, Progressive −4.1%, Amica +8.9%, AmFam +7.5%, Allstate +5.5%, Donegal +5.0%, Liberty +3.4%, +State Farm −3% newsroom)
- [x] SC (Oct 2025–Jul 2026: 6 filings — State Farm −8.1%/1.2M [25.5% share], American National +18.96%, American Family +8.8%, Allstate −7.0%, Southern Farm Bureau −3.86%, Amica +3.0%. Selective SELC-134783974 DEFERRED — increase, prior +30%, exact % unread)
- [ ] TN · [ ] LA · [ ] FL · [ ] TX · [ ] CA
- [ ] NY · [ ] PA · [ ] OH · [ ] IL · [ ] MI · [ ] NC · [ ] VA · [ ] WA · [ ] AZ · [ ] MA · [ ] MO · [ ] MN
- [ ] AL · [ ] AK · [ ] AR · [ ] CO · [ ] CT · [ ] DE · [ ] DC · [ ] HI · [ ] ID · [ ] IN · [ ] IA · [ ] KS · [ ] KY · [ ] ME · [ ] MD · [ ] MS · [ ] MT · [ ] NE · [ ] NH · [ ] NJ · [ ] NM · [ ] ND · [ ] OK · [ ] OR · [ ] RI · [ ] SD · [ ] UT · [ ] VT · [ ] WV · [ ] WI · [ ] WY

## Phase 2 — monthly maintenance (~1.5–2.5 hrs/month at 50 states)

Last-30-day disposition window per state. Nothing expires — a skipped month
just means a 60-day window next time. **Keep the thresholds strict at this
scale** (±3% / top-10 family / ≥10k vehicles) or the dataset drowns in
micro-writers.

## The monthly loop (per state)

1. Open the state's portal (table below). SERFF states: accept the terms,
   click **Begin Search**.
2. Search settings (SERFF Filing Access states). The form only has: Business
   Type, TOI, company/NAIC/product/tracking fields, and four date boxes —
   there is NO filing-type or status filter on the form (those are result
   columns). Enter:
   - Business Type: **Property & Casualty**
   - Type of Insurance (TOI): **19.0 Private Passenger Automobile**
   - Company/NAIC/Product/Tracking: leave **blank** (one search = all carriers)
   - **Start Disposition Date**: 30 days ago · **End Disposition Date**: today
   - Submission Date boxes: leave **empty** (disposition = decided filings)
3. In the RESULTS table, first filter by eye using the columns:
   - filing type includes **Rate** ("Rate", "Rate/Rule") — skip Form/Rule-only
   - disposition is **Approved / Closed-Approved** — skip Withdrawn/Disapproved/Pending
   Then keep a row when EITHER:
   - overall rate impact is **±3% or bigger**, OR
   - it's a **top-10 carrier family** (entity map below) with any change, OR
   - policyholders affected ≥ **10,000**
   Ignore the rest (tiny writers, symbol updates, 0.0% rule filings).
4. Click into each kept filing and grab (30 sec each):
   - **SERFF Tracking #** (e.g. PRGS-134...)
   - Company (filing entity name — map to family below)
   - **Overall % rate impact** (the filed/approved statewide average)
   - **# policyholders affected** (sometimes "written premium change" instead)
   - **Effective date — new business** and **effective date — renewal**
   - Disposition (approval) date
5. Hand the rows to Claude in any form (paste, screenshot, CSV — doesn't need
   to be clean). Claude adds them to `rate_changes.json` with the portal URL +
   tracking # as source, regenerates the tracker (`gen_rate_tracker.py`),
   bumps sitemap lastmod, verifies, commits, pushes, pings IndexNow.

## State portals (start = current 8 tracker states)

| State | Portal | Notes |
|---|---|---|
| NV | https://filingaccess.serff.com/sfa/home/NV | standard SERFF flow above |
| GA | https://filingaccess.serff.com/sfa/home/GA | standard |
| SC | https://filingaccess.serff.com/sfa/home/SC | standard |
| TN | https://filingaccess.serff.com/sfa/home/TN | standard |
| LA | https://ldi.la.gov/news/press-releases | they PRESS-RELEASE approvals — read the list, no search needed; SERFF LA also works |
| FL | https://irfs.fldfs.com/ (FLOIR filing search) | FL runs its own system; also watch https://floir.gov/newsroom |
| TX | https://www.tdi.texas.gov + data.texas.gov | open-data CSVs of rate filings — downloadable, no clicking |
| CA | https://interactive.web.insurance.ca.gov/apex_extprd/f?p=192:1 (CDI rate filing search) | CA is not in SERFF public access |
| WA (expansion) | https://www.insurance.wa.gov (search "rate increases") | OIC publishes approved changes as a browsable list |
| NY/PA/OH/IL (expansion) | https://filingaccess.serff.com/sfa/home/{NY,PA,OH,IL} | add once the 8 are routine |

## Top-carrier entity map (families file under many names)

Recognize these in results; log the family name in the tracker note.

- **State Farm**: State Farm Mutual Automobile Ins. Co., State Farm Fire & Casualty
- **Progressive**: Progressive Casualty / Direct / Specialty / Preferred /
  Northern / County Mutual (TX) / Security (LA) / Paloverde (LA) …anything "Progressive"
- **GEICO**: Government Employees Ins. Co., GEICO General / Indemnity /
  Advantage / Choice / Casualty
- **Allstate**: Allstate Ins. / Fire & Casualty / Property & Casualty /
  Indemnity / North American; also **Esurance, Encompass, National General** (all Allstate-owned)
- **USAA**: USAA, USAA Casualty, USAA General Indemnity, Garrison P&C
- **Liberty Mutual**: Liberty Mutual, LM General, LM Ins. Corp.; also **Safeco**
- **Farmers**: Farmers Ins. Exchange, Mid-Century, Farmers of Columbus; also **Bristol West**
- **Nationwide**: Nationwide Mutual / General / P&C; also **Allied**
- **Travelers**: Travelers Personal Ins., Travelers Home & Marine, The Standard Fire Ins. Co.
- **American Family**: American Family Mutual, American Family Connect, Midvale Indemnity

## FASTEST WORKFLOW (proven GA, 2026-07-02): zip → jacket PDF

The single best method, no copy-paste:
1. On each filing page click **Download Zip File**; drop the zip into ChromeOS
   **Linux files** (Chrome Downloads is NOT shared to Linux — the Files-app
   "copy into Linux files" step is required). Claude finds it in `~`.
2. Claude moves it to `_serff/<STATE>/`, unzips into a per-tracking subfolder.
3. **The `<TRACKING>.pdf` "jacket" is the single source of truth** — its
   *Disposition* and *Rate Information* pages carry a clean table with:
   Overall % Rate Impact, Written Premium Change, **Number of Policyholders
   Affected**, both Effective Dates (New/Renewal), Disposition Date, AND the
   prior revision % + its filing #. **You never need the supporting-doc PDFs
   for the numbers.** Claude reads the jacket directly.
   - Exception: Progressive/Travelers-style jackets split the data-row values
     into a separate text stream; if a text-extractor misses the %, just Read
     the jacket PDF and take the "Company Rate Information" table row.
   - `_serff/` is gitignored (we cite filings, don't republish); discard anytime.

## ⚠ Multi-company & 0%-typed traps (SC lessons — READ)

- **MULTI-COMPANY filings show a FAKE "Overall Percentage Rate Impact For This
  Filing: 0.000%" summary** — SERFF does not aggregate across the entities, so
  that line is meaningless. The REAL impacts are the per-company rows in the
  "Company Rate Information" table. SC State Farm SFMA-134701541 read as
  "0.000%" but was actually **−8.1%** (Mutual, 1.2M PH) / −6.0% (Fire). If the
  extractor says 0.000% but **Rate Change Type is Increase/Decrease**, DO NOT
  trust it — read the per-company rows.
- **`Rate Change Type` is the skip signal, not the impact number.** Neutral →
  genuinely 0%, skip. Increase/Decrease → real, get the per-company %. BUT even
  Increase/Decrease-typed filings can be **0.0% overall** (revenue-neutral
  factor rebalancing — SC Auto-Owners, GA Farmers); confirm with the
  "% Premium Change" field / the per-company "Overall % Rate Impact" column.
- **Cheapest reliable sources for the overall %, in order:** (1) the SC-style
  **"% Premium Change"** plain-text field on the State Specific page; (2) the
  **Co Tr Num / project name** sometimes encodes it (Allstate "R60304: RAF
  OVERALL RATE DECREASE −7.0%"); (3) full Read of the jacket's Company Rate
  Information table — EXPENSIVE (harness render; the zlib text extractor CANNOT
  get those positioned table values). Exhaust 1–2 before Reading.
- **SC forms also give `% Market Share in SC for Line of Business`** — capture
  it (serff_filings.market_share_sc). SC State Farm 25.5%, Southern Farm Bureau
  2.4%. Feeds the market-share angle directly. (Field is state-specific.)

## Triage lessons (what to skip — refined on GA's 254 filings)

- **A "Rate/Rule" filing type does NOT mean a rate change.** Check the jacket's
  Rate Change Type / Overall % Rate Impact. SKIP when it's **"Neutral" or
  0.000%** — even for top-10 carriers. On GA that killed GEICO, USAA, Farmers
  (FLEX "Decrease" but 0.0% impact — just new rating rules), Nationwide, and
  Country Financial, all of which filed 0% symbol/rule refreshes.
- **State Farm `INS-...` = billing/installment filing**, not rates (attachments
  were only a Billing & Payment Agreement + fee forms). Attachment list is the
  truth-teller.
- **Skip immaterial books** even with a real %: GA Auto-Owners filed a decrease
  affecting **17 policyholders** — not worth a row.
- **File-and-Use is NOT a skip.** In mixed states (GA), "Rate/Rule File and Use"
  → "Closed-Received/Filed" are real in-force rate filings; only skip
  Withdrawn/Disapproved/Rejected and Form-only.
- **Big carriers file as "Multiple"** with just a tracking prefix (SFMA, USAA,
  PRGS, LBPM, AOIC, TRVD) — scan prefixes, not company names.
- **"-G" tracking numbers** (NWPP-G…, TRVD-G…): the numeric part ≠ SERFF
  filingId and is NOT derivable (confirmed: NWPP-G134870398 → real filingId
  134873604, a +3,206 jump, no formula — the filingId is an internal ID stamped
  at submission). The `filingId=<tracking digits>` deep link therefore 403s.
  **Assistant: do NOT emit a fabricated filingId link for a "-G" tracking
  number** — instead point the user to the row by tracking # ("click the
  NWPP-G… row"); the row link carries the correct filingId. Plain-numeric
  tracking #s (SFMA, USAA, ALSE, PRCA…) DO map to filingId=<digits>, keep
  linking those.
- **"Approved as Amended"**: the cover-letter % is the *proposed* figure; the
  approved number is in the `_REV` exhibit / jacket disposition table (GA
  Progressive: proposed −2.7% → approved −4.1%).

## Field lessons (from the July 2026 NV pilot)

- **Fastest path to the numbers:** the "Rate Filing Data Summary" attachment
  (state PC form). One page: per-coverage %, TOTAL %, new/renewal effective
  dates, insured-vehicle count. Skip the Filing Memo unless there's no PC form.
- **Noise you can spot from the attachment list** (no PDF click needed): rows
  whose Rate/Rule attachments are "Symbol & Identification Pages", "Model
  Year 20XX", "Updated Factors", or symbol sets = annual vehicle-symbol
  maintenance, ~0.0% overall. Cover letters saying "no rate effect on the
  current book" = skip.
- Filings WITHOUT a PC form (e.g. Progressive) state the impact in the cover
  letter's first paragraphs.
- **Citation URL format:** `https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId=<digits of tracking #>`.
  Deep links may bounce readers to a terms page — cite as "NV DOI rate filing
  ALSE-XXXX (SERFF)" so the tracking # is searchable regardless. The portal
  403s bots (verified 2026-07-02) — fetching must stay human.
- "Affected" counts in filings are usually **insured vehicles**, not
  policyholders — the tracker table header says "Affected" for this reason;
  say which in the entry note.
- A "Rate Disruption" attachment existing is a strong tell the filing is a
  real rate change (disruption exhibits only accompany price movement).

## Track expansion candidates while triaging

Each state's full list surfaces non-roster carriers. When a **standard/regional**
carrier files a real (non-0%/non-symbol) PPA rate change but isn't in the tool
roster, add it to `expansion_candidates.json` with the state. Exclude pure
nonstandard/high-risk writers. This builds a data-driven roster-expansion list
(American National is the leading candidate — seen in NV/GA/SC/TN).

### While pulling: look for TERRITORY-DEFINITION sources (unlocks true ZIP-level rating)

Rate-change jackets contain the by-peril **territory FACTORS** (text-extractable for a subset —
USAA, Selective, Chubb…) but NOT the **ZIP→territory MAP** (verified absent in USAA/Selective/Chubb;
carriers file rate changes against a *separate, older* territory-definition filing, often ISO-licensed).
So true ZIP-level primary-source pricing is blocked on sourcing that map. **As you pull, watch for and
grab, when present:**
- a carrier's separate **territory-definition / territory-plan filing** on SERFF (search that carrier's
  Rule/Territory filings, not just the latest Rate filing) — the ZIP/county → territory table;
- any **ZIP→territory or ZIP→zone exhibit** attached to the rate filing itself (rare, but Chubb-type
  high-value writers sometimes include one);
- the filing's **BASE RATES-by-peril** block (present in the jacket) → the peril loss weights for the
  composite `offset = Σ(peril_weight × territory_factor)`.
When we have a carrier's factors AND its ZIP→territory map, that carrier graduates from state-avg (or the
modeled metro offset) to real ZIP-level offsets. **Same applies to AUTO** — capture territory factors +
the Max/Min dispersion from auto jackets as we pull them. See SESSION_NOTES 07-14c for the full plan.
Until then, sub-state granularity comes from the modeled directional **HOME_METRO_OFFSET**
(gen_home_metro_offsets.py), guardrailed by the captured Max/Min dispersion.

### HOME: add a manual base entry for each aggregator-blind regional you pull

**When pulling a new HOME state, add a manual `HOME_CARRIERS` base entry (home/index.html)
for every material regional that turns up but is NOT covered by NerdWallet/MoneyGeek** —
LA Farm Bureau, Allied Trust, Cajun Underwriters, Gulf States, SafePoint, Vault, etc. Without
a roster base these carriers can't appear in the tool OR be reranked by the `HOME_DRIFT` engine
(`apply_home_filings.py`), so their filings are stranded. This is the same "aggregator-blind
regional" pattern as the Germania auto fix ([[boringrate-tool-filing-consistency]]).

How to set the base (a modeled prior — the drift engine refines it as post-anchor filings land):
- **base = the carrier's typical premium ÷ the state avg.** Best signal: the filing's book average
  = `written_premium ÷ policyholders` (e.g. Allied Trust $102.08M / 22,038 = $4,632/policy ÷ LA
  avg $3,635 ≈ 1.27 → set ~1.2, tempered toward the standard-$300k-dwelling quote). Farm-Bureau
  member mutuals run cheap (~0.78–0.90, cf. Texas Farm Bureau 0.78); coastal/surplus specialty
  writers run expensive (>1.1).
- Set `states:["XX"]` (state-exclusive), `restricted:true`, an `availNote`, and copy a peer
  regional's `sens`. **Respect consistency:** a filing that RAISED shouldn't read artificially
  cheap; a CUTTER shouldn't read artificially expensive.
- After adding: re-run `gen_home_state_pages.py` → `gen_home_filing_highlights.py` → `build_nav.py`,
  then `apply_home_filings.py --apply` so the drift layer picks up the new roster carrier.
- Precise NAIC-share carriers also belong in `home_market_share.json` (F̄ weight); regionals below
  the NAIC top-25 fall to the de-minimis floor there — that's fine.

## Presenting the click list to the user

Give **full clickable `filingSummary.xhtml?filingId=<digits>` links for
plain-numeric tracking numbers** (SFMA, USAA, ALSE, PRCA, AMMA, AOIC…) — those
resolve and the user wants to click them fast. For **"-G" tracking numbers
ONLY** (NWPP-G…, TRVD-G…) the deep link 403s, so give just the digit string and
the user **Ctrl+F's it on the results page** → opens the row. Order keeps with
State Farm / biggest carriers first; then Download Zip → drop in Linux files.

**Format: ONE LINK PER LINE** (not several separated by `·` on one line) — the
user clicks them one at a time and inline separators make that fiddly. Carrier
label + the single clickable link per row.

## Assistant-side workflow (when the user pastes portal data)

1. **Triage a results table**: keep Rate/"Rate/Rule" + Closed-Approved rows
   meeting the thresholds; name the skips and WHY (symbol/model-year
   attachments, Form-only, withdrawn, advisory orgs like ISO/AIPSO/LexisNexis)
   so the user's eye keeps calibrating. Give direct next links:
   `https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId=<tracking digits>`.
2. **Log a completed filing into TWO files:**
   a. `rate_changes.json` `changes[]` (the tracker DISPLAY feed): carrier
      (family name + entity in note), state, pct (TOTAL row, 3 decimals), dir,
      effective (new-business date), renewal, affected, source
      `"XX DOI rate filing TRACKING-# (SERFF)"`, url (filingSummary link), note.
   b. `serff_filings.json` `filings[]` (the durable STRUCTURED dataset for
      future charts/tools — see its `_meta.schema`): capture the analytical
      fields the tracker drops — **indicated_pct** (asked vs approved),
      **prior_revision_pct** (rate trajectory), **written_premium** +
      **written_premium_change** (book size, for weighting), and
      **coverage_changes** (per-coverage % — the liability-vs-physical-damage
      split). All of these live in the jacket's Disposition/Rate-Information
      table EXCEPT per-coverage, which is in the **PC form "Part 1 / Requested
      Percent Changes by Type of Coverage"** — grab it whenever text-available
      (jacket-only/image exhibits → coverage_changes: null).
      Also capture **premium_as_of** — the valuation date of the book size,
      shown as "@ MM/DD/YYYY" atop the PC form Part 2. REQUIRED for any
      market-share-over-time comparison (a $298M book is only meaningful with
      its as-of date). And add `recorded_date` + a `_meta.pulls` entry
      (state, disposition window, date pulled, scanned/kept counts) so each
      state's survey is reproducible and re-runnable.
3. **Publish**: `python3 gen_rate_tracker.py` → bump that state's + hub's
   sitemap `<lastmod>` → `node verify_rate.js` (expect 0 errors) → commit
   ("NV tracker: ..." style, one commit per state batch) → push → POST the
   changed URLs to IndexNow (key file in repo root; snippet pattern in
   SESSION_NOTES 2026-07-01d).
4. Update the progress checklist above + SESSION_NOTES.
5. Never invent a figure. If a field is missing, publish without it (affected
   is optional; effective can be "approved <month>" as year-month) rather
   than guess.

## Feeding filings into the rate tool — DESIGN (not yet built)

Decision 2026-07-02 (user + Fable consult). Build `apply_filed_changes.py`
AFTER more states are backfilled (the coverage gate below keeps most states
frozen until then, so there's no rush — keep pulling first).

**Core principle: use filing % CHANGES as renormalized drift on the relative
layer. Do NOT use filing dollar LEVELS.** written_premium ÷ count is a
whole-book blend (all coverage tiers + driver types), inconsistent count basis
(NV vehicles vs GA policyholders), and ran ±45–100% off a profile quote — dead
for level-setting. The % changes are the asset.

Design:
- Per (state, carrier): `F(s,c) = Π(1 + approved_pct)` over filings whose
  effective date is AFTER the anchor's `anchor_as_of` (NerdWallet/MoneyGeek
  snapshot date; only later filings count).
- **Multiple entities per family → premium-weight-average their % changes.**
  Don't pick a "representative" book (entities aren't labeled; you'll guess
  wrong). Filed changes hit NEW business immediately (renewals lag), so the
  filed % represents the shopper better than the in-force book average — this
  is why the multiple-books worry doesn't bite the % approach.
- Apply renormalized to the state mean (shifts ORDERING, not level):
  `ADJ'(s,c) = ADJ(s,c) × F(s,c) / F̄(s)`, `F̄(s)` = premium-weighted mean of F
  across tracked carriers. Optionally drift the level `stateAvg'(s) =
  stateAvg(s) × F̄(s)` capped ±10%/yr.
- **RESET all F to 1 on every NerdWallet/MoneyGeek refresh + recalibration** —
  their new averages already embed the changes, so skipping the reset
  double-counts. This snapshot discipline is load-bearing.
- **COVERAGE GATE:** only APPLY drift in a state once filings cover the
  majority of that state's top-5 carriers. Otherwise sparse pulls distort
  ordering by which filings we happened to grab. Store filings for
  under-covered states; don't apply yet. (This is the real answer to "we can't
  know full market share" — you don't need share, you need top-5 coverage.)
- **Validate BACKWARD:** drift NV/GA filings across the gap to the next
  NerdWallet refresh; confirm drifted ordering moves TOWARD the new published
  ordering. Whole hypothesis, one test.

Rejected: filing premium-LEVELS for leveling (dead); reconstructing per-carrier
market share from old filings (gold-plating — NAIC publishes state/carrier
share free annually if ever needed). Demote premium÷count to a SCRAPER sanity
check, not a model check. Skip per-coverage-split MODELING for now (capture it;
overall % drives the drift).

## Data discipline (unchanged)

Every entry needs a real, dateable source URL — now that's the filing record
itself (better than citing an article about it). The `pct` is the approved
statewide AVERAGE; individual rates vary (regulators' own caveat — keep it in
the page footer). Never publish a figure you can't trace to a filing or an
official release.

## Why not automate the pull

SERFF public access and most DOI portals 403 bots and their terms prohibit
scraping (confirmed June 2026). Monthly cadence doesn't need automation; the
value is the primary sourcing, not the speed. Everything downstream of the
copy-paste IS automated.

## After a pull: compact the PDFs (owner policy, 2026-08-19)

SERFF PDFs are bulky and re-downloadable from the portal; their **text is neither**. Once a pull is
parsed and appended, run:

```
python3 serff_compact.py --apply
```

It extracts every PDF under `_serff/` to a sibling `<dir>_txt/`, then deletes the PDFs. It refuses to
delete anything whose extraction came back under 200 chars, so a bad decode can't silently destroy the
source. First run (2026-08-19) took `_serff/` from 36MB → 16MB, 500 PDFs → 500 .txt, zero failures.

**Keep the text, not the PDF.** The ledger JSON holds the parsed numbers, but only the jacket text
carries the context that answers follow-up questions without a re-download:
- **Supporting Document Schedules** — distinguishes "no actuarial memo exists" (Bypassed) from "we
  didn't check that download box". This is what settled the VA Farm Bureau base question.
- **Program scope** — e.g. State Farm's VA jacket discussing Condominium Unitowners, which is how the
  line-blending problem was caught.
- **DOI objection letters** — e.g. Virginia telling Liberty Mutual to file its indications and in-force
  counts.
- **Rate-manual base rates** from attachments (VAFB Homeowner $2,240.04 / Tenant $74.65 / Mobile $377.48).

Note `_serff/` is **gitignored** — nothing in it is recoverable from git. The text is the only copy.

Two extractors, try in this order (serff_compact.py already does both and keeps the better result):
- `serff_pdftext.py` — jackets (literal `(string) Tj`)
- `serff_pdftext_cid.py` — attachments (subset CID fonts: hex glyph IDs + ToUnicode CMap). The original
  returns EMPTY on these, which misreads as "no text in this PDF" rather than "wrong decoder".

No poppler in this container, so PDFs cannot be rendered to images — text extraction is the only path.

## After compacting: mine the text (2026-09-16)

`serff_compact.py` keeps the jacket text; **`mine_filing_text.py` makes it useful.** Run both after
every pull, in this order:

```
python3 serff_compact.py --apply    # PDFs -> text, delete PDFs
python3 mine_filing_text.py         # text -> filing_digests.json.gz  (committed, 25x smaller)
python3 mine_discounts.py           # digest -> rate_modifiers.json
python3 mine_capping.py             # digest -> filing_caps.json (qualifies the spread)
```

The digest keeps filing descriptions, DOI objection letters, carrier responses and reviewer notes —
the parts that answer "what actually changed and what did the regulator say", which the ledger's
percentage cannot. It is committed to git, so filing narrative survives a `_serff/` wipe.

Full rationale, what is still unmined, and the extraction rules: **`EXTRACTION_PLAN.md`**.

## Texas does not need a manual pull (2026-09-18)

TDI publishes every personal auto and homeowners rate filing to `data.texas.gov` as a plain
Socrata dataset (`iubg-btfs`) — 18,043 rows, no session, no terms barrier, updated continuously.
We had been hand-pulling a state that has an API.

```
python3 fetch_tx_filings.py                 # material 2026 filings not yet in the ledger
python3 fetch_tx_filings.py --write         # -> tx_filings_new.json for review
```

**What it does NOT give you.** The feed carries company, percent change, effective dates, SERFF id
and status, and nothing else: no policyholders affected, no written premium, no indicated-vs-taken,
no max/min spread, no filing narrative. TX rows stay thinner than hand-pulled states. This buys
coverage and freshness, not depth.

**It reports, it does not append.** The ledgers are curated — family mapping, editorial notes and
the tool↔filing consistency rule need judgement — so merging stays a human step.

Two traps found building it, both worth remembering for any future state feed:
- **TDI emits one row per COMPANY**, so a multi-company filing repeats its `serff_id` with a
  different percentage each time (FARM-134961095 appears 4× at 6.2/5.4/2.2/6.2%). Collapse per
  tracking or you double-count one filing as several.
- **Substring family matching is dangerous.** `"ace "` matched "hor*ace* mann", filing Horace Mann
  under Chubb. The matcher is word-boundary now and returns None rather than guessing, because a
  wrong family silently corrupts the drift layer.

## California is a bulk download, not a manual read (2026-09-18)

CDI publishes the Approval/Closed list as a stable YTD `.xlsx` (3,993 rows, all P&C lines,
refreshed ~15 days after each month end). We had been hand-reading it.

```
python3 fetch_ca_filings.py            # material personal auto/home not yet in the ledger
python3 fetch_ca_filings.py --write    # -> ca_filings_new.json for review
```

**★ CA gives us something no SERFF state does for free: `% RATE CHNG REQ` alongside
`% RATE CHNG APPVD`.** Requested vs approved, as a column. In SERFF states that comparison is the
indicated-vs-taken story we can only get by opening each jacket. California is prior-approval
(Prop 103), so regulators genuinely trim — State Farm asked +40.8% on home and was approved +8.7%.

Terms: `insurance.ca.gov/robots.txt` disallows `/0100-consumers/`, the statistical-plan archives,
`loader.cfm` and `login.cfm`. The rate-filing path is not restricted.

Parsed with `zipfile` + regex over `sheet1.xml` — openpyxl is not installed and is not needed,
since an .xlsx is a zip of XML.

## Survey of all 51 jurisdictions (2026-09-18)

The old ledger claim "only TX+CA publish rate-filing open data" was **mostly true but incomplete**.
Verified by fetching, not from memory:

- **TX** — Socrata API. Scripted (`fetch_tx_filings.py`).
- **CA** — bulk xlsx, richer than we credited. Scripted (`fetch_ca_filings.py`).
- **IL** — ★ the new find. `insurance.illinois.gov/Applications/CompanyRateInfo/SearchRF3.aspx`
  is state-hosted, non-SERFF, no auth, no CAPTCHA, and `idoi.illinois.gov/robots.txt` is
  `Allow: /`. Carries indicated %, taken %, written premium change, policyholder count AND the
  max/min spread — i.e. nearly everything we read jackets for. Needs a carrier→EntityNumber
  lookup then a two-call scripted loop. **Not yet built; highest-value remaining automation.**
- **~40 states** — flat SERFF pointer, no alternative. Confirmed per state, not assumed.
- **FL, LA** — a non-SERFF tool with the right data exists, but both are bot-walled (FLOIR
  CAPTCHA; LDI Cloudflare Turnstile). Treated as equivalent to SERFF's bot ban. Worth a direct
  data-sharing request rather than scraping.
- **CO** — real structured data, no login, but `robots.txt` has a blanket `Disallow: /pls/real/`
  covering the exact endpoint. **Owner decision, not automated.**
- **AL, MS** — on-domain forms, no stated restriction, but need scripted form posts. Unbuilt.
- **NAIC** — no filing-level public data centrally. **No state** offers RSS/email alerts on new
  filings, and **no state** publishes actuarial memoranda or per-coverage exhibits in structured
  form — those stay jacket-only everywhere, including TX/CA/IL.

## ★ Illinois is scripted, and it is the RICHEST non-SERFF source (2026-09-18)

IDOI runs its own Company Rate Information app — state-hosted, not SERFF, no account, no CAPTCHA,
and `idoi.illinois.gov/robots.txt` is `Allow: /`.

```
python3 fetch_il_filings.py --carrier "State Farm" --year 2025
python3 fetch_il_filings.py --carrier "Allstate" --year 2024 --line auto
python3 fetch_il_filings.py --carrier "State Farm" --year 2025 --write
```

Unlike TX/CA (a percent and little else) it returns, per filing:
**indicated % · taken % · written premium change $ · policyholder count · written premium $ ·
max % · min % ·** SERFF tracking number — i.e. nearly the whole Company Rate Information block we
open jackets for, **and multiple years in a single call.** State Farm IL home came back with 15
filings spanning 2012-2025; Allstate IL with auto and home back to 2014.

**The chain (ASP.NET WebForms — VIEWSTATE must be carried between steps):**
1. `RegEntPortal/Default.aspx` — GET, postback `rdbCriteria=5` to reveal the search box, then
   postback company name + year → links carrying `?EntityNumber=NNNNNN`
2. `SearchRF3.aspx/TOINamesForFein` — JSON PageMethod, `{EntityIDStr, filingYear}` → TOI list
3. `SearchRF3.aspx` postback with the chosen TOI → the filing table

**Traps:**
- Step 3 needs BOTH `TOINameList` (the AJAX-populated select) and `TOINameListHold`. Sending only
  the hold field makes the server throw *"Index was outside the bounds of the array"*.
- `EntityNumber` is NOT a small sequential id (probing 1-40 returns nothing) — it is a 6-digit
  registry number, and the PageMethod name `TOINamesForFein` hints it keys off the FEIN. Get it
  from step 1, never guess it.
- Coverage is partial and skews older; ~6 of 24 spot-checked entity/year combos returned data, and
  IDOI's own page points to SERFF for electronic filings. **Supplements the IL manual pull, does
  not replace it.**
- Requests are serialised with a delay. It is a small legacy app; do not hammer it.

## Creative-sourcing pass — what else exists (2026-09-18)

Second research pass, scoped to legitimately obtainable channels only. **No CAPTCHA solving, no
Cloudflare bypass, no ignoring robots.txt.** A site whose credibility rests on being a trustworthy
primary source cannot be caught scraping a regulator against its terms; the reputational cost
dwarfs the data. FL (FLOIR CAPTCHA) and LA (LDI Cloudflare) therefore stay closed to us.

**Net result: this pass converted ZERO additional states to automatable.** Manual SERFF pulling
stays the backbone for 35+ of the 40 SERFF-only states. Three things are still worth doing:

**1. Write to Colorado.** DORA has real structured filing data, no login, no CAPTCHA — the only
obstacle is a `robots.txt` DORA itself wrote. That makes it the single best candidate for simply
asking: we are not asking them to build anything, only to export what their own site already shows
a human. Draft letter below.

**2. Mine the FL and LA aggregate reports.** Both states are bot-walled at the filing level but
publish unrestricted statutory reports nobody has mined:
  - **FLOIR Property Insurance Stability Report** — semi-annual PDF at
    `floir.gov/docs-sf/default-source/property-and-casualty/stability-unit-reports/<month>-<year>-isu-report.pdf`
    (note: `floir.com` 302s to `floir.gov`). Carries the 30-day and 180-day AVERAGE RATE REQUEST
    for homeowners plus counts of filings by decrease/0%/increase, back to 2023 — i.e. a citable
    regulator number for "is Florida cooling off", which our 8 FL filings cannot support.
    **Caveat: partially machine-readable only.** The jacket extractor pulls ~53k chars but the
    headline figures live in tables it cannot reach, and there is no poppler in this container for
    a visual read. Treat as a manual read per issue, not a feed.
  - **LA LDI annual report + Louisiana P&C Insurance Commission report to the legislature** —
    confirmed to exist, contents not yet mined.

**3. Send the same letter to FL, LA, NJ, IL, WA, VA, GA.** Expect most to bounce to "just use
SERFF" — when Consumer Reports/ProPublica needed this data they *bought* commercial access rather
than winning it via records request. Treat one conversion as a win, not seven.

### Draft request (from hello@boringrate.com, adapt per state)

> Subject: Bulk/structured export of approved P&C rate filings — independent publisher request
>
> I'm the editor of BoringRate (boringrate.com), an independent insurance-rate research site. We
> maintain a sourced ledger of auto and home rate filings (boringrate.com/rate-filings/) and a
> press page for journalists (boringrate.com/press/) — every figure we publish traces back to the
> underlying regulatory filing.
>
> For [STATE] we currently read each disposition individually via [SERFF Filing Access / your rate
> filing search]. A few states publish this same information as a structured export: Texas
> (data.texas.gov dataset `iubg-btfs`), California (the CDI approval/closed .xlsx), and Illinois
> (the Company Rate Information app).
>
> Does [STATE DOI] have, or could it produce, a similar structured export (CSV/XLSX/API) of
> approved personal auto and homeowners rate filings? We would cite the department as the source
> on every figure, as we already do for filings we pull manually.
>
> Happy to discuss by phone. Thank you for your time.

### Ruled out, with reasons

- **S&P Global (SNL Insurance Product Filings)** and **AM Best (Best's State Rate Filings)** both
  sell exactly this data. Pricing unpublished and **redistribution rights unstated** — licensed
  data is useless to us unless republication on a public site is permitted in writing. Do not
  pursue without that in hand.
- **rateauthority.org** (Rate Authority / PolicyChat) — a CC BY 4.0 API covering 16 states, which
  looks like the shortcut. **Do not use.** Its own methodology says it does not scrape SERFF, yet
  its coverage includes states this survey confirmed are SERFF-only with no alternative portal.
  That contradiction is unresolved from the outside, it is a commercial competitor's byproduct,
  and building on it would mean republishing data whose collection method may be exactly what we
  declined to do ourselves. Our primary-source credibility is the asset; this trades it cheaply.
- **NAIC** — no free filing-level product. Its 2018-2025 homeowners market data call is real but
  NOT public; a consumer-group coalition is petitioning for release. Worth watching, not building
  against.
- **CKAN / ArcGIS / data.gov** federated search — checked, nothing beyond the known TX set. Not
  exhaustive; worth a quarterly recheck since TX and IL were both found under unglamorous titles.
- **Wayback Machine** — legitimate for backfilling a specific historical gap (reading an existing
  archive is not defeating an access control), useless for monitoring since snapshots do not track
  disposition cadence.

### Free and unused: NAIC Consumer Information Source
`content.naic.org` CIS publishes company-level complaint counts and policies-in-force by state and
line, free and unrestricted. Does not answer "did my rate go up", but does answer "does this
carrier draw more complaints than its peers" — adjacent, cheap, currently unused.
