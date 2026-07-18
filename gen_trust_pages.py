#!/usr/bin/env python3
"""
gen_trust_pages.py — build the E-E-A-T trust surfaces (/about.html, /editorial-standards.html)
by cloning the methodology.html shell (head styles + single-source nav + footer + nav scripts),
swapping only the <head> meta and the <article> body. Nav stays in sync via build_nav.py.

Run: python3 gen_trust_pages.py   (idempotent; overwrites the two target files)

Voice: editorial / boring on purpose. Everything here is verifiable from the site itself.
OWNER-FILL slots are marked with <!-- OWNER: ... --> comments (named founder + real sameAs),
left deliberately blank so we never invent a persona or credential.
"""
import re, pathlib

SRC = pathlib.Path("methodology.html").read_text(encoding="utf-8")

# Split the shell: everything up to the opening <article>, and everything from </article> on.
PRE, _, rest = SRC.partition('<article class="method">')
_, _, TAIL = rest.partition('</article>')   # TAIL starts right after </article> (wrap-close + footer + scripts)

def shell(title, desc, slug, kicker, h1_html, deck, meta_line, body, jsonld=""):
    head = PRE
    # Swap head meta (these exact strings all appear in methodology.html's head).
    head = head.replace("Methodology — BoringRate", title)
    head = head.replace(
        "How BoringRate ranks auto insurance carriers. Plain-English explanation of our data sources, scoring rules, and the limits of what we know.",
        desc)
    head = head.replace("https://boringrate.com/methodology.html", f"https://boringrate.com/{slug}")
    if jsonld:
        head = head.replace("</head>", jsonld + "\n</head>")
    article = (
        f'<article class="method">\n\n'
        f'    <div class="article-kicker">{kicker}</div>\n'
        f'    <h1 class="article-h">{h1_html}</h1>\n'
        f'    <p class="article-deck">{deck}</p>\n'
        f'    <div class="article-meta">{meta_line}</div>\n\n'
        f'    <div class="prose">\n{body}\n    </div>\n  '
    )
    return head + article + "</article>" + TAIL

# ─────────────────────────────────────────────────────────── ABOUT ──
about_body = """
      <p>BoringRate is an independent research project that tracks prices for auto, home, and renters insurance to provide visibility to the consumer — including who is raising and cutting rates — using the carriers' own approved rate filings. It exists for one reader in particular: the person who just opened a renewal notice, saw a number that made no sense, and wants to know whether it's them, their carrier, or the whole market.</p>

      <div class="callout">
        There's no form on this site that routes your details to buyers, and no one can pay to affect a ranking — <strong>you can't buy your way up, and best rates come first.</strong>
      </div>

      <h2><span class="num">§ 01</span>What BoringRate is</h2>

      <p>Most rate-comparison sites are lead funnels wearing an editorial costume — the ranking exists to route your contact information to three to five buyers who then call and email you for weeks. BoringRate is the opposite arrangement. There is no form that sends your details anywhere. The rankings and rate-change trackers are the product, and they are built to be <strong>read and checked</strong>, not to harvest a lead.</p>

      <p>We cover three lines today: auto, homeowners, and renters. Auto is the long game; home and renters are where a reader blindsided by a rate increase most often lands first. Every one of those readers is treated the same way — shown who is cheapest for their situation, and shown the primary evidence behind it.</p>

      <h2><span class="num">§ 02</span>Where our numbers come from</h2>

      <p>The distinguishing thing about BoringRate is the source. Where other sites cite a single blended national average, we work from the <strong>primary documents carriers file with regulators</strong>: approved rate filings in the SERFF system, state insurance-department open data (Texas and California publish machine-readable filing data), and the rate comparisons that a handful of departments publish directly. Those figures are cross-checked against multiple secondary aggregator averages, which act as a guardrail rather than the source of truth.</p>

      <p>You can inspect the raw material yourself. The <a href="/rate-filings/">rate-filings roll-up</a> lists every auto and home filing we've captured, each row linking its primary source — the SERFF tracking number and the regulator's portal. The <a href="/methodology.html">methodology</a> explains exactly how those filings become a ranking, and — just as importantly — what we will not claim from them.</p>

      <h2><span class="num">§ 03</span>Editorial independence</h2>

      <p>The ranking rewards carriers that cut rates and marks the ones raising them, regardless of who they are or how large. That rule is not negotiable and not for sale. We publish the direction of a carrier's filed changes even when it's unflattering, because the entire value of a rate-transparency site collapses the moment a reader suspects the list was arranged for someone other than them. Our full sourcing hierarchy, independence rules, and corrections policy live on the <a href="/editorial-standards.html">editorial standards</a> page.</p>

      <h2><span class="num">§ 04</span>Who's behind it</h2>

      <p>BoringRate is run by a <strong>team of insurance insiders with decades of combined experience in product, pricing, and insurance lead generation</strong>. That's the background the whole site is built on: first-hand knowledge of how rates are set, how filings work, and exactly how the lead-generation machine turns a shopper into a product that gets sold to several buyers at once.</p>

      <p>BoringRate is the deliberate opposite of that machine. Having seen how the aggregators operate from the inside, the aim is simple — give the shopper the honest version (who's cheapest, who's raising rates, backed by the carriers' own filings) and point them straight at the carrier instead of into a funnel.</p>

      <div class="callout">
        <strong>The mission:</strong> help you find the best coverage at the best price, get you there faster, and leave you better informed than the ad you clicked. We do the boring part — reading the rate filings — so you don't have to.
      </div>

      <!-- OWNER-FILL (optional, strongest E-E-A-T signal): add named team members / a real byline and
           real profile links (LinkedIn / X) to the Person + Organization sameAs in the JSON-LD. The
           team's experience is stated above; attaching real names is the maximal Experience/Expertise
           signal. Left nameless per owner (2026-07-18) — never invent one. -->

      <p>We're deliberately not licensed agents and don't sell insurance — that independence is the point, not a gap. When you're ready to actually buy, you'll talk to a carrier or an agent; our job ends at telling you which two or three are worth the call.</p>

      <h2><span class="num">§ 05</span>Corrections &amp; contact</h2>

      <p>If a number here doesn't reconcile with a regulator's published figure, or a filing moved and we haven't caught it, we want to know. Corrections are logged with dates on the <a href="/editorial-standards.html">editorial standards</a> page. Reach us at <a href="mailto:hello@boringrate.com">hello@boringrate.com</a>.</p>

      <div class="footnotes">
        <h3>Primary sources we work from</h3>
        <ol>
          <li><strong>System for Electronic Rates &amp; Forms Filing (SERFF).</strong> Approved carrier rate filings — the underlying source for our rate-change trackers and price positioning. <a href="https://filingaccess.serff.com/">filingaccess.serff.com</a></li>
          <li><strong>State insurance-department open data.</strong> Texas Department of Insurance (data.texas.gov) and California Department of Insurance publish machine-readable filing data.</li>
          <li><strong>NAIC.</strong> National Association of Insurance Commissioners — market-share and complaint data. <a href="https://content.naic.org/">content.naic.org</a></li>
          <li><strong>The full audit trail.</strong> <a href="/rate-filings/">Every filing we've captured</a>, each linking its primary source.</li>
        </ol>
      </div>
"""

