#!/usr/bin/env python3
"""Insert a "Nearby states" cross-link module into every renters/state/*.html.

Renters state pages did not link to each other at all — each striking-distance
page (Maine, DC, New Mexico, …) had ~5 contextual inbound links, nearly all
from its own hub/metro. This distributes internal link equity across the 51
pages with keyword-rich anchors ("New Hampshire renters insurance"), which is
the standard on-page lever for position 11-30 pages, and gives readers the
obvious next step: comparing a neighboring state.

SAFE + IDEMPOTENT: inserts a single new <section> before the article-email
block; never edits existing content and never touches a <script> block
(CLAUDE.md / patch_hamburger_js.py). Re-running replaces the module in place.
"""
import re, glob, os

MARK_OPEN, MARK_CLOSE = "<!-- nearby-states -->", "<!-- /nearby-states -->"

# Land borders (50 states + DC). Symmetric.
BORDERS = {
    "alabama": ["florida", "georgia", "mississippi", "tennessee"],
    "alaska": [],
    "arizona": ["california", "colorado", "nevada", "new-mexico", "utah"],
    "arkansas": ["louisiana", "mississippi", "missouri", "oklahoma", "tennessee", "texas"],
    "california": ["arizona", "nevada", "oregon"],
    "colorado": ["arizona", "kansas", "nebraska", "new-mexico", "oklahoma", "utah", "wyoming"],
    "connecticut": ["massachusetts", "new-york", "rhode-island"],
    "delaware": ["maryland", "new-jersey", "pennsylvania"],
    "florida": ["alabama", "georgia"],
    "georgia": ["alabama", "florida", "north-carolina", "south-carolina", "tennessee"],
    "hawaii": [],
    "idaho": ["montana", "nevada", "oregon", "utah", "washington", "wyoming"],
    "illinois": ["indiana", "iowa", "kentucky", "missouri", "wisconsin"],
    "indiana": ["illinois", "kentucky", "michigan", "ohio"],
    "iowa": ["illinois", "minnesota", "missouri", "nebraska", "south-dakota", "wisconsin"],
    "kansas": ["colorado", "missouri", "nebraska", "oklahoma"],
    "kentucky": ["illinois", "indiana", "missouri", "ohio", "tennessee", "virginia", "west-virginia"],
    "louisiana": ["arkansas", "mississippi", "texas"],
    "maine": ["new-hampshire"],
    "maryland": ["delaware", "pennsylvania", "virginia", "west-virginia", "washington-dc"],
    "massachusetts": ["connecticut", "new-hampshire", "new-york", "rhode-island", "vermont"],
    "michigan": ["indiana", "ohio", "wisconsin"],
    "minnesota": ["iowa", "north-dakota", "south-dakota", "wisconsin"],
    "mississippi": ["alabama", "arkansas", "louisiana", "tennessee"],
    "missouri": ["arkansas", "illinois", "iowa", "kansas", "kentucky", "nebraska", "oklahoma", "tennessee"],
    "montana": ["idaho", "north-dakota", "south-dakota", "wyoming"],
    "nebraska": ["colorado", "iowa", "kansas", "missouri", "south-dakota", "wyoming"],
    "nevada": ["arizona", "california", "idaho", "oregon", "utah"],
    "new-hampshire": ["maine", "massachusetts", "vermont"],
    "new-jersey": ["delaware", "new-york", "pennsylvania"],
    "new-mexico": ["arizona", "colorado", "oklahoma", "texas", "utah"],
    "new-york": ["connecticut", "massachusetts", "new-jersey", "pennsylvania", "vermont"],
    "north-carolina": ["georgia", "south-carolina", "tennessee", "virginia"],
    "north-dakota": ["minnesota", "montana", "south-dakota"],
    "ohio": ["indiana", "kentucky", "michigan", "pennsylvania", "west-virginia"],
    "oklahoma": ["arkansas", "colorado", "kansas", "missouri", "new-mexico", "texas"],
    "oregon": ["california", "idaho", "nevada", "washington"],
    "pennsylvania": ["delaware", "maryland", "new-jersey", "new-york", "ohio", "west-virginia"],
    "rhode-island": ["connecticut", "massachusetts"],
    "south-carolina": ["georgia", "north-carolina"],
    "south-dakota": ["iowa", "minnesota", "montana", "nebraska", "north-dakota", "wyoming"],
    "tennessee": ["alabama", "arkansas", "georgia", "kentucky", "mississippi", "missouri", "north-carolina", "virginia"],
    "texas": ["arkansas", "louisiana", "new-mexico", "oklahoma"],
    "utah": ["arizona", "colorado", "idaho", "nevada", "wyoming"],
    "vermont": ["massachusetts", "new-hampshire", "new-york"],
    "virginia": ["kentucky", "maryland", "north-carolina", "tennessee", "west-virginia", "washington-dc"],
    "washington": ["idaho", "oregon"],
    "west-virginia": ["kentucky", "maryland", "ohio", "pennsylvania", "virginia"],
    "wisconsin": ["illinois", "iowa", "michigan", "minnesota"],
    "wyoming": ["colorado", "idaho", "montana", "nebraska", "south-dakota", "utah"],
    "washington-dc": ["maryland", "virginia"],
}

