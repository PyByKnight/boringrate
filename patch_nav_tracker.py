#!/usr/bin/env python3
"""Add the Rate Change Tracker link to the Guides nav panel (#res-guides) site-wide.
Idempotent: skips pages that already have the link."""
import pathlib

ROOT = pathlib.Path(__file__).parent
ANCHOR = 'id="res-guides">'
LINK = '<a href="/article/rate-changes/">2026 Rate Change Tracker &mdash; Who Raised, Who Cut</a>'

changed = skipped = 0
for p in ROOT.rglob("*.html"):
    h = p.read_text(encoding="utf-8")
    if ANCHOR not in h:
        continue
    if "/article/rate-changes/" in h.split(ANCHOR, 1)[1][:400]:
        skipped += 1
        continue
    h = h.replace(ANCHOR, ANCHOR + LINK, 1)
    p.write_text(h, encoding="utf-8")
    changed += 1

print(f"{changed} pages updated, {skipped} already had the link")
