#!/usr/bin/env python3
"""Trust guard: does the ZIP tool's per-carrier ranking AGREE with the primary-source
rate filings? A state page that says "State Farm +30%" while the tool ranks State Farm
cheapest is a credibility killer (owner requirement, 2026-07-06).

Evaluates the TRUE full tool roster (nationals CARRIERS_STANDARD + per-state regionals
from STATE_LOCAL_CARRIERS/LOCAL_CARRIER_DEFS), price = avg × base × STATE_CARRIER_ADJ —
the same base-profile the static pages use. NOTE: state_rankings.json is nationals-only,
so do NOT use it here. For each carrier×state we have filings for, compare the COMPOUNDED
filed trajectory (excludes drift_exclude) to its rank in the full roster. Flags:
  RAISED_BUT_CHEAP — filed net >= +THRESH but in the cheapest third
  CUT_BUT_PRICEY   — filed net <= -THRESH but in the most-expensive third
Review flags, not auto-fail (a cheap-base carrier can raise a bit and stay cheap).
Read-only; exit 1 on hard contradictions."""
import re, json, sys
from collections import defaultdict
from functools import reduce

THRESH, HARD = 5.0, 10.0

def load_model():
    h = open("index.html").read()
    avg = {k: v["avg"] for k, v in json.load(open("state_rankings.json")).items()}
    nat = {}
    m = re.search(r'CARRIERS_STANDARD\s*=\s*\[(.*?)\n\];', h, re.DOTALL)
    for mm in re.finditer(r'name:\s*["\']([^"\']+)["\'][^}]*?base:\s*([0-9.]+)', m.group(1)):
        nat[mm.group(1)] = float(mm.group(2))
    loc = {}
    m = re.search(r'LOCAL_CARRIER_DEFS\s*=\s*\{(.*?)\n\};', h, re.DOTALL)
    for mm in re.finditer(r'"([^"]+)":\s*\{\s*base:\s*([0-9.]+)', m.group(1)):
        loc[mm.group(1)] = float(mm.group(2))
    slc = {}
    m = re.search(r'STATE_LOCAL_CARRIERS\s*=\s*\{(.*?)\n\};', h, re.DOTALL)
    for mm in re.finditer(r'"([A-Z]{2})":\s*\[([^\]]*)\]', m.group(1)):
        slc[mm.group(1)] = re.findall(r'"([^"]+)"', mm.group(2))
    adj = {}
    m = re.search(r'STATE_CARRIER_ADJ\s*=\s*\{(.*?)\n\};', h, re.DOTALL)
    for mm in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', m.group(1)):
        adj[mm.group(1)] = {k.group(1): float(k.group(2)) for k in re.finditer(r'"([^"]+)":\s*([0-9.]+)', mm.group(2))}
    return avg, nat, loc, slc, adj

def full_rank(st, avg, nat, loc, slc, adj):
    a = avg.get(st)
    if not a: return {}
    roster = dict(nat)
    for n in slc.get(st, []):
        if n in loc: roster[n] = loc[n]
    A = adj.get(st, {})
    rows = sorted(((n, round(a * b * A.get(n, 1.0))) for n, b in roster.items()), key=lambda x: x[1])
    return {n: (i + 1, p, len(rows)) for i, (n, p) in enumerate(rows)}

def main():
    sf = json.load(open("serff_filings.json"))["filings"]
    model = load_model()
    fil = defaultdict(list)
    for r in sf:
        if r.get("overall_pct") is None or r.get("drift_exclude"): continue
        # a tiny-book filing (e.g. a 654-PH sub-brand) isn't the carrier's trajectory — skip it
        aff = r.get("affected")
        if aff is not None and aff < 4000 and abs(r["overall_pct"]) >= 1: continue
        fil[(r["state"], r["carrier"])].append(r)
    hard = 0
    for st in sorted({s for s, _ in fil}):
        rank = full_rank(st, *model)
        if not rank: continue
        lines = []
        for (s, car), rs in fil.items():
            if s != st: continue
            net = (reduce(lambda a, r: a * (1 + r["overall_pct"] / 100.0), rs, 1.0) - 1) * 100
            rk = rank.get(car)
            flag = ""
            if rk and abs(net) >= THRESH:
                pr = rk[0] / rk[2]
                if net >= THRESH and pr <= 0.33:
                    flag = "  ⚠ RAISED_BUT_CHEAP"
                    if net >= HARD and rk[0] <= 3: flag += " [HARD]"; hard += 1
                elif net <= -THRESH and pr >= 0.67:
                    flag = "  ⚠ CUT_BUT_PRICEY"
                    if net <= -HARD: flag += " [HARD]"; hard += 1
            pos = "#%d/%d $%d" % (rk[0], rk[2], rk[1]) if rk else "not in tool roster"
            lines.append((net, "  %-22s filed net %+6.1f%%   tool %s%s" % (car, net, pos, flag)))
        print("== %s ==" % st)
        for _, ln in sorted(lines): print(ln)
        print()
    print("HARD contradictions: %d" % hard)
    return 1 if hard else 0

if __name__ == "__main__":
    sys.exit(main())
