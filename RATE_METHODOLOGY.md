# BoringRate — Auto Rate Methodology & Verification

_Maintained for repeatability. Last full review: 2026-06-17 (Opus 4.8)._

This documents **how the auto rate model works**, **where every number comes
from**, **what is sourceable vs modeled**, and **the repeatable process** for
re-verifying all of it. The machine-readable companion is `rate_audit.json`
(the ledger) driven by `audit_rates.py` (the auditor).

> **Integrity SLA:** every rate atom is re-verified at least once every 30 days.
> Run `python3 audit_rates.py` — it exits non-zero if anything is stale, drifted,
> or untracked.

---

## 1. The formula

From `index.html` → `estimatePremium(carrier, avg)`:

```
premium = round( (stateAvg / 2)
                 × carrier.base
                 × STATE_CARRIER_ADJ[state][carrier]      (default 1.0)
                 × METRO_CARRIER_ADJ[metro][carrier]       (default 1.0)
                 × Π(1 + sensitivities)                    (driver profile)
                 × COVERAGE_MULT[carrier][tier]
                 × SHOP_MULT[carrier][channel] )
```

Ranking = sort all active carriers for the ZIP by `premium`; the "median" line
is the median of the top 10.

### Per-vehicle calibration — RESOLVED 2026-06-17
`stateAvg` (`STATE_DATA[code].avg`) is the **published full-coverage, per-vehicle
state average** (national mean ≈ $2,529 vs ValuePenguin's $2,496 — see §4). The
tool returns `round(avg × m)` — **the legacy `/2` was removed** so every premium
on the site is on one consistent per-vehicle basis.

Now consistent (all `avg × base × …`, no halving): the auto rate tool
(`index.html`), the renters/home tools, `state_rankings.json` (regenerated via
`node gen_state_rankings.js --export`), the per-state/metro article tables
(`--states` / `--metros`), the rate-change pages (`gen_rate_tracker.py`), the
interactive `article/state-rankings.html` (STATES array + embedded `rates` +
`MAX_PRICE`), and `coverage.html`'s `STATE_DATA`.

Sanity (CA, post-fix): `STATE_DATA.avg = 2652`, tool median **$2,628** — lands on
the published CA full-coverage average, as it should.

> If any state average changes, re-run `node gen_state_rankings.js --export
> --states --metros` then `python3 gen_rate_tracker.py`, and sync the
> `STATE_DATA` copies in `coverage.html` and `article/state-rankings.html`.

---

## 2. The layers — sourceable vs modeled

| Layer | What it is | Source type |
|---|---|---|
| `STATE_DATA[code].avg` | Per-state average annual premium (carrier-independent anchor) | **Sourceable** — NAIC / ValuePenguin / Bankrate / Insurify |
| carrier **CS grade** + NAIC complaint ratio | Service quality shown next to each carrier | **Sourceable** — NAIC complaint index |
| `carrier.base` | Each carrier's price **relative to the market** (e.g. USAA 0.82) | **Modeled** — calibrated from published "cheapest companies" rankings; no single citation |
| `STATE_CARRIER_ADJ[state][carrier]` | Per-state carrier tilt (home-turf pricing) | **Modeled**, sparse (see §3) |
| `METRO_CARRIER_ADJ[metro][carrier]` | Per-metro carrier tilt (urban/rural) | **Modeled** |
| `carrier.sens` | Driver-profile factors (age, credit, accident, telematics, own/rent, multi-car, lapse/renewal) | **Modeled** to mirror standard industry rating factors |
| `COVERAGE_MULT` / `SHOP_MULT` | Coverage tier + buy-channel multipliers | **Modeled** |

**Bottom line:** the only carrier-independent, citation-backed number is the
state average; CS grades map to NAIC complaint data; **everything
carrier-specific is a modeled relative multiplier.** "Verifying" a modeled atom
means confirming its *relative ordering* still matches current research (e.g.
USAA/GEICO still cheap, Liberty Mutual still high), not matching a single URL.

Regional carriers (`LOCAL_CARRIER_DEFS`) carry a **state-appropriate base for
their footprint** ("Bases are already state-appropriate — no STATE_CARRIER_ADJ
applied"), so they are effectively state-specific by construction. The
national-base-everywhere problem in §3 applies to the 14 **national** carriers.

---

## 3. Are we capturing carrier-by-state variation? (the known gap)

State-level *cost* is fully captured (every carrier scales with `STATE_DATA.avg`).
Carrier-specific *state competitiveness* is **not** — it only exists where
`STATE_CARRIER_ADJ` has an entry.

As of 2026-06-17 (`python3 audit_rates.py --coverage`):

- **714 national carrier × state cells** (14 nationals × 51 states)
- **157 (22%) have a documented state offset; 557 (78%) inherit the pure national base**
- Only 5 nationals are state-tuned at all:
  - USAA 51/51 · GEICO 48/51 · State Farm 36/51 · Progressive 17/51 · Farmers 5/51
- **9 nationals have ZERO state offsets** (identical relative price in every state):
  Allstate, Liberty Mutual, Nationwide, Travelers, Safeco, The Hartford, Root,
  Kemper, National General.

Real carriers swing their *relative* position a lot by state (a carrier can be
cheapest in one state, mid-pack in another). We capture that for ~a fifth of
cells. Closing this = adding `STATE_CARRIER_ADJ` rows for the 9 untuned
nationals, prioritized by population/traffic. (See §6.)

Every documented offset is tracked in the ledger as `offset/<state>/<carrier>`.

### Closing the gap (2026-06-17) — modeled cost-responsiveness tilt
The 9 untuned nationals now get a per-state offset from a transparent, documented
model (manual offsets for USAA/GEICO/State Farm/Progressive/Farmers are left
intact). For each state:

```
offset = round( 1 + k × (2 × costPercentile − 1), 2 )     # dropped if it rounds to 1.00
costPercentile = rank of the state's corrected STATE_DATA.avg, 0 (cheapest) … 1 (priciest)
```

`k` is the carrier's relative-price slope vs. state cost — **agent/traditional
carriers load high-cost states (k > 0); direct/value carriers hold the line
(k < 0)**, per the evidence in §0 sources (Allstate most expensive major;
Travelers cheapest large national; Nationwide competitive):

| Carrier | k | Carrier | k |
|---|---|---|---|
| Allstate | +0.10 | Nationwide | −0.05 |
| Liberty Mutual | +0.09 | Travelers | −0.07 |
| The Hartford | +0.05 | Root Insurance | −0.05 |
| Safeco | +0.04 | National General | +0.06 |
| Kemper | +0.05 | | |

Result: offset coverage rose from 22% → **80.5%** of national cells (575/714).
These are **modeled/directional** (same status as the existing manual offsets),
not citation-exact; verify by confirming the high-cost/low-cost ordering still
holds against carrier-by-state research. Mid-cost states intentionally carry no
offset (tilt ≈ neutral). Still partial and improvable later: State Farm (36/51),
Progressive (17/51), Farmers (5/51).

---

## 4. State-average verification — 2026-06-17 pass

**Canonical source:** ValuePenguin, "Car Insurance Rates by State", full-coverage
annual, published 2026-06-16 (national avg $2,496).
URL: https://www.valuepenguin.com/car-insurance-by-state

National mean: ours **$2,529** vs source **$2,496** (within 1.3% — good).
State distribution: **21/51 within 10%**, 19 within 10–20%, **11 off by >20%.**

States needing a decision (>20% divergence; ours → source):

| State | Ours | Source | Δ | Note |
|---|---|---|---|---|
| MI | 4724 | 3120 | +51% | MI is volatile across sources (no-fault); cross-check before changing |
| CO | 1706 | 3264 | **−48%** | **Almost certainly wrong** — CO is expensive, not cheap |
| GA | 3224 | 2208 | +46% | |
| CA | 3668 | 2652 | +38% | |
| MA | 2842 | 2172 | +31% | |
| FL | 4848 | 3732 | +30% | FL genuinely high, but we overstate |
| NY | 3484 | 2712 | +28% | |
| WY | 1986 | 1572 | +26% | |
| IA | 1586 | 2040 | −22% | |
| KS | 2124 | 2700 | −21% | |
| HI | 1446 | 1812 | −20% | |

Full per-state comparison: `audit_rates.py` ledger (`state_avg/*` atoms carry
`reference` + `source`). Aggregators disagree on some states (esp. MI), so
cross-check a second source before overwriting; **CO is a clear fix regardless.**

> Decision pending: whether to overwrite `STATE_DATA.avg` to source values.
> This changes every displayed price site-wide and interacts with the `/2`
> calibration (§1), so it is intentionally **not** auto-applied.

---

## 5. The ledger & auditor (`rate_audit.json` / `audit_rates.py`)

293 tracked atoms: 14 national + 8 nonstandard + 63 regional carrier defs,
51 state averages, 157 documented state offsets. Each stores a value
**snapshot**; if `index.html` later differs, the atom is flagged **DRIFTED**
(forces a fresh source check). Atoms past the 30-day SLA are **STALE**.

```
python3 audit_rates.py                 # check; exit 1 if anything needs attention (cron/CI)
python3 audit_rates.py --coverage      # carrier × state offset coverage report (§3)
python3 audit_rates.py --due 7         # what falls due in the next 7 days
python3 audit_rates.py --sync          # add/remove atoms after a roster change
python3 audit_rates.py --mark <id> --source <url> --note "..."   # record a verification
python3 audit_rates.py --mark-all --source <url>                 # after a full pass
```

Atom id scheme: `carrier/<national|nonstandard|regional>/<Name>`,
`state_avg/<XX>`, `offset/<XX>/<Carrier>`.

---

## 6. Repeatable monthly process

1. `python3 audit_rates.py` → see what's stale/drifted.
2. **State averages** (sourceable): refresh from the canonical source (§4).
   Compare with `audit_rates.py` ledger references; decide keep/update per the
   >10% list; then `--mark state_avg/<XX> --source <url>`.
3. **CS grades / complaint ratios** (sourceable): re-check against NAIC complaint
   index; `--mark carrier/.../<Name> --source <naic-url>`.
4. **Modeled atoms** (bases, offsets, sens): confirm relative ordering still
   matches current "cheapest companies" research (NerdWallet / Bankrate /
   Insurify / MoneyGeek). Directional, not citation-exact; `--mark` with the
   research URL used.
5. Commit ledger + this doc.

### Open action items
- [x] **Resolved the `/2` calibration** + reconciled all per-vehicle displays (§1). _2026-06-17_
- [x] **Fixed CO + the 11 states >20% off** vs source (§4). _2026-06-17_
- [x] **Added `STATE_CARRIER_ADJ` for the 9 untuned nationals** → 80.5% coverage (§3). _2026-06-17_
- [ ] Deepen partial offsets: State Farm (36/51), Progressive (17/51), Farmers (5/51).
- [ ] Decide on the 10–20% state-average divergences (left as-is for now, §4).
- [ ] **Verify CS grades vs NAIC complaint index** (next sourceable batch).
- [ ] Apply the same per-vehicle + carrier-by-state passes to renters/home.
- [ ] Source list to standardize on: NAIC (grades), ValuePenguin/Bankrate
      (state avgs), Insurify/MoneyGeek (carrier rankings).

### Canonical sources
- State averages: https://www.valuepenguin.com/car-insurance-by-state
- Cross-check: https://www.bankrate.com/insurance/car/states/ ·
  https://insurify.com/car-insurance/states/
- Complaint ratios / grades: NAIC complaint index (https://content.naic.org)
- Rate-change context (already used): see `rate_changes.json` `_meta`.
