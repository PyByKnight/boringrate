#!/usr/bin/env python3
"""Home (homeowners) rate-change tracker — the parallel to gen_rate_tracker.py (auto).

Reads serff_home_filings.json (single source), filters to material moves (|%|>=0.5),
and builds per-state 'who raised / who cut home rates in [state]' pages + a hub, under
home/rate-changes/. Same reactive-shopper angle as the auto tracker; homeowners voice.
Page skeleton reuses the gen_home_faq.py scaffold (home/state/florida.html)."""
import json, re, pathlib
from datetime import date
from gen_metro_page import STATE, esc, _json

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "serff_home_filings.json"
OUTDIR = ROOT / "home" / "rate-changes"
RED, GREEN = "#b4321a", "#2f6b3a"
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MIN = 0.5  # material-move threshold

scaff = (ROOT / "home" / "state" / "florida.html").read_text(encoding="utf-8")
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>") + len("</style>")]
NAV = scaff[scaff.index('<header class="top">'):scaff.index("</header>") + len("</header>")]
TAIL = scaff[scaff.index("<footer>"):]
TAIL = re.sub(r'Compare [A-Za-z ]+ rates <span class="ascta-arrow">', 'Compare home rates <span class="ascta-arrow">', TAIL)


def fdate(iso):
    if not iso:
        return "—"
    p = iso.split("-")
    if len(p) == 1:
        return p[0]
    if len(p) == 2:
        return f"{MONTHS[int(p[1])]} {p[0]}"
    return f"{MONTHS[int(p[1])]} {int(p[2])}, {p[0]}"


def signed(pct, dr):
    s = ("+" if dr == "increase" else "−") + f"{abs(pct):g}%"
    return f'<span style="color:{RED if dr == "increase" else GREEN};font-weight:600;">{s}</span>'


ZIPBOX = ('<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);'
          'if(/^\\d{5}$/.test(z)){location.href=\'/home/?zip=\'+z}else{this.zc.focus()}" '
          'style="display:flex;gap:0;max-width:360px;margin:16px 0;">'
          '<input name="zc" type="text" inputmode="numeric" maxlength="5" placeholder="Enter your ZIP" aria-label="ZIP code" '
          'style="flex:1;min-width:0;font-family:var(--mono);font-size:16px;letter-spacing:0.12em;padding:12px 14px;border:2px solid var(--ink);border-right:none;background:var(--paper);color:var(--ink);outline:none;" />'
          '<button type="submit" style="font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:0 20px;border:2px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;">Compare home rates &rarr;</button></form>')


def rows_table(changes):
    head = ('<table style="width:100%;border-collapse:collapse;font-size:15px;margin:18px 0;">'
            '<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">'
            '<th style="padding:9px 8px;">Carrier</th><th>Change</th><th>Effective</th><th>Source</th></tr></thead><tbody>')
    body = []
    for c in sorted(changes, key=lambda x: (x.get("effective_new") or "", -abs(x["overall_pct"]))):
        src = f'<a class="ca-link" href="{c["url"]}" target="_blank" rel="noopener nofollow">{esc(c["source_note"].split(";")[0])}</a>'
        body.append(
            f'<tr style="border-bottom:1px solid var(--rule);"><td style="padding:9px 8px;"><strong>{esc(c["carrier"])}</strong>'
            f'<span style="color:var(--ink-mute);font-size:12px;"> &nbsp;{esc(c.get("entity",""))}</span></td>'
            f'<td>{signed(c["overall_pct"], c["dir"])}</td><td>{fdate(c.get("effective_new"))}</td><td style="font-size:13px;">{src}</td></tr>')
    return head + "".join(body) + "</tbody></table>"


def head_html(url, title, desc, faq):
    faq_items = ",".join('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}' % (_json(q), _json(a)) for q, a in faq)
    jsonld = ('<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' + faq_items + ']}\n</script>')
    return f'''<!DOCTYPE html>
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
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
{jsonld}
</head>
<body>'''


