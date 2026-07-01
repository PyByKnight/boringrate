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
  ("Personal property (Coverage C)","<p>Replaces your belongings when they're stolen or destroyed by a covered peril: fire, theft, vandalism, windstorm, and most <a class=\"ca-link\" href=\"/renters/does-renters-insurance-cover-water-damage.html\">water damage from plumbing</a> (a burst pipe). It follows you off-premises too — a bike stolen from a rack, a laptop taken from your car or a hotel. Choose <strong>replacement cost</strong> coverage so you're paid to buy new, not the depreciated value.</p>"),
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
  ("Water damage","<p><strong>Sometimes.</strong> Sudden, accidental water from inside — a burst pipe, an overflowing appliance, a leak from the unit above — is covered. <strong>Flood</strong> (rising water from outside) is <em>not</em> — that needs a separate flood policy. Sewer/drain backup is often excluded unless you add an endorsement. <a class=\"ca-link\" href=\"/renters/does-renters-insurance-cover-water-damage.html\">Full guide: does renters insurance cover water damage? &rarr;</a></p>"),
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

"is-renters-insurance-required": dict(
 title="Is Renters Insurance Required? (2026)",
 h1="Is renters insurance required?",
 dek="Not by any state law — but your landlord almost certainly requires it in the lease, and there are good reasons to carry it even when no one's making you.",
 kicker="Renters Basics",
 lead="<p>No U.S. state legally requires renters insurance. But that's not the whole story: <strong>landlords can require it as a condition of your lease, and most now do</strong> — typically $100,000 in liability, with proof before you get the keys.</p>",
 sections=[
  ("Why landlords require it","<p>Your landlord's policy covers the <em>building</em>, not your belongings or your liability. Requiring renters insurance shifts responsibility for tenant-caused damage and injuries onto your policy — and protects them from being dragged into your claims. Larger and professionally managed buildings almost always require it; smaller landlords increasingly do too.</p>"),
  ("What the lease usually asks for","<p>Commonly <strong>$100,000 in personal liability</strong> (sometimes $300,000), proof of coverage before move-in, and occasionally that the landlord be named as an 'interested party' so they're notified if your policy lapses. Read the lease — some specify minimum limits.</p>"),
  ("What happens if you don't carry it","<p>If your lease requires it and you let it lapse, you're in <strong>breach of the lease</strong> — grounds for penalties or, in the worst case, eviction. Even without a requirement, going without means a fire, theft, or liability claim comes entirely out of your pocket.</p>"),
  ("Should you carry it anyway?","<p>Almost always yes. At ~$14/month it covers your belongings, your liability, and temporary living costs. The only real question is which carrier is cheapest for you — enter your ZIP to compare.</p>"),
 ],
 callout="<strong>Bottom line:</strong> it's not required by law, but it's required by most leases — and worth carrying regardless. Compare carriers so you meet the requirement at the lowest price.",
 faq=[
  ("Is renters insurance required by law?","No state legally requires it. However, landlords can and usually do require it in the lease, typically $100,000 in liability."),
  ("Can a landlord require renters insurance?","Yes. It's a legal lease condition, and most landlords require proof of coverage before move-in."),
  ("What happens if I don't have required renters insurance?","If your lease requires it and you don't maintain it, you're in breach of the lease — which can lead to penalties or eviction."),
  ("How much liability coverage do landlords require?","Usually $100,000, sometimes $300,000. Check your lease for the exact minimum."),
 ],
 cross=("/renters/coverage.html","Renters Coverage Calculator")),

