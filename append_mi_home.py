#!/usr/bin/env python3
"""Append MI HOME rows to serff_home_filings.json + build MI renters ledger.
Home schema adds line/product. Renters (04.0004 standalones) go to a SEPARATE
serff_renters_filings.json — the first primary-sourced renters data."""
import json, datetime, os
FAM={'FABF':'Auto Club Group (AAA)','SFMA':'State Farm','AOIC':'Auto-Owners','FRNK':'Frankenmuth Insurance',
'FRIC':'Fremont','MEEM':'MEEMIC','FBMI':'Michigan Farm Bureau','PSMI':'Pioneer State Mutual','HAST':'Hastings Mutual',
'WOMI':'Wolverine Mutual','MBPI':'Michigan Basic','HART':'The Hartford','LBPM':'Safeco','ACEH':'Chubb','PRIV':'PURE',
'CEMC':'Central','DNGL':'Donegal Insurance','HRMN':'Teachers','AMMA':'Amica','APCG':'AIG','HMSS':'Homesite',
'BKON':'Berkley','ARMD':'Armed Forces','FARM':'Farmers','FAIG':'Farmers','MUOF':'POM','HNVR':'The Hanover',
'ALSE':'Allstate','UNKP':'Technology','SPRO':'Accelerant'}
RENT={'LBPM-134825970','ALSE-134767745','UNKP-134572731','SPRO-G134909041'}
def iso(d):
    if not d or '/' not in d: return None
    m,dd,y=d.split('/'); return f"{y}-{m}-{dd}"
parsed=json.load(open('/tmp/oh_parsed.json'))
today=datetime.date.today().isoformat()

def make(j,line,product,source):
    cands=[c for c in j['companies'] if c['overall_pct'] is not None and (c['affected'] or c['written_premium'])]
    if not cands: return None
    dom=max(cands,key=lambda c:(c['affected'] or 0,c['written_premium'] or 0))
    # Liberty entity: Safeco vs Liberty Mutual
    fam=FAM.get(j['tracking'].split('-')[0],j['tracking'].split('-')[0])
    ent_raw=dom['entity'] or ''
    if j['tracking'].split('-')[0]=='LBPM' and 'Safeco' not in ent_raw:
        fam='Liberty Mutual' if 'Liberty' in ent_raw else ('American Economy' if 'Economy' in ent_raw else fam)
    ent=ent_raw.replace('Rate Premium for ','').strip()
    if len(cands)>1: ent+=f" (dominant of {len(cands)} entities)"
    if not dom['affected'] and dom['overall_pct']==0: ent+=" (rate-neutral: 0% impact, 0 PH - NOT a rate change)"
    return {'state':'MI','line':line,'carrier':fam,'entity':ent,'tracking':j['tracking'],
        'url':f"https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId={j['tracking'].split('-',1)[1].lstrip('G')}",
        'product':product,'filing_type':j.get('filing_type') or None,
        'disposition_date':iso(j.get('disposition_date')),
        'effective_new':iso(j.get('effective_new')),'effective_renewal':iso(j.get('effective_renewal')),
        'overall_pct':dom['overall_pct'],'indicated_pct':dom['indicated_pct'],'prior_revision_pct':j.get('prior_revision_pct'),
        'written_premium':dom['written_premium'],'written_premium_change':dom['written_premium_change'],
        'affected':dom['affected'],'count_basis':'policyholders','coverage_changes':None,'premium_as_of':None,
        'note':None,'source_note':f'MI DIFS SERFF {j["tracking"]}','status':j.get('filing_type') or None,'recorded_date':today}

# HOME
hled=json.load(open('serff_home_filings.json')); hrows=hled if isinstance(hled,list) else hled['filings']
hexist={r['tracking'] for r in hrows}
hnew=[]
for j in parsed:
    if j['tracking'] in RENT or not j['companies'] or j['tracking'] in hexist: continue
    row=make(j,'home','Homeowners','MI DIFS')
    if row: hnew.append(row)
hrows.extend(hnew); json.dump(hled,open('serff_home_filings.json','w'),indent=1)
print(f"HOME: appended {len(hnew)}; home ledger now {len(hrows)}")

# RENTERS (new ledger)
rpath='serff_renters_filings.json'
rled=json.load(open(rpath)) if os.path.exists(rpath) else {"_meta":{"purpose":"Primary-sourced renters (HO-4/Tenant, SERFF 04.0004) rate filings. THIN by nature — most carriers bundle renters into the homeowners combo (blended, not separable), so standalone tenant rate filings are rare."},"filings":[]}
rrows=rled['filings']; rexist={r['tracking'] for r in rrows}
rnew=[]
for j in parsed:
    if j['tracking'] not in RENT or j['tracking'] in rexist: continue
    row=make(j,'renters','Renters (HO-4)','MI DIFS')
    if row: rnew.append(row)
rrows.extend(rnew); json.dump(rled,open(rpath,'w'),indent=1)
print(f"RENTERS: created/updated ledger with {len(rnew)} rows (total {len(rrows)})")
import collections
print("home carriers:",dict(collections.Counter(r['carrier'] for r in hnew)))
print("renters:",[(r['carrier'],r['overall_pct'],r['affected']) for r in rnew])
