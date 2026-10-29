#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pull DEEP rate history from Illinois IDOI into filing_history.json.

NOT a backfill. fetch_il_filings.py already captured everything IL has inside our
disposition window — a spot check returned 14 State Farm home filings of which
exactly ONE was in-window. What IDOI also carries, and nobody else publishes, is
the full history back to ~2012 with indicated %, taken %, max/min spread and
policyholder count per filing.

That answers the question the reactive pages exist for. State Farm has raised IL
home rates 14 times since 2012, compounding to +104.5% on 1.37M policyholders.

Kept DELIBERATELY SEPARATE from serff_*_filings.json. Per memory
boringrate-open-book-model, pre-window filings are pre-baked and must never move
the rate model; this file is narrative evidence only and no drift path reads it.

  python3 fetch_il_history.py            # all IL carriers in the ledgers
  python3 fetch_il_history.py --carrier "State Farm"
"""
import json, os, re, subprocess, sys, time

OUT = 'filing_history.json'
ROW = re.compile(r'^\s*(\d{4}-\d{2}-\d{2})\s+(auto|home)\s+([\-\d.]+)%\s+([\-\d.]+)%\s+([\d,]+)\s+([+\-\d./]+)\s+(\S+)')

def carriers():
    names = set()
    for led in ('serff_filings.json', 'serff_home_filings.json'):
        d = json.load(open(led)); rows = d if isinstance(d, list) else d['filings']
        names |= {r['carrier'] for r in rows if r.get('state') == 'IL'}
    return sorted(names)

def pull(carrier, line):
    try:
        p = subprocess.run(['python3', 'fetch_il_filings.py', '--carrier', carrier,
                            '--year', '2026', '--line', line],
                           capture_output=True, text=True, timeout=240)
    except subprocess.TimeoutExpired:
        return []
    out = []
    for l in p.stdout.splitlines():
        m = ROW.match(l)
        if m:
            d, ln, ind, taken, ph, spread, trk = m.groups()
            mx, mn = (spread.split('/') + [None])[:2]
            out.append({'date': d, 'line': ln, 'indicated_pct': float(ind),
                        'overall_pct': float(taken), 'affected': int(ph.replace(',', '')),
                        'max_pct': float(mx) if mx else None,
                        'min_pct': float(mn) if mn else None, 'tracking': trk})
    return out

def compound_main(fil):
    """Compound ONE book only, never across entities.

    A carrier often files several programs on the SAME DAY under different
    entities - Kemper filed twice on each of four dates, Allstate's 2014 series
    mixes a 2,792-policyholder program with a 267,613-policyholder one. Chaining
    those multiplies unrelated books together: it turned Kemper's real +139%
    into +429.6% and Allstate's +121.7% into +268.9%.

    So: keep the largest filing per date, then drop any program under 25% of the
    biggest book, and compound what remains. That tracks the carrier's main book.
    """
    by = {}
    for r in fil:
        d = r['date']
        if d not in by or (r['affected'] or 0) > (by[d]['affected'] or 0):
            by[d] = r
    seq = [by[d] for d in sorted(by)]
    mx = max((r['affected'] or 0) for r in seq) or 1
    seq = [r for r in seq if (r['affected'] or 0) >= 0.25 * mx]
    c = 1.0
    for r in seq:
        c *= 1 + r['overall_pct'] / 100
    return (c - 1) * 100, len(seq), mx

def main():
    only = None
    if '--carrier' in sys.argv:
        only = sys.argv[sys.argv.index('--carrier') + 1]
    hist = json.load(open(OUT)) if os.path.exists(OUT) else {}
    names = [only] if only else carriers()
    print(f'IL history: {len(names)} carriers x 2 lines', flush=True)
    for i, c in enumerate(names, 1):
        for line in ('auto', 'home'):
            rows = pull(c, line)
            if rows:
                rows.sort(key=lambda r: r['date'])
                comp, n_main, main_book = compound_main(rows)
                hist.setdefault('IL', {}).setdefault(c, {})[line] = {
                    'filings': rows, 'first': rows[0]['date'], 'last': rows[-1]['date'],
                    'n': len(rows), 'n_main_book': n_main,
                    'compounded_pct': round(comp, 1),
                    'main_book_affected': main_book,
                    'max_affected': max(r['affected'] for r in rows)}
                print(f'  [{i}/{len(names)}] {c:26} {line:5} {len(rows):3} filings '
                      f'{rows[0]["date"][:4]}-{rows[-1]["date"][:4]}  '
                      f'compounded {comp:+.1f}% (main book {n_main}/{len(rows)})', flush=True)
            else:
                print(f'  [{i}/{len(names)}] {c:26} {line:5} —', flush=True)
            time.sleep(1.0)
        json.dump(hist, open(OUT, 'w'), indent=1)
    tot = sum(len(v.get(l, {}).get('filings', [])) for v in hist.get('IL', {}).values() for l in ('auto', 'home'))
    print(f'\ndone: {tot} historical filings -> {OUT}')

if __name__ == '__main__':
    main()
