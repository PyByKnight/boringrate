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
# cheapest-carrier rankings, exported by `node gen_state_rankings.js --export`
_RANKF = ROOT / "state_rankings.json"
RANKINGS = json.loads(_RANKF.read_text()) if _RANKF.exists() else {}


def ranking_block(code, name):
    """Embed the 'cheapest carriers' ranking + a ZIP entry box on a tracker page."""
    r = RANKINGS.get(code)
    if not r:
        return ""
    rows = []
    for i, c in enumerate(r["top"]):
        d = c["price"] - r["median"]
        vs = (f'<span style="color:{GREEN};font-weight:600;">Save ${abs(d):,}</span>' if d <= 0
              else f'<span style="color:{RED};font-weight:600;">+${d:,}</span>')
        rows.append(f'<tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;color:var(--ink-mute);">{i+1}</td>'
                    f'<td style="padding:8px 6px;"><strong>{esc(c["name"])}</strong></td>'
                    f'<td style="padding:8px 6px;">${c["price"]:,}/yr</td><td style="padding:8px 6px;">{vs}</td></tr>')
    table = ('<table style="width:100%;border-collapse:collapse;font-size:16px;margin:14px 0;max-width:660px;">'
             '<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">'
             '<th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">Carrier</th><th style="padding:8px 6px;">Est. annual</th><th style="padding:8px 6px;">vs avg</th></tr></thead>'
             '<tbody>' + "".join(rows) + '</tbody></table>')
    zipbox = ('<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);'
              'if(/^\\d{5}$/.test(z)){location.href=\'/?zip=\'+z}else{this.zc.focus()}" '
              'style="display:flex;gap:0;max-width:360px;margin:16px 0;">'
              '<input name="zc" type="text" inputmode="numeric" maxlength="5" placeholder="Enter your ZIP" aria-label="ZIP code" '
              'style="flex:1;min-width:0;font-family:var(--mono);font-size:16px;letter-spacing:0.12em;padding:12px 14px;border:2px solid var(--ink);border-right:none;background:var(--paper);color:var(--ink);outline:none;" />'
              '<button type="submit" style="font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:0 20px;border:2px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;">See rates &rarr;</button></form>')
    return (f'<h2>Cheapest car insurance carriers in {esc(name)} right now</h2>'
            f'<p>Estimated annual premiums for a standard profile, cheapest first &mdash; {esc(name)} averages about '
            f'<strong>${r["avg"]:,}/yr</strong>. The spread between carriers is wide, so shopping is how you beat a rate hike.</p>'
            + table + zipbox)


def fdate(iso):
    p = iso.split("-")
    if len(p) == 1:
        return p[0]                                  # year only
    if len(p) == 2:
        return f"{MONTHS[int(p[1])]} {p[0]}"         # year-month
    return f"{MONTHS[int(p[1])]} {int(p[2])}, {p[0]}"


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
    # lambda replacements so backslashes in the HTML (e.g. \d in the ZIP form onsubmit)
    # aren't interpreted as regex escapes
    html = re.sub(r'<div class="article-header">.*?</div>\s*<div class="article-body">',
                  lambda _m: header, html, count=1, flags=re.DOTALL)
    body_repl = '<div class="article-body">\n' + body_html + '\n    <div class="article-email">'
    html = re.sub(r'<div class="article-body">.*?<div class="article-email">',
                  lambda _m: body_repl, html, count=1, flags=re.DOTALL)
    html = html.replace("when Atlanta rates move", "when rates move in your area")
    html = html.replace("Compare Atlanta rates", "Compare rates")

    OUTDIR.mkdir(exist_ok=True)
    out = OUTDIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return out, url


