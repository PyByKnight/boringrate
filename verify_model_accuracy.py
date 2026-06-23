#!/usr/bin/env python3
"""
verify_model_accuracy.py — measure the auto model against REAL external data.

Unlike verify_offset_consistency.py (which compares the tool to the in-house
editorial rankings page), this scores the model against cheapest_by_state.json —
published third-party per-state cheapest carriers (NerdWallet, cross-checked vs
ValuePenguin). This is the closest thing we have to ground truth.

Metric: for each state whose real cheapest carrier is one we carry, where does the
model rank it? USAA is excluded (the published "cheapest" lists exclude it as
military-restricted). Reports #1-match, top-3, top-5, median rank, and the misses.

Caveat: the reference is essentially single-source and the exact #1 varies by
source/profile, so treat top-5 / median-rank as the real signals, not #1-exact —
and do NOT tune the model to 100% (that's overfitting to one source's quirks).

Exit 0 always (report only) unless --min TOP5_FRACTION given as a regression gate.
"""
import argparse
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def blk(s, a, e="\n};"):
    i = s.index(a)
    return s[i + len(a):s.index(e, i)]


def load():
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    natbase = {}
    for ch in re.split(r"\n  \{", blk(s, "CARRIERS_STANDARD = [", "\n];")):
        nm = re.search(r'name:\s*"([^"]+)"', ch)
        bs = re.search(r"base:\s*([0-9.]+)", ch)
        if nm and bs:
            natbase[nm.group(1)] = float(bs.group(1))
    regbase = {m.group(1): float(m.group(2)) for m in
               re.finditer(r'"([^"]+)":\s*\{\s*base:\s*([0-9.]+)', blk(s, "LOCAL_CARRIER_DEFS = {"))}
    statereg = {m.group(1): re.findall(r'"([^"]+)"', m.group(2)) for m in
                re.finditer(r'"([A-Z]{2})":\s*\[([^\]]*)\]', blk(s, "STATE_LOCAL_CARRIERS = {"))}
    SD = {m.group(1): int(m.group(3)) for m in
          re.finditer(r'"([A-Z]{2})":\s*\{\s*name:\s*"([^"]+)"\s*,\s*avg:\s*(\d+)', blk(s, "STATE_DATA = {"))}
    adj = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', blk(s, "STATE_CARRIER_ADJ = {")):
        adj[m.group(1)] = {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
    return natbase, regbase, statereg, SD, adj


def ranked(code, natbase, regbase, statereg, SD, adj, exclude=()):
    avg = SD[code]
    t = adj.get(code, {})
    pr = [(c, avg * b * t.get(c, 1)) for c, b in natbase.items() if c not in exclude]
    for c in statereg.get(code, []):
        if c in regbase:
            pr.append((c, avg * regbase[c] * t.get(c, 1)))
    pr.sort(key=lambda x: x[1])
    return [c for c, _ in pr]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=None, help="regression gate: min top-5 fraction")
    args = ap.parse_args()

    natbase, regbase, statereg, SD, adj = load()
    ref = json.load(open(ROOT / "cheapest_by_state.json"))["states"]

    scored = r1 = top3 = top5 = unavail = 0
    ranks = []
    misses = []
    for code, d in ref.items():
        rn = d["roster_name"]
        if not rn:
            continue
        scored += 1
        order = ranked(code, natbase, regbase, statereg, SD, adj, exclude={"USAA"})
        if rn not in order:
            unavail += 1
            misses.append("%s: %s NOT SHOWN (availability gap)" % (code, rn))
            continue
        rk = order.index(rn) + 1
        ranks.append(rk)
        r1 += rk == 1
        top3 += rk <= 3
        top5 += rk <= 5
        if rk > 5:
            misses.append("%s: real=%s at model #%d (top3=%s)" % (code, rn, rk, order[:3]))

    f5 = top5 / scored
    print("Model accuracy vs published cheapest-by-state (cheapest_by_state.json, USAA excluded)")
    print("  states scored        : %d" % scored)
    print("  real #1 == model #1  : %d (%.0f%%)" % (r1, r1 / scored * 100))
    print("  real #1 in top-3     : %d (%.0f%%)" % (top3, top3 / scored * 100))
    print("  real #1 in top-5     : %d (%.0f%%)" % (top5, f5 * 100))
    print("  median rank of real#1: %.1f" % statistics.median(ranks))
    print("  not shown at all     : %d" % unavail)
    if misses:
        print("\n  misses:")
        for m in misses:
            print("    " + m)
    if args.min is None:
        raise SystemExit(0)
    ok = f5 >= args.min
    print("\n%s top-5 %.0f%% vs gate %.0f%%" % ("PASS" if ok else "FAIL", f5 * 100, args.min * 100))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
