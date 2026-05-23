#!/usr/bin/env python3
"""
Add ZIP bar navigation handler to all article pages that have zipBarForm/embedZipForm
but no handler wiring them to /?zip=XXXXX.

Inserts a new <script> block before </body> — never replaces existing blocks.
"""
from pathlib import Path

ARTICLE_DIR = Path(__file__).parent / "article"

ZIP_SCRIPT = (
    '<script>(function(){'
    'function goZip(fid,iid){'
    'var f=document.getElementById(fid),i=document.getElementById(iid);'
    'if(!f||!i)return;'
    'f.addEventListener("submit",function(e){'
    'e.preventDefault();'
    'var z=i.value.replace(/\\D/g,"").substring(0,5);'
    'if(!/^\\d{5}$/.test(z)){i.focus();return;}'
    'window.location.href="/?zip="+z;'
    '});}'
    'goZip("zipBarForm","zipBarInput");'
    'goZip("embedZipForm","embedZipInput");'
    '})();</script>\n'
)

MARKER = '</body>'

updated = skipped = errors = 0
for path in sorted(ARTICLE_DIR.rglob("*.html")):
    html = path.read_text(encoding="utf-8")

    if "zipBarForm" not in html:
        continue  # page doesn't have the form
    if '/?zip=' in html or 'goZip(' in html:
        skipped += 1
        continue  # already handled

    if MARKER not in html:
        print(f"  ERROR: no </body> in {path.name}")
        errors += 1
        continue

    html = html.replace(MARKER, ZIP_SCRIPT + MARKER, 1)
    path.write_text(html, encoding="utf-8")
    updated += 1

print(f"\nDone. {updated} updated, {skipped} already handled, {errors} errors.")
