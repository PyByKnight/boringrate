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
- [ ] GA · [ ] SC · [ ] TN · [ ] LA · [ ] FL · [ ] TX · [ ] CA
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
2. **Log a completed filing** into `rate_changes.json` `changes[]`:
   carrier (family name + entity in note), state, pct (TOTAL row, keep 3
   decimals), dir, effective (new-business date), renewal (renewal date),
   affected (vehicle count), source `"XX DOI rate filing TRACKING-# (SERFF)"`,
   url (filingSummary link), note (approval date, per-coverage story — e.g.
   BI vs comp/collision split — and "Count is insured vehicles").
3. **Publish**: `python3 gen_rate_tracker.py` → bump that state's + hub's
   sitemap `<lastmod>` → `node verify_rate.js` (expect 0 errors) → commit
   ("NV tracker: ..." style, one commit per state batch) → push → POST the
   changed URLs to IndexNow (key file in repo root; snippet pattern in
   SESSION_NOTES 2026-07-01d).
4. Update the progress checklist above + SESSION_NOTES.
5. Never invent a figure. If a field is missing, publish without it (affected
   is optional; effective can be "approved <month>" as year-month) rather
   than guess.

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
