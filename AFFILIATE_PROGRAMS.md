# Affiliate / referral programs — roster check (2026-11-20)

Link layer: `js/carrier-out.js` (PARTNERS map). Adding a partner = one entry there; nothing else.
Rule: partnership changes the link only. Never rank order, rate estimate, or filing coverage.
Licensing: pay-per-click / per-quote / per-lead only. No per-sale commission (needs producer license).

Figures below are from third-party affiliate directories, which conflict and go stale.
**Treat them as leads; confirm terms in the network dashboard before adding.**

| Carrier (on our roster) | Tool | Network (reported) | Payout model (reported) | Status |
|---|---|---|---|---|
| Liberty Mutual | auto/home/renters | CJ, also FlexOffers | per quote: auto ~$9–11, home ~$12–14, renters ~$4–5 | apply |
| Allstate | auto/renters | FlexOffers ("National Quoting") | per lead ~$5–28 by line; one listing marked closed | verify open, apply |
| Root Insurance | auto | own page joinroot.com/affiliates | unknown | apply |
| Lemonade | renters | Impact | ~$10/completed quote (+bonus on bind — check it's not sale-contingent) | apply |
| Hippo | (not on home roster) | ShareASale (reported) | ~$25/lead | only if added to roster on merit |
| USAA | all 3 | **CJ** (confirmed 11-20): lead $0–36 + $1 sale | owner accepting (11-20) — see risk stance below |
| GEICO | auto | unclear; reports conflict | — | verify; likely marketplace-only |
| Progressive | auto | no confirmed public program (agency programs only) | — | marketplace-only (MediaAlpha etc.) |
| State Farm, Farmers, Nationwide, regionals | — | none found | — | marketplace or direct deal later |

Not carriers, but possible off-ramp (separate labeled module, NOT in the ranking): The Zebra (Impact, ~$8/quote), Insurify.

Sub-IDs: Impact `subId1..3`, CJ `sid`. Template placeholders `{product} {state} {source}`.
Verify after any change: `node verify_carrier_out.js` (also in rebuild.sh VALIDATE).

## Owner risk stance (2026-11-20)
Pre-revenue sole proprietor: accept boilerplate terms that don't fit our situation (vendor insurance, workers'
comp) when the realistic worst case is program termination. Nothing illegal. The one non-negotiable is
editorial: if a carrier objects to rankings or filing coverage, we drop the PROGRAM, never the content.

## Terms to flag (learned from USAA's CJ terms, 2026-11-20)
Read every program's special terms; flag these to the owner:
- **Approval of any written material that mentions the carrier** (USAA III.B / I.B / I.C(i)) — this would
  hand them a veto over rankings, carrier pages and filing coverage. Incompatible with editorial independence.
- **No "negative light"** clauses — we report rate increases; that's the product.
- **Publisher insurance** (USAA: $1M/$2M CGL, $4M umbrella, $5M/$10M E&O + cyber, workers comp, certificates
  naming them additional insured *before* signing) — accepting = instant breach of a rep & warranty.
- Only their creative/text allowed (our "@ domain.com" label is our own text).

## Status log
- 2026-11-20 CJ publisher account ACTIVE. Applied: USAA (manual review), AAA – Auto Club (check what it
  links to — likely membership sales; territory may not match our CSAA / Auto Club Group rows).
  Not on CJ: Liberty Mutual, Allstate, and the other A–O roster carriers.
- 2026-11-20 FlexOffers registration submitted (review ≤5 business days). Verification: `fo-verify` meta tag
  on index.html — keep it. After approval: apply Liberty Mutual + Allstate (insurance quote program).
- 2026-11-20 Impact: marketplace application DECLINED (likely traffic/site age). Verification tag stays on
  index.html. Workarounds: brand direct-invite link (Lemonade partners page) bypasses the marketplace;
  appeal via Impact support; reapply at higher traffic.
- 2026-11-20 Impact support ticket #927690 opened (asked for decline reason). Decline email gave none.
