#!/usr/bin/env python3
"""Generate carrier review pages for the NJ regionals surfaced by the NJ pull (CURE, Palisades,
Plymouth Rock). Clones article/carrier/alfa.html; content grounded in the approved SERFF filings +
accurate positioning — no invented NAIC ratios / founding dates. Idempotent."""
import re, pathlib
ROOT = pathlib.Path(__file__).parent
TMPL = (ROOT / "article" / "carrier" / "alfa.html").read_text(encoding="utf-8")

CARRIERS = [
    {
        "slug": "cure", "name": "CURE", "full": "CURE Auto Insurance", "region": "New Jersey",
        "pill": "CURE &middot; No credit scoring &middot; NJ/PA/MI",
        "title": "CURE Auto Insurance Review 2026 — No-Credit-Scoring Rates (NJ, PA, MI)",
        "meta": "CURE (Citizens United Reciprocal Exchange) is a New Jersey-based auto insurer that doesn't use credit score, education, or occupation to price. It raised NJ auto rates ~6% for 2026, per approved NJ DOBI filings.",
        "jsonld": "CURE (Citizens United Reciprocal Exchange) is a New Jersey-based auto insurer that prices without credit score, education, or occupation, writing in NJ, PA, and MI.",
        "dek": "CURE &mdash; Citizens United Reciprocal Exchange &mdash; is a New Jersey-based auto insurer that <strong>doesn't use credit score, education, or occupation</strong> to set rates. That makes it a genuine value option for drivers those factors penalize. It <strong>raised NJ rates about 6%</strong> for 2026.",
        "tldr": [
            "Prices <strong>without credit score, education, or occupation</strong> &mdash; unusual, and its whole appeal",
            "New Jersey-based reciprocal exchange (member-owned); writes NJ, PA, and Michigan",
            "<strong>Raised NJ auto rates ~6%</strong> for 2026 on ~45,600 policyholders (approved NJ DOBI filing)",
            "Best for drivers penalized by thin credit, a non-traditional job, or no college degree",
            "Its low book-average premium reflects a minimum-limits coverage mix &mdash; compare full coverage before assuming it's cheapest",
        ],
        "body": """<p>CURE (Citizens United Reciprocal Exchange) is built around one idea: your <strong>credit, education, and occupation shouldn't set your car-insurance price</strong>. Most insurers lean heavily on credit-based insurance scores; CURE doesn't use them at all. For a driver with a clean record but thin credit, a blue-collar job, or no college degree &mdash; the profiles those factors quietly surcharge &mdash; CURE can be dramatically cheaper than a national carrier.</p>
<p>It's a <strong>reciprocal exchange</strong> (member-owned rather than shareholder-owned), based in New Jersey and writing in NJ, Pennsylvania, and Michigan. That focus is a feature: CURE knows its three markets deeply, but it isn't an option outside them.</p>
<h2>What the filings show</h2>
<p>New Jersey regulators approved a CURE rate <strong>increase of about 6%</strong> for 2026, across roughly 45,600 policyholders. That runs with New Jersey's broader 2026 pattern &mdash; most mid-size NJ auto writers raised, while the two giants (NJM and State Farm) held flat and GEICO cut. A CURE increase doesn't undo its structural advantage for credit-penalized drivers, but it does make comparing worthwhile.</p>
<h2>Who CURE is right for</h2>
<p>CURE is strongest for <strong>good drivers who get penalized for things unrelated to driving</strong> &mdash; a low or thin credit file, a service or trade occupation, or no bachelor's degree. For those drivers it is frequently the cheapest legitimate option in NJ/PA/MI. It's a weaker fit for drivers with excellent credit and a white-collar profile, who often do better at a credit-using national carrier.</p>
<div class="callout"><p><strong>One caveat on the "cheapest" label:</strong> CURE's low book-average premium partly reflects a minimum-limits coverage mix, not just a cheap full-coverage price. If you need full coverage on a financed car, compare CURE against the national carriers for your exact profile &mdash; don't assume the headline is your number.</p></div>""",
        "states": [("new-jersey", "New Jersey"), ("pennsylvania", "Pennsylvania"), ("michigan", "Michigan")],
        "metros": [("new-jersey", "New Jersey"), ("philadelphia", "Philadelphia"), ("detroit", "Detroit")],
    },
    {
        "slug": "palisades", "name": "Palisades", "full": "Palisades Insurance", "region": "New Jersey",
        "pill": "Palisades &middot; A Plymouth Rock company &middot; NJ",
        "title": "Palisades Insurance Review 2026 — New Jersey Auto & Home Rates",
        "meta": "Palisades is a New Jersey auto and home insurer, part of the Plymouth Rock Assurance group. It cut NJ auto rates ~5% and raised home ~7.5% for 2026, per approved NJ DOBI filings.",
        "jsonld": "Palisades Insurance is a New Jersey-focused auto and home insurer in the Plymouth Rock Assurance group.",
        "dek": "Palisades is a <strong>New Jersey-focused auto and home insurer</strong>, part of the Plymouth Rock Assurance group. For 2026 it <strong>cut NJ auto rates about 5%</strong> while <strong>raising home about 7.5%</strong> &mdash; a split worth knowing if you bundle.",
        "tldr": [
            "New Jersey auto &amp; home specialist &mdash; part of the Plymouth Rock Assurance group",
            "<strong>Cut NJ auto rates ~5%</strong> (approved, ~97,700 policyholders) for 2026",
            "<strong>Raised NJ home rates ~7.5%</strong> (approved, ~74,300 policyholders) for 2026",
            "Agent and direct distribution with deep New Jersey local presence",
            "Its auto cut runs against the NJ grain &mdash; most mid-size NJ auto writers raised in 2026",
        ],
        "body": """<p>Palisades is a <strong>New Jersey regional</strong> in the Plymouth Rock Assurance group &mdash; one of the more recognizable local names in a market dominated by NJM and the nationals. It writes both auto and home in New Jersey and competes on local knowledge and service rather than national scale.</p>
<h2>What the filings show</h2>
<p>The 2026 filings tell a split story. On <strong>auto</strong>, New Jersey approved a Palisades rate <strong>cut of about 5%</strong> across ~97,700 policyholders &mdash; notable because most mid-size NJ auto writers <em>raised</em> in 2026 (Selective, Farmers, CURE, Encompass all up ~6&ndash;7%). On <strong>home</strong>, Palisades went the other way with an approved <strong>increase of about 7.5%</strong> on ~74,300 policyholders, in line with New Jersey's broadly rising homeowners market.</p>
<h2>Who Palisades is right for</h2>
<p>Palisades suits <strong>New Jersey drivers and homeowners who want a local carrier</strong> with Plymouth Rock's backing. Its 2026 auto cut makes it worth a quote for NJ drivers specifically &mdash; a carrier cutting while its peers raise is exactly the kind of move that pays to catch at renewal. Bundlers should note the divergence: the auto side is getting cheaper while the home side is getting more expensive, so price each separately rather than assuming the bundle is best.</p>
<div class="callout"><p><strong>Bottom line:</strong> For New Jersey specifically, Palisades is worth including in any 2026 comparison &mdash; it cut auto against a rising market. Compare its auto and home separately, since they moved in opposite directions this year.</p></div>""",
        "states": [("new-jersey", "New Jersey")],
        "metros": [("new-jersey", "New Jersey"), ("new-york-city", "New York City")],
    },
    {
        "slug": "plymouth-rock", "name": "Plymouth Rock", "full": "Plymouth Rock Assurance", "region": "Northeast",
        "pill": "Plymouth Rock &middot; Northeast auto &amp; home",
        "title": "Plymouth Rock Assurance Review 2026 — Northeast Auto & Home Rates",
        "meta": "Plymouth Rock Assurance is a Northeast auto and home insurer (MA, CT, NH, NJ, NY, PA) known for its Door-to-Door claims service. Its NJ home rates rose ~4.5% for 2026.",
        "jsonld": "Plymouth Rock Assurance is a Northeast auto and home insurer writing in Massachusetts, Connecticut, New Hampshire, New Jersey, New York, and Pennsylvania.",
        "dek": "Plymouth Rock Assurance is a <strong>Northeast auto and home insurer</strong> &mdash; Massachusetts, Connecticut, New Hampshire, New Jersey, New York, and Pennsylvania &mdash; known for its Door-to-Door valet claims service. Its NJ home rates rose <strong>about 4.5%</strong> for 2026.",
        "tldr": [
            "Northeast specialist &mdash; MA, CT, NH, NJ, NY, PA (auto &amp; home)",
            "Signature <strong>Door-to-Door</strong> valet claims service (they pick up and return your car)",
            "Writes New Jersey through its Palisades brand; <strong>NJ home +4.5%</strong> for 2026 (approved)",
            "Agent and direct distribution across its Northeast footprint",
            "Strong regional-service reputation; not available outside the Northeast",
        ],
        "body": """<p>Plymouth Rock Assurance is a <strong>Northeast regional</strong> writing auto and home across Massachusetts, Connecticut, New Hampshire, New Jersey, New York, and Pennsylvania. It's best known for <strong>Door-to-Door</strong> claims &mdash; a valet service that picks up your damaged car, leaves you a loaner, and returns it repaired &mdash; the kind of high-touch service a regional can offer that national carriers generally don't.</p>
<p>In New Jersey it operates through its <strong>Palisades</strong> brand, one of the state's recognizable local names.</p>
<h2>What the filings show</h2>
<p>New Jersey approved a Plymouth Rock home rate <strong>increase of about 4.5%</strong> for 2026 &mdash; a moderate move in a New Jersey homeowners market where most carriers raised in the 5&ndash;7% range. On the auto side, its Palisades arm <em>cut</em> NJ rates about 5% (see the <a class="ca-link" href="/article/carrier/palisades.html">Palisades review</a>).</p>
<h2>Who Plymouth Rock is right for</h2>
<p>Plymouth Rock is strongest for <strong>Northeast drivers and homeowners who value claims service</strong> and want a regional alternative to the nationals. The Door-to-Door program is a genuine differentiator if you'd rather not manage a repair yourself. As with any regional, it's only an option inside its footprint &mdash; and rates still vary enough by profile that it's worth comparing against national carriers before committing.</p>
<div class="callout"><p><strong>Bottom line:</strong> A solid Northeast regional with a standout claims experience. In New Jersey, compare Plymouth Rock/Palisades against NJM and the nationals for your ZIP &mdash; the service is a real plus, but confirm the price works for your profile.</p></div>""",
        "states": [("new-jersey", "New Jersey"), ("new-york", "New York"), ("pennsylvania", "Pennsylvania"), ("massachusetts", "Massachusetts"), ("connecticut", "Connecticut")],
        "metros": [("new-jersey", "New Jersey"), ("new-york-city", "New York City"), ("boston", "Boston")],
    },
]

