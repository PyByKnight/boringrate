#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the click-to-download SERFF jacket pull list (~/<st>_home_jackets.html).

Input: _serff/<ST>/candidates.tsv — one rate-bearing filing per line, already triaged
from the pasted SERFF search results (Rate in filing type; not withdrawn; owner-occupied /
combination sub-TOIs; no ISO, vendor or loss-cost filings):

    tracking <TAB> family <TAB> product <TAB> filing_type <TAB> note

Tiering: a family whose name is in the home roster (home/index.html HOME_CARRIERS) can move
a displayed price, so it goes in START HERE, newest trackings first, capped per family
(CAP, overridable). Everything else lands in the collapsed second tier.

    python3 build_pull_list.py CO "Colorado" [--note "..."]
"""
import re, sys, html, pathlib
from collections import OrderedDict

ROOT = pathlib.Path(__file__).parent
CAP = 3
CAP_OVERRIDE = {"State Farm": 4, "Farmers": 4, "Liberty Mutual / Safeco": 5, "Allstate": 7}
# Family label -> roster names it covers (labels that are not roster names verbatim).
FAMILY_ROSTER = {"Liberty Mutual / Safeco": ["Liberty Mutual", "Safeco"], "Amica": ["Amica Mutual"]}
ORDER = ["State Farm", "Allstate", "USAA", "Farmers", "Liberty Mutual / Safeco", "Travelers",
         "Nationwide", "American Family"]
SERFF = "https://serff-sfa.naic.org/serff/sfa/search/filingSummary.xhtml?filingId="


def roster():
    h = (ROOT / "home" / "index.html").read_text(encoding="utf-8")
    return set(re.findall(r'name:"([^"]+)",\s*base:', h))


def fid(t):
    return re.sub(r"\D", "", t.split("-", 1)[1])   # filingId drops the G (NWPP-G1347... -> 1347...)


def li(r):
    t = r["tracking"]
    warn = f'<span class="warn">{html.escape(r["note"])}</span>' if r["note"] else ""
    return (f'<li><label><input type="checkbox" data-k="{t}"> <a href="{SERFF}{fid(t)}" '
            f'target="_blank" rel="noopener">{t}</a> <span class="p">{html.escape(r["product"])}</span>'
            f'<span class="t">{html.escape(r["type"])}</span>{warn}</label></li>')


def block(fam, rows):
    return f'<h3>{html.escape(fam)} <span class="n">{len(rows)}</span></h3><ul>\n' + "\n".join(li(r) for r in rows) + "</ul>"


def main():
    st, name = sys.argv[1], sys.argv[2]
    note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
    rows = []
    for line in (ROOT / "_serff" / st / "candidates.tsv").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = (line.split("\t") + [""] * 5)[:5]
        rows.append(dict(tracking=f[0], family=f[1], product=f[2], type=f[3], note=f[4]))
    ros = roster()
    fams = OrderedDict()
    for r in sorted(rows, key=lambda r: fid(r["tracking"]), reverse=True):
        fams.setdefault(r["family"], []).append(r)

    def in_roster(fam):
        return any(n in ros for n in FAMILY_ROSTER.get(fam, [fam]))

    start, rest = OrderedDict(), OrderedDict()
    for fam, rs in fams.items():
        if in_roster(fam):
            cap = CAP_OVERRIDE.get(fam, CAP)
            start[fam] = rs[:cap]
            if rs[cap:]:
                rest[fam] = rs[cap:]
        else:
            rest[fam] = rs
    rank = lambda fam: (ORDER.index(fam) if fam in ORDER else len(ORDER), -len(start.get(fam, rest.get(fam, []))))
    start = OrderedDict(sorted(start.items(), key=lambda kv: rank(kv[0])))
    rest = OrderedDict(sorted(rest.items(), key=lambda kv: (-len(kv[1]), kv[0])))
    n_start = sum(len(v) for v in start.values())
    n_rest = sum(len(v) for v in rest.values())

    tn = (pathlib.Path.home() / "tn_home_jackets.html").read_text(encoding="utf-8")
    style = tn[tn.index("<style>"):tn.index("</style>") + len("</style>")]
    key = f"{st.lower()}_home_jackets"
    out = (f'<!doctype html><meta charset="utf-8"><title>{st} home filings</title>\n{style}\n'
           f'<h1>{html.escape(name)} homeowners filings</h1>\n'
           f'<div class="sub">{len(rows)} rate-bearing filings (dropped: Form-only and Rule-only, Withdrawn, '
           f'Tenant/Mobile/Condo/Other sub-TOIs, ISO &amp; vendor filings, loss costs).\n'
           f' Click a link, hit <b>Download Zip File</b>; the box ticks itself. Drop the zips in <b>Linux files</b>.</div>\n'
           + (f'<div class="sub" style="color:#b4321a;font-weight:600">{html.escape(note)}</div>\n' if note else "")
           + f'<div id="bar"><b><span id="done">0</span></b> opened &middot; <b>Start here = {n_start}</b><button id="reset">reset</button>'
           f' &middot; <a href="https://serff-sfa.naic.org/serff/sfa/home/{st}" target="_blank">{st} SERFF portal &rarr;</a></div>\n'
           f'<h2>START HERE &mdash; {n_start} jackets</h2>\n'
           f'<div class="sub">All in the home roster, so these move a displayed price. Big families capped at the newest few.</div>\n'
           + "\n".join(block(f, rs) for f, rs in start.items())
           + f'\n<details><summary>Second tier &mdash; {n_rest} more (older filings of the big families, non-roster carriers)</summary>\n'
           + "\n".join(block(f, rs) for f, rs in rest.items()) + "</details>\n"
           "<script>\n"
           f"const K='{key}';let s=JSON.parse(localStorage.getItem(K)||'{{}}');\n"
           "const b=[...document.querySelectorAll('input')];\n"
           "const paint=()=>document.getElementById('done').textContent=b.filter(x=>x.checked).length;\n"
           "b.forEach(x=>{x.checked=!!s[x.dataset.k];x.onchange=()=>{s[x.dataset.k]=x.checked;localStorage.setItem(K,JSON.stringify(s));paint();};});\n"
           "document.querySelectorAll('a').forEach(a=>a.onclick=()=>{const i=a.closest('li').querySelector('input');if(!i.checked){i.checked=true;i.onchange();}});\n"
           "document.getElementById('reset').onclick=()=>{localStorage.removeItem(K);b.forEach(x=>x.checked=false);paint();};\n"
           "paint();\n</script>\n")
    dest = pathlib.Path.home() / f"{st.lower()}_home_jackets.html"
    dest.write_text(out, encoding="utf-8")
    print(f"{dest}: start here {n_start} ({', '.join(f'{k} {len(v)}' for k, v in start.items())}); second tier {n_rest}")


if __name__ == "__main__":
    main()
