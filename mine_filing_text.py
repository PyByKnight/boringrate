#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Distil the SERFF jacket corpus into a compact, durable, queryable digest store.

PROBLEM: `_serff/*_txt/` holds ~500 jacket texts (~16 MB) across 10 states. Most of it is
boilerplate — SERFF repeats an 8-line identity header plus a "PDF Pipeline ... Generated"
footer on EVERY page, and the schedule tables restate the same rows. The genuinely useful
prose is a small fraction of the bytes and is currently unqueryable.

WHAT'S WORTH KEEPING (each answers a consumer question the ledger JSON cannot):
  • Filing Description  — the carrier explaining, in its own words, what it changed and why.
  • Objection Letters   — the state DOI pushing back. Regulators challenging carriers is
                          editorial material effectively nobody else publishes.
  • Response Letters    — how the carrier answered, and what it conceded.
  • Filing Notes        — informal reviewer/filer exchanges.
These are the raw material for future articles AND the basis for tracking how a carrier's
posture shifts over time, which a percentage in serff_filings.json cannot show.

OUTPUT: `filing_digests.json.gz` — gzipped JSON keyed by SERFF tracking number. Gzip is the
right call here: this is highly repetitive English prose, so it compresses ~5-6x, and the
whole store stays a single file that `git` handles fine and any script can load in one line.
Raw `_txt` remains the source of truth on disk; this is the distilled, revisitable layer.

  python3 mine_filing_text.py            # build/refresh the store
  python3 mine_filing_text.py --stats    # report only, write nothing
"""
import re, os, json, gzip, glob, sys, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_serff')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'filing_digests.json.gz')
STATS = '--stats' in sys.argv

# The per-page identity header SERFF stamps on every page, ending at the pipeline footer.
BOILER = re.compile(
    r'SERFF Tracking #:.*?PDF Pipeline for SERFF Tracking Number \S+ Generated [\d/]+ [\d:]+ [AP]M',
    re.S)
PAGEFOOT = re.compile(r'PDF Pipeline for SERFF Tracking Number \S+ Generated [\d/]+ [\d:]+ [AP]M')

# Section terminators — a narrative block ends at the next structural heading.
END = re.compile(
    r'\n(?:Filing Contact Information|Filing Company Information|Filing Fees|'
    r'Correspondence Summary|Form Schedule|Rate Information|Rate/Rule Schedule|'
    r'Supporting Document Schedule|Superseded Schedule Items|Disposition|'
    r'Objection Letter|Response Letter|Filing Notes|Note To|State Specific|'
    r'Company Rate Information|Attachment\(s\):|Item Status)')

ABBR = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO',
 'Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID',
 'Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME',
 'Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO',
 'Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
 'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR',
 'Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN',
 'Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV',
 'Wisconsin':'WI','Wyoming':'WY','District of Columbia':'DC'}


def clean(t):
    t = PAGEFOOT.sub('', t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()


def grab(text, start_re, maxlen=9000):
    """All blocks starting at start_re, each running to the next structural heading."""
    out = []
    for m in re.finditer(start_re, text):
        seg = text[m.end():m.end() + maxlen]
        e = END.search(seg)
        if e:
            seg = seg[:e.start()]
        seg = clean(seg)
        if len(seg) > 40:
            out.append(seg)
    return out


def dedupe(items):
    """SERFF restates blocks across pages; keep first occurrence of each."""
    seen, out = set(), []
    for x in items:
        k = re.sub(r'\W+', '', x.lower())[:220]
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out


def parse(path):
    raw = open(path, encoding='utf-8', errors='replace').read()
    body = BOILER.sub('\n', raw)

    desc = dedupe(grab(body, r'Filing Description:\s*\n'))
    objections = dedupe(grab(body, r'Objection Letter Date\s*\n'))
    responses = dedupe(grab(body, r'Response Letter Date\s*\n'))
    notes = dedupe(grab(body, r'(?:Note To Reviewer|Note To Filer)\s*\n', 3000))

    def first(pat):
        m = re.search(pat, raw)
        return m.group(1).strip() if m else None

    return {
        'desc': desc[0] if desc else None,
        'objections': objections,
        'responses': responses,
        'notes': notes,
        'company': first(r'Filing Company:\s*\n([^\n]+)'),
        'toi': first(r'TOI/Sub-TOI:\s*\n([^\n]+)'),
        'product': first(r'Product Name:\s*\n([^\n]+)'),
        'disposition_date': first(r'Disposition Date:\s*([\d/]+)'),
        # Fallback identity for jackets we pulled but triaged out of the ledgers (~100 of them):
        # they are still real filings and still carry usable narrative, so keep them findable.
        'state_name': first(r'\nState:\s*\n([A-Z][a-z]+(?: [A-Z][a-z]+)*)\n'),
    }


def main():
    # carrier/state/line come from the ledgers so the digest joins cleanly to them
    meta = {}
    for f, line in [('serff_filings.json', 'auto'), ('serff_home_filings.json', 'home'),
                    ('serff_renters_filings.json', 'renters')]:
        p = os.path.join(os.path.dirname(OUT), f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for r in (d['filings'] if isinstance(d, dict) else d):
            meta[r['tracking']] = {'state': r.get('state'), 'carrier': r.get('carrier'),
                                   'line': r.get('line', line), 'overall_pct': r.get('overall_pct')}

    digests, raw_bytes = {}, 0
    for path in sorted(glob.glob(os.path.join(ROOT, '*_txt', '*.txt'))):
        trk = os.path.basename(path)[:-4]
        raw_bytes += os.path.getsize(path)
        d = parse(path)
        if not (d['desc'] or d['objections'] or d['responses'] or d['notes']):
            continue
        d.update(meta.get(trk, {}))
        if not d.get('state') and d.get('state_name'):
            d['state'] = ABBR.get(d['state_name'])
            d['in_ledger'] = False        # pulled but triaged out — narrative still usable
        d.pop('state_name', None)
        d = {k: v for k, v in d.items() if v not in (None, [], '')}
        digests[trk] = d

    payload = {
        '_meta': {
            'purpose': 'Distilled narrative sections from SERFF jackets — filing descriptions, '
                       'DOI objection letters, carrier responses, reviewer notes. Source of raw '
                       'text is _serff/*_txt/ (gitignored). Built by mine_filing_text.py.',
            'built': datetime.date.today().isoformat(),
            'filings': len(digests),
        },
        'digests': digests,
    }

    n_obj = sum(len(d.get('objections', [])) for d in digests.values())
    n_desc = sum(1 for d in digests.values() if d.get('desc'))
    body = json.dumps(payload, indent=1, ensure_ascii=False).encode('utf-8')

    print(f'jackets scanned : {len(glob.glob(os.path.join(ROOT, "*_txt", "*.txt")))}')
    print(f'digests kept    : {len(digests)}')
    print(f'  descriptions  : {n_desc}')
    print(f'  objections    : {n_obj}')
    print(f'  responses     : {sum(len(d.get("responses", [])) for d in digests.values())}')
    print(f'raw corpus      : {raw_bytes/1e6:.1f} MB')
    print(f'digest (json)   : {len(body)/1e6:.2f} MB')

    if STATS:
        print('\n--stats: nothing written')
        return
    with gzip.open(OUT, 'wb', compresslevel=9) as fh:
        fh.write(body)
    print(f'digest (gz)     : {os.path.getsize(OUT)/1e6:.2f} MB  -> {os.path.basename(OUT)}')
    print(f'compression     : {raw_bytes/max(1,os.path.getsize(OUT)):.0f}x vs raw corpus')


if __name__ == '__main__':
    main()
