#!/usr/bin/env python3
"""Inject a per-carrier 'Recent rate filings' section into article/carrier/ AND home/carrier/.

The reactive shopper's first query is "why did my <carrier> insurance go up." These pages are
where that traffic lands, but they carried no primary-source filing evidence. We already hold
121 auto + 132 home SERFF filings (100% with tracking #s) — this surfaces each carrier's actual
cross-state filing record as a sourced table, the strongest byline-free E-E-A-T artifact we can
build without new data. Every row deep-links the /rate-filings/ ledger anchor + the state portal
(shared filing_cite helpers, so the anchors agree with the ledger and the trackers).

Both trees are covered. The home tree was missed for a long time — article/carrier carried this
section on 36 of 44 pages while home/carrier had it on 0 of 12, even though the home ledger was
already loaded here. Each page leads with its own line (a home carrier page opens with its home
filings, not its auto ones) and lists the other line after.

Carrier pages are hand-built (no live generator), so this is a PATCH: insert before the first
"<h2>Compare …" heading (the internal-links footer cluster), never replacing a block
(CLAUDE.md patch-safety rule). Idempotent by strip-then-insert between the markers, so re-running
after a data pull or wording change refreshes every page. Pages whose carrier has no filing on
record are skipped (and any prior section stripped) — no fabricated citations.
"""
import json
import re
import pathlib
from filing_cite import anchor, portal_url

ROOT = pathlib.Path(__file__).parent
# (directory, product to lead with). The home tree was never covered: article/carrier
# had this section on 36 of 44 pages while home/carrier had it on 0 of 12, despite the
# home ledger already being loaded here. A home carrier page leads with HOME filings —
# opening USAA's home page with its auto filings buries the relevant line.
CARRIER_DIRS = [
    (ROOT / "article" / "carrier", "Auto"),
    (ROOT / "home" / "carrier", "Home"),
]
BEGIN = "<!-- carrier-filing-record start -->"
END = "<!-- carrier-filing-record end -->"
SECTION_RE = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\s*", re.DOTALL)
INSERT_BEFORE = re.compile(r'<h2>Compare ')
FALLBACK = '<div class="article-email">'
RED, GREEN = "#b4321a", "#2f6b3a"
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load(path, product):
    out = {}
    for r in json.load(open(ROOT / path))["filings"]:
        if r.get("overall_pct") is None:
            continue
        r = {**r, "_product": product}
        if abs(r["overall_pct"]) < 0.05:        # rounds to 0.0%: treat as flat, never "cut −0.0%"
            r["overall_pct"] = 0.0
        out.setdefault(norm(r["carrier"]), []).append(r)
    return out


AUTO = load("serff_filings.json", "Auto")
HOME = load("serff_home_filings.json", "Home")


def signed(pct):
    if pct > 0:
        return f'<span style="color:{RED};font-weight:600;">+{pct:.1f}%</span>'
    if pct < 0:
        return f'<span style="color:{GREEN};font-weight:600;">−{abs(pct):.1f}%</span>'
    return '<span style="color:var(--ink-mute);font-weight:600;">0.0%</span>'


def eff(r):
    iso = r.get("effective_new") or r.get("disposition_date") or ""
    p = iso.split("-")
    if len(p) >= 2 and p[1].isdigit():
        return f"{MONTHS[int(p[1])]} {p[0]}"
    return p[0] if p and p[0] else "—"


def phrase(rows, product):
    """'12 auto rate changes across 7 states, averaging −4.6%' — sourced summary clause."""
    n = len(rows)
    states = len({r["state"] for r in rows})
    mean = sum(r["overall_pct"] for r in rows) / n
    mean = round(mean, 1)                       # sign from the ROUNDED value: no "−0.0%"
    avg = ("roughly flat on average" if mean == 0 else
           f'averaging {"+" if mean > 0 else "−"}{abs(mean):.1f}%')
    return (f'{n} {product.lower()} rate change{"s" if n != 1 else ""} across '
            f'{states} state{"s" if states != 1 else ""}, {avg}')


