#!/usr/bin/env python3
"""
resync_prose.py — bring stale article prose averages back in sync with the single
source (index.html), SURGICALLY (numbers only — never rebuilds page structure).

Full regeneration is unsafe: gen_metro_page.py rebuilds from a stale template that
predates the CTA/nav migrations, so it would regress the live pages. Instead this
patches just the displayed average + "% vs national" wording in place.

Per page it replaces:
  - the headline market average ($X,XXX) everywhere it appears
  - "N% below/above the national average|norm"  -> recomputed
  - the stat-pill "&middot; ±N%"                  -> recomputed
National baseline = mean of the model's 51 state averages (self-consistent).

After this, run gen_metro_compare.js (sibling-metro numbers) and
gen_state_rankings.js --states --metros (ranking tables), then audit_prose.py
must report 0 drift. --dry shows what would change without writing.
"""
import argparse
import re
import statistics
from pathlib import Path
import audit_prose as A

ROOT = Path(__file__).resolve().parent
STATE_AVG = A.parse_state_avgs()
MADJ = A.parse_metro_adj()
MSTATE = A.parse_metro_state()
NAMES = A.parse_metro_names()
NATIONAL = round(statistics.mean(STATE_AVG.values()))


def pct_word(avg):
    p = round((avg / NATIONAL - 1) * 100)
    return abs(p), ("above" if p >= 0 else "below")


def patch(path, new_avg, dry):
    html = path.read_text(encoding="utf-8")
    old = A.displayed_avg(html)
    if old is None:
        return None
    if not (800 <= old <= 9000):      # implausible parse -> skip, flag for manual review
        return ("SKIP", old, new_avg)
    p, word = pct_word(new_avg)
    out = html.replace(f"${old:,}", f"${new_avg:,}")
    out = re.sub(r'\b\d+% (?:below|above) the national (average|norm)',
                 lambda m: f"{p}% {word} the national {m.group(1)}", out)
    sign = "+" if word == "above" else "-"
    out = re.sub(r'(&middot;\s*)[+-]?\d+%', rf'\g<1>{sign}{p}%', out)
    changed = out != html
    if changed and not dry:
        path.write_text(out, encoding="utf-8")
    return ("CHANGE" if changed else "ok", old, new_avg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", help="patch a single slug (testing)")
    args = ap.parse_args()

    targets = []  # (kind, slug, path, new_avg)
    for key, offsets in MADJ.items():
        st = MSTATE.get(key)
        if not st or st not in STATE_AVG:
            continue
        slug = A.slugify(key, NAMES)
        f = ROOT / "article" / "metro" / f"{slug}.html"
        if f.exists():
            targets.append(("metro", slug, f, round(STATE_AVG[st] * statistics.mean(offsets) / 10) * 10))
    sd_block = A.block("const STATE_DATA", "{", "}")
    for code, avg in STATE_AVG.items():
        nm = re.search(r'"%s":\s*\{\s*name:\s*"([^"]+)"' % code, sd_block)
        if not nm:
            continue
        slug = nm.group(1).lower().replace(".", "").replace(" ", "-")
        f = ROOT / "article" / "state" / f"{slug}.html"
        if f.exists():
            targets.append(("state", slug, f, avg))

    if args.only:
        targets = [t for t in targets if t[1] == args.only]

    changed = skipped = 0
    for kind, slug, f, new_avg in targets:
        r = patch(f, new_avg, args.dry)
        if not r:
            continue
        status, old, new = r
        if status == "CHANGE":
            changed += 1
            print("  %-6s %-22s $%-6s -> $%-6s" % (kind, slug, f"{old:,}", f"{new:,}"))
        elif status == "SKIP":
            skipped += 1
            print("  SKIP   %-22s displayed $%s implausible — review manually" % (slug, old))
    print("\n%s%d pages %s, %d skipped (national baseline $%d)" % (
        "[dry] " if args.dry else "", changed, "would change" if args.dry else "patched",
        skipped, NATIONAL))


if __name__ == "__main__":
    main()
