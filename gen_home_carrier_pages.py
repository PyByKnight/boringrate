#!/usr/bin/env python3
# Generate home (homeowners) carrier review pages: home/carrier/<slug>.html for the 12
# HOME_CARRIERS. Reuses renters/carrier/state-farm.html as the structural scaffold
# (exact CSS/nav/footer). Per-carrier content grounded in the carrier metadata.
import os, json

NATIONAL = 1915

# slug, name, base, naic, csGrade, stability, avail text, headline, about, whoFor,
# pros[3], cons[3], bottomLine
C = {
 "usaa": dict(name="USAA", base=0.72, naic=0.52, grade="A+", stab=5,
   avail="Military members &amp; their immediate family only",
   head="cheapest home insurance for the military",
   about="USAA serves active-duty military, veterans, and their immediate families, and it consistently posts both the lowest homeowners premiums and one of the lowest complaint ratios in the industry. Membership is the catch — if you or a parent or spouse served, you likely qualify; if not, you can't buy it. For eligible homeowners, USAA is almost always the first quote to get.",
   whoFor="Eligible military households. If you qualify, USAA is the default starting point — it routinely beats every national competitor on price while ranking at the top for claims satisfaction.",
   pros=["Lowest average premiums of any national carrier","Top-tier claims service and complaint ratio (0.52)","Strong bundle, military-specific perks, and financial stability"],
   cons=["Eligibility limited to military members and their families","No local agent offices — phone, app, and web only","Members in high-catastrophe states still face large increases"],
   bottom="If you're eligible for USAA, get its quote first — it's the carrier to beat on both price and claims. If you're not, the next-cheapest names below are your realistic field."),
 "amica": dict(name="Amica Mutual", base=0.86, naic=0.38, grade="A+", stab=5,
   avail="Nationwide · direct (no local agents)",
   head="best-in-class claims service",
   about="Amica is a policyholder-owned mutual that sells directly rather than through agents, and it carries the lowest complaint ratio of any major home insurer (0.38). Many policies are eligible for an annual dividend that returns a share of profits. You trade the local-agent relationship for excellent claims handling and below-average pricing.",
   whoFor="Homeowners who prioritize claims experience over having a local agent, and who are comfortable managing a policy by phone or online. The dividend policy option appeals to long-term holders.",
   pros=["Lowest complaint ratio of any major home insurer","Optional dividend policies return cash to members","Below-average pricing with strong financial stability"],
   cons=["No local agents — direct service only","Not the rock-bottom price in every market","Dividend amounts vary and aren't guaranteed"],
   bottom="Amica is the pick if claims service is your priority. Quote it alongside the cheapest names — its price is competitive and its claims reputation is the best in the business."),
 "auto-owners": dict(name="Auto-Owners", base=0.82, naic=0.68, grade="A", stab=5,
   avail="26 states · independent agent required",
   head="strong agent-sold value in its footprint",
   about="Auto-Owners sells exclusively through independent agents across 26 states and pairs low pricing with high marks for service and stability. There's no online quote — you work with a local independent agent who can also shop other carriers. Where it operates, it's frequently among the cheapest A-rated options.",
   whoFor="Homeowners in Auto-Owners states who prefer an independent agent and want competitive pricing without going fully digital.",
   pros=["Consistently low pricing among A-rated carriers","Excellent financial stability and agent service","Independent agents can tailor and bundle coverage"],
   cons=["Available in only 26 states","Requires an agent — no direct online quote","Less brand-name recognition than national carriers"],
   bottom="In its 26 states, Auto-Owners is one of the best agent-sold values. If you like working with an independent agent, get its quote alongside the direct carriers below."),
 "erie": dict(name="Erie Insurance", base=0.84, naic=0.72, grade="A", stab=4,
   avail="12 states + DC · agent required",
   head="low rates and Rate Lock in its region",
   about="Erie operates across the Mid-Atlantic and Midwest (plus DC), selling through local agents. It's known for low pricing, broad standard coverage, and its Rate Lock feature, which holds your premium steady until you change your policy. Within its footprint it's regularly among the cheapest highly-rated carriers.",
   whoFor="Homeowners in Erie's coverage states who want low rates, generous standard coverage, and a local agent relationship.",
   pros=["Low premiums and generous standard coverage","Rate Lock holds your premium steady between changes","Strong agent network and claims reputation"],
   cons=["Available in only 12 states plus DC","Requires a local agent — limited online self-service","Smaller national footprint and brand presence"],
   bottom="If you live in an Erie state, it belongs on your shortlist — low rates plus Rate Lock are a strong combination. Compare it with Auto-Owners and the direct carriers."),
 "travelers": dict(name="Travelers", base=0.91, naic=0.82, grade="B+", stab=4,
   avail="Nationwide",
   head="best for auto + home bundlers",
   about="Travelers is one of the largest home insurers in the country and tends to shine when you bundle auto and home — its multi-policy discount is among the most generous. It offers a deep menu of optional coverages and endorsements, and it's available nationwide through agents and online.",
   whoFor="Homeowners who bundle auto and home and want a wide range of optional coverages. The combined discount often makes Travelers more competitive than its standalone price suggests.",
   pros=["One of the largest auto+home bundle discounts","Broad menu of optional coverages and endorsements","Nationwide availability with agent and online options"],
   cons=["Standalone (non-bundled) pricing is only middling","Complaint ratio near the industry average","Some endorsements add up quickly"],
   bottom="Travelers is a strong bundle play — if you'll carry auto and home together, get its combined quote. Standalone, compare it against the cheaper names above."),
 "american-family": dict(name="American Family", base=0.93, naic=0.86, grade="B+", stab=4,
   avail="19 Midwest &amp; Western states · local agents",
   head="competitive Midwest &amp; West bundling",
   about="American Family (AmFam) sells through local agents across 19 Midwest and Western states. It's competitive on bundled auto+home pricing and offers a deep discount stack — multi-policy, loyalty, smart-home, and more. Within its footprint it's a solid mainstream option.",
   whoFor="Homeowners in AmFam's 19 states who want a local agent and plan to bundle auto and home for the discount stack.",
   pros=["Competitive bundled pricing in its footprint","Deep discount stack (multi-policy, loyalty, smart home)","Local agents and solid financial stability"],
   cons=["Available in only 19 states","Requires an agent in most cases","Standalone pricing is roughly average"],
   bottom="If you're in an AmFam state and bundling, it's worth a quote. Compare the bundled number against Travelers and the cheaper carriers above."),
 "nationwide": dict(name="Nationwide", base=0.96, naic=0.76, grade="B+", stab=4,
   avail="Nationwide",
   head="vanishing deductible and smart-home savings",
   about="Nationwide is a large mutual offering homeowners coverage nationwide through agents and online. Its signature features are SmartHome device discounts and a vanishing-deductible option that reduces your deductible over claim-free years. Pricing is roughly average, with a better-than-average complaint ratio.",
   whoFor="Homeowners who want recognizable national coverage with features like vanishing deductible and smart-home credits, and who don't mind average base pricing.",
   pros=["Vanishing deductible rewards claim-free years","SmartHome device discounts","Nationwide availability and solid complaint ratio"],
   cons=["Base pricing is around the national average","Best savings require bundling and add-ons","Coverage details vary by region"],
   bottom="Nationwide is a reasonable mainstream choice, especially for its vanishing deductible. Still quote the cheaper names above before committing."),
 "state-farm": dict(name="State Farm", base=1.00, naic=1.08, grade="B+", stab=3,
   avail="Nationwide",
   head="the largest agent network in the country",
   about="State Farm is the largest home insurer in the U.S., built on a captive network of roughly 19,000 local agents. Its homeowners pricing sits near the national average, and its strength is service access — a local agent who knows your policy. Note that State Farm has pulled back on new business in some catastrophe-exposed markets like California.",
   whoFor="Homeowners who value a local agent relationship and reliable nationwide claims, especially those bundling with State Farm auto.",
   pros=["Largest local agent network in the country","Reliable nationwide claims handling","Meaningful bundle discount with State Farm auto"],
   cons=["Pricing only around the national average","Complaint ratio slightly above average for mutuals","Has restricted new business in some high-risk states"],
   bottom="State Farm is a safe, agent-first default — strongest if you bundle auto. But it's rarely the cheapest, so compare it with USAA, Amica, and your best regional carrier."),
 "progressive": dict(name="Progressive", base=1.04, naic=1.12, grade="B", stab=3,
   avail="Nationwide",
   head="easy bundle for Progressive auto customers",
   about="Progressive makes it easy to add home to an existing auto policy, though much of its homeowners coverage is underwritten by third-party partners through its Homeowners Program. That means the actual insurer — and the claims experience — can vary. Pricing is slightly above average and the complaint ratio runs a bit high.",
   whoFor="Progressive auto customers who want a convenient bundle and a single point of purchase, and who'll verify which underwriter actually backs their home policy.",
   pros=["Convenient bundling for Progressive auto customers","Wide availability and online quoting","Access to many underwriters through one program"],
   cons=["Home often underwritten by third-party partners","Above-average pricing and complaint ratio","Claims experience varies by underwriter"],
   bottom="Progressive is mostly a convenience play for existing auto customers. Check which underwriter backs the policy, and compare against the cheaper, more consistent carriers above."),
 "farmers": dict(name="Farmers", base=1.12, naic=0.88, grade="B", stab=3,
   avail="Nationwide",
   head="full-service agents and guaranteed replacement cost",
   about="Farmers sells through dedicated agents and offers strong optional coverages, including guaranteed replacement cost that pays to rebuild even if costs exceed your limit. The trade-off is price — Farmers is among the more expensive national carriers — but its coverage menu and agent service appeal to homeowners who want a hands-on relationship.",
   whoFor="Homeowners who want a full-service agent and premium coverage options like guaranteed replacement cost, and who'll pay more for them.",
   pros=["Guaranteed replacement cost option","Full-service agents and broad coverage menu","Strong optional endorsements"],
   cons=["Among the more expensive national carriers","Best value requires bundling and add-ons","Complaint ratio around average"],
   bottom="Farmers is for homeowners who value coverage depth and agent service over price. If cost is the priority, the carriers above will almost always beat it."),
 "allstate": dict(name="Allstate", base=1.15, naic=1.24, grade="C+", stab=2,
   avail="Nationwide",
   head="broad discounts, but priced at the high end",
   about="Allstate is a large national carrier with an extensive discount lineup and a Claim Satisfaction Guarantee in many states. Its base pricing is on the high end, and its complaint ratio runs above the industry average, so the headline rate matters less than the after-discount, bundled number you actually qualify for.",
   whoFor="Homeowners who can stack Allstate's discounts (bundling, claim-free, autopay) enough to offset its higher base rate, and who want a large agent network.",
   pros=["Extensive discount lineup","Claim Satisfaction Guarantee in many states","Large agent network and brand recognition"],
   cons=["High base pricing","Above-average complaint ratio","Best price depends heavily on stacking discounts"],
   bottom="Allstate can work if you qualify for enough discounts, but its starting price is high. Always compare the cheaper, better-rated carriers above first."),
 "liberty-mutual": dict(name="Liberty Mutual", base=1.18, naic=1.18, grade="C+", stab=2,
   avail="Nationwide",
   head="new-home discounts at a higher base price",
   about="Liberty Mutual is a large national insurer with features like Inflation Guard (which raises your dwelling limit with construction costs) and discounts aimed at new and first-time homeowners. Its base pricing is among the highest of the national carriers and its complaint ratio is above average, so discounts and bundling do a lot of the work.",
   whoFor="New or first-time homeowners who can capture Liberty Mutual's new-home and bundling discounts, offsetting its higher starting price.",
   pros=["Inflation Guard keeps dwelling limits current","New-home and first-time-buyer discounts","Nationwide availability and online tools"],
   cons=["Among the highest base prices nationally","Above-average complaint ratio","Value depends on stacking discounts"],
   bottom="Liberty Mutual makes most sense for new homeowners who can use its targeted discounts. Otherwise, the cheaper, higher-rated carriers above are the smarter first quotes."),
}

