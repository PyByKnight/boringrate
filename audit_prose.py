#!/usr/bin/env python3
"""
audit_prose.py — drift check: do the AVERAGES baked into the article prose still
match the single source of truth (the rate model in index.html)?

Each metro/state article hardcodes a market average in its prose (meta description,
dek, FAQ, stat pill). Those were generated at different times; when state averages
in index.html change (e.g. CO 1706 -> 3264), the prose can go stale while the live
tool + ranking tables update. This script recomputes each page's average from
index.html and reports every page whose displayed average has drifted.

Source of truth (all parsed from index.html):
  state avg   = STATE_DATA[code].avg
  metro avg   = state avg * mean(METRO_CARRIER_ADJ[key])   (same as the tool/engine)

Read-only. Exit 1 if any page is out of sync (CI-friendly). --verbose lists all.
"""
import argparse
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDX = (ROOT / "index.html").read_text(encoding="utf-8")
NATIONAL = 2400  # national baseline used by the metro prose generator
TOL = 0.04       # allow 4% / $40 rounding slack before flagging

SLUG_OVERRIDE = {"tam": "tampa", "sjv": "san-jose", "nfk": "norfolk", "csc": "columbia-sc",
                 "gso": "greensboro", "wil": "wilmington-de", "mnh": "manchester-nh",
                 "bvt": "burlington-vt"}


def block(name, open_, close):
    i = IDX.index(name); s = IDX.index(open_, i); d = 0; j = s
    while j < len(IDX):
        if IDX[j] == open_: d += 1
        elif IDX[j] == close:
            d -= 1
            if d == 0: j += 1; break
        j += 1
    return IDX[s:j]


def parse_state_avgs():
    b = block("const STATE_DATA", "{", "}")
    return {m[0]: int(m[1]) for m in re.findall(r'"([A-Z]{2})":\s*\{[^}]*?avg:\s*(\d+)', b)}


def parse_metro_adj():
    b = block("const METRO_CARRIER_ADJ", "{", "}")
    out = {}
    for m in re.finditer(r'(\w+):\s*\{([^}]*)\}', b):
        vals = [float(v) for v in re.findall(r':\s*([0-9.]+)', m.group(2))]
        if vals:
            out[m.group(1)] = vals
    return out


def parse_metro_state():
    zm = {m[0]: m[1] for m in re.findall(r'"(\d+)":\s*"(\w+)"', block("const ZIP_PREFIX_METRO", "{", "}"))}
    z3 = {m[0]: m[1] for m in re.findall(r'"(\d+)":\s*"([A-Z]{2})"', block("const ZIP3_TO_STATE", "{", "}"))}
    ms = {}
    for pfx, key in zm.items():
        if key not in ms:
            st = z3.get(pfx) or z3.get(pfx[:2])
            if st:
                ms[key] = st
    return ms


def parse_metro_names():
    return {m[0]: m[1] for m in re.findall(r'(\w+):\s*"([^"]+)"', block("const METRO_NAMES", "{", "}"))}


def slugify(key, names):
    if key in SLUG_OVERRIDE:
        return SLUG_OVERRIDE[key]
    clean = re.sub(r'\s+metro$', '', names.get(key, key), flags=re.I)
    s = clean.lower()
    s = re.sub(r'[–—]', '-', s)
    s = re.sub(r'[.,/]', '', s)
    s = s.replace(' & ', '-')
    s = re.sub(r'\s+', '-', s)
    return s


def displayed_avg(html):
    """Pull the headline average the page advertises (first $X,XXX in the meta description)."""
    m = re.search(r'<meta name="description" content="[^"]*?\$([0-9,]+)', html)
    return int(m.group(1).replace(",", "")) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    state_avg = parse_state_avgs()
    madj = parse_metro_adj()
    mstate = parse_metro_state()
    names = parse_metro_names()

    rows = []  # (kind, slug, displayed, expected, state)
    # --- metros ---
    for key, offsets in madj.items():
        st = mstate.get(key)
        if not st or st not in state_avg:
            continue
        expected = round(state_avg[st] * statistics.mean(offsets) / 10) * 10
        slug = slugify(key, names)
        f = ROOT / "article" / "metro" / f"{slug}.html"
        if not f.exists():
            continue
        disp = displayed_avg(f.read_text(encoding="utf-8"))
        if disp is None:
            continue
        rows.append(("metro", slug, disp, expected, st))
    # --- states ---
    for code, avg in state_avg.items():
        # state article slug = state name slugified; resolve via STATE_DATA name
        nm = re.search(r'"%s":\s*\{\s*name:\s*"([^"]+)"' % code, block("const STATE_DATA", "{", "}"))
        if not nm:
            continue
        slug = nm.group(1).lower().replace(".", "").replace(" ", "-")
        f = ROOT / "article" / "state" / f"{slug}.html"
        if not f.exists():
            continue
        disp = displayed_avg(f.read_text(encoding="utf-8"))
        if disp is None:
            continue
        rows.append(("state", slug, disp, avg, code))

    drift = [r for r in rows if abs(r[2] - r[3]) > max(TOL * r[3], 40)]
    drift.sort(key=lambda r: -abs(r[2] - r[3]) / r[3])

    print("Prose-vs-model average drift (source: index.html STATE_DATA + METRO_CARRIER_ADJ)")
    print("  pages checked : %d  (%d metro, %d state)" % (
        len(rows), sum(r[0] == "metro" for r in rows), sum(r[0] == "state" for r in rows)))
    print("  in sync       : %d" % (len(rows) - len(drift)))
    print("  DRIFTED       : %d\n" % len(drift))
    if drift:
        print("  %-6s %-22s %10s %10s %8s" % ("kind", "slug", "shows", "should be", "off"))
        for kind, slug, disp, exp, st in drift:
            off = (disp - exp) / exp * 100
            print("  %-6s %-22s %10s %10s %+7.0f%%" % (kind, slug, f"${disp:,}", f"${exp:,}", off))
    if args.verbose:
        print("\n  in-sync pages:")
        for kind, slug, disp, exp, st in rows:
            if (kind, slug) not in {(d[0], d[1]) for d in drift}:
                print("    %-6s %-22s $%s" % (kind, slug, f"{disp:,}"))
    raise SystemExit(1 if drift else 0)


if __name__ == "__main__":
    main()
