#!/usr/bin/env python3
# Single-source nav: stamp the partials into every page so the menu is identical
# everywhere. Edit a partial, run this, commit. Nav stays in static HTML (SEO-safe).
#   partials/nav-top.html  -> the top-bar dropdowns  (<nav class="primary">…</nav>)
#   partials/nav-mega.html -> the hamburger mega menu (<div class="nav-mega">…</div>)
import os, re
TOP  = open("partials/nav-top.html",  encoding="utf-8").read().strip()
MEGA = open("partials/nav-mega.html", encoding="utf-8").read().strip()
RE_TOP  = re.compile(r'<nav class="primary">.*?</nav>', re.S)
RE_MEGA = re.compile(r'<div class="nav-mega" id="navMega">.*?</div></div>(?=\s*</header>)', re.S)
seen = changed = 0
for root, _, files in os.walk("."):
    if "/.git" in root: continue
    for fn in files:
        if not fn.endswith(".html"): continue
        p = os.path.join(root, fn)
        s = open(p, encoding="utf-8").read()
        if 'class="nav-mega"' not in s and '<nav class="primary">' not in s: continue
        seen += 1; o = s
        if RE_TOP.search(s):  s = RE_TOP.sub(lambda _m: TOP, s, count=1)
        if RE_MEGA.search(s): s = RE_MEGA.sub(lambda _m: MEGA, s, count=1)
        if s != o:
            open(p, "w", encoding="utf-8").write(s); changed += 1
print(f"pages seen: {seen} | updated: {changed}")