"how-much-renters-insurance-do-i-need": dict(
 title="How Much Renters Insurance Do You Need? (2026)",
 h1="How much renters insurance do you actually need?",
 dek="Set your personal property to what it costs to re-buy everything, your liability to at least your net worth, and add replacement cost. Here's how to land on the right numbers.",
 kicker="Renters Basics",
 lead="<p>Renters insurance has a few dials, and most people set them by guessing. The right amounts aren't hard to figure out — and our <a class=\"ca-link\" href=\"/renters/coverage.html\">coverage calculator</a> does the math for you in two minutes. Here's the logic behind it.</p>",
 sections=[
  ("Personal property: what it costs to re-buy everything","<p>Walk room by room and total the <strong>replacement cost</strong> of your belongings — furniture, electronics, clothes, kitchenware. Most renters land between $20,000 and $50,000, and most <em>under</em>-estimate. Set Coverage C to that number, and choose <strong>replacement cost</strong> (not actual cash value) so you're paid to buy new.</p>"),
  ("Liability: at least your net worth","<p>Carry liability at least equal to what you'd want protected if you were sued — $100,000 is the practical floor, and $300,000 costs only a little more. If you have real savings, a $1–2M umbrella policy stacks cheaply on top.</p>"),
  ("Loss of use and medical payments","<p>Loss of use is usually bundled at 20–40% of your property coverage — just confirm it's there. Medical payments ($1,000–$5,000) covers minor guest injuries without a liability claim; bump it to $5,000 for a few dollars.</p>"),
  ("High-value items: schedule them","<p>Standard policies cap categories like jewelry, watches, cameras, and bikes (often $1,000–$2,500 total). If you own something valuable, add a <strong>scheduled endorsement</strong> for it — appraised value, usually no deductible.</p>"),
 ],
 callout="<strong>Fastest path:</strong> the renters coverage calculator turns your stuff, assets, and deductible into the right Coverage C / liability / add-ons — then sends you straight to compare carriers for that coverage.",
 faq=[
  ("How much personal property coverage do I need?","Enough to re-buy everything you own new — usually $20,000–$50,000 for most renters. Do a quick room-by-room total and choose replacement-cost coverage."),
  ("How much liability coverage do I need for renters insurance?","At least $100,000, with $300,000 only slightly more. Carry at least as much as your net worth; add an umbrella policy if you have significant assets."),
  ("Is $100,000 of renters liability enough?","For most renters, yes. If you have substantial savings or assets, step up to $300,000 or add an umbrella policy."),
  ("Do I need replacement cost coverage?","Yes — it pays to buy items new instead of their depreciated value, usually for only a small premium increase."),
 ],
 cross=("/renters/coverage.html","Renters Coverage Calculator")),

