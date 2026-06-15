import os, re, collections
TOOLS = {"/","/index.html","/coverage.html","/renters/","/renters/index.html","/renters/coverage.html","/home/","/home/index.html","/home/coverage.html"}
RATE = {"/","/index.html","/renters/","/renters/index.html","/home/","/home/index.html"}
COV  = {"/coverage.html","/renters/coverage.html","/home/coverage.html"}
href = re.compile(r'href="([^"#]+)"')
pages=[]; dead=collections.Counter(); inbound=collections.Counter()
def exists(t):
    t=t.split("?")[0]
    if t.startswith("http") or t.startswith("mailto"): return True
    if t in ("/","/index.html"): return os.path.exists("index.html")
    if t.endswith("/"): return os.path.exists(t.lstrip("/")+"index.html")
    return os.path.exists(t.lstrip("/"))
for root,_,files in os.walk("."):
    if "/.git" in root: continue
    for fn in files:
        if not fn.endswith(".html"): continue
        p=os.path.join(root,fn); rel=p[1:]  # leading . -> /path
        s=open(p,encoding="utf-8").read()
        hrefs=set(m.group(1) for m in href.finditer(s))
        internal=[h for h in hrefs if h.startswith("/") and not h.startswith("//")]
        for h in internal:
            if not exists(h): dead[h]+=1
            norm=h.split("?")[0]
            if norm in TOOLS: inbound[norm]+=1
        has_rate=any(h.split("?")[0] in RATE for h in internal)
        has_cov =any(h.split("?")[0] in COV for h in internal)
        pages.append((rel,has_rate,has_cov))
print("=== TOTAL pages:",len(pages))
print("=== DEAD internal link targets (top 25) ===")
for t,c in dead.most_common(25): print(f"  {c:4d}  {t}")
print("=== inbound links to each TOOL dest ===")
for t in sorted(TOOLS): print(f"  {inbound.get(t,0):5d}  {t}")
nr=[p for p,r,c in pages if not r]; nc=[p for p,r,c in pages if not c]
print("=== pages with NO rate-tool link:",len(nr))
for p in nr[:30]: print("   ",p)
print("=== pages with NO coverage-tool link:",len(nc))
for p in nc[:30]: print("   ",p)