about_jsonld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "AboutPage",
  "name": "About BoringRate",
  "url": "https://boringrate.com/about.html",
  "publishingPrinciples": "https://boringrate.com/editorial-standards.html",
  "about": {
    "@type": "Organization",
    "name": "BoringRate",
    "url": "https://boringrate.com",
    "description": "Independent insurance-rate research built from carriers' own approved rate filings. No lead sales, no email capture, no commissioned carrier relationships.",
    "foundingDate": "2024",
    "knowsAbout": ["auto insurance rates", "homeowners insurance rates", "renters insurance", "insurance rate filings", "SERFF"],
    "publishingPrinciples": "https://boringrate.com/editorial-standards.html",
    "sameAs": []
  }
}
</script>"""

# ────────────────────────────────────────────── EDITORIAL STANDARDS ──
ed_body = """
      <p>This page states how BoringRate produces what it publishes: what we source, in what order of authority, how we stay independent, what we will and won't claim, and how we fix mistakes. It's meant to be held against the site — if a page doesn't live up to what's written here, that's a bug, and the contact address is at the bottom.</p>

      <h2><span class="num">§ 01</span>Sourcing hierarchy</h2>

      <p>Not all sources are equal, and we rank them explicitly. In descending order of authority:</p>

      <p><strong>1. Approved rate filings (primary).</strong> For any claim about what a carrier is charging or how its rates are moving, the source of record is the carrier's own filing approved by a state regulator — accessed through SERFF or a state insurance department's open data. This is what lets us say "this carrier filed a 6.2% increase, effective July" and point you at the document.</p>

      <p><strong>2. Regulator-published comparisons and bulletins.</strong> Where a state department publishes its own rate comparison or a consumer bulletin, we use it directly and link the specific page, not the portal home.</p>

      <p><strong>3. NAIC data.</strong> For market-level facts — market share, complaint indices — the National Association of Insurance Commissioners is the source.</p>

      <p><strong>4. Secondary aggregators (guardrail only).</strong> Blended averages from other research sites are used to sanity-check our primary-sourced figures, never as the origin of a number. When primary and secondary disagree, primary wins and we say so.</p>

      <div class="callout">
        For questions of <strong>coverage</strong> — "does homeowners insurance cover mold?" — a rate filing is the wrong document and citing one would be overclaiming. Coverage claims are sourced to <strong>standard policy-form language</strong> (the ISO HO-3 homeowners form, the PP&nbsp;00&nbsp;01 personal-auto form), state insurance-department consumer guides, or statute — with the caveat that your carrier's specific form may differ.
      </div>

      <h2><span class="num">§ 02</span>Independence</h2>

      <p>No carrier, agency, or lead buyer pays for placement, and none can influence a ranking. A carrier that cuts rates is marked as a cutter and a carrier that raises them is marked as a raiser, regardless of size, relationship, or how the result reads.</p>

      <p>BoringRate does not monetize today. If that changes, it will be in ways aligned with the reader's interest — for example, paid ad placement for independent agents who provide genuine comparison value. One thing will never be for sale: a carrier, agent, or anyone else paying to change a ranking. Rankings are ordered by the data — best rates first — full stop.</p>

      <h2><span class="num">§ 02b</span>How pages are produced</h2>

      <p>Our rankings, trackers, and rate figures are generated from a maintained dataset of parsed filings, not written by hand per page — which is what keeps them internally consistent and lets a correction propagate everywhere at once. Editorial judgment — which filings are material, how to frame a market, where to be skeptical — is applied deliberately and is the responsibility of the site's operator.</p>

      <!-- OWNER-FILL (optional, increasingly expected): if you want to disclose the use of AI
           tooling in the production pipeline, state it here plainly. Left blank pending your call. -->

      <h2><span class="num">§ 03</span>Estimates, not quotes</h2>

      <p>Every price on BoringRate is an <strong>editorial estimate of typical positioning</strong>, not a quote. We don't have your full underwriting profile, and no site without it does. We show which carriers are likely to come back competitive for someone in your situation, so you can stop after a few calls instead of a dozen. The <a href="/methodology.html">methodology</a> spells out exactly how the estimate is built and rounded, and why we show a directional delta instead of a fake-precise dollar figure.</p>

      <h2><span class="num">§ 04</span>Accuracy &amp; corrections</h2>

      <p>When the underlying filings move, the pages move with them, and material methodology changes are dated where they're made. If you spot a figure that doesn't reconcile with a regulator's published number, tell us at <a href="mailto:hello@boringrate.com">hello@boringrate.com</a> and we'll correct it and log it below.</p>

      <div class="callout">
        <strong>Corrections log.</strong> No corrections logged yet. When we make a material correction, it will appear here with the date, what was wrong, and what changed.
      </div>

      <h2><span class="num">§ 05</span>Privacy</h2>

      <p>There is no email capture and no lead form on this site. We use privacy-friendly, cookieless analytics (Plausible) to understand which pages help, and we don't collect personal information to sell. The reason we can be this blunt about which carriers are expensive is that we don't owe any of them a shopper.</p>

      <div class="footnotes">
        <h3>Referenced sources</h3>
        <ol>
          <li><strong>SERFF.</strong> System for Electronic Rates &amp; Forms Filing. <a href="https://filingaccess.serff.com/">filingaccess.serff.com</a></li>
          <li><strong>ISO standard policy forms.</strong> Homeowners HO-3 (HO&nbsp;00&nbsp;03) and Personal Auto (PP&nbsp;00&nbsp;01) — the baseline forms most carrier policies build on.</li>
          <li><strong>NAIC.</strong> Market share and complaint data. <a href="https://content.naic.org/">content.naic.org</a></li>
          <li><strong>Full filing audit trail.</strong> <a href="/rate-filings/">rate-filings roll-up</a>.</li>
        </ol>
      </div>
