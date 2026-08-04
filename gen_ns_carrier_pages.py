#!/usr/bin/env python3
"""Generate carrier review pages for the LA non-standard writers surfaced by the LA auto pull
(Safeway, Imperial, Old American). Clones article/carrier/alfa.html (already has the CTA template,
analytics, nav) and swaps carrier-specific content. Content is grounded in the FACTUAL approved
SERFF filings (from serff_filings.json) + accurate non-standard positioning — no invented NAIC
ratios / founding dates. Re-run is idempotent (overwrites the 3 pages)."""
import re, pathlib
ROOT = pathlib.Path(__file__).parent
TMPL = (ROOT / "article" / "carrier" / "alfa.html").read_text(encoding="utf-8")

CARRIERS = [
    {
        "slug": "safeway", "name": "Safeway", "full": "Safeway Insurance",
        "pill": "Safeway &middot; Louisiana non-standard",
        "title": "Safeway Insurance Louisiana Auto Review 2026 — Rates & Non-Standard Coverage",
        "meta": "Safeway Insurance is a value non-standard auto insurer with one of Louisiana's larger high-risk books. It cut Louisiana auto rates ~5.8% for 2026 after a +3.1% 2024 increase, per approved LA DOI filings.",
        "jsonld": "Safeway Insurance is a value/non-standard auto insurer concentrated in Louisiana and nearby Southern states, built for minimum-coverage and higher-risk drivers.",
        "dek": "Safeway Insurance is a value-focused, non-standard auto insurer with one of Louisiana's larger high-risk books — built for drivers who need affordable liability coverage, including those with SR-22 requirements, coverage lapses, or thin records. It <strong>cut Louisiana rates about 5.8%</strong> for 2026.",
        "tldr": [
            "Non-standard / value auto insurer &mdash; concentrated in Louisiana and nearby Southern states",
            "One of Louisiana's larger high-risk books (~31,000 policyholders on its 2024 filing)",
            "<strong>Cut Louisiana auto rates ~5.8%</strong> for 2026 &mdash; after a +3.1% increase the prior year (approved LA DOI filings)",
            "Agent-based; strongest for minimum-coverage and higher-risk Louisiana drivers",
            "Limited coverage menu &mdash; compare a standard carrier if you need full coverage or higher limits",
        ],
        "body": """<p>Safeway Insurance is a <strong>non-standard auto insurer</strong> &mdash; the market segment built for drivers a standard carrier won't write at its best rate: SR-22 filings, prior lapses, tickets or accidents, or simply a preference for the lowest-cost path to legal coverage. It writes primarily in Louisiana and neighboring Southern states through local agents, and Louisiana is one of its larger markets.</p>
<p>In the most expensive auto-insurance market in the country, Safeway's role is straightforward: affordable state-minimum and basic liability coverage for drivers who would pay far more &mdash; or be declined outright &mdash; at a standard carrier. That focus is exactly why its book-average premium reads low; it reflects a minimum-limits coverage mix, not a cheap full-coverage price. For a driver who needs full coverage on a financed vehicle, a standard carrier is usually the better comparison.</p>
<h2>What the filings show</h2>
<p>Louisiana regulators approved a Safeway rate <strong>decrease of about 5.8%</strong> for its 2026 book, effective December 2025 &mdash; a reversal from the <strong>+3.1%</strong> increase approved the prior year. That trajectory tracks the broader 2026 Louisiana pattern: after years of steep increases, most of the state's larger auto books are now cutting as legal-reform effects and moderating loss trends work through. Safeway's cut is smaller than the double-digit reductions from Louisiana Farm Bureau, but it moves in the same direction.</p>
<h2>Who Safeway is right for</h2>
<p>Safeway is strongest for <strong>Louisiana drivers who need low-cost liability coverage</strong> &mdash; those carrying state minimums, rebuilding after a lapse, or filing an SR-22. Its agent network and long Louisiana presence mean it can often quote and bind quickly for profiles that national direct carriers decline. It is not built for drivers who want rich coverage, high limits, or extensive add-ons; those buyers should compare standard carriers first.</p>
<div class="callout"><p><strong>Bottom line:</strong> For high-risk and minimum-coverage Louisiana drivers, Safeway is a real option worth quoting &mdash; and it's cutting rates for 2026. But its low headline premium reflects thin coverage, not a bargain on full coverage. Run your ZIP against both Safeway and the standard carriers before deciding.</p></div>""",
    },
    {
        "slug": "imperial", "name": "Imperial", "full": "Imperial Fire & Casualty",
        "pill": "Imperial F&amp;C &middot; Louisiana non-standard",
        "title": "Imperial Fire & Casualty Louisiana Auto Review 2026 — Non-Standard Rates",
        "meta": "Imperial Fire & Casualty is a non-standard Louisiana auto insurer for high-risk and minimum-coverage drivers. It cut Louisiana rates ~2.9% for 2026 on a ~33,000-policyholder book, per approved LA DOI filings.",
        "jsonld": "Imperial Fire & Casualty is a non-standard auto insurer focused on high-risk and minimum-coverage drivers in Louisiana.",
        "dek": "Imperial Fire &amp; Casualty is a <strong>non-standard Louisiana auto insurer</strong> — built for higher-risk and minimum-coverage drivers who don't fit a standard carrier's best rate. It <strong>cut Louisiana rates about 2.9%</strong> for 2026 on one of the state's larger non-standard books.",
        "tldr": [
            "Non-standard auto insurer &mdash; higher-risk and minimum-coverage Louisiana drivers",
            "One of Louisiana's larger non-standard books (~33,000 policyholders)",
            "<strong>Cut Louisiana auto rates ~2.9%</strong> for 2026 (approved LA DOI filing)",
            "Agent-based; SR-22, lapses, and thin records are its core market",
            "Limited coverage menu &mdash; compare a standard carrier for full coverage or higher limits",
        ],
        "body": """<p>Imperial Fire &amp; Casualty is a <strong>non-standard auto insurer</strong> operating in Louisiana &mdash; the segment that writes drivers standard carriers decline or surcharge heavily: SR-22 filings, prior lapses, accidents or violations, and buyers who simply want the cheapest legal coverage. It works through local agents and carries one of the larger non-standard books in the state.</p>
<p>As with any non-standard carrier, Imperial's low book-average premium reflects a <strong>minimum-limits coverage mix</strong>, not a cheap full-coverage price. Its value is speed and acceptance for hard-to-place profiles, not rich coverage. A driver who needs full coverage on a financed car will usually do better comparing standard carriers.</p>
<h2>What the filings show</h2>
<p>Louisiana approved an Imperial rate <strong>decrease of about 2.9%</strong> for its 2026 book. That places Imperial with the majority of Louisiana's larger auto writers now cutting rates in 2026 &mdash; a notable turn after several years of increases across the state's high-cost market.</p>
<h2>Who Imperial is right for</h2>
<p>Imperial suits <strong>Louisiana drivers who need to file an SR-22, are rebuilding after a lapse, or want low-cost state-minimum coverage</strong> and have been declined or heavily surcharged elsewhere. It is not the right carrier for drivers seeking high limits or comprehensive add-ons &mdash; those buyers should start with standard carriers and use Imperial only if they can't place the risk.</p>
<div class="callout"><p><strong>Bottom line:</strong> Imperial is a non-standard option worth quoting if you're a high-risk or minimum-coverage Louisiana driver, and it's cutting rates for 2026. Treat its low premium as thin coverage, not a bargain &mdash; compare against standard carriers for your ZIP before deciding.</p></div>""",
    },
    {
        "slug": "old-american", "name": "Old American", "full": "Old American Indemnity",
        "pill": "Old American &middot; Louisiana non-standard",
        "title": "Old American Indemnity Louisiana Auto Review 2026 — Non-Standard Rates",
        "meta": "Old American Indemnity is a non-standard Louisiana auto insurer for high-risk and minimum-coverage drivers. Its Louisiana rates were about flat (+0.7%) for 2026 per approved LA DOI filings.",
        "jsonld": "Old American Indemnity is a non-standard auto insurer serving high-risk and minimum-coverage drivers in Louisiana.",
        "dek": "Old American Indemnity is a <strong>non-standard Louisiana auto insurer</strong> for higher-risk and minimum-coverage drivers. Its Louisiana rates held roughly <strong>flat (+0.7%)</strong> for 2026 &mdash; steady while most of the state's larger books cut.",
        "tldr": [
            "Non-standard auto insurer &mdash; higher-risk and minimum-coverage Louisiana drivers",
            "~10,000-policyholder Louisiana book",
            "Louisiana rates roughly <strong>flat (+0.7%)</strong> for 2026 (approved LA DOI filing)",
            "Agent-based; SR-22, lapses, and minimum-coverage profiles are its market",
            "Limited coverage menu &mdash; compare a standard carrier for full coverage or higher limits",
        ],
        "body": """<p>Old American Indemnity is a <strong>non-standard auto insurer</strong> writing in Louisiana &mdash; the market for drivers who don't qualify for a standard carrier's best rate: SR-22 filings, coverage lapses, violations, or a preference for the lowest-cost legal coverage. It distributes through local agents and carries a mid-size non-standard Louisiana book.</p>
<p>Like its non-standard peers, Old American's low book-average premium reflects a <strong>minimum-limits coverage mix</strong> rather than a cheap full-coverage price. It's a placement option for hard-to-write risks, not a full-coverage value play.</p>
<h2>What the filings show</h2>
<p>Louisiana approved an Old American rate change of about <strong>+0.7%</strong> for 2026 &mdash; effectively flat. That makes it one of the steadier books in a year when most of Louisiana's larger auto writers cut rates; steady is not the same as cheap, so a quote comparison still matters.</p>
<h2>Who Old American is right for</h2>
<p>Old American fits <strong>Louisiana drivers who need low-cost minimum coverage or an SR-22</strong> and have limited options at standard carriers. Drivers who want full coverage, higher limits, or add-ons should compare standard carriers first and use Old American only as a placement of last resort.</p>
<div class="callout"><p><strong>Bottom line:</strong> Old American is a non-standard placement option for high-risk Louisiana drivers, with roughly flat 2026 rates. Its low premium reflects thin coverage &mdash; compare it against standard carriers for your ZIP before committing.</p></div>""",
    },
]

