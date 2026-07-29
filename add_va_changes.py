#!/usr/bin/env python3
"""Add VA auto movers to rate_changes.json from the SERFF ledger.
Flat (0%) filings EXCLUDED (filing flat != a rate change). Carries the tier-2/1
content juice: indicated_pct (more-coming signal) + max_pct/min_pct (spread)."""
import json, collections
led = json.load(open('serff_filings.json')); rows = led if isinstance(led, list) else led['filings']
rc = json.load(open('rate_changes.json'))
have = {(c['carrier'], c['state'], c.get('url')) for c in rc['changes']}
added = []
for r in rows:
    if r['state'] != "VA" or not r['overall_pct']: continue
    if not r.get('effective_new'): continue
    e = {'carrier': r['carrier'], 'state': 'VA',
         'pct': abs(round(r['overall_pct'], 2)),
         'dir': 'decrease' if r['overall_pct'] < 0 else 'increase',
         'effective': r['effective_new'], 'affected': r['affected'],
         'indicated_pct': r.get('indicated_pct'),
         'max_pct': r.get('max_pct'), 'min_pct': r.get('min_pct'),
         'source': 'Virginia Bureau of Insurance (SERFF)', 'url': r['url']}
    if (e['carrier'], "VA", e['url']) in have: continue
    added.append(e)
rc['changes'].extend(added)
json.dump(rc, open('rate_changes.json','w'), indent=1)
print(f"added {len(added)} VA changes; total {len(rc['changes'])}")
print(collections.Counter(a['dir'] for a in added))
