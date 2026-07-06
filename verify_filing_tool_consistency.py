#!/usr/bin/env python3
"""Trust guard: does the ZIP tool's per-carrier ranking AGREE with the primary-source
rate filings? A state page that says "State Farm +30%" while the tool ranks State Farm
cheapest is a credibility killer (owner requirement, 2026-07-06).

For each carrier x state we have filings for, compute the COMPOUNDED filed trajectory
(exclude drift_exclude/segment filings) and compare it to the tool's rank/price from
state_rankings.json (top-N cheapest export). Flags:
  RAISED_BUT_CHEAP  — filed net >= +THRESH but sits in the cheapest tier (rank pct < 0.3)
  CUT_BUT_PRICEY    — filed net <= -THRESH but expensive/absent from the cheap tier
These are REVIEW flags (a cheap-base carrier can raise a little and stay cheap), not
auto-fails — eyeball before publishing filing callouts. Read-only; never edits index.html.
Exit 1 if any hard contradiction (raised >= HARD and top-3 cheapest, or cut >= HARD and absent)."""
import json, sys
from collections import defaultdict
from functools import reduce

THRESH = 5.0   # % net move to be "material" for the check
HARD   = 10.0  # % net move that makes a contradiction a hard fail

def eff(r): return r.get("effective_new") or r.get("effective_renewal") or r.get("disposition_date") or ""

def main():
    sf = json.load(open("serff_filings.json"))["filings"]
    sr = json.load(open("state_rankings.json"))
    # compounded filed trajectory per (state, carrier), excluding segment-only filings
    fil = defaultdict(list)
    for r in sf:
        if r.get("overall_pct") is None or r.get("drift_exclude"):
            continue
        fil[(r["state"], r["carrier"])].append(r)
    hard = 0
    for st in sorted({s for s, _ in fil}):
        d = sr.get(st)
        if not d:
            continue
        top = d["top"]; n = len(top)
        rankmap = {c["name"]: (i + 1, c["price"]) for i, c in enumerate(top)}
        lines = []
        for (s, car), rs in fil.items():
            if s != st:
                continue
            net = (reduce(lambda a, r: a * (1 + r["overall_pct"] / 100.0), rs, 1.0) - 1) * 100
            rk = rankmap.get(car)
            flag = ""
            if abs(net) >= THRESH:
                if rk:
                    pr = rk[0] / n
                    if net >= THRESH and pr < 0.30:
                        flag = "  ⚠ RAISED_BUT_CHEAP"
                        if net >= HARD and rk[0] <= 3: flag += " [HARD]"; hard += 1
                    elif net <= -THRESH and pr >= 0.70:
                        flag = "  ⚠ CUT_BUT_PRICEY"
                else:  # cut hard but not even in the cheapest-N export
                    if net <= -THRESH:
                        flag = "  ⚠ CUT_BUT_ABSENT (not in top-%d cheapest)" % n
                        if net <= -HARD: flag += " [HARD]"; hard += 1
            pos = "#%d/%d $%d" % (rk[0], n, rk[1]) if rk else "absent from top-%d" % n
            lines.append((net, "  %-22s filed net %+6.1f%%   tool %s%s" % (car, net, pos, flag)))
        if lines:
            print("== %s (%s) — tool avg $%d ==" % (st, d["name"], d["avg"]))
            for _, ln in sorted(lines):
                print(ln)
            print()
    print("HARD contradictions: %d" % hard)
    return 1 if hard else 0

if __name__ == "__main__":
    sys.exit(main())
