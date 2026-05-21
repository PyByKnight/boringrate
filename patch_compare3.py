#!/usr/bin/env python3
"""Patch compare pages (pass 3):
1. Add pb-summary bar (general rates + customize toggle) above the profile builder
2. Collapse the profile builder by default (display:none)
3. Add CSS for pb-summary elements
"""
import os, re, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

NEW_CSS = """
  .pb-summary{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 18px;border:1px solid var(--rule);background:var(--paper-deep);max-width:660px;margin:0 0 12px;flex-wrap:wrap;}
  .pb-summary-left{display:flex;flex-direction:column;gap:2px;}
  .pb-summary-label{font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);}
  .pb-summary-rates{font-family:var(--serif);font-size:16px;font-weight:500;letter-spacing:-0.01em;color:var(--ink);}
  .pb-summary-toggle{font-family:var(--mono);font-size:11px;letter-spacing:0.06em;text-transform:uppercase;background:none;border:1px solid var(--rule);padding:8px 14px;cursor:pointer;color:var(--ink-soft);white-space:nowrap;transition:all 120ms;flex-shrink:0;}
  .pb-summary-toggle:hover,.pb-summary-toggle.open{border-color:var(--ink);color:var(--ink);}"""


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # 1. Add CSS for summary bar (only if not already present)
    if 'pb-summary' not in html:
        html = html.replace('\n</style>', NEW_CSS + '\n</style>', 1)

    # 2. Insert pb-summary div between <h2> and <div class="profile-builder">
    #    and set display:none on the profile-builder
    OLD_H2_BUILDER = '<h2>Who wins for your profile?</h2>\n    <div class="profile-builder" id="profileBuilder">'
    NEW_H2_BUILDER = '''<h2>Who wins for your profile?</h2>
    <div class="pb-summary" id="pbSummary">
      <div class="pb-summary-left">
        <div class="pb-summary-label" id="pbSummaryLabel">General rates</div>
        <div class="pb-summary-rates" id="pbSummaryRates"></div>
      </div>
      <button type="button" class="pb-summary-toggle" id="pbCustomizeBtn">Customize for your profile &#9662;</button>
    </div>
    <div class="profile-builder" id="profileBuilder" style="display:none;">'''

    html = html.replace(OLD_H2_BUILDER, NEW_H2_BUILDER)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


files = sorted(glob.glob(os.path.join(COMPARE_DIR, "*.html")))
files = [f for f in files if not f.endswith('/index.html')]

patched = skipped = 0
for f in files:
    if patch_file(f):
        patched += 1
    else:
        skipped += 1
        print(f"SKIPPED: {os.path.basename(f)}")

print(f"\nDone: {patched} patched, {skipped} unchanged.")
