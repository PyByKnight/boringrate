#!/usr/bin/env python3
# Generate the home (homeowners) state article tree: home/state/<slug>.html for all
# 50 states + DC. Uses renters/state/colorado.html as the structural scaffold (inherits
# the exact CSS / nav / footer / sticky-CTA), swapping in homeowners content. Each page
# is differentiated by the state's catastrophe profile (the SEO/quality differentiator)
# plus its average premium and a generated cheapest-carrier ranking from HOME_CARRIERS.
import os, json, re
from plausible_snippet import ensure

NATIONAL = 1915
RED, GREEN = "#b4321a", "#2f6b3a"

# ── Model: parsed live from home/index.html so the static state pages never drift
# from the tool (roster, state averages, and the per-state carrier offset). ──
def _block(s, start, end="\n};"):
    i = s.index(start); j = s.index(end, i); return s[i+len(start):j]

def _load_model():
    s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "home/index.html"), encoding="utf-8").read()
    # State averages -> {code: (name, avg)}
    states = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{name:\s*"([^"]+)",avg:(\d+)', _block(s, "HOME_STATE_DATA = {")):
        states[m.group(1)] = (m.group(2), int(m.group(3)))
    # Carriers -> list of (name, base, states_set_or_None); national = no states: array
    carriers = []
    for chunk in re.split(r'\n  \{', _block(s, "HOME_CARRIERS = [", "\n];")):
        nm = re.search(r'name:\s*"([^"]+)"', chunk)
        bs = re.search(r'base:\s*([0-9.]+)', chunk)
        if not (nm and bs):
            continue
        st = re.search(r'states:\s*\[([^\]]*)\]', chunk)
        states_set = set(re.findall(r'"([A-Z]{2})"', st.group(1))) if st else None
        carriers.append((nm.group(1), float(bs.group(1)), states_set))
    # Per-state carrier offset -> {code: {name: mult}}
    adj = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', _block(s, "STATE_CARRIER_ADJ = {")):
        adj[m.group(1)] = {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
    # Primary-source drift layer (apply_home_filings.py) -> {code: {name: mult}}; applied on top of adj.
    drift = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', _block(s, "HOME_DRIFT = {")):
        drift[m.group(1)] = {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
    return states, carriers, adj, drift

STATES, CARRIERS, STATE_CARRIER_ADJ, HOME_DRIFT = _load_model()

# ── Per-state catastrophe / cost driver (the differentiator) ──
# (peril phrase, one-sentence detail)
RISK = {
 "AL":("hurricanes and severe storms","Gulf Coast hurricane exposure and frequent spring tornadoes and hail across the state push Alabama premiums well above the national average, with coastal counties paying the most."),
 "AK":("winter weather and remote rebuilding costs","Alaska's low premiums reflect limited catastrophe exposure, though long winters, freeze claims, and high remote-area rebuilding costs factor into rates."),
 "AZ":("wildfire and monsoon hail/wind","Arizona stays below the national average, but wildfire risk in the wildland-urban interface and monsoon-season hail and microbursts drive rates in higher-risk ZIPs."),
 "AR":("tornadoes and hail","Arkansas sits in the path of frequent spring tornadoes and damaging hail, which keeps premiums noticeably above the national average."),
 "CA":("wildfire (earthquake is separate)","California's headline risk is wildfire, which has reshaped the market and the FAIR Plan; note that earthquake is excluded from standard policies and requires a separate policy."),
 "CO":("hail and wildfire","Colorado is one of the most hail-prone states in the country, and growing wildfire exposure along the Front Range has pushed premiums sharply above the national average."),
 "CT":("coastal storms and Nor'easters","Connecticut's rates reflect coastal wind exposure along Long Island Sound and winter Nor'easters, though it remains below the national average."),
 "DC":("dense urban property and storms","The District's relatively low average reflects compact housing stock; the main rate drivers are wind/hail storms and high rebuilding costs in a dense market."),
 "DE":("low catastrophe exposure","Delaware has some of the lowest home premiums in the country thanks to limited catastrophe exposure, with coastal storms the main consideration near the shore."),
 "FL":("hurricanes and a stressed market","Florida is the most expensive home insurance market in the nation — hurricane exposure, litigation, and reinsurance costs have driven premiums far above every other state, and many buyers rely on Citizens or surplus-lines carriers."),
 "GA":("tornadoes, hail and hurricanes","Georgia faces a mix of spring tornadoes, hail, and occasional hurricane remnants, keeping premiums modestly above the national average."),
 "HI":("hurricane and volcanic risk","Hawaii's average looks low, but standard policies often exclude hurricane and lava, which are written separately — so the headline premium understates total coverage cost for many homeowners."),
 "ID":("wildfire","Idaho enjoys some of the lowest premiums nationally; wildfire in the wildland-urban interface is the main driver in higher-risk mountain ZIPs."),
 "IL":("tornadoes, hail and winter storms","Illinois rates reflect Midwest tornado and hail exposure plus hard winters, landing near the national average."),
 "IN":("tornadoes and hail","Indiana sits near the national average, with spring tornadoes and hail the primary storm-related rate drivers."),
 "IA":("tornadoes, hail and derechos","Iowa's exposure to tornadoes, hail, and derecho windstorms (like the 2020 event) keeps premiums close to the national average."),
 "KS":("tornadoes and hail (Tornado Alley)","Kansas sits in the heart of Tornado Alley — frequent tornadoes and severe hail make it one of the most expensive home insurance states in the country."),
 "KY":("tornadoes, wind and flooding","Kentucky faces tornadoes, straight-line wind, and river flooding, pushing premiums above the national average."),
 "LA":("hurricanes and flooding","Louisiana is among the most expensive markets in the nation — Gulf hurricane exposure and widespread flood risk have driven premiums sharply higher and thinned carrier availability."),
 "ME":("Nor'easters and winter storms","Maine keeps premiums below the national average; winter storms, ice, and coastal Nor'easters are the main rate drivers."),
 "MD":("coastal storms and hail","Maryland stays below the national average, with Chesapeake-area wind and inland hail the primary considerations."),
 "MA":("Nor'easters and coastal wind","Massachusetts rates reflect coastal wind exposure and winter Nor'easters, landing modestly below the national average."),
 "MI":("winter weather and storms","Michigan sits near the national average; winter freeze claims and severe summer storms are the main drivers."),
 "MN":("hail, wind and severe winters","Minnesota's hail and windstorm activity plus harsh winters push premiums above the national average."),
 "MS":("hurricanes and tornadoes","Mississippi combines Gulf hurricane exposure with frequent tornadoes, keeping premiums well above the national average."),
 "MO":("tornadoes and hail","Missouri's position in the lower Midwest brings frequent tornadoes and hail, pushing rates above the national average."),
 "MT":("wildfire and hail","Montana faces wildfire and hail exposure, with premiums near the national average despite a low population."),
 "NE":("tornadoes and hail","Nebraska's severe-storm and hail exposure makes it one of the more expensive home insurance states in the country."),
 "NV":("low catastrophe exposure (wildfire in the west)","Nevada keeps premiums well below the national average thanks to its dry, low-catastrophe climate; wildfire is the main risk in western foothill ZIPs."),
 "NH":("winter storms","New Hampshire has some of the lowest home premiums in the nation; winter storms and ice are the primary rate drivers."),
 "NJ":("coastal storms and Nor'easters","New Jersey stays below the national average; shore-area wind and winter Nor'easters are the main considerations."),
 "NM":("wildfire and hail","New Mexico's premiums sit near the national average, with wildfire and hail the main drivers in higher-risk areas."),
 "NY":("winter storms and coastal wind","New York's average is held down by upstate; downstate and Long Island carry higher coastal-wind and rebuilding-cost driven rates."),
 "NC":("hurricanes and coastal wind","North Carolina's coastal hurricane exposure drives a separate wind pool and higher coastal premiums, with the statewide average modestly above national."),
 "ND":("hail, wind and severe winters","North Dakota faces hail, windstorms, and hard winters, keeping premiums near the national average."),
 "OH":("tornadoes and hail","Ohio sits below the national average; spring tornadoes and hail are the primary storm-related rate drivers."),
 "OK":("tornadoes and hail (Tornado Alley)","Oklahoma is one of the most expensive home insurance states in the nation — it sits in Tornado Alley with extreme tornado and hail frequency."),
 "OR":("wildfire","Oregon enjoys low premiums overall; wildfire in the wildland-urban interface is the fastest-growing rate driver."),
 "PA":("winter storms and flooding","Pennsylvania stays below the national average, with winter weather and localized flooding the main considerations."),
 "RI":("coastal wind and Nor'easters","Rhode Island's coastal wind exposure and Nor'easters keep premiums near the national average for such a small state."),
 "SC":("hurricanes and coastal wind","South Carolina's Atlantic hurricane exposure drives higher coastal premiums, with the statewide average near national."),
 "SD":("hail, wind and tornadoes","South Dakota's hail and severe-storm exposure keeps premiums near the national average."),
 "TN":("tornadoes, wind and hail","Tennessee faces frequent tornadoes, straight-line wind, and hail, pushing premiums above the national average."),
 "TX":("hurricanes, tornadoes and hail","Texas is one of the most expensive home insurance states — Gulf hurricanes on the coast plus tornadoes and severe hail inland combine to drive premiums far above national."),
 "UT":("wildfire and earthquake exposure","Utah has some of the lowest premiums nationally; wildfire and Wasatch Front earthquake risk (earthquake is separate) are the main considerations."),
 "VT":("winter storms","Vermont has among the lowest home premiums in the nation, with winter storms and ice the primary rate drivers."),
 "VA":("hurricanes and coastal wind","Virginia stays below the national average; coastal Tidewater wind and inland storms are the main drivers."),
 "WA":("wildfire and windstorms","Washington keeps premiums low; west-side windstorms and east-side wildfire are the main regional rate drivers."),
 "WV":("flooding and winter weather","West Virginia sits below the national average, with flooding and winter storms the primary considerations."),
 "WI":("hail, wind and winter","Wisconsin has some of the lowest home premiums in the country; hail, wind, and hard winters are the main rate drivers."),
 "WY":("hail and wind","Wyoming's premiums sit near the national average, with hail and high winds the primary drivers."),
}

def slugify(name):
    return name.lower().replace(".", "").replace(" ", "-")

def tier(avg):
    r = avg / NATIONAL
    if r < 0.78:   return ("among the lowest in the country", "Low Cost", "well below the national average")
    if r < 0.92:   return ("below the national average", "Below Avg", "below the national average")
    if r <= 1.10:  return ("near the national average", "Near Avg", "near the national average")
    if r <= 1.45:  return ("above the national average", "Above Avg", "above the national average")
    return ("among the highest in the country", "High Cost", "well above the national average")

def rank(code):
    avg = STATES[code][1]
    tilt = STATE_CARRIER_ADJ.get(code, {})
    drift = HOME_DRIFT.get(code, {})
    avail = [(n, round(avg*b*tilt.get(n, 1)*drift.get(n, 1))) for (n,b,st) in CARRIERS if (st is None or code in st)]
    avail.sort(key=lambda x: x[1])
    top = avail[:10]
    prices = sorted(p for _,p in top)
    m = len(prices)//2
    median = prices[m] if len(prices)%2 else round((prices[m-1]+prices[m])/2)
    return avg, top, median

def ranking_block(code, name):
    avg, top, median = rank(code)
    rows = ""
    for i,(n,p) in enumerate(top):
        d = p - median
        vs = (f'<span style="color:{GREEN};font-weight:600;">Save ${abs(d):,}</span>' if d <= 0
              else f'<span style="color:{RED};font-weight:600;">+${d:,}</span>')
        rows += (f'<tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;color:var(--ink-mute);">{i+1}</td>'
                 f'<td style="padding:8px 6px;"><strong>{n}</strong></td>'
                 f'<td style="padding:8px 6px;">${p:,}/yr</td><td style="padding:8px 6px;">{vs}</td></tr>')
    cheapest = [n for n,_ in top[:3]]
    return (avg, median, cheapest,
        f'''<!-- state-rankings-start -->
<h2>Cheapest homeowners insurance carriers in {name}</h2>
<p>Estimated annual premiums for a standard policy (~$300k dwelling, $1,000 deductible), ranked cheapest first &mdash; {name} averages about <strong>${avg:,}/yr</strong> (median of the carriers below: ${median:,}/yr). Enter ZIP for a ranking tuned to your dwelling amount, deductible, and coverage.</p>
<table style="width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:660px;">
<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;"><th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">Carrier</th><th style="padding:8px 6px;">Est. annual</th><th style="padding:8px 6px;">vs median</th></tr></thead>
<tbody>{rows}</tbody></table>
<form onsubmit="event.preventDefault();var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);if(/^\\d{{5}}$/.test(z)){{location.href='/home/?zip='+z}}else{{this.zc.focus()}}" style="display:flex;gap:0;max-width:360px;margin:16px 0;">
<input name="zc" type="text" inputmode="numeric" maxlength="5" placeholder="Enter ZIP" aria-label="ZIP code" style="flex:1;min-width:0;font-family:var(--mono);font-size:16px;letter-spacing:0.12em;padding:12px 14px;border:2px solid var(--ink);border-right:none;background:var(--paper);color:var(--ink);outline:none;" />
<button type="submit" style="font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:0 20px;border:2px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;">See rates &rarr;</button>
</form>
<p style="font-size:13px;color:var(--ink-mute);max-width:660px;">Directional estimates from public rate filings and NAIC data &mdash; not a quote. Your actual rate depends on dwelling amount, deductible, roof age, claims history, and ZIP.</p>
<!-- state-rankings-end -->''')

# ── Extract reusable scaffold from a renters state page ──
scaff = open("renters/state/colorado.html", encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>")+len("</style>")]
NAV   = scaff[scaff.index('<header class="top">'):scaff.index("</header>")+len("</header>")]
TAIL  = scaff[scaff.index("<footer>"):]
TAIL  = TAIL.replace("/renters/index.html?zip=", "/home/index.html?zip=")
TAIL  = TAIL.replace('window.location.href="/renters/"', 'window.location.href="/home/"')

CARRIER_OPTS = "".join(f"<option>{n}</option>" for n in
    ["USAA","Amica","Auto-Owners","Erie","Travelers","American Family","Nationwide",
     "State Farm","Progressive","Farmers","Allstate","Liberty Mutual","Other"])

def esc(s): return s.replace('"', "&quot;")

def build(code):
    name, avg = STATES[code]
    slug = slugify(name)
    monthly = round(avg/12)
    tnote, pill, tphrase = tier(avg)
    peril, peril_detail = RISK[code]
    a2, median, cheapest = rank(code)[0], rank(code)[2], None
    _avg, median, cheapest, rblock = ranking_block(code, name)
    c1, c2, c3 = cheapest[0], cheapest[1], cheapest[2]
    url = f"https://boringrate.com/home/state/{slug}.html"
    desc = f"The cheapest homeowners insurance in {name} comes from {c1}, {c2} and {c3}. The state average is ${avg:,}/year — {tphrase}. Compare the cheapest carriers for your ZIP."

    faq = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":f"What is the average cost of homeowners insurance in {name}?",
         "acceptedAnswer":{"@type":"Answer","text":f"The average cost of homeowners insurance in {name} is ${avg:,} per year, or about ${monthly:,} per month, for a standard policy with roughly $300,000 in dwelling coverage and a $1,000 deductible. That is {tphrase} of about ${NATIONAL:,}. Rates vary widely by ZIP, dwelling amount, roof age, and claims history — comparing at least three carriers is the best way to find your lowest rate."}},
        {"@type":"Question","name":f"What is the cheapest homeowners insurance in {name}?",
         "acceptedAnswer":{"@type":"Answer","text":f"{c1}, {c2}, and {c3} are consistently among the cheapest homeowners insurance options in {name} for a standard policy. Pricing varies by your dwelling amount, deductible, and ZIP — enter your ZIP to compare current carrier rankings for your area."}},
        {"@type":"Question","name":f"Why is homeowners insurance {('expensive' if avg>NATIONAL else 'priced the way it is')} in {name}?",
         "acceptedAnswer":{"@type":"Answer","text":f"{name} home insurance rates are driven largely by {peril}. {peril_detail} Your individual rate also depends on your home's age, roof, construction, and claims history."}},
        {"@type":"Question","name":f"Is homeowners insurance required in {name}?",
         "acceptedAnswer":{"@type":"Answer","text":f"No state law in {name} requires homeowners insurance. However, if you have a mortgage your lender will require it, and most homeowners carry it regardless because it protects the largest asset most people own. Standard policies exclude flood and earthquake, which require separate coverage."}},
    ]})
    crumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"BoringRate","item":"https://boringrate.com"},
        {"@type":"ListItem","position":2,"name":"Home Insurance","item":"https://boringrate.com/home/index.html"},
        {"@type":"ListItem","position":3,"name":f"{name} Homeowners Insurance Rates (2026)","item":url},
    ]})
    art = json.dumps({"@context":"https://schema.org","@type":"Article",
        "headline":f"Cheapest Homeowners Insurance in {name} (2026)","description":desc,
        "publisher":{"@type":"Organization","name":"BoringRate","url":"https://boringrate.com"},
        "dateModified":"2026-06-15","mainEntityOfPage":url})

    head = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Cheapest Homeowners Insurance in {name} (2026) — BoringRate</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
