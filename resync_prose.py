#!/usr/bin/env python3
"""
resync_prose.py — bring stale article prose averages back in sync with the single
source (the product's rate model), SURGICALLY (numbers/direction words only — never
rebuilds page structure). The fixer half of audit_prose.py; same three products.

Full regeneration is unsafe: the metro/state generators rebuild from stale templates
that predate the CTA/nav migrations, so they'd regress the live pages. Instead this
patches just the displayed average + "vs national" wording in place.

Per page it replaces:
  - the headline market average ($X / $X,XXX) everywhere it appears (all products)
  - "N% below/above the national average|norm"   -> recomputed % + direction (auto/renters)
  - the stat-pill "&middot; ±N%"                   -> recomputed (auto)
National baseline = mean of that product's 51 state averages (self-consistent:
auto $2,458 / renters $168 / home $1,863).

Deliberately NOT touched: bare "below/above the national average" prose with no
percentage. That's editorial (catastrophe-risk narrative, "just below" for a
near-mean state) — mechanically flipping the direction word lies about magnitude
("well below" by 1%) and can't recompute the intensity qualifier. audit_prose.py
still guards the NUMBER on those pages; a genuine sign flip is a human edit.
Consequence: home prose carries no numeric %, so home resync is effectively a
dollar-figure sync (which is the primary drift vector anyway).

Metros are AUTO-ONLY (only auto stores per-metro offsets in its own model — see
audit_prose.py).

  python3 resync_prose.py --product home      # fix one product
  python3 resync_prose.py --dry               # show changes, write nothing
After writing, run (auto only) gen_metro_compare.js + gen_state_rankings.js
--states --metros, then audit_prose.py must report 0 drift.
"""
import argparse
import re
import statistics
from pathlib import Path
import audit_prose as A

ROOT = Path(__file__).resolve().parent

# per-product plausibility bounds for the parsed displayed average (guards a bad parse)
# bounds bracket each product's real avg range (auto ~$1.3k-4.6k, renters ~$100-260,
# home ~$479 HI - $4.2k FL) with margin — tight enough to catch a mis-parse.
PLAUSIBLE = {"auto": (800, 9000), "renters": (60, 600), "home": (400, 9000)}


def pct_word(avg, national):
    p = round((avg / national - 1) * 100)
    return abs(p), ("above" if p >= 0 else "below")


def patch(path, new_avg, national, product, dry):
    html = path.read_text(encoding="utf-8")
    old = A.displayed_avg(html, product)
    if old is None:
        return None
    lo, hi = PLAUSIBLE[product]
    if not (lo <= old <= hi):          # implausible parse -> skip, flag for manual review
        return ("SKIP", old, new_avg)
    p, word = pct_word(new_avg, national)
    out = html.replace(f"${old:,}", f"${new_avg:,}")
    # numeric "N% below/above the national average|norm" (auto, renters) — formulaic,
    # safe to recompute (the % IS derived from the number, direction word included).
    # NOTE: bare "below/above the national average" (no %) is NOT touched — it's
    # editorial prose (e.g. catastrophe-risk narrative, "just below" near the mean)
    # that can't be mechanically flipped without lying or breaking the intensity word.
    out = re.sub(r'\b\d+% (below|above) the national (average|norm)',
                 lambda m: f"{p}% {word} the national {m.group(2)}", out)
    # stat-pill "&middot; ±N%" (auto)
    sign = "+" if word == "above" else "-"
    out = re.sub(r'(&middot;\s*)[+-]?\d+%', rf'\g<1>{sign}{p}%', out)
    changed = out != html
    if changed and not dry:
        path.write_text(out, encoding="utf-8")
    return ("CHANGE" if changed else "ok", old, new_avg)


def targets_for(product):
    """Return (targets, national) for one product. targets = (kind, slug, path, new_avg)."""
    cfg = A.PRODUCTS[product]
    src = (ROOT / cfg["idx"]).read_text(encoding="utf-8")
    state_avg = A.parse_state_avgs(src, cfg["state_var"])
    national = round(statistics.mean(state_avg.values()))
    sd_block = A.block(cfg["state_var"], "{", "}", src)
    targets = []

    if cfg["metros"]:
        madj = A.parse_metro_adj(src)
        mstate = A.parse_metro_state(src)
        names = A.parse_metro_names(src)
        for key, offsets in madj.items():
            st = mstate.get(key)
            if not st or st not in state_avg:
                continue
            slug = A.slugify(key, names)
            f = ROOT / cfg["metro_dir"] / f"{slug}.html"
            if f.exists():
                targets.append(("metro", slug, f,
                                round(state_avg[st] * statistics.mean(offsets) / 10) * 10))

    for code, avg in state_avg.items():
        nm = re.search(r'"%s":\s*\{\s*name:\s*"([^"]+)"' % code, sd_block)
        if not nm:
            continue
        f = ROOT / cfg["state_dir"] / f"{A.state_slug(nm.group(1))}.html"
        if f.exists():
            targets.append(("state", A.state_slug(nm.group(1)), f, avg))

    return targets, national


def run(product, only, dry):
    targets, national = targets_for(product)
    if only:
        targets = [t for t in targets if t[1] == only]
    changed = skipped = 0
    for kind, slug, f, new_avg in targets:
        r = patch(f, new_avg, national, product, dry)
        if not r:
            continue
        status, old, new = r
        if status == "CHANGE":
            changed += 1
            print("  %-6s %-22s $%-6s -> $%-6s" % (kind, slug, f"{old:,}", f"{new:,}"))
        elif status == "SKIP":
            skipped += 1
            print("  SKIP   %-22s displayed $%s implausible — review manually" % (slug, old))
    print("[%s] %s%d pages %s, %d skipped (national baseline $%d)" % (
        product, "[dry] " if dry else "", changed,
        "would change" if dry else "patched", skipped, national))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", choices=list(A.PRODUCTS) + ["all"], default="all")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", help="patch a single slug (testing)")
    args = ap.parse_args()

    products = list(A.PRODUCTS) if args.product == "all" else [args.product]
    for i, product in enumerate(products):
        if i:
            print()
        run(product, args.only, args.dry)


if __name__ == "__main__":
    main()