# state slugs for internal links
LINK_STATES = [("california","California"),("texas","Texas"),("florida","Florida"),("new-york","New York"),
 ("colorado","Colorado"),("oklahoma","Oklahoma"),("ohio","Ohio"),("georgia","Georgia"),
 ("north-carolina","North Carolina"),("illinois","Illinois"),("pennsylvania","Pennsylvania"),
 ("michigan","Michigan"),("virginia","Virginia"),("washington","Washington"),("tennessee","Tennessee")]

def costword(base):
    if base < 0.85: return "well below the national average"
    if base < 0.97: return "below the national average"
    if base <= 1.05: return "about the national average"
    return "above the national average"

# ── scaffold ──
scaff = open("renters/carrier/state-farm.html", encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>")+len("</style>")]
NAV   = scaff[scaff.index('<header class="top">'):scaff.index("</header>")+len("</header>")]
ZIPBAR = scaff[scaff.index('<div class="zip-bar">'):scaff.index('<div class="wrap-narrow">')]
ZIPBAR = ZIPBAR.replace("compare <em>renters</em> rates", "compare <em>home</em> rates").replace("compare renters rates","compare home rates")
TAIL  = scaff[scaff.index("<footer>"):]
TAIL  = TAIL.replace("/renters/index.html?zip=", "/home/index.html?zip=").replace('window.location.href="/renters/"','window.location.href="/home/"')

def esc(s): return s.replace('"', "&quot;").replace("&amp;","&amp;")

def build(slug):
    d = C[slug]
    name = d["name"]
    est = round(NATIONAL * d["base"]); monthly = round(est/12)
    cw = costword(d["base"])
    naic_note = ("well below industry average" if d["naic"]<0.7 else
                 "near industry average" if d["naic"]<=1.1 else "above industry average")
    url = f"https://boringrate.com/home/carrier/{slug}.html"
    desc = f"{name} homeowners insurance review: estimated ${est:,}/year ({cw}), NAIC complaint ratio {d['naic']}, {d['grade']} financial strength. See {name}'s pros, cons, and how it ranks for your ZIP."
    pros = "\n".join(f"<li>{p}</li>" for p in d["pros"])
    cons = "\n".join(f"<li>{c}</li>" for c in d["cons"])
    statelinks = "".join(f'<a href="/home/state/{s}.html">{n} →</a>' for s,n in LINK_STATES)

    faq = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":f"How much does {name} homeowners insurance cost?",
         "acceptedAnswer":{"@type":"Answer","text":f"{name} homeowners insurance averages roughly ${est:,} per year (about ${monthly:,}/month) for a standard policy with about $300,000 in dwelling coverage — {cw} of about ${NATIONAL:,}. Your exact price depends on your dwelling amount, deductible, roof age, location, and claims history."}},
        {"@type":"Question","name":f"Is {name} good for homeowners insurance?",
         "acceptedAnswer":{"@type":"Answer","text":f"{name} has an NAIC complaint ratio of {d['naic']} ({naic_note}) and {d['grade']} financial strength. {d['bottom']}"}},
        {"@type":"Question","name":f"Where is {name} homeowners insurance available?",
         "acceptedAnswer":{"@type":"Answer","text":f"Availability: {d['avail'].replace('&amp;','and')}. Enter ZIP on BoringRate to see whether {name} is competitive in your specific area and how it ranks against other carriers."}},
    ]})
    crumb = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"BoringRate","item":"https://boringrate.com"},
        {"@type":"ListItem","position":2,"name":"Home Insurance","item":"https://boringrate.com/home/index.html"},
        {"@type":"ListItem","position":3,"name":f"{name} Homeowners Insurance Review","item":url}]})
    art = json.dumps({"@context":"https://schema.org","@type":"Article",
        "headline":f"{name} Homeowners Insurance Review (2026)","description":desc,
        "publisher":{"@type":"Organization","name":"BoringRate","url":"https://boringrate.com"},
        "dateModified":"2026-06-15","mainEntityOfPage":url})

    head = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{name} Homeowners Insurance Review (2026) — BoringRate</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
