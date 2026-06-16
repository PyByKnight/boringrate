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
