#!/usr/bin/env python3
"""
verify_model_accuracy_rh.py — renters/home twin of verify_model_accuracy.py.

Scores each product's model (stateAvg x base x STATE_CARRIER_ADJ, footprint
carriers only in their states — same math as the tool and the static state
pages) against cheapest_by_state_{product}.json (NerdWallet + MoneyGeek tier).

USAA is NOT excluded (unlike auto): the sources include it, and both tools show
it with an availability note. Metric: does a real cheap-tier carrier land in
the model's top-3/top-5 for that state. Median best-rank across states.

Usage: verify_model_accuracy_rh.py [--product renters|home|all] [--min FRAC]
"""
import argparse
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = {
    "renters": ("renters/index.html", "RENTERS_CARRIERS = [", "RENTERS_STATE_DATA = {"),
    "home": ("home/index.html", "HOME_CARRIERS = [", "HOME_STATE_DATA = {"),
}


def blk(s, a, e):
    i = s.index(a)
    return s[i + len(a):s.index(e, i)]


def load(product):
    page, ckey, skey = CFG[product]
    s = (ROOT / page).read_text(encoding="utf-8")
    carriers = []
    for ch in blk(s, ckey, "\n];").split("\n  {"):
        nm = re.search(r'name:\s*"([^"]+)"', ch)
        bs = re.search(r'base:\s*([0-9.]+)', ch)
        if not (nm and bs):
            continue
        stm = re.search(r'states:\s*\[([^\]]*)\]', ch)
        states = set(re.findall(r'"([A-Z]{2})"', stm.group(1))) if stm else None
        carriers.append((nm.group(1), float(bs.group(1)), states))
    SD = {m.group(1): int(m.group(2)) for m in
          re.finditer(r'"([A-Z]{2})":\s*\{[^}]*avg:\s*(\d+)', blk(s, skey, "\n};"))}
    adj = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', blk(s, "STATE_CARRIER_ADJ = {", "\n};")):
        adj[m.group(1)] = {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
    return carriers, SD, adj


def ranked(code, carriers, SD, adj):
    avg = SD[code]
    t = adj.get(code, {})
    pr = [(n, avg * b * t.get(n, 1)) for n, b, states in carriers
          if states is None or code in states]
    pr.sort(key=lambda x: x[1])
    return [n for n, _ in pr]


def score(product, min_gate=None):
    carriers, SD, adj = load(product)
    ref = json.load(open(ROOT / f"cheapest_by_state_{product}.json"))["states"]
    scored = hit3 = hit5 = agree_scored = agree_hit5 = 0
    best_ranks, misses = [], []
    for code, d in ref.items():
        cheap = d.get("roster_cheap") or []
        if not cheap or code not in SD:
            continue
        scored += 1
        order = ranked(code, carriers, SD, adj)
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
            misses.append("%s: cheap=%s -> %s (model top3=%s)" % (code, cheap, shown or "not shown", order[:3]))
    f5 = hit5 / scored
    print(f"[{product}] vs multi-source published cheapest-by-state (USAA included)")
    print("  states scored                 : %d" % scored)
    print("  real cheap carrier in top-3   : %d (%.0f%%)" % (hit3, hit3 / scored * 100))
    print("  real cheap carrier in top-5   : %d (%.0f%%)" % (hit5, f5 * 100))
    print("  median best rank              : %.1f" % statistics.median(best_ranks))
    if agree_scored:
        print("  [high-confidence] both agree  : %d/%d in top-5" % (agree_hit5, agree_scored))
    if misses:
        print("  misses (no cheap carrier in top-5):")
        for m in misses:
            print("    " + m)
    print()
    return f5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", default="all", choices=["renters", "home", "all"])
    ap.add_argument("--min", type=float, default=None, help="regression gate: min top-5 fraction")
    args = ap.parse_args()
    products = ["renters", "home"] if args.product == "all" else [args.product]
    worst = min(score(p) for p in products)
    if args.min is not None:
        ok = worst >= args.min
        print("%s worst top-5 %.0f%% vs gate %.0f%%" % ("PASS" if ok else "FAIL", worst * 100, args.min * 100))
        raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
