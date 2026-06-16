#!/usr/bin/env python3
# Renters guide/FAQ cluster — renters has tools but no content. Mirrors the auto FAQ
# generator using the renters scaffold; CTAs funnel to /renters/ + /renters/coverage.html.
import re, json

scaff = open("renters/state/colorado.html", encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>")+len("</style>")]
NAV   = scaff[scaff.index('<header class="top">'):scaff.index("</header>")+len("</header>")]
TAIL  = scaff[scaff.index("<footer>"):]
TAIL  = re.sub(r'Compare [A-Za-z ]+ rates <span class="ascta-arrow">', 'Compare renters rates <span class="ascta-arrow">', TAIL)

CTA = ('<div class="tooltiles">'
 '<div class="tile"><div class="tile-kicker">Compare rates</div>'
 '<div class="tile-name">Cheapest renters insurance for your ZIP</div>'
 '<div class="tile-desc">Rank carriers by estimated price for your area &mdash; national average is about $168/yr ($14/mo). No calls, no spam.</div>'
 '<form class="tile-zipform" onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z)){location.href=\'/renters/?zip=\'+z}else{this.zc.focus()}"><input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="tile-zip-btn">Compare &rarr;</button></form>'
 '</div>'
 '<div class="tile"><div class="tile-kicker">Coverage calculator</div>'
 '<div class="tile-name">How much do you actually need?</div>'
 '<div class="tile-desc">Size your personal property + liability in two minutes &mdash; see what to buy and what to skip.</div>'
 '<a class="tbtn secondary" href="/renters/coverage.html">Help me choose my coverage &rarr;</a>'
 '</div></div>')

def esc(s): return s.replace('"', "&quot;")

ARTICLES = {
"is-renters-insurance-worth-it": dict(
 title="Is Renters Insurance Worth It? (2026)",
 h1="Is renters insurance worth it? Almost always — here's the math.",
 dek="At about $14 a month for ~$30,000 of belongings plus $100,000 of liability, renters insurance is one of the best-value products in personal finance. Here's what you're actually buying.",
 kicker="Renters Basics",
 lead="<p>The national average renters policy runs about <strong>$168 a year — roughly $14 a month</strong>. For that you get three things most renters underestimate: coverage for your belongings, personal liability protection, and money to live on if your place becomes unlivable. The question isn't really whether it's worth it; it's whether you can find the cheapest one.</p>",
 sections=[
  ("What you're actually protecting","<p>Three things. <strong>Personal property</strong>: everything you own — furniture, electronics, clothes — replaced if it's stolen or destroyed by a covered event, even away from home (a laptop swiped from your car). <strong>Liability</strong>: if a guest is injured in your unit, your dog bites someone, or you accidentally cause damage (a kitchen fire that spreads), it covers their costs and your legal defense — up to $100,000+ for a few dollars a month. <strong>Loss of use</strong>: if a fire or burst pipe forces you out, it pays for a hotel and extra living costs.</p>"),
  ("The math","<p>Add up what it would cost to re-buy your stuff from scratch — a couch, a TV, a laptop, a phone, a bed, a closet of clothes clears $15–20k fast. Now compare that to ~$168/year. A single theft or kitchen fire pays for decades of premiums. Liability is the real sleeper: one injured guest or dog-bite claim can run tens of thousands, which is exactly what the policy caps.</p>"),
  ("When it's required","<p>No state mandates renters insurance, but <strong>most landlords now require it</strong> in the lease — typically $100,000 of liability and proof before move-in. Even when it's optional, the cost is low enough that skipping it rarely makes sense.</p>"),
  ("The few times it's marginal","<p>If you own almost nothing and live with no liability exposure, the property piece matters less — but the liability and loss-of-use coverage still do. For nearly everyone, the honest answer is yes. The only real decision is which carrier; prices for identical coverage vary widely, so compare for your ZIP.</p>"),
 ],
 callout="<strong>Bottom line:</strong> at ~$14/month, renters insurance is rarely the wrong call. Spend your energy on finding the cheapest policy, not on whether to buy one.",
 faq=[
  ("How much does renters insurance cost?","About $168/year nationally — roughly $14/month — for ~$30,000 in personal property and $100,000 in liability. It ranges from ~$127 in low-cost states to over $250 in Florida and Louisiana."),
  ("Is renters insurance required?","Not by law, but most landlords require it in the lease (usually $100,000 liability). Even when optional, it's inexpensive enough that most renters benefit."),
  ("What does renters insurance actually cover?","Personal property, personal liability, and loss of use (temporary living costs). It does not cover flood, earthquake, your car, or a roommate's belongings."),
  ("Is renters insurance worth it for one person?","Usually yes — the liability and loss-of-use protection apply regardless of how much you own, and the cost is only a few dollars a month."),
 ],
 cross=("/renters/coverage.html","Renters Coverage Calculator")),

"what-does-renters-insurance-cover": dict(
 title="What Does Renters Insurance Cover? (2026)",
 h1="What renters insurance covers — and what it doesn't.",
 dek="It covers your stuff, your liability, and your living costs if you're displaced. It does not cover floods, your car, or your roommate's things. Here's the full picture.",
 kicker="Renters Basics",
 lead="<p>A standard renters policy (an HO-4) has four parts. Knowing what each does — and the big exclusions — is the difference between a smooth claim and an unpleasant surprise.</p>",
 sections=[
  ("Personal property (Coverage C)","<p>Replaces your belongings when they're stolen or destroyed by a covered peril: fire, theft, vandalism, windstorm, and most water damage from plumbing (a burst pipe). It follows you off-premises too — a bike stolen from a rack, a laptop taken from your car or a hotel. Choose <strong>replacement cost</strong> coverage so you're paid to buy new, not the depreciated value.</p>"),
  ("Personal liability (Coverage E)","<p>Covers you when someone is hurt in your unit or you damage someone else's property — a guest's fall, a dog bite, a tub that overflows into the apartment below. It pays their costs <em>and</em> your legal defense, typically up to $100,000–$300,000.</p>"),
  ("Loss of use (Coverage D)","<p>If a covered loss makes your place unlivable, this pays for a hotel, restaurant meals above your normal grocery bill, and other extra costs while you're displaced.</p>"),
  ("Medical payments (Coverage F)","<p>Pays small medical bills for a guest hurt in your home, regardless of fault — usually $1,000–$5,000 — without anyone filing a liability claim.</p>"),
  ("What renters insurance does NOT cover","<p>The big exclusions: <strong>flood</strong> and <strong>earthquake</strong> (separate policies), <strong>your car</strong> and its theft (that's auto comprehensive — though stuff stolen <em>from</em> the car is covered by renters), your <strong>roommate's belongings</strong> (they need their own policy), <strong>pests and bedbugs</strong>, and value above category <strong>sublimits</strong> (jewelry, watches, cameras are often capped at $1,000–$2,500 unless you schedule them).</p>"),
 ],
 callout="<strong>Two things to get right:</strong> pick replacement-cost (not actual-cash-value) coverage, and schedule any high-value items (a ring, a camera kit) that exceed the standard category caps. The coverage calculator walks you through both.",
 faq=[
  ("What does renters insurance cover?","Personal property (theft, fire, most water damage, off-premises), personal liability, loss of use (temporary living costs), and medical payments for guests."),
  ("What does renters insurance not cover?","Flood, earthquake, your car, your roommate's belongings, pests/bedbugs, and value above category sublimits for items like jewelry unless scheduled."),
  ("Does renters insurance cover my stuff outside my home?","Yes — personal property coverage follows you, so items stolen from your car, a hotel, or while traveling are typically covered (subject to your deductible and limits)."),
  ("Does replacement cost matter?","Yes. Replacement-cost coverage pays to buy items new; actual-cash-value pays the depreciated amount. The upgrade is usually small and worth it."),
 ],
 cross=("/renters/coverage.html","Renters Coverage Calculator")),

"does-renters-insurance-cover": dict(
 title="Does Renters Insurance Cover That? (Water Damage, Theft, Dogs &amp; More)",
 h1="Does renters insurance cover that? The common questions.",
 dek="Water damage, theft, your dog, a roommate's stuff, a car break-in, moving — quick, honest answers to the scenarios renters actually search for.",
 kicker="Renters Basics",
 lead="<p>Most 'does it cover…' questions come down to two things: was it a <em>covered peril</em>, and which coverage applies. Here are the ones renters ask most.</p>",
 sections=[
  ("Water damage","<p><strong>Sometimes.</strong> Sudden, accidental water from inside — a burst pipe, an overflowing appliance, a leak from the unit above — is covered. <strong>Flood</strong> (rising water from outside) is <em>not</em> — that needs a separate flood policy. Sewer/drain backup is often excluded unless you add an endorsement.</p>"),
  ("Theft","<p><strong>Yes</strong> — theft of your belongings is covered, including off-premises (your car, a hotel, the gym) and break-ins. You'll pay your deductible, and high-value categories like jewelry may be capped unless scheduled.</p>"),
  ("Your dog (and dog bites)","<p><strong>Usually</strong> — your liability coverage handles a dog-bite claim. But many insurers exclude certain breeds or a dog with a bite history, so disclose your pet. Damage your dog does to your <em>own</em> apartment isn't covered.</p>"),
  ("A roommate's belongings","<p><strong>No.</strong> A standard policy covers only the named policyholder (and usually family). Roommates need their own renters policies — you generally can't (and shouldn't) cover them on yours.</p>"),
  ("A car break-in","<p><strong>Split.</strong> Items stolen <em>from</em> your car (a laptop, headphones) are covered by your <strong>renters</strong> policy. Damage to the car itself or theft of the car is your <strong>auto</strong> comprehensive coverage, not renters.</p>"),
  ("Moving and storage","<p><strong>Partially.</strong> Your belongings are typically covered while in a storage unit (often at a reduced limit), and during a move for covered perils — but not for damage caused by the movers (that's the mover's liability) or simple breakage in transit. Check your policy's off-premises limit.</p>"),
 ],
 callout="<strong>The pattern:</strong> renters insurance covers sudden, accidental loss of <em>your</em> property and your liability — not floods, not your car, not your roommate, not pests. When in doubt, the coverage calculator shows exactly what your limits protect.",
 faq=[
  ("Does renters insurance cover water damage?","Sudden internal water (burst pipe, overflow, leak from above) yes; flood (rising water) no — that needs separate flood insurance. Sewer backup often needs an endorsement."),
  ("Does renters insurance cover theft?","Yes, including off-premises theft and break-ins, subject to your deductible. Jewelry and other high-value items may be capped unless scheduled."),
  ("Does renters insurance cover dog bites?","Usually, under personal liability — but some insurers exclude certain breeds or dogs with a bite history, so always disclose your pet."),
  ("Does renters insurance cover my roommate?","No. Each renter needs their own policy; a standard policy covers only the named policyholder and family members."),
 ],
 cross=("/renters/coverage.html","Renters Coverage Calculator")),
}

def build(slug, c):
    url=f"https://boringrate.com/renters/{slug}.html"
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
<div class="zip-bar-slogan"><strong>Boring Research.</strong> Easy Decision. &mdash; Enter your ZIP to compare <em>renters</em> rates.</div>
<form class="zip-bar-form" id="zipBarForm" autocomplete="off"><input class="zip-bar-input" id="zipBarInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="zip-bar-btn">Compare &rarr;</button></form>
</div></div></div>'''
    body=f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/renters/index.html">Renters Insurance</a> &nbsp;·&nbsp; {c["kicker"]} &nbsp;·&nbsp; 4 min read</div>
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

import os
n=0
for slug,c in ARTICLES.items():
    open(f"renters/{slug}.html","w",encoding="utf-8").write(build(slug,c)); n+=1
    print("wrote renters/"+slug+".html")
print("done",n)
