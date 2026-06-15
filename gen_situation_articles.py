#!/usr/bin/env python3
# Build high-purchase-intent "cheapest car insurance for [situation]" articles.
# Top-3 + bottom-3 are computed from the SAME model the rate tool uses (parsed from
# index.html), so the article ranking and the tool (via ?sit=) line up directionally.
# Each leads with the ranking, then a "you may be overpaying -> shop" bottom-3, a ZIP
# CTA carrying the situation, and genuinely useful guidance.
import re, json, html as _html

NATIONAL = 2568  # national full-coverage average (directional)

src = open("index.html", encoding="utf-8").read()
def grab(name, o, c):
    i = src.index(name); s = src.index(o, i); d = 0; j = s
    for j in range(s, len(src)):
        if src[j] == o: d += 1
        elif src[j] == c:
            d -= 1
            if not d: return src[s:j+1]
    return ""
# parse carriers via JS-ish -> python (quote keys)
def parse_carriers(blockname):
    raw = grab(blockname, "[", "]")
    # keep only name/base/csGrade/tag/bestFor/sens — eval as JS object is hard; use regex per entry
    cars = []
    for m in re.finditer(r'\{\s*name:\s*"([^"]+)",\s*base:\s*([0-9.]+)[^}]*?(?:bestFor:\s*"([^"]*)")?[^}]*?sens:\s*(\{.*?\})\s*\}', raw, re.S):
        name, base, bestFor = m.group(1), float(m.group(2)), m.group(3) or ""
        sensraw = m.group(4)
        sens = {}
        # flat keys
        for k in ["own","rent","youngDriver","telematics","multi","single","lapsed","renewal","accident"]:
            mm = re.search(rf'\b{k}:\s*(-?[0-9.]+)', sensraw)
            if mm: sens[k] = float(mm.group(1))
        # age tiers
        am = re.search(r'age:\s*\{([^}]*)\}', sensraw)
        if am:
            sens["age"] = {a: float(b) for a,b in re.findall(r'"([^"]+)":\s*(-?[0-9.]+)', am.group(1))}
        # credit
        cm = re.search(r'credit:\s*\{([^}]*)\}', sensraw)
        if cm:
            sens["credit"] = {a: float(b) for a,b in re.findall(r'(\w+):\s*(-?[0-9.]+)', cm.group(1))}
        # tag
        tm = re.search(r'tag:\s*"([^"]*)"', m.group(0))
        cars.append({"name":name,"base":base,"bestFor":bestFor,"tag":tm.group(1) if tm else "","sens":sens})
    return cars

STD = parse_carriers("const CARRIERS_STANDARD")
NS  = parse_carriers("const CARRIERS_NONSTANDARD")

def price(car, *factors):
    m = car["base"]
    for f in factors: m *= (1 + f)
    return round((NATIONAL/2) * m)

def age(car, tier): return car["sens"].get("age",{}).get(tier, 0)

def rank_standard(extra):
    # extra(car) -> total fractional adjustment (already summed via repeated *(1+x))
    rows = []
    for c in STD:
        p = c["base"]*(1+age(c,"35-54"))
        for f in extra(c): p *= (1+f)
        rows.append({"name":c["name"],"price":round((NATIONAL/2)*p),"car":c})
    rows.sort(key=lambda r:r["price"]); return rows

def rank_young():
    rows=[]
    for c in STD:
        p=c["base"]*(1+age(c,"18-24"))*(1+c["sens"].get("youngDriver",0))
        rows.append({"name":c["name"],"price":round((NATIONAL/2)*p),"car":c})
    rows.sort(key=lambda r:r["price"]); return rows

def rank_senior():
    rows=[{"name":c["name"],"price":round((NATIONAL/2)*c["base"]*(1+age(c,"55+"))),"car":c} for c in STD]
    rows.sort(key=lambda r:r["price"]); return rows

def rank_credit():
    rows=[{"name":c["name"],"price":round((NATIONAL/2)*c["base"]*(1+age(c,"35-54"))*(1+c["sens"].get("credit",{}).get("fair",0))),"car":c} for c in STD]
    rows.sort(key=lambda r:r["price"]); return rows

def rank_accident():
    rows=[{"name":c["name"],"price":round((NATIONAL/2)*c["base"]*(1+age(c,"35-54"))*(1+c["sens"].get("accident",0))),"car":c} for c in STD]
    rows.sort(key=lambda r:r["price"]); return rows

