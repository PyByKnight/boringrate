#!/usr/bin/env python3
# Build tool-driving FAQ articles (informational, funnel to the ZIP tool). Reuses the
# auto article scaffold + the two-tile CTA. Config-driven so more FAQ pages are easy.
import re, json

scaff = open("article/state/texas.html", encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>")+len("</style>")]
NAV   = scaff[scaff.index('<header class="top">'):scaff.index("</header>")+len("</header>")]
TAIL  = scaff[scaff.index("<footer>"):]
TAIL  = re.sub(r'Compare [A-Za-z ]+ rates <span class="ascta-arrow">', 'Compare rates <span class="ascta-arrow">', TAIL)

CTA = ('<div class="tooltiles">'
 '<div class="tile"><div class="tile-kicker">Compare rates</div>'
 '<div class="tile-name">See your cheapest carrier for your ZIP</div>'
 '<div class="tile-desc">Rank every carrier by estimated price for your exact ZIP and profile &mdash; in seconds, no calls.</div>'
 '<form class="tile-zipform" onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z)){location.href=\'/?zip=\'+z}else{this.zc.focus()}"><input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="tile-zip-btn">Compare &rarr;</button></form>'
 '</div>'
 '<div class="tile"><div class="tile-kicker">Coverage calculator</div>'
 '<div class="tile-name">Not sure how much you need?</div>'
 '<div class="tile-desc">See what to buy and what to skip &mdash; and how each choice changes your price.</div>'
 '<a class="tbtn secondary" href="/coverage.html">Help me choose my coverage options &rarr;</a>'
 '</div></div>')

def esc(s): return s.replace('"', "&quot;")

ARTICLES = {
"how-to-switch-car-insurance": dict(
 title="How to Switch Car Insurance (2026): Step-by-Step",
 h1="How to switch car insurance — without a coverage gap.",
 dek="It's faster than people think, you can do it any time (not just at renewal), and you get a refund for the unused part of your old policy. Here's the 5-step way to do it right.",
 kicker="Shopping &amp; Saving",
 lead="<p>Switching car insurance is one of the highest-value 20-minute tasks in personal finance — the gap between the cheapest and priciest carrier for the same driver is roughly <strong>$550 a year</strong>. You don't have to wait for your renewal date, there's rarely a real penalty for leaving mid-policy, and the one rule that matters is simple: <strong>never cancel the old policy before the new one is active.</strong></p>",
 sections=[
  ("Step 1 — Compare quotes for the same coverage","<p>Get quotes from at least three carriers using <em>identical</em> coverage limits and deductibles, or you're comparing apples to oranges. Enter your ZIP below and we'll rank carriers for your exact profile in about two minutes — no phone calls, no selling your info.</p>"),
  ("Step 2 — Buy the new policy first","<p>Once you've picked a winner, <strong>start the new policy before you cancel the old one</strong>. Set the new policy's start date to the day you want coverage to switch. This guarantees zero gap — even one day of lapse can raise your future rates and, in some states, your license status.</p>"),
  ("Step 3 — Cancel the old policy","<p>Call or log in to your old carrier and request cancellation effective the new policy's start date. Ask for a <strong>prorated refund</strong> of the unused premium — you're entitled to it. Most carriers refund automatically; a few charge a small short-rate fee, but it's almost always far less than your savings.</p>"),
  ("Step 4 — Send proof to your lender (if financed)","<p>If you lease or have a loan, your lienholder requires continuous coverage. Send them the new policy's declarations page so they don't force-place expensive coverage on you.</p>"),
  ("Step 5 — Confirm no lapse, then set a reminder","<p>Check that the old policy shows canceled and the new one shows active with no gap between them. Then set a calendar reminder to re-compare in 6–12 months — that habit, not loyalty, is what keeps your rate low.</p>"),
 ],
 callout="<strong>The one mistake to avoid:</strong> canceling your old policy before the new one starts. A lapse — even a day — is exactly what makes future premiums jump. Overlap is fine; a gap is costly.",
 faq=[
  ("Can I switch car insurance any time, or only at renewal?","You can switch any time. Policies are month-to-month in practice — you are not locked in until renewal, and you'll get a prorated refund for the unused portion."),
  ("Will I get money back if I cancel mid-policy?","Yes. You're refunded the unused premium. Most carriers prorate it; a few apply a small short-rate fee, but it's usually minor compared to the savings."),
  ("Does switching car insurance hurt your credit?","No. Insurance quotes use a soft inquiry, which doesn't affect your credit score, and switching carriers has no credit impact."),
  ("Does switching raise my rates later?","No — switching itself doesn't. A coverage <em>lapse</em> does, which is why you always start the new policy before canceling the old one."),
 ],
 cross=("/article/cost-of-not-shopping-car-insurance.html","The Hidden Cost of Not Shopping")),

"does-car-insurance-follow-the-car-or-driver": dict(
 title="Does Car Insurance Follow the Car or the Driver? (2026)",
 h1="Does car insurance follow the car or the driver?",
 dek="Short answer: mostly the car. So if you lend your car to a licensed friend, your policy usually covers them. But there are real exceptions worth knowing before you hand over the keys.",
 kicker="Coverage Basics",
 lead="<p>In the U.S., car insurance <strong>primarily follows the car, not the driver</strong>. Your policy is what responds first when your vehicle is in an accident — even if someone else was driving it with your permission. That's called <em>permissive use</em>. But coverage can also follow <em>you</em> in certain situations, and there are exclusions that surprise people. Here's how it actually works.</p>",
 sections=[
  ("Lending your car: permissive use","<p>If a licensed friend or family member borrows your car with your permission and crashes, <strong>your</strong> policy is generally primary — your liability and collision/comprehensive respond first, and a claim goes on <em>your</em> record. If the damage exceeds your limits, the driver's own policy may kick in as secondary. Bottom line: when you lend your car, you're lending your insurance.</p>"),
  ("When coverage follows you (the driver)","<p>Your liability coverage can follow you into a car you don't own — for example, when you rent a car or occasionally drive someone else's vehicle. It's usually <strong>secondary</strong> there (the car owner's policy pays first). People who don't own a car but still drive can buy a <strong>non-owner policy</strong> to carry their own liability coverage with them.</p>"),
  ("The exclusions that catch people","<p>Coverage can disappear in these cases: a driver you've formally <strong>excluded</strong> from your policy; a <strong>household member</strong> (roommate, partner, adult child) who drives your car regularly but isn't listed; using your personal car for <strong>business or delivery/rideshare</strong> without the right endorsement; or someone driving <strong>without your permission</strong>. List everyone in your household who drives your car — leaving a regular driver off can void a claim.</p>"),
 ],
 callout="<strong>Why this affects your rate:</strong> insurers price your policy on <em>everyone</em> who regularly drives your car, not just you. Adding a teen or a high-risk household driver changes your premium — which is exactly why comparing carriers with your real household profile matters.",
 faq=[
  ("Can someone else drive my car with my insurance?","Yes — a licensed driver using your car with your permission is generally covered by your policy (permissive use). Your coverage is primary and any claim goes on your record."),
  ("Am I covered driving someone else's car?","Usually yes, as secondary coverage — the car owner's policy pays first, and yours can cover amounts beyond their limits. If you don't own a car, a non-owner policy gives you your own liability coverage."),
  ("Does my car insurance cover a rental car?","Often, yes — your existing liability typically extends to a rental, and if you carry collision/comprehensive it usually does too. Check your limits before declining the rental counter's coverage."),
  ("Do I have to list everyone in my household?","Yes. Insurers expect all regular drivers in your household to be listed. Leaving off a regular driver to lower your rate can get a claim denied."),
 ],
 cross=("/coverage.html","Coverage Calculator")),

"how-long-does-an-accident-stay-on-your-insurance": dict(
 title="How Long Does an Accident, Ticket, or DUI Stay on Your Insurance? (2026)",
 h1="How long do accidents, tickets, and DUIs follow your insurance?",
 dek="Most surcharges fade after 3 years — but a DUI can haunt your rate for up to 10. Here's the timeline for each, and the move that saves you money: re-shopping the moment it drops off.",
 kicker="Rates &amp; Records",
 lead="<p>Insurers price your premium on a <strong>look-back period</strong> — a window of recent driving history. Once an incident ages past that window, its surcharge disappears and your rate should fall. The catch: <strong>your carrier won't always drop it automatically or competitively</strong>, which is exactly why the smart move is to re-compare carriers the moment something falls off your record.</p>",
 sections=[
  ("The timeline, by incident","<p>How long each typically affects your insurance rate (the surcharge window, which differs from how long it stays on your DMV record):</p>"
   "<table style=\"width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:660px;\">"
   "<thead><tr style=\"text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;\"><th style=\"padding:8px 6px;\">Incident</th><th style=\"padding:8px 6px;\">Typical rate impact</th></tr></thead>"
   "<tbody>"
   "<tr style=\"border-bottom:1px solid var(--rule);\"><td style=\"padding:8px 6px;\">At-fault accident</td><td style=\"padding:8px 6px;\">3–5 years</td></tr>"
   "<tr style=\"border-bottom:1px solid var(--rule);\"><td style=\"padding:8px 6px;\">Speeding / minor ticket</td><td style=\"padding:8px 6px;\">~3 years</td></tr>"
   "<tr style=\"border-bottom:1px solid var(--rule);\"><td style=\"padding:8px 6px;\">DUI / major violation</td><td style=\"padding:8px 6px;\">3–10 years (varies widely by state)</td></tr>"
   "<tr style=\"border-bottom:1px solid var(--rule);\"><td style=\"padding:8px 6px;\">Comprehensive claim (theft, weather)</td><td style=\"padding:8px 6px;\">Usually little to none</td></tr>"
   "<tr style=\"border-bottom:1px solid var(--rule);\"><td style=\"padding:8px 6px;\">Coverage lapse</td><td style=\"padding:8px 6px;\">~6 months–1 year, but can be steep</td></tr>"
   "</tbody></table>"
   "<p>Exact windows vary by carrier and state — California, for example, surcharges accidents for ~3 years, while a DUI can affect rates for 10. The point is that none of it is permanent.</p>"),
  ("Why your rate doesn't always drop on its own","<p>When an incident ages out, your premium <em>should</em> fall — but carriers don't compete for their existing customers. The surcharge may come off while other quiet renewal increases stay. The only way to capture the drop is to <strong>get fresh quotes</strong> right after the anniversary when the incident falls outside the look-back window.</p>"),
  ("Cheaper options while it's still on your record","<p>Even during the surcharge period, carriers weigh incidents very differently — the cheapest carrier after an accident or DUI can be hundreds less than the priciest. See our rankings for <a class=\"ca-link\" href=\"/article/cheapest-car-insurance-after-accident.html\">cheapest after an accident</a> and <a class=\"ca-link\" href=\"/article/cheapest-car-insurance-after-dui.html\">cheapest after a DUI / SR-22</a>, or enter your ZIP below to compare for your exact situation.</p>"),
 ],
 callout="<strong>The money move:</strong> set a reminder for the 3-year mark after any incident. The day it ages out of the look-back window, re-compare carriers — that's when switching often unlocks a real drop your current insurer won't volunteer.",
 faq=[
  ("How long does an at-fault accident raise your insurance?","Typically 3–5 years, depending on your carrier and state. After that the surcharge should come off — re-shop to make sure you're getting the lower rate."),
  ("How long does a DUI affect car insurance?","Commonly 3–10 years depending on the state — far longer than most violations, and it usually moves you to the non-standard market with an SR-22 requirement for ~3 years."),
  ("How long do speeding tickets affect insurance?","Most minor violations affect your rate for about 3 years, then drop off the look-back window insurers use for pricing."),
  ("Will my rate automatically go down when it falls off?","Not always competitively. Carriers rarely lower a loyal customer's rate on their own — comparing quotes when the incident ages out is how you actually capture the savings."),
 ],
 cross=("/article/cheapest-car-insurance-after-accident.html","Cheapest Car Insurance After an Accident")),

"does-car-insurance-cover": dict(
 title="What Does Car Insurance Actually Cover? (Rentals, Deer, Theft &amp; More)",
 h1="Does car insurance cover that? The common scenarios.",
 dek="Rental cars, hitting a deer, theft, a friend borrowing your car, weather damage — what's covered depends on which coverages you carry. Here's the plain-English breakdown.",
 kicker="Coverage Basics",
 lead="<p>Whether something is covered comes down to which of three coverages you carry: <strong>liability</strong> (damage you cause to others), <strong>collision</strong> (your car in a crash), and <strong>comprehensive</strong> (your car from non-crash events — theft, weather, animals). 'Full coverage' just means you carry all three. Here's how that plays out in the situations people actually search for.</p>",
 sections=[
  ("Hitting a deer or animal","<p>Covered by <strong>comprehensive</strong>, not collision — animal strikes are treated as an unavoidable event. You'll pay your comprehensive deductible. If you only carry liability, it's not covered.</p>"),
  ("A rental car","<p>Your <strong>liability</strong> typically extends to a rental, and if you carry collision and comprehensive, those usually do too — so you can often decline the rental counter's pricey coverage. Confirm your limits first, and note this applies to personal rentals, not business use.</p>"),
  ("Someone else driving your car","<p>Generally covered — car insurance follows the car, so a licensed friend driving with your permission is covered by <em>your</em> policy. See <a class=\"ca-link\" href=\"/article/does-car-insurance-follow-the-car-or-driver.html\">does insurance follow the car or the driver</a> for the exceptions (excluded and unlisted drivers).</p>"),
  ("Theft and vandalism","<p>Covered by <strong>comprehensive</strong> — theft of the vehicle, broken windows, and vandalism. Personal belongings stolen <em>from</em> the car are not covered by auto insurance; that's a renters or homeowners claim.</p>"),
  ("Weather, floods, and falling trees","<p><strong>Comprehensive</strong> covers hail, flood, fire, falling trees, and storm damage to your car — yes, including flood (unlike a home policy, where flood is separate). Without comprehensive, weather damage is on you.</p>"),
  ("Your own injuries","<p>Covered by <strong>medical payments (MedPay)</strong> or <strong>personal injury protection (PIP)</strong> in no-fault states — not by liability, which only pays for the <em>other</em> party. If the other driver is at fault and uninsured, <strong>uninsured-motorist</strong> coverage steps in.</p>"),
  ("What car insurance never covers","<p>Mechanical breakdown and normal wear, intentional damage, using your personal car for delivery/rideshare without an endorsement, and personal items inside the car. Those need other products (warranty, rideshare endorsement, renters/home insurance).</p>"),
 ],
 callout="<strong>The takeaway:</strong> most 'is this covered?' answers come down to whether you carry comprehensive and collision on top of liability. Use the coverage calculator to see exactly what to carry — and skip — for your situation.",
 faq=[
  ("Does car insurance cover hitting a deer?","Yes, under comprehensive coverage (minus your deductible). It's not covered if you only carry liability."),
  ("Does my car insurance cover a rental car?","Usually — your liability extends to rentals, and collision/comprehensive carry over if you have them. Check your limits before paying for the rental company's coverage."),
  ("Does car insurance cover theft?","Comprehensive covers theft of the vehicle and vandalism. Items stolen from inside the car fall under renters or homeowners insurance, not auto."),
  ("Does car insurance cover flood or weather damage?","Yes — comprehensive covers flood, hail, fire, and storm damage to your vehicle. (Home insurance, by contrast, excludes flood.)"),
 ],
 cross=("/coverage.html","Coverage Calculator")),

"driving-without-car-insurance": dict(
 title="What Happens If You Drive Without Car Insurance? (2026)",
 h1="What happens if you drive without car insurance?",
 dek="It's illegal in 48 states, and the penalties stack fast: fines, a suspended license and registration, an SR-22 requirement, and full personal liability for any crash. Here's the real cost — and the cheap fix.",
 kicker="Requirements",
 lead="<p>Every state except New Hampshire (and, loosely, Virginia) requires car insurance or proof of financial responsibility. Driving without it isn't a gray area — it triggers escalating penalties, and a single at-fault accident while uninsured can be financially ruinous. The good news: getting at least minimum coverage is fast and cheap relative to the risk.</p>",
 sections=[
  ("The immediate penalties","<p>Get caught driving uninsured and you can face <strong>fines</strong> (from ~$150 to over $1,500 for repeat offenses), <strong>license and registration suspension</strong>, reinstatement fees, and in many states an <strong>SR-22 filing</strong> requirement for ~3 years afterward. Some states impound the vehicle. Penalties escalate sharply on a second offense.</p>"),
  ("The real risk: an at-fault accident","<p>The penalties are minor next to this: if you cause a crash while uninsured, <strong>you pay for everything out of pocket</strong> — the other party's car, medical bills, and any lawsuit. That can mean wage garnishment and liens for years. Liability coverage exists precisely to cap that exposure.</p>"),
  ("The hidden cost: higher rates later","<p>A coverage lapse follows you. When you do buy insurance, carriers surcharge a recent gap — sometimes for a year or more — so going uninsured to 'save' money usually costs more once you're insured again. See <a class=\"ca-link\" href=\"/article/cost-of-not-shopping-car-insurance.html\">the hidden cost of not shopping</a> for how lapses and loyalty quietly inflate premiums.</p>"),
  ("The fix is cheaper than the fine","<p>Minimum-liability coverage is the cheapest policy you can buy, and it's almost always less than a single uninsured-driving fine — let alone an at-fault accident. Enter your ZIP below to see the lowest-priced carriers in your area, including the non-standard insurers that specialize in drivers reinstating after a lapse.</p>"),
 ],
 callout="<strong>Bottom line:</strong> the fine is the small risk; an uninsured at-fault accident is the one that wrecks finances. Even state-minimum liability caps that exposure for a few dollars a month — compare carriers and get covered before you drive.",
 faq=[
  ("Is it illegal to drive without car insurance?","Yes, in 48 states. New Hampshire and Virginia are partial exceptions, but you're still personally liable for any damage you cause, so coverage is strongly advised everywhere."),
  ("What happens if you get caught driving without insurance?","Expect fines, possible license and registration suspension, reinstatement fees, and often an SR-22 requirement for about 3 years. Penalties increase for repeat offenses."),
  ("Will driving uninsured raise my rates?","Yes. A coverage lapse is a surcharge factor when you buy insurance again, often for a year or more — so a gap usually costs more than it 'saves.'"),
  ("What's the cheapest way to get legal again?","Minimum-liability coverage is the lowest-cost policy. Compare carriers (including non-standard insurers for post-lapse drivers) to find the cheapest — it's almost always less than the fine."),
 ],
 cross=("/article/sr22-insurance.html","SR-22 Insurance Explained")),
}

def build(slug, c):
    url=f"https://boringrate.com/article/{slug}.html"
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
<div class="zip-bar-slogan"><strong>Boring Research.</strong> Easy Decision. &mdash; Enter your ZIP to compare rates.</div>
<form class="zip-bar-form" id="zipBarForm" autocomplete="off"><input class="zip-bar-input" id="zipBarInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="zip-bar-btn">Compare &rarr;</button></form>
</div></div></div>'''
    body=f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/">← BoringRate</a> &nbsp;·&nbsp; {c["kicker"]} &nbsp;·&nbsp; 4 min read</div>
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
    open(f"article/{slug}.html","w",encoding="utf-8").write(build(slug,c)); n+=1
    print("wrote article/"+slug+".html")
print("done",n)
