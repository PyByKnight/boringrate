#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Point every footer "Contact" link at /contact.html instead of a bare mailto.

The footer is copied into pages by many generators/templates, so this runs as a rebuild step
after them. Only an <a> whose TEXT is exactly "Contact" changes; hello@boringrate.com links in
body copy stay as they are. Added 2026-11-17 (AdSense review: a real contact page).

    python3 patch_contact_link.py            # dry run
    python3 patch_contact_link.py --apply
"""
import pathlib, sys

ROOT = pathlib.Path(__file__).parent
OLD = '<a href="mailto:hello@boringrate.com">Contact</a>'
NEW = '<a href="/contact.html">Contact</a>'
SKIP_DIRS = {"_serff", "_umami", "_gsc", "node_modules", "partials", ".git", "__pycache__"}

n = 0
for p in sorted(ROOT.rglob("*.html")):
    if set(p.relative_to(ROOT).parts) & SKIP_DIRS:
        continue
    s = p.read_text(encoding="utf-8")
    if OLD in s:
        n += 1
        if "--apply" in sys.argv:
            p.write_text(s.replace(OLD, NEW), encoding="utf-8")
print(f"contact link: {n} pages {'patched' if '--apply' in sys.argv else 'to patch (dry run)'}")
