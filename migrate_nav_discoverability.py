#!/usr/bin/env python3
# Global-nav discoverability: make all three rate tools + all three coverage
# calculators reachable from every page. Idempotent; safe to re-run.
#  R1  Product dropdown: dimmed "Home soon" -> real /home/ link.
#  R2  Tools dropdown: single auto Coverage Calculator -> Auto/Renters/Home
#      (SCOPED to the dropdown panel so the footer copy is never touched).
#  R3  Mega-menu Tools section: same 3 coverage calculators (uniform literal).
import os

R1_OLD = '<span class="nav-dd-panel-dim">Home<span class="nav-dd-soon">soon</span></span>'
R1_NEW = '<a href="/home/index.html">Home</a>'

R3_OLD = ('<a href="/coverage.html" class="nav-tool"><span class="nav-tool-name">Coverage Calculator</span>'
          '<span class="nav-tool-desc">Find the right coverage level</span></a>')
R3_NEW = ('<a href="/coverage.html" class="nav-tool"><span class="nav-tool-name">Auto Coverage Calculator</span>'
          '<span class="nav-tool-desc">Find the right coverage level</span></a>'
          '<a href="/renters/coverage.html" class="nav-tool"><span class="nav-tool-name">Renters Coverage Calculator</span>'
          '<span class="nav-tool-desc">How much renters coverage you need</span></a>'
          '<a href="/home/coverage.html" class="nav-tool"><span class="nav-tool-name">Home Coverage Calculator</span>'
          '<span class="nav-tool-desc">Dwelling, liability &amp; add-ons</span></a>')

R2_NEW = ('<a href="/coverage.html">Auto Coverage Calculator</a>'
          '<a href="/renters/coverage.html">Renters Coverage Calculator</a>'
          '<a href="/home/coverage.html">Home Coverage Calculator</a>')
R2_DROPDOWN_MARKER = 'renters/coverage.html">Renters Coverage Calculator'  # idempotency guard

def migrate(s):
    changed = False
    if R1_OLD in s:
        s = s.replace(R1_OLD, R1_NEW); changed = True
    if R3_OLD in s and 'renters/coverage.html" class="nav-tool"' not in s:
        s = s.replace(R3_OLD, R3_NEW); changed = True
    if R2_DROPDOWN_MARKER not in s:
        k = s.find('navDdToolsPanel">')
        if k >= 0:
            for old in ['<a href="/coverage.html" class="active">Coverage Calculator</a>',
                        '<a href="/coverage.html">Coverage Calculator</a>']:
                j = s.find(old, k)
                if 0 <= j < k + 800:
                    s = s[:j] + R2_NEW + s[j + len(old):]; changed = True
                    break
    return s, changed

n = 0
for root, _, files in os.walk("."):
    if "/.git" in root:
        continue
    for fn in files:
        if not fn.endswith(".html"):
            continue
        p = os.path.join(root, fn)
        s = open(p, encoding="utf-8").read()
        s2, ch = migrate(s)
        if ch:
            open(p, "w", encoding="utf-8").write(s2); n += 1
print("migrated", n, "files")
