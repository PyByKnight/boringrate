#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove the dead email-capture block and its dead footer link, sitewide.

WHY: the `.article-email` block (email + ZIP + current carrier + renewal month + "Notify me")
survives on 213 pages, concentrated in the renters/ and home/ trees that the locked CTA rollout
(patch_article_ctas.py) never reached. It is NOT functional: `articleEmailBtn` appears exactly
once per page — markup only, no handler, no endpoint — and `.email-thanks` is display:none with
nothing to reveal it. A visitor fills four fields, clicks, and nothing whatsoever happens.
Separately, the footer "Subscribe -> Rate change alerts" link exists on 425 pages and points at
`#articleEmailForm`, an anchor absent from 239 of them.

This violates the owner's standing no-email-capture rule and is a broken interaction either way.

SAFETY (see CLAUDE.md): this only ever REMOVES two self-contained HTML blocks located by
balanced-div scan. It never rewrites or replaces a <script> block — the incident that wiped JS
across 66 pages came from replacing whole <script> elements. Orphaned `.article-email` CSS is
left in place deliberately: it lives inside shared <style> blocks alongside rules still in use,
and deleting from those is exactly the risky edit this project has been burned by. Dead CSS is
inert; dead form markup is not.

Idempotent. Refuses to write a file whose block boundaries don't scan cleanly.

  python3 patch_strip_dead_email.py --dry
  python3 patch_strip_dead_email.py
"""
import re, sys, glob, os

DRY = '--dry' in sys.argv
# Two variants exist: the common one, and `<div class="article-email" id="articleEmailForm">`
# on article/market-share.html + article/state-rankings.html (different copy, same dead form).
OPEN_RE = re.compile(r'<div class="article-email"(?: id="articleEmailForm")?>')
FOOT_LINK = re.compile(
    r'\s*<div class="foot-col"><h5>Subscribe</h5>'
    r'<a href="#articleEmailForm">[^<]*</a></div>')


def strip_block(html, path):
    """Remove the <div class="article-email"> ... </div> element by balanced-div scan."""
    m0 = OPEN_RE.search(html)
    if not m0:
        return html, False
    i = m0.start()
    depth, j = 0, i
    for m in re.finditer(r'<div\b[^>]*>|</div>', html[i:]):
        if m.group(0).startswith('</'):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            j = i + m.end()
            break
    else:
        print(f'  SKIP (unbalanced divs): {path}')
        return html, None
    block = html[i:j]
    # sanity: the block we matched must actually be the email module, not something nested
    if 'articleEmailInput' not in block or len(block) > 6000:
        print(f'  SKIP (block failed sanity check, {len(block)} chars): {path}')
        return html, None
    # take the preceding whitespace/newline with it
    k = i
    while k > 0 and html[k - 1] in ' \t':
        k -= 1
    if k > 0 and html[k - 1] == '\n':
        k -= 1
    return html[:k] + html[j:], True


def main():
    files = [f for f in glob.glob('**/*.html', recursive=True) if '/.git/' not in f]
    n_form = n_foot = skipped = 0
    for path in sorted(files):
        html = open(path, encoding='utf-8').read()
        orig = html

        html, ok = strip_block(html, path)
        if ok is None:
            skipped += 1
            continue
        if ok:
            n_form += 1

        html, nsub = FOOT_LINK.subn('', html)
        if nsub:
            n_foot += 1

        if html != orig and not DRY:
            open(path, 'w', encoding='utf-8').write(html)

    verb = 'would strip' if DRY else 'stripped'
    print(f'\n{verb}: {n_form} dead email blocks, {n_foot} dead footer links'
          f'{f", {skipped} SKIPPED" if skipped else ""}')
    if DRY:
        print('dry run — re-run without --dry to apply')


if __name__ == '__main__':
    main()
