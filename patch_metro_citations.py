#!/usr/bin/env python3
"""Add the Layer-2 'Sources & method' provenance line to metro auto pages that lack it.

Most metro pages predate gen_metro_page.py (built by one-off commits 0a8d13f3 / 7a060f9a /
167bbd4f) and no live generator regenerates them, so build_page's new sources note never
reaches them. This inserts the IDENTICAL note (build_sources_note) via a SAFE insert before
<div class="article-email"> — never replacing a block (CLAUDE.md patch-safety rule).

Idempotent by strip-then-insert: any existing note is removed and the current one reinserted, so
re-running after a wording change refreshes every page (incl. the 12 generator-managed pages).
State + metro name are read from reliable in-body anchors:
  - state slug  <- the relative body link ../../article/state/<slug>.html (unique per page)
  - metro name  <- og:title ("Auto Insurance Rates in <METRO> (2026)" or "<METRO> Car Insurance …")
"""
import pathlib
import re

from gen_metro_page import STATE, build_sources_note

ROOT = pathlib.Path(__file__).parent
METRO_DIR = ROOT / "article" / "metro"
MARKER = '<div class="article-email">'
SENTINEL = "Sources &amp; method"
# matches a previously-inserted note (my own <p>, no JS inside) so re-runs refresh wording
NOTE_RE = re.compile(r'\s*<p style="font-size:13px[^>]*><strong>Sources &amp; method\.</strong>.*?</p>',
                     re.DOTALL)

# state slug -> (code, display name), inverted from the single-source STATE map
SLUG_TO_STATE = {slug: (code, name) for code, (name, slug, _avg) in STATE.items()}


def metro_name(html):
    m = re.search(r'og:title" content="Auto Insurance Rates in (.+?) \(2026\)"', html)
    if m:
        return m.group(1)
    m = re.search(r'og:title" content="(.+?) Car Insurance Rates', html)
    return m.group(1) if m else None


def state_slug(html):
    m = re.search(r'\.\./\.\./article/state/([a-z-]+)\.html', html)
    return m.group(1) if m else None


def main():
    patched = refreshed = failed = 0
    for p in sorted(METRO_DIR.glob("*.html")):
        html = p.read_text(encoding="utf-8")
        slug = state_slug(html)
        metro = metro_name(html)
        if not slug or slug not in SLUG_TO_STATE or not metro or MARKER not in html:
            print(f"  SKIP (unresolved) {p.name}  slug={slug} metro={metro}")
            failed += 1
            continue
        had = SENTINEL in html
        html = NOTE_RE.sub("", html)  # strip any prior note (refresh wording on re-run)
        code, st_name = SLUG_TO_STATE[slug]
        note = build_sources_note(metro, st_name, code, slug)
        # safe insert: place the note immediately before the FIRST article-email block
        html = html.replace(MARKER, f'    {note}\n    {MARKER}', 1)
        p.write_text(html, encoding="utf-8")
        refreshed += had
        patched += not had
    print(f"\nnewly added {patched}, refreshed {refreshed}, unresolved {failed}")


if __name__ == "__main__":
    main()
