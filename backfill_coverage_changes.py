#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backfill `coverage_changes` where a filing states it unambiguously in prose.

WHY IT MATTERS: `overall_pct` is a statewide average across all coverages, so it can hide
the change a given customer actually felt. The clearest case in the corpus is Virginia Farm
Bureau — headline **0.0%**, while BI Liability went **+3%** and PD/Comprehensive/Collision went
**-1%**. A liability-only policyholder got a 3% increase on a filing that reads "no change".

WHY THIS IS HAND-CURATED AND NOT A PARSER: an automated sweep of all 486 digests for
"<coverage> ... N%" returns 28 candidates, and reading them shows most are NOT rate changes —
they are loss-trend selections ("loss trend selection of 27.4% for PIP"), minimum rate
differentials, or capping discussion inside regulator objections. Only the entries below state
an actual filed per-coverage base-rate change. Each carries the source sentence so the claim is
auditable, and `source` records which digest section it came from.

WHAT'S BLOCKED (and it is most of it): the per-coverage tables for the rest live in ATTACHMENT
exhibits — "Exhibit L - Impact of Rate Change by Coverage and Component" and similar — which
were never downloaded, because pulls default to the jacket only. No jacket in the 7-state corpus
contains a parseable per-coverage table; verified by grep. `--pull-list` prints exactly which
filings advertise such an exhibit, ranked by book size, so a future SERFF session can grab them
with one extra checkbox instead of re-triaging from scratch.

  python3 backfill_coverage_changes.py --dry        # show what would change
  python3 backfill_coverage_changes.py             # apply to the ledgers
  python3 backfill_coverage_changes.py --pull-list # what to fetch attachments for, ranked
"""
import json, gzip, re, sys, os, collections

DRY = '--dry' in sys.argv
PULL = '--pull-list' in sys.argv
ROOT = os.path.dirname(os.path.abspath(__file__))

# Verified by reading the filing description in full. Keys are SERFF tracking numbers.
# `quote` is the exact sentence the numbers come from — do not edit one without the other.
VERIFIED = {
    'CURE-134400950': {
        'coverage_changes': {'BI': 8.0, 'UMBI': 30.0, 'UIMBI': 30.0, 'PD': 20.0, 'UMPD': 20.0},
        'source': 'desc',
        'quote': 'Increase Bodily Injury base rates by +8% / Increase Uninsured Motorist'
                 '/Underinsured Motorist Bodily Injury by +30% / Increase Property Damage and '
                 'Uninsured/Underinsured Motorist base rates by +20%',
    },
    'VRFB-134968347': {
        'coverage_changes': {'BI': 3.0, 'PD': -1.0, 'COMP': -1.0, 'COLL': -1.0},
        'source': 'desc',
        'quote': 'BI Liability has been increased by 3%. PD Liability, Comprehensive and '
                 'Collision have been decreased by 1%. The overall rate impact for these '
                 'changes is 0.0%.',
    },
    'VRFB-134968381': {
        'coverage_changes': {'BI': 3.0, 'PD': -1.0, 'COMP': -1.0, 'COLL': -1.0},
        'source': 'desc',
        'quote': 'BI Liability has been increased by 3%. PD Liability, Comprehensive and '
                 'Collision have been decreased by 1%. The overall rate impact for these '
                 'changes is 0.0%.',
    },
}

LEDGERS = ['serff_filings.json', 'serff_home_filings.json']
EXHIBIT = re.compile(r'Rate Change by Coverage|Impact by Coverage|by Coverage and Component|'
                     r'rate change by coverage|rate level changes by coverage', re.I)


def pull_list():
    """Filings that advertise a per-coverage exhibit we never downloaded, ranked by book size."""
    import glob
    led = {}
    for f in LEDGERS:
        for r in json.load(open(os.path.join(ROOT, f)))['filings']:
            led[r['tracking']] = r

    rows = []
    for path in glob.glob(os.path.join(ROOT, '_serff', '*_txt', '*.txt')):
        trk = os.path.basename(path)[:-4]
        txt = open(path, encoding='utf-8', errors='replace').read()
        if not EXHIBIT.search(txt):
            continue
        r = led.get(trk)
        if not r or r.get('coverage_changes'):
            continue
        rows.append((r.get('affected') or 0, r.get('state'), r.get('carrier'),
                     trk, r.get('overall_pct'), r.get('url')))
    rows.sort(reverse=True)

    print(f'{len(rows)} filings advertise a per-coverage exhibit but have no coverage_changes.')
    print('Re-pull these with "Supporting Document Attachments" checked, biggest book first:\n')
    print(f'{"affected":>10}  {"st":<3} {"carrier":<22} {"overall":>8}  tracking')
    print('-' * 78)
    for aff, st, car, trk, pct, url in rows:
        a = f'{aff:,}' if aff else '—'
        p = f'{pct:+.1f}%' if isinstance(pct, (int, float)) else '—'
        print(f'{a:>10}  {st or "?":<3} {str(car)[:22]:<22} {p:>8}  {trk}')
    tot = sum(r[0] for r in rows)
    print(f'\ncombined book across these filings: {tot:,} policyholders')


def main():
    if PULL:
        pull_list()
        return

    changed = collections.Counter()
    for f in LEDGERS:
        p = os.path.join(ROOT, f)
        data = json.load(open(p))
        hit = False
        for r in data['filings']:
            v = VERIFIED.get(r.get('tracking'))
            if not v:
                continue
            if r.get('coverage_changes') == v['coverage_changes']:
                changed['already'] += 1
                continue
            print(f'  {r["tracking"]:<20} {r["state"]} {r["carrier"]}')
            print(f'      overall {r["overall_pct"]}%  ->  {v["coverage_changes"]}')
            r['coverage_changes'] = v['coverage_changes']
            r['coverage_source'] = f'SERFF {r["tracking"]} ({v["source"]}): {v["quote"]}'
            changed['set'] += 1
            hit = True
        if hit and not DRY:
            json.dump(data, open(p, 'w'), indent=1, ensure_ascii=False)

    print(f'\nset {changed["set"]}, already current {changed["already"]}')
    if DRY:
        print('dry run — nothing written')
    elif changed['set']:
        print('ledgers updated. Run ./rebuild.sh to propagate.')


if __name__ == '__main__':
    main()
