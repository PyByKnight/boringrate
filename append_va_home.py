#!/usr/bin/env python3
"""Append the VA homeowners pull -> serff_home_filings.json (+ 4 renters new-program rows
-> serff_renters_filings.json). Reads the parse_oh.py output for _serff/VA_home_txt.

Multi-entity filings collapse to one row on the DOMINANT entity (existing home-store
convention, 0 suffixed rows there), but overall_pct is the PREMIUM-WEIGHTED family average
and affected/written_premium are sums -- the TN tracker precedent -- so USAA's 4-entity
spread isn't misread as its largest entity's number.
"""
import json, datetime, sys

today = datetime.date.today().isoformat()
PARSED = sys.argv[1] if len(sys.argv) > 1 else '/tmp/oh_parsed.json'

FAM = [('allstate vehicle', 'Allstate'), ('allstate north american', 'Allstate'), ('allstate', 'Allstate'),
       ('amica', 'Amica'), ('american strategic', 'Progressive'), ('auto-owners', 'Auto-Owners'),
       ('erie', 'Erie'), ('farmers insurance exchange', 'Farmers'), ('fire insurance exchange', 'Farmers'),
       ('mid-century', 'Farmers'), ('truck insurance exchange', 'Farmers'), ('homesite', 'Homesite'),
       ('liberty mutual', 'Liberty Mutual'), ('nationwide', 'Nationwide'), ('state farm', 'State Farm'),
       ('garrison', 'USAA'), ('usaa', 'USAA'), ('united services automobile', 'USAA'),
       ('virginia farm bureau', 'Virginia Farm Bureau'), ('hartford', 'The Hartford'),
       ('national general', 'National General'), ('mic general', 'Allstate'), ('new south', 'Allstate')]

def fam(ent):
    e = ent.lower()
    for sub, f in FAM:
        if sub in e:
            return f
    return '??'

def iso(d):
    if not d or '/' not in d:
        return None
    m, dd, y = d.split('/')
    return f"{y}-{m}-{dd}"

url = lambda t: f"https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId={t.split('-', 1)[1].lstrip('G')}"

# Rule-only / revenue-neutral jackets: "Rate data does NOT apply to filing" + 0.000% impact,
# $0 WP change, 0 policyholders. Real filings on real books, so they belong in the open-book
# ledger at 0.0%, but they are NOT rate changes and stay out of the display tracker.
NEUTRAL = {
    'ALSE-134914653': ('Allstate', 'Allstate Insurance Company / Allstate Vehicle and Property (multi-entity)',
                       'R60476 MPD/qualifying-company rule update - manual pages only, no rate impact.'),
    'HART-134606166': ('The Hartford', 'Hartford Fire / Hartford Underwriters / Trumbull / Twin City (multi-entity)',
                       'VA Home Advantage rule-page revision - no rate impact.'),
    'NWPP-134498871': ('Nationwide', 'Nationwide multi-entity (filed for all except Allied P&C)',
                       'NGI rate-manual revision - no rate impact. VA DOI noted it was filed for all companies '
                       'except Allied Property and Casualty.'),
    'LBPM-135016955': ('Liberty Mutual', 'Liberty Mutual multi-entity',
                       'Rating-manual page revision - no rate impact.'),
}

# Renters: every 04.0004 jacket came back "Rate data does NOT apply" and the downloads carried
# no Rate/Rule attachments, so there are no percentages and no base rates to extract. The four
# below are NEW PROGRAM launches -- recorded as market-entry facts (overall_pct null), not rates.
RENTERS_NEW = {
    'ALSE-134750995': ('Allstate', 'Allstate North American Insurance Company', 'ANAIC REN',
                       'Introduction of ANAIC Renters (R59673).'),
    'GMMX-134712870': ('National General', 'National General Insurance Company', 'VA_NGIC_R8M Renters',
                       'New renters program.'),
    'GMMX-134712892': ('Allstate', 'MIC General Insurance Corporation', 'VA_MICG_R8VRV Renters',
                       'New renters program (Allstate-family non-standard entity).'),
    'GMMX-134712828': ('Allstate', 'New South Insurance Company', 'VA_NSIC_R8 Renters',
                       'New renters program (Allstate-family non-standard entity).'),
}

parsed = {r['tracking']: r for r in json.load(open(PARSED))}

home_led = json.load(open('serff_home_filings.json'))
home_rows = home_led['filings']
home_have = {r['tracking'] for r in home_rows}
rent_led = json.load(open('serff_renters_filings.json'))
rent_rows = rent_led['filings'] if isinstance(rent_led, dict) else rent_led
rent_have = {r['tracking'] for r in rent_rows}

