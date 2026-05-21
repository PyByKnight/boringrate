#!/usr/bin/env python3
"""Patch compare pages (pass 4):
1. Move profile section (summary + form) to top of article-body, before verdict
2. ZIP first in form (pb-extra-row becomes first child of profile-builder)
3. Move CTAs out of form → standalone section after comparison table
4. Add Clear button to summary bar
5. Add muted-pill CSS (has-selection class)
6. Fix pb-extra-row border direction (now leads the form, not follows)
"""
import os, re, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

NEW_CSS = """
  .pb-summary-right{display:flex;align-items:center;gap:8px;flex-shrink:0;}
  .pb-clear-btn{font-family:var(--mono);font-size:11px;letter-spacing:0.06em;text-transform:uppercase;background:none;border:1px solid var(--rule);padding:7px 12px;cursor:pointer;color:var(--ink-mute);white-space:nowrap;transition:all 120ms;}
  .pb-clear-btn:hover{border-color:var(--accent);color:var(--accent);}
  .pb-pills.has-selection .pb-pill:not(.active){opacity:0.3;color:var(--ink-mute);}
  .pb-standalone-actions{display:flex;gap:12px;flex-wrap:wrap;max-width:660px;margin:0 0 36px;}"""

OLD_TOGGLE = (
    '      <button type="button" class="pb-summary-toggle" id="pbCustomizeBtn">'
    'Customize for your profile &#9662;</button>\n    </div>'
)
NEW_TOGGLE = (
    '      <div class="pb-summary-right">\n'
    '        <button type="button" class="pb-summary-toggle" id="pbCustomizeBtn">'
    'Customize for your profile &#9662;</button>\n'
    '        <button type="button" class="pb-clear-btn" id="pbClearBtn" style="display:none;">Clear</button>\n'
    '      </div>\n    </div>'
)

# The pb-actions block inside the profile-builder (to be removed from there)
OLD_ACTIONS_IN_FORM = (
    '      <div class="pb-actions">\n'
    '        <a href="/" class="pb-cta" id="pbCta">Compare all carriers for your profile &rarr;</a>\n'
    '        <a href="/article/compare/index.html" class="pb-cta pb-cta-alt">Return to Compare Hub &rarr;</a>\n'
    '      </div>\n    </div>'
)
CLOSE_BUILDER_ONLY = '    </div>'

# Standalone CTAs that go after the table
STANDALONE_ACTIONS = (
    '    <div class="pb-standalone-actions">\n'
    '      <a href="/" class="pb-cta" id="pbCta">Compare all carriers for your profile &rarr;</a>\n'
    '      <a href="/article/compare/index.html" class="pb-cta pb-cta-alt">Return to Compare Hub &rarr;</a>\n'
    '    </div>'
)

PROFILE_START_MARKER  = '\n\n    <a href="/article/compare/index.html" class="hub-back">Compare hub</a>'
BEFORE_ZIP_MARKER     = '\n\n    <div class="zip-embed">'
ARTICLE_BODY_VERDICT  = '  <div class="article-body">\n\n    <div class="cmp-verdict">'


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    # ── 1. Add CSS ─────────────────────────────────────────────────────────────
    if 'pb-clear-btn' not in html:
        html = html.replace('\n</style>', NEW_CSS + '\n</style>', 1)

    # Fix pb-extra-row: was bottom separator, now top of form → use bottom border
    html = html.replace(
        '.pb-extra-row{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0 0;padding-top:14px;border-top:1px solid var(--rule);}',
        '.pb-extra-row{display:flex;gap:16px;flex-wrap:wrap;margin:0 0 14px;padding-bottom:14px;border-bottom:1px solid var(--rule);}'
    )

    # ── 2. Add Clear button to summary bar ────────────────────────────────────
    html = html.replace(OLD_TOGGLE, NEW_TOGGLE)

    # ── 3. Remove pb-actions from inside profile-builder ──────────────────────
    html = html.replace(OLD_ACTIONS_IN_FORM, CLOSE_BUILDER_ONLY)

    # ── 4. Move pb-extra-row to first position inside profile-builder ─────────
    EXTRA_ROW_OPEN  = '\n      <div class="pb-extra-row">'
    PB_RESULT_OPEN  = '\n      <div class="pb-result"'
    BUILDER_OPEN    = '<div class="profile-builder" id="profileBuilder" style="display:none;">'

    er_start = html.find(EXTRA_ROW_OPEN)
    er_end   = html.find(PB_RESULT_OPEN)
    bo_idx   = html.find(BUILDER_OPEN)

    if -1 not in (er_start, er_end, bo_idx) and bo_idx < er_start < er_end:
        extra_row_block = html[er_start:er_end]   # '\n      <div class="pb-extra-row">...'
        html_no_er = html[:er_start] + html[er_end:]
        # builder position unchanged (it's before the removed block)
        bo_idx2 = html_no_er.find(BUILDER_OPEN) + len(BUILDER_OPEN)
        html = html_no_er[:bo_idx2] + extra_row_block + html_no_er[bo_idx2:]

    # ── 5. Move profile section to top of article-body ────────────────────────
    ps_idx = html.find(PROFILE_START_MARKER)
    bz_idx = html.find(BEFORE_ZIP_MARKER)
    ab_idx = html.find(ARTICLE_BODY_VERDICT)

    if -1 not in (ps_idx, bz_idx, ab_idx) and ab_idx < ps_idx < bz_idx:
        profile_section = html[ps_idx:bz_idx]   # '\n\n    <a href=...>...(entire block)</div>'

        # Remove from between table and zip-embed
        html_no_prof = html[:ps_idx] + html[bz_idx:]

        # Locate article-body again (unchanged) and insert profile section after opening line
        ab_idx2 = html_no_prof.find(ARTICLE_BODY_VERDICT)
        if ab_idx2 != -1:
            after_open = ab_idx2 + len('  <div class="article-body">\n')
            html = (html_no_prof[:after_open]
                    + '\n' + profile_section.strip() + '\n\n    '
                    + html_no_prof[after_open:])

    # ── 6. Insert standalone CTAs before zip-embed ────────────────────────────
    bz_idx2 = html.find(BEFORE_ZIP_MARKER)
    if bz_idx2 != -1 and 'pb-standalone-actions' not in html:
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
