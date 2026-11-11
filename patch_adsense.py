#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install (or remove) the Google AdSense loader on CONTENT pages only, and write /ads.txt.

Policy (owner decision 2026-11-11): ads may run on articles, guides, trackers and filing pages
to measure revenue potential. They NEVER run on the rate tools or their results, the coverage
calculators, or the trust pages - payment must never sit next to a ranking it could appear
to influence (editorial standards § 02).

Config lives in adsense.json:  {"client": "ca-pub-XXXXXXXXXXXXXXXX"}
Until that file holds a real publisher id this script is a no-op, so it is safe in rebuild.sh.

    python3 patch_adsense.py            # dry run: count pages that would get the loader
    python3 patch_adsense.py --apply    # insert loader (idempotent) + write ads.txt
    python3 patch_adsense.py --remove   # strip the loader from every page (rollback)

Safety (CLAUDE.md): the loader is INSERTED as its own marked <script> before </head>; no
existing script block is ever replaced. Re-running after a regen re-adds it, so generators
need no changes.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
MARK = "<!-- br-adsense -->"
META_MARK = "<!-- br-adsense-meta -->"
CFG = ROOT / "adsense.json"

# Never ads: tools + results, calculators, trust/policy pages, templates, previews.
EXCLUDE = {
    "index.html", "home/index.html", "renters/index.html",
    "coverage.html", "home/coverage.html", "renters/coverage.html",
    "about.html", "editorial-standards.html", "methodology.html", "privacy.html", "press/index.html",
    "gen_metro_base.html", "cta-preview.html",
}
SKIP_DIRS = {"_serff", "_umami", "_gsc", "node_modules", "partials", ".git", "__pycache__"}


def client():
    try:
        c = json.loads(CFG.read_text())["client"].strip()
    except Exception:
        return None
    return c if re.fullmatch(r"ca-pub-\d{16}", c) else None


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if rel in EXCLUDE or set(p.relative_to(ROOT).parts) & SKIP_DIRS:
            continue
        yield p, rel


def meta(c):
    # Ownership verification only - loads no script and shows no ads. Goes on EVERY page,
    # tools included, because Google verifies the homepage (which is the ad-free ZIP tool).
    return f'{META_MARK}<meta name="google-adsense-account" content="{c}">\n'


def all_pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if set(p.relative_to(ROOT).parts) & SKIP_DIRS or rel in ("gen_metro_base.html", "cta-preview.html"):
            continue
        yield p, rel


def snippet(c):
    return (f'{MARK}<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={c}" crossorigin="anonymous"></script>\n')


def main():
    if "--remove" in sys.argv:
        rx = re.compile(re.escape(MARK) + r'<script async src="https://pagead2\.googlesyndication\.com[^"]*" crossorigin="anonymous"></script>\n?')
        n = 0
        for p in ROOT.rglob("*.html"):
            if set(p.relative_to(ROOT).parts) & SKIP_DIRS:
                continue
            s = p.read_text(encoding="utf-8")
            t = rx.sub("", s)
            t = re.sub(re.escape(META_MARK) + r'<meta name="google-adsense-account" content="[^"]*">\n?', "", t)
            if t != s:
                p.write_text(t, encoding="utf-8"); n += 1
        print(f"removed AdSense loader from {n} pages")
        return

    c = client()
    if not c:
        print("adsense: not configured (adsense.json needs {\"client\": \"ca-pub-<16 digits>\"}) - no-op")
        return
    todo, have, nohead = [], 0, []
    for p, rel in pages():
        s = p.read_text(encoding="utf-8")
        if MARK in s:
            have += 1
        elif "</head>" not in s:
            nohead.append(rel)
        else:
            todo.append((p, s))
    # Excluded pages must never carry it, even if a past run or a hand edit put it there.
    leaked = [r for r in EXCLUDE if (ROOT / r).exists() and MARK in (ROOT / r).read_text(encoding="utf-8")]
    if leaked:
        sys.exit(f"AdSense loader found on excluded pages {leaked} - run --remove, then --apply")
    print(f"adsense {c}: {len(todo)} pages to patch, {have} already have it, {len(nohead)} without </head>")
    if "--apply" not in sys.argv:
        print("dry run - re-run with --apply"); return
    for p, s in todo:
        i = s.index("</head>")
        p.write_text(s[:i] + snippet(c) + s[i:], encoding="utf-8")
    nm = 0
    for p, rel in all_pages():
        s = p.read_text(encoding="utf-8")
        if META_MARK in s or "</head>" not in s:
            continue
        i = s.index("</head>")
        p.write_text(s[:i] + meta(c) + s[i:], encoding="utf-8"); nm += 1
    print(f"verification meta tag added to {nm} pages")
    pub = c.replace("ca-", "")
    (ROOT / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    print(f"patched {len(todo)} pages; wrote ads.txt")


if __name__ == "__main__":
    main()
