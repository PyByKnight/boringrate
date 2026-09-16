#!/usr/bin/env python3
"""National rate-filings roll-up — the citable/linkable data asset (Fable #3).

One page: every captured 2026 auto + home rate filing, by state and carrier, each
row linked to its primary source (SERFF tracking # + the DOI portal/dataset). Rows
are server-rendered (crawlable + citable); vanilla JS adds sort/filter. Draws from
serff_filings.json (auto) + serff_home_filings.json (home). Output: rate-filings/index.html."""
import json, re, gzip, pathlib
from filing_cite import anchor, portal_url
from datetime import date
from gen_metro_page import STATE, esc
from plausible_snippet import ensure
import brand_share

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


# Filing narrative (mine_filing_text.py). Optional: the page degrades to numbers-only
# if the digest hasn't been built yet, so this generator never hard-fails on it.
try:
    DIGEST = json.load(gzip.open(ROOT / "filing_digests.json.gz"))["digests"]
except Exception:
    DIGEST = {}

# Rate-capping rules (mine_capping.py). Optional, same as the digest.
try:
    CAPS = json.load(open(ROOT / "filing_caps.json"))["caps"]
except Exception:
    CAPS = {}

scaff = (ROOT / "home" / "state" / "florida.html").read_text(encoding="utf-8")
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>") + len("</style>")]
NAV = scaff[scaff.index('<header class="top">'):scaff.index("</header>") + len("</header>")]
TAIL = scaff[scaff.index("<footer>"):]
# The scaffold is home/state/florida.html, so its sticky CTA rides along: it read
# "Compare Florida home rates", pointed at #zipBarInput (which does not exist on
# this page), and fell back to /home/ — the home section, on a page that is mostly
# auto filings. Retarget both to the ZIP tool on the main page.
TAIL = TAIL.replace(
    'href="#zipBarInput" aria-label="Compare Florida home rates">Compare Florida home rates',
    'href="/" aria-label="Check rates in your ZIP">Check rates in your ZIP')
TAIL = TAIL.replace('else{window.location.href="/home/";}', 'else{window.location.href="/";}')
assert "Compare Florida home rates" not in TAIL, "sticky CTA not retargeted — scaffold markup changed"


# In-body CTA. The page previously ended in a disclaimer straight into the footer,
# so nothing in the body drove anywhere. Reuses the canonical two-tile module
# (insert_tool_tiles.py) — its CSS already rides in on the scaffold STYLE.
_ONSUBMIT = ("event.preventDefault();var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);"
             "if(/^\\d{5}$/.test(z)){location.href='/?zip='+z}else{this.zc.focus()}")
CTA_TILES = (
    '<div class="tooltiles" style="margin-top:26px;">'
    '<div class="tile">'
    '<div class="tile-kicker">Compare rates</div>'
    '<div class="tile-name">What these filings mean for your ZIP</div>'
    '<div class="tile-desc">A filed change is a statewide average. See what every carrier is '
    'estimated to charge for your exact ZIP and profile.</div>'
    f'<form class="tile-zipform" onsubmit="{_ONSUBMIT}">'
    '<input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" '
    'placeholder="ZIP" aria-label="ZIP code" />'
    '<button type="submit" class="tile-zip-btn">Compare &rarr;</button>'
    '</form>'
    '</div>'
    '<div class="tile">'
    '<div class="tile-kicker">Rate change tracker</div>'
    '<div class="tile-name">Read your state in plain English</div>'
    '<div class="tile-desc">Who raised, who cut, and whether the new rate reaches you at '
    'renewal or only new customers.</div>'
    '<a class="tbtn secondary" href="/article/rate-changes/">See the state-by-state tracker &rarr;</a>'
    '</div>'
    '</div>')


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


COV_LABEL = {
    "BI": "Bodily injury liability", "PD": "Property damage liability",
    "COMP": "Comprehensive", "COLL": "Collision", "MED": "Medical payments",
    "PIP": "Personal injury protection", "UM": "Uninsured motorist",
    "UIM": "Underinsured motorist", "UMBI": "Uninsured motorist — bodily injury",
    "UIMBI": "Underinsured motorist — bodily injury",
    "UMPD": "Uninsured motorist — property damage", "OTHER": "Other coverages",
}


def pct_str(v):
    """Signed percent in the house style (− is a real minus sign, not a hyphen)."""
    sign = "+" if v > 0 else ("−" if v < 0 else "±")
    return f"{sign}{abs(v):.1f}%"


