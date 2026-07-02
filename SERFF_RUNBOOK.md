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
- [ ] SC · [ ] TN · [ ] LA · [ ] FL · [ ] TX · [ ] CA
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
