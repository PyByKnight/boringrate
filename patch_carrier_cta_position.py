#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Move the SECOND rz-zip CTA below the per-carrier filings table.

WHY. In the 2026-10-28 Umami pull, carrier pages were the most-viewed section on
the site (312 US views) and the worst converting (5.8% reach the tool, against a
13.5% site baseline). CTA placement explains it: patch_carrier_filings.py appends
the "<carrier>'s recent rate filings" section AFTER the CTAs were positioned, so
on the big national-carrier pages that section spans 14%-91% of the body and both
CTAs end up stranded in the top eighth. A reader who scrolls the filings table
passes 77% of the page with no way into the tool.

This does NOT add a third CTA - the two-CTA layout is locked (memory
boringrate-article-cta-template). It relocates CTA #2 to just after the filings
block, which is where the small carrier pages already have it (median 43%).

Idempotent: a page whose CTA #2 already sits after the filings block is skipped.
Strip-then-insert of one self-contained <div>; no script or style block is touched.

  python3 patch_carrier_cta_position.py            # report
  python3 patch_carrier_cta_position.py --apply
"""
import glob, re, sys

BEGIN = "<!-- carrier-filing-record start -->"
END   = "<!-- carrier-filing-record end -->"
RZ    = re.compile(r'<div class="rz-zip">.*?</form></div>', re.S)
# the filings block must dominate the page before moving anything
MIN_SHARE = 0.35

def body_span(s):
    i = s.find('<div class="article-body"')
    j = s.find('<footer')
    return (i, j) if i > 0 and j > i else (None, None)

def process(path, apply=False):
    s = open(path, encoding='utf-8').read()
    if BEGIN not in s or END not in s:
        return None
    i, j = body_span(s)
    if i is None:
        return None
    blen = j - i
    b0, b1 = s.index(BEGIN), s.index(END) + len(END)
    share = (b1 - b0) / blen
    ctas = [m for m in RZ.finditer(s) if i < m.start() < j]
    if len(ctas) < 2 or share < MIN_SHARE:
        return ('skip', share, None, None)
    second = ctas[1]
    if second.start() > b1:                      # already below the filings block
        return ('ok', share, (second.start() - i) / blen, None)
    before = (second.start() - i) / blen
    block = second.group(0)
    out = s[:second.start()] + s[second.end():]  # lift it out
    out = out.replace(END, END + "\n    " + block, 1)   # drop it just after the table
    i2, j2 = body_span(out)
    after = (out.index(block, i2) - i2) / (j2 - i2)
    if apply:
        open(path, 'w', encoding='utf-8').write(out)
    return ('move', share, before, after)

def main():
    apply = '--apply' in sys.argv
    moved = skipped = 0
    for p in sorted(glob.glob('article/carrier/*.html') +
                    glob.glob('home/carrier/*.html') +
                    glob.glob('renters/carrier/*.html')):
        r = process(p, apply)
        if not r:
            continue
        kind, share, before, after = r
        if kind == 'move':
            moved += 1
            print(f"  {p:44} filings {share:4.0%} of body | CTA2 {before:4.0%} -> {after:4.0%}")
        elif kind == 'skip':
            skipped += 1
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {moved} pages repositioned, {skipped} left alone")

if __name__ == '__main__':
    main()
