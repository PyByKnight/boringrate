#!/usr/bin/env python3
"""Rate-change tracker: hub + per-state pages from rate_changes.json (sourced data only).

Angle: who raised, who cut, and "are you actually getting the new rate?" Every figure
links to its source. Pages built from the article/metro/atlanta.html scaffolding.
"""
import json
import pathlib
import re
from datetime import date
from gen_metro_page import STATE, esc, _json

ROOT = pathlib.Path(__file__).parent
TEMPLATE = ROOT / "article" / "metro" / "atlanta.html"
OUTDIR = ROOT / "article" / "rate-changes"
RED, GREEN = "#b4321a", "#2f6b3a"
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fdate(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m)]} {int(d)}, {y}"


def signed(c):
    s = ("+" if c["dir"] == "increase" else "−") + f'{c["pct"]:g}%'
    color = RED if c["dir"] == "increase" else GREEN
    return f'<span style="color:{color};font-weight:600;">{s}</span>'


def render(slug, title, desc, h1, dek, body_html, faq, in_subdir=True):
    url = f"https://boringrate.com/article/rate-changes/{slug}.html" if slug != "index" \
        else "https://boringrate.com/article/rate-changes/"
    html = TEMPLATE.read_text(encoding="utf-8")
    html = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf'\g<1>{url}\g<2>', html)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{url}\g<2>', html)
    html = re.sub(r'<title>[^<]*</title>', f'<title>{esc(title)}</title>', html)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', rf'\g<1>{esc(desc)}\g<2>', html)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf'\g<1>{esc(h1)}\g<2>', html)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf'\g<1>{esc(desc)}\g<2>', html)
    html = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', rf'\g<1>{esc(h1)}\g<2>', html)
    html = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', rf'\g<1>{esc(desc)}\g<2>', html)

    faq_items = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}' % (_json(q), _json(a))
        for q, a in faq)
    jsonld = (
        '<script type="application/ld+json">\n'
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"https://boringrate.com/"},'
        f'{{"@type":"ListItem","position":2,"name":{_json(h1)},"item":{_json(url)}}}]}}\n</script>\n'
        '<script type="application/ld+json">\n'
        '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' + faq_items + ']}\n</script>')
    html = re.sub(r'(?:<script type="application/ld\+json">.*?</script>\s*)+', jsonld + "\n",
                  html, count=1, flags=re.DOTALL)

    header = (
        '<div class="article-header">\n'
        f'    <div class="article-kicker"><a href="../../index.html#guides">Rate Tracker</a> &nbsp;&middot;&nbsp; Updated {date.today():%B %Y}</div>\n'
        f'    <h1 class="article-title">{h1}</h1>\n'
        f'    <p class="article-dek">{dek}</p>\n'
        '    <div class="article-byline">BoringRate Editorial &nbsp;&middot;&nbsp; sourced from state DOI filings</div>\n'
        '  </div>\n  <div class="article-body">')
    html = re.sub(r'<div class="article-header">.*?</div>\s*<div class="article-body">',
                  header, html, count=1, flags=re.DOTALL)
    html = re.sub(r'<div class="article-body">.*?<div class="article-email">',
                  '<div class="article-body">\n' + body_html + '\n    <div class="article-email">',
                  html, count=1, flags=re.DOTALL)
    html = html.replace("when Atlanta rates move", "when rates move in your area")
    html = html.replace("Compare Atlanta rates", "Compare rates")

    OUTDIR.mkdir(exist_ok=True)
    out = OUTDIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return out, url


def rows_table(changes):
    head = ('<table style="width:100%;border-collapse:collapse;font-size:15px;margin:18px 0;">'
            '<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">'
            '<th style="padding:9px 8px;">Carrier</th><th>Change</th><th>Effective</th><th>Policyholders</th><th>Source</th></tr></thead><tbody>')
    body = []
    for c in sorted(changes, key=lambda x: x["effective"]):
        aff = f'{c["affected"]:,}' if c.get("affected") else "—"
        src = f'<a class="ca-link" href="{c["url"]}" target="_blank" rel="noopener nofollow">{esc(c["source"])}</a>'
        body.append(
            f'<tr style="border-bottom:1px solid var(--rule);"><td style="padding:9px 8px;"><strong>{esc(c["carrier"])}</strong></td>'
            f'<td>{signed(c)}</td><td>{fdate(c["effective"])}</td><td>{aff}</td><td style="font-size:13px;">{src}</td></tr>')
    return head + "".join(body) + "</tbody></table>"


