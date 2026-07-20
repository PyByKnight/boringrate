#!/usr/bin/env python3
"""National rate-filings roll-up — the citable/linkable data asset (Fable #3).

One page: every captured 2026 auto + home rate filing, by state and carrier, each
row linked to its primary source (SERFF tracking # + the DOI portal/dataset). Rows
are server-rendered (crawlable + citable); vanilla JS adds sort/filter. Draws from
serff_filings.json (auto) + serff_home_filings.json (home). Output: rate-filings/index.html."""
import json, re, pathlib
from filing_cite import anchor, portal_url
from datetime import date
from gen_metro_page import STATE, esc
from plausible_snippet import ensure

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "rate-filings" / "index.html"
RED, GREEN, MUTE = "#b4321a", "#2f6b3a", "var(--ink-mute)"
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# NAIC national private-passenger-auto market share (%), keyed to filing carrier names.
# Auto only; home rows and regionals below the top-16 have no share.
_MS = json.load(open(ROOT / "market_share.json"))["national"]
_MS_ALIAS = {"Erie": "Erie Insurance", "Shelter": "Shelter Insurance"}


def market_share(carrier, product):
    if product != "Auto":
        return None
    return _MS.get(carrier) or _MS.get(_MS_ALIAS.get(carrier, ""))

scaff = (ROOT / "home" / "state" / "florida.html").read_text(encoding="utf-8")
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>") + len("</style>")]
NAV = scaff[scaff.index('<header class="top">'):scaff.index("</header>") + len("</header>")]
TAIL = scaff[scaff.index("<footer>"):]


def fdate(iso):
    if not iso:
        return ""
    p = iso.split("-")
    if len(p) == 1: return p[0]
    if len(p) == 2: return f"{MONTHS[int(p[1])]} {p[0]}"
    return f"{MONTHS[int(p[1])]} {int(p[2])}, {p[0]}"


def source_label(url, note):
    if "data.texas.gov" in url: return "TX TDI open data"
    if "insurance.ca.gov" in url: return "CA CDI filings list"
    if "filingaccess.serff.com" in url: return "SERFF Filing Access"
    if "irfssearch.floir.gov" in url or "floir" in url: return "FL FLOIR IRFS"
    if "newsroom" in url: return "Carrier newsroom"
    m = re.search(r"https?://([^/]+)", url)
    return m.group(1) if m else "source"


def collect():
    rows = []
    for r in json.load(open(ROOT / "serff_filings.json"))["filings"]:
        if r.get("overall_pct") is None: continue
        rows.append((r, "Auto"))
    for r in json.load(open(ROOT / "serff_home_filings.json"))["filings"]:
        if r.get("overall_pct") is None: continue
        rows.append((r, "Home"))
    out = []
    for r, product in rows:
        eff = r.get("effective_new") or r.get("effective_renewal") or r.get("disposition_date") or ""
        out.append({
            "state": r["state"], "product": product, "carrier": r["carrier"],
            "entity": r.get("entity") or "", "pct": r["overall_pct"],
            "eff": eff, "status": r.get("status") or ("Approved" if r.get("disposition_date") else ""),
            "tracking": r.get("tracking") or "", "url": r.get("url") or "",
            "src": source_label(r.get("url") or "", r.get("source_note") or ""),
            "share": market_share(r["carrier"], product),
        })
    # sort: biggest absolute move first (default view)
    out.sort(key=lambda x: (-abs(x["pct"]), x["state"]))
    return out


