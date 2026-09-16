#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract per-carrier DISCOUNT changes from the filing digest store.

WHY THIS AND NOT THE LEDGER: serff_filings.json answers "did my rate go up?". It cannot answer
"which carrier will actually give me a break, and for what?" — which is the question a shopper
asks once they've decided to switch. Discount terms are the clearest carrier DIFFERENTIATOR in
the whole filing, and they're stated in plain English in the filing description.

Real examples this pulls out of the existing corpus:
  • a carrier doubling its multi-car discount from 10% to 20%
  • "Increasing our Participation in Safe Driving Discount to 15%"
  • an Advance Quote Discount that phases out over five years, max 15%
  • "Removing Elite Policy Discount (factors will change to 1.00)" — a discount being KILLED,
    which is a rate increase that never shows up as one in the headline percentage

That last category matters most: a carrier can hold its filed rate flat and still raise your
bill by deleting a discount you were getting. The overall_pct hides that completely.

Reads `filing_digests.json.gz`; writes `rate_modifiers.json` (the scaffold that has been sitting
empty since MODIFIERS_PLAN.md). Sentence-level extraction with the carrier/state/date already
joined, so every row is citable back to a SERFF tracking number.

  python3 mine_discounts.py            # write rate_modifiers.json
  python3 mine_discounts.py --report   # print findings, write nothing
