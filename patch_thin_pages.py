#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keep templated near-duplicate pages out of Google's index (and out of the sitemap).

Why (2026-11-17): AdSense rejected the site for content quality. The metro pages are one
template filled per city - home/metro Akron vs Dayton share 97% of their words - and earned
22 of ~300 search clicks in the 3 months to 2026-10-15 (none above 2). They stay live and
linked (noindex,FOLLOW keeps link equity flowing) but stop counting as site content.

    python3 patch_thin_pages.py            # dry run
    python3 patch_thin_pages.py --apply    # stamp robots meta, drop URLs from sitemap.xml
    python3 patch_thin_pages.py --remove   # undo: strip the meta (re-add sitemap URLs by hand / git)

Runs in rebuild.sh after the generators, so regenerated pages get the tag back.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
THIN_DIRS = ("home/metro", "renters/metro", "article/metro")
MARK = "<!-- br-noindex -->"
TAG = f'{MARK}<meta name="robots" content="noindex,follow">\n'
SITE = "https://boringrate.com/"


def thin_pages():
    for d in THIN_DIRS:
        for p in sorted((ROOT / d).glob("*.html")):
            if p.name == "index.html":      # section hub (gen_section_hubs.py) stays indexable
                continue
            yield p, p.relative_to(ROOT).as_posix()


def main():
    apply, remove = "--apply" in sys.argv, "--remove" in sys.argv
    todo, have = [], 0
    for p, rel in thin_pages():
        s = p.read_text(encoding="utf-8")
        if remove:
            if MARK in s:
                p.write_text(s.replace(TAG, ""), encoding="utf-8"); have += 1
            continue
        if MARK in s:
            have += 1
        elif "</head>" in s:
            todo.append((p, s))
    if remove:
        print(f"removed noindex from {have} pages"); return
    sm = ROOT / "sitemap.xml"
    x = sm.read_text(encoding="utf-8")
    urls = [SITE + rel for _, rel in thin_pages()]
    in_sm = [u for u in urls if f"<loc>{u}</loc>" in x]
    print(f"thin pages: {len(todo)} to tag, {have} already tagged; {len(in_sm)} still in sitemap")
    if not apply:
        print("dry run - re-run with --apply"); return
    for p, s in todo:
        i = s.index("</head>")
        p.write_text(s[:i] + TAG + s[i:], encoding="utf-8")
    for u in in_sm:
        x = re.sub(r"[ \t]*<url><loc>" + re.escape(u) + r"</loc>.*?</url>\n?", "", x, flags=re.S)
    sm.write_text(x, encoding="utf-8")
    print(f"tagged {len(todo)} pages, dropped {len(in_sm)} sitemap URLs")


if __name__ == "__main__":
    main()