def section(name, rows, lead="Auto"):
    # most-recent first, with the page's own line first
    rows = sorted(rows, key=lambda r: (r["_product"] != lead,
                                       -(int((r.get("effective_new") or r.get("disposition_date") or "0-0-0")
                                             .replace("-", "") or 0))))
    body = []
    for r in rows:
        a = anchor(r)
        cite = (f'<a href="/rate-filings/#{a}" style="color:var(--ink);border-bottom:1px solid var(--rule);text-decoration:none;" '
                f'title="See this filing in the rate-filings ledger">#{r["tracking"]}</a> '
                f'<a href="{portal_url(r)}" target="_blank" rel="noopener nofollow" '
                f'style="color:var(--ink-mute);text-decoration:none;" title="Open the state filing portal and search by this SERFF number" '
                f'aria-label="Open state filing portal">&#8599;</a>')
        body.append(
            f'<tr style="border-bottom:1px solid var(--rule);">'
            f'<td style="padding:9px 8px;">{r["_product"]}</td>'
            f'<td style="padding:9px 8px;">{r["state"]}</td>'
            f'<td style="padding:9px 8px;">{signed(r["overall_pct"])}</td>'
            f'<td style="padding:9px 8px;">{eff(r)}</td>'
            f'<td style="padding:9px 8px;font-size:13px;">{cite}</td></tr>')
    table = ('<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;font-size:15px;margin:14px 0;max-width:660px;">'
             '<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">'
             '<th style="padding:9px 8px;">Product</th><th style="padding:9px 8px;">State</th><th style="padding:9px 8px;">Change</th>'
             '<th style="padding:9px 8px;">Effective</th><th style="padding:9px 8px;">SERFF filing</th></tr></thead>'
             '<tbody>' + "".join(body) + '</tbody></table></div>')

    first = [r for r in rows if r["_product"] == lead]
    second = [r for r in rows if r["_product"] != lead]
    other = "Home" if lead == "Auto" else "Auto"
    clauses = [phrase(first, lead)] if first else []
    if second:
        clauses.append(phrase(second, other))
    summary = " and ".join(clauses)
    # 2026-11-19 prose strip: the shared 'primary-source numbers' opener and the 2-sentence
    # disclaimer repeated on every carrier page; the summary + one-line note carry it.
    lead = (f'<p>In the filings we track, <strong>{name}</strong> filed {summary} '
            f'(<a href="/rate-filings/" style="color:var(--ink);border-bottom:1px solid var(--rule);text-decoration:none;">full ledger</a>).</p>')
    note = ('<p style="font-size:13px;color:var(--ink-mute);max-width:660px;">Approved statewide averages from '
            'state insurance departments, not quotes (<a href="/methodology.html">methodology</a>).</p>')
    return (f'{BEGIN}\n    <h2 id="filing-record">{name}&rsquo;s recent rate filings</h2>\n    {lead}\n    {table}\n    {note}\n    {END}\n    ')


TOP_BEGIN = "<!-- carrier-filing-top start -->"
TOP_END = "<!-- carrier-filing-top end -->"
TOP_RE = re.compile(re.escape(TOP_BEGIN) + r".*?" + re.escape(TOP_END) + r"\s*", re.DOTALL)
TOOL = {"Auto": "/", "Home": "/home/"}


def _when(r):
    return r.get("effective_new") or r.get("disposition_date") or ""


def _chip(r):
    return f'{r["state"]} {signed(r["overall_pct"])} <span style="color:var(--ink-mute);">({eff(r)})</span>'


