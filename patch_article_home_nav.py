#!/usr/bin/env python3
"""Replace the old 'Home (soon)' dim span in article nav dropdowns with a live link.

Idempotent: files lacking the old markup are skipped. Surgical string replace —
no <script>/<style> block rewrites (see CLAUDE.md patch safety rule).
"""
import pathlib

ROOT = pathlib.Path(__file__).parent / "article"

OLD = '<span class="nav-dd-panel-dim">Home<span class="nav-dd-soon">soon</span></span>'
NEW = '<a href="/home/index.html">Home</a>'

changed = 0
for path in ROOT.rglob("*.html"):
    html = path.read_text(encoding="utf-8")
    if OLD not in html:
        continue
    path.write_text(html.replace(OLD, NEW), encoding="utf-8")
    changed += 1
    print(f"patched {path.relative_to(ROOT.parent)}")

print(f"\n{changed} file(s) patched")