<meta property="og:title" content="{name} Homeowners Insurance Review (2026)" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{name} Homeowners Insurance Review (2026)" />
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

    article = f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/home/index.html">Home Insurance</a> &nbsp;&middot;&nbsp; Carrier Review &nbsp;&middot;&nbsp; 4 min read</div>
    <div class="stat-pill">{name} &middot; ~${monthly:,}/mo</div>
    <h1 class="article-title">{name} homeowners insurance review (2026): {d['head']}.</h1>
    <p class="article-dek">{d['whoFor']}</p>
    <div class="article-byline">BoringRate Editorial &nbsp;&middot;&nbsp; June 2026</div>
  </div>
  <div class="article-body">
    <div class="tldr-card">
      <div class="tldr-label">TLDR</div>
      <ul class="tldr-list">
        <li>Estimated ${est:,}/year (~${monthly:,}/month) for a standard $300k policy — {cw}</li>
        <li>NAIC complaint ratio {d['naic']} ({naic_note}); {d['grade']} financial strength</li>
        <li>Availability: {d['avail']}</li>
        <li>{d['pros'][0]}</li>
        <li>{d['cons'][0]}</li>
      </ul>
    </div>

    <div class="naic-badge">NAIC complaint ratio &nbsp;<strong>{d['naic']}</strong>&nbsp; &mdash; {naic_note}</div>

    <h2>About {name} homeowners insurance</h2>
    <p>{d['about']}</p>

    <h2>Who {name} homeowners insurance is right for</h2>
    <p>{d['whoFor']}</p>

    <h2>How much does {name} homeowners insurance cost?</h2>
    <p>{name} homeowners insurance averages roughly <strong>${est:,}/year</strong> (about ${monthly:,}/month) for a standard policy with around $300,000 in dwelling coverage and a $1,000 deductible — {cw} of about ${NATIONAL:,}. Homeowners pricing varies enormously by state, dwelling amount, roof age, and claims history, so treat this as a directional benchmark and get a quote for your specific home.</p>
    <p><strong>Availability:</strong> {d['avail']}.</p>

    <h2>{name} homeowners insurance pros and cons</h2>
    <div class="pros-cons">
      <div class="pros-cons-col pros">
        <h4>Pros</h4>
        <ul>{pros}</ul>
      </div>
      <div class="pros-cons-col cons">
        <h4>Cons</h4>
        <ul>{cons}</ul>
      </div>
    </div>

    <div class="callout"><p><strong>Bottom line:</strong> {d['bottom']}</p></div>

    <div class="zip-embed">
      <div class="zip-embed-label">Compare {name} against other carriers</div>
      <h3>See how {name} ranks <em>in your specific ZIP code.</em></h3>
      <div class="zip-embed-sub">Enter ZIP &mdash; carrier rankings update for your location in seconds.<br>No phone. No spam. No selling your information.</div>
      <form class="zip-embed-form" id="embedZipForm" autocomplete="off">
        <input class="zip-embed-input" id="embedZipInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />
        <button type="submit" class="zip-embed-btn">Compare &rarr;</button>
      </form>
    </div>

    <h2>Compare {name} homeowners rates by state</h2>
    <div class="internal-links">{statelinks}</div>

    <h2>Frequently asked questions</h2>
    <div class="callout"><p><strong>How much is {name} homeowners insurance?</strong><br>Roughly ${est:,}/year (~${monthly:,}/month) for a standard $300k-dwelling policy — {cw}. Your exact price depends on your home, deductible, and claims history.</p></div>
    <div class="callout"><p><strong>Is {name} good for homeowners insurance?</strong><br>It carries an NAIC complaint ratio of {d['naic']} ({naic_note}) and {d['grade']} financial strength. {d['bottom']}</p></div>
    <div class="callout"><p><strong>Not sure how much coverage you need?</strong><br>Use the <a href="/home/coverage.html">home coverage calculator</a> to size your dwelling, liability, and add-ons before you compare {name} against other carriers.</p></div>

    <div class="article-email">
      <strong>Get notified when {name} home insurance rates change.</strong>
      <div class="sub">No spam, no calls, no selling your information.</div>
      <div class="email-row" id="articleEmailForm">
        <input class="email-input" id="articleEmailInput" type="email" placeholder="your@email.com" aria-label="Email address" />
        <input class="email-input email-zip" id="articleEmailZip" type="text" inputmode="numeric" placeholder="ZIP code" maxlength="5" aria-label="ZIP code" />
        <select class="email-select" id="articleEmailCarrier" aria-label="Current carrier (optional)">
          <option value="">{name} (current)</option>
          <option>USAA</option><option>Amica</option><option>Auto-Owners</option><option>Erie</option>
          <option>Travelers</option><option>American Family</option><option>Nationwide</option>
          <option>State Farm</option><option>Progressive</option><option>Farmers</option>
          <option>Allstate</option><option>Liberty Mutual</option><option>Other</option>
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
      <div class="email-thanks" id="articleEmailThanks">&#10003; You&#39;re on the list.</div>
    </div>
  </div>
</div>'''

    tail = TAIL.replace("Compare State Farm renters rates", f"Compare {name} home rates")
    return head + "\n" + NAV + "\n" + ZIPBAR + "\n" + article + "\n" + tail

os.makedirs("home/carrier", exist_ok=True)
n=0
for slug in C:
    open(f"home/carrier/{slug}.html","w",encoding="utf-8").write(build(slug)); n+=1
print("wrote", n, "home carrier pages")
