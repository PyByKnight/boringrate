#!/usr/bin/env python3
"""Insert the newly-added metros into the nav mega-menu metro list across every page.

The metro list (`<div class="nav-res-metros">...</div>`) is identical on all 414
pages and alphabetical by display name. We parse the existing links, merge in the
new metros, re-sort, and rewrite the div everywhere. Idempotent (re-sorting an
already-complete list is a no-op).
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
DIV_RE = re.compile(r'<div class="nav-res-metros">(.*?)</div>', re.DOTALL)
LINK_RE = re.compile(r'<a href="(/article/metro/[^"]+)">([^<]+)</a>')

NEW = {
    "/article/metro/akron.html": "Akron",
    "/article/metro/allentown.html": "Allentown",
    "/article/metro/asheville.html": "Asheville",
    "/article/metro/chattanooga.html": "Chattanooga",
    "/article/metro/colorado-springs.html": "Colorado Springs",
    "/article/metro/dayton.html": "Dayton",
    "/article/metro/grand-rapids.html": "Grand Rapids",
    "/article/metro/lexington.html": "Lexington",
    "/article/metro/pensacola.html": "Pensacola",
    "/article/metro/reno.html": "Reno",
    "/article/metro/savannah.html": "Savannah",
    "/article/metro/worcester.html": "Worcester",
}


def build_list(sample_html):
    m = DIV_RE.search(sample_html)
    pairs = dict(LINK_RE.findall(m.group(1)))  # href -> name (existing)
    pairs.update(NEW)
    links = sorted(pairs.items(), key=lambda kv: kv[1].lower())
    inner = "".join(f'<a href="{href}">{name}</a>' for href, name in links)
    return '<div class="nav-res-metros">' + inner + "</div>", len(links)


def main():
    pages = [p for p in ROOT.rglob("*.html") if DIV_RE.search(p.read_text(encoding="utf-8"))]
    if not pages:
        print("no pages with metro nav found")
        return
    new_div, n = build_list(pages[0].read_text(encoding="utf-8"))
    changed = 0
    for p in pages:
        html = p.read_text(encoding="utf-8")
        new_html = DIV_RE.sub(lambda _: new_div, html, count=1)
        if new_html != html:
            p.write_text(new_html, encoding="utf-8")
            changed += 1
    print(f"{n} metros in list · {changed}/{len(pages)} pages updated")


if __name__ == "__main__":
    main()
