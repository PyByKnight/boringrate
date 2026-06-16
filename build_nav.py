#!/usr/bin/env python3
# Single-source nav: stamp partials/nav-mega.html into every page's <div class="nav-mega">
# region. Edit the partial once, run this, and the mega menu updates everywhere (and any
# drifted variants get re-unified). The nav stays in static HTML (good for SEO crawl).
import os, re
PART = open("partials/nav-mega.html", encoding="utf-8").read().strip()
RE = re.compile(r'<div class="nav-mega" id="navMega">.*?</div></div>(?=\s*</header>)', re.S)
n = changed = 0
for root, _, files in os.walk("."):
    if "/.git" in root: continue
    for fn in files:
        if not fn.endswith(".html"): continue
        p = os.path.join(root, fn)
        s = open(p, encoding="utf-8").read()
        if not RE.search(s): continue
        n += 1
        s2 = RE.sub(lambda _m: PART, s, count=1)
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2); changed += 1
print(f"pages with nav-mega: {n} | updated: {changed}")
