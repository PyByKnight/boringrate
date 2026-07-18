#!/usr/bin/env python3
"""
Fix incorrect carrier recommendations in metro articles.
Many articles were templated with Erie Insurance (only available in 11 states)
and other regional carriers that don't appear in ZIP tool results for those states.

Replaces carrier mentions in 3 locations per file:
  1. JSON-LD schema answer text
  2. TLDR bullet
  3. FAQ callout paragraph

Safe to re-run — skips files already showing the correct carriers.
"""
import re
from pathlib import Path

METRO_DIR = Path(__file__).parent / "article" / "metro"

# State slug → state code
STATE_SLUG_TO_CODE = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new-hampshire': 'NH', 'new-jersey': 'NJ', 'new-mexico': 'NM', 'new-york': 'NY',
    'north-carolina': 'NC', 'north-dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode-island': 'RI', 'south-carolina': 'SC',
    'south-dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'washington-dc': 'DC',
    'west-virginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY',
}

# Per-state recommended carriers (c1, c2, also_worth_comparing)
# Based on STATE_LOCAL_CARRIERS and LOCAL_CARRIER_DEFS in index.html.
# Only carriers that actually appear in the ZIP tool for that state.
STATE_CHEAPEST = {
    'AL': ('GEICO', 'Alfa Insurance', 'Nationwide'),
    'AK': ('GEICO', 'State Farm', 'Nationwide'),
    'AZ': ('GEICO', 'Mercury Insurance', 'Nationwide'),
    'AR': ('GEICO', 'Shelter Insurance', 'Nationwide'),
    'CA': ('GEICO', 'Wawanesa', 'Nationwide'),
    'CO': ('GEICO', 'American Family', 'Nationwide'),
    'CT': ('NJM Insurance', 'GEICO', 'Amica Mutual'),
    'DC': ('Erie Insurance', 'GEICO', 'Nationwide'),
    'DE': ('Erie Insurance', 'GEICO', 'Nationwide'),
    'FL': ('GEICO', 'Auto-Owners', 'Nationwide'),
    'GA': ('Georgia Farm Bureau', 'GEICO', 'Alfa Insurance'),
    'HI': ('GEICO', 'State Farm', 'Nationwide'),
    'ID': ('GEICO', 'PEMCO', 'American Family'),
    'IL': ('Erie Insurance', 'Country Financial', 'GEICO'),
    'IN': ('Indiana Farm Bureau', 'Erie Insurance', 'GEICO'),
    'IA': ('GEICO', 'Grinnell Mutual', 'Nationwide'),
    'KS': ('GEICO', 'Kansas Farm Bureau', 'Nationwide'),
    'KY': ('Kentucky Farm Bureau', 'GEICO', 'Auto-Owners'),
    'LA': ('Louisiana Farm Bureau', 'GEICO', 'Nationwide'),
    'ME': ('GEICO', 'Amica Mutual', 'Nationwide'),
    'MD': ('Erie Insurance', 'NJM Insurance', 'GEICO'),
    'MA': ('GEICO', 'Amica Mutual', 'MAPFRE Insurance'),
    'MI': ('GEICO', 'Auto-Owners', 'Nationwide'),
    'MN': ('GEICO', 'Auto-Owners', 'Nationwide'),
    'MS': ('GEICO', 'Mississippi Farm Bureau', 'Nationwide'),
    'MO': ('GEICO', 'Shelter Insurance', 'Auto-Owners'),
    'MT': ('GEICO', 'State Farm', 'Nationwide'),
    'NE': ('GEICO', 'American Family', 'Shelter Insurance'),
    'NV': ('GEICO', 'Mercury Insurance', 'Nationwide'),
    'NH': ('GEICO', 'Amica Mutual', 'Nationwide'),
    'NJ': ('NJM Insurance', 'Erie Insurance', 'GEICO'),
    'NM': ('GEICO', 'State Farm', 'Nationwide'),
    'NY': ('Erie Insurance', 'NYCM Insurance', 'GEICO'),
    'NC': ('NC Farm Bureau', 'GEICO', 'Auto-Owners'),
    'ND': ('GEICO', 'Nodak Mutual', 'Nationwide'),
    'OH': ('Erie Insurance', 'Auto-Owners', 'Westfield Insurance'),
    'OK': ('GEICO', 'Oklahoma Farm Bureau', 'Nationwide'),
    'OR': ('GEICO', 'PEMCO', 'Amica Mutual'),
    'PA': ('Erie Insurance', 'NJM Insurance', 'GEICO'),
    'RI': ('GEICO', 'Amica Mutual', 'Nationwide'),
    'SC': ('SC Farm Bureau', 'GEICO', 'Auto-Owners'),
    'SD': ('GEICO', 'American Family', 'Nationwide'),
    'TN': ('Tennessee Farm Bureau', 'GEICO', 'Nationwide'),
    'TX': ('Texas Farm Bureau', 'GEICO', 'Nationwide'),
    'UT': ('GEICO', 'American Family', 'CSAA / AAA'),
    'VT': ('GEICO', 'Amica Mutual', 'Nationwide'),
    'VA': ('Erie Insurance', 'Virginia Farm Bureau', 'GEICO'),
    'WA': ('GEICO', 'PEMCO', 'American Family'),
    'WV': ('Erie Insurance', 'Auto-Owners', 'GEICO'),
    'WI': ('American Family', 'GEICO', 'West Bend Mutual'),
    'WY': ('GEICO', 'State Farm', 'Nationwide'),
}

