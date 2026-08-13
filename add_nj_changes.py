#!/usr/bin/env python3
"""Add NJ movers to rate_changes.json from both ledgers (auto + home).
Threshold: PH>=4000 and |pct|>=1.0; flats excluded. No existing NJ changes to reconcile."""
import json
rc = json.load(open('rate_changes.json'))
have = {(c['carrier'], c.get('product', 'auto')) for c in rc['changes'] if c.get('state') == 'NJ'}
SRC = 'New Jersey Department of Banking and Insurance (SERFF)'
added = []

def pull(fn, product, is_home):
    rows = json.load(open(fn))['filings']
    rows = sorted(rows, key=lambda r: r.get('effective_new') or '', reverse=True)  # newest = open book wins dedup
    out = []
    for r in rows:
        if r['state'] != 'NJ': continue
        if is_home and r.get('line') != 'home': continue
        if not is_home and r.get('line') == 'home': continue
        op = r.get('overall_pct')
        if op is None or abs(op) < 1.0 or (r.get('affected') or 0) < 4000: continue
        if not r.get('effective_new'): continue
        if (r['carrier'], product) in have: continue
        out.append({'carrier': r['carrier'], 'state': 'NJ', 'product': product,
            'pct': abs(round(op, 2)), 'dir': 'decrease' if op < 0 else 'increase',
            'effective': r['effective_new'], 'affected': r['affected'], 'source': SRC, 'url': r['url']})
        have.add((r['carrier'], product))
    return out

added += pull('serff_filings.json', 'auto', False)
# home movers come from serff_home_filings.json via gen_home_rate_tracker (its own tracker); NOT rate_changes.json
rc['changes'].extend(added)
json.dump(rc, open('rate_changes.json', 'w'), indent=1)
print(f"added {len(added)} NJ changes:")
for a in added: print(f"  {a['product']:5} {a['carrier']:22} {a['dir']:9} {a['pct']}%  PH={a['affected']}")