def rows_table(changes):
    head = ('<table style="width:100%;border-collapse:collapse;font-size:15px;margin:18px 0;">'
            '<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">'
            '<th style="padding:9px 8px;">Carrier</th><th>Change</th><th>Effective</th><th>Affected</th><th>Source</th></tr></thead><tbody>')
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
    def phrase(n, verb):
        return f"{n} carrier{'s' if n != 1 else ''} {verb}"
    bits = []
    if incs: bits.append(phrase(len(incs), "raised"))
    if decs: bits.append(phrase(len(decs), "cut"))
    summary = " and ".join(bits) if bits else "carriers changed"
    title = f"{name} Auto Insurance Rate Changes (2026) — Who Raised, Who Cut"
    desc = (f"{summary[0].upper() + summary[1:]} {name} auto rates in 2026. "
            f"See the filings, effective dates, and whether you're getting the new rate.")
    h1 = f"{name} auto insurance rate changes in 2026"
    dek = (f"{summary[0].upper() + summary[1:]} rates in {name} this year &mdash; from approved DOI filings. "
           "Here&rsquo;s who, by how much, and whether your renewal reflects it.")
    parts = []
    # 1) data-driven headline + "shop for a better rate" CTA
    max_inc = max((c["pct"] for c in incs), default=0)
    if incs and decs:
        lead = f"{phrase(len(incs), 'raised')} and {phrase(len(decs), 'cut')} {name} auto rates in 2026."
    elif incs:
        upto = f" by up to {max_inc:g}%" if max_inc else ""
        lead = f"{phrase(len(incs), 'raised')} {name} auto rates{upto} in 2026 — you may be overpaying."
    else:
        lead = f"{phrase(len(decs), 'cut')} {name} auto rates in 2026 — make sure you're actually getting it."
    parts.append(f'<p style="font-size:20px;line-height:1.45;color:var(--ink);max-width:660px;"><strong>{lead}</strong> '
                 f'The fastest way to stop overpaying is to compare carriers for your ZIP &mdash; the cheapest options in {esc(name)} are below.</p>')
    # 2) cheapest carriers + ZIP entry box
    parts.append(ranking_block(code, name))
    # 3) the filing detail (who changed, by how much, sourced)
    if incs:
        parts.append(f'<h2>Carriers that raised {esc(name)} rates in 2026</h2>' + rows_table(incs))
    if decs:
        parts.append(f'<h2>Carriers that cut {esc(name)} rates in 2026</h2>' + rows_table(decs))
    # 4) the existing-customer catch
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
    parts.append('<p style="font-size:13px;color:var(--ink-mute);">Filing figures are filed/approved statewide '
                 'averages from each state&rsquo;s Department of Insurance; rankings are directional estimates. '
                 '&ldquo;Affected&rdquo; counts are policyholders or insured vehicles as stated in each filing. '
                 'Your individual rate varies by risk profile. Each filing links to its source. Not a quote.</p>')
    faq = []
    if incs:
        faq.append((f"Which carriers raised car insurance rates in {name} in 2026?",
                    "; ".join(f'{c["carrier"]} (+{c["pct"]:g}%)' for c in incs[:6]) +
                    ". Each is an approved statewide-average filing — see the table for dates and sources."))
    if decs:
        faq.append((f"Which carriers cut car insurance rates in {name} in 2026?",
                    "; ".join(f'{c["carrier"]} (-{c["pct"]:g}%)' for c in decs) +
                    ". Cuts usually reach new customers first and existing customers only at renewal."))
    faq.append(("If my carrier cut rates, will my bill go down automatically?",
                "Not necessarily. Decreases often apply to new business first and to existing customers only at "
                "renewal. Re-shopping is the reliable way to capture the lowest current rate."))
    faq.append((f"Where does this {name} rate-change data come from?",
                "Approved rate filings from the state Department of Insurance and reputable outlets — each row "
                "links to its source. Figures are statewide averages; your change depends on your risk profile."))
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
    sw = data["statewide_2026"]
    parts = [
        f'<p>{esc(m["national_2026"])} '
        f'(<a class="ca-link" href="{m["national_url"]}" target="_blank" rel="noopener nofollow">{esc(m["national_source"])}</a>)</p>',
        '<div class="callout"><p><strong>The catch most drivers miss:</strong> an approved rate <em>cut</em> '
        'usually reaches new customers first &mdash; your own bill may not drop until renewal, if at all. '
        'A rate <em>hike</em>, though, hits at your next renewal. Either way, re-shopping is how you stay on the best price.</p></div>',
    ]
    if m.get("dividend_note"):
        extra = ""
        if m.get("statefarm_cuts"):
            extra = (" " + esc(m["statefarm_cuts"]) +
                     f' (<a class="ca-link" href="{m["statefarm_cuts_url"]}" target="_blank" rel="noopener nofollow">State Farm</a>)')
        parts.append('<div class="callout"><p><strong>Biggest 2026 story:</strong> '
                     + esc(m["dividend_note"]) +
                     f' (<a class="ca-link" href="{m["dividend_url"]}" target="_blank" rel="noopener nofollow">State Farm</a>).'
                     + extra + '</p></div>')
    # deep-dive states (carrier-by-carrier filings)
    if states:
        parts.append('<h2>States we track carrier-by-carrier</h2>')
        for s in states:
            name, slug, _ = STATE[s]
            incs = sum(1 for c in by_state[s] if c["dir"] == "increase")
            decs = sum(1 for c in by_state[s] if c["dir"] == "decrease")
            bits = []
            if incs: bits.append(f'<span style="color:{RED};">{incs} raised</span>')
            if decs: bits.append(f'<span style="color:{GREEN};">{decs} cut</span>')
            parts.append(f'<p style="margin:6px 0;"><a class="ca-link" href="/article/rate-changes/{slug}.html">'
                         f'{esc(name)} rate-change tracker &rarr;</a> &nbsp;&middot;&nbsp; {", ".join(bits)}</p>')
    # full 51-state projected-change table (the supplement)
    parts.append('<h2>2026 projected rate change &mdash; every state</h2>')
    parts.append('<p>Projected statewide <em>average</em> change for 2026 from '
                 f'<a class="ca-link" href="{sw["_url"]}" target="_blank" rel="noopener nofollow">{esc(sw["_source"])}</a>. '
                 'These are modest market-wide projections &mdash; individual carriers still file double-digit '
                 'moves (see the trackers above). Your own rate depends on your ZIP and profile.</p>')
    deep = set(states)
    rows = []
    for code in sorted([k for k in sw if not k.startswith("_")], key=lambda c: STATE[c][0]):
        name, slug, _ = STATE[code]
        pct, prem = sw[code]
        color = RED if pct > 0 else (GREEN if pct < 0 else "var(--ink-mute)")
        chg = ("+" if pct > 0 else ("−" if pct < 0 else "±")) + f"{abs(pct):g}%"
        if code in deep:
            link = f'<a class="ca-link" href="/article/rate-changes/{slug}.html">tracker &rarr;</a>'
        else:
            link = f'<a class="ca-link" href="/article/state/{slug}.html">state report &rarr;</a>'
        rows.append(f'<tr style="border-bottom:1px solid var(--rule);"><td style="padding:7px 8px;">{esc(name)}</td>'
                    f'<td style="color:{color};font-weight:600;">{chg}</td><td>${prem:,}</td><td style="font-size:13px;">{link}</td></tr>')
    parts.append('<table style="width:100%;border-collapse:collapse;font-size:15px;margin:14px 0;">'
                 '<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">'
                 '<th style="padding:8px;">State</th><th>2026 proj.</th><th>Avg premium</th><th></th></tr></thead><tbody>'
                 + "".join(rows) + '</tbody></table>')
    parts.append('<p style="font-size:13px;color:var(--ink-mute);margin-top:18px;">Carrier filings are '
                 'filed/approved statewide-average changes from state Departments of Insurance (each row linked to '
                 'its source). State projections are Insurify forecasts. Individual rates vary by risk. Not a quote.</p>')
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
