# TN SERFF Backfill — Working Notes (COMPLETE)

**Status:** ✅ DONE (2026-07-03, Opus 4.8). All 18 pulled TN filings parsed → `serff_filings.json`
(34 new entity rows, all TN), rolled up into the TN tracker (`rate_changes.json`, 11 display
entries) and regenerated `article/rate-changes/tennessee.html` via `gen_rate_tracker.py`.

## What was done
- Extraction method that worked: pure-python `serff_pdftext.py` dumps the SERFF **"Company Rate
  Information"** block as label-lines followed by value-lines (Company / Overall % Indicated /
  Overall % Rate Impact / WP Change / Policyholders / WP / Max / Min). Parses cleanly per entity —
  no visual `Read` needed except DNGL (which is "Rate data does NOT apply"; overall from prose).
- One `serff_filings.json` row per entity; multi-entity trackings suffixed `-2/-3/-4`.
- Tracker headline per carrier family = **premium-weighted average** of entity overall %s,
  `affected` = sum. Revenue-neutral (~0%) filings kept in `serff_filings.json` only, excluded
  from the display feed (threshold |wavg| ≥ 0.5%).

## Final TN results (approved overall, premium-weighted family avg)
| Carrier | Tracking | Approved | Indicated | Affected | Notes |
|---|---|---|---|---|---|
| State Farm | SFMA-134611724 | **−10.7%** (F&C −7.0%) | — | 1,309,799 | PV-48953, primary-sourced upgrade |
| State Farm | SFMA-134859733 | **−6.8%** (F&C −8.6%) | — | 1,334,001 | PV-49363, 2nd cut in a year |
| American National | ANPC-134881820 | **+8.0%** | +17.1% | 1,998 | asked +17, got +8 — standout |
| Country Financial | CFPC-134718424 | **−6.0%** | −6.04% | 3,783 | 3 entities |
| Root | CLIN-134910716 | **−5.7%** | −6.3% | 8,010 | |
| Progressive | PRGS-134800104 | **−4.3%** | −7.1/−10.8% | 444,034 | biggest book, −$20M |
| American Family | PRCA-134868307 | **+4.0%** | +5.5% | 3,209 | |
| Shelter | SHEL-134846853 | **−3.4%** | −3.7% | 90,672 | |
| Nationwide | NWPP-G134730628 | **−2.3%** | −4.0% | 25,649 | Mutual book −10% |
| Farmers | FARM-134932086 | **+1.4%** | +6.7% | 32,328 | File & Use |
| Auto-Owners | AOIC-134836495 | **−0.6%** | — | 46,476 | |
| Allstate (ANAIC) | ALSE-134820921 | 0.0% | — | 74,882 | simplified-product intro |
| Amica | AMMA-134682165 | ~0.0% | −3.7% | 4,534 | |
| Erie | ERAP-134830669 | 0.0% | 0.0% | 109,330 | revenue-neutral |
| Safeco (Liberty) | LBPM-134893094 | 0.0% | −13.5% | 20,020 | held flat despite −13.5% indicated |
| Travelers | TRVD-G134842611 | 0.0% | — | 54,156 | Quantum Auto 2.0 |
| USAA | USAA-134934508 | 0.0% | — | ~$390M book | factor/symbol, revenue-neutral |
| Donegal (Atlantic States) | DNGL-134935028 | 0.0% | — | — | annual-policy option, "no rate impact" |

## Content angles captured (in serff_filings.json notes / tracker notes)
- **State Farm:** two TN cuts in a year, ~−17% cumulative on a 1.3M book; ties to the $5B dividend story.
- **American National:** "carrier asked +17%, TN approved +8%" (indicated-vs-approved).
- **Safeco:** "their own numbers said cut 13.5% — they held rates flat" (indicated −13.5%, approved 0%).
- **Progressive:** biggest mover by scale — 444K policyholders, ~−$20M.

## Not done (intentionally deferred — see memory)
- `apply_filed_changes.py` (feed filing %-drift into the rate model) still deferred; coverage gate
  keeps states frozen until top-5 carriers covered. No prose resync needed (rate model unchanged).
- Per-coverage splits (`coverage_changes`) left null — summary blocks don't expose them; would need
  visual reads of each PC-form exhibit. Low priority.

Source zips remain in `/home/knighttyler/*.zip`; re-extract with:
`for z in ~/*.zip; do unzip -o "$z" -d /tmp/tn/"$(basename "${z%.zip}")"; done`