"does-renters-insurance-cover-water-damage": dict(
 title="Does Renters Insurance Cover Water Damage? Leaks, Burst Pipes &amp; Floods (2026)",
 h1="Does renters insurance cover water damage? Usually — but not floods or slow leaks.",
 dek="Sudden, accidental water — a burst pipe, an overflowing appliance, a leak from the unit above — is covered. Flood, gradual leaks, and neglect are not. Here's the full breakdown, plus what to do when water hits your stuff.",
 kicker="Renters Basics",
 read="6",
 lead="<p>Water is the messiest question in renters insurance because the answer genuinely depends on <em>how</em> the water got to your things. The rule insurers use is simple to say and easy to get wrong: <strong>sudden and accidental is covered; gradual or preventable is not, and flood is its own separate policy.</strong> Below is exactly where the line falls, the scenarios renters ask about most, and what to do in the first hour after a leak.</p>",
 sections=[
  ("The short answer","<p><strong>Yes — for sudden, accidental water damage to your belongings.</strong> If a pipe bursts, a dishwasher overflows, or the unit above you leaks into yours, your renters policy replaces your damaged property (minus your deductible). What it will <em>not</em> pay for: <strong>flood</strong> (water that rises from outside), a <strong>slow leak</strong> you could have caught, damage from <strong>neglect</strong>, and <strong>sewer or drain backup</strong> unless you've added an endorsement. Everything below is just detail on those two lists.</p>"),
  ("Water damage that IS covered","<p>These are all treated as sudden, accidental discharge and are covered for your belongings under personal property (Coverage C):</p><ul><li><strong>A burst or frozen pipe</strong> that lets go and soaks your things.</li><li><strong>An overflowing appliance</strong> — washing machine, dishwasher, water heater, or a toilet that overflows.</li><li><strong>A leak from the unit above you</strong> — the neighbor's overflow or burst pipe that comes through your ceiling.</li><li><strong>Rain or snow that enters through storm damage</strong> — a roof or window opened up by wind or hail, then water gets in.</li><li><strong>Accidental discharge</strong> from plumbing, HVAC, or a fire-sprinkler system.</li><li><strong>Water used to put out a fire.</strong></li></ul><p>In each case the policy pays to repair or replace <em>your</em> ruined items — carpet you own, furniture, electronics, clothes — at <strong>replacement cost</strong> if you carry that upgrade (worth it; it pays to re-buy new instead of the depreciated value).</p>"),
  ("Water damage that is NOT covered","<p>These are the common denials. Most trace back to \"gradual,\" \"preventable,\" or \"came from outside\":</p><ul><li><strong>Flood</strong> — rising water from outside: storm surge, an overflowing river, or heavy rain that pools up from the ground. This needs a separate <strong>flood policy</strong> (NFIP or private); it is never part of a standard renters policy.</li><li><strong>Sewer or drain backup</strong> and sump-pump failure — excluded by default. A cheap <strong>water-backup endorsement</strong> adds it.</li><li><strong>Gradual leaks and seepage</strong> — a slow drip under the sink you ignored for weeks is \"maintenance,\" not a sudden loss.</li><li><strong>Neglect and wear</strong> — anything the insurer decides you could reasonably have prevented.</li><li><strong>Mold</strong> — usually excluded or tightly capped, especially when it grew from an uncovered or gradual leak.</li><li><strong>The source itself</strong> — the broken pipe, the failed water heater, the building's structure. That's the landlord's problem (or the appliance owner's), not a claim on your belongings.</li></ul>"),
  ("The confusing ones renters actually ask","<p><strong>A leak from the apartment above.</strong> Your renters policy pays for <em>your</em> damaged belongings, minus your deductible — file with your own insurer first. The <em>source</em> and the building repairs are the upstairs neighbor's or the landlord's responsibility; your insurer may pursue them to recover your deductible.</p><p><strong>\"Water leak\" vs \"flood.\"</strong> The label decides everything. Water reaching your stuff from <em>inside</em> the building (pipes, appliances, the ceiling) is covered. Water that rose from the <em>ground or outside</em> is a flood — not covered without flood insurance — no matter how it's described.</p><p><strong>Carpet and ceiling damage.</strong> Carpet and belongings that are <em>yours</em>, ruined by a covered water event, are covered. The <strong>ceiling, walls, and floors themselves belong to the building</strong> — that's the landlord's insurance, not your renters policy.</p><p><strong>Damage you cause downstairs.</strong> If your tub or toilet overflows into the unit below, that neighbor's damage is paid by your <strong>personal liability</strong> (Coverage E) — one of the quietly important reasons to carry renters insurance at all. (More on <a class=\"ca-link\" href=\"/renters/is-renters-insurance-worth-it.html\">why renters insurance is worth it</a>.)</p>"),
  ("What to do in the first hour","<p>Your policy expects you to limit further damage — this is a real duty, not a suggestion:</p><ol><li><strong>Stop the source.</strong> Shut the valve or the main; kill power to the area if water is near outlets.</li><li><strong>Move what you can</strong> out of the water and mop up — mitigating further loss protects your claim.</li><li><strong>Document before you clean.</strong> Photos and video of everything wet, wide and close.</li><li><strong>Inventory the damaged items</strong> with rough values and any receipts.</li><li><strong>Notify your insurer and your landlord promptly.</strong> Fast reporting matters.</li><li><strong>Keep receipts</strong> for anything you spend, and <em>don't throw ruined items out</em> until the adjuster signs off.</li></ol>"),
  ("How to cover the gaps","<p>Two inexpensive add-ons close the biggest holes: a <strong>water-backup (sewer/drain) endorsement</strong> for a few dollars a month, and a separate <strong>flood policy</strong> if you're anywhere near flood risk — renters flood is contents-only and cheap. And pick <strong>replacement-cost</strong> coverage so a soaked couch is paid at what a new one costs. The <a class=\"ca-link\" href=\"/renters/coverage.html\">coverage calculator</a> flags which of these you're missing.</p>"),
 ],
 callout="<strong>Bottom line:</strong> sudden and accidental water damage to your belongings is covered; flood, slow leaks, and neglect are not. A water-backup endorsement and a cheap flood policy close the two biggest gaps — and replacement-cost coverage makes the payout actually replace what you lost.",
 faq=[
  ("Does renters insurance cover water damage?","Yes, when it's sudden and accidental — a burst pipe, an overflowing appliance, or a leak from the unit above. It replaces your damaged belongings after your deductible. Flood, gradual leaks, and neglect are not covered."),
  ("Does renters insurance cover water leaks?","A sudden leak — a burst or failed pipe, or a leak from the apartment above — is covered for your belongings. A slow, long-term leak you could have caught is treated as maintenance and is excluded."),
  ("Does renters insurance cover a leak from the apartment above?","Yes. Your policy covers your damaged property, subject to your deductible. The source and the building itself are the upstairs neighbor's or landlord's responsibility, and your insurer may pursue them to recover your deductible."),
  ("Does renters insurance cover water damage to carpet?","If the carpet is yours and it's ruined by a covered water event, yes. Wall-to-wall carpet that belongs to the building is the landlord's insurance, not your renters policy."),
  ("Does renters insurance cover flooding?","No. Flood — rising water from outside — needs a separate flood policy (NFIP or private). Renters flood coverage is contents-only and inexpensive."),
  ("Does renters insurance cover sewer or drain backup?","Not by default. You need a water-backup (sewer/drain) endorsement, which is an inexpensive add-on to a standard renters policy."),
 ],
 cross=("/renters/what-does-renters-insurance-cover.html","What renters insurance covers")),