BODY_RE = re.compile(r'(<div class="article-body">\s*<div class="rz-zip">.*?</div>\s*)(<div class="tldr-card">.*?)(\s*<div class="rz-zip">)', re.DOTALL)

def build(cfg):
    h = TMPL
    # title + meta
    h = re.sub(r'<title>[^<]*</title>', f"<title>{cfg['title']}</title>", h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+cfg['meta']+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+f"{cfg['full']} Louisiana Auto Review 2026"+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+cfg['meta']+m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1)+cfg['meta']+m.group(2), h)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1)+f"{cfg['full']} Louisiana Auto Review 2026"+m.group(2), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1)+f"https://boringrate.com/article/carrier/{cfg['slug']}.html"+m.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1)+f"https://boringrate.com/article/carrier/{cfg['slug']}.html"+m.group(2), h)
    # JSON-LD Article description + breadcrumb/name
    h = h.replace('"description": "Alfa Insurance is a regional Southeast specialist with competitive pricing and strong agent networks in Alabama, Georgia, Mississippi, and surrounding states.",', f'"description": "{cfg["jsonld"]}",')
    h = h.replace('"name": "Alfa",', f'"name": "{cfg["name"]}",')
    # kicker region + pill + h1 + dek
    h = h.replace('Local Carrier Research &nbsp;&middot;&nbsp; Southeast', 'Local Carrier Research &nbsp;&middot;&nbsp; Louisiana')
    h = re.sub(r'<div class="stat-pill"[^>]*>[^<]*</div>', f'<div class="stat-pill" style="background:#6b665e;">{cfg["pill"]}</div>', h, count=1)
    h = re.sub(r'<h1 class="article-title">[^<]*</h1>', f'<h1 class="article-title">{cfg["full"]} Louisiana Auto Review 2026</h1>', h, count=1)
    h = re.sub(r'<p class="article-dek">.*?</p>', f'<p class="article-dek">{cfg["dek"]}</p>', h, count=1, flags=re.DOTALL)
    # rz-zip CTA carrier name (both CTAs)
    h = h.replace('Instantly compare Alfa Insurance to all carriers', f"Instantly compare {cfg['full']} to all carriers")
    # JSON-LD headline + sticky mobile CTA label
    h = h.replace('"headline": "Alfa Insurance Auto Review 2026",', f'"headline": "{cfg["full"]} Louisiana Auto Review 2026",')
    h = h.replace('Compare Alfa Insurance rates', f"Compare {cfg['name']} rates")
    # TLDR + prose body
    tldr = "\n".join(f"    <li>{x}</li>" for x in cfg['tldr'])
    newmid = ('<div class="tldr-card">\n      <div class="tldr-label">TLDR</div>\n      <ul class="tldr-list">\n'
              + tldr + '\n      </ul>\n    </div>\n\n' + cfg['body'] + '\n    ')
    h, n = BODY_RE.subn(lambda m: m.group(1) + newmid + m.group(3), h, count=1)
    if n != 1:
        raise SystemExit(f"body replace failed for {cfg['slug']} (n={n})")
    # internal links: LA + LA metros; and the two "Compare Alfa ..." headings
    h = h.replace('<div class="internal-links internal-links-state"><a href="../../article/state/alabama.html">Alabama →</a><a href="../../article/state/georgia.html">Georgia →</a><a href="../../article/state/mississippi.html">Mississippi →</a><a href="../../article/state/tennessee.html">Tennessee →</a><a href="../../article/state/virginia.html">Virginia →</a></div>',
                  '<div class="internal-links internal-links-state"><a href="../../article/state/louisiana.html">Louisiana →</a></div>')
    h = h.replace('<div class="internal-links internal-links-metro"><a href="../../article/metro/atlanta.html">Atlanta →</a><a href="../../article/metro/birmingham.html">Birmingham →</a><a href="../../article/metro/nashville.html">Nashville →</a><a href="../../article/metro/memphis.html">Memphis →</a><a href="../../article/metro/jackson-ms.html">Jackson, MS →</a></div>',
                  '<div class="internal-links internal-links-metro"><a href="../../article/metro/new-orleans.html">New Orleans →</a><a href="../../article/metro/baton-rouge.html">Baton Rouge →</a></div>')
    h = h.replace('Compare Alfa Insurance Auto Review 2026 rates by state', f"Compare {cfg['full']} rates by state")
    h = h.replace('Compare Alfa Insurance rates by metro', f"Compare {cfg['full']} rates by metro")
    out = ROOT / "article" / "carrier" / f"{cfg['slug']}.html"
    out.write_text(h, encoding="utf-8")
    return out

for c in CARRIERS:
    p = build(c)
    print("wrote", p)
