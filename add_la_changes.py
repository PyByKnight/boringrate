#!/usr/bin/env python3
"""Add LA auto movers to rate_changes.json from the SERFF ledger.
Keeps the 5 existing LDI press-release changes (they carry narrative + press citations and will
serff_match the ledger for an inline SERFF cite). Adds only market-weight movers those don't cover:
PH >= 4000 and |pct| >= 1.0, family not already represented, flats excluded."""
import json, collections
led = json.load(open('serff_filings.json'))
rows = led if isinstance(led, list) else led['filings']
rc = json.load(open('rate_changes.json'))

# families already covered by the existing LA (press) changes
covered = {'Progressive', 'Allstate', 'Encompass', 'Louisiana Farm Bureau'}
have_urls = {c.get('url') for c in rc['changes'] if c.get('state') == 'LA'}
added = []
for r in rows:
    if r['state'] != 'LA' or not r['overall_pct']:
        continue
    if r['carrier'] in covered:
        continue
    if abs(r['overall_pct']) < 1.0 or (r['affected'] or 0) < 4000:
        continue
    if not r.get('effective_new') or r['url'] in have_urls:
        continue
    added.append({
        'carrier': r['carrier'], 'state': 'LA',
        'pct': abs(round(r['overall_pct'], 2)),
        'dir': 'decrease' if r['overall_pct'] < 0 else 'increase',
        'effective': r['effective_new'], 'affected': r['affected'],
        'source': 'Louisiana Department of Insurance (SERFF)', 'url': r['url']})
rc['changes'].extend(added)
json.dump(rc, open('rate_changes.json', 'w'), indent=1)
print(f"added {len(added)} LA changes:")
for a in added: print(f"  {a['carrier']:20} {a['dir']:9} {a['pct']}%  PH={a['affected']}")
