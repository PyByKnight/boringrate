# SERFF Rate-Filing Pull — Monthly Runbook

Goal: primary-source the rate-change tracker (`rate_changes.json`) from state
filing portals instead of news articles. One search per state per month pulls
**every carrier at once** — you never search carrier-by-carrier. Human-in-the-
loop by design: these portals prohibit bots. ~30–45 min/month for 8–10 states.

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