def detail_html(d):
    """The expandable panel: what the headline percentage leaves out.

    Built only from fields we actually hold — every clause is conditional, so a row with
    thin data shows a short panel rather than a grid of em-dashes. Returns "" when we
    have nothing beyond what the visible row already says."""
    bits = []

    # indicated-vs-taken. `indicated_pct` is the carrier's OWN actuarial indication — what its
    # analysis says the book needs — NOT a request submitted to the regulator. Carriers routinely
    # file below indication voluntarily (rate capping, competitive pressure), so phrasing this as
    # "asked the state for X and was approved for Y" would assert regulator action the data does
    # not establish. House voice, matching the reactive pages: "its actuaries indicated it needed".
    ind, took = d["indicated"], d["pct"]
    if ind is not None and abs(ind - took) >= 0.05:
        if took < ind:
            bits.append(
                f'<p><strong>{esc(d["carrier"])}&rsquo;s actuaries indicated it needed '
                f'{pct_str(ind)}</strong>, and it filed {pct_str(took)}. A carrier that prices '
                f'below its own indication is under-earning on the book &mdash; which often means '
                f'another filing follows.</p>')
        else:
            bits.append(
                f'<p><strong>{esc(d["carrier"])} filed {pct_str(took)}</strong>, above the '
                f'{pct_str(ind)} its actuaries indicated the book needed.</p>')
    elif ind is not None:
        bits.append(f'<p>{esc(d["carrier"])} filed {pct_str(took)} &mdash; exactly the change its '
                    f'actuaries indicated the book needed.</p>')

    # the spread — the single most useful number for "why is mine different".
    # MUST be qualified where the filing carries a rate-capping rule: an unqualified spread is
    # wrong in one of two directions, and the corpus has both. Michigan told Bristol West its
    # filed +14% was "before any capping" (overstates what anyone felt); Louisiana told Imperial
    # the filed maximum was itself a capped figure and the real one was +163% (understates).
    cap = CAPS.get(d["tracking"] or "")
    if d["max_pct"] is not None and d["min_pct"] is not None and d["max_pct"] != d["min_pct"]:
        before = " before capping" if cap and cap.get("direction") == "overstates" else ""
        bits.append(
            f'<p>The {pct_str(d["pct"])} is a <em>statewide average</em>. Individual policies in this '
            f'filing moved <strong>{pct_str(d["max_pct"])} to {pct_str(d["min_pct"])}</strong>'
            f'{before} depending on the vehicle, ZIP code, driving record and coverages on the '
            f'policy.</p>')
    if cap:
        if cap.get("direction") == "corrected":
            bits.append('<p class="rf-cap">The carrier first reported a <strong>capped</strong> '
                        'maximum here. State regulators required it to publish the real one &mdash; '
                        'which is the figure shown above.</p>')
        elif cap.get("cap"):
            bits.append(f'<p class="rf-cap">This filing caps individual rate changes at '
                        f'<strong>{esc(cap["cap"])}</strong>, so a policy moves toward its full '
                        f'new rate over several renewals rather than all at once.</p>')
        else:
            bits.append('<p class="rf-cap">This filing carries a <strong>rate-capping rule</strong>, '
                        'which limits how far any single policy can move at one renewal — so the '
                        'range above may not be what any one customer actually saw.</p>')

    # per-coverage splits, where the filing stated them (backfill_coverage_changes.py).
    # This is the sharpest version of "the average isn't your bill": VA Farm Bureau filed an
    # overall 0.0% while BI went +3% and PD/COMP/COLL went -1%.
    cc = d.get("coverage_changes") or {}
    if cc:
        parts = "".join(
            f'<li><span>{esc(COV_LABEL.get(k, k))}</span>'
            f'<span style="color:{RED if v > 0 else (GREEN if v < 0 else MUTE)};font-weight:600;">'
            f'{pct_str(v)}</span></li>'
            for k, v in sorted(cc.items(), key=lambda kv: -abs(kv[1])))
        bits.append(f'<p>Not every coverage moved the same way:</p><ul class="rf-cov">{parts}</ul>')

    if d["affected"]:
        basis = esc(d["count_basis"])
        bits.append(f'<p>Book size: <strong>{d["affected"]:,}</strong> {basis}.</p>')

    if d["prior"] is not None:
        bits.append(f'<p>The carrier&rsquo;s previous revision in this state was '
                    f'<strong>{pct_str(d["prior"])}</strong>.</p>')

    # the carrier in its own words — unique, citable, and crawlable
    if d.get("desc"):
        q = re.sub(r"\s+", " ", d["desc"]).strip()
        if len(q) > 340:
            cut = q[:340].rsplit(" ", 1)[0]
            q = cut + "…"
        bits.append(f'<blockquote class="rf-quote">{esc(q)}'
                    f'<cite>&mdash; {esc(d["carrier"])}, filing {esc(d["tracking"])}</cite></blockquote>')

    if not bits:
        return ""
    return ('<div class="rf-detail-inner">' + "".join(bits) +
            f'<p class="rf-detail-src"><a href="{esc(portal_url(d))}" target="_blank" '
            f'rel="noopener nofollow">Read the filing at {esc(d["src"])} &rarr;</a></p></div>')


