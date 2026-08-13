#!/usr/bin/env python3
"""Append NJ both-boxes pull: auto -> serff_filings.json, home -> serff_home_filings.json.
Maps family by ENTITY NAME; dedups by tracking (home refresh mostly re-hits July filings).
Product split is by tracking (AUTO_TRK); everything else parsed is home."""
import json, datetime
today = datetime.date.today().isoformat()

AUTO_TRK = {'ALSE-134914761','ALSE-134675302','APCG-134652591','BRWS-134378141','CURE-134400950',
    'CURE-134612398','FARM-134703203','GECC-134961490','GMMX-134649881','GMMX-134806021','HART-134610008',
    'HMSS-134633195','HPIC-134859181','LBPM-134577831','MERY-134759707','NJMI-134601162','PRIV-134638422',
    'SELC-134599344','SFMA-134653651','SPIS-134715716','USAA-134719983','PRGS-134675345','PRGS-134675404','AMMA-134740625'}

def fam(ent):
    e = ent.lower()
    table = [('new jersey manufa','NJM Insurance'),('njm','NJM Insurance'),('state farm','State Farm'),
        ('government employees','GEICO'),('geico','GEICO'),('allstate','Allstate'),('palisades','Palisades'),
        ('foremost','Bristol West'),('selective','Selective Insurance'),('farmers','Farmers'),
        ('encompass','Encompass'),('mercury','Mercury Insurance'),('privilege underwr','PURE'),('aig','AIG'),
        ('hartford','The Hartford'),('national general','National General'),('vault','Vault'),
        ('citizens united','CURE'),('cure','CURE'),('usaa','USAA'),
        # home-only regionals
        ('germantown','Plymouth Rock'),('plymouth','Plymouth Rock'),('homesite','Homesite'),
        ('stillwater','Stillwater'),('preferred mutual','Preferred Mutual'),('cumberland','Cumberland Insurance'),
        ('narragansett','Narragansett Bay'),('norfolk','Norfolk & Dedham'),('franklin','Franklin Mutual'),
        ('fmi','Franklin Mutual'),('providence','Providence'),('amica','Amica'),('hanover','The Hanover')]
    for sub, f in table:
        if sub in e: return f
    return '??'

def iso(d):
    if not d or '/' not in d: return None
    m, dd, y = d.split('/'); return f"{y}-{m}-{dd}"

def dom_of(j):
    cands = [c for c in (j.get('companies') or []) if c['overall_pct'] is not None and (c['affected'] or c['written_premium'])]
    if not cands: return None, 0
    return max(cands, key=lambda c: (c['affected'] or 0, c['written_premium'] or 0)), len(cands)

parsed = json.load(open('/tmp/oh_parsed.json'))
auto_led = json.load(open('serff_filings.json')); auto_rows = auto_led['filings']
home_led = json.load(open('serff_home_filings.json')); home_rows = home_led['filings']
auto_have = {r['tracking'] for r in auto_rows}; home_have = {r['tracking'] for r in home_rows}
url = lambda t: f"https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId={t.split('-',1)[1].lstrip('G')}"
na, nh, skip = 0, 0, []
for j in parsed:
    t = j['tracking']; dom, nc = dom_of(j)
    if dom is None: continue
    ent = dom['entity'].replace('Rate Premium for ', '').strip()
    f = fam(ent)
    if f == '??': skip.append((t, ent)); continue
    if nc > 1: ent += f" (dominant of {nc} entities)"
    if not dom['affected'] and dom['overall_pct'] == 0: ent += " (rate-neutral: 0% - NOT a rate change)"
    common = dict(carrier=f, entity=ent, tracking=t, url=url(t), filing_type=j.get('filing_type') or None,
        disposition_date=iso(j.get('disposition_date')), effective_new=iso(j.get('effective_new')),
        effective_renewal=iso(j.get('effective_renewal')), overall_pct=dom['overall_pct'],
        indicated_pct=dom['indicated_pct'], prior_revision_pct=j.get('prior_revision_pct'),
        written_premium=dom['written_premium'], written_premium_change=dom['written_premium_change'],
        affected=dom['affected'], count_basis='policyholders', max_pct=dom.get('max_pct'),
        min_pct=dom.get('min_pct'), coverage_changes=None, premium_as_of=None, recorded_date=today)
    if t in AUTO_TRK:
        if t in auto_have: continue
        auto_rows.append(dict(state='NJ', product='PPA', **common)); na += 1
    else:
        if t in home_have: continue
        r = dict(state='NJ', line='home', product='HO', **common)
        r.update(status=j.get('filing_type') or None, source_note=f'NJ DOBI SERFF {t}', note=None)
        home_rows.append(r); nh += 1
json.dump(auto_led, open('serff_filings.json', 'w'), indent=1)
json.dump(home_led, open('serff_home_filings.json', 'w'), indent=1)
print(f"NJ appended: {na} auto rows, {nh} home rows")
for t, e in skip: print('  UNMAPPED', t, e)