def rank_dui():
    rows=[{"name":c["name"],"price":round((NATIONAL/2)*c["base"]*(1+age(c,"35-54"))),"car":c} for c in NS]
    rows.sort(key=lambda r:r["price"]); return rows

# carrier slug for "full review" links (only standard national carriers have review pages)
REVIEW={"USAA":"usaa","GEICO":"geico","State Farm":"state-farm","Progressive":"progressive","Allstate":"allstate","Liberty Mutual":"liberty-mutual","Farmers":"farmers","Nationwide":"nationwide","Travelers":"travelers","Safeco":"safeco","The Hartford":"the-hartford","Root Insurance":"root-insurance"}

SIT = {
 "cheapest-car-insurance-young-drivers": dict(
   sit="young", title="Cheapest Car Insurance for Young Drivers (2026)",
   h1="Cheapest car insurance for young drivers in 2026.",
   dek="Under-25 drivers pay the most of any age group. Here are the carriers that sting the least — and the ones to avoid.",
   ranker=rank_young, cross=("/article/young-drivers.html","Young Driver Insurance Guide"),
   why="Drivers under 25 are statistically the highest-risk group insurers write, so every carrier surcharges them — but by wildly different amounts. The cheapest carriers for a teen or 20-something pair a low base rate with a smaller young-driver penalty and strong good-student or telematics discounts.",
   tips=["Stay on a parent's policy as long as possible — it's almost always cheaper than a standalone policy.",
         "Take the good-student discount (usually a B average) — it can cut 10–25%.",
         "Opt into a telematics/usage-based program; for safe young drivers it's the single biggest lever.",
         "Choose a cheap-to-insure car (older, high safety rating, modest horsepower)."]),
 "cheapest-car-insurance-after-accident": dict(
   sit="accident", title="Cheapest Car Insurance After an At-Fault Accident (2026)",
   h1="Cheapest car insurance after an at-fault accident.",
   dek="One at-fault accident can raise your premium 20–45%. These carriers raise it the least — and accident forgiveness can erase it entirely.",
   ranker=rank_accident, cross=("/article/premium-went-up.html","Why Your Premium Went Up"),
   why="An at-fault accident typically adds 20–45% to your premium for 3–5 years. How much depends entirely on the carrier: forgiving insurers (and those offering accident forgiveness) barely move, while strict ones can non-renew. The cheapest after an accident combine a low base rate with a modest surcharge.",
   tips=["Ask about accident forgiveness — some carriers waive the first at-fault accident entirely.",
         "Shop at renewal: your current carrier's surcharge may be far higher than a competitor's fresh quote.",
         "Raise your deductible to offset the surcharge if you have savings to cover it.",
         "The surcharge usually drops off after 3 years — re-shop once it does."]),
 "cheapest-car-insurance-after-dui": dict(
   sit="sr22", title="Cheapest Car Insurance After a DUI / SR-22 (2026)",
   h1="Cheapest car insurance after a DUI (and who files your SR-22).",
   dek="A DUI moves you to the non-standard market and usually triggers an SR-22 filing. These carriers specialize in it and price it the lowest.",
   ranker=rank_dui, cross=("/article/sr22-insurance.html","SR-22 Insurance Explained"),
   why="A DUI roughly doubles many premiums and often pushes you into the non-standard market — and most states require an SR-22 (proof-of-financial-responsibility) filing for ~3 years. Standard carriers may non-renew; the carriers below specialize in high-risk drivers and file the SR-22 for you, often same-day.",
   tips=["Use a carrier that files the SR-22 electronically same-day so you can get your license reinstated fast.",
         "Don't let coverage lapse during the SR-22 period — it resets the clock and spikes rates.",
         "Re-shop every 6–12 months; SR-22 pricing drops as the violation ages.",
         "Once the SR-22 period ends, shop the standard market again — you'll likely save a lot."]),
 "cheapest-car-insurance-bad-credit": dict(
   sit="credit", title="Cheapest Car Insurance for Bad Credit (2026)",
   h1="Cheapest car insurance for bad or fair credit.",
   dek="In most states insurers use a credit-based score — fair/poor credit can add 20–35%. These carriers weigh it the least.",
   ranker=rank_credit, cross=("/article/credit-score-insurance.html","Credit Score & Car Insurance"),
   why="In all but a few states (CA, HI, MA, MI), insurers use a credit-based insurance score, and fair-or-poor credit can add 20–35% versus excellent credit. Carriers weight it very differently — the ones below apply the smallest credit penalty, so they're usually cheapest if your score isn't great.",
   tips=["If you live in CA, HI, MA, or MI, credit can't be used — focus on other factors.",
         "Your insurance score improves as your credit does; re-shop after it climbs.",
         "Avoid carriers known for heavy credit weighting (often the ones with the biggest excellent-credit discounts).",
         "A telematics program can offset a weak credit score for safe drivers."]),
 "cheapest-car-insurance-for-seniors": dict(
   sit="senior", title="Cheapest Car Insurance for Seniors (2026)",
   h1="Cheapest car insurance for seniors (55+).",
   dek="Rates fall through your 50s and 60s, then creep back up. Here's who's cheapest for mature drivers — and the AARP angle.",
   ranker=rank_senior, cross=("/article/coverage-guide.html","Coverage Guide"),
   why="Drivers 55+ are among the lowest-risk groups, so most carriers discount them — until the late 70s, when rates tick back up. Carriers with strong mature-driver programs (and the AARP-partnered Hartford) tend to be cheapest for seniors.",
   tips=["Ask about mature-driver / defensive-driving course discounts — many states mandate them.",
         "Low-mileage or pay-per-mile pricing fits retirees who drive less.",
         "AARP members should compare The Hartford's program.",
         "Re-evaluate coverage as your car ages — you may be able to drop collision."]),
}