nh = nr = 0
skipped = []

for t, j in sorted(parsed.items()):
    if t in RENTERS_NEW:
        if t in rent_have:
            continue
        carrier, entity, product, note = RENTERS_NEW[t]
        rent_rows.append(dict(
            state='VA', line='renters', carrier=carrier, entity=entity, tracking=t, url=url(t),
            product=product, filing_type=j.get('filing_type'), disposition_date=iso(j.get('disposition_date')),
            effective_new=iso(j.get('effective_new')), effective_renewal=iso(j.get('effective_renewal')),
            overall_pct=None, indicated_pct=None, prior_revision_pct=None, written_premium=None,
            written_premium_change=None, affected=None, count_basis=None, coverage_changes=None,
            premium_as_of=None, recorded_date=today, status='APPROVED',
            source_note=f'VA SCC Bureau of Insurance SERFF {t}',
            note=note + ' New program - no rate impact filed (base rates not in the public jacket).'))
        nr += 1
        continue

    if t in home_have:
        continue

    if t in NEUTRAL:
        carrier, entity, note = NEUTRAL[t]
        home_rows.append(dict(
            state='VA', line='home', carrier=carrier, entity=entity, tracking=t, url=url(t),
            product='HO', filing_type=j.get('filing_type'), disposition_date=iso(j.get('disposition_date')),
            effective_new=iso(j.get('effective_new')), effective_renewal=iso(j.get('effective_renewal')),
            overall_pct=0.0, indicated_pct=None, prior_revision_pct=j.get('prior_revision_pct'),
            written_premium=None, written_premium_change=None, affected=None, count_basis=None,
            max_pct=None, min_pct=None, coverage_changes=None, premium_as_of=None, recorded_date=today,
            status=j.get('filing_type'), source_note=f'VA SCC Bureau of Insurance SERFF {t}',
            note=note + ' Rate-neutral: kept in the ledger, excluded from the tracker.'))
        nh += 1
        continue

    cos = [c for c in j['companies'] if c['overall_pct'] is not None]
    if not cos:
        skipped.append((t, 'no rate table'))
        continue

    dom = max(cos, key=lambda c: (c['written_premium'] or 0, c['affected'] or 0))
    entity = dom['entity'].replace('Rate Premium for ', '').strip()
    carrier = fam(entity)
    if carrier == '??':
        skipped.append((t, f'unmapped entity: {entity}'))
        continue

    wp_tot = sum(c['written_premium'] or 0 for c in cos)
    ph_tot = sum(c['affected'] or 0 for c in cos)
    wpc_tot = sum(c['written_premium_change'] or 0 for c in cos)
    if len(cos) > 1 and wp_tot:
        pct = round(sum((c['overall_pct'] or 0) * (c['written_premium'] or 0) for c in cos) / wp_tot, 3)
        ind = [c['indicated_pct'] for c in cos if c['indicated_pct'] is not None]
        ind_pct = round(sum((c['indicated_pct'] or 0) * (c['written_premium'] or 0) for c in cos) / wp_tot, 3) if ind else None
        entity += f' (+{len(cos) - 1} entities, premium-weighted)'
    else:
        pct, ind_pct = dom['overall_pct'], dom['indicated_pct']

    home_rows.append(dict(
        state='VA', line='home', carrier=carrier, entity=entity, tracking=t, url=url(t),
        product='HO', filing_type=j.get('filing_type'), disposition_date=iso(j.get('disposition_date')),
        effective_new=iso(j.get('effective_new')), effective_renewal=iso(j.get('effective_renewal')),
        overall_pct=pct, indicated_pct=ind_pct, prior_revision_pct=j.get('prior_revision_pct'),
        written_premium=wp_tot or None, written_premium_change=wpc_tot or None,
        affected=ph_tot or None, count_basis='policyholders' if ph_tot else None,
        max_pct=dom.get('max_pct'), min_pct=dom.get('min_pct'), coverage_changes=None,
        premium_as_of=None, recorded_date=today, status=j.get('filing_type'),
        source_note=f'VA SCC Bureau of Insurance SERFF {t}', note=None))
    nh += 1

home_led['filings'] = home_rows
json.dump(home_led, open('serff_home_filings.json', 'w'), indent=1)
if isinstance(rent_led, dict):
    rent_led['filings'] = rent_rows
    json.dump(rent_led, open('serff_renters_filings.json', 'w'), indent=1)
else:
    json.dump(rent_rows, open('serff_renters_filings.json', 'w'), indent=1)

print(f'VA appended: {nh} home rows, {nr} renters rows')
for t, why in skipped:
    print(f'  skipped {t}: {why}')
