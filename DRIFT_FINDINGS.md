# Filing-Drift Engine — Build + First Findings
_2026-07-04 (Opus 4.8). Steps 1 & 2 of BACKFILL_AND_NEXT_STEPS.md._

## Built
- **`anchor_dates.json`** (step 1) — per-state `anchor_as_of`; global default `2026-06-23`
  (the cheapest_by_state.json / calibrate_model.py snapshot). The one missing timestamp.
- **`apply_filed_changes.py`** (step 2 engine) — parses STATE_CARRIER_ADJ + stateAvg from
  index.html, computes premium-weighted `F(s,c)` from filings **effective after the anchor**,
  renormalizes `ADJ' = ADJ × F/F̄`, applies the top-5 coverage gate, emits a proposed patch +
  provenance sidecar. **Never edits index.html** (dry-run default; `--emit` writes the sidecar).
- **`validate_drift.py`** (step 2 harness) — readiness report + backward-test (PENDING a 2nd snapshot).

## Finding 1 — the engine is a correct NO-OP on TN today, and that's the point
TN passes the gate (top-5 covered 3/5), but net drift ≈ 0. Why: **27 of 38 TN filings are
pre-anchor** (effective before 2026-06-23), so the 3rd-party snapshot the model is calibrated to
*already embeds them*. Applying them would double-count — the engine correctly excludes them. Of the
post-anchor filings, 8 are 0% (revenue-neutral) and only 3 are real movers.

**This validates the reset discipline** Fable/the runbook insisted on: right after a fresh
calibration there is almost nothing to drift, because the aggregator already reflects the cuts. The
drift's value **accrues as the anchor ages** (or when we pull a state whose snapshot is stale). It is
insurance against staleness, not a same-day rate mover.

## Finding 2 — the real movers aren't in STATE_CARRIER_ADJ (design decision needed)
The biggest TN filings — Progressive −4.3%, Shelter −3.4%, Country Financial −6.0%, and the
post-anchor American Family +4% / American National +8% — have **no STATE_CARRIER_ADJ entry**, so
`ADJ × F/F̄` has nothing to multiply. Renormalized-drift-on-existing-ADJ only reaches carriers already
given a per-state offset. Options:
  - **(a)** keep drift limited to already-tuned carriers (simple, but misses the movers), or
  - **(b)** initialize a `1.0` ADJ entry for any tracked carrier with filings, then drift it
    (reaches the movers, but is a bigger model change and needs its own sanity bound).
Recommend (b), gated behind the same coverage gate + the ±15% relativity cap. **Not yet decided.**

**Implemented (2026-07-04) as `apply_filed_changes.py --reach-movers`** (off by default, still never
writes index.html). It initializes a 1.0 ADJ entry for tracked carriers that have post-anchor filings
but no offset, then drifts them — proposing NEW entries (e.g. TN: American Family 1.0→1.039,
American National 1.0→1.079).

**Renormalization nuance to know before flipping it on:** F̄(s) is the mean of F only over carriers
that have a **post-anchor** filing. Right after a fresh calibration, the established leaders
(State Farm, GEICO, Progressive…) have *no* post-anchor filing, so they don't participate in F̄ and
don't move — the "ordering shift" only reshuffles the small recently-filed subset. So with the
2026-06-23 anchor, `--reach-movers` nudges only American Family / American National (tiny TN books)
and renormalizes a few 0% carriers by ~0.0007. This is directionally right but low-signal until the
anchor ages; don't read the tiny current deltas as meaningful. Another reason the live payoff waits
on the next snapshot (Finding 3).

## Finding 3 — backward-validation is genuinely blocked on a 2nd snapshot
We hold only the 2026-06-23 reference. The convergence test needs a second dated
NerdWallet/MoneyGeek pull (`cheapest_by_state_next.json`). Until then the harness runs the readiness
report only. This is the one true test of the whole hypothesis, so **capturing the next aggregator
refresh (with its date) is now on the critical path.**

## What the GEICO + TN Farm Bureau pull changes
Both are already in TN's STATE_CARRIER_ADJ (GEICO 0.92, Tennessee Farm Bureau 0.82). If GEICO's
latest approved TN rate filing is effective after 2026-06-23, it becomes the **first roster carrier to
actually drift TN** — and TN Farm Bureau lifts gate coverage toward 5/5. So the pull is what turns the
engine from a validated no-op into a live adjustment on TN.

## Immediate next decisions (for when you're back)
1. Decide Finding 2 (a vs b). Recommend (b).
2. Log the date of the next NerdWallet/MoneyGeek snapshot when it's pulled → unblocks the backward test.
3. After GEICO/Farm Bureau land: re-run `apply_filed_changes.py` → if GEICO is post-anchor, review the
   proposed TN patch, then (separately, deliberately) apply it to index.html via a targeted edit
   (NOT a block replace — see CLAUDE.md).
