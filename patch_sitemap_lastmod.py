#!/usr/bin/env python3
"""
Inject <lastmod> dates into sitemap.xml using each file's last git commit date.
Inserts <lastmod> immediately after <loc> in each <url> entry.
"""
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).parent
SITEMAP = BASE / "sitemap.xml"
BASE_URL = "https://boringrate.com/"


def git_date(rel_path: str) -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ai", "--", rel_path],
        capture_output=True, text=True, cwd=BASE,
    )
    raw = result.stdout.strip()
    return raw[:10] if raw else "2026-05-22"  # date only; fallback to today


def url_to_path(url: str) -> str:
    path = url.removeprefix(BASE_URL)
    if not path or path == "/":
        return "index.html"
    return path


sitemap = SITEMAP.read_text(encoding="utf-8")

def replace_url(m: re.Match) -> str:
    block = m.group(0)
    loc_m = re.search(r'<loc>([^<]+)</loc>', block)
    if not loc_m:
        return block
    rel = url_to_path(loc_m.group(1))
    date = git_date(rel)
    # Insert <lastmod> right after </loc>
    return block.replace('</loc>', f'</loc><lastmod>{date}</lastmod>', 1)

new_sitemap = re.sub(r'<url>.*?</url>', replace_url, sitemap, flags=re.DOTALL)

SITEMAP.write_text(new_sitemap, encoding="utf-8")
print("Done. Sample output:")
for line in new_sitemap.splitlines()[2:8]:
    print(" ", line.strip())
