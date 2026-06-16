#!/usr/bin/env python3
# Home (homeowners) guide/FAQ cluster — home has tools but no content. Home scaffold;
# CTAs funnel to /home/ + /home/coverage.html.
import re, json

scaff = open("home/state/florida.html", encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>")+len("</style>")]
NAV   = scaff[scaff.index('<header class="top">'):scaff.index("</header>")+len("</header>")]
TAIL  = scaff[scaff.index("<footer>"):]
TAIL  = re.sub(r'Compare [A-Za-z ]+ rates <span class="ascta-arrow">', 'Compare home rates <span class="ascta-arrow">', TAIL)

CTA = ('<div class="tooltiles">'
 '<div class="tile"><div class="tile-kicker">Compare rates</div>'
 '<div class="tile-name">Cheapest home insurance for your ZIP</div>'
 '<div class="tile-desc">Rank carriers by estimated premium for your area &mdash; national average is about $1,915/yr. No calls, no spam.</div>'
 '<form class="tile-zipform" onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z)){location.href=\'/home/?zip=\'+z}else{this.zc.focus()}"><input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="tile-zip-btn">Compare &rarr;</button></form>'
 '</div>'
 '<div class="tile"><div class="tile-kicker">Coverage calculator</div>'
 '<div class="tile-name">How much do you actually need?</div>'
 '<div class="tile-desc">Size your dwelling, liability, and add-ons in two minutes &mdash; the dwelling number is the one that matters most.</div>'
 '<a class="tbtn secondary" href="/home/coverage.html">Help me choose my coverage &rarr;</a>'
 '</div></div>')

def esc(s): return s.replace('"', "&quot;")

ARTICLES = {
"how-much-homeowners-insurance-do-i-need": dict(
 title="How Much Homeowners Insurance Do You Need? (2026)",
 h1="How much homeowners insurance do you actually need?",
 dek="The number that matters most is dwelling coverage — and it should equal your rebuild cost, not your home's market value. Here's how to set every coverage right.",
 kicker="Home Basics",
 lead="<p>Homeowners insurance has six standard coverages, but one of them — <strong>Dwelling (Coverage A)</strong> — drives almost everything. Get it right and the rest mostly falls into place. Our <a class=\"ca-link\" href=\"/home/coverage.html\">coverage calculator</a> sizes it all for you; here's the logic.</p>",
 sections=[
  ("Dwelling (Coverage A): rebuild cost, not market value","<p>This is the number that matters most. Set it to what a contractor would charge to <strong>rebuild your home today</strong> — not its market price (which includes land) and not what you paid. In hot markets rebuild cost is often <em>below</em> market value; after a construction-cost spike it can be above. <strong>Under-insuring here is the costliest mistake</strong>, and many policies pro-rate even partial claims if you insure for less than 80% of rebuild cost. Ask your insurer to run a free replacement-cost estimate.</p>"),
  ("Other structures &amp; personal property (B &amp; C)","<p>Other Structures (detached garage, fence, shed) defaults to 10% of dwelling — fine for most. Personal Property defaults to 50% of dwelling; do a quick room total to confirm, and choose replacement cost so you're paid to buy new.</p>"),
  ("Liability (Coverage E): at least your net worth","<p>$100,000 is the floor, but $300,000–$500,000 costs only a little more. Carry at least as much as your net worth, and add a $1–2M umbrella if you have real assets — it's the cheapest liability per dollar you can buy.</p>"),
  ("The add-ons worth considering","<p><strong>Water backup</strong> (sewer/sump failure — a common basement claim, ~$50–100/yr), <strong>extended/guaranteed replacement cost</strong> (pays above your limit if rebuild costs surge), and <strong>scheduled items</strong> for jewelry or art above the standard caps. And remember: <strong>flood and earthquake are never included</strong> — they're separate policies.</p>"),
 ],
 callout="<strong>Get the dwelling number right first.</strong> The coverage calculator turns your rebuild cost and assets into the right Coverage A / liability / add-ons — then sends you to compare carriers for that coverage.",
 faq=[
  ("How much dwelling coverage do I need?","Enough to rebuild your home today (rebuild cost) — not its market value or purchase price. Ask your insurer for a replacement-cost estimate, and insure for at least 80% of it to avoid pro-rated claims."),
  ("Should homeowners insurance equal my home's value?","No — it should equal your rebuild cost, which excludes land. In many markets that's less than market value; after construction-cost spikes it can be more."),
  ("How much liability coverage do I need on a home policy?","At least $100,000, with $300,000–$500,000 recommended and only slightly more. Add an umbrella policy if you have significant assets."),
  ("What's the 80% rule in homeowners insurance?","If you insure your home for less than 80% of its rebuild cost, insurers may pro-rate (reduce) even partial claims — so don't under-insure the dwelling."),
 ],
 cross=("/home/coverage.html","Home Coverage Calculator")),

"what-does-homeowners-insurance-cover": dict(
 title="What Does Homeowners Insurance Cover? (2026)",
 h1="What homeowners insurance covers — and what it doesn't.",
 dek="Six coverages handle your house, your stuff, and your liability. But flood, earthquake, and neglected maintenance are on you. Here's the full picture.",
 kicker="Home Basics",
 lead="<p>A standard homeowners policy (an HO-3) bundles six coverages. Knowing what each does — and the exclusions that surprise people — is the difference between a smooth claim and a denied one.</p>",
 sections=[
  ("Dwelling, other structures, personal property (A, B, C)","<p><strong>Dwelling</strong> rebuilds your house after a covered loss; <strong>Other Structures</strong> covers detached garages, fences, and sheds; <strong>Personal Property</strong> replaces your belongings (often 50% of dwelling), and follows you off-premises too.</p>"),
  ("Loss of use, liability, medical payments (D, E, F)","<p><strong>Loss of Use</strong> pays hotel and extra living costs if your home is unlivable; <strong>Personal Liability</strong> covers injuries and damage you cause (plus legal defense); <strong>Medical Payments</strong> covers minor guest injuries regardless of fault.</p>"),
  ("Covered perils","<p>A standard HO-3 covers fire, lightning, windstorm, hail, theft, vandalism, falling objects, and sudden water damage from plumbing — among others. Your <em>house</em> is covered against most perils except those specifically excluded; your <em>belongings</em> are covered against a named list.</p>"),
  ("What homeowners insurance does NOT cover","<p>The big exclusions: <strong>flood</strong> and <strong>earthquake</strong> (separate policies), <strong>normal wear and maintenance</strong> (a roof that simply aged out, not a storm), <strong>mold</strong> beyond small limits, <strong>pests/termites</strong>, <strong>sewer/drain backup</strong> (needs an endorsement), and high-value items above category sublimits unless scheduled.</p>"),
 ],
 callout="<strong>The pattern:</strong> homeowners insurance covers sudden, accidental damage — not gradual wear, not flood, not earthquake. Use the coverage calculator to see exactly what your limits protect and what to add.",
 faq=[
  ("What does homeowners insurance cover?","Your dwelling, other structures, personal property, loss of use, personal liability, and medical payments — against perils like fire, wind, hail, theft, and sudden water damage."),
  ("What does homeowners insurance not cover?","Flood, earthquake, normal wear and maintenance, mold beyond small limits, pests, and sewer backup (unless you add an endorsement)."),
  ("Does homeowners insurance cover the contents of my home?","Yes — personal property coverage (often 50% of dwelling) replaces your belongings, and it follows you off-premises. Choose replacement cost and schedule high-value items."),
  ("Is flood covered by homeowners insurance?","No. Flood requires a separate policy (NFIP or private). Earthquake is also separate. Sudden internal water (a burst pipe) is covered, but rising water is not."),
 ],
 cross=("/home/coverage.html","Home Coverage Calculator")),

"does-homeowners-insurance-cover": dict(
 title="Does Homeowners Insurance Cover That? (Roof, Water, Mold &amp; More)",
 h1="Does homeowners insurance cover that? The common questions.",
 dek="Roof damage, water damage, mold, a fallen tree, your dog, theft, foundation cracks — honest answers to the scenarios homeowners actually search for.",
 kicker="Home Basics",
 lead="<p>Most 'does it cover…' answers come down to one test: was the damage <strong>sudden and accidental</strong>, or <strong>gradual wear / a maintenance issue</strong>? The former is usually covered; the latter usually isn't. Here are the ones homeowners ask most.</p>",
 sections=[
  ("Roof damage","<p><strong>Depends.</strong> Sudden damage from a covered peril — a storm, hail, a fallen tree — is covered. A roof that simply <em>wore out</em> with age is not (that's maintenance). Note: many insurers now pay <strong>actual cash value</strong> (depreciated) on older roofs rather than full replacement, so check your roof settlement terms.</p>"),
  ("Water damage","<p><strong>Sudden, internal water</strong> — a burst pipe, an overflowing washer, a leak from a covered roof breach — is covered. <strong>Flood</strong> (rising water from outside) is not — that's a separate policy. <strong>Sewer/drain backup</strong> needs a water-backup endorsement. Slow, long-term leaks you should have caught are treated as maintenance and excluded.</p>"),
  ("Mold","<p><strong>Limited.</strong> If mold results from a covered water loss (a burst pipe), remediation is usually covered up to a sublimit ($1,000–$10,000 typically). Mold from ongoing humidity or a neglected leak is not.</p>"),
  ("A fallen tree","<p><strong>Usually yes.</strong> If a tree hits your house, garage, or fence, dwelling/other-structures coverage handles the damage and removal (up to a limit). A tree that falls and hits <em>nothing</em> is often only removed if it blocks a driveway or ramp.</p>"),
  ("Your dog (and dog bites)","<p><strong>Usually</strong>, under personal liability — but many insurers exclude certain breeds or a dog with a bite history. Disclose your pet; an undisclosed dog can void the claim.</p>"),
  ("Theft and foundation","<p><strong>Theft</strong> of belongings is covered (subject to deductible and sublimits). <strong>Foundation cracks</strong> from settling, soil movement, or earthquake are generally <em>not</em> covered — only if caused by a specific covered peril like a burst pipe.</p>"),
 ],
 callout="<strong>The rule of thumb:</strong> sudden accidents are covered; wear, neglect, flood, and earthquake are not. The coverage calculator shows what your limits and endorsements actually protect.",
 faq=[
  ("Does homeowners insurance cover roof damage?","Sudden damage from a storm, hail, or fallen tree — yes. A roof that wore out from age — no. Older roofs may settle at depreciated (actual cash) value."),
  ("Does homeowners insurance cover water damage?","Sudden internal water (burst pipe, overflow) yes; flood no (separate policy); sewer backup only with an endorsement; slow leaks treated as maintenance are excluded."),
  ("Does homeowners insurance cover mold?","Usually only when it results from a covered water loss, up to a sublimit. Mold from humidity or a neglected leak isn't covered."),
  ("Does homeowners insurance cover a fallen tree?","Yes if it damages your home or other structures — repairs and removal up to a limit. A tree that hits nothing is often only removed if it blocks access."),
 ],
 cross=("/home/coverage.html","Home Coverage Calculator")),

"is-homeowners-insurance-required": dict(
 title="Is Homeowners Insurance Required? (2026)",
 h1="Is homeowners insurance required?",
 dek="Not by law — but if you have a mortgage, your lender requires it, and going without exposes your largest asset. Here's what actually applies.",
 kicker="Home Basics",
 lead="<p>No state legally requires homeowners insurance. But that rarely matters in practice: <strong>if you have a mortgage, your lender requires it</strong> as a condition of the loan — and even paid-off homeowners are taking a large risk by skipping it.</p>",
 sections=[
  ("Why lenders require it","<p>Your home is the bank's collateral. Lenders require you to carry homeowners insurance (with them named as mortgagee) so the asset backing the loan is protected. If you let it lapse, the lender can buy <strong>force-placed insurance</strong> on your behalf — far more expensive and protecting only them, not your belongings or liability.</p>"),
  ("What about paid-off homes?","<p>Once the mortgage is gone, no one requires coverage — but a fire or major loss without insurance means rebuilding entirely out of pocket, plus losing the liability protection. For most owners, dropping it isn't worth the savings.</p>"),
  ("Condos and renters are different","<p>Condo owners need an <strong>HO-6</strong> policy (the condo association's master policy only covers the building shell). Renters need <a class=\"ca-link\" href=\"/renters/is-renters-insurance-worth-it.html\">renters insurance</a>, which landlords usually require.</p>"),
  ("The takeaway","<p>Required or not, homeowners insurance protects the largest asset most people own. The real decision is which carrier is cheapest — compare for your ZIP below.</p>"),
 ],
 callout="<strong>Bottom line:</strong> not legally mandated, but mortgage lenders require it and force-place a costly policy if you lapse. Carry it, and compare carriers to get the lowest rate.",
 faq=[
  ("Is homeowners insurance required by law?","No state legally requires it. But mortgage lenders require it as a loan condition, and force-place expensive coverage if you let it lapse."),
  ("Do I need homeowners insurance if my house is paid off?","Not required by anyone, but going without means rebuilding out of pocket after a major loss and losing liability protection — rarely worth the savings."),
  ("What is force-placed insurance?","Coverage your lender buys for you if you let your policy lapse. It's usually much more expensive and protects only the lender, not your belongings or liability."),
  ("Do condo owners need homeowners insurance?","Yes — an HO-6 policy. The condo association's master policy typically covers only the building structure, not your interior, belongings, or liability."),
 ],
 cross=("/home/coverage.html","Home Coverage Calculator")),

"how-much-does-homeowners-insurance-cost": dict(
 title="How Much Does Homeowners Insurance Cost? (2026)",
 h1="How much does homeowners insurance cost?",
 dek="Roughly $1,900–$2,500 a year nationally for ~$300k of dwelling coverage — but it swings from ~$1,100 in low-risk states to over $4,000 in Florida. Here's what drives it.",
 kicker="Home Basics",
 lead="<p>The national average homeowners premium runs about <strong>$1,900–$2,500 a year</strong> for roughly $300,000 in dwelling coverage. But no line of insurance varies more by location — catastrophe risk dominates the price.</p>",
 sections=[
  ("What it costs by state","<p>State averages range from around <strong>$1,100</strong> in low-risk states (Hawaii, Vermont, Delaware) to over <strong>$4,000</strong> in Florida, and high in Oklahoma, Kansas, Texas, and Louisiana — driven by hurricanes, tornadoes, hail, and wildfire. See your state's average and cheapest carriers on our <a class=\"ca-link\" href=\"/home/index.html\">home rate comparison</a>.</p>"),
  ("What drives your premium","<p>The biggest factors: <strong>your dwelling amount</strong> (rebuild cost), <strong>local catastrophe risk</strong> (the dominant one), your <strong>roof's age and type</strong>, your <strong>deductible</strong>, prior <strong>claims</strong>, and in most states your <strong>credit-based insurance score</strong>. A new roof and a higher deductible are two of the biggest levers you control.</p>"),
  ("How to pay less","<p><strong>Bundle</strong> with auto (often 10–20% off), <strong>raise your deductible</strong>, add <strong>roof/impact-resistant and smart-home discounts</strong>, avoid small claims (they raise renewals), and <strong>compare carriers</strong> — premiums for the same home can differ by hundreds to over a thousand dollars a year.</p>"),
 ],
 callout="<strong>The cheapest move:</strong> bundling and a higher deductible help, but comparing carriers is where the biggest spread is. Enter your ZIP to see the lowest-priced home insurers for your area.",
 faq=[
  ("How much is homeowners insurance per year?","About $1,900–$2,500 nationally for ~$300,000 in dwelling coverage, but it ranges from ~$1,100 in low-risk states to over $4,000 in Florida and other catastrophe-prone states."),
  ("Why is homeowners insurance so expensive in some states?","Catastrophe risk — hurricanes in Florida and the Gulf, tornadoes and hail in the Plains, wildfire in the West — drives premiums far above low-risk states."),
  ("What's the cheapest way to lower homeowners insurance?","Bundle with auto, raise your deductible, add roof and smart-home discounts, avoid small claims, and compare carriers — the spread for the same home is often hundreds of dollars."),
  ("Does my credit affect homeowners insurance?","In most states, yes — a credit-based insurance score is a rating factor. California, Maryland, and Massachusetts restrict its use."),
 ],
 cross=("/home/index.html","Home Rate Comparison")),
}

def build(slug, c):
    url=f"https://boringrate.com/home/{slug}.html"
    secs="".join(f'<h2>{t}</h2>{b}' for t,b in c["sections"])
    faqhtml="".join(f'<div class="callout"><p><strong>{q}</strong><br>{a}</p></div>' for q,a in c["faq"])
    faqjson=json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub(r"<[^>]+>","",a)}} for q,a in c["faq"]]})
    crossUrl,crossLbl=c["cross"]
    head=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{c["title"]} — BoringRate</title>
