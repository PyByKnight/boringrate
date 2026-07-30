#!/usr/bin/env python3
"""Free backfill: re-parse on-disk OH/IL/PA/MI auto jackets to recover the
within-filing max_pct/min_pct spread (dropped before parse_oh.py captured it) and
fill it into the EXISTING ledger rows — no re-pull. Matches by tracking, then by
the entity whose overall_pct equals the ledger row's (falls back to the dominant
entity), so the spread lines up with the % already recorded."""
import json, os, subprocess, glob, sys
from parse_oh import parse

STATES = ['OH', 'IL', 'PA', 'MI']
SCRATCH = '/tmp/claude-1000/-home-knighttyler/a67eaa79-0691-435f-86f4-bb8c089a1996/scratchpad/reparse'

def dom(cs):
    c = [x for x in cs if x['overall_pct'] is not None and (x['affected'] or x['written_premium'])]
    return max(c, key=lambda x: (x['affected'] or 0, x['written_premium'] or 0)) if c else None

def maxmin_for(companies, row_pct):
    """Pick the company row whose overall matches the ledger %, else the dominant."""
    if row_pct is not None:
        for c in companies:
            if c['overall_pct'] is not None and abs(c['overall_pct'] - row_pct) < 0.05 \
               and (c.get('max_pct') is not None or c.get('min_pct') is not None):
                return c.get('max_pct'), c.get('min_pct')
    d = dom(companies)
    return (d.get('max_pct'), d.get('min_pct')) if d else (None, None)

# 1) extract + parse each state -> {tracking: parsed-jacket}
parsed = {}
for st in STATES:
    d = os.path.join(SCRATCH, st); os.makedirs(d, exist_ok=True)
    pdfs = glob.glob(f'_serff/{st}/*.pdf')
    for p in pdfs:
        txt = os.path.join(d, os.path.basename(p)[:-4] + '.txt')
        if not os.path.exists(txt) or os.path.getsize(txt) == 0:
            with open(txt, 'w') as f:
                subprocess.run(['python3', 'serff_pdftext.py', p], stdout=f, stderr=subprocess.DEVNULL)
    got = 0
    for txt in glob.glob(os.path.join(d, '*.txt')):
        j = parse(txt)
        if j['companies']:
            parsed[j['tracking']] = j; got += 1
    print(f"{st}: {len(pdfs)} pdf -> {got} parsed with a rate table")

# 2) backfill ledger rows
led = json.load(open('serff_filings.json')); rows = led['filings']
filled = miss = 0
for r in rows:
    if r['state'] not in STATES or r.get('max_pct') is not None:
        continue
    j = parsed.get(r['tracking'])
    if not j:
        miss += 1; continue
    mx, mn = maxmin_for(j['companies'], r.get('overall_pct'))
    if mx is not None or mn is not None:
        r['max_pct'] = mx; r['min_pct'] = mn; filled += 1
    else:
        miss += 1
json.dump(led, open('serff_filings.json', 'w'), indent=1)
print(f"\nbackfilled max/min into {filled} rows; {miss} rows unmatched/no-spread")
