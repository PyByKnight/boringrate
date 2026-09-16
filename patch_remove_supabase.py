#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove the live Supabase email-capture / auth integration from the three tool pages.

Owner decision (2026-09-16): Supabase isn't in active use, and email capture isn't worth
running at current traffic. May return later — git history is the restore path
(this commit's parent has the full working implementation).

Unlike the dead `.article-email` markup stripped in 21cd3734, this code WORKS: it's a
Supabase Auth magic-link (OTP) flow with profile sync to a `profiles` table. What goes:
  index.html          header "Notify me" panel + sign-in/sign-out, the email-capture module,
                      and a 9,017-char contiguous JS region (syncToSupabase, loadFromSupabase,
                      updateAuthUI, showToast, renderProfileDetails, auth handlers)
  renters/index.html  config block + email-capture JS + the email section markup
  home/index.html     a self-contained <script> block (verified: supabase only) + markup
  all three           the @supabase/supabase-js CDN <script src> tag

What STAYS: all localStorage persistence (PROFILE_KEY, br_notify). It is local-only, needs no
account, and survives independently — index.html's sole coupling was one line,
`if (currentUser) syncToSupabase();`, removed here.

SAFETY (CLAUDE.md): for index.html and renters/index.html the JS is excised BY MARKER from
inside larger shared <script> blocks — the surrounding block is left intact, never rewritten.
home/index.html is the one case where a whole <script> element is removed, and only after
verifying it contains nothing but the Supabase code. Every span is verified present before any
write; a file whose markers don't all match is skipped whole, never partially transformed.

  python3 patch_remove_supabase.py --dry
  python3 patch_remove_supabase.py
"""
import re, sys

DRY = '--dry' in sys.argv

CDN = re.compile(r'\n?<script src="https://cdn\.jsdelivr\.net/npm/@supabase/supabase-js@2[^"]*"></script>')


def div_span(s, start_marker):
    """(start, end) of the balanced <div> element beginning at start_marker."""
    i = s.find(start_marker)
    if i < 0:
        return None
    depth = 0
    for m in re.finditer(r'<div\b[^>]*>|</div>', s[i:]):
        depth += -1 if m.group(0).startswith('</') else 1
        if depth == 0:
            return (i, i + m.end())
    return None


def text_span(s, start_marker, end_marker):
    """(start, end) from start_marker up to (not including) end_marker."""
    i = s.find(start_marker)
    if i < 0:
        return None
    j = s.find(end_marker, i)
    if j < 0:
        return None
    return (i, j)


def script_span(s, inner_marker):
    """(start, end) of the whole <script> element containing inner_marker."""
    i = s.find(inner_marker)
    if i < 0:
        return None
    a = s.rfind('<script>', 0, i)
    b = s.find('</script>', i)
    if a < 0 or b < 0:
        return None
    return (a, b + len('</script>'))


PLAN = {
    'index.html': [
        ('markup: header auth (signed-out)', lambda s: div_span(s, '<div id="headerAuthOut">')),
        ('markup: header auth (signed-in)',  lambda s: div_span(s, '<div id="headerAuthIn"')),
        ('markup: email-capture module',     lambda s: div_span(s, '<div class="email-capture">')),
        ('js: supabase auth region',         lambda s: text_span(s, '// ── Supabase auth ─', '// ── Refine bar toggle ─')),
        ('js: lone syncToSupabase call',     lambda s: text_span(s, '\n    if (currentUser) syncToSupabase();', '\n  } catch(e) {}')),
    ],
    'renters/index.html': [
        ('markup: email section',  lambda s: div_span(s, '<div class="email-section" id="emailSection"')),
        ('js: email capture',      lambda s: text_span(s, '// ── Supabase email capture ──', '// ── Pill refinement handlers ──')),
        ('js: config',             lambda s: text_span(s, '// ── Supabase ──', '// ── ZIP → state lookup ──')),
    ],
    'home/index.html': [
        ('markup: email section',  lambda s: div_span(s, '<div class="email-section" id="emailSection"')),
        ('js: whole supabase block', lambda s: script_span(s, '// Supabase email capture')),
    ],
}


def main():
    total = 0
    for path, steps in PLAN.items():
        s = open(path, encoding='utf-8').read()
        orig = s
        spans, ok = [], True
        for label, fn in steps:
            sp = fn(s)
            if sp is None:
                print(f'  {path}: MARKER NOT FOUND — {label}  (file skipped)')
                ok = False
                break
            spans.append((sp, label))
        if not ok:
            continue

        # sanity: no span may overlap another
        flat = sorted(sp for sp, _ in spans)
        for (a1, b1), (a2, b2) in zip(flat, flat[1:]):
            if b1 > a2:
                print(f'  {path}: OVERLAPPING SPANS — skipped')
                ok = False
        if not ok:
            continue

        print(f'\n{path}')
        for (a, b), label in spans:
            print(f'   -{b - a:>6} chars  {label}')
        # highest offset first so earlier offsets stay valid
        for (a, b), _ in sorted(spans, reverse=True):
            s = s[:a] + s[b:]
        s, n = CDN.subn('', s)
        print(f'   -{n} supabase CDN tag')

        if not DRY and s != orig:
            open(path, 'w', encoding='utf-8').write(s)
        total += len(orig) - len(s)

    print(f'\n{"would remove" if DRY else "removed"}: {total:,} chars across {len(PLAN)} pages')
    if DRY:
        print('dry run — re-run without --dry to apply')


if __name__ == '__main__':
    main()
