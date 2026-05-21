#!/usr/bin/env python3
"""Fix nav on all 51 state pages:
- Replace old nav-mega HTML using </header> as the end boundary (avoids depth-count
  failure caused by malformed HTML in the old nav structure).
- Replace old hamburger JS.
- Replace old nav-mega-inner grid CSS with new block CSS.
"""
import os, glob
from patch_nav_redesign import build_nav_mega, NEW_NAV_CSS, NEW_NAV_CSS_MOBILE, NEW_HAMBURGER_JS

STATE_DIR = "/home/knighttyler/boringrate/article/state"

NAV_START = '<div class="nav-mega" id="navMega">'
HEADER_END = '</header>'
OLD_JS_MARKER = 'data-mega-toggle'  # only in old hamburger JS after nav HTML is replaced

NEW_JS = NEW_HAMBURGER_JS

# Old CSS that the state pages still have (injected from previous partial runs)
OLD_TOOL_CSS_LINE = '.nav-tool{display:flex;flex-direction:column;gap:3px;padding:11px 14px;text-decoration:none;flex:1;min-width:150px;background:rgba(246,241,232,0.04);border:1px solid rgba(246,241,232,0.08);transition:background 120ms;}'
NEW_TOOL_CSS_LINE = '.nav-tool{display:flex;flex-direction:column;gap:3px;padding:11px 14px;text-decoration:none;color:var(--paper);flex:1;min-width:150px;background:rgba(246,241,232,0.04);border:1px solid rgba(246,241,232,0.08);transition:background 120ms;}'


def patch_file(path, new_nav):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    # 1. Replace nav HTML using </header> boundary
    nav_start = html.find(NAV_START)
    header_end = html.find(HEADER_END, nav_start) if nav_start != -1 else -1
    if nav_start != -1 and header_end != -1:
        html = html[:nav_start] + new_nav + '\n' + html[header_end:]

    # 2. Replace old hamburger JS (now data-mega-toggle only appears in JS)
    m = html.find(OLD_JS_MARKER)
    if m != -1:
        script_start = html.rfind('<script>', 0, m)
        script_end = html.find('</script>', m)
        if script_start != -1 and script_end != -1:
            html = html[:script_start] + NEW_JS + html[script_end + 9:]

    # 3. Ensure CSS has color on .nav-tool (fix old partial injection)
    html = html.replace(OLD_TOOL_CSS_LINE, NEW_TOOL_CSS_LINE)

    # 4. If CSS block missing entirely, add it
    if '.nav-section-label{' not in html:
        html = html.replace('\n</style>', NEW_NAV_CSS + NEW_NAV_CSS_MOBILE + '\n</style>', 1)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


files = sorted(glob.glob(os.path.join(STATE_DIR, '*.html')))
new_nav = build_nav_mega()

patched = skipped = 0
for path in files:
    if patch_file(path, new_nav):
        patched += 1
    else:
        skipped += 1
        print(f'SKIPPED: {os.path.basename(path)}')

print(f'\nDone: {patched} patched, {skipped} unchanged out of {len(files)} files.')
