#!/usr/bin/env python3
"""
audit_prose.py — drift check: do the AVERAGES baked into the article prose still
match the single source of truth (the rate model), across ALL THREE products?

Each state/metro article hardcodes a market average in its prose (meta description,
dek, FAQ, stat pill). Those were generated at different times; when the state
averages in a product's model change (e.g. auto CO 1706 -> 3264), the prose can go
stale while the live tool + ranking tables update. This script recomputes each
page's average from the model and reports every page whose displayed average drifted.

Sources of truth (one model file per product):
  auto     index.html          const STATE_DATA          article/state, article/metro
  renters  renters/index.html  const RENTERS_STATE_DATA   renters/state
  home     home/index.html     const HOME_STATE_DATA      home/state
    state avg = STATE_DATA[code].avg
    metro avg = state avg * mean(METRO_CARRIER_ADJ[key])   (auto only — see note)

Metros are AUTO-ONLY here: auto is the only product whose model stores a per-metro
offset (METRO_CARRIER_ADJ) in its own source. Renters metro pages were baked from
directional offsets that don't live in renters/index.html, so their averages are not
recomputable from a single source and are intentionally not guarded.

Read-only. Exit 1 if any checked page is out of sync (CI-friendly).
  python3 audit_prose.py                 # all products
  python3 audit_prose.py --product home  # one product
  python3 audit_prose.py --verbose       # also list in-sync pages
"""
import argparse
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDX = (ROOT / "index.html").read_text(encoding="utf-8")  # auto model (module default)
TOL = 0.04       # allow 4% before flagging
FLOOR = 10       # absolute $ floor; 4%*auto-avg (>$1000) always dominates -> auto unchanged

# product -> model file, STATE_DATA var name, page dirs, whether metros are recomputable
PRODUCTS = {
    "auto":    dict(idx="index.html",         state_var="const STATE_DATA",
                    state_dir="article/state", metros=True,  metro_dir="article/metro"),
    "renters": dict(idx="renters/index.html", state_var="const RENTERS_STATE_DATA",
                    state_dir="renters/state", metros=False, metro_dir=None),
    "home":    dict(idx="home/index.html",     state_var="const HOME_STATE_DATA",
                    state_dir="home/state",    metros=False, metro_dir=None),
}

SLUG_OVERRIDE = {"tam": "tampa", "sjv": "san-jose", "nfk": "norfolk", "csc": "columbia-sc",
                 "gso": "greensboro", "wil": "wilmington-de", "mnh": "manchester-nh",
                 "bvt": "burlington-vt",
                 # two Portlands: 'por'=Oregon, 'pme'=Maine — both are named "Portland metro",
                 # so without this they collide on article/metro/portland.html.
                 "por": "portland", "pme": "portland-me"}


def block(name, open_, close, src=IDX):
    i = src.index(name); s = src.index(open_, i); d = 0; j = s
    while j < len(src):
        if src[j] == open_: d += 1
        elif src[j] == close:
            d -= 1
            if d == 0: j += 1; break
        j += 1
    return src[s:j]


def parse_state_avgs(src=IDX, var="const STATE_DATA"):
    b = block(var, "{", "}", src)
    return {m[0]: int(m[1]) for m in re.findall(r'"([A-Z]{2})":\s*\{[^}]*?avg:\s*(\d+)', b)}


def parse_metro_adj(src=IDX):
    b = block("const METRO_CARRIER_ADJ", "{", "}", src)
    out = {}
    for m in re.finditer(r'(\w+):\s*\{([^}]*)\}', b):
        vals = [float(v) for v in re.findall(r':\s*([0-9.]+)', m.group(2))]
        if vals:
            out[m.group(1)] = vals
    return out


def parse_metro_state(src=IDX):
    zm = {m[0]: m[1] for m in re.findall(r'"(\d+)":\s*"(\w+)"', block("const ZIP_PREFIX_METRO", "{", "}", src))}
    z3 = {m[0]: m[1] for m in re.findall(r'"(\d+)":\s*"([A-Z]{2})"', block("const ZIP3_TO_STATE", "{", "}", src))}
    ms = {}
    for pfx, key in zm.items():
        if key not in ms:
            st = z3.get(pfx) or z3.get(pfx[:2])
            if st:
                ms[key] = st
    return ms


