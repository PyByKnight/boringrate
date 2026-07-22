#!/usr/bin/env python3
"""Parse OH SERFF auto jackets -> structured rows. Reads pre-extracted .txt files."""
import re, os, sys, json, glob

TXT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/ohtxt'

PCT  = re.compile(r'^-?[\d,]+\.?\d*%$')
MONEY= re.compile(r'^\$-?[\d,]+$')
NUM  = re.compile(r'^-?[\d,]+$')

def num(s):
    s = s.replace('$','').replace(',','').replace('%','')
    try: return float(s)
    except: return None

def parse(path):
    lines = [l.strip() for l in open(path, encoding='utf-8', errors='replace')]
    trk = os.path.basename(path)[:-4]
    rec = {'tracking': trk, 'companies': []}
    # header dates
    for i,l in enumerate(lines):
        if l.startswith('Effective Date (New):') and len(l) > 22:
            rec.setdefault('effective_new', l.split(':',1)[1].strip())
        if l.startswith('Effective Date (Renewal):') and len(l) > 26:
            rec.setdefault('effective_renewal', l.split(':',1)[1].strip())
        if l == 'Disposition Date:' and i+1 < len(lines):
            rec.setdefault('disposition_date', lines[i+1].strip())
        elif l.startswith('Disposition Date:') and len(l) > 17:
            rec.setdefault('disposition_date', l.split(':',1)[1].strip())
        if l.startswith('Overall Percentage of Last Rate Revision:'):
            v = l.split(':',1)[1].strip()
            if v: rec.setdefault('prior_revision_pct', num(v))
        if l == 'Filing Type:' and i+1 < len(lines):
            rec.setdefault('filing_type', lines[i+1].strip())
        elif l.startswith('Filing Type:') and len(l) > 12:
            rec.setdefault('filing_type', l.split(':',1)[1].strip())
    # company rate table
    try: start = next(i for i,l in enumerate(lines) if l == 'Company Rate Information')
    except StopIteration: return rec
    name, vals = [], []
    for l in lines[start+1:]:
        if l.startswith('SERFF Tracking') or l == 'Rate Information': break
        if not l: continue
        if l in ('Company','Name:'): continue
        if l == '%':
            vals.append(('blank', None)); continue
        if PCT.match(l):   vals.append(('pct',   num(l))); continue
        if MONEY.match(l): vals.append(('money', num(l))); continue
        if NUM.match(l) and name:
            vals.append(('int', num(l)))
        else:
            if vals and name:                      # flush completed row
                rec['companies'].append(_row(name, vals)); name, vals = [], []
            if not any(k in l for k in ('Overall','Written','Number','Maximum','Minimum','Change','Impact','Indicated','Holders','Program','where req')):
                name.append(l)
    if vals and name: rec['companies'].append(_row(name, vals))
    return rec

def _row(name, toks):
    """toks: list of (kind, value) where kind in pct/money/int/blank.
    Columns: indicated(pct) impact(pct) wpchange(money) ph(int) wp(money) max(pct) min(pct).
    Anchor on types, not position: the LAST money token is Written Premium,
    the int immediately before it is Policyholders, any money before that is WP Change."""
    money_ix = [i for i,(k,_) in enumerate(toks) if k=='money']
    wp = wpc = ph = None
    if money_ix:
        wp = toks[money_ix[-1]][1]
        for i in range(money_ix[-1]-1, -1, -1):
            if toks[i][0]=='int': ph = toks[i][1]; break
            if toks[i][0]=='money': break
        if len(money_ix) >= 2: wpc = toks[money_ix[-2]][1]
    else:
        ints=[v for k,v in toks if k=='int']
        if ints: ph = ints[-1]
    lead = [v for k,v in toks[:money_ix[0] if money_ix else len(toks)] if k in ('pct','blank')]
    ind  = lead[0] if len(lead)>0 else None
    imp  = lead[1] if len(lead)>1 else None
    return {'entity': ' '.join(name).strip(), 'indicated_pct': ind, 'overall_pct': imp,
            'written_premium_change': wpc, 'affected': int(ph) if ph is not None else None,
            'written_premium': wp}

if __name__ == '__main__':
    out = [parse(p) for p in sorted(glob.glob(os.path.join(TXT,'*.txt')))]
    json.dump(out, open('/tmp/oh_parsed.json','w'), indent=1)
    got = sum(1 for r in out if r['companies'])
    print(f"parsed {len(out)} jackets; {got} with a rate table; {len(out)-got} without")