def num(v):
    """Ledger hygiene: 12 rows carry indicated_pct as '' rather than null (parser artifact).
    Coerce anything non-numeric to None so the detail panel simply omits that clause."""
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def collect():
    _bt, _eb = brand_share.build()
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
            "brand": brand_share.share(r, _bt, _eb) if product == "Auto" else None,
            # ── detail-row payload ──────────────────────────────────────────────
            # Held in the ledger all along but never rendered: the headline % alone
            # cannot answer "why did MINE go up more than that?". indicated = what the
            # carrier asked for, max/min = how far individual policies actually moved,
            # affected = book size, desc = the carrier's own account of the change.
            "indicated": num(r.get("indicated_pct")),
            "max_pct": num(r.get("max_pct")), "min_pct": num(r.get("min_pct")),
            "affected": num(r.get("affected")), "count_basis": r.get("count_basis") or "policyholders",
            "prior": num(r.get("prior_revision_pct")),
            "coverage_changes": r.get("coverage_changes") or None,
            "desc": DIGEST.get(r.get("tracking") or "", {}).get("desc"),
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
        brand_cell = (brand_share.fmt(d["brand"]) if d["brand"] is not None
                      else '<span class="rf-na">&mdash;</span>')
        # data-eff: ISO for chronological sort; data-share: -1 sinks unknowns to the bottom
        trs.append(
            f'<tr id="{anchor(d)}" class="rf-row" data-product="{d["product"]}" data-state="{d["state"]}" data-dir="{cls}" '
            f'data-pct="{d["pct"]}" data-eff="{esc(d["eff"])}" data-share="{d["share"] if d["share"] is not None else -1}" '
            f'data-carrier="{esc(d["carrier"].lower())}" '
            f'data-brand="{round(d["brand"]*100, 2) if d["brand"] is not None else -1}">'
            f'<td>{esc(STATE[d["state"]][0])}</td><td>{d["product"]}</td><td>{car}</td>'
            f'<td style="color:{color};font-weight:600;text-align:right;">{chg}</td>'
            f'<td>{esc(fdate(d["eff"]))}</td>'
            f'<td class="rf-num rf-share">{share_cell}</td>'
            f'<td class="rf-num rf-share">{brand_cell}</td>'
            f'<td class="rf-src">{src} {trk}</td></tr>')
        # Detail row: server-rendered (crawlable + citable), collapsed via CSS, toggled by JS.
        det = detail_html(d)
        if det:
            trs[-1] = trs[-1].replace('<tr id=', '<tr data-detail="1" id=', 1)
            trs.append(f'<tr class="rf-detail" data-for="{anchor(d)}" hidden>'
                       f'<td colspan="8">{det}</td></tr>')
    table = ('<div class="rf-tablewrap"><table class="rf-table" id="rfTable"><thead><tr>'
             '<th data-sort="state">State</th><th data-sort="product">Product</th><th data-sort="carrier">Carrier</th>'
             '<th data-sort="pct" class="rf-num">Change</th><th data-sort="eff">Effective</th>'
             '<th data-sort="share" class="rf-num" title="NAIC national auto market share">U.S. share</th>'
             '<th data-sort="brand" class="rf-num" title="This filing entity&#39;s share of the carrier&#39;s '
             'policyholders across all captured filings in this state. Shown only where we hold two or more '
             'entities for that carrier.">% of brand</th>'
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
    .rf-row.hidden,.rf-detail.hidden{display:none;}
    .rf-row{scroll-margin-top:96px;}
    /* expandable filing detail */
    .rf-row[data-detail]{cursor:pointer;}
    .rf-row[data-detail]:hover td{background:rgba(0,0,0,0.025);}
    .rf-row[data-detail] td:first-child::before{content:"▸";color:var(--ink-mute);font-size:10px;margin-right:6px;display:inline-block;transition:transform .12s;}
    .rf-row[data-detail][aria-expanded="true"] td:first-child::before{transform:rotate(90deg);}
    .rf-row[data-detail]:focus-visible{outline:2px solid var(--accent);outline-offset:-2px;}
    .rf-detail > td{background:var(--paper-deep);padding:0 8px 4px 8px;border-bottom:1px solid var(--rule);}
    .rf-detail-inner{max-width:680px;padding:14px 4px 16px 22px;}
    .rf-detail-inner p{font-family:var(--serif);font-size:15px;line-height:1.55;margin:0 0 9px;}
    .rf-quote{margin:12px 0 9px;padding:10px 0 4px 14px;border-left:2px solid var(--rule);}
    .rf-quote{font-family:var(--serif);font-size:14px;line-height:1.55;color:var(--ink-soft);font-style:italic;}
    .rf-quote cite{display:block;font-family:var(--mono);font-size:11px;font-style:normal;color:var(--ink-mute);letter-spacing:0.04em;margin-top:7px;}
    .rf-cov{list-style:none;margin:2px 0 11px;padding:0;max-width:330px;}
    .rf-cov li{display:flex;justify-content:space-between;gap:16px;font-family:var(--sans);font-size:14px;padding:4px 0;border-bottom:1px dotted var(--rule);}
    .rf-cov li span:first-child{color:var(--ink-soft);}
    .rf-cap{background:var(--paper);border-left:2px solid var(--accent);padding:8px 12px;margin:10px 0 11px !important;font-size:14px !important;}
    .rf-detail-src{font-family:var(--mono);font-size:11px;letter-spacing:0.04em;text-transform:uppercase;}
    @media (max-width:640px){.rf-detail-inner{padding-left:10px;}}
    .rf-row:target td{background:rgba(180,50,26,0.10);}
    .rf-row:target td:first-child{box-shadow:inset 3px 0 0 var(--accent);}
    /* wide container for the table; keep prose at a readable measure */
    .rf-page .article-header,.rf-page .article-body>p,.rf-page .callout{max-width:720px;}
    .rf-page .rf-tablewrap,.rf-page .rf-controls{max-width:1000px;}
    </style>'''

    script = '''<script>
    (function(){
      var tbl=document.getElementById("rfTable");
      // Only .rf-row are data rows. Detail rows (.rf-detail) are paired to a parent and must
      // never be filtered, counted, or sorted as if they were filings — they ride along.
      var rows=[].slice.call(tbl.querySelectorAll("tbody > tr.rf-row"));
      rows.forEach(function(r){
        var d=r.nextElementSibling;
        r._detail=(d&&d.classList.contains("rf-detail"))?d:null;
      });
      var q=document.getElementById("rfSearch"),fp=document.getElementById("rfProduct"),
          fs=document.getElementById("rfState"),fd=document.getElementById("rfDir"),cnt=document.getElementById("rfCount");
      function apply(){
        var s=(q.value||"").toLowerCase(),p=fp.value,st=fs.value,d=fd.value,shown=0;
        rows.forEach(function(r){
          var ok=(!p||r.dataset.product===p)&&(!st||r.dataset.state===st)&&(!d||r.dataset.dir===d)&&(!s||r.dataset.carrier.indexOf(s)>=0);
          r.classList.toggle("hidden",!ok); if(ok)shown++;
          // a filtered-out row takes its (possibly open) detail panel with it
          if(r._detail){r._detail.classList.toggle("hidden",!ok); if(!ok){r._detail.hidden=true;r.setAttribute("aria-expanded","false");}}
        });
        cnt.textContent=shown+" of "+rows.length+" filings";
      }
      [q,fp,fs,fd].forEach(function(el){el.addEventListener("input",apply);});
      // numeric columns sort by their data-* value; eff sorts on ISO date; text cols on dataset strings
      var NUM={pct:1,share:1,brand:1},dir={};
      tbl.tHead.rows[0].querySelectorAll("th[data-sort]").forEach(function(th){
        th.addEventListener("click",function(){
          var k=th.dataset.sort,asc=dir[k]=!dir[k];
          rows.sort(function(a,b){
            var va,vb;
            if(NUM[k]){va=parseFloat(a.dataset[k]);vb=parseFloat(b.dataset[k]);}
            else{va=a.dataset[k]||"";vb=b.dataset[k]||"";}
            return (va<vb?-1:va>vb?1:0)*(asc?1:-1);
          });
          // re-append each row followed immediately by its detail panel, so sorting
          // never separates a panel from the filing it describes
          var tb=tbl.tBodies[0];
          rows.forEach(function(r){tb.appendChild(r); if(r._detail)tb.appendChild(r._detail);});
        });
      });
      // expand / collapse a filing's detail panel
      function toggle(r){
        if(!r._detail)return;
        var open=r._detail.hidden;
        r._detail.hidden=!open;
        r.setAttribute("aria-expanded",open?"true":"false");
        if(open&&window.track)window.track("filing_detail_opened",{state:r.dataset.state,product:r.dataset.product});
      }
      rows.forEach(function(r){
        if(!r._detail)return;
        r.setAttribute("aria-expanded","false");
        r.setAttribute("tabindex","0");
        r.setAttribute("role","button");
        r.addEventListener("click",function(e){
          if(e.target.closest("a"))return;   // let source links through
          toggle(r);
        });
        r.addEventListener("keydown",function(e){
          if(e.key==="Enter"||e.key===" "){e.preventDefault();toggle(r);}
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
    {CTA_TILES}
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