<meta name="description" content="{esc(c["dek"])}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
<meta property="og:title" content="{esc(c["title"])}" />
<meta property="og:description" content="{esc(c["dek"])}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(c["title"])}" />
<meta name="twitter:description" content="{esc(c["dek"])}" />
<meta name="twitter:image" content="https://boringrate.com/og-default.png" />
<script type="application/ld+json">
{faqjson}
</script>
</head>
<body>'''
    zipbar='''<div class="zip-bar"><div class="wrap"><div class="zip-bar-inner">
<div class="zip-bar-slogan"><strong>Boring Research.</strong> Easy Decision. &mdash; Enter your ZIP to compare <em>home</em> rates.</div>
<form class="zip-bar-form" id="zipBarForm" autocomplete="off"><input class="zip-bar-input" id="zipBarInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="zip-bar-btn">Compare &rarr;</button></form>
</div></div></div>'''
    body=f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/home/index.html">Home Insurance</a> &nbsp;·&nbsp; {c["kicker"]} &nbsp;·&nbsp; 4 min read</div>
    <h1 class="article-title">{c["h1"]}</h1>
    <p class="article-dek">{c["dek"]}</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; June 2026</div>
  </div>
  <div class="article-body">
    {c["lead"]}
    {CTA}
    {secs}
    <div class="callout"><p>{c["callout"]}</p></div>
    <h2>Frequently asked questions</h2>
    {faqhtml}
    <div class="callout"><p>Related: <a class="ca-link" href="{crossUrl}">{crossLbl} &rarr;</a></p></div>
  </div>
</div>'''
    return head+"\n"+NAV+"\n"+zipbar+"\n"+body+"\n"+TAIL

n=0
for slug,c in ARTICLES.items():
    open(f"home/{slug}.html","w",encoding="utf-8").write(build(slug,c)); n+=1
    print("wrote home/"+slug+".html")
print("done",n)
