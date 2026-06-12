#!/usr/bin/env python3
"""Generate a metro auto-insurance page from the existing metro template.

Model (see memory boringrate-metro-model): metro avg = state avg * metro offset.
Goal is DIRECTIONAL accuracy — honest, state-DOI-anchored, not a quote. Content is
templated but truthful; no invented metro-specific narrative beyond the model.

Usage: import build_page(cfg) or run the __main__ pilot. Writes article/metro/<slug>.html.
Idempotent-ish: overwrites the target file.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
TEMPLATE = ROOT / "article" / "metro" / "atlanta.html"
NATIONAL_AVG = 2400  # baseline implied by existing pages (Atlanta $3,600 = +50%)

# state code -> (display name, slug, state avg). Mirrors STATE_DATA in index.html.
_ST = {'AL':('Alabama',2468),'AK':('Alaska',2314),'AZ':('Arizona',2578),'AR':('Arkansas',2362),
'CA':('California',3668),'CO':('Colorado',1706),'CT':('Connecticut',3124),'DC':('Washington D.C.',3486),
'DE':('Delaware',3218),'FL':('Florida',4848),'GA':('Georgia',3224),'HI':('Hawaii',1446),'ID':('Idaho',1654),
'IL':('Illinois',2194),'IN':('Indiana',1842),'IA':('Iowa',1586),'KS':('Kansas',2124),'KY':('Kentucky',2756),
'LA':('Louisiana',4612),'ME':('Maine',1468),'MD':('Maryland',2986),'MA':('Massachusetts',2842),
'MI':('Michigan',4724),'MN':('Minnesota',2214),'MS':('Mississippi',2438),'MO':('Missouri',2648),
'MT':('Montana',2268),'NE':('Nebraska',2012),'NV':('Nevada',3842),'NH':('New Hampshire',1624),
'NJ':('New Jersey',3486),'NM':('New Mexico',2314),'NY':('New York',3484),'NC':('North Carolina',1842),
'ND':('North Dakota',1748),'OH':('Ohio',1724),'OK':('Oklahoma',2648),'OR':('Oregon',1986),
'PA':('Pennsylvania',2468),'RI':('Rhode Island',3124),'SC':('South Carolina',2586),'SD':('South Dakota',1986),
'TN':('Tennessee',2124),'TX':('Texas',3136),'UT':('Utah',2468),'VT':('Vermont',1524),'VA':('Virginia',1924),
'WA':('Washington',2312),'WV':('West Virginia',2124),'WI':('Wisconsin',1724),'WY':('Wyoming',1986)}
def _slug(n): return n.lower().replace('.', '').replace(' ', '-')
STATE = {k: (v[0], _slug(v[0]), v[1]) for k, v in _ST.items()}


def pct_phrase(metro_avg):
    p = round((metro_avg / NATIONAL_AVG - 1) * 100)
    if p >= 8:   word = f"+{p}% above"
    elif p <= -8: word = f"{abs(p)}% below"
    else:        word = "about even with"
    pill = (f"+{p}%" if p > 0 else f"{p}%") if abs(p) >= 2 else "≈ avg"
    return p, word, pill


def esc(s):
    return s.replace("&", "&amp;")


def build_page(cfg):
    """cfg: slug, name (e.g. 'Colorado Springs'), state (code). Optional: offset."""
    slug = cfg["slug"]
    metro = cfg["name"]
    st_name, st_slug, st_avg = STATE[cfg["state"]]
    offset = cfg.get("offset", 1.0)
    avg = int(round(st_avg * offset / 10) * 10)  # round to $10
    p, word, pill = pct_phrase(avg)
    url = f"https://boringrate.com/article/metro/{slug}.html"
    title = f"{metro} Car Insurance Rates (2026) — Average Cost & Cheapest Carriers"
    desc = (f"{metro} averages ~${avg:,}/yr for auto insurance — {word} the national norm. "
            f"Carrier pricing varies widely. Compare rates in your ZIP.")

    html = TEMPLATE.read_text(encoding="utf-8")

    # ---- head: canonical, og:url, title, descriptions, social titles ----
    html = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf'\g<1>{url}\g<2>', html)
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{url}\g<2>', html)
    html = re.sub(r'<title>[^<]*</title>', f'<title>{esc(title)}</title>', html)
    html = re.sub(r'(<meta name="description" content=")[^"]*(")', rf'\g<1>{esc(desc)}\g<2>', html)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                  rf'\g<1>{esc(metro)} Car Insurance Rates (2026)\g<2>', html)
    html = re.sub(r'(<meta property="og:description" content=")[^"]*(")', rf'\g<1>{esc(desc)}\g<2>', html)
    html = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
                  rf'\g<1>{esc(metro)} Car Insurance Rates (2026)\g<2>', html)
    html = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', rf'\g<1>{esc(desc)}\g<2>', html)

    # ---- JSON-LD: rebuild Breadcrumb + FAQ (replace both blocks up to </head>) ----
    faq = [
        (f"What is the cheapest car insurance in {metro}?",
         f"For drivers with clean records in {st_name}, GEICO, State Farm, and USAA (military and veterans) "
         f"are frequently the most competitive; Progressive often prices best for drivers with incidents. "
         f"The cheapest carrier varies by ZIP — enter yours to see current rankings."),
        (f"Why is car insurance priced the way it is in {metro}?",
         f"{metro} runs {word} the national average at roughly ${avg:,}/year. Traffic density, repair-labor "
         f"costs, theft and claims frequency are the main drivers; rural parts of {st_name} typically price lower."),
        (f"How much can drivers save by shopping in {metro}?",
         f"Because the same driver can see a 30–50% spread between carriers, comparing at every renewal commonly "
         f"saves hundreds of dollars a year — the single highest-ROI move most drivers can make."),
    ]
    faq_items = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (_json(q), _json(a)) for q, a in faq)
    jsonld = (
        '<script type="application/ld+json">\n'
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        '{"@type":"ListItem","position":1,"name":"Home","item":"https://boringrate.com/"},'
        f'{{"@type":"ListItem","position":2,"name":{_json(metro + " Car Insurance Rates")},"item":{_json(url)}}}]}}\n'
        '</script>\n'
        '<script type="application/ld+json">\n'
        '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[' + faq_items + ']}\n'
        '</script>'
    )
    # Replace the run of consecutive JSON-LD blocks in <head> (a <style> sits between
    # them and </head>, so anchor on the blocks themselves, not on </head>).
    html = re.sub(r'(?:<script type="application/ld\+json">.*?</script>\s*)+', jsonld + "\n",
                  html, count=1, flags=re.DOTALL)

    # ---- article-header ----
    header = (
        '<div class="article-header">\n'
        f'    <div class="article-kicker"><a href="../../index.html#guides">Metro Report</a> &nbsp;&middot;&nbsp; {esc(metro)} &nbsp;&middot;&nbsp; 3 min read</div>\n'
        f'    <div class="stat-pill">{esc(metro)} &middot; {pill}</div>\n'
        f'    <h1 class="article-title">{esc(metro)} auto insurance rates in 2026 &mdash; what drivers here actually pay.</h1>\n'
        f'    <p class="article-dek">{esc(metro)} averages ~${avg:,}/year for full coverage, {word} the national average. Here&rsquo;s what&rsquo;s driving costs and which carriers compete hardest in this market.</p>\n'
        '    <div class="article-byline">BoringRate Editorial &nbsp;&middot;&nbsp; June 2026</div>\n'
        '  </div>\n  <div class="article-body">'
    )
    html = re.sub(r'<div class="article-header">.*?</div>\s*<div class="article-body">',
                  header, html, count=1, flags=re.DOTALL)

    # ---- article-body (everything up to the article-email block) ----
    body = f'''
<p class="internal-links-state" style="margin-bottom:24px;font-size:16px;color:var(--ink-mute);">Part of our <a href="../../article/state/{st_slug}.html" style="color:var(--accent);text-decoration:none;border-bottom:1px solid var(--rule);">{esc(st_name)} auto insurance report</a> &mdash; statewide rates &amp; carrier rankings.</p>

    <div class="tldr-card">
      <div class="tldr-label">TLDR</div>
      <ul class="tldr-list">
        <li>{esc(metro)} averages ~${avg:,}/year for full coverage &mdash; {word} the national average</li>
        <li>Rate spreads are wide &mdash; the cheapest carrier can run 30&ndash;50% below the priciest for the same driver</li>
        <li><a class="ca-link" href="/article/carrier/geico.html">GEICO</a>, <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, and <a class="ca-link" href="/article/carrier/usaa.html">USAA</a> (military) are usually among the most competitive &mdash; your ZIP sets the order</li>
        <li>{esc(st_name)} minimum liability limits are legal floors that leave gaps for most drivers &mdash; compare full coverage</li>
        <li>Rates re-price constantly &mdash; shopping at renewal is the single highest-ROI move most drivers can make</li>
      </ul>
    </div>
    <p>{esc(metro)} drivers pay roughly <strong>${avg:,}/year</strong> for full coverage &mdash; {word} the national average. Traffic density, repair-labor costs, theft risk, and local claims frequency all feed into metro pricing.</p>
    <p>Within {esc(st_name)}, the {esc(metro)} area prices differently from rural parts of the state. Urban density raises accident and theft probability, and carriers bake that into local rates regardless of an individual driver&rsquo;s record. Your exact ZIP shifts the number further.</p>
    <h2>How to find the cheapest carrier in {esc(metro)}</h2>
    <p>The highest-ROI move a {esc(metro)} driver can make is comparing carriers at every renewal. Pricing models change often, and last year&rsquo;s cheapest option is rarely this year&rsquo;s. The spread between the highest and lowest rate for the same driver profile is commonly 30&ndash;50% in this market &mdash; hundreds of dollars a year on the table.</p>
    <div class="callout"><p><strong>{esc(st_name)} coverage note:</strong> {esc(st_name)} sets minimum liability limits you must carry. Those are legal floors &mdash; full coverage (comprehensive + collision) protects substantially better for most {esc(metro)} drivers.</p></div>
    <div class="zip-embed">
      <div class="zip-embed-label">Compare rates in {esc(metro)}</div>
      <h3>See who&rsquo;s cheapest <em>in your part of {esc(metro)}.</em></h3>
      <div class="zip-embed-sub">Enter your ZIP &mdash; we rank all major carriers for your area in seconds.<br>No phone. No spam. No selling your information.</div>
      <form class="zip-embed-form" id="embedZipForm" autocomplete="off">
        <input class="zip-embed-input" id="embedZipInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />
        <button type="submit" class="zip-embed-btn">Compare &rarr;</button>
      </form>
    </div>
    <h2>Frequently asked questions</h2>
    <div class="callout"><p><strong>What is the cheapest car insurance in {esc(metro)}?</strong><br>For drivers with clean records, <a class="ca-link" href="/article/carrier/geico.html">GEICO</a>, <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, and <a class="ca-link" href="/article/carrier/usaa.html">USAA</a> (military and veterans) are frequently the most competitive in {esc(st_name)}. Enter your ZIP above to see current rankings for your specific location &mdash; rates vary across the state.</p></div>
    <div class="callout"><p><strong>Why is car insurance priced the way it is in {esc(metro)}?</strong><br>{esc(metro)} runs {word} the national average. Urban density, repair costs, theft, and claims frequency are the main factors; rural parts of {esc(st_name)} usually price lower.</p></div>
    <div class="article-email">'''
    html = re.sub(r'<div class="article-body">.*?<div class="article-email">',
                  '<div class="article-body">' + body, html, count=1, flags=re.DOTALL)

    # ---- article-email: swap the city name in the reminder line ----
    html = html.replace("when Atlanta rates move", f"when {metro} rates move")
    # ---- sticky mobile CTA label (carried over from the template) ----
    html = html.replace("Compare Atlanta rates", f"Compare {metro} rates")

    out = ROOT / "article" / "metro" / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return out, avg, p


def _json(s):
    import json
    return json.dumps(s, ensure_ascii=False)


if __name__ == "__main__":
    out, avg, p = build_page({"slug": "colorado-springs", "name": "Colorado Springs",
                              "state": "CO", "offset": 1.02})
    print(f"wrote {out}  (avg ${avg}, {p}% vs national)")
