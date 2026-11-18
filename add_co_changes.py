#!/usr/bin/env python3
"""Add CO auto movers to rate_changes.json from the SERFF ledger (2026-11-18 pull).
Flats excluded; small books gated via filing_guards.too_small; drift_exclude rows
(jacket sign conflicts) kept out of the display feed. Dominant entity per jacket wins
the (carrier, state, url) dedupe because append_co_auto.py writes it first."""
import json, collections
import filing_guards as fg
led = json.load(open('serff_filings.json')); rows = led if isinstance(led, list) else led['filings']
rc = json.load(open('rate_changes.json'))
have = {(c['carrier'], c['state'], c.get('url')) for c in rc['changes']}
added = []
for r in rows:
    if r['state'] != 'CO' or not r['overall_pct'] or not r.get('effective_new'): continue
    if not fg.is_driftable(r) or fg.too_small(r): continue
    if round(r['overall_pct'], 2) == 0: continue  # rounding-zero (The General -0.004%)
    e = {'carrier': r['carrier'], 'state': 'CO',
         'pct': abs(round(r['overall_pct'], 2)),
         'dir': 'decrease' if r['overall_pct'] < 0 else 'increase',
         'effective': r['effective_new'], 'affected': r['affected'],
         'indicated_pct': r.get('indicated_pct'),
         'max_pct': r.get('max_pct'), 'min_pct': r.get('min_pct'),
         'source': 'Colorado Division of Insurance (SERFF)', 'url': r['url']}
    if (e['carrier'], 'CO', e['url']) in have: continue
    have.add((e['carrier'], 'CO', e['url'])); added.append(e)
rc['changes'].extend(added)
json.dump(rc, open('rate_changes.json', 'w'), indent=1)
print(f"added {len(added)} CO changes; total {len(rc['changes'])}")
for a in sorted(added, key=lambda a: (a['carrier'], a['effective'])):
    print(f"  {a['carrier']:20} {a['dir']:9} {a['pct']:>6}%  eff {a['effective']}  PH={a['affected']}")