"""
import re, json, gzip, sys, datetime, collections

SRC = 'filing_digests.json.gz'
OUT = 'rate_modifiers.json'
REPORT = '--report' in sys.argv

# Named discount/surcharge programs worth tracking. Ordered longest-first so that
# e.g. "Multi-Policy Discount" wins over a bare "Policy Discount" match.
NAMED = [
    'Participation in Safe Driving', 'Evidence of Continuous Insurance', 'Accident Prevention Course',
    'Advance Quote', 'Advanced Quote', 'Preferred Policy', 'Defensive Driver', 'Payment Plan',
    'Prior Coverage', 'Full Coverage', 'Elite Policy', 'Safe Driving', 'Multi-Policy', 'Multi-Vehicle',
    'Multi-Product', 'Multi-Line', 'Multi-Car', 'Good Student', 'Distant Student', 'Student Away',
    'Anti-Theft', 'Paid in Full', 'Paperless', 'Paperless Delivery', 'Electronic Funds Transfer',
    'Homeowner', 'Home Owner', 'Bundling', 'Bundle', 'Loyalty', 'Tenure', 'Renewal', 'Longevity',
    'Telematics', 'Usage-Based', 'Safe Driver', 'Claim Free', 'Claims Free', 'Accident Free',
    'New Car', 'New Home', 'Green Home', 'Roof', 'Protective Device', 'Fire Alarm', 'Smoke Alarm',
    'Sprinkler', 'Gated Community', 'Senior', 'Mature Driver', 'Military', 'Affinity', 'Group',
    'Occupational', 'Educator', 'Early Signing', 'Early Shopper', 'Welcome', 'Transfer',
    'Continuous Insurance', 'Violation Free', 'Good Payer', 'Autopay', 'Auto Pay', 'Pay in Full',
]
NAMED.sort(key=len, reverse=True)

SENT = re.compile(r'(?<=[.;:\n])\s*')
# a sentence qualifies only if it names a discount AND carries a number or a change verb
HAS_DISC = re.compile(r'\b(discount|surcharge|credit)s?\b', re.I)
HAS_VAL = re.compile(r'\b\d+(?:\.\d+)?\s*%|\bfactors?\b|\b0\.\d+\b|\$\s?\d+', re.I)
CHANGE = re.compile(
    r'\b(increas\w+|decreas\w+|rais\w+|reduc\w+|remov\w+|eliminat\w+|introduc\w+|add\w*|'
    r'expand\w+|revis\w+|new|from\s+\d+(?:\.\d+)?\s*%?\s*to|chang\w+|discontinu\w+)\b', re.I)
# reviewer/objection prose that is about process, not about a consumer-visible term
NOISE = re.compile(
    r'\b(please (amend|provide|explain|clarify|confirm|submit)|objection \d|'
    r'we (are )?(request|require)|pursuant to|per your|attach\w+ herewith|see attach)\b', re.I)


def sentences(text):
    parts = []
    for chunk in text.split('\n'):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts.extend(p.strip() for p in re.split(r'(?<=[.!?])\s+', chunk) if p.strip())
    # re-join fragments split mid-sentence by the PDF's hard line wraps
    merged, buf = [], ''
    for p in parts:
        buf = (buf + ' ' + p).strip() if buf else p
        if re.search(r'[.!?]$', buf) or len(buf) > 320:
            merged.append(buf)
            buf = ''
    if buf:
        merged.append(buf)
    return merged


def named_programs(s):
    found = []
    low = s.lower()
    for n in NAMED:
        if n.lower() in low and not any(n.lower() in f.lower() for f in found):
            found.append(n)
    return found[:4]


def pcts(s):
    return [float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%', s)][:6]


def main():
    store = json.load(gzip.open(SRC))
    digests = store['digests']
    rows = []

    for trk, d in digests.items():
        blocks = []
        if d.get('desc'):
            blocks.append(('description', d['desc']))
        for o in d.get('objections', []):
            blocks.append(('doi_objection', o))
        for r in d.get('responses', []):
            blocks.append(('carrier_response', r))
        for n in d.get('notes', []):
            blocks.append(('note', n))

        seen = set()
        for src, text in blocks:
            for s in sentences(text):
                if len(s) < 35 or len(s) > 400:
                    continue
                if not HAS_DISC.search(s):
                    continue
                if not (HAS_VAL.search(s) and CHANGE.search(s)):
                    continue
                if NOISE.search(s) and src != 'description':
                    continue
                key = re.sub(r'\W+', '', s.lower())[:110]
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    'tracking': trk,
                    'state': d.get('state'),
                    'carrier': d.get('carrier') or d.get('company'),
                    'line': d.get('line'),
                    'effective': d.get('disposition_date'),
                    'source': src,
                    'programs': named_programs(s),
                    'pcts': pcts(s),
                    'removal': bool(re.search(r'\b(remov\w+|eliminat\w+|discontinu\w+)\b', s, re.I)),
                    'text': re.sub(r'\s+', ' ', s).strip(),
                })

    rows.sort(key=lambda r: (r['state'] or '', r['carrier'] or '', r['tracking']))

    prog = collections.Counter(p for r in rows for p in r['programs'])
    by_state = collections.Counter(r['state'] for r in rows)
    removals = [r for r in rows if r['removal']]

    print(f'discount/surcharge statements extracted: {len(rows)}')
    print(f'  from {len({r["tracking"] for r in rows})} filings, '
          f'{len({r["carrier"] for r in rows if r["carrier"]})} carriers')
    print(f'  DISCOUNT REMOVALS (hidden increases): {len(removals)}')
    print(f'\nby state: {dict(by_state.most_common())}')
    print(f'\ntop named programs:')
    for p, n in prog.most_common(18):
        print(f'   {p:<34} {n}')

    if REPORT:
        print('\n--- sample: discount removals (a rate hike the headline % hides) ---')
        for r in removals[:8]:
            print(f'\n  [{r["state"]}] {r["carrier"]} ({r["tracking"]})')
            print(f'    {r["text"][:230]}')
        print('\n--report: nothing written')
        return

    json.dump({
        '_meta': {
            'purpose': 'Per-carrier discount/surcharge program changes mined from SERFF filing '
                       'narrative (see MODIFIERS_PLAN.md). Each row cites a SERFF tracking number. '
                       'Built by mine_discounts.py from filing_digests.json.gz.',
            'built': datetime.date.today().isoformat(),
            'rows': len(rows),
            'caveat': 'Sentence-level extraction from filing prose. Values are as STATED by the '
                      'carrier or regulator and are not independently verified against the rate '
                      'manual; treat as citable quotes, not as computed factors.',
        },
        'modifiers': rows,
    }, open(OUT, 'w'), indent=1, ensure_ascii=False)
    print(f'\nwrote {OUT}')


if __name__ == '__main__':
    main()
