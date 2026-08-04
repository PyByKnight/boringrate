#!/usr/bin/env python3
"""Append LA auto rows to serff_filings.json (dominant entity per jacket).
Maps family by ENTITY NAME (LA shares the GMMX filer code across Imperial/Encompass/NatGen).
Excludes the State Farm Classic collector filing (garbage parse: +46% / max 1347%)."""
import json, datetime

# (substring, family) — first match wins; None = exclude
ENTMAP = [
    ('State Farm Classic', None),            # collector program — bad parse, exclude
    ('State Farm', 'State Farm'), ('Progressive', 'Progressive'), ('GEICO', 'GEICO'),
    ('Allstate', 'Allstate'), ('Encompass', 'Encompass'), ('Amica', 'Amica'),
    ('American National', 'American National'), ('AIG', 'AIG'), ('Foremost', 'Bristol West'),
    ('Root', 'Root'), ('Imperial', 'Imperial'), ('Midvale', 'American Family'),
    ('Hugo', 'Hugo'), ('GM National', 'GM National'), ('Privilege Underwriters', 'PURE'),
    ('Southern Farm Bureau', 'Louisiana Farm Bureau'), ('Shelter', 'Shelter'),
    ('Vault', 'Vault'), ('United Services Automobile', 'USAA'), ('USAA', 'USAA'),
    ('Automobile Club', 'AAA'), ('Old American', 'Old American'),
    ('General Insurance Company', 'Liberty Mutual'), ('Safeco', 'Safeco'),
    ('Safeway', 'Safeway'), ('GoAuto', 'GoAuto'), ('Cincinnati', 'Cincinnati'),
]
WINDOW_START = '2025-07-01'  # dataset window; skips the out-of-window 2024 Safeway filing pulled for context
def fam_of(ent):
    for sub, fam in ENTMAP:
        if sub.lower() in ent.lower():
            return fam  # may be None (exclude)
    return '??'

def iso(d):
    if not d or '/' not in d: return None
    m, dd, y = d.split('/'); return f"{y}-{m}-{dd}"

parsed = json.load(open('/tmp/oh_parsed.json'))
led = json.load(open('serff_filings.json'))
rows = led if isinstance(led, list) else led['filings']
existing = {r['tracking'] for r in rows}
today = datetime.date.today().isoformat()
new, skipped = [], []
for j in parsed:
    if not j.get('companies') or j['tracking'] in existing: continue
    _disp = iso(j.get('disposition_date'))
    if _disp and _disp < WINDOW_START:
        skipped.append((j['tracking'], f'pre-window {_disp} (context only)')); continue
    cands = [c for c in j['companies'] if c['overall_pct'] is not None
             and (c['affected'] or c['written_premium'])]
    if not cands: continue
    dom = max(cands, key=lambda c: (c['affected'] or 0, c['written_premium'] or 0))
    ent_clean = dom['entity'].replace('Rate Premium for ', '').strip()
    fam = fam_of(ent_clean)
    if fam is None:
        skipped.append((j['tracking'], ent_clean)); continue
    if fam == '??':
        skipped.append((j['tracking'], 'UNMAPPED: ' + ent_clean)); continue
    ent = ent_clean
    if len(cands) > 1: ent += f" (dominant of {len(cands)} entities)"
    if not dom['affected'] and dom['overall_pct'] == 0:
        ent += " (rate-neutral: 0% impact, 0 policyholders affected - NOT a rate change)"
    new.append({
        'state': 'LA', 'carrier': fam, 'entity': ent, 'tracking': j['tracking'],
        'url': f"https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId={j['tracking'].split('-',1)[1].lstrip('G')}",
        'product': 'PPA', 'filing_type': j.get('filing_type') or None,
        'disposition_date': iso(j.get('disposition_date')),
        'effective_new': iso(j.get('effective_new')), 'effective_renewal': iso(j.get('effective_renewal')),
        'overall_pct': dom['overall_pct'], 'indicated_pct': dom['indicated_pct'],
        'prior_revision_pct': j.get('prior_revision_pct'),
        'written_premium': dom['written_premium'], 'written_premium_change': dom['written_premium_change'],
        'affected': dom['affected'], 'count_basis': 'policyholders',
        'max_pct': dom.get('max_pct'), 'min_pct': dom.get('min_pct'),
        'coverage_changes': None, 'premium_as_of': None, 'recorded_date': today})
rows.extend(new)
json.dump(led, open('serff_filings.json', 'w'), indent=1)
print(f"appended {len(new)} LA rows; ledger now {len(rows)}")
for t, e in skipped: print('  skipped', t, e)
