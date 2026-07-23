#!/usr/bin/env python3
"""LEVEL check: does each carrier's tool PRICE agree with what its filing implies?

The existing verify_filing_tool_consistency.py checks rate DIRECTION (did a
carrier's filed change agree with its rank). This is the complement: it checks
the price LEVEL. A filing reports written_premium and policyholders, so
written_premium / policyholders is the carrier's real book-average premium —
an independent, primary-source signal for whether the tool's modeled base is
in the right ballpark.

Two things muddy a naive comparison, so the check handles both:
  1. POLICY TERM. Carriers report on different terms — State Farm & MEEMIC file
     6-month, Progressive/Auto-Owners annual — so raw avg is off by 2x for some.
     We don't know term from the data, so we accept a match at EITHER x1 (annual)
     or x2 (6-month): if the filing at either reading lands near the tool price,
     the base is plausible. Only when NEITHER reading matches is it suspect.
  2. COVERAGE MIX. A liability-heavy book averages below a full-coverage book
     regardless of competitiveness, so this is DIRECTIONAL, not exact. Tolerance
     is wide (default 30%) and a flag means "eyeball the base," not "it's wrong."

Read-only. Prints carriers whose filed level disagrees with the tool at both
term readings — the candidates for a base fix (this is how CURE surfaced).
"""
import json, sys
from collections import defaultdict
from verify_filing_tool_consistency import load_model, full_rank

TOL = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30

# Carriers whose BOOK coverage-mix is known to deviate from average, so a
# level flag is EXPECTED (coverage mix), not a base error. Per the insight that
# a no-credit carrier self-selects high-credit min-limits buyers, its book-avg
# reads low even if its standard-full-coverage price is ordinary.
LOW_COVERAGE_BOOK = {"CURE", "Bristol West"}          # min-limits / non-standard -> reads LOW
HIGH_COVERAGE_BOOK = {"Chubb", "PURE", "Amica Mutual"}  # high-value -> reads HIGH


def main():
    model = load_model()
    rows = json.load(open("serff_filings.json"))["filings"]
    # Build each carrier's book as the LATEST-effective filing per DISTINCT entity,
    # then sum across entities. Two guards mirror the rest of the pipeline:
    #  - skip entity_aggregate rows (multi-company blends double-count)
    #  - skip sub-scale entities (<4000 PH): a 434-policy sub-brand at $4,886 is
    #    not the carrier's book (this is what made GA read 2x before the fix).
    # Using latest-per-entity (not summing all filings) avoids counting the same
    # 2M-policy State Farm book three times across its dated revisions.
    MIN_BOOK = 4000
    latest = {}   # (state, carrier, entity) -> (eff, wp, ph)
    for r in rows:
        if r.get("entity_aggregate") or not (r.get("affected") and r.get("written_premium")):
            continue
        if r["affected"] < MIN_BOOK:
            continue
        ent = (r.get("entity") or "").split("(")[0].strip().lower()
        k = (r["state"], r["carrier"], ent)
        eff = r.get("effective_new") or r.get("effective_renewal") or ""
        if k not in latest or eff > latest[k][0]:
            latest[k] = (eff, r["written_premium"], r["affected"])
    book = {}
    for (st, car, ent), (eff, wp, ph) in latest.items():
        cur = book.setdefault((st, car), {"wp": 0.0, "ph": 0})
        cur["wp"] += wp
        cur["ph"] += ph

    flagged = []
    for (st, car), b in sorted(book.items()):
        rank = full_rank(st, *model)
        tp = rank.get(car)
        if not tp:
            continue                       # not in tool roster (regional not modeled here)
        tool_price = tp[1]
        filing_avg = b["wp"] / b["ph"]
        annual = filing_avg
        halfyr = filing_avg * 2
        # best reading = whichever is closer to the tool price
        near_annual = abs(annual - tool_price) / tool_price
        near_6mo = abs(halfyr - tool_price) / tool_price
        best = min(near_annual, near_6mo)
        term = "annual" if near_annual <= near_6mo else "6-month"
        if best > TOL:
            flagged.append((best, st, car, tool_price, filing_avg, term, halfyr if term == "6-month" else annual, tp[0], tp[2]))

    flagged.sort(reverse=True)
    def cause(car, adj, tp):
        if car in LOW_COVERAGE_BOOK:  return "expected: low-coverage book"
        if car in HIGH_COVERAGE_BOOK: return "expected: high-value book"
        return "BASE SUSPECT" if abs(adj-tp)/tp > TOL else ""
    print(f"BASE-vs-FILING level check  |  tolerance {TOL:.0%}  |  {len(flagged)} carriers off at BOTH term readings\n")
    print(f"{'state':<6}{'carrier':<22}{'tool$':>8}{'filing/pol':>11}{'term-adj':>10}{'gap':>7}  rank        note")
    for best, st, car, tp, favg, term, adj, rk, n in flagged:
        print(f"{st:<6}{car:<22}{tp:>8,}{favg:>11,.0f}{adj:>10,.0f}{best:>+6.0%}   #{rk}/{n:<3} {term:<8} {cause(car,adj,tp)}")
    if not flagged:
        print("  none — every carrier's filed level matches the tool at annual or 6-month.")


if __name__ == "__main__":
    main()
