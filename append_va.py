#!/usr/bin/env python3
"""Append VA auto rows to serff_filings.json (one row per jacket, dominant entity).
Stores max_pct/min_pct (within-filing spread) — tier-1 content juice. Canonical
carrier names so drift/verifier/tracker link."""
import json, datetime
FAM={'USAA':'USAA','GECC':'GEICO','SFMA':'State Farm','ALSE':'Allstate','PRGS':'Progressive','ERAP':'Erie',
'VRFB':'Virginia Farm Bureau','EINS':'Elephant','FARM':'Farmers','FAIG':'Farmers','LBPM':'Liberty Mutual',
'AOIC':'Auto-Owners','CNNB':'Cincinnati Insurance','AMMA':'Amica','MERY':'Mercury','IACA':'Auto Club Group (AAA)',
'WSUN':'CSAA','GMMX':'National General','HART':'The Hartford','PNPR':'Penn National','NWPP':'Nationwide',
'TRVD':'Travelers','HNVR':'The Hanover','RMUT':'Rockingham','DNGL':'Donegal Insurance','VSGP':'Trexis',
'UTCX':'Utica/Republic-Franklin','ACUT':'Acuity','CEMC':'Central','GRAN':'Grange','CLEA':'Clearcover',
'TSIS':'Tesla','AGMK':'Toggle','SPIS':'Vault','ANPC':'American National','PRCA':'American Family',
'ASRN':'AssuranceAmerica','PGAC':'The General','GNSC':'MGA Insurance','SELC':'Selective','CLIN':'Root',
'ONST':'GM National','VKNG':'Peak','REPW':'Repwest','GDMT':'Goodville','BRMT':'Brethren Mutual',
'AUGU':'Augusta Mutual','MMGC':'MMG','AICM':'Agency Ins of MD','BRWS':'Bristol West','FRST':'First Acceptance'}
def iso(d):
    if not d or '/' not in d: return None
    m,dd,y=d.split('/'); return f"{y}-{m}-{dd}"
parsed=json.load(open('/tmp/oh_parsed.json'))
led=json.load(open('serff_filings.json')); rows=led if isinstance(led,list) else led['filings']
existing={r['tracking'] for r in rows}
today=datetime.date.today().isoformat()
new=[]
for j in parsed:
    if not j['companies'] or j['tracking'] in existing: continue
    cands=[c for c in j['companies'] if c['overall_pct'] is not None and (c['affected'] or c['written_premium'])]
    if not cands: continue
    dom=max(cands,key=lambda c:(c['affected'] or 0,c['written_premium'] or 0))
    fam=FAM.get(j['tracking'].split('-')[0],j['tracking'].split('-')[0])
    ent=dom['entity'].replace('Rate Premium for ','').strip()
    if len(cands)>1: ent+=f" (dominant of {len(cands)} entities)"
    if not dom['affected'] and dom['overall_pct']==0: ent+=" (rate-neutral: 0% impact, 0 PH - NOT a rate change)"
    new.append({'state':'VA','carrier':fam,'entity':ent,'tracking':j['tracking'],
        'url':f"https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId={j['tracking'].split('-',1)[1].lstrip('G')}",
        'product':'PPA','filing_type':j.get('filing_type') or None,
        'disposition_date':iso(j.get('disposition_date')),
        'effective_new':iso(j.get('effective_new')),'effective_renewal':iso(j.get('effective_renewal')),
        'overall_pct':dom['overall_pct'],'indicated_pct':dom['indicated_pct'],'prior_revision_pct':j.get('prior_revision_pct'),
        'max_pct':dom.get('max_pct'),'min_pct':dom.get('min_pct'),
        'written_premium':dom['written_premium'],'written_premium_change':dom['written_premium_change'],
        'affected':dom['affected'],'count_basis':'policyholders','coverage_changes':None,'premium_as_of':None,'recorded_date':today})
rows.extend(new)
json.dump(led,open('serff_filings.json','w'),indent=1)
print(f"appended {len(new)} VA rows; ledger now {len(rows)}")
import collections
print("VA carriers:",dict(collections.Counter(r['carrier'] for r in new)))
