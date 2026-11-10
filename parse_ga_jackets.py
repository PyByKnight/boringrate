#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read the Company Rate Information block out of SERFF jacket PDFs.

The jacket renders that block as a column of LABELS followed by a column of
VALUES, so label:value regexes find nothing (0/36 on the first attempt). The
real shape is:

    <label lines x9>  <company name 1-3 lines>  <7 numeric values>  [next company...]
    Overall Rate Information for Multiple Company Filings
    Overall Percentage Rate Indicated For This Filing   <value>
    Overall Percentage Rate Impact For This Filing      <value>

Per-company values are positional, in header order:
    indicated %, impact %, WP change $, policyholders, WP $, max %, min %

Runbook trap: on multi-company filings the summary "Overall Percentage Rate
Impact" can read 0.000% because SERFF does not aggregate across entities. We
capture BOTH the summary and the per-company rows and flag any disagreement.
"""
import re, subprocess, glob, os, json, sys

NUM = re.compile(r'^-?[\d,]+\.?\d*%$|^\$-?[\d,]+$|^-?[\d,]+$')
# An EMPTY cell renders as a bare '%' or '$'. It still occupies a column, so it
# must be consumed positionally - skipping it shifts every later value left and
# turned Amica's $41,446,710 written premium into a policyholder count.
EMPTY = re.compile(r'^[%$]$')

def text(pdf):
    txt = os.path.join(os.path.dirname(pdf) + '_txt', os.path.basename(pdf)[:-4] + '.txt')
    if not os.path.exists(pdf) and os.path.exists(txt):
        return open(txt, encoding='utf-8', errors='replace').read()
    try:
        return subprocess.run(['python3', 'serff_pdftext.py', pdf],
                              capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return ''

def num(s):
    s = s.strip().replace(',', '').replace('$', '').rstrip('%')
    try: return float(s)
    except ValueError: return None

def parse(pdf):
    L = [l.strip() for l in text(pdf).splitlines()]
    out = {'companies': [], 'summary': {}, 'disposition': None,
           'eff_new': None, 'eff_ren': None, 'status': None}
    DATE = re.compile(r'^\d{2}/\d{2}/\d{4}$')

    def val(i, l):
        """Value on the label line, else (label alone on its line) the next line if it is a date."""
        v = l.split(':', 1)[1].strip()
        if not v and i + 1 < len(L) and DATE.match(L[i + 1]):
            v = L[i + 1]
        return v or None

    req_new = req_ren = None
    for i, l in enumerate(L):
        # FIRST non-empty wins: the header block is the current disposition. Later
        # 'Disposition Date:' lines are the disposition HISTORY, oldest last - the old
        # last-wins rule read CO State Farm SFMA-134942134 as 08/12 instead of 10/21.
        if l.startswith('Disposition Date:'): out['disposition'] = out['disposition'] or val(i, l)
        elif l.startswith('Effective Date (New):'): out['eff_new'] = out['eff_new'] or val(i, l)
        elif l.startswith('Effective Date (Renewal):'): out['eff_ren'] = out['eff_ren'] or val(i, l)
        # Colorado (file & use) leaves the two fields above blank and carries the dates
        # only as 'Effective Date / Requested (New):' in the header.
        elif l.startswith('Requested (New):'): req_new = req_new or val(i, l)
        elif l.startswith('Requested (Renewal):'): req_ren = req_ren or val(i, l)
        elif l.startswith('Status:') and not out['status']: out['status'] = l.split(':', 1)[1].strip()
        # multi-company summary: label line, value on the next
        elif l.startswith('Overall Percentage Rate Impact For This Filing'):
            out['summary']['impact'] = num(L[i+1]) if i+1 < len(L) else None
        elif l.startswith('Overall Percentage Rate Indicated For This Filing'):
            out['summary']['indicated'] = num(L[i+1]) if i+1 < len(L) else None
        elif l.startswith('Effect of Rate Filing - Number of Policyholders'):
            out['summary']['affected'] = num(L[i+1]) if i+1 < len(L) else None
        elif l.startswith('Effect of Rate Filing-Written Premium Change'):
            out['summary']['wp_change'] = num(L[i+1]) if i+1 < len(L) else None

    if not out['eff_new'] and req_new: out['eff_new'], out['eff_requested'] = req_new, True
    if not out['eff_ren'] and req_ren: out['eff_ren'], out['eff_requested'] = req_ren, True

    # per-company rows. The header block repeats on every page of a long jacket,
    # so walk ALL occurrences and keep the first complete row per entity.
    seen = set()
    for h in [i for i, l in enumerate(L) if l == "Minimum %"]:
        i = h + 3
        while i < len(L):
            if L[i].startswith(('Overall Rate Information', 'Schedule', 'PDF Pipeline')): break
            name = []
            while i < len(L) and not NUM.match(L[i]) and not EMPTY.match(L[i]):
                if L[i].startswith(('Overall Rate Information', 'Schedule', 'PDF Pipeline')): break
                if L[i]: name.append(L[i])
                i += 1
            # Keep the RAW token: a column can be omitted entirely (COUNTRY's
            # jacket drops Written Premium Change, giving 6 values not 7), so pure
            # positional assignment shifts. Percentages, dollars and the bare
            # policyholder integer are distinguishable by their own formatting.
            raw = []
            while i < len(L) and len(raw) < 7 and (NUM.match(L[i]) or EMPTY.match(L[i])):
                raw.append(None if EMPTY.match(L[i]) else L[i].strip()); i += 1
            vals = [None if r is None else num(r) for r in raw]
            key = ' '.join(name)[:70]
            if name and len(vals) >= 2 and key not in seen:
                seen.add(key)
                pcts = [v for r, v in zip(raw, vals) if r and r.endswith('%')]
                dols = [v for r, v in zip(raw, vals) if r and r.startswith('$')]
                ints = [v for r, v in zip(raw, vals) if r and not r.endswith('%') and not r.startswith('$')]
                out['companies'].append({
                'entity': key,
                'indicated': pcts[0] if len(pcts) > 0 else None,
                'impact':    pcts[1] if len(pcts) > 1 else None,
                'max_pct':   pcts[2] if len(pcts) > 2 else None,
                'min_pct':   pcts[3] if len(pcts) > 3 else None,
                'wp_change': dols[0] if len(dols) > 1 else None,
                'wp':        dols[-1] if dols else None,
                'affected':  int(ints[0]) if ints and ints[0] is not None else None})
            elif not name:
                i += 1
    return out

if __name__ == '__main__':
    st = sys.argv[1] if len(sys.argv) > 1 else 'GA'
    res = {}
    for d in sorted(glob.glob(f'_serff/{st}/*/')):
        if d.rstrip('/').endswith('_txt'): continue
        t = os.path.basename(d.rstrip('/'))
        res[t] = parse(os.path.join(d, t + '.pdf'))
        print('.', end='', flush=True)
    json.dump(res, open(f'_serff/{st}/_parsed.json', 'w'), indent=1)
    print(f"\nparsed {len(res)} jackets -> _serff/{st}/_parsed.json")
