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

    # Score against the cheap TIER (roster_cheap = in-roster carriers named cheapest
    # by EITHER source), since the single per-state #1 is source-noise. A state is a
    # "hit" if the model ranks any of its real cheap-tier carriers in the top-N.
    scored = hit3 = hit5 = 0
    agree_scored = agree_hit5 = 0
    best_ranks = []
    misses = []
    for code, d in ref.items():
        cheap = d.get("roster_cheap") or []
        if not cheap:
            continue
        scored += 1
        order = ranked(code, natbase, regbase, statereg, SD, adj, exclude={"USAA"})
        rks = [order.index(c) + 1 for c in cheap if c in order]
        best = min(rks) if rks else 99
        best_ranks.append(best)
        hit3 += best <= 3
        hit5 += best <= 5
        if d.get("sources_agree"):
            agree_scored += 1
            agree_hit5 += best <= 5
        if best > 5:
            shown = {c: order.index(c) + 1 for c in cheap if c in order}
            misses.append("%s: cheap=%s -> %s (model top3=%s)" % (
                code, cheap, shown or "none shown", order[:3]))

    f5 = hit5 / scored
    print("Model accuracy vs MULTI-SOURCE published cheapest-by-state (USAA excluded)")
    print("  scored on the in-roster cheap TIER (either source); single-#1 is source-noise.")
    print("  states scored             : %d" % scored)
    print("  a real cheap carrier in top-3 : %d (%.0f%%)" % (hit3, hit3 / scored * 100))
    print("  a real cheap carrier in top-5 : %d (%.0f%%)" % (hit5, f5 * 100))
    print("  median best rank          : %.1f" % statistics.median(best_ranks))
    if agree_scored:
        print("  [high-confidence] both sources agree: %d/%d in top-5 (%.0f%%)" % (
            agree_hit5, agree_scored, agree_hit5 / agree_scored * 100))
    if misses:
        print("\n  misses (no real cheap carrier in model top-5):")
        for m in misses:
            print("    " + m)
    if args.min is None:
        raise SystemExit(0)
    ok = f5 >= args.min
    print("\n%s top-5 %.0f%% vs gate %.0f%%" % ("PASS" if ok else "FAIL", f5 * 100, args.min * 100))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
