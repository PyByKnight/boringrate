#!/usr/bin/env python3
"""Add OH auto movers to rate_changes.json from the SERFF ledger.
Flat (0%) filings are EXCLUDED: filing flat is not a rate change (FL press<->ledger lesson)."""
import json
led = json.load(open('serff_filings.json'))
rows = led if isinstance(led, list) else led['filings']
rc = json.load(open('rate_changes.json'))
have = {(c['carrier'], c['state'], c.get('url')) for c in rc['changes']}
added = []
for r in rows:
    if r['state'] != 'OH' or not r['overall_pct']:
        continue                                   # skips None and 0.0 (flat)
    if not r.get('effective_new'):
        continue
    e = {'carrier': r['carrier'], 'state': 'OH',
         'pct': abs(round(r['overall_pct'], 2)),
         'dir': 'decrease' if r['overall_pct'] < 0 else 'increase',
         'effective': r['effective_new'], 'affected': r['affected'],
         'source': 'Ohio Department of Insurance (SERFF)', 'url': r['url']}
    if (e['carrier'], 'OH', e['url']) in have: continue
    added.append(e)
rc['changes'].extend(added)
json.dump(rc, open('rate_changes.json','w'), indent=1)
print(f"added {len(added)} OH changes; total {len(rc['changes'])}")
import collections
print(collections.Counter(a['dir'] for a in added))