<meta property="og:title" content="Cheapest Homeowners Insurance in {name} (2026)" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Cheapest Homeowners Insurance in {name} (2026)" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image" content="https://boringrate.com/og-default.png" />
<script type="application/ld+json">
{faq}
</script>
<script type="application/ld+json">
{crumb}
</script>
<script type="application/ld+json">
{art}
</script>
</head>
<body>'''

    zipbar = f'''<div class="zip-bar">
  <div class="wrap">
    <div class="zip-bar-inner">
      <div class="zip-bar-slogan"><strong>Boring Research.</strong> Easy Decision. — Enter ZIP to compare <em>home</em> rates.</div>
      <form class="zip-bar-form" id="zipBarForm" autocomplete="off">
        <input class="zip-bar-input" id="zipBarInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />
        <button type="submit" class="zip-bar-btn">Compare →</button>
      </form>
    </div>
  </div>
</div>'''

    article = f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/home/index.html">Home Insurance</a> &nbsp;·&nbsp; {name} &nbsp;·&nbsp; 3 min read</div>
    <div class="stat-pill">{code} · {pill}</div>
    <h1 class="article-title">The cheapest homeowners insurance in {name} (2026).</h1>
    <p class="article-dek">{name} homeowners pay an average of ${avg:,}/year (${monthly:,}/month) — {tphrase}. Rates here are shaped largely by {peril}.</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; June 2026</div>
  </div>
  <div class="article-body">
{rblock}
    <div class="tldr-card">
      <div class="tldr-label">TLDR</div>
      <ul class="tldr-list">
        <li>{name} averages ${avg:,}/year (${monthly:,}/month) for homeowners insurance — {tphrase}</li>
        <li>Rates here are driven largely by {peril} — your home's age, roof, and claims history matter too</li>
        <li>{c1}, {c2}, and {c3} are typically the most competitive; compare at least 3 carriers when shopping</li>
        <li>Not required by state law, but your mortgage lender will require it — and it protects your largest asset</li>
        <li>Standard policies exclude flood and earthquake; buy those separately if you're exposed</li>
      </ul>
    </div>

    <h2>What is the average cost of homeowners insurance in {name}?</h2>
    <p>The average cost of homeowners insurance in {name} is <strong>${avg:,} per year</strong> — about ${monthly:,}/month — for a standard policy with roughly $300,000 in dwelling coverage and a $1,000 deductible. That puts {name} {tphrase} of about ${NATIONAL:,}. The single biggest factor behind {name}'s rates is {peril}. {peril_detail} The spread between the cheapest and most expensive carrier for the same home is often $600–1,500/year, so shopping at renewal genuinely pays off.</p>
    <p>Carrier selection matters more than most homeowners assume. {c1}, {c2}, and {c3} tend to price most competitively in {name}, but the right answer depends on your dwelling amount, roof age, and whether you bundle auto. Entering your ZIP takes about two minutes and reveals current carrier pricing for your specific location.</p>

    <h2>Cheapest homeowners insurance companies in {name}</h2>
    <p>{c1}, {c2}, and {c3} are consistently among the most competitive options for homeowners insurance in {name}. Bundling your auto policy is usually the single largest discount available — often 10–20% — followed by raising your deductible and adding modern roof, security, or smart-home credits. Comparing all three at renewal takes about 10 minutes and typically reveals a several-hundred-dollar spread for the same coverage.</p>
    <p>One thing many homeowners underestimate: under-insuring the dwelling to save on premium is a costly mistake. Coverage A should reflect your home's <strong>rebuild cost</strong>, not its market value — and many policies pro-rate even partial claims if you insure for less than 80% of rebuild cost. Use the <a href="/home/coverage.html">home coverage calculator</a> to get the levels right before you shop.</p>

    <h2>What drives homeowners insurance rates in {name}?</h2>
    <p>{name}'s premiums are shaped primarily by {peril}. {peril_detail} On top of regional risk, insurers price your individual home on its age, roof type and age, construction, distance to a fire station, prior claims, and increasingly your insurance-based credit score. Two homes on the same street can pay very different rates based on roof age alone.</p>

    <h2>Is homeowners insurance required in {name}?</h2>
    <p>No state law in {name} requires homeowners insurance. However, if you carry a mortgage, your lender will require it as a condition of the loan and can force-place a (usually more expensive) policy if you let coverage lapse. Even without a mortgage, most owners carry it — a home is the largest asset most people own, and a total loss without coverage is financially catastrophic.</p>
    <p>Remember that a standard policy <strong>excludes flood and earthquake</strong>. In {name}, if you're in a flood-prone area you'll need a separate NFIP or private flood policy; earthquake is a separate policy or endorsement. The base policy alone can leave you exposed on the very loss most likely to total your home.</p>

    <div class="callout"><p><strong>{name} homeowners insurance average:</strong> ${avg:,}/year (${monthly:,}/month). Rates here run {tphrase} and are driven mostly by {peril}. Bundling auto and getting your dwelling amount right are the two biggest levers on your premium.</p></div>

    <div class="zip-embed">
      <div class="zip-embed-label">Compare homeowners insurance in {name}</div>
      <h3>Find the cheapest rate <em>in your part of {name}.</em></h3>
      <div class="zip-embed-sub">Enter ZIP — see carrier rankings for your area in seconds.<br>No phone. No spam. No selling your information.</div>
      <form class="zip-embed-form" id="embedZipForm" autocomplete="off">
        <input class="zip-embed-input" id="embedZipInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />
        <button type="submit" class="zip-embed-btn">Compare →</button>
      </form>
    </div>

    <h2>Frequently asked questions</h2>
    <div class="callout"><p><strong>What is the average cost of homeowners insurance in {name}?</strong><br>The average is ${avg:,}/year (about ${monthly:,}/month) for ~$300k dwelling coverage with a $1,000 deductible — {tphrase} of ${NATIONAL:,}. Rates vary by ZIP, dwelling amount, roof age, and claims history.</p></div>
    <div class="callout"><p><strong>What is the cheapest homeowners insurance in {name}?</strong><br>{c1}, {c2}, and {c3} are consistently among the cheapest in {name}. Enter ZIP to compare current carrier rankings for your area.</p></div>
    <div class="callout"><p><strong>What drives {name} home insurance rates?</strong><br>Mainly {peril}. {peril_detail}</p></div>
    <div class="callout"><p><strong>Is homeowners insurance required in {name}?</strong><br>Not by state law, but mortgage lenders require it. Standard policies exclude flood and earthquake — buy those separately if you're exposed.</p></div>

    <div class="article-email">
      <strong>Get a Boring Reminder when {name} rates move.</strong>
      <div class="sub">We&#39;ll notify you when homeowners insurance rates change in your area. No spam, no calls, no selling your information.</div>
      <div class="email-row" id="articleEmailForm">
        <input class="email-input" id="articleEmailInput" type="email" placeholder="your@email.com" aria-label="Email address" />
        <input class="email-input email-zip" id="articleEmailZip" type="text" inputmode="numeric" placeholder="ZIP code" maxlength="5" aria-label="ZIP code" />
        <select class="email-select" id="articleEmailCarrier" aria-label="Current carrier (optional)">
          <option value="">Current carrier (optional)</option>
          {CARRIER_OPTS}
        </select>
        <select class="email-select email-month" id="articleEmailMonth" aria-label="Renewal month (optional)">
          <option value="">Renewal month (optional)</option>
          <option>January</option><option>February</option><option>March</option>
          <option>April</option><option>May</option><option>June</option>
          <option>July</option><option>August</option><option>September</option>
          <option>October</option><option>November</option><option>December</option>
        </select>
        <button type="button" class="email-btn" id="articleEmailBtn">Notify me</button>
      </div>
      <div class="email-thanks" id="articleEmailThanks">✓ You&#39;re on the list.</div>
    </div>
  </div>
</div>'''

    tail = TAIL.replace("Compare Colorado renters rates", f"Compare {name} home rates")
    return head + "\n" + NAV + "\n" + zipbar + "\n" + article + "\n" + tail

os.makedirs("home/state", exist_ok=True)
n = 0
for code in STATES:
    slug = slugify(STATES[code][0])
    open(f"home/state/{slug}.html", "w", encoding="utf-8").write(ensure(build(code)))
    n += 1
print("wrote", n, "home state pages")
