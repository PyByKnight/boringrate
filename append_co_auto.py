#!/usr/bin/env python3
"""Append CO personal-auto rows to serff_filings.json (2026-11-18 pull).

Run `python3 parse_ga_jackets.py CO_auto` first (reads _serff/CO_auto/<ID>/<ID>.pdf).
Pull list: ~/co_auto_jackets.html; candidate families in _serff/CO_auto/candidates.tsv.

Ledger convention (matches OH/PA): one row per jacket on the DOMINANT entity
(tagged "dominant of N entities"), sibling entities as <tracking>-2, -3 ...
Zero-book entities (0 PH and $0 WP) are dropped. CO is file & use, so dates
come from the requested fields and rows carry effective_is_requested.
ADD-ONLY: an existing tracking is never touched.
"""
import json, datetime, csv

FAM = {'SFMA': 'State Farm', 'ALSE': 'Allstate', 'USAA': 'USAA', 'FARM': 'Farmers', 'FAIG': 'Farmers',
       'LBPM': 'Liberty Mutual', 'TRVD': 'Travelers', 'NWPP': 'Nationwide', 'AMFC': 'American Family',
       'PRCA': 'American Family', 'GECC': 'GEICO', 'SFBC': 'Colorado Farm Bureau', 'GMMX': 'National General',
       'WSUN': 'CSAA', 'PERR': 'Safeway', 'BRWS': 'Bristol West', 'SHEL': 'Shelter', 'CLIN': 'Root',
       'CFPC': 'Country Financial', 'AOIC': 'Auto-Owners', 'PRGS': 'Progressive', 'PGAC': 'The General',
       'VKNG': 'Dairyland', 'HART': 'The Hartford', 'UTRN': 'Kemper'}
# Safeco books file under LBPM as American Economy; roster_name() keys Safeco off "Safeco" in entity.
SAFECO_ENT = ('American Economy', 'Safeco')
# Source-jacket sign conflicts (% impact vs $ WP change disagree in SERFF itself) - recorded as filed.
NOTES = {
    'SFBC-134867882': 'Jacket conflict: Overall % Rate Impact -5.0% but WP change +$1,387,886 (+5.0% of WP). '
                      'Recorded as filed; sign unverified.',
    'GMMX-134857795': 'Jacket conflict: Overall % Rate Impact -1.4% but WP change +$163,525 (+1.4% of WP). '
                      'Recorded as filed; sign unverified.',
}
WINDOW_START = '2025-07-01'

def iso(d):
    if not d or '/' not in d: return None
    m, dd, y = d.split('/'); return f"{y}-{m}-{dd}"

product = {}
for r in csv.reader(open('_serff/CO_auto/candidates.tsv'), delimiter='\t'):
    if r and not r[0].startswith('#'): product[r[0]] = (r[2], r[3])

parsed = json.load(open('_serff/CO_auto/_parsed.json'))
led = json.load(open('serff_filings.json'))
rows = led if isinstance(led, list) else led['filings']
existing = {r['tracking'] for r in rows}
today = datetime.date.today().isoformat()
new, skipped = [], []
for t, j in sorted(parsed.items()):
    if t in existing: continue
    disp = iso(j.get('disposition'))
    if disp and disp < WINDOW_START:
        skipped.append((t, f'pre-window {disp}')); continue
    cos = [c for c in j['companies'] if c['impact'] is not None and (c['affected'] or c['wp'])]
    if not cos:
        skipped.append((t, 'no usable rate rows')); continue
    cos.sort(key=lambda c: (c['affected'] or 0, c['wp'] or 0), reverse=True)
    fam = FAM[t.split('-')[0]]
    prod, ftype = product.get(t, ('PPA', None))
    for i, c in enumerate(cos):
        ent = c['entity']
        if fam == 'Liberty Mutual' and ent.startswith(SAFECO_ENT[0]): ent += ' (Safeco)'
        if i == 0 and len(cos) > 1: ent += f' (dominant of {len(cos)} entities)'
        if not c['affected'] and c['impact'] == 0:
            ent += ' (rate-neutral: 0% impact, 0 PH - NOT a rate change)'
        row = {'state': 'CO', 'carrier': fam, 'entity': ent,
               'tracking': t if i == 0 else f'{t}-{i + 1}',
               'url': f"https://serff-sfa.naic.org/serff/sfa/search/filingSummary.xhtml?filingId={t.split('-', 1)[1].lstrip('G')}",
               'product': prod, 'filing_type': ftype, 'disposition_date': disp,
               'effective_new': iso(j.get('eff_new')), 'effective_renewal': iso(j.get('eff_ren')),
               'overall_pct': c['impact'], 'indicated_pct': c['indicated'], 'prior_revision_pct': None,
               'max_pct': c['max_pct'], 'min_pct': c['min_pct'],
               'written_premium': c['wp'], 'written_premium_change': c['wp_change'],
               'affected': c['affected'], 'count_basis': 'policyholders',
               'coverage_changes': None, 'premium_as_of': None, 'recorded_date': today}
        if j.get('eff_requested'): row['effective_is_requested'] = True
        if t in NOTES and i == 0: row['note'] = NOTES[t]; row['drift_exclude'] = True
        new.append(row)
rows.extend(new)
json.dump(led, open('serff_filings.json', 'w'), indent=1)
print(f"appended {len(new)} CO auto rows ({len({r['url'] for r in new})} jackets); ledger now {len(rows)}")
for t, why in skipped: print('  skipped', t, why)
