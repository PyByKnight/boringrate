#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Detect rate-capping (rate-stabilization) rules in filings, and qualify the spread.

WHY THIS IS A CORRECTNESS FIX, NOT A FEATURE: /rate-filings/ renders `max_pct`/`min_pct` as
"individual policies moved +X% to -Y%". For any filing that also carries a capping rule, that
sentence is wrong in one of two directions, and the corpus contains both:

  UNDERSTATED — the filed max IS the cap, and the uncapped figure is far higher. Louisiana to
    Imperial (GMMX-134796306): "0% is a capped maximum change, remove it and display the actual
    expected maximum change of +163."
  OVERSTATED — the filed max is pre-capping, and no single policy can actually move that far.
    Michigan to Bristol West (BRWS-134728991): "rate increases are capped at 10% and rate
    decreases are capped at -5% ... the maximum rate change shown ... of +14% is before any
    capping."

Either way a reader takes the spread literally and is misled, so where a capping rule exists the
page has to say so.

PRECISION: "cap" is heavily overloaded in filings — capped LOSSES, capped expense ratios, large-
loss caps at $100,000 — none of which limit a policyholder's rate change. Those are excluded by
pattern. Values are only asserted where hand-verified (VERIFIED below); everything else is
recorded as presence-only, which is enough to qualify the sentence honestly.

Writes `filing_caps.json`. Read by gen_rate_filings_rollup.py.

  python3 mine_capping.py --report    # show what was found, write nothing
  python3 mine_capping.py             # write filing_caps.json
"""
import gzip, json, re, sys, datetime, collections

SRC, OUT = 'filing_digests.json.gz', 'filing_caps.json'
REPORT = '--report' in sys.argv

# A rate-capping rule limits how far ONE POLICY's premium can move at renewal.
RATE_CAP = re.compile(
    r'rate[- ]capp?(?:ing|ed)|capping rule|capp?(?:ing|ed)[^.]{0,40}\b(?:at|to)\s*[+\-±]?\s?\d+(?:\.\d+)?\s*%'
    r'|rate stabilization|capp?ed at [+\-±]?\s?\d+(?:\.\d+)?\s*%', re.I)
# ...as opposed to these, which cap LOSSES or EXPENSES and say nothing about your bill.
NOT_RATE = re.compile(
    r'capped loss|capped expense|loss(?:es)? (?:are |is )?capp|cap(?:ped)? at \$|'
    r'large loss|excess loss|basic limit|capped premium trend', re.I)

# Hand-verified caps. Key: tracking. `cap` is free text stated as the filing states it.
VERIFIED = {
    'SPIS-134785306': {'cap': '±10%, for five years', 'quote':
        'Vault is proposing the implementation of rate capping of ±10% for a period of five years.'},
    'BRWS-134728991': {'cap': '+10% / −5%', 'direction': 'overstates', 'quote':
        'rate increases are capped at 10% and rate decreases are capped at -5% ... the maximum '
        'rate change shown in the Rate Information section of +14% is before any capping.'},
    'CLIN-134595066': {'cap': '+10% / −10%', 'quote':
        'We are updating the rate capping to -10% and +10% to be effective on 11/7/2025.'},
    'SELC-134557134': {'cap': '+20% / −20%', 'quote': 'Capping Rule SICSC is proposing capping at +20%/-20%.'},
    'SELC-134891661': {'cap': '+20% / −20%', 'quote': 'Capping Rule Capping is set at +20%/-20%.'},
    # Louisiana caught Imperial reporting a CAPPED maximum (0%) and made it publish the real one.
    # The ledger's +163.1% is that corrected figure, so the number shown is already uncapped —
    # an earlier pass here wrongly implied the true change was higher still.
    'GMMX-134796306': {'cap': None, 'direction': 'corrected', 'quote':
        'Louisiana objected that the filed maximum was a capped figure: "0% is a capped maximum '
        'change, remove it and display the actual expected maximum change of +163."'},
}


def sentences(blob):
    return [s.strip() for s in re.split(r'(?<=[.;])\s+', re.sub(r'\s+', ' ', blob)) if s.strip()]


def main():
    dig = json.load(gzip.open(SRC))['digests']
    out = {}
    for t, d in dig.items():
        blob = ' '.join([d.get('desc') or ''] + d.get('responses', []) + d.get('objections', []))
        hits = [s for s in sentences(blob)
                if RATE_CAP.search(s) and not NOT_RATE.search(s) and len(s) < 400]
        if not hits and t not in VERIFIED:
            continue
        rec = {'state': d.get('state'), 'carrier': d.get('carrier'), 'line': d.get('line'),
               'evidence': hits[:2]}
        rec.update(VERIFIED.get(t, {}))
        rec['verified'] = t in VERIFIED
        out[t] = rec

    ver = sum(1 for v in out.values() if v['verified'])
    print(f'filings with a rate-capping rule: {len(out)}  ({ver} hand-verified with a value)')
    print('by state:', dict(collections.Counter(v['state'] for v in out.values()).most_common()))

    if REPORT:
        print('\n--- verified ---')
        for t, v in out.items():
            if not v['verified']:
                continue
            print(f'  [{v["state"]}] {v["carrier"]}  {t}  cap={v.get("cap")}  '
                  f'dir={v.get("direction", "—")}')
        print('\n--- detected, value not verified (presence-only qualifier) ---')
        for t, v in list(out.items()):
            if v['verified']:
                continue
            ev = (v['evidence'] or [''])[0]
            print(f'  [{v["state"]}] {str(v["carrier"])[:20]:<20} {t}  {ev[:100]}')
        print('\n--report: nothing written')
        return

    json.dump({'_meta': {
        'purpose': 'Filings carrying a rate-capping / rate-stabilization rule, which limits how '
                   'far a single policy can move at renewal. Used to qualify the max/min spread '
                   'on /rate-filings/, where an unqualified spread misleads in both directions.',
        'built': datetime.date.today().isoformat(), 'filings': len(out), 'verified': ver,
        'caveat': 'Presence is pattern-detected; cap VALUES are asserted only where hand-verified.',
    }, 'caps': out}, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