# Same-region fill so low-border states (Maine, DC, the Dakotas) still reach 5
# and so each target picks up inbound links from region-mates, not just borders.
REGIONS = [
    ["maine", "new-hampshire", "vermont", "massachusetts", "rhode-island", "connecticut"],
    ["new-york", "new-jersey", "pennsylvania", "delaware", "maryland", "washington-dc"],
    ["virginia", "west-virginia", "north-carolina", "south-carolina", "georgia", "florida"],
    ["kentucky", "tennessee", "alabama", "mississippi"],
    ["north-dakota", "south-dakota", "nebraska", "kansas", "minnesota", "iowa", "missouri"],
    ["montana", "idaho", "wyoming", "nevada", "utah", "colorado", "arizona", "new-mexico"],
    ["washington", "oregon", "california", "alaska", "hawaii"],
    ["wisconsin", "michigan", "illinois", "indiana", "ohio"],
    ["arkansas", "louisiana", "oklahoma", "texas"],
]
REGION_OF = {s: grp for grp in REGIONS for s in grp}


def title_of(slug):
    if slug == "washington-dc":
        return "Washington, D.C."
    if slug == "new-mexico":
        return "New Mexico"
    return " ".join(w.capitalize() for w in slug.split("-"))


def nearby(slug, want=5):
    out = list(BORDERS.get(slug, []))
    for s in REGION_OF.get(slug, []):
        if len(out) >= want:
            break
        if s != slug and s not in out:
            out.append(s)
    return out[:want]


def module(slug):
    links = "".join(
        f'<a class="ns-link" href="/renters/state/{n}.html">{title_of(n)} renters insurance</a>'
        for n in nearby(slug))
    return (
        f'{MARK_OPEN}'
        '<section class="nearby-states" aria-label="Nearby states" '
        'style="margin:34px 0;padding-top:26px;border-top:1px solid var(--rule);">'
        '<div style="font-family:var(--mono);font-size:11px;text-transform:uppercase;'
        'letter-spacing:0.08em;color:var(--ink-mute);margin-bottom:12px;">Compare nearby states</div>'
        '<div class="ns-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));'
        'gap:8px 20px;">'
        f'{links}</div>'
        '<style>.nearby-states .ns-link{font-family:var(--serif);font-size:15px;color:var(--ink-soft);'
        'text-decoration:none;padding:4px 0;border-bottom:1px solid transparent;}'
        '.nearby-states .ns-link:hover{color:var(--accent);border-bottom-color:var(--accent);}</style>'
        '</section>'
        f'{MARK_CLOSE}')


def patch(path):
    slug = os.path.basename(path)[:-5]
    if slug not in BORDERS:
        return "skip-unknown"
    html = open(path, encoding="utf-8").read()
    mod = module(slug)
    if MARK_OPEN in html:                       # idempotent: replace in place
        new = re.sub(re.escape(MARK_OPEN) + ".*?" + re.escape(MARK_CLOSE), mod, html, flags=re.DOTALL)
        verb = "refresh"
    else:
        anchor = '\n    <div class="article-email">'
        if anchor not in html:
            return "skip-no-anchor"
        new = html.replace(anchor, "\n    " + mod + anchor, 1)
        verb = "insert"
    if new != html:
        open(path, "w", encoding="utf-8").write(new)
    return verb


if __name__ == "__main__":
    import collections
    counts = collections.Counter()
    for p in sorted(glob.glob("renters/state/*.html")):
        counts[patch(p)] += 1
    print(dict(counts))
    # report inbound link count each page now receives
    inbound = collections.Counter()
    for s in BORDERS:
        for n in nearby(s):
            inbound[n] += 1
    targets = ["maine", "new-mexico", "new-hampshire", "kentucky", "vermont",
               "washington-dc", "west-virginia", "new-jersey", "north-dakota", "south-dakota", "montana"]
    print("\nnew contextual inbound links to striking-distance targets:")
    for t in targets:
        print(f"   {t:<16}+{inbound[t]}")
