#!/usr/bin/env python3
"""Add Twitter Card meta tags (mirrored from existing Open Graph tags) to every
page that already has an OG block, and backfill og:image where missing.

Why: shared links currently render as plain previews. `twitter:card =
summary_large_image` + mirrored title/description/image upgrades previews on X
and the many scrapers that read twitter:* before falling back to og:*.

Idempotent: skips files that already have twitter:card. Surgical inserts only —
no <script>/<style> block rewrites (CLAUDE.md safety rule).
"""
import pathlib
import re

BASE = pathlib.Path(__file__).parent
DEFAULT_IMG = "https://boringrate.com/og-default.png"

RE_OG_TITLE = re.compile(r'<meta property="og:title" content="([^"]*)"\s*/?>')
RE_OG_DESC = re.compile(r'<meta property="og:description" content="([^"]*)"\s*/?>')
RE_OG_IMAGE_LINE = re.compile(r'[ \t]*<meta property="og:image" content="([^"]*)"\s*/?>\n?')
RE_OG_TITLE_LINE = re.compile(r'([ \t]*)<meta property="og:title" content="[^"]*"\s*/?>\n?')


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;') if s else s


def twitter_block(indent, title, desc, image):
    t = indent
    return (
        f'{t}<meta name="twitter:card" content="summary_large_image" />\n'
        f'{t}<meta name="twitter:title" content="{title}" />\n'
        f'{t}<meta name="twitter:description" content="{desc}" />\n'
        f'{t}<meta name="twitter:image" content="{image}" />\n'
    )


changed = skipped = noog = img_added = 0
for path in sorted(BASE.rglob("*.html")):
    html = path.read_text(encoding="utf-8")
    if "twitter:card" in html:
        skipped += 1
        continue
    mt = RE_OG_TITLE.search(html)
    if not mt:
        noog += 1
        continue
    title = mt.group(1)
    md = RE_OG_DESC.search(html)
    desc = md.group(1) if md else ""

    # Ensure og:image exists; capture its value + the indent used by og:title.
    mi = RE_OG_IMAGE_LINE.search(html)
    indent_m = RE_OG_TITLE_LINE.search(html)
    indent = indent_m.group(1) if indent_m else ""
    if mi:
        image = mi.group(1)
    else:
        image = DEFAULT_IMG
        # insert og:image right after the og:title line
        html = RE_OG_TITLE_LINE.sub(
            lambda m: m.group(0) + f'{indent}<meta property="og:image" content="{DEFAULT_IMG}" />\n',
            html, count=1)
        img_added += 1
        mi = RE_OG_IMAGE_LINE.search(html)

    block = twitter_block(indent, title, desc, image)
    # insert the twitter block immediately after the og:image line
    html = RE_OG_IMAGE_LINE.sub(lambda m: m.group(0) + block, html, count=1)

    path.write_text(html, encoding="utf-8")
    changed += 1

print(f"{changed} patched ({img_added} og:image backfilled), {skipped} already had twitter, {noog} had no og:title (skipped)")