def parse_metro_names(src=IDX):
    return {m[0]: m[1] for m in re.findall(r'(\w+):\s*"([^"]+)"', block("const METRO_NAMES", "{", "}", src))}


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


def state_slug(name):
    return name.lower().replace(".", "").replace(" ", "-")


def displayed_avg(html, product="auto"):
    """Pull the headline average from the meta description.
    renters/home use the clean 'is $X/year' phrasing; auto's prose varies, so we keep
    the original $X,XXX comma-form heuristic (a 4-digit average). Returns None if the
    meta has no such figure (page not auto-checkable)."""
    md = re.search(r'<meta name="description" content="([^"]*)"', html)
    if not md:
        return None
    text = md.group(1)
    if product in ("renters", "home"):
        m = re.search(r'\bis \$([0-9,]+)/year', text)
    else:
        m = re.search(r'\$([0-9],[0-9]{3})\b', text)
    return int(m.group(1).replace(",", "")) if m else None


def collect(product):
    """Return (rows, cfg) for one product. rows = (kind, slug, displayed, expected, code)."""
    cfg = PRODUCTS[product]
    src = (ROOT / cfg["idx"]).read_text(encoding="utf-8")
    state_avg = parse_state_avgs(src, cfg["state_var"])
    sd_block = block(cfg["state_var"], "{", "}", src)
    rows = []

    # --- metros (auto only) ---
    if cfg["metros"]:
        madj = parse_metro_adj(src)
        mstate = parse_metro_state(src)
        names = parse_metro_names(src)
        for key, offsets in madj.items():
            st = mstate.get(key)
            if not st or st not in state_avg:
                continue
            expected = round(state_avg[st] * statistics.mean(offsets) / 10) * 10
            slug = slugify(key, names)
            f = ROOT / cfg["metro_dir"] / f"{slug}.html"
            if not f.exists():
                continue
            disp = displayed_avg(f.read_text(encoding="utf-8"), product)
            if disp is None:
                continue
            rows.append(("metro", slug, disp, expected, st))

    # --- states (all products) ---
    for code, avg in state_avg.items():
        nm = re.search(r'"%s":\s*\{\s*name:\s*"([^"]+)"' % code, sd_block)
        if not nm:
            continue
        f = ROOT / cfg["state_dir"] / f"{state_slug(nm.group(1))}.html"
        if not f.exists():
            continue
        disp = displayed_avg(f.read_text(encoding="utf-8"), product)
        if disp is None:
            continue
        rows.append(("state", state_slug(nm.group(1)), disp, avg, code))

    return rows, cfg


def report(product, rows):
    drift = [r for r in rows if abs(r[2] - r[3]) > max(TOL * r[3], FLOOR)]
    drift.sort(key=lambda r: -abs(r[2] - r[3]) / r[3])
    print("[%s] prose-vs-model average drift" % product)
    print("  pages checked : %d  (%d metro, %d state)" % (
        len(rows), sum(r[0] == "metro" for r in rows), sum(r[0] == "state" for r in rows)))
    print("  in sync       : %d" % (len(rows) - len(drift)))
    print("  DRIFTED       : %d" % len(drift))
    if drift:
        print("  %-6s %-22s %10s %10s %8s" % ("kind", "slug", "shows", "should be", "off"))
        for kind, slug, disp, exp, st in drift:
            off = (disp - exp) / exp * 100
            print("  %-6s %-22s %10s %10s %+7.0f%%" % (kind, slug, f"${disp:,}", f"${exp:,}", off))
    return drift


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", choices=list(PRODUCTS) + ["all"], default="all")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    products = list(PRODUCTS) if args.product == "all" else [args.product]
    any_drift = False
    for i, product in enumerate(products):
        if i:
            print()
        rows, _ = collect(product)
        drift = report(product, rows)
        any_drift = any_drift or bool(drift)
        if args.verbose:
            drifted = {(d[0], d[1]) for d in drift}
            print("  in-sync pages:")
            for kind, slug, disp, exp, st in rows:
                if (kind, slug) not in drifted:
                    print("    %-6s %-22s $%s" % (kind, slug, f"{disp:,}"))
    raise SystemExit(1 if any_drift else 0)


if __name__ == "__main__":
    main()