# ---- scaffold from an existing auto article ----
scaff = open("article/state/texas.html", encoding="utf-8").read()
STYLE = scaff[scaff.index("<style>"):scaff.index("</style>")+len("</style>")]
NAV   = scaff[scaff.index('<header class="top">'):scaff.index("</header>")+len("</header>")]
TAIL  = scaff[scaff.index("<footer>"):]
TAIL  = re.sub(r'Compare [A-Za-z ]+ rates <span class="ascta-arrow">', 'Compare rates <span class="ascta-arrow">', TAIL)

RED, GREEN = "#b4321a", "#2f6b3a"
def esc(s): return s.replace('"',"&quot;")

def whyGood(car, key):
    bf = car.get("bestFor") or car.get("tag") or ""
    return bf

def build(slug, cfg):
    rows = cfg["ranker"]()
    top3 = rows[:3]; bottom3 = rows[-3:]
    url = f"https://boringrate.com/article/{slug}.html"
    sit = cfg["sit"]
    desc = cfg["dek"]
    # ranking table (top to bottom of the shown set, top highlighted)
    def review(name):
        s = REVIEW.get(name)
        return f'<a href="/article/carrier/{s}.html" style="color:var(--accent);text-decoration:none;border-bottom:1px solid var(--rule);">{name}</a>' if s else name
    trows=""
    for i,r in enumerate(top3):
        trows+=(f'<tr style="border-bottom:1px solid var(--rule);background:var(--paper-deep);">'
                f'<td style="padding:8px 6px;color:var(--ink-mute);">{i+1}</td>'
                f'<td style="padding:8px 6px;"><strong>{review(r["name"])}</strong></td>'
                f'<td style="padding:8px 6px;">${r["price"]:,}/yr</td>'
                f'<td style="padding:8px 6px;font-size:14px;color:var(--ink-soft);">{whyGood(r["car"],slug)}</td></tr>')
    faq = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":cfg["title"].replace(" (2026)",""),
         "acceptedAnswer":{"@type":"Answer","text":f"{top3[0]['name']}, {top3[1]['name']}, and {top3[2]['name']} are typically the cheapest for this situation based on the BoringRate model. {cfg['why']} Enter your ZIP to see the ranking for your exact area."}},
        {"@type":"Question","name":"How much more will I pay?",
         "acceptedAnswer":{"@type":"Answer","text":cfg["why"]}},
    ]})
    head=f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="canonical" href="{url}" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{cfg["title"]} — BoringRate</title>
<meta name="description" content="{esc(desc)}" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
{STYLE}
<meta property="og:title" content="{cfg['title']}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:image" content="https://boringrate.com/og-default.png" />
<meta property="og:url" content="{url}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{cfg['title']}" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image" content="https://boringrate.com/og-default.png" />
<script type="application/ld+json">
{faq}
</script>
</head>
<body>'''
    zipbar='''<div class="zip-bar"><div class="wrap"><div class="zip-bar-inner">
