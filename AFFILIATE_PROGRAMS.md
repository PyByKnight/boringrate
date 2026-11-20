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
| USAA | renters | unclear | ~$5/renters quote (reported) | verify |
| GEICO | auto | unclear; reports conflict | — | verify; likely marketplace-only |
| Progressive | auto | no confirmed public program (agency programs only) | — | marketplace-only (MediaAlpha etc.) |
| State Farm, Farmers, Nationwide, regionals | — | none found | — | marketplace or direct deal later |

Not carriers, but possible off-ramp (separate labeled module, NOT in the ranking): The Zebra (Impact, ~$8/quote), Insurify.

Sub-IDs: Impact `subId1..3`, CJ `sid`. Template placeholders `{product} {state} {source}`.
Verify after any change: `node verify_carrier_out.js` (also in rebuild.sh VALIDATE).