"""

ed_jsonld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "Editorial Standards & Corrections Policy — BoringRate",
  "url": "https://boringrate.com/editorial-standards.html",
  "publisher": {
    "@type": "Organization",
    "name": "BoringRate",
    "url": "https://boringrate.com"
  }
}
</script>"""

pages = [
    dict(path="about.html",
         title="About BoringRate",
         desc="Who's behind BoringRate: an independent insurance-rate research project built from carriers' own approved rate filings. No lead sales, no email capture, no carrier commissions.",
         slug="about.html",
         kicker="§ About · Who's behind BoringRate",
         h1_html="Independent rate research. <em>Boring on purpose.</em>",
         deck="An independent research project that tracks prices for auto, home, and renters insurance to give consumers visibility — who's raising and cutting rates — from the carriers' own filings. Built by a team of insurance insiders. We do the boring part so you don't have to.",
         meta_line="Last updated · July 2026 &nbsp;·&nbsp; By a team of insurance insiders &nbsp;·&nbsp; Public data only",
         body=about_body, jsonld=about_jsonld),
    dict(path="editorial-standards.html",
         title="Editorial Standards & Corrections Policy — BoringRate",
         desc="How BoringRate sources, ranks, and corrects its insurance-rate research: the sourcing hierarchy (primary filings first), independence rules, estimates-not-quotes, and a dated corrections policy.",
         slug="editorial-standards.html",
         kicker="§ Editorial Standards",
         h1_html="How we source, rank, and <em>correct.</em>",
         deck="What we source and in what order of authority, how we stay independent, what we will and won't claim, and how we fix mistakes.",
         meta_line="Last updated · July 2026 &nbsp;·&nbsp; Reviewed quarterly &nbsp;·&nbsp; Corrections logged below",
         body=ed_body, jsonld=ed_jsonld),
]

for pg in pages:
    html = shell(pg["title"], pg["desc"], pg["slug"], pg["kicker"], pg["h1_html"],
                 pg["deck"], pg["meta_line"], pg["body"], pg["jsonld"])
    pathlib.Path(pg["path"]).write_text(html, encoding="utf-8")
    print(f"wrote {pg['path']}  ({len(html):,} bytes)")