def top_summary(name, key, rows, lead):
    """Above-the-fold filing summary (2026-11-17, Umami: carrier pages bounce 81% and only 7%
    reach the tool - visitors are researching a carrier; the rate-change pages, which lead
    with filings, convert best). Latest filing per state for the page's own line, then who
    filed CUTS in the states where this carrier raised (tool<->filing consistency: name the
    cutters, never invent). Links down to the full sourced table."""
    rows = [r for r in rows if not r.get("drift_exclude")]   # closed books: renewal-only, not what a shopper gets
    if not rows:
        return ""
    own = [r for r in rows if r["_product"] == lead] or rows
    prod = own[0]["_product"]
    # Newest filing per state that actually moved the rate: a carrier files several books per
    # state, and a newer 0% endorsement (CO Allstate landlords rider) must not hide its +15.9%.
    latest = {}
    for r in sorted(own, key=_when):
        cur = latest.get(r["state"])
        if cur is None or r["overall_pct"] != 0 or cur["overall_pct"] == 0:
            latest[r["state"]] = r
    recent = sorted(latest.values(), key=_when, reverse=True)[:5]
    up = [r for r in recent if r["overall_pct"] > 0]
    down = [r for r in recent if r["overall_pct"] < 0]
    flat = [r for r in recent if r["overall_pct"] == 0]
    parts = []
    if up:
        parts.append("raised rates in " + ", ".join(_chip(r) for r in up))
    if down:
        parts.append("cut rates in " + ", ".join(_chip(r) for r in down))
    if flat:
        parts.append("held rates flat in " + ", ".join(r["state"] for r in flat))
    line = "; ".join(parts)

    # cutters: other carriers, same line, newest filing per carrier+state is a cut, in a state this one raised
    ledger = AUTO if prod == "Auto" else HOME
    newest = {}
    for k, rs in ledger.items():
        if k == key:
            continue
        for r in rs:
            if r["state"] in {u["state"] for u in up} and not r.get("drift_exclude"):
                kk = (k, r["state"])
                if kk not in newest or _when(r) > _when(newest[kk]):
                    newest[kk] = r
    cutters = sorted((r for r in newest.values() if r["overall_pct"] <= -1.0), key=lambda r: r["overall_pct"])[:3]
    cut_line = ""
    if cutters:
        cut_line = ("<br>Filing <strong>cuts</strong> in the same states: " +
                    ", ".join(f'{r["carrier"]} ({r["state"]} {signed(r["overall_pct"])})' for r in cutters) + ".")
    tool = TOOL[prod]
    return (f'{TOP_BEGIN}\n    <div style="margin:22px 0;padding:14px 16px;border-left:3px solid var(--ink);background:var(--paper-deep);max-width:660px;">'
            f'<div style="font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.08em;color:var(--ink-mute);margin-bottom:6px;">'
            f'{name} {prod.lower()} rate filings &middot; from state regulators</div>'
            f'<p style="margin:0;">In its latest approved {prod.lower()} filings, {name} {line}.{cut_line}</p>'
            f'<p style="margin:8px 0 0;font-size:14px;"><a href="#filing-record" style="color:var(--ink);border-bottom:1px solid var(--rule);text-decoration:none;">Full filing record with SERFF numbers &darr;</a>'
            f' &nbsp;&middot;&nbsp; <a href="{tool}" style="color:var(--accent);text-decoration:none;font-weight:600;">Compare {name} to every insurer in your ZIP &rarr;</a></p>'
            f'</div>\n    {TOP_END}\n    ')


def carrier_name(rows):
    """Display name = the most common carrier string among the matched filings."""
    from collections import Counter
    return Counter(r["carrier"] for r in rows).most_common(1)[0][0]


def main():
    added = refreshed = skipped = 0
    for carrier_dir, lead in CARRIER_DIRS:
      for p in sorted(carrier_dir.glob("*.html")):
        html = p.read_text(encoding="utf-8")
        had = BEGIN in html
        html = SECTION_RE.sub("", html)  # strip any prior section (idempotent refresh)
        html = TOP_RE.sub("", html)
        key = norm(p.stem.replace("-", ""))
        rows = AUTO.get(key, []) + HOME.get(key, [])
        if not rows:
            if had:
                p.write_text(html, encoding="utf-8"); skipped += 1
                print(f"  stripped (no filings) {carrier_dir.parent.name}/carrier/{p.name}")
            continue
        name = carrier_name(rows)
        sec = section(name, rows, lead)
        if INSERT_BEFORE.search(html):
            html = INSERT_BEFORE.sub(sec + "<h2>Compare ", html, count=1)
        elif FALLBACK in html:
            html = html.replace(FALLBACK, sec + FALLBACK, 1)
        else:
            print(f"  SKIP (no anchor) {carrier_dir.parent.name}/carrier/{p.name}"); continue
        # top summary: before the first <h2> that follows the TLDR card
        t = html.find('<div class="tldr-card">')
        h2 = html.find("<h2", t if t >= 0 else html.find("<h1"))
        if h2 > 0:
            html = html[:h2] + top_summary(name, key, rows, lead) + html[h2:]
        p.write_text(html, encoding="utf-8")
        refreshed += had
        added += not had
        print(f"  {'refreshed' if had else 'added'} {carrier_dir.parent.name}/carrier/{p.name}  ({len(rows)} filings, {name})")
    print(f"\nadded {added}, refreshed {refreshed}, stripped {skipped}")


if __name__ == "__main__":
    main()
