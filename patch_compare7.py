#!/usr/bin/env python3
"""Patch compare pages (pass 7):
1. Remove <div class="zip-embed">...</div> block
2. Add CSS for pb-why section
"""
import os, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

NEW_CSS = """
  .pb-why{display:flex;gap:40px;flex-wrap:wrap;margin:40px 0 32px;padding-top:32px;border-top:1px solid var(--rule);}
  .pb-why-col{flex:1;min-width:240px;}
  .pb-why-kicker{font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);margin:0 0 6px;}
  .pb-why-name{font-family:var(--serif);font-size:20px;font-weight:500;margin:0 0 14px;color:var(--ink);letter-spacing:-0.01em;}
  .pb-why-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px;}
  .pb-why-item{font-size:13px;line-height:1.55;color:var(--ink-soft);padding-left:18px;position:relative;}
  .pb-why-item::before{content:'—';position:absolute;left:0;color:var(--accent);}"""


def remove_zip_embed(html):
    """Remove the zip-embed div using depth counting to find its closing tag."""
    marker = '\n\n    <div class="zip-embed">'
    start = html.find(marker)
    if start == -1:
        return html
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return html[:start] + html[i + 6:]
            i += 6
        else:
            i += 1
    return html  # fallback: no change if matching close not found


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    if 'pb-why' not in html:
        html = html.replace('\n</style>', NEW_CSS + '\n</style>', 1)

    html = remove_zip_embed(html)

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