BODY_RE = re.compile(r'(<div class="article-body">\s*<div class="rz-zip">.*?</div>\s*)(<div class="tldr-card">.*?)(\s*<div class="rz-zip">)', re.DOTALL)

def build(cfg):
    h = TMPL
    h = re.sub(r'<title>[^<]*</title>', f"<title>{cfg['title']}</title>", h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+cfg['meta']+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+f"{cfg['full']} Review 2026"+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+cfg['meta']+m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1)+cfg['meta']+m.group(2), h)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1)+f"{cfg['full']} Review 2026"+m.group(2), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1)+f"https://boringrate.com/article/carrier/{cfg['slug']}.html"+m.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1)+f"https://boringrate.com/article/carrier/{cfg['slug']}.html"+m.group(2), h)
    h = h.replace('"description": "Alfa Insurance is a regional Southeast specialist with competitive pricing and strong agent networks in Alabama, Georgia, Mississippi, and surrounding states.",', f'"description": "{cfg["jsonld"]}",')
    h = h.replace('"name": "Alfa",', f'"name": "{cfg["name"]}",')
    h = h.replace('"url": "https://boringrate.com/article/carrier/alfa.html"', f'"url": "https://boringrate.com/article/carrier/{cfg["slug"]}.html"', 1)
    h = h.replace('"headline": "Alfa Insurance Auto Review 2026",', f'"headline": "{cfg["full"]} Review 2026",')
    h = h.replace('Local Carrier Research &nbsp;&middot;&nbsp; Southeast', f'Local Carrier Research &nbsp;&middot;&nbsp; {cfg["region"]}')
    h = re.sub(r'<div class="stat-pill"[^>]*>[^<]*</div>', f'<div class="stat-pill" style="background:#1a4a8a;">{cfg["pill"]}</div>', h, count=1)
    h = re.sub(r'<h1 class="article-title">[^<]*</h1>', f'<h1 class="article-title">{cfg["full"]} Review 2026</h1>', h, count=1)
    h = re.sub(r'<p class="article-dek">.*?</p>', f'<p class="article-dek">{cfg["dek"]}</p>', h, count=1, flags=re.DOTALL)
    h = h.replace('Instantly compare Alfa Insurance to all carriers', f"Instantly compare {cfg['full']} to all carriers")
    h = h.replace('Compare Alfa Insurance rates', f"Compare {cfg['name']} rates")
    tldr = "\n".join(f"    <li>{x}</li>" for x in cfg['tldr'])
    newmid = ('<div class="tldr-card">\n      <div class="tldr-label">TLDR</div>\n      <ul class="tldr-list">\n'
              + tldr + '\n      </ul>\n    </div>\n\n' + cfg['body'] + '\n    ')
    h, n = BODY_RE.subn(lambda m: m.group(1) + newmid + m.group(3), h, count=1)
    if n != 1:
        raise SystemExit(f"body replace failed for {cfg['slug']}")
    st_links = "".join(f'<a href="../../article/state/{s}.html">{name} →</a>' for s, name in cfg['states'])
    mt_links = "".join(f'<a href="../../article/metro/{s}.html">{name} →</a>' for s, name in cfg['metros'])
    h = re.sub(r'<div class="internal-links internal-links-state">.*?</div>', f'<div class="internal-links internal-links-state">{st_links}</div>', h, count=1, flags=re.DOTALL)
    h = re.sub(r'<div class="internal-links internal-links-metro">.*?</div>', f'<div class="internal-links internal-links-metro">{mt_links}</div>', h, count=1, flags=re.DOTALL)
    h = h.replace('Compare Alfa Insurance Auto Review 2026 rates by state', f"Compare {cfg['full']} rates by state")
    h = h.replace('Compare Alfa Insurance rates by metro', f"Compare {cfg['full']} rates by metro")
    out = ROOT / "article" / "carrier" / f"{cfg['slug']}.html"
    out.write_text(h, encoding="utf-8")
    return out

for c in CARRIERS:
    print("wrote", build(c))