def get_state_code(html: str) -> str | None:
    """Extract state code from the article's internal-links-state link."""
    m = re.search(r'internal-links-state.*?article/state/([^"\.]+)\.html', html, re.DOTALL)
    if not m:
        return None
    slug = m.group(1)
    return STATE_SLUG_TO_CODE.get(slug)


def apply_carriers(html: str, c1: str, c2: str, c3: str, city: str, state_name: str) -> str:
    """Replace the three carrier-mention locations in the HTML."""

    # 1. TLDR bullet: "X and Y are consistently among the cheapest carriers in this market"
    html = re.sub(
        r'<li>.+? and .+? are consistently among the cheapest carriers in this market</li>',
        f'<li>{c1} and {c2} are consistently among the cheapest carriers in this market</li>',
        html, count=1
    )

    # 2. JSON-LD text (inside double-quotes, — not &mdash;)
    # Pattern: "For {City} drivers with clean records, X and Y are frequently ...
    #           Z is also worth comparing. Enter ZIP..."
    html = re.sub(
        r'("text": "For ' + re.escape(city) + r' drivers with clean records, ).+? and .+? are frequently the most competitive\. .+? is also worth comparing\.',
        r'\g<1>' + c1 + ' and ' + c2 + ' are frequently the most competitive. ' + c3 + ' is also worth comparing.',
        html, count=1
    )

    # 3. FAQ callout (inside HTML, — is &mdash;)
    html = re.sub(
        r'(<br>For ' + re.escape(city) + r' drivers with clean records, ).+? and .+? are frequently the most competitive\. .+? is also worth comparing\.',
        r'\g<1>' + c1 + ' and ' + c2 + ' are frequently the most competitive. ' + c3 + ' is also worth comparing.',
        html, count=1
    )

    return html


def get_city_name(html: str) -> str | None:
    """Extract city name from article kicker line (e.g. 'Metro Report · Atlanta · 3 min read')."""
    m = re.search(r'Metro Report</a> &nbsp;&middot;&nbsp; (.+?) &nbsp;&middot;&nbsp;', html)
    return m.group(1).strip() if m else None


updated = skipped = errors = 0

for path in sorted(METRO_DIR.glob("*.html")):
    html = path.read_text(encoding='utf-8')

    state_code = get_state_code(html)
    if not state_code:
        print(f"  ERROR: could not detect state for {path.name}")
        errors += 1
        continue

    rec = STATE_CHEAPEST.get(state_code)
    if not rec:
        print(f"  SKIP: no recommendation defined for {state_code} ({path.name})")
        skipped += 1
        continue

    c1, c2, c3 = rec
    city = get_city_name(html)
    if not city:
        print(f"  ERROR: could not detect city for {path.name}")
        errors += 1
        continue

    # Check if already correct (idempotency)
    tldr_check = f'<li>{c1} and {c2} are consistently among the cheapest carriers in this market</li>'
    if tldr_check in html:
        skipped += 1
        continue

    new_html = apply_carriers(html, c1, c2, c3, city, state_code)
    if new_html == html:
        print(f"  WARN: no change made for {path.name} (city='{city}', state={state_code})")
        skipped += 1
        continue

    path.write_text(new_html, encoding='utf-8')
    print(f"  updated {path.name}: {state_code} → {c1} / {c2} / {c3}")
    updated += 1

print(f"\nDone. {updated} updated, {skipped} already correct/skipped, {errors} errors.")
