#!/usr/bin/env python3
"""
Restore ZIP bar JS (profile pre-fill + form handlers) that was wiped by patch_hamburger_js.py.
Insert as a separate <script> block before the hamburger JS on:
  - All 66 compare pages (need zipBar + embedZip handlers)
  - All 7 guide article pages (need zipBar handlers only)
"""
import os, glob

HAMBURGER_MARKER = "<script>(function(){var btn=document.getElementById('navHamburger')"

ZIPBAR_JS_COMPARE = """<script>
(function(){try{var p=JSON.parse(localStorage.getItem("br_profile"));if(p&&p.zip){var zi=document.getElementById("zipBarInput");if(zi)zi.value=p.zip;var btn=document.querySelector(".zip-bar-btn");if(btn)btn.textContent="Return to Rates →";}}catch(e){}}());
document.getElementById("zipBarForm").addEventListener("submit",function(e){e.preventDefault();var zip=document.getElementById("zipBarInput").value.trim();if(!/^\d{5}$/.test(zip)){document.getElementById("zipBarInput").focus();return;}window.location.href="/?zip="+zip;});
document.getElementById("zipBarInput").addEventListener("input",function(e){e.target.value=e.target.value.replace(/\D/g,"").substring(0,5);});
document.getElementById("embedZipForm").addEventListener("submit",function(e){e.preventDefault();var zip=document.getElementById("embedZipInput").value.trim();if(!/^\d{5}$/.test(zip)){document.getElementById("embedZipInput").focus();return;}window.location.href="/?zip="+zip;});
document.getElementById("embedZipInput").addEventListener("input",function(e){e.target.value=e.target.value.replace(/\D/g,"").substring(0,5);});
</script>
"""

ZIPBAR_JS_ARTICLE = """<script>
(function(){try{var p=JSON.parse(localStorage.getItem("br_profile"));if(p&&p.zip){var zi=document.getElementById("zipBarInput");if(zi)zi.value=p.zip;var btn=document.querySelector(".zip-bar-btn");if(btn)btn.textContent="Return to Rates →";}}catch(e){}}());
document.getElementById("zipBarForm").addEventListener("submit",function(e){e.preventDefault();var zip=document.getElementById("zipBarInput").value.trim();if(!/^\d{5}$/.test(zip)){document.getElementById("zipBarInput").focus();return;}window.location.href="/?zip="+zip;});
document.getElementById("zipBarInput").addEventListener("input",function(e){e.target.value=e.target.value.replace(/\D/g,"").substring(0,5);});
</script>
"""

ALREADY_PATCHED = "zipBarForm"

def patch_file(path, zip_js):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Skip if already has zipBarForm handlers in a script block (not just the form element)
    # Check if it appears in a script context (not just the form HTML)
    scripts_portion = html[html.find('</footer>'):]
    if 'zipBarForm' in scripts_portion and 'addEventListener' in scripts_portion:
        print(f"  SKIP (already has zipBarForm handler): {path}")
        return False

    if HAMBURGER_MARKER not in html:
        print(f"  SKIP (no hamburger marker): {path}")
        return False

    idx = html.find(HAMBURGER_MARKER)
    new_html = html[:idx] + zip_js + html[idx:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"  PATCHED: {path}")
    return True

# Compare pages (66 files, skip compare/index.html which is the picker)
compare_files = sorted(glob.glob("article/compare/*.html"))
compare_files = [f for f in compare_files if not f.endswith('/index.html')]

print(f"\n=== Compare pages ({len(compare_files)} files) ===")
compare_patched = 0
for path in compare_files:
    if patch_file(path, ZIPBAR_JS_COMPARE):
        compare_patched += 1

# Guide article pages
guide_files = [
    "article/coverage-guide.html",
    "article/credit-score-insurance.html",
    "article/florida-rates-dropping.html",
    "article/premium-went-up.html",
    "article/shopping-strategy.html",
    "article/sr22-insurance.html",
    "article/young-drivers.html",
]

print(f"\n=== Guide article pages ({len(guide_files)} files) ===")
guide_patched = 0
for path in guide_files:
    if os.path.exists(path):
        if patch_file(path, ZIPBAR_JS_ARTICLE):
            guide_patched += 1
    else:
        print(f"  MISSING: {path}")

print(f"\nDone. Patched {compare_patched}/{len(compare_files)} compare pages, {guide_patched}/{len(guide_files)} guide pages.")
