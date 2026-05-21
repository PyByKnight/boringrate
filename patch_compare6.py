#!/usr/bin/env python3
"""Patch compare pages (pass 6):
1. "Clear" button → "Clear profile"
2. Remove cmp-verdict block and "Side-by-side comparison" h2
3. Add "Hide profile" button at bottom of form
4. Add CSS for pb-col-winner, pb-best-badge, pb-muted, pb-bottom-close
"""
import os, re, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

NEW_CSS = """
  .cmp-table th.pb-col-winner{color:#1a7a3c;position:relative;}
  .cmp-table th.pb-col-winner::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:#1a7a3c;}
  .pb-best-badge{display:block;font-family:var(--mono);font-size:10px;letter-spacing:0.04em;color:#1a7a3c;font-weight:400;margin-top:3px;}
  .cmp-table .pb-muted{opacity:0.22;transition:opacity 150ms;}
  .pb-bottom-close{margin-top:14px;padding-top:14px;border-top:1px solid var(--rule);text-align:right;}"""

OLD_CLEAR_BTN = '>Clear</button>'
NEW_CLEAR_BTN = '>Clear profile</button>'

OLD_PB_RESULT_END = (
    '        <div id="pbShoppingNote" class="pb-shopping-note" style="display:none;"></div>\n'
    '      </div>\n'
    '    </div>'
)
NEW_PB_RESULT_END = (
    '        <div id="pbShoppingNote" class="pb-shopping-note" style="display:none;"></div>\n'
    '      </div>\n'
    '      <div class="pb-bottom-close">\n'
    '        <button type="button" class="pb-summary-toggle open" id="pbCloseBottom">Hide profile &#9650;</button>\n'
    '      </div>\n'
    '    </div>'
)

# Matches verdict block + the h2 that follows it
VERDICT_RE = re.compile(
    r'\s*<div class="cmp-verdict">.*?</div>\s*<h2>Side-by-side comparison</h2>',
    re.DOTALL
)


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    # 1. Add CSS
    if 'pb-col-winner' not in html:
        html = html.replace('\n</style>', NEW_CSS + '\n</style>', 1)

    # 2. "Clear" → "Clear profile"
    html = html.replace(OLD_CLEAR_BTN, NEW_CLEAR_BTN)

    # 3. Remove verdict + h2
    html = VERDICT_RE.sub('\n\n    ', html, count=1)

    # 4. Add bottom close button
    html = html.replace(OLD_PB_RESULT_END, NEW_PB_RESULT_END, 1)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


files = sorted(glob.glob(os.path.join(COMPARE_DIR, '*.html')))
files = [f for f in files if not f.endswith('/index.html')]

patched = skipped = 0
for f in files:
    if patch_file(f):
        patched += 1
    else:
        skipped += 1
        print(f'SKIPPED: {os.path.basename(f)}')

print(f'\nDone: {patched} patched, {skipped} unchanged out of {len(files)} files.')