def page(slug, title, desc, h1, dek, body_html, faq):
    url = f"https://boringrate.com/home/rate-changes/{slug}.html" if slug != "index" else "https://boringrate.com/home/rate-changes/"
    body = f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/home/index.html">Home Insurance</a> &nbsp;·&nbsp; Home Rate Tracker &nbsp;·&nbsp; Updated {date.today():%B %Y}</div>
    <h1 class="article-title">{h1}</h1>
    <p class="article-dek">{dek}</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; sourced from state DOI filings</div>
  </div>
  <div class="article-body">
    {body_html}
  </div>
</div>'''
    html = head_html(url, title, desc, faq) + "\n" + NAV + "\n" + body + "\n" + TAIL
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / f"{slug}.html").write_text(html, encoding="utf-8")
    return url


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
    max_inc = max((c["overall_pct"] for c in incs), default=0)
    title = f"{name} Homeowners Insurance Rate Changes (2026) — Who Raised, Who Cut"
    desc = (f"{summary[0].upper() + summary[1:]} {name} homeowners insurance rates in 2026. "
            f"See the filings, effective dates, and whether you're getting the new rate.")
    h1 = f"{name} homeowners insurance rate changes in 2026"
    dek = (f"{summary[0].upper() + summary[1:]} rates in {name} this year &mdash; from approved state DOI filings. "
           "Here&rsquo;s who, by how much, and whether your renewal reflects it.")
    if incs and decs:
        lead = f"{phrase(len(incs), 'raised')} and {phrase(len(decs), 'cut')} {name} homeowners rates in 2026."
    elif incs:
        upto = f" by up to {max_inc:g}%" if max_inc else ""
        lead = f"{phrase(len(incs), 'raised')} {name} homeowners rates{upto} in 2026 &mdash; you may be overpaying."
    else:
        lead = f"{phrase(len(decs), 'cut')} {name} homeowners rates in 2026 &mdash; make sure you're actually getting it."
    parts = [
        f'<p style="font-size:20px;line-height:1.45;color:var(--ink);max-width:660px;"><strong>{lead}</strong> '
        f'Homeowners rate hikes hit at renewal &mdash; the fastest way to stop overpaying is to compare carriers for your ZIP.</p>',
        ZIPBOX,
    ]
    if incs:
        parts.append(f'<h2>Carriers that raised {esc(name)} home rates in 2026</h2>' + rows_table(incs))
    if decs:
        parts.append(f'<h2>Carriers that cut {esc(name)} home rates in 2026</h2>' + rows_table(decs))
    parts.append(
        '<div class="callout"><p><strong>Are you actually getting the new rate?</strong><br>'
        'Approved changes are statewide averages, and they reach your policy at <em>renewal</em>. A cut often '
        'reaches new buyers first; a hike lands on your next renewal notice. Re-shopping is the only way to know '
        'you&rsquo;re on the best current price for your home.</p></div>')
    parts.append('<p style="font-size:13px;color:var(--ink-mute);">Figures are filed/approved statewide-average '
                 'changes from each state&rsquo;s Department of Insurance (CA via CDI, TX via data.texas.gov, others via SERFF). '
                 'Individual rates vary by home, roof age, and risk. Each filing links to its source. Not a quote.</p>')
    faq = []
    if incs:
        faq.append((f"Which insurers raised homeowners rates in {name} in 2026?",
                    "; ".join(f'{c["carrier"]} (+{c["overall_pct"]:g}%)' for c in incs[:6]) +
                    ". Each is an approved statewide-average filing — see the table for dates and sources."))
    if decs:
        faq.append((f"Which insurers cut homeowners rates in {name} in 2026?",
                    "; ".join(f'{c["carrier"]} (-{abs(c["overall_pct"]):g}%)' for c in decs) +
                    ". Cuts usually reach new customers first and existing customers at renewal."))
    faq.append(("Will my homeowners bill change automatically if my insurer files a new rate?",
                "No — filed changes reach your policy at your next renewal, and a cut may apply to new business first. "
                "Re-shopping is the reliable way to capture the lowest current rate."))
    faq.append((f"Where does this {name} homeowners rate data come from?",
                "Approved rate filings from the state Department of Insurance. Figures are statewide averages; "
                "your change depends on your home and risk profile. Each row links to its source."))
    return page(slug, title, desc, h1, dek, "\n".join(parts), faq)


def hub_page(by_state):
    title = "Homeowners Insurance Rate Change Tracker (2026) — By State & Carrier"
    desc = ("Which home insurers raised or cut rates in 2026, by state — from approved DOI filings. "
            "And how to tell if you're actually getting the new rate.")
    h1 = "Homeowners insurance rate change tracker &mdash; 2026"
    dek = ("Who&rsquo;s raising home rates, who&rsquo;s cutting, and whether your renewal reflects it &mdash; "
           "tracked from state Department of Insurance filings.")
    parts = [
        '<p>Homeowners insurance is the sharp edge of the 2025–26 rate crisis — climate losses and '
        'reinsurance costs are pushing double-digit increases in the hardest-hit states, while a few carriers cut. '
        'We track the approved filings so you can see who moved, by how much, and whether your renewal reflects it.</p>',
        '<div class="callout"><p><strong>The catch:</strong> a filed rate change reaches your policy at '
        '<em>renewal</em>. A hike lands on your next bill; a cut may reach new buyers first. Either way, '
        're-shopping is how you stay on the best price.</p></div>',
        '<h2>States we track carrier-by-carrier</h2>',
    ]
    for s in sorted(by_state, key=lambda c: STATE[c][0]):
        name, slug, _ = STATE[s]
        incs = sum(1 for c in by_state[s] if c["dir"] == "increase")
        decs = sum(1 for c in by_state[s] if c["dir"] == "decrease")
        bits = []
        if incs: bits.append(f'<span style="color:{RED};">{incs} raised</span>')
        if decs: bits.append(f'<span style="color:{GREEN};">{decs} cut</span>')
        parts.append(f'<p style="margin:6px 0;"><a class="ca-link" href="/home/rate-changes/{slug}.html">'
                     f'{esc(name)} home rate-change tracker &rarr;</a> &nbsp;·&nbsp; {", ".join(bits)}</p>')
    parts.append(ZIPBOX)
    parts.append('<p style="font-size:13px;color:var(--ink-mute);margin-top:18px;">Carrier filings are '
                 'filed/approved statewide-average changes from state Departments of Insurance (each row linked to '
                 'its source). Individual rates vary by home and risk. Not a quote.</p>')
    faq = [
        ("Are homeowners insurance rates going up in 2026?",
         "In many states, sharply — climate losses and reinsurance costs are driving double-digit increases in "
         "the hardest-hit markets (Texas home filings run to +20–30%), though a few carriers have filed cuts."),
        ("How do I tell if I'm getting a filed rate cut?",
         "Filed changes reach your policy at renewal, and cuts often apply to new business first. Re-shop your ZIP "
         "to confirm you're on the lowest current rate."),
    ]
    return page("index", title, desc, h1, dek, "\n".join(parts), faq)


def main():
    data = json.load(open(SRC))
    changes = []
    for r in data["filings"]:
        if r.get("line") != "home" or r.get("overall_pct") is None or abs(r["overall_pct"]) < MIN:
            continue
        r = dict(r)
        r["dir"] = "increase" if r["overall_pct"] > 0 else "decrease"
        changes.append(r)
    by_state = {}
    for c in changes:
        by_state.setdefault(c["state"], []).append(c)
    for code, ch in by_state.items():
        u = state_page(code, ch)
        print("wrote", u)
    print("wrote", hub_page(by_state))
    print(f"done: {len(by_state)} states, {len(changes)} material moves")


if __name__ == "__main__":
    main()
