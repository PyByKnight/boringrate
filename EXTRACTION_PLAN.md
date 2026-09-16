# Filing Text Extraction — What We Keep, Why, and How to Revisit It

_Created 2026-09-16. Companion to `SERFF_RUNBOOK.md`, `MODIFIERS_PLAN.md`, `serff_filings.json`._

## The problem this solves

`serff_filings.json` answers exactly one question: **"did my rate go up?"** Everything else a SERFF
jacket contains — why the carrier did it, what the regulator said back, which discounts changed, what
got removed — was being read once during triage and then thrown away. We compacted the PDFs
(`serff_compact.py`) and kept the text, but 15 MB of raw jacket text is not queryable and not
revisitable in practice.

**The filings work is the best-performing content on the site** (tracker pages average GSC position
8.2 / 1.05% CTR, vs. position 60-74 and ~0% for the programmatic state/metro pages). So the return on
extracting *more* per filing is high, and it costs no additional portal pulling — it all runs against
text already on disk.

## The three-layer store

| layer | file | size | what it is |
|---|---|---|---|
| raw | `_serff/*_txt/*.txt` | 15.1 MB | full jacket text, gitignored, source of truth |
| **digest** | `filing_digests.json.gz` | **0.60 MB** | distilled narrative, **committed to git** |
| derived | `rate_modifiers.json` | 28 KB | structured discount/surcharge rows |

**25x compression, and the digest is the layer you actually query.** Raw text stays on disk for
re-mining with better extractors later; the digest is small enough to commit, so filing narrative is
now version-controlled and survives a `_serff/` wipe (which is a live risk — `_serff/` is gitignored).

### What the digest keeps (`mine_filing_text.py`)

Four narrative sections, because each answers something the ledger's percentage cannot:

- **Filing Description** (469 of 486 filings) — the carrier explaining its own change, in plain
  English. This is where discount changes, new coverage options, and competitive intent are stated.
- **Objection Letters** (695) — the state DOI pushing back on the carrier. *Regulators challenging
  insurers is editorial material effectively nobody else publishes.* Example: Virginia forced
  Allstate to apply the Defensive Driver Discount to **each** qualifying driver rather than once per
  vehicle, citing §38.2-2217 (`ALSE-134699857`).
- **Response Letters** (689) — what the carrier conceded, and what it refused.
- **Filing Notes** — informal reviewer/filer exchanges.

Dropped: the 8-line identity header and "PDF Pipeline … Generated" footer SERFF stamps on *every*
page, plus schedule tables that restate the same rows. That boilerplate is most of the 15 MB.

Every digest is keyed by SERFF tracking number and joined to state/carrier/line/overall_pct from the
ledgers, so any quote is citable straight back to the filing. **102 digests are from jackets we pulled
but triaged out of the ledgers** — they carry `in_ledger: false`, keep their narrative, and are
identity-resolved from the jacket text itself. Those were previously pure waste.

## Seeing change over time

The digest is keyed per filing, and each filing carries `disposition_date`. That makes two things
queryable that weren't before:

1. **A carrier's posture across states** — group by `(carrier, program)` and look at the state set.
   This already surfaced that **USAA raised its Participation in Safe Driving telematics discount to
   15% in five states** (LA, MI, OH, PA, VA), and that **Shelter** overhauled Loyalty / Evidence of
   Continuous Insurance / Prior Coverage / Tenure across IL, LA, OH.
2. **A carrier's posture over time in one state** — successive filings for the same book, ordered by
   disposition date. This is the "cumulative increase" angle in `MODIFIERS_PLAN.md` tier 3.

Re-running `mine_filing_text.py` after each pull is idempotent and rebuilds the whole store, so the
committed digest doubles as a dated snapshot in git history.

## Derived: discounts (`mine_discounts.py`)

Sentence-level extraction of discount/surcharge changes → `rate_modifiers.json` (the scaffold that had
been empty since `MODIFIERS_PLAN.md` was written). 55 statements from 38 filings / 27 carriers.

**★ The category that matters most: 11 rows are discount REMOVALS.** A carrier can hold its filed rate
flat and still raise your bill by deleting a discount you were getting — and the headline `overall_pct`
hides that completely. This is the only place in the pipeline that catches it.

Article-ready findings already sitting in the output:
- **Donegal doubled its Multi-Car discount 10% → 20% in Michigan** — and the DOI made them extend it
  to renewal policies, not just new business (`DNGL`, MI).
- **Progressive cut its Kia/Hyundai COMP surcharge to 40%** in PA, and regulators required the
  surcharge factors to expire 11/13/2026. The Kia/Hyundai theft crisis is a high-demand consumer topic.
- **Nationwide's new-vehicle discount phases out over five years** with large initial discounts that
  vary by coverage — i.e. a quiet annual increase built into the product.

Caveat recorded in the file's `_meta`: these are values **as stated** by the carrier or regulator in
prose, not computed from the rate manual. Treat them as citable quotes, not as verified factors.

## Running it

```
python3 mine_filing_text.py            # rebuild digest store (after every pull)
python3 mine_filing_text.py --stats    # report only, write nothing
python3 mine_discounts.py              # rebuild rate_modifiers.json
python3 mine_discounts.py --report     # print findings incl. removals, write nothing
```

Order matters: `mine_discounts.py` reads the digest, so refresh the digest first.

## Not yet mined — ranked by expected value

Signal counts below are files-containing-the-term across the current 500-jacket corpus, so they are an
upper bound on yield, not a promise.

1. **Territory / ZIP-level dispersion** (101 files) — several carriers file per-territory rate impact
   exhibits. `gen_home_metro_offsets.py` currently models sub-state offsets with **no filing data at
   all**; this would make metro pages primary-sourced. Highest value, hardest parse (tables).
2. **Tier / credit factors** (85 files) — feeds the credit-score article, which is an existing page.
3. **Deductible options** (78 files) — new deductible tiers being introduced (e.g. USAA adding $750 /
   $1500 / $2000 / $2500) map to a real shopper decision.
4. **Capping / transition rules** (68 files) — "your increase is capped at X% this term" is directly
   reassuring to the reactive shopper the site targets.
5. **Per-coverage splits** (BI/PD/COMP/COLL, 45-62 files) — `coverage_changes` exists in the ledger
   schema and is mostly null. CURE's NJ filing, for instance, states BI +8% / UM-UIM +30% separately.

## Rules

- **Never** derive a price level from a jacket's `written_premium / affected` — it is line-blended
  across HO/condo/tenant/mobile. See `boringrate-jacket-averages-blended` and `VA_HOME_SERFF_WORKING.md`.
- Quote regulators and carriers verbatim where a claim is contestable; always cite the tracking number.
- The digest is derived data. Never hand-edit it — fix the extractor and rebuild.
