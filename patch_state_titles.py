#!/usr/bin/env python3
"""
Patch <title> tags on all 51 state pages to keyword-targeted format:
  {State} Auto Insurance Rates (2026) — BoringRate

H1s are left untouched — editorial headlines stay as-is.
"""
import re
from pathlib import Path

STATE_DIR = Path(__file__).parent / "article" / "state"

TITLES = {
    "alabama.html":        "Alabama Auto Insurance Rates (2026) — BoringRate",
    "alaska.html":         "Alaska Auto Insurance Rates (2026) — BoringRate",
    "arizona.html":        "Arizona Auto Insurance Rates (2026) — BoringRate",
    "arkansas.html":       "Arkansas Auto Insurance Rates (2026) — BoringRate",
    "california.html":     "California Auto Insurance Rates (2026) — BoringRate",
    "colorado.html":       "Colorado Auto Insurance Rates (2026) — BoringRate",
    "connecticut.html":    "Connecticut Auto Insurance Rates (2026) — BoringRate",
    "delaware.html":       "Delaware Auto Insurance Rates (2026) — BoringRate",
    "florida.html":        "Florida Auto Insurance Rates (2026) — BoringRate",
    "georgia.html":        "Georgia Auto Insurance Rates (2026) — BoringRate",
    "hawaii.html":         "Hawaii Auto Insurance Rates (2026) — BoringRate",
    "idaho.html":          "Idaho Auto Insurance Rates (2026) — BoringRate",
    "illinois.html":       "Illinois Auto Insurance Rates (2026) — BoringRate",
    "indiana.html":        "Indiana Auto Insurance Rates (2026) — BoringRate",
    "iowa.html":           "Iowa Auto Insurance Rates (2026) — BoringRate",
    "kansas.html":         "Kansas Auto Insurance Rates (2026) — BoringRate",
    "kentucky.html":       "Kentucky Auto Insurance Rates (2026) — BoringRate",
    "louisiana.html":      "Louisiana Auto Insurance Rates (2026) — BoringRate",
    "maine.html":          "Maine Auto Insurance Rates (2026) — BoringRate",
    "maryland.html":       "Maryland Auto Insurance Rates (2026) — BoringRate",
    "massachusetts.html":  "Massachusetts Auto Insurance Rates (2026) — BoringRate",
    "michigan.html":       "Michigan Auto Insurance Rates (2026) — BoringRate",
    "minnesota.html":      "Minnesota Auto Insurance Rates (2026) — BoringRate",
    "mississippi.html":    "Mississippi Auto Insurance Rates (2026) — BoringRate",
    "missouri.html":       "Missouri Auto Insurance Rates (2026) — BoringRate",
    "montana.html":        "Montana Auto Insurance Rates (2026) — BoringRate",
    "nebraska.html":       "Nebraska Auto Insurance Rates (2026) — BoringRate",
    "nevada.html":         "Nevada Auto Insurance Rates (2026) — BoringRate",
    "new-hampshire.html":  "New Hampshire Auto Insurance Rates (2026) — BoringRate",
    "new-jersey.html":     "New Jersey Auto Insurance Rates (2026) — BoringRate",
    "new-mexico.html":     "New Mexico Auto Insurance Rates (2026) — BoringRate",
    "new-york.html":       "New York Auto Insurance Rates (2026) — BoringRate",
    "north-carolina.html": "North Carolina Auto Insurance Rates (2026) — BoringRate",
    "north-dakota.html":   "North Dakota Auto Insurance Rates (2026) — BoringRate",
    "ohio.html":           "Ohio Auto Insurance Rates (2026) — BoringRate",
    "oklahoma.html":       "Oklahoma Auto Insurance Rates (2026) — BoringRate",
    "oregon.html":         "Oregon Auto Insurance Rates (2026) — BoringRate",
    "pennsylvania.html":   "Pennsylvania Auto Insurance Rates (2026) — BoringRate",
    "rhode-island.html":   "Rhode Island Auto Insurance Rates (2026) — BoringRate",
    "south-carolina.html": "South Carolina Auto Insurance Rates (2026) — BoringRate",
    "south-dakota.html":   "South Dakota Auto Insurance Rates (2026) — BoringRate",
    "tennessee.html":      "Tennessee Auto Insurance Rates (2026) — BoringRate",
    "texas.html":          "Texas Auto Insurance Rates (2026) — BoringRate",
    "utah.html":           "Utah Auto Insurance Rates (2026) — BoringRate",
    "vermont.html":        "Vermont Auto Insurance Rates (2026) — BoringRate",
    "virginia.html":       "Virginia Auto Insurance Rates (2026) — BoringRate",
    "washington.html":     "Washington State Auto Insurance Rates (2026) — BoringRate",
    "washington-dc.html":  "Washington D.C. Auto Insurance Rates (2026) — BoringRate",
    "west-virginia.html":  "West Virginia Auto Insurance Rates (2026) — BoringRate",
    "wisconsin.html":      "Wisconsin Auto Insurance Rates (2026) — BoringRate",
    "wyoming.html":        "Wyoming Auto Insurance Rates (2026) — BoringRate",
}

TITLE_RE = re.compile(r'<title>[^<]+</title>')

updated = 0
for filename, new_title in TITLES.items():
    path = STATE_DIR / filename
    html = path.read_text(encoding="utf-8")
    new_html = TITLE_RE.sub(f"<title>{new_title}</title>", html, count=1)
    if new_html == html:
        print(f"  SKIP (no change): {filename}")
        continue
    path.write_text(new_html, encoding="utf-8")
    updated += 1
    print(f"  updated: {filename}")

print(f"\nDone. {updated}/{len(TITLES)} files updated.")
