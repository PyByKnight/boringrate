#!/usr/bin/env python3
"""Patch compare pages (pass 5):
1. Move profile section to top of article-body (before verdict)
2. Insert standalone CTAs between table and zip-embed
(Fixes pass 4 failures: wrong indentation in PROFILE_START_MARKER,
 and CSS-string false-positive in standalone-actions guard.)
"""
import os, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

# 12-space indentation matches actual generated HTML (table closes, then profile section)
PROFILE_START_MARKER = '\n\n            <a href="/article/compare/index.html" class="hub-back">Compare hub</a>'
BEFORE_ZIP_MARKER    = '\n\n    <div class="zip-embed">'
ARTICLE_BODY_VERDICT = '  <div class="article-body">\n\n    <div class="cmp-verdict">'

STANDALONE_ACTIONS = (
    '    <div class="pb-standalone-actions">\n'
    '      <a href="/" class="pb-cta" id="pbCta">Compare all carriers for your profile &rarr;</a>\n'
    '      <a href="/article/compare/index.html" class="pb-cta pb-cta-alt">Return to Compare Hub &rarr;</a>\n'
    '    </div>'
)


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    ps_idx = html.find(PROFILE_START_MARKER)
    bz_idx = html.find(BEFORE_ZIP_MARKER)
    ab_idx = html.find(ARTICLE_BODY_VERDICT)

    # ── Move profile section to top of article-body ───────────────────────────
    if -1 not in (ps_idx, bz_idx, ab_idx) and ab_idx < ps_idx < bz_idx:
        profile_section = html[ps_idx:bz_idx]

        # Remove from between table and zip-embed
        html_no_prof = html[:ps_idx] + html[bz_idx:]

        # Re-find article-body marker (position unchanged, it's before removed block)
        ab_idx2 = html_no_prof.find(ARTICLE_BODY_VERDICT)
        if ab_idx2 != -1:
            after_open = ab_idx2 + len('  <div class="article-body">\n')
            html = (html_no_prof[:after_open]
                    + '\n' + profile_section.strip() + '\n\n    '
                    + html_no_prof[after_open:])

    # ── Insert standalone CTAs before zip-embed ───────────────────────────────
    # Guard on the actual div attribute (not the CSS selector string)
    bz_idx2 = html.find(BEFORE_ZIP_MARKER)
    if bz_idx2 != -1 and 'class="pb-standalone-actions"' not in html:
        html = html[:bz_idx2] + '\n\n    ' + STANDALONE_ACTIONS + html[bz_idx2:]

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
