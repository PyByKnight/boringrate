#!/usr/bin/env python3
"""Append OH auto rows to serff_filings.json (one row per jacket, dominant entity)."""
import json, datetime
FAM={'SFMA':'State Farm','PRGS':'Progressive','GECC':'GEICO','ALSE':'Allstate','USAA':'USAA','ERAP':'Erie',
'FARM':'Farmers','FAIG':'Farmers','LBPM':'Liberty Mutual','AMFC':'American Family','PRCA':'American Family',
'NWPP':'Nationwide','TRVD':'Travelers','HNVR':'Hanover','GRAN':'Grange','MTRS':'Motorists','WSRG':'Westfield',
'CEMC':'Central','CEIN':'Celina','OHMG':'Ohio Mutual','CNNB':'Cincinnati','CLIN':'Root','ACUT':'Acuity',
'WSUN':'CSAA','IACA':'Auto Club','BUCK':'Buckeye','FRNK':'Frankenmuth','ACEH':'Chubb','SHEL':'Shelter',
'PKNS':'Pekin','GRCP':'Grinnell','DNGL':'Donegal','AMMA':'American Modern','GMMX':'Encompass','HAST':'Hastings',
'IFMI':'Indiana Farmers','WMIN':'Wayne Mutual','HRMN':'Harleysville','SELC':'Selective','HART':'The Hartford',
'NJMI':'NJM','AOIC':'Auto-Owners'}
def iso(d):
    if not d or '/' not in d: return None
    m,dd,y = d.split('/'); return f"{y}-{m}-{dd}"

parsed = json.load(open('/tmp/oh_parsed.json'))
led = json.load(open('serff_filings.json'))
rows = led if isinstance(led, list) else led['filings']
existing = {r['tracking'] for r in rows}
today = datetime.date.today().isoformat()
new = []
for j in parsed:
    if not j['companies'] or j['tracking'] in existing: continue
    cands = [c for c in j['companies'] if c['overall_pct'] is not None
             and (c['affected'] or c['written_premium'])]
    if not cands: continue
    # rank on policyholders; fall back to written premium for rate-neutral filings
    # (0% impact -> SERFF reports 0 affected, but the book is still real)
    dom = max(cands, key=lambda c: (c['affected'] or 0, c['written_premium'] or 0))
    fam = FAM.get(j['tracking'].split('-')[0], j['tracking'].split('-')[0])
    ent = dom['entity'].replace('Rate Premium for ','').strip()
    if fam == 'Nationwide':
        ent += ' (FLAG: single-entity filing — only in-window Nationwide rate filing; understates the OH book, do not present as family-wide)'
    if len(cands) > 1:
        ent += f" (dominant of {len(cands)} entities)"
    if not dom['affected'] and dom['overall_pct'] == 0:
        ent += " (rate-neutral: 0% impact, 0 policyholders affected - NOT a rate change)"
    new.append({
        'state':'OH','carrier':fam,'entity':ent,'tracking':j['tracking'],
        'url':f"https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId={j['tracking'].split('-',1)[1].lstrip('G')}",
        'product':'PPA','filing_type':j.get('filing_type') or None,
        'disposition_date':iso(j.get('disposition_date')),
        'effective_new':iso(j.get('effective_new')),'effective_renewal':iso(j.get('effective_renewal')),
        'overall_pct':dom['overall_pct'],'indicated_pct':dom['indicated_pct'],
        'prior_revision_pct':j.get('prior_revision_pct'),
        'written_premium':dom['written_premium'],'written_premium_change':dom['written_premium_change'],
        'affected':dom['affected'],'count_basis':'policyholders',
        'coverage_changes':None,'premium_as_of':None,'recorded_date':today})
rows.extend(new)
json.dump(led, open('serff_filings.json','w'), indent=1)
print(f"appended {len(new)} OH rows; ledger now {len(rows)}")