"how-much-does-renters-insurance-cost": dict(
 title="How Much Does Renters Insurance Cost? (2026)",
 h1="How much does renters insurance cost?",
 dek="About $168 a year nationally — roughly $14 a month — but it ranges from ~$127 to over $250 by state. Here's what drives the price and how to pay less.",
 kicker="Renters Basics",
 lead="<p>Renters insurance is cheap. The national average is around <strong>$168 a year (~$14/month)</strong> for about $30,000 in personal property and $100,000 in liability. Where you land depends mostly on your state, how much you insure, and your deductible.</p>",
 sections=[
  ("What it costs by state","<p>State averages run from roughly <strong>$127</strong> in low-cost states (Maine, New Hampshire, Vermont) to over <strong>$250</strong> in Florida and Louisiana, where catastrophe risk pushes every line of insurance up. See your state's average and the cheapest carriers on our <a class=\"ca-link\" href=\"/renters/index.html\">renters rate comparison</a>.</p>"),
  ("What drives your price","<p>The biggest factors: <strong>your location</strong> (crime and weather risk by ZIP), <strong>how much personal property you insure</strong>, your <strong>deductible</strong> ($250 vs $1,000), whether you pick <strong>replacement cost</strong>, and in most states your <strong>credit-based insurance score</strong>. Add-ons like scheduled jewelry or water-backup raise it slightly.</p>"),
  ("How to pay less","<p><strong>Bundle</strong> with your auto policy (often 10–15% off the renters premium), <strong>raise your deductible</strong> if you can cover it, skip coverage you don't need, and — the big one — <strong>compare carriers</strong>. The same coverage can vary $80–180/year between insurers for the same renter.</p>"),
 ],
 callout="<strong>The cheapest move:</strong> bundling and a higher deductible help, but comparing carriers is where the real spread is. Enter your ZIP to see the lowest-priced renters carriers for your area.",
 faq=[
  ("How much does renters insurance cost per month?","About $14/month on average nationally (~$168/year) for ~$30,000 in property and $100,000 in liability. It ranges from ~$10 to over $20/month by state."),
  ("Why is renters insurance so cheap?","It only covers your belongings and liability — not a building — so the insurer's exposure is small compared to home or auto insurance."),
  ("What's the cheapest way to get renters insurance?","Bundle it with auto, raise your deductible, and compare carriers — the same coverage can vary $80–180/year between companies."),
  ("Does renters insurance cost more in some states?","Yes — from ~$127 in low-risk states to over $250 in Florida and Louisiana, driven by local crime and catastrophe risk."),
 ],
 cross=("/renters/index.html","Renters Rate Comparison")),
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
    <div class="article-kicker"><a href="/renters/index.html">Renters Insurance</a> &nbsp;·&nbsp; {c["kicker"]} &nbsp;·&nbsp; {c.get("read","4")} min read</div>
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
