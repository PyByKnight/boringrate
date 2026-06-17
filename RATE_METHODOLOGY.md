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

### The `/ 2` calibration (important)
`stateAvg` (`STATE_DATA[code].avg`) is on the scale of a **published
full-coverage state average** (our national mean ≈ $2,529 vs ValuePenguin's
$2,496 — see §4). The live tool then **halves it**, so displayed per-carrier
prices land ~45–50% of the full-coverage average.

Example (CA, 2026-06-17): `STATE_DATA.avg = 3668`, displayed **median $1,822**,
top carriers $1,431–$1,553 — i.e. roughly half the published CA full-coverage
average (~$2,652).

**Implication:** the displayed defaults read like *minimum / light* coverage,
not full coverage, even though the default coverage tier is "standard"
(`COVERAGE_MULT.standard = 1.00`). This is an internal-consistency decision to
revisit (see §6 action items) — either `stateAvg` should represent the
light-coverage baseline directly (drop the `/2`), or the displayed prices should
be labeled/standardized to the coverage level they actually represent.

> ⚠️ Note: `state_rankings.json` (static, used by the rate-tracker pages) was
> generated with **un-halved** math (`avg × base`-scale), so its prices differ
> from the live tool. Reconcile these to one calibration.

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

### Open action items (carried forward)
- [ ] **Resolve the `/2` calibration** and the `state_rankings.json` mismatch (§1).
- [ ] **Fix CO state average** (clear error) and decide on the other >20% states (§4).
- [ ] **Add `STATE_CARRIER_ADJ` rows for the 9 untuned nationals** (§3), top
      states first, to capture carrier-by-state variation.
- [ ] Source list to standardize on: NAIC (grades), ValuePenguin/Bankrate
      (state avgs), Insurify/MoneyGeek (carrier rankings).

### Canonical sources
- State averages: https://www.valuepenguin.com/car-insurance-by-state
- Cross-check: https://www.bankrate.com/insurance/car/states/ ·
  https://insurify.com/car-insurance/states/
- Complaint ratios / grades: NAIC complaint index (https://content.naic.org)
- Rate-change context (already used): see `rate_changes.json` `_meta`.
