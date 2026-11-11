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
    python3 patch_adsense.py --remove   # strip loader, meta, units + unit CSS from every page (rollback)

In-article units: adsense.json may also hold {"slots": {"intro": "<id>", "prefaq": "<id>"}}.
Each slot with an id is placed on every loader page that has a fitting spot (see anchors());
a blank or missing id leaves that unit off. Units are re-placed fresh on every --apply.

Safety (CLAUDE.md): the loader is INSERTED as its own marked <script> before </head>; no
existing script block is ever replaced. Re-running after a regen re-adds it, so generators
need no changes.
"""
import json, pathlib, re, sys
from collections import Counter

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


def slots():
    """{"intro": "<slot id>", "prefaq": "<slot id>"} from adsense.json; blank/missing = unit off."""
    try:
        sl = json.loads(CFG.read_text()).get("slots", {})
    except Exception:
        return {}
    return {k: str(v).strip() for k, v in sl.items() if re.fullmatch(r"\d{6,}", str(v).strip())}


# ── In-article units ──────────────────────────────────────────────────────────────────
# Each unit is ONE self-contained marked block (start/end comments) so it can be found,
# updated (new slot id) or removed without touching anything around it.
UNIT_RX = re.compile(r"<!-- br-ad:(intro|prefaq) -->.*?<!-- /br-ad -->\n?", re.S)
AD_CSS_MARK = "<!-- br-ad-css -->"
AD_CSS = (AD_CSS_MARK + "<style>.br-ad{margin:30px 0;padding-top:10px;border-top:1px solid var(--rule,#d8d0bd);"
          "min-height:120px;}.br-ad-label{font-family:var(--mono,ui-monospace,monospace);font-size:10.5px;"
          "letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mute,#6b665e);margin-bottom:8px;}"
          # AdSense marks a slot it could not fill; drop the whole labeled box, not just the ad.
          '.br-ad:has(ins[data-ad-status="unfilled"]){display:none;}</style>\n')


def unit(c, name, slot):
    return (f'<!-- br-ad:{name} --><div class="br-ad" role="complementary" aria-label="Advertisement">'
            f'<div class="br-ad-label">Advertisement</div>'
            f'<ins class="adsbygoogle" style="display:block;text-align:center;" data-ad-layout="in-article" '
            f'data-ad-format="fluid" data-ad-client="{c}" data-ad-slot="{slot}"></ins>'
            f'<script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script></div><!-- /br-ad -->\n')


def anchors(s):
    """(intro_pos, prefaq_pos) inside the article body, either may be None.

    intro  = before the 2nd <h2> (after the first full section - works whether a page opens
             with a TL;DR card, a table or prose).
    prefaq = before the FAQ <h2>; with no FAQ, before the last <h2> if >= 2 sections separate it
             from the intro unit. A unit never sits straight after a ZIP box (.rz-zip): it moves
             to the next <h2>.
    """
    b = s.find('<div class="article-body">')
    if b < 0:
        return None, None
    end = s.find("<footer", b)
    end = len(s) if end < 0 else end
    h2 = [m.start() for m in re.finditer(r"<h2[\s>]", s[b:end])]
    h2 = [b + x for x in h2]

    def clear(pos):
        """False only when a ZIP box is the block directly before this heading."""
        tail = s[b:pos]
        z = tail.rfind('<div class="rz-zip"')
        if z < 0:
            return True
        return bool(re.search(r"<(p|h[1-6]|table|ul|ol|blockquote|section)[\s>]", tail[z:]))

    def first_clear(cands):
        for pos in cands:
            if clear(pos):
                return pos
        return None

    intro = first_clear(h2[1:]) if len(h2) >= 2 else None
    m = re.search(r"<h2[^>]*>\s*(?:<[^>]+>\s*)*Frequently asked questions", s[b:end])
    if m:
        pre = b + m.start()
        pre = pre if clear(pre) else None
    else:
        later = [x for x in h2 if intro is not None and x > intro]
        pre = later[-1] if len(later) >= 3 and clear(later[-1]) else None
    if pre is not None and intro is not None and pre <= intro:
        pre = None
    return intro, pre


def place_units(s, c, sl):
    s = UNIT_RX.sub("", s)                     # idempotent: strip ours, re-place fresh
    if not sl:
        return s.replace(AD_CSS, "")
    intro, pre = anchors(s)
    ins = []
    if intro is not None and "intro" in sl:
        ins.append((intro, unit(c, "intro", sl["intro"])))
    if pre is not None and "prefaq" in sl:
        ins.append((pre, unit(c, "prefaq", sl["prefaq"])))
    for pos, blk in sorted(ins, reverse=True):
        s = s[:pos] + blk + s[pos:]
    if ins and AD_CSS_MARK not in s:
        i = s.index("</head>")
        s = s[:i] + AD_CSS + s[i:]
    if not ins:
        s = s.replace(AD_CSS, "")
    return s


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
            t = UNIT_RX.sub("", t).replace(AD_CSS, "")
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
    sl = slots()
    nu = Counter()
    for p, rel in pages():
        s0 = p.read_text(encoding="utf-8")
        if MARK not in s0:
            continue
        s1 = place_units(s0, c, sl)
        nu["intro"] += s1.count("<!-- br-ad:intro -->")
        nu["prefaq"] += s1.count("<!-- br-ad:prefaq -->")
        if s1 != s0:
            p.write_text(s1, encoding="utf-8")
    print(f"in-article units: {dict(nu) or 'none (no slot ids in adsense.json)'}")
    pub = c.replace("ca-", "")
    (ROOT / "ads.txt").write_text(f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    print(f"patched {len(todo)} pages; wrote ads.txt")


if __name__ == "__main__":
    main()
