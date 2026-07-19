#!/usr/bin/env python3
"""Inject a per-carrier 'Recent rate filings' section into article/carrier/<slug>.html.

The reactive shopper's first query is "why did my <carrier> insurance go up." These pages are
where that traffic lands, but they carried no primary-source filing evidence. We already hold
121 auto + 132 home SERFF filings (100% with tracking #s) — this surfaces each carrier's actual
cross-state filing record as a sourced table, the strongest byline-free E-E-A-T artifact we can
build without new data. Every row deep-links the /rate-filings/ ledger anchor + the state portal
(shared filing_cite helpers, so the anchors agree with the ledger and the trackers).

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
CARRIER_DIR = ROOT / "article" / "carrier"
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
    sign = "+" if mean > 0 else ("−" if mean < 0 else "±")
    return (f'{n} {product.lower()} rate change{"s" if n != 1 else ""} across '
            f'{states} state{"s" if states != 1 else ""}, averaging {sign}{abs(mean):.1f}%')


def section(name, rows):
    # most-recent first, auto before home
    rows = sorted(rows, key=lambda r: (r["_product"] != "Auto",
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

    auto = [r for r in rows if r["_product"] == "Auto"]
    home = [r for r in rows if r["_product"] == "Home"]
    clauses = [phrase(auto, "Auto")] if auto else []
    if home:
        clauses.append(phrase(home, "Home"))
    summary = " and ".join(clauses)
    lead = (f'<p>The actual rate changes <strong>{name}</strong> filed with state insurance '
            f'regulators &mdash; primary-source numbers, not estimates. In the filings we track, '
            f'{name} filed {summary}. Each row links to the filing in our '
            f'<a href="/rate-filings/" style="color:var(--ink);border-bottom:1px solid var(--rule);text-decoration:none;">rate-filings ledger</a>.</p>')
    note = ('<p style="font-size:13px;color:var(--ink-mute);max-width:660px;">Filed/approved statewide-average '
            'changes from each state&rsquo;s Department of Insurance; a filed average is not your rate &mdash; '
            'your change depends on your ZIP, coverage, and risk profile, and a cut often reaches new customers '
            'before renewals. Not a quote.</p>')
    return (f'{BEGIN}\n    <h2>{name}&rsquo;s recent rate filings</h2>\n    {lead}\n    {table}\n    {note}\n    {END}\n    ')


def carrier_name(rows):
    """Display name = the most common carrier string among the matched filings."""
    from collections import Counter
    return Counter(r["carrier"] for r in rows).most_common(1)[0][0]


def main():
    added = refreshed = skipped = 0
    for p in sorted(CARRIER_DIR.glob("*.html")):
        html = p.read_text(encoding="utf-8")
        had = BEGIN in html
        html = SECTION_RE.sub("", html)  # strip any prior section (idempotent refresh)
        key = norm(p.stem.replace("-", ""))
        rows = AUTO.get(key, []) + HOME.get(key, [])
        if not rows:
            if had:
                p.write_text(html, encoding="utf-8"); skipped += 1
                print(f"  stripped (no filings) {p.name}")
            continue
        name = carrier_name(rows)
        sec = section(name, rows)
        if INSERT_BEFORE.search(html):
            html = INSERT_BEFORE.sub(sec + "<h2>Compare ", html, count=1)
        elif FALLBACK in html:
            html = html.replace(FALLBACK, sec + FALLBACK, 1)
        else:
            print(f"  SKIP (no anchor) {p.name}"); continue
        p.write_text(html, encoding="utf-8")
        refreshed += had
        added += not had
        print(f"  {'refreshed' if had else 'added'} {p.name}  ({len(rows)} filings, {name})")
    print(f"\nadded {added}, refreshed {refreshed}, stripped {skipped}")


if __name__ == "__main__":
    main()
