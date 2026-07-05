# BoringRate — Data Organization, Backfill Advice & Next Steps
_Briefing written 2026-07-03 (Opus 4.8), while owner was away. Grounded in the actual files._

## 1. Where the pulled data stands (organized)

### Primary source — `serff_filings.json` (54 entity rows)
| State | Entity rows | Distinct carriers | Top-10 carriers covered | Gate status |
|---|---|---|---|---|
| **TN** | 38 | 17 | **9/10** (only GEICO missing) | ✅ effectively gate-ready |
| GA | 7 | 7 | 5/10 | ◻ half |
| SC | 6 | 6 | 3/10 | ◻ thin |
| NV | 3 | 2 | 2/10 (Allstate + Safeco) | ✗ negligible |

### Display feed — `rate_changes.json` (49 tracker entries → generates `article/rate-changes/*.html`)
NV 11, TN 11, GA 8, FL 6, SC 6, LA 5, CA 1, TX 1.
- TN/GA/SC entries are now **primary-sourced** (SERFF tracking #s).
- **FL, LA, CA, TX, and most of NV** are from press / DOI reports (3rd-party) — tracker content
  exists but has **no `serff_filings.json` backing**. Fine for the tracker; not usable for drift.

### Supporting stores
- `expansion_candidates.json` — non-roster carriers seen filing real changes (American National is
  the strongest; TN added Elephant, Tesla, Grange, Stillwater, Celina).
- `rate_modifiers.json` — **new, empty scaffold** for opportunistic per-carrier modifiers (see
  `MODIFIERS_PLAN.md`).
- Source zips for all pulls remain in `/home/knighttyler/*.zip` (durable).

## 2. Backfill advice — ranked by ROI (coverage-gate logic)

The drift model can only turn on for a state once its **top-5 carriers are covered** (renormalized
drift shifts ordering, not level — so partial coverage = biased ordering). Backfill toward closing
top-5 gaps, not toward volume.

1. **TN — finish 2 filings, then it's the pilot. (Highest ROI by far.)**
   Missing only **GEICO** (top-10) and **Tennessee Farm Bureau** (TN's #2 by share, and it carries a
   0.82 home-turf offset in the model, so its ordering matters). Two pulls and TN clears the gate →
   first state to wire `apply_filed_changes.py`. **Do this first.**

2. **GA — needs the majors before it's gate-ready. (Medium lift.)**
   Missing **State Farm, GEICO, USAA, Farmers, Nationwide** (+ Georgia Farm Bureau regionally). GA
   already has 8 tracker entries, so backfilling these upgrades an existing content page *and* moves
   GA toward the gate. Good second target.

3. **SC — 7 of top-10 missing. (Bigger lift.)**
   Missing GEICO, Progressive, USAA, Liberty/Safeco, Farmers, Nationwide, Travelers. Worth it only
   after TN + GA; SC has Southern Farm Bureau + American National already (good regional spine).

4. **NV — deprioritize primary pulls.**
   Only 2 carriers, and the Las Vegas Review-Journal DOI report already gives NV 11 tracker entries.
   Not worth SERFF effort until the higher-value states are done. Its content page is fine as-is.

**Also capture opportunistically on every pull (cheap, high-value):**
- `premium_as_of` valuation date (the PC-form "@ MM/DD/YYYY" header) — skipped in the TN pass.
- Any UX-aligned **rate modifier** exposed (homeowner/young-driver/multi-car discounts) → `rate_modifiers.json`.
- Per-coverage % splits (BI/PD/COMP/COLL) when the filing breaks them out — good content, and future coverage-level drift.

## 3. Next steps (in order)

**A. Before drift can ship (small, do first):**
1. Pull **GEICO + TN Farm Bureau** TN auto filings → append to `serff_filings.json` (same "Company
   Rate Information" block method documented in `TN_SERFF_WORKING.md` — no visual reads needed).
2. Add a per-state **`anchor_as_of`** field (date of the NerdWallet/MoneyGeek snapshot each state was
   calibrated to). Without it, "apply only filings effective after the anchor" is undefined and the
   double-count guard is guesswork. This is the one missing timestamp (it's on the *anchor* side, not
   the filing side — `premium_as_of` barely matters).

**B. The pilot (the day that tests the whole thesis):**
3. Build **`apply_filed_changes.py`** exactly per `SERFF_RUNBOOK.md`: F per carrier family with
   premium-weighted entities → renormalize drift to state mean → cap (±15%/snapshot; shrink single
   |pct|>15% toward mean) → coverage gate → emit a `STATE_CARRIER_ADJ` patch **plus a provenance
   sidecar keyed by tracking #** so every adjusted rate traces to filing + date.
4. Run the **backward-validation harness** on the NV/GA/SC filings already held: did filing-driven
   drift move each state's carrier ordering *toward* the next published 3rd-party ordering? If yes,
   the hypothesis holds; if a state diverges, freeze its drift and investigate. **This costs ~a day
   and validates the entire primary-source direction before more pulls.**

**C. Deferred (documented, not now):**
- Per-carrier `P` from `rate_modifiers.json` (gated — see `MODIFIERS_PLAN.md`).
- Bottom-up rate-manual parsing — **do not build** (tar pit: top carriers file jacket-only; where
  manuals exist they need proprietary tier/score inputs not in the filing).
- Shift `audit_rates.py` re-verify cadence toward filings (freshness) with 3rd-party checks quarterly,
  so the aggregators don't quietly re-become the source of truth.

## 4. Content produced this session
- `article/rate-changes/tennessee.html` regenerated from the primary-sourced TN data (3 raised, 8 cut).
- `article/tennessee-rates-dropping.html` — new standalone editorial piece (see it for the TN story:
  State Farm's two cuts, Progressive's −$20M, the indicated-vs-approved angle). Sourced to SERFF
  tracking #s throughout. **Not yet linked from global nav** — to surface it, add a "Tennessee
  Rates — 2026" entry in `partials/nav-mega.html` (beside the Florida one) and run `build_nav.py`
  (single-source nav; don't hand-edit per page). Also worth a cross-link from
  `article/florida-rates-dropping.html`'s related section.

## Open content ideas (GSC-demand-driven, primary-sourced — for when you're back)
- "Carriers asked Tennessee for double-digit hikes and got trimmed" — the indicated-vs-approved angle
  (American National +17.1%→+8.0%; Safeco −13.5% indicated→held flat). **Nobody else has this data.**
- Refresh `article/market-share.html` / `article/florida-rates-dropping.html` cross-links to the new
  TN piece once GEICO/Farm Bureau land.
