#!/usr/bin/env python3
"""Home (homeowners) metro pages: home/metro/<slug>.html for the metros where we have a
directional HOME_METRO_OFFSET (the states we've pulled filings for). Mirrors the auto metro
pages, but home: metro avg = state avg x metro offset, carriers ranked at the metro level, and
a per-metro home-catastrophe angle (the SEO differentiator). Model + offsets parsed live from
home/index.html so pages never drift from the tool."""
import os, re, json

NATIONAL = 1915
RED, GREEN = "#b4321a", "#2f6b3a"
ROOT = os.path.dirname(os.path.abspath(__file__))


def _block(s, start, end="\n};"):
    i = s.index(start); j = s.index(end, i); return s[i + len(start):j]


def _load_model():
    s = open(os.path.join(ROOT, "home/index.html"), encoding="utf-8").read()
    states = {m.group(1): (m.group(2), int(m.group(3)))
              for m in re.finditer(r'"([A-Z]{2})":\s*\{name:\s*"([^"]+)",avg:(\d+)', _block(s, "HOME_STATE_DATA = {"))}
    carriers = []
    for chunk in re.split(r'\n  \{', _block(s, "HOME_CARRIERS = [", "\n];")):
        nm = re.search(r'name:\s*"([^"]+)"', chunk); bs = re.search(r'base:\s*([0-9.]+)', chunk)
        if not (nm and bs): continue
        st = re.search(r'states:\s*\[([^\]]*)\]', chunk)
        carriers.append((nm.group(1), float(bs.group(1)), set(re.findall(r'"([A-Z]{2})"', st.group(1))) if st else None))
    adj = {m.group(1): {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
           for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', _block(s, "STATE_CARRIER_ADJ = {"))}
    drift = {m.group(1): {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
             for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', _block(s, "HOME_DRIFT = {"))}
    off = dict(re.findall(r'"([a-z]{3,4})":\s*([0-9.]+)', _block(s, "HOME_METRO_OFFSET = {")))
    off = {k: float(v) for k, v in off.items()}
    return states, carriers, adj, drift, off


STATES, CARRIERS, STATE_CARRIER_ADJ, HOME_DRIFT, METRO_OFF = _load_model()

# code -> (display name, slug, state, peril headline, one-sentence home-risk detail)
METROS = {
 "nor": ("New Orleans", "new-orleans", "LA", "hurricanes and flooding", "Gulf hurricane exposure, storm surge, and widespread flood risk make New Orleans one of the most expensive home insurance markets in the country, and have thinned carrier availability."),
 "bat": ("Baton Rouge", "baton-rouge", "LA", "hurricanes and severe storms", "Baton Rouge sits inland of the coast but still carries significant hurricane and wind exposure, keeping premiums well above the national average though below New Orleans."),
 "nyc": ("New York City", "new-york-city", "NY", "coastal wind and high rebuilding costs", "Coastal wind exposure across Long Island and the outer boroughs, dense high-value property, and steep rebuilding costs push New York City-area home premiums well above the low upstate average."),
 "alb": ("Albany", "albany", "NY", "winter storms", "Albany's home premiums sit near the low end for New York — winter storms and ice are the main rate drivers, with little coastal exposure."),
 "buf": ("Buffalo", "buffalo", "NY", "lake-effect snow and winter storms", "Buffalo has some of the most affordable home insurance in New York; heavy lake-effect snow and winter freeze claims are the primary considerations."),
 "roc": ("Rochester", "rochester", "NY", "lake-effect snow and winter", "Rochester keeps premiums well below the New York average, with lake-effect snow and winter weather the main rate drivers."),
 "syr": ("Syracuse", "syracuse", "NY", "heavy snow and winter storms", "Syracuse's home premiums are among the lowest in New York; record snowfall and winter freeze risk are the main factors."),
 "phl": ("Philadelphia", "philadelphia", "PA", "urban density and storms", "Philadelphia runs above the Pennsylvania average — dense property, higher rebuilding and theft costs, and summer wind and hail storms are the main drivers."),
 "pit": ("Pittsburgh", "pittsburgh", "PA", "flooding and winter weather", "Pittsburgh sits near or below the Pennsylvania average, with river flooding, landslides, and winter storms the primary rate considerations."),
 "abe": ("Allentown", "allentown", "PA", "storms and winter weather", "The Lehigh Valley runs close to the Pennsylvania average, with summer storms, hail, and winter weather the main rate drivers."),
 "cle": ("Cleveland", "cleveland", "OH", "lake-effect snow and storms", "Cleveland runs slightly above the Ohio average — lake-effect snow, winter freeze claims, and summer wind and hail storms are the main drivers."),
 "akr": ("Akron", "akron", "OH", "winter weather and storms", "Akron sits near the Ohio average, with winter weather and summer wind and hail storms the primary rate considerations."),
 "col": ("Columbus", "columbus", "OH", "tornadoes, hail and winter", "Columbus prices close to the Ohio average, with spring tornadoes, hail, and winter storms the main rate drivers."),
 "cin": ("Cincinnati", "cincinnati", "OH", "flooding, tornadoes and hail", "Cincinnati sits near or just below the Ohio average, with Ohio River flooding, tornadoes, and hail the main considerations."),
 "day": ("Dayton", "dayton", "OH", "tornadoes and hail", "Dayton runs close to the Ohio average; the region's tornado and hail exposure (including the 2019 Memorial Day tornadoes) is the primary driver."),
 "chi": ("Chicago", "chicago", "IL", "hail, severe storms and winter", "Chicago-area home rates reflect dense high-value property, higher rebuilding and theft costs, frequent summer hail and wind storms, and hard winters; downstate Illinois generally prices lower."),
 "nwj": ("Newark / Jersey City", "newark", "NJ", "coastal storms and dense urban property", "The North Jersey metro (Newark, Jersey City, and the shore-adjacent counties) carries coastal wind exposure, dense high-value property, and higher rebuilding and theft costs, pricing above the low New Jersey statewide average."),
 "hou": ("Houston", "houston", "TX", "hurricanes and flooding", "Gulf hurricane exposure, tropical-storm flooding, and severe hail make Houston one of the most expensive major-metro home insurance markets in Texas and the nation."),
 "dfw": ("Dallas-Fort Worth", "dallas-fort-worth", "TX", "hail and severe storms", "Dallas-Fort Worth sits in one of the most hail-prone corridors in the country; frequent severe hail and wind storms keep premiums above the national average."),
 "aus": ("Austin", "austin", "TX", "hail, storms and flooding", "Austin faces hail, severe storms, and flash flooding along the Balcones Escarpment, keeping premiums above the national average though below the Gulf coast."),
 "san": ("San Antonio", "san-antonio", "TX", "hail and severe storms", "San Antonio's premiums reflect hail and severe-storm exposure across South-Central Texas, running above the national average."),
 "elp": ("El Paso", "el-paso", "TX", "low catastrophe exposure", "El Paso has some of the lowest home premiums in Texas thanks to its arid climate and limited catastrophe exposure."),
 "sjv": ("San Jose", "san-jose", "CA", "wildfire and high rebuilding costs", "Bay Area home premiums are driven by wildland-urban-interface wildfire risk and some of the highest rebuilding costs in the nation; note earthquake is a separate policy."),
 "sdg": ("San Diego", "san-diego", "CA", "wildfire and coastal exposure", "San Diego's rates reflect backcountry wildfire risk and coastal rebuilding costs; earthquake coverage is separate from a standard policy."),
 "riv": ("Riverside / Inland Empire", "riverside-inland-empire", "CA", "wildfire", "The Inland Empire carries significant wildland-urban-interface wildfire exposure, the main driver of home premiums; earthquake is written separately."),
 "sac": ("Sacramento", "sacramento", "CA", "wildfire and flood risk", "Sacramento faces both foothill wildfire risk and Central Valley flood exposure; earthquake coverage is separate from a standard policy."),
 "fre": ("Fresno", "fresno", "CA", "lower catastrophe exposure", "Fresno keeps home premiums below the California coastal metros, with Central Valley heat and localized flood the main considerations; earthquake is separate."),
 "bak": ("Bakersfield", "bakersfield", "CA", "lower catastrophe exposure", "Bakersfield's premiums sit below the California coastal average, with wildfire on the valley edges and earthquake (written separately) the main considerations."),
}


def slugify(n): return n.lower().replace(".", "").replace(" / ", "-").replace(" ", "-")


def tier_phrase(avg):
    r = avg / NATIONAL
    if r < 0.78: return "well below the national average"
    if r < 0.92: return "below the national average"
    if r <= 1.10: return "near the national average"
    if r <= 1.45: return "above the national average"
    return "well above the national average"


def rank(code, offset):
    avg = STATES[code][1]
    tilt = STATE_CARRIER_ADJ.get(code, {}); drift = HOME_DRIFT.get(code, {})
    avail = [(n, round(avg * b * tilt.get(n, 1) * drift.get(n, 1) * offset)) for (n, b, st) in CARRIERS
             if (st is None or code in st)]
    avail.sort(key=lambda x: x[1])
    top = avail[:10]; prices = sorted(p for _, p in top); m = len(prices) // 2
    median = prices[m] if len(prices) % 2 else round((prices[m - 1] + prices[m]) / 2)
    return round(avg * offset), top, median


scaff = open(os.path.join(ROOT, "renters/state/colorado.html"), encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>") + len("</style>")]
NAV = scaff[scaff.index('<header class="top">'):scaff.index("</header>") + len("</header>")]
TAIL = scaff[scaff.index("<footer>"):]
TAIL = TAIL.replace("/renters/index.html?zip=", "/home/index.html?zip=").replace('window.location.href="/renters/"', 'window.location.href="/home/"')


def esc(s): return s.replace('"', "&quot;")


def build(code):
    name, slug, st, peril, detail = METROS[code]
    offset = METRO_OFF[code]
    st_name = STATES[st][0]
    avg, top, median = rank(st, offset)
    monthly = round(avg / 12)
    tphrase = tier_phrase(avg)
    c1, c2, c3 = [n for n, _ in top[:3]]
    url = f"https://boringrate.com/home/metro/{slug}.html"
    desc = (f"Home insurance in {name} averages about ${avg:,}/year — {tphrase}. The cheapest carriers are "
            f"{c1}, {c2} and {c3}. Compare homeowners rates for your ZIP.")
    rows = ""
    for i, (n, p) in enumerate(top):
        d = p - median
        vs = (f'<span style="color:{GREEN};font-weight:600;">Save ${abs(d):,}</span>' if d <= 0
              else f'<span style="color:{RED};font-weight:600;">+${d:,}</span>')
        rows += (f'<tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;color:var(--ink-mute);">{i+1}</td>'
                 f'<td style="padding:8px 6px;"><strong>{n}</strong></td><td style="padding:8px 6px;">${p:,}/yr</td>'
                 f'<td style="padding:8px 6px;">{vs}</td></tr>')

    faq = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f"How much is homeowners insurance in {name}?",
         "acceptedAnswer": {"@type": "Answer", "text": f"Homeowners insurance in {name} averages about ${avg:,} per year (roughly ${monthly:,}/month) for a standard policy with about $300,000 in dwelling coverage and a $1,000 deductible — {tphrase} of about ${NATIONAL:,}. Rates vary widely by ZIP, dwelling amount, roof age, and claims history."}},
        {"@type": "Question", "name": f"What is the cheapest home insurance in {name}?",
         "acceptedAnswer": {"@type": "Answer", "text": f"{c1}, {c2}, and {c3} are consistently among the cheapest home insurance options in {name} for a standard policy. Pricing varies by your dwelling amount, deductible, and exact ZIP — enter your ZIP to compare current carrier rankings."}},
        {"@type": "Question", "name": f"Why is home insurance {'expensive' if avg > NATIONAL else 'priced the way it is'} in {name}?",
         "acceptedAnswer": {"@type": "Answer", "text": f"{name}-area home rates are driven largely by {peril}. {detail} Within the metro, individual ZIPs can price well above or below this average, and your own rate also depends on your home's age, roof, and claims history."}},
    ]})
    crumb = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "BoringRate", "item": "https://boringrate.com"},
        {"@type": "ListItem", "position": 2, "name": "Home Insurance", "item": "https://boringrate.com/home/index.html"},
        {"@type": "ListItem", "position": 3, "name": f"{name} Home Insurance", "item": url}]})

    head = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(name)} Home Insurance Rates (2026) — Average Cost &amp; Cheapest Carriers | BoringRate</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