def state_page(code, changes):
    name, slug, _ = STATE[code]
    incs = [c for c in changes if c["dir"] == "increase"]
    decs = [c for c in changes if c["dir"] == "decrease"]
    title = f"{name} Auto Insurance Rate Changes (2026) — Who Raised, Who Cut"
    desc = (f"{len(incs)} carriers raised and {len(decs)} cut {name} auto rates in 2026. "
            f"See the filings, effective dates, and whether you're getting the new rate.")
    h1 = f"{name} auto insurance rate changes in 2026"
    dek = (f"{len(incs)} carrier{'s' if len(incs)!=1 else ''} raised rates and "
           f"{len(decs)} cut them in {name} this year &mdash; from approved DOI filings. "
           "Here&rsquo;s who, by how much, and whether your renewal reflects it.")
    parts = []
    decline_note = ""
    if decs:
        ex = decs[0]
        if ex.get("renewal"):
            decline_note = (f' For example, {esc(ex["carrier"])}&rsquo;s cut took effect for <em>new</em> '
                            f'customers on {fdate(ex["effective"])} but existing customers only at renewals '
                            f'starting {fdate(ex["renewal"])}.')
    parts.append(
        '<div class="callout"><p><strong>Are you actually getting the new rate?</strong><br>'
        'Approved changes are statewide averages, and a cut usually reaches <em>new</em> buyers first &mdash; '
        'existing customers often don&rsquo;t see it until their next renewal, if at all.' + decline_note +
        ' The only way to know you&rsquo;re on the best current price is to re-shop.</p></div>')
    if incs:
        parts.append(f'<h2>Carriers that raised {esc(name)} rates in 2026</h2>' + rows_table(incs))
    if decs:
        parts.append(f'<h2>Carriers that cut {esc(name)} rates in 2026</h2>' + rows_table(decs))
    parts.append(
        '<div class="zip-embed"><div class="zip-embed-label">Compare rates in ' + esc(name) + '</div>'
        '<h3>See who&rsquo;s cheapest <em>for you</em> right now.</h3>'
        '<div class="zip-embed-sub">Enter your ZIP &mdash; we rank every major carrier for your area. '
        'No phone. No spam. No selling your information.</div>'
        '<form class="zip-embed-form" id="embedZipForm" autocomplete="off">'
        '<input class="zip-embed-input" id="embedZipInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
        '<button type="submit" class="zip-embed-btn">Compare &rarr;</button></form></div>')
    parts.append('<p style="font-size:13px;color:var(--ink-mute);">Figures are filed/approved statewide '
                 'averages from each state&rsquo;s Department of Insurance; your individual change varies by '
                 'risk profile. Each row links to its source. Not a quote.</p>')
    faq = [
        (f"Which carriers raised car insurance rates in {name} in 2026?",
         "; ".join(f'{c["carrier"]} ({"+" if c["dir"]=="increase" else "-"}{c["pct"]:g}%)' for c in incs[:6]) +
         ". Each is an approved statewide-average filing — see the table for dates and sources."),
        (f"Did any carrier cut rates in {name} in 2026?",
         ("Yes — " + "; ".join(f'{c["carrier"]} (-{c["pct"]:g}%)' for c in decs) +
          ". Cuts usually reach new customers first and existing customers at renewal.") if decs
         else "No approved decreases are in our tracker for this state yet — check back as filings post."),
        ("If my carrier cut rates, will my bill go down automatically?",
         "Not necessarily. Decreases often apply to new business first and to existing customers only at "
         "renewal. Re-shopping is the reliable way to capture the lowest current rate."),
    ]
    return render(slug, title, desc, h1, dek, "\n".join(parts), faq)


def hub_page(data):
    changes = data["changes"]
    states = sorted({c["state"] for c in changes})
    by_state = {s: [c for c in changes if c["state"] == s] for s in states}
    m = data["_meta"]
    title = "Auto Insurance Rate Change Tracker (2026) — By State & Carrier"
    desc = ("Which auto insurers raised or cut rates in 2026, by state — from approved DOI filings. "
            "And how to tell if you're actually getting the new rate.")
    h1 = "Auto insurance rate change tracker &mdash; 2026"
    dek = ("Who&rsquo;s raising rates, who&rsquo;s cutting, and whether your renewal reflects it &mdash; "
           "tracked from state Department of Insurance filings.")
    parts = [
        f'<p>{esc(m["national_2026"])} '
        f'(<a class="ca-link" href="{m["national_url"]}" target="_blank" rel="noopener nofollow">{esc(m["national_source"])}</a>)</p>',
        '<div class="callout"><p><strong>The catch most drivers miss:</strong> an approved rate <em>cut</em> '
        'usually reaches new customers first &mdash; your own bill may not drop until renewal, if at all. '
        'A rate <em>hike</em>, though, hits at your next renewal. Either way, re-shopping is how you stay on the best price.</p></div>',
        '<h2>Rate changes by state</h2>',
    ]
    for s in states:
        name, slug, _ = STATE[s]
        incs = sum(1 for c in by_state[s] if c["dir"] == "increase")
        decs = sum(1 for c in by_state[s] if c["dir"] == "decrease")
        bits = []
        if incs: bits.append(f'<span style="color:{RED};">{incs} raised</span>')
        if decs: bits.append(f'<span style="color:{GREEN};">{decs} cut</span>')
        parts.append(f'<p style="margin:6px 0;"><a class="ca-link" href="/article/rate-changes/{slug}.html">'
                     f'{esc(name)} rate changes &rarr;</a> &nbsp;&middot;&nbsp; {", ".join(bits)}</p>')
    parts.append('<p style="font-size:13px;color:var(--ink-mute);margin-top:20px;">Every figure is a '
                 'filed/approved statewide-average change from a state Department of Insurance, linked to its '
                 'source. Individual rates vary by risk. Coverage expands as filings post. Not a quote.</p>')
    faq = [
        ("Are auto insurance rates going up or down in 2026?",
         esc(m["national_2026"])),
        ("If my insurer files a rate cut, do I get it automatically?",
         "Often no. Cuts typically apply to new business first and to existing customers only at renewal. "
         "Re-shop to make sure you're on the lowest current rate."),
        ("Where does this data come from?",
         "Approved rate filings reported by state Departments of Insurance and reputable outlets. Each entry "
         "links to its source. Figures are statewide averages; your change depends on your risk profile."),
    ]
    return render("index", title, desc, h1, dek, "\n".join(parts), faq)


def main():
    data = json.loads((ROOT / "rate_changes.json").read_text())
    out, _ = hub_page(data)
    print(f"  hub: {out.relative_to(ROOT)}")
    states = sorted({c["state"] for c in data["changes"]})
    for s in states:
        ch = [c for c in data["changes"] if c["state"] == s]
        out, _ = state_page(s, ch)
        print(f"  {s}: {out.relative_to(ROOT)}  ({len(ch)} filings)")


if __name__ == "__main__":
    main()
