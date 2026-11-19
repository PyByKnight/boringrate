#!/usr/bin/env python3
"""Templated-prose audit: share of each INDEXABLE page family's body text that also appears
(numbers normalized) on 3+ other indexable pages. Tables, nav, header, footer, scripts excluded;
noindexed pages skipped (they don't count toward site quality).

Why: AdSense rejected the site for content quality 2026-11-17; the 11-19 audit found trackers
50-62%, home why-pages 43%, renters state 37% repeated, all cut to <=19%. Rule: repeated LAYOUT
is fine, repeated PROSE is not (memory boringrate-unique-content-rule).

    python3 audit_templated_prose.py          # table; WARN for families over LIMIT
"""
import re,glob,collections,sys,html as H
LIMIT = 0.25
def body(s):
    s=re.sub(r'(?s)<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<header.*?</header>|<footer.*?</footer>|<div class="nav-mega".*?</div></div></div></div>','',s)
    m=re.search(r'(?s)<main.*?</main>|<article.*?</article>|<div class="article-body">.*',s)
    s=m.group(0) if m else s
    s=re.sub(r'(?s)<table.*?</table>','',s)  # tables = data, not prose
    t=H.unescape(re.sub(r'<[^>]+>',' ',s))
    return re.sub(r'\s+',' ',t)
def sents(t):
    out=[]
    for x in re.split(r'(?<=[.?!])\s+',t):
        x=x.strip()
        if len(x.split())<6: continue
        k=re.sub(r'[$]?[-+−]?\d[\d,.]*%?','#',x.lower())
        out.append((x,k))
    return out
pages={}
for f in glob.glob('**/*.html',recursive=True):
    if f.startswith(('_','node_modules','partials')) or 'gen_' in f: continue
    s=open(f,errors='ignore').read()
    if re.search(r'<meta name="robots" content="noindex', s): continue
    pages[f]=sents(body(s))
cnt=collections.Counter()
for f,ss in pages.items():
    for k in {k for _,k in ss}: cnt[k]+=1
def fam(f):
    d=f.rsplit('/',1)[0] if '/' in f else '(root)'
    n=f.rsplit('/',1)[-1]
    if 'why-did-my' in n: return d+'/why-did-my'
    m=re.match(r'([a-z]+-[a-z]+)-',n)
    return d
rows=collections.defaultdict(list)
for f,ss in pages.items():
    w=sum(len(x.split()) for x,_ in ss)
    rep=sum(len(x.split()) for x,k in ss if cnt[k]>=3)
    rows[fam(f)].append((f,w,rep))
print(f"{'family':38}{'pages':>6}{'med words':>10}{'% repeated':>11}")
res=[]
for k,v in rows.items():
    W=sum(w for _,w,_ in v); R=sum(r for *_,r in v)
    med=sorted(w for _,w,_ in v)[len(v)//2]
    res.append((R/W if W else 0,k,len(v),med))
for p,k,n,med in sorted(res,reverse=True):
    print(f"{k:38}{n:6}{med:10}{p*100:10.0f}%")
bad=[(k,p) for p,k,n,med in res if p>LIMIT and n>=3]
for k,p in bad: print(f"WARN: {k} is {p*100:.0f}% repeated prose (limit {LIMIT*100:.0f}%)")
print(f"templated prose: {len(bad)} family(ies) over limit")
