# Rate Modifiers — Opportunistic Extraction Plan

_Created 2026-07-03 (Opus 4.8). Companion to `SERFF_RUNBOOK.md` and `serff_filings.json`._

## Goal
Build a **per-carrier, dated, sourced** store of the rating modifiers that line up with the tool's
UX personalization inputs, so `P(profile, coverage)` (the sensitivity term) can eventually be
**per-carrier** instead of one generic curve — and, before that, so filed modifiers act as a
**check/prior** on the generic curve.

**Discipline: opportunistic, NOT exhaustive.** Grab a modifier when a filing already exposes it in
the same triage pass that populates `serff_filings.json`. Never open a separate hunt for them, never
parse a 260-page manual for them. Missing is fine; wrong or half-applied is not.

## Why this is a "grab it when you see it," not a project (per Fable's earlier read)
- The carriers that lead the comparison (State Farm, Progressive, USAA, Allstate, Shelter) file
  **jacket-only** — no manual, no factor pages. So per-carrier modifier coverage will always be
  **sparse and lopsided**.
- A **half-populated per-carrier P is worse than a consistent generic P** when the user is directly
  comparing carriers side by side: giving Carrier A a real homeowner discount and Carrier B the
  generic one manufactures a false ranking difference. So the store fills quietly and does **not**
  drive P until a factor clears a coverage gate (below).

## UX factors → modifier targets
Map only to what the UX actually asks. Current personalization inputs:

| UX input | Model sensitivity (target of per-carrier data) | Filed modifier name(s) to capture |
|---|---|---|
| Young/teen driver | `youngDriver` (state-keyed today, generic across carriers) | Youthful/inexperienced operator surcharge; age-band relativities |
| Driver age | age-band curve | Age/gender/marital relativity table |
| Homeowner | homeowner discount multiplier | Homeownership / package discount |
| Multi-car / multi-policy | multi-car, multi-policy discount | Multi-car, multi-line/bundling discount |
| Good student | good-student discount | Good-student / distant-student discount |
| (implicit) credit | credit tier factor | Insurance-score / financial-stability tier factors (often proprietary — usually NOT exposed) |
| (implicit) prior coverage | prior-coverage/continuity factor | Prior-insurance / continuity-of-coverage discount |

Coverage tier stays modeled (not a per-carrier modifier target).

## Where these show up in a filing (capture priority)
1. **Rule pages / Manual pages** (`Rate-Rule Attachments/`) — cleanest when present (discount % or
   factor stated). Rare for top carriers.
2. **Supporting Document Attachments** — sometimes a "Rate Level Effect by Discount" or a
   "Summary of Rate Revisions" exhibit lists discount factors.
3. **Filing Description prose** — occasionally states a changed discount ("increasing the
   homeowner discount from 5% to 7%"). Capture both old and new when the filing shows a change.

If none of the above expose a UX-relevant modifier: record nothing. Do not infer.

## Minimal schema — new file `rate_modifiers.json` (sits beside serff_filings.json)
One row per (carrier entity, factor, state, effective_date). Keep it flat and dated.

```json
{
  "_meta": {
    "purpose": "Opportunistic per-carrier rating modifiers aligned to the tool's UX inputs. Dated + primary-sourced. Feeds a FUTURE per-carrier P(profile) term; until a factor clears the coverage gate it is a CHECK on the generic curve, not a driver.",
    "gate": "Do NOT make P per-carrier for a factor until that factor is captured for >= the top-N carriers a user actually compares in a state (mirrors the drift coverage gate). Below the gate: use as sanity-check/prior only.",
    "schema": {
      "state": "2-letter",
      "carrier": "family name",
      "entity": "exact filing company | null (family-level)",
      "factor": "ux slug: young_driver | age_band | homeowner | multi_car | multi_policy | good_student | prior_coverage | credit_tier",
      "value": "number or object — discount as signed % (e.g. -0.07) OR a relativity table {band: factor}",
      "value_kind": "discount_pct | surcharge_pct | relativity_table | factor",
      "prior_value": "same shape as value, if the filing shows a CHANGE | null",
      "tracking": "SERFF tracking # (join key to serff_filings.json)",
      "url": "filingSummary deep link",
      "effective_date": "YYYY-MM-DD (effective_new of the filing)",
      "source_doc": "which PDF/section it came from (e.g. 'Rate-Rule: Rule 12 Homeowner Discount')",
      "recorded_date": "YYYY-MM-DD we logged it",
      "confidence": "stated | derived | inferred-from-prose"
    }
  },
  "modifiers": []
}
```

## Workflow (folds into existing SERFF triage — no new pass)
1. While parsing a state's filings for `serff_filings.json`, if a filing's rule/manual/supporting
   pages or prose expose a UX-relevant modifier, append a `rate_modifiers.json` row keyed by the
   same `tracking` #.
2. Capture the **value and the prior_value when the filing shows a change** (change data is the
   high-value part — same primary-source-owns-the-derivative logic as the drift design).
3. Guard on (tracking, factor, entity) to avoid dupes.
4. Do **not** touch `index.html` / P. Consumption is deferred.

## Consumption — deferred, gated
- Build **after** `apply_filed_changes.py` (the drift-on-ordering step) ships and validates.
- Then, per factor, only flip P to per-carrier where the **coverage gate** is met for the compared
  set; elsewhere keep the generic curve. Use captured-but-below-gate modifiers to **audit** the
  generic curve (flag when a real filed discount diverges hard from the generic assumption).
- Same provenance discipline as rates: any per-carrier modifier shown/used must trace to
  `tracking` + `effective_date`.

## Status
Store schema defined; `rate_modifiers.json` scaffold created (empty). **Nothing captured yet** —
begin populating on the next state triage (and backfill from the TN zips in `/home/knighttyler/*.zip`
opportunistically if cheap). Not urgent, not exhaustive.

> Note: a follow-up Fable consult on this exact question was cut off by a session limit on 2026-07-03;
> this plan reflects the architecture Fable already laid out (P as the modeled term; sparse per-carrier
> data as a gated check, not a driver). Re-consult when convenient to pressure-test the gate threshold.

## Scan log
- **2026-07-04** — scanned every extracted TN rate-rule/supporting attachment in `/tmp/tn/*` for
  text-exposed UX modifiers.
  - ✅ **GEICO homeowner discount** (Exhibit 5, GECC-134888920, GEICO Marine GB) — clean per-coverage
    factor table by Prior BI Tier; captured (value + prior_value). The only clean per-factor values found.
  - ⚠️ **Root** (`CLIN-134910716/TN RFD.pdf`) — uses homeowner, prior-insurance, safe-driver,
    paid-in-full, accident-free factors, but values come out as **undelimited concatenated tables**
    (e.g. `married1n2.62603.2292…`) with no column headers — not safely parseable; would mis-assign.
    Left uncaptured (discipline: don't record guessed values).
  - ⚠️ **GEICO priv rules** (`TN-GB/GI-priv-2026-099.pdf`) — names the full discount menu (good-student,
    homeownership, multi-line, defensive-driver, senior 55+, paid-in-full, early-shopper) but states the
    numeric factors live "in the Rate Pages" (image tables). Menu is qualitative only; not captured as values.
  - Conclusion: clean modifier values need a purpose-built exhibit (like GEICO's Exhibit 5) or a
    text-parseable rate page. Manuals with image/undelimited factors are the tar pit Fable flagged —
    skip unless a visual read is specifically worth it for one carrier/factor.
