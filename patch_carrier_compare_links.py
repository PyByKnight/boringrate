#!/usr/bin/env python3
"""
Add a "Compare head-to-head" section to each carrier page that has compare pages.
Inserts before <div class="article-email"> — does NOT touch any existing script blocks.

Top 5 compare pages per carrier are chosen by search relevance (biggest competitors first).
"""
from pathlib import Path

CARRIER_DIR = Path(__file__).parent / "article" / "carrier"
MARKER = '<div class="article-email">'

# (filename, display_label, [list of (compare_slug, link_text)])
CARRIERS = [
    (
        "geico.html", "GEICO",
        [
            ("geico-vs-progressive",    "GEICO vs. Progressive"),
            ("geico-vs-state-farm",     "GEICO vs. State Farm"),
            ("geico-vs-allstate",       "GEICO vs. Allstate"),
            ("geico-vs-usaa",           "GEICO vs. USAA"),
            ("geico-vs-nationwide",     "GEICO vs. Nationwide"),
        ],
    ),
    (
        "state-farm.html", "State Farm",
        [
            ("geico-vs-state-farm",         "GEICO vs. State Farm"),
            ("state-farm-vs-progressive",   "State Farm vs. Progressive"),
            ("state-farm-vs-allstate",      "State Farm vs. Allstate"),
            ("state-farm-vs-usaa",          "State Farm vs. USAA"),
            ("state-farm-vs-nationwide",    "State Farm vs. Nationwide"),
        ],
    ),
    (
        "progressive.html", "Progressive",
        [
            ("geico-vs-progressive",        "GEICO vs. Progressive"),
            ("state-farm-vs-progressive",   "State Farm vs. Progressive"),
            ("progressive-vs-allstate",     "Progressive vs. Allstate"),
            ("progressive-vs-usaa",         "Progressive vs. USAA"),
            ("progressive-vs-nationwide",   "Progressive vs. Nationwide"),
        ],
    ),
    (
        "allstate.html", "Allstate",
        [
            ("geico-vs-allstate",           "GEICO vs. Allstate"),
            ("state-farm-vs-allstate",      "State Farm vs. Allstate"),
            ("progressive-vs-allstate",     "Progressive vs. Allstate"),
            ("allstate-vs-usaa",            "Allstate vs. USAA"),
            ("allstate-vs-nationwide",      "Allstate vs. Nationwide"),
        ],
    ),
    (
        "usaa.html", "USAA",
        [
            ("geico-vs-usaa",           "GEICO vs. USAA"),
            ("state-farm-vs-usaa",      "State Farm vs. USAA"),
            ("progressive-vs-usaa",     "Progressive vs. USAA"),
            ("allstate-vs-usaa",        "Allstate vs. USAA"),
            ("nationwide-vs-usaa",      "Nationwide vs. USAA"),
        ],
    ),
    (
        "farmers.html", "Farmers",
        [
            ("geico-vs-farmers",            "GEICO vs. Farmers"),
            ("state-farm-vs-farmers",       "State Farm vs. Farmers"),
            ("progressive-vs-farmers",      "Progressive vs. Farmers"),
            ("allstate-vs-farmers",         "Allstate vs. Farmers"),
            ("nationwide-vs-farmers",       "Nationwide vs. Farmers"),
        ],
    ),
    (
        "liberty-mutual.html", "Liberty Mutual",
        [
            ("geico-vs-liberty-mutual",         "GEICO vs. Liberty Mutual"),
            ("state-farm-vs-liberty-mutual",    "State Farm vs. Liberty Mutual"),
            ("progressive-vs-liberty-mutual",   "Progressive vs. Liberty Mutual"),
            ("allstate-vs-liberty-mutual",      "Allstate vs. Liberty Mutual"),
            ("usaa-vs-liberty-mutual",          "USAA vs. Liberty Mutual"),
        ],
    ),
    (
        "nationwide.html", "Nationwide",
        [
            ("geico-vs-nationwide",         "GEICO vs. Nationwide"),
            ("state-farm-vs-nationwide",    "State Farm vs. Nationwide"),
            ("progressive-vs-nationwide",   "Progressive vs. Nationwide"),
            ("allstate-vs-nationwide",      "Allstate vs. Nationwide"),
            ("nationwide-vs-usaa",          "Nationwide vs. USAA"),
        ],
    ),
    (
        "travelers.html", "Travelers",
        [
            ("geico-vs-travelers",          "GEICO vs. Travelers"),
            ("state-farm-vs-travelers",     "State Farm vs. Travelers"),
            ("progressive-vs-travelers",    "Progressive vs. Travelers"),
            ("allstate-vs-travelers",       "Allstate vs. Travelers"),
            ("travelers-vs-usaa",           "Travelers vs. USAA"),
        ],
    ),
    (
        "safeco.html", "Safeco",
        [
            ("geico-vs-safeco",         "GEICO vs. Safeco"),
            ("state-farm-vs-safeco",    "State Farm vs. Safeco"),
            ("progressive-vs-safeco",   "Progressive vs. Safeco"),
            ("allstate-vs-safeco",      "Allstate vs. Safeco"),
            ("usaa-vs-safeco",          "USAA vs. Safeco"),
        ],
    ),
    (
        "the-hartford.html", "The Hartford",
        [
            ("geico-vs-the-hartford",           "GEICO vs. The Hartford"),
            ("state-farm-vs-the-hartford",      "State Farm vs. The Hartford"),
            ("progressive-vs-the-hartford",     "Progressive vs. The Hartford"),
            ("allstate-vs-the-hartford",        "Allstate vs. The Hartford"),
            ("usaa-vs-the-hartford",            "USAA vs. The Hartford"),
        ],
    ),
    (
        "root-insurance.html", "Root Insurance",
        [
            ("geico-vs-root-insurance",         "GEICO vs. Root"),
            ("progressive-vs-root-insurance",   "Progressive vs. Root"),
            ("state-farm-vs-root-insurance",    "State Farm vs. Root"),
            ("allstate-vs-root-insurance",      "Allstate vs. Root"),
            ("usaa-vs-root-insurance",          "USAA vs. Root"),
        ],
    ),
]


def build_compare_block(carrier_label, compares):
    links = "".join(
        f'<a href="../../article/compare/{slug}.html">{label} →</a>'
        for slug, label in compares
    )
    return (
        f'<h2>Compare {carrier_label} head-to-head</h2>\n'
        f'<div class="internal-links internal-links-compare">{links}</div>\n'
    )


updated = 0
for filename, label, compares in CARRIERS:
    path = CARRIER_DIR / filename
    html = path.read_text(encoding="utf-8")

    if "internal-links-compare" in html:
        print(f"  SKIP (already has compare links): {filename}")
        continue

    marker_pos = html.find(MARKER)
    if marker_pos == -1:
        print(f"  ERROR: marker not found in {filename}")
        continue

    block = build_compare_block(label, compares)
    html = html[:marker_pos] + block + html[marker_pos:]
    path.write_text(html, encoding="utf-8")
    updated += 1
    print(f"  updated: {filename}")

print(f"\nDone. {updated}/{len(CARRIERS)} files updated.")