def build():
    data = collect()
    n_states = len({d["state"] for d in data})
    n_carriers = len({d["carrier"] for d in data})
    n_inc = sum(1 for d in data if d["pct"] > 0)
    n_dec = sum(1 for d in data if d["pct"] < 0)
    today = date.today()
    url = "https://boringrate.com/rate-filings/"
    title = "2026 U.S. Auto & Home Insurance Rate Filings — By State & Carrier"
    desc = (f"A primary-source roll-up of {len(data)} approved 2026 auto and homeowners insurance rate "
            f"filings across {n_states} states, each linked to its state DOI source. Sortable and filterable.")

    # filter controls
    state_opts = "".join(f'<option value="{s}">{esc(STATE[s][0])}</option>' for s in sorted({d["state"] for d in data}, key=lambda c: STATE[c][0]))
    controls = f'''<div class="rf-controls">
      <input id="rfSearch" type="search" placeholder="Search carrier…" aria-label="Search carrier" />
      <select id="rfProduct" aria-label="Product"><option value="">All products</option><option value="Auto">Auto</option><option value="Home">Home</option></select>
      <select id="rfState" aria-label="State"><option value="">All states</option>{state_opts}</select>
      <select id="rfDir" aria-label="Direction"><option value="">All changes</option><option value="inc">Increases</option><option value="dec">Decreases</option><option value="flat">Flat (0%)</option></select>
      <span id="rfCount" class="rf-count"></span>
    </div>'''

    # rows (server-rendered)
    trs = []
    for d in data:
        cls = "inc" if d["pct"] > 0 else ("dec" if d["pct"] < 0 else "flat")
        color = RED if d["pct"] > 0 else (GREEN if d["pct"] < 0 else MUTE)
        sign = "+" if d["pct"] > 0 else ("−" if d["pct"] < 0 else "±")
        chg = f"{sign}{abs(d['pct']):.1f}%"
        src = f'<a class="ca-link" href="{esc(portal_url(d))}" target="_blank" rel="noopener nofollow">{esc(d["src"])}</a>'
        trk = f'<span class="rf-trk">{esc(d["tracking"])}</span>' if d["tracking"] else ""
        car = f'<strong>{esc(d["carrier"])}</strong>' + (f' <span class="rf-ent">{esc(d["entity"])}</span>' if d["entity"] else "")
        share_cell = (f'{d["share"]:g}%' if d["share"] is not None else '<span class="rf-na">—</span>')
        # data-eff: ISO for chronological sort; data-share: -1 sinks unknowns to the bottom
        trs.append(
            f'<tr id="{anchor(d)}" class="rf-row" data-product="{d["product"]}" data-state="{d["state"]}" data-dir="{cls}" '
            f'data-pct="{d["pct"]}" data-eff="{esc(d["eff"])}" data-share="{d["share"] if d["share"] is not None else -1}" '
            f'data-carrier="{esc(d["carrier"].lower())}">'
            f'<td>{esc(STATE[d["state"]][0])}</td><td>{d["product"]}</td><td>{car}</td>'
            f'<td style="color:{color};font-weight:600;text-align:right;">{chg}</td>'
            f'<td>{esc(fdate(d["eff"]))}</td>'
            f'<td class="rf-num rf-share">{share_cell}</td>'
            f'<td class="rf-src">{src} {trk}</td></tr>')
    table = ('<div class="rf-tablewrap"><table class="rf-table" id="rfTable"><thead><tr>'
             '<th data-sort="state">State</th><th data-sort="product">Product</th><th data-sort="carrier">Carrier</th>'
             '<th data-sort="pct" class="rf-num">Change</th><th data-sort="eff">Effective</th>'
             '<th data-sort="share" class="rf-num" title="NAIC national auto market share">U.S. share</th>'
             '<th>Source</th>'
             '</tr></thead><tbody>' + "".join(trs) + '</tbody></table></div>')

    intro = f'''<p style="font-size:19px;line-height:1.5;max-width:680px;">Every approved <strong>2026 auto and
      homeowners insurance rate filing</strong> we&rsquo;ve collected, by state and carrier &mdash; <strong>{n_inc}
      increases, {n_dec} decreases</strong> across <strong>{n_states} states</strong> and {n_carriers} carriers.
      Each row links to its primary source: the state Department of Insurance filing (by SERFF tracking number) or
      open-data portal it came from. <strong>Filter</strong> by product, state, or direction and search any carrier;
      <strong>click any column</strong> to sort by rate change, effective date, or national market share.</p>
      <div class="callout"><p><strong>For journalists &amp; researchers:</strong> figures are filed/approved
      <em>statewide-average</em> rate changes from state insurance regulators. Sources are the SERFF Filing Access
      system (session-bound — cited by tracking number), Texas TDI open data (data.texas.gov), and the California
      CDI filings list. Please cite as &ldquo;BoringRate, 2026 rate-filing roll-up, {today:%B %Y}.&rdquo;</p></div>'''

    style_extra = '''<style>
    .rf-controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:18px 0;}
    .rf-controls input,.rf-controls select{font-family:var(--sans);font-size:14px;padding:8px 10px;border:1.5px solid var(--rule);background:var(--paper);color:var(--ink);border-radius:2px;}
    .rf-controls input{flex:1;min-width:150px;}
    .rf-count{font-family:var(--mono);font-size:12px;color:var(--ink-mute);margin-left:auto;}
    .rf-tablewrap{overflow-x:auto;margin:12px 0;}
    .rf-table{width:100%;border-collapse:collapse;font-size:14px;min-width:720px;}
    .rf-table thead th{text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.05em;padding:9px 8px;cursor:pointer;white-space:nowrap;user-select:none;}
    .rf-table thead th[data-sort]:hover{color:var(--accent);}
    .rf-table thead th.rf-num{text-align:right;}
    .rf-table tbody td{padding:9px 8px;border-bottom:1px solid var(--rule);vertical-align:top;}
    .rf-table td.rf-num{text-align:right;font-variant-numeric:tabular-nums;}
    .rf-na{color:var(--ink-mute);}
    .rf-ent{color:var(--ink-mute);font-size:12px;}
    .rf-trk{font-family:var(--mono);font-size:11px;color:var(--ink-mute);}
    .rf-src{font-size:12px;}
    .rf-row.hidden{display:none;}
    .rf-row{scroll-margin-top:96px;}
    .rf-row:target td{background:rgba(180,50,26,0.10);}
    .rf-row:target td:first-child{box-shadow:inset 3px 0 0 var(--accent);}
    /* wide container for the table; keep prose at a readable measure */
    .rf-page .article-header,.rf-page .article-body>p,.rf-page .callout{max-width:720px;}
    .rf-page .rf-tablewrap,.rf-page .rf-controls{max-width:1000px;}
    </style>'''

    script = '''<script>
    (function(){
      var tbl=document.getElementById("rfTable"), rows=[].slice.call(tbl.tBodies[0].rows);
      var q=document.getElementById("rfSearch"),fp=document.getElementById("rfProduct"),
          fs=document.getElementById("rfState"),fd=document.getElementById("rfDir"),cnt=document.getElementById("rfCount");
      function apply(){
        var s=(q.value||"").toLowerCase(),p=fp.value,st=fs.value,d=fd.value,shown=0;
        rows.forEach(function(r){
          var ok=(!p||r.dataset.product===p)&&(!st||r.dataset.state===st)&&(!d||r.dataset.dir===d)&&(!s||r.dataset.carrier.indexOf(s)>=0);
          r.classList.toggle("hidden",!ok); if(ok)shown++;
        });
        cnt.textContent=shown+" of "+rows.length+" filings";
      }
      [q,fp,fs,fd].forEach(function(el){el.addEventListener("input",apply);});
      // numeric columns sort by their data-* value; eff sorts on ISO date; text cols on dataset strings
      var NUM={pct:1,share:1},dir={};
      tbl.tHead.rows[0].querySelectorAll("th[data-sort]").forEach(function(th){
        th.addEventListener("click",function(){
          var k=th.dataset.sort,asc=dir[k]=!dir[k];
          rows.sort(function(a,b){
            var va,vb;
            if(NUM[k]){va=parseFloat(a.dataset[k]);vb=parseFloat(b.dataset[k]);}
            else{va=a.dataset[k]||"";vb=b.dataset[k]||"";}
            return (va<vb?-1:va>vb?1:0)*(asc?1:-1);
          });
          var tb=tbl.tBodies[0]; rows.forEach(function(r){tb.appendChild(r);});
        });
      });
      // deep-link: /rate-filings/?state=TX&product=Home&dir=inc preselects filters (metro/data pages link in)
      var pr=new URLSearchParams(location.search);
      var stv=(pr.get("state")||"").toUpperCase(); if(stv)fs.value=stv;
      var pv=pr.get("product"); if(pv){fp.value=pv.charAt(0).toUpperCase()+pv.slice(1).toLowerCase();}
      var dv=pr.get("dir"); if(dv)fd.value=dv;
      apply();
    })();
    </script>'''

    body = f'''<div class="wrap rf-page">
  <div class="article-header">
    <div class="article-kicker">Data &nbsp;·&nbsp; Rate-Filing Roll-Up &nbsp;·&nbsp; Updated {today:%B %-d, %Y}</div>
    <h1 class="article-title">2026 auto &amp; home insurance rate filings, by state &amp; carrier</h1>
    <p class="article-dek">A primary-source roll-up of approved state rate filings &mdash; who raised, who cut, by how much, with a link to every source.</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; sourced from state DOI filings</div>
  </div>
  <div class="article-body">
    {intro}
    {controls}
    {table}
    <p style="font-size:13px;color:var(--ink-mute);margin-top:18px;">Coverage: {n_states} states so far (expanding).
    Figures are filed/approved statewide-average changes; individual rates vary by risk, home, and vehicle.
    &ldquo;Flat (0%)&rdquo; rows include symbol/rule filings that carried no overall rate impact. Not a quote.</p>
  </div>
</div>'''

    faq_ld = ('<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"Dataset",'
              f'"name":{json.dumps(title)},"description":{json.dumps(desc)},'
              f'"url":"{url}","dateModified":"{today.isoformat()}","creator":{{"@type":"Organization","name":"BoringRate"}},'
              '"isAccessibleForFree":true}\n</script>')
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
{style_extra}
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
{faq_ld}
</head>
<body>
{NAV}
{body}
{script}
{TAIL}'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(ensure(html), encoding="utf-8")
    print(f"wrote {OUT} — {len(data)} rows, {n_states} states, {n_carriers} carriers ({n_inc} inc / {n_dec} dec)")


if __name__ == "__main__":
    build()