<meta property="og:title" content="{esc(name)} Home Insurance Rates (2026)" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<script type="application/ld+json">{crumb}</script>
<script type="application/ld+json">{faq}</script>
</head>
<body>'''

    body = f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/home/index.html">Home Insurance</a> &nbsp;·&nbsp; <a href="/home/state/{slugify(st_name)}.html">{esc(st_name)}</a> &nbsp;·&nbsp; {esc(name)}</div>
    <h1 class="article-title">Home insurance in {esc(name)}: average cost &amp; cheapest carriers (2026)</h1>
    <p class="article-dek">{esc(name)} homeowners insurance averages about <strong>${avg:,}/year</strong> &mdash; {tphrase}. Here&rsquo;s who&rsquo;s cheapest, and why {esc(name)} prices the way it does.</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; directional estimates from public rate filings &amp; NAIC data</div>
  </div>
  <div class="article-body">
    <h2>Cheapest home insurance carriers in {esc(name)}</h2>
    <p>Estimated annual premiums for a standard policy (~$300k dwelling, $1,000 deductible), ranked cheapest first &mdash; {esc(name)} averages about <strong>${avg:,}/yr</strong> (median of the carriers below: ${median:,}/yr). Enter ZIP for a ranking tuned to your home.</p>
    <table style="width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:660px;">
    <thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;"><th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">Carrier</th><th style="padding:8px 6px;">Est. annual</th><th style="padding:8px 6px;">vs median</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <form onsubmit="event.preventDefault();var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);if(/^\\d{{5}}$/.test(z)){{location.href='/home/?zip='+z}}else{{this.zc.focus()}}" style="display:flex;gap:0;max-width:360px;margin:16px 0;">
    <input name="zc" type="text" inputmode="numeric" maxlength="5" placeholder="Enter ZIP" aria-label="ZIP code" style="flex:1;min-width:0;font-family:var(--mono);font-size:16px;letter-spacing:0.12em;padding:12px 14px;border:2px solid var(--ink);border-right:none;background:var(--paper);color:var(--ink);outline:none;" />
    <button type="submit" style="font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:0 20px;border:2px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;">See rates &rarr;</button></form>

    <h2>Why home insurance costs what it does in {esc(name)}</h2>
    <p>{esc(name)}-area home insurance is priced mainly around <strong>{peril}</strong>. {detail}</p>
    <div class="callout"><p><strong>The metro average hides your ZIP.</strong> A single carrier can price neighboring ZIPs very differently &mdash; coastal, wildfire, or older-home areas load high while lower-risk pockets pay less. This page is a {esc(name)}-level estimate; <a href="/home/index.html">compare carriers for your exact ZIP</a> to see where you land, and see <a href="/home/why-did-my-home-insurance-go-up.html">why your rate can jump even when your carrier&rsquo;s filing looks flat</a>.</p></div>

    <p style="font-size:14px;"><a class="ca-link" href="/home/state/{slugify(st_name)}.html">See all {esc(st_name)} home rates &amp; carriers &rarr;</a> &nbsp;·&nbsp; <a class="ca-link" href="/home/rate-changes/{slugify(st_name)}.html">Who&rsquo;s raising &amp; cutting {esc(st_name)} home rates &rarr;</a></p>
    <p style="font-size:13px;color:var(--ink-mute);max-width:660px;margin-top:14px;">Directional estimates from public rate filings and NAIC data &mdash; not a quote. Metro figures apply a modeled {esc(name)} offset to the {esc(st_name)} average; your actual rate depends on dwelling amount, deductible, roof age, claims history, and exact ZIP.</p>
  </div>
</div>'''
    return head + "\n" + NAV + "\n" + body + "\n" + TAIL


def main():
    outdir = os.path.join(ROOT, "home", "metro")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for code in METROS:
        if code not in METRO_OFF:
            continue
        _, slug, _, _, _ = METROS[code]
        open(os.path.join(outdir, f"{slug}.html"), "w", encoding="utf-8").write(build(code))
        n += 1
    print(f"wrote {n} home metro pages -> home/metro/")


if __name__ == "__main__":
    main()