<div class="zip-bar-slogan"><strong>Boring Research.</strong> Easy Decision. &mdash; Enter your ZIP to compare rates.</div>
<form class="zip-bar-form" id="zipBarForm" autocomplete="off"><input class="zip-bar-input" id="zipBarInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="zip-bar-btn">Compare &rarr;</button></form>
</div></div></div>'''
    onsub=("event.preventDefault();var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);"
           "if(/^\\d{5}$/.test(z)){location.href='/?zip='+z+'&sit="+sit+"'}else{this.zc.focus()}")
    cta=('<div class="tooltiles">'
      '<div class="tile"><div class="tile-kicker">Compare rates</div>'
      '<div class="tile-name">See your cheapest carrier &mdash; tuned to this situation</div>'
      '<div class="tile-desc">Enter your ZIP and we will rank carriers with this exact situation applied, for your area.</div>'
      f'<form class="tile-zipform" onsubmit="{onsub}"><input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="tile-zip-btn">Compare &rarr;</button></form>'
      '</div>'
      '<div class="tile"><div class="tile-kicker">Coverage calculator</div>'
      '<div class="tile-name">Not sure how much you need?</div>'
      '<div class="tile-desc">See what to buy and what to skip &mdash; and how each choice changes your price.</div>'
      '<a class="tbtn secondary" href="/coverage.html">Help me choose my coverage options &rarr;</a>'
      '</div></div>')
    bottomlist=" · ".join(f"<strong>{r['name']}</strong>" for r in reversed(bottom3))
    tips="".join(f"<li>{t}</li>" for t in cfg["tips"])
    crossUrl,crossLbl=cfg["cross"]
    body=f'''<div class="wrap-narrow">
  <div class="article-header">
    <div class="article-kicker"><a href="/">← BoringRate</a> &nbsp;·&nbsp; Cheapest For… &nbsp;·&nbsp; 4 min read</div>
    <h1 class="article-title">{cfg["h1"]}</h1>
    <p class="article-dek">{cfg["dek"]}</p>
    <div class="article-byline">BoringRate Editorial &nbsp;·&nbsp; June 2026</div>
  </div>
  <div class="article-body">
    <h2>Top 3 carriers for this situation</h2>
    <p>Estimated national full-coverage premiums with this situation applied, cheapest first. Directional model estimates &mdash; <strong>enter your ZIP below for your real local ranking</strong>.</p>
    <table style="width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:660px;">
    <thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;"><th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">Carrier</th><th style="padding:8px 6px;">Est. national</th><th style="padding:8px 6px;">Why</th></tr></thead>
    <tbody>{trows}</tbody></table>
    <div class="callout"><p><strong>Often the most expensive for this situation:</strong> {bottomlist_safe(bottomlist=bottomlist)} If you're with one of these, you're probably overpaying — it takes two minutes to check.</p></div>
    {cta}
    <h2>Why this raises your rate</h2>
    <p>{cfg["why"]}</p>
    <h2>How to pay less</h2>
    <ul style="font-size:17px;line-height:1.6;color:var(--ink-soft);max-width:660px;margin:0 0 24px;padding-left:22px;">{tips}</ul>
    <div class="callout"><p>Rankings are directional estimates from the BoringRate model, not quotes — your real rate depends on your ZIP, vehicle, and history. Related: <a class="ca-link" href="{crossUrl}">{crossLbl} &rarr;</a></p></div>
    <h2>Frequently asked questions</h2>
    <div class="callout"><p><strong>Who is cheapest for this situation?</strong><br>{top3[0]['name']}, {top3[1]['name']}, and {top3[2]['name']} rank cheapest in the model. Enter your ZIP to see the order for your area.</p></div>
    <div class="callout"><p><strong>Will my rate stay high forever?</strong><br>{cfg["why"]}</p></div>
  </div>
</div>'''
    return head+"\n"+NAV+"\n"+zipbar+"\n"+body+"\n"+TAIL

def bottomlist_safe(bottomlist):
    return bottomlist

n=0
for slug,cfg in SIT.items():
    open(f"article/{slug}.html","w",encoding="utf-8").write(build(slug,cfg)); n+=1
    r=cfg["ranker"]()
    print(f"{slug}: top3 = {[x['name'] for x in r[:3]]} | bottom3 = {[x['name'] for x in r[-3:]]}")
print("wrote",n,"situation articles")
