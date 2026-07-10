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
  ("Roof damage","<p><strong>Depends.</strong> Sudden damage from a covered peril — a storm, hail, a fallen tree — is covered. A roof that simply <em>wore out</em> with age is not (that's maintenance). Note: many insurers now pay <strong>actual cash value</strong> (depreciated) on older roofs rather than full replacement, so check your roof settlement terms. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-roof-damage.html\">Full guide: roof damage, leaks &amp; replacement &rarr;</a></p>"),
  ("Water damage","<p><strong>Sudden, internal water</strong> — a burst pipe, an overflowing washer, a leak from a covered roof breach — is covered. <strong>Flood</strong> (rising water from outside) is not — that's a separate policy. <strong>Sewer/drain backup</strong> needs a water-backup endorsement. Slow, long-term leaks you should have caught are treated as maintenance and excluded. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-water-damage.html\">Full guide: water damage &rarr;</a></p>"),
  ("Mold","<p><strong>Limited.</strong> If mold results from a covered water loss (a burst pipe), remediation is usually covered up to a sublimit ($1,000–$10,000 typically). Mold from ongoing humidity or a neglected leak is not. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-mold.html\">Full guide: mold &rarr;</a></p>"),
  ("A fallen tree","<p><strong>Usually yes.</strong> If a tree hits your house, garage, or fence, dwelling/other-structures coverage handles the damage and removal (up to a limit). A tree that falls and hits <em>nothing</em> is often only removed if it blocks a driveway or ramp. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-tree-damage.html\">Full guide: fallen trees &amp; tree damage &rarr;</a></p>"),
  ("Your dog (and dog bites)","<p><strong>Usually</strong>, under personal liability — but many insurers exclude certain breeds or a dog with a bite history. Disclose your pet; an undisclosed dog can void the claim. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-dog-bites.html\">Full guide: dog bites &rarr;</a></p>"),
  ("Wind, hail &amp; storms","<p><strong>Covered</strong> — wind, hail, and hurricane wind are covered perils. The catch: a separate percentage-based wind/hurricane deductible often applies, and older roofs pay depreciated value. Storm surge is flood, not homeowners. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-storm-damage.html\">Full guide: wind, hail &amp; storm damage &rarr;</a></p>"),
  ("Sewer &amp; drain backup","<p><strong>Not by default</strong> — sewer/drain backup and sump-pump failure are excluded; a cheap water-backup endorsement (~$50–100/yr) adds them. Separate from both flood and ordinary water damage. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-sewer-backup.html\">Full guide: sewer backup &rarr;</a></p>"),
  ("Flood","<p><strong>No — never.</strong> Standard homeowners excludes flood (rising water from outside); you need a separate NFIP or private flood policy. Sudden <em>internal</em> water is covered, but rising water is not. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-flood-damage.html\">Full guide: flood damage &rarr;</a></p>"),
  ("Theft and foundation","<p><strong>Theft</strong> of belongings is covered (subject to deductible and sublimits). <strong>Foundation cracks</strong> from settling, soil movement, or earthquake are generally <em>not</em> covered — only if caused by a specific covered peril like a burst pipe. <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-foundation.html\">Full guide: foundation repair &rarr;</a></p>"),
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

"does-homeowners-insurance-cover-water-damage": dict(
 title="Does Homeowners Insurance Cover Water Damage? (2026)",
 h1="Does homeowners insurance cover water damage? Sudden yes, gradual no.",
 dek="A burst pipe or an overflowing appliance is covered. A slow leak you ignored, flood, and sewer backup are not. Here's exactly where the line falls — and the endorsements that close the gaps.",
 kicker="Home Basics", read="6",
 lead="<p>Water is the messiest question in homeowners insurance because the answer depends entirely on <em>how</em> the water reached your home. The rule insurers use is simple to state and easy to get wrong: <strong>sudden and accidental is covered; gradual, preventable, or from outside is not.</strong> Below is where that line falls, the scenarios homeowners ask about most, and the two cheap endorsements that close the biggest gaps.</p>",
 sections=[
  ("The short answer","<p><strong>Yes — for sudden, accidental water damage from inside your home.</strong> A burst pipe, an overflowing washing machine, a water heater that lets go, or rain entering through storm damage to your roof are all covered under dwelling and personal property. What your policy will <em>not</em> pay for: <strong>flood</strong> (rising water from outside), <strong>sewer or drain backup</strong> (unless you add an endorsement), <strong>gradual leaks</strong> you could have caught, and damage from deferred <strong>maintenance</strong>. Everything below is detail on those two lists.</p>"),
  ("Water damage that IS covered","<ul><li><strong>A burst or frozen pipe</strong> that ruptures and floods a room.</li><li><strong>An overflowing appliance</strong> — washer, dishwasher, water heater.</li><li><strong>A sudden plumbing or HVAC discharge.</strong></li><li><strong>Rain or snow entering through storm damage</strong> — wind or hail opens the roof, then water gets in (the resulting interior damage is covered; see the <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-roof-damage.html\">roof guide</a>).</li><li><strong>Water used to put out a fire.</strong></li></ul><p>In each case the policy pays to repair the structure and replace damaged belongings — at replacement cost if you carry that upgrade.</p>"),
  ("Water damage that is NOT covered","<ul><li><strong>Flood</strong> — rising water from outside (storm surge, overflowing river, heavy rain pooling from the ground). Needs a separate <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-flood-damage.html\">flood policy</a>; never part of standard homeowners.</li><li><strong>Sewer or drain backup</strong> and sump-pump failure — excluded by default; a <strong>water-backup endorsement</strong> ($50–100/yr) adds it.</li><li><strong>Gradual leaks and seepage</strong> — a slow drip under a sink for weeks is \"maintenance,\" not a sudden loss.</li><li><strong>Mold</strong> from a gradual or uncovered leak (see the <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-mold.html\">mold guide</a>).</li><li><strong>The source itself</strong> — the failed pipe or appliance. The policy pays for the <em>damage</em> the water caused, not the broken part.</li></ul>"),
  ("The two endorsements almost everyone should add","<p><strong>Water-backup coverage</strong> is the big one — sewer/drain backup and sump-pump failure are among the most common basement claims and are excluded by default. For ~$50–100/year it's usually worth it. Second, <strong>service-line coverage</strong> handles the buried water/sewer line from the street to your house, which is your responsibility and not otherwise covered. The <a class=\"ca-link\" href=\"/home/coverage.html\">coverage calculator</a> flags both.</p>"),
  ("What to do after water damage","<ol><li><strong>Stop the source</strong> — shut off the water main if a pipe burst.</li><li><strong>Document everything</strong> — photos and video before you clean up.</li><li><strong>Mitigate</strong> — extract water and dry the area fast; insurers can deny mold that grows because you delayed. Keep receipts for emergency work.</li><li><strong>File promptly</strong> and get a repair estimate.</li><li><strong>Check your deductible</strong> before filing a small claim — water claims can raise your premium.</li></ol>"),
  ("Make sure you're actually covered","<p>Three things decide a water claim: <strong>replacement cost</strong> (so you're paid to rebuild, not the depreciated value), a <strong>water-backup endorsement</strong>, and enough <strong>dwelling coverage</strong> to rebuild. The <a class=\"ca-link\" href=\"/home/coverage.html\">coverage calculator</a> checks all three, and the <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover.html\">does-it-cover hub</a> answers the rest.</p>"),
 ],
 callout="<strong>Bottom line:</strong> sudden internal water is covered; flood, sewer backup, and slow leaks are not — but a $50–100 water-backup endorsement closes the most common gap. Carry replacement cost and document fast.",
 faq=[
  ("Does homeowners insurance cover water damage?","Sudden, accidental internal water — a burst pipe, overflowing appliance, or storm-driven roof leak — is covered. Flood, sewer backup, and gradual leaks are not (though a water-backup endorsement adds sewer/sump coverage)."),
  ("Does homeowners insurance cover a burst pipe?","Yes — a burst or frozen pipe is a classic covered loss. The policy pays to repair the water damage and replace ruined belongings, though not the pipe itself. Your deductible applies."),
  ("Does homeowners insurance cover sewer backup?","Not by default — it's excluded. A water-backup endorsement (about $50–100/year) adds coverage for sewer/drain backup and sump-pump failure, one of the most common basement claims."),
  ("Does homeowners insurance cover a slow leak?","Usually no. A gradual leak you could reasonably have caught is treated as a maintenance issue and excluded. Sudden, accidental water is what's covered."),
  ("Does homeowners insurance cover water damage from rain?","If rain enters through sudden storm damage (wind or hail opens your roof), the interior water damage is covered. Rain that seeps in through a worn roof or foundation is not — that's maintenance or flood."),
 ],
 cross=("/home/does-homeowners-insurance-cover.html","Does homeowners insurance cover that?")),

"does-homeowners-insurance-cover-roof-damage": dict(
 title="Does Homeowners Insurance Cover Roof Damage, Leaks &amp; Replacement? (2026)",
 h1="Does homeowners insurance cover roof damage? Storm yes, age no.",
 dek="Sudden damage from a storm, hail, or fallen tree is covered. A roof that simply wore out is not — and many insurers now pay depreciated value on older roofs. Here's how roof claims actually work.",
 kicker="Home Basics", read="6",
 lead="<p>The roof is where the most homeowners insurance surprises live, because insurers draw a hard line between <strong>sudden damage</strong> (covered) and <strong>wear and age</strong> (not) — and they've quietly tightened how they pay for older roofs. Here's what's covered, the actual-cash-value trap that shrinks payouts, and what to check before you file.</p>",
 sections=[
  ("The short answer","<p><strong>Covered:</strong> sudden roof damage from a covered peril — wind, hail, a fallen tree, fire. The policy pays to repair or replace the roof and any resulting interior water damage. <strong>Not covered:</strong> a roof that <em>wore out</em> with age, gradual leaks, poor maintenance, or manufacturer defects. The catch even when it IS covered: many insurers now settle older roofs at <strong>actual cash value</strong> (depreciated), not full replacement.</p>"),
  ("Roof damage that's covered","<p>Damage from a <strong>windstorm or hurricane</strong>, <strong>hail</strong>, a <strong>fallen tree or limb</strong> (see the <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-tree-damage.html\">tree guide</a>), <strong>fire or lightning</strong>, and the weight of ice or snow. If the roof breach then lets water in, the resulting interior and personal-property damage is covered too — that overlaps with <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-water-damage.html\">water damage</a>.</p>"),
  ("Roof damage that's NOT covered","<ul><li><strong>Age and wear</strong> — asphalt shingles last ~20–25 years; a roof at end of life that starts leaking is a maintenance replacement, on you.</li><li><strong>Gradual leaks</strong> you should have caught and repaired.</li><li><strong>Neglect</strong> — missing shingles or flashing you didn't maintain.</li><li><strong>Defects</strong> — poor installation or a bad product (chase the contractor/manufacturer).</li><li><strong>Cosmetic hail dents</strong> on metal roofs, if you have a cosmetic-damage exclusion.</li></ul>"),
  ("The ACV vs. replacement-cost trap","<p>This is the big one. A <strong>replacement-cost (RCV)</strong> policy pays to install a new roof (minus your deductible). An <strong>actual-cash-value (ACV)</strong> policy pays the depreciated value — a 15-year-old roof might be worth 40% of a new one, leaving you thousands short. Insurers increasingly push ACV or a separate <strong>roof-payment schedule</strong> on roofs over 10–15 years, especially in hail-prone states. <strong>Check your declarations page for the roof settlement type</strong> before you need it.</p>"),
  ("Roof age, inspections, and non-renewal","<p>Insurers care a lot about roof age. Many won't write a new policy on a roof over 15–20 years without an inspection, and some non-renew or force ACV on old roofs. If yours is aging, a pre-emptive replacement can lower premiums and keep you on a replacement-cost settlement — and it's a common discount.</p>"),
  ("What to do after roof damage","<ol><li><strong>Document the storm</strong> — date, photos, and any local hail/wind reports.</li><li><strong>Get a tarp up</strong> to prevent further damage (keep receipts).</li><li><strong>Get an independent roofer's inspection</strong>, not just the adjuster's.</li><li><strong>File before the claim window closes</strong> (often 1 year from the storm).</li><li><strong>Compare the settlement</strong> to your policy's RCV/ACV terms.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> storm damage is covered, age is not — and whether you get a new roof or a depreciated check depends on your RCV-vs-ACV settlement terms. Check those terms and your roof's age before a claim, not after.",
 faq=[
  ("Does homeowners insurance cover roof replacement?","Yes, if the roof was damaged by a covered peril like wind, hail, or a fallen tree. It does not cover replacing a roof that simply wore out with age — that's maintenance."),
  ("Does homeowners insurance cover roof leaks?","A leak from sudden storm damage is covered, including the interior water damage. A leak from an old, worn, or poorly maintained roof is not."),
  ("Why did my insurer only pay part of my roof claim?","Likely an actual-cash-value (ACV) settlement — it pays the depreciated value of an older roof, not full replacement cost. Check your declarations page for the roof settlement type."),
  ("Does homeowners insurance cover a 20-year-old roof?","Often at reduced (actual cash value) terms, and some insurers won't cover an old roof at all without an inspection or may non-renew. Replacing an end-of-life roof can restore replacement-cost coverage."),
  ("Does homeowners insurance cover hail damage to a roof?","Yes — hail is a covered peril. But older roofs may be settled at depreciated value, and metal roofs with a cosmetic-damage exclusion may not be covered for dents alone."),
 ],
 cross=("/home/does-homeowners-insurance-cover.html","Does homeowners insurance cover that?")),

"does-homeowners-insurance-cover-mold": dict(
 title="Does Homeowners Insurance Cover Mold? (2026)",
 h1="Does homeowners insurance cover mold? Only from a covered water loss.",
 dek="Mold from a sudden covered loss — like a burst pipe — is usually covered up to a sublimit. Mold from humidity, neglect, or flood is not. Here's the line and the limits.",
 kicker="Home Basics", read="5",
 lead="<p>Mold is one of the most disputed homeowners claims, because coverage hinges on a single question: <strong>what caused the water that fed it?</strong> If the source was a covered, sudden loss, mold remediation is usually covered — but only up to a capped sublimit. If the source was gradual, preventable, or a flood, you're on your own.</p>",
 sections=[
  ("The short answer","<p><strong>Covered — if the mold results from a covered water loss</strong>, like a burst pipe or a storm-driven roof leak. Remediation is paid up to a <strong>mold sublimit</strong>, typically $1,000–$10,000. <strong>Not covered:</strong> mold from ongoing humidity, condensation, a slow leak you ignored, or a flood. The cause of the water is everything.</p>"),
  ("When mold IS covered","<p>A <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-water-damage.html\">covered water loss</a> that you addressed promptly and that then produced mold — a pipe bursts behind a wall, you file, and mold is found during repairs. Because it traces to a sudden, covered event and you mitigated quickly, remediation is covered up to the sublimit.</p>"),
  ("When mold is NOT covered","<ul><li><strong>Humidity and condensation</strong> — bathroom or basement mold from poor ventilation is maintenance.</li><li><strong>Gradual leaks</strong> — a slow drip you should have caught.</li><li><strong>Flood</strong> — mold after rising water needs a separate flood policy (and flood policies have their own mold limits).</li><li><strong>Neglect</strong> — mold that spread because you delayed drying out a covered loss.</li></ul>"),
  ("The sublimit — and how to raise it","<p>Even when covered, mold is capped. A standard policy might include $1,000–$5,000; some default to $10,000. Full remediation of a serious mold problem can far exceed that. If you live in a humid or flood-prone region, ask about a <strong>higher mold endorsement</strong> — it's inexpensive relative to a five-figure remediation bill. The <a class=\"ca-link\" href=\"/home/coverage.html\">coverage calculator</a> flags mold and water-backup limits together.</p>"),
  ("How to protect the claim","<ol><li><strong>Act fast on any water loss</strong> — dry the area within 24–48 hours; delay is the top reason mold claims get denied.</li><li><strong>Document the source</strong> and that it was sudden.</li><li><strong>Keep mitigation receipts.</strong></li><li><strong>Don't rip everything out before the adjuster sees it</strong> — but do stop the moisture.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> mold is covered only when it flows from a sudden covered water loss, and only up to a sublimit. Fix water fast, document the cause, and consider a higher mold limit if you're in a humid or flood-prone area.",
 faq=[
  ("Does homeowners insurance cover mold?","Only when the mold results from a covered, sudden water loss — like a burst pipe — and only up to a mold sublimit (typically $1,000–$10,000). Mold from humidity, neglect, or flood is not covered."),
  ("How much mold coverage does homeowners insurance include?","Usually a sublimit of $1,000–$10,000, well below the cost of major remediation. You can often buy a higher mold endorsement, worth considering in humid or flood-prone areas."),
  ("Why was my mold claim denied?","Most often because the water source was gradual (a slow leak or humidity), was a flood, or because remediation was delayed and the insurer deemed the spread preventable."),
  ("Does homeowners insurance cover black mold?","The type of mold doesn't change coverage — the cause of the water does. Black mold from a covered burst pipe is treated the same as any mold; from humidity or flood it's excluded."),
 ],
 cross=("/home/does-homeowners-insurance-cover-water-damage.html","Does homeowners insurance cover water damage?")),

"does-homeowners-insurance-cover-tree-damage": dict(
 title="Does Homeowners Insurance Cover Tree Damage &amp; Fallen Trees? (2026)",
 h1="Does homeowners insurance cover a fallen tree? Usually — if it hits something.",
 dek="A tree that hits your house, garage, fence, or car is covered, including removal up to a limit. A tree that falls and hits nothing usually isn't removed. Here's how it works — and whose policy pays.",
 kicker="Home Basics", read="5",
 lead="<p>Tree claims turn on two questions: <strong>did the tree hit a covered structure</strong>, and <strong>whose tree was it?</strong> The answers are less intuitive than people expect — a healthy neighbor's tree that falls on your house is usually <em>your</em> claim, and a tree that falls and damages nothing often isn't removed at all.</p>",
 sections=[
  ("The short answer","<p><strong>Covered:</strong> a fallen tree (or large limb) that <strong>strikes a covered structure</strong> — your house, detached garage, fence, or shed — from a covered peril like wind or a storm. Dwelling/other-structures coverage pays for the damage, plus <strong>tree removal</strong> up to a limit (often $500–$1,000). <strong>Usually not covered:</strong> a tree that falls and hits <em>nothing</em>, or a tree that fell because it was dead and you knew it.</p>"),
  ("Whose policy pays when it's the neighbor's tree","<p>Counterintuitive but standard: if a neighbor's healthy tree falls on your house in a storm, <strong>your</strong> homeowners policy pays (and your insurer may try to recover from theirs). The exception: if the tree was <strong>visibly dead or diseased</strong> and you'd warned the neighbor in writing, their policy — via negligence — may be on the hook. Document any warnings.</p>"),
  ("Tree removal: the fine print","<p>Removal is only covered when the tree <strong>hit a covered structure</strong> or is <strong>blocking a driveway or a handicap-access ramp</strong>. A large tree that falls across your yard and damages nothing is typically <strong>your</strong> cost to remove — insurers won't pay to clear debris that caused no covered damage. Removal limits are low ($500–$1,000); large-tree removal can exceed that.</p>"),
  ("Your car under the tree","<p>If the tree lands on your <strong>car</strong>, that's not homeowners — it's the <strong>comprehensive</strong> portion of your <em>auto</em> policy. Two different policies for one falling tree: the house is homeowners, the car is auto comprehensive.</p>"),
  ("What to do after a tree falls","<ol><li><strong>Document</strong> the tree, the damage, and the weather.</li><li><strong>Prevent further damage</strong> (tarp the roof) but don't start major removal before the adjuster.</li><li><strong>Note whose tree it was</strong> and any prior warnings if it was dead.</li><li><strong>File the structure claim on homeowners, the car on auto.</strong></li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> a tree is covered when it hits a covered structure, with limited removal coverage — but a tree that hits nothing, or your car, follows different rules. Dead-tree neglect can shift liability to whoever ignored it.",
 faq=[
  ("Does homeowners insurance cover a fallen tree?","Yes, when the tree hits a covered structure like your house, garage, or fence — dwelling and other-structures coverage pay for the damage, plus limited tree removal (often $500–$1,000)."),
  ("If my neighbor's tree falls on my house, whose insurance pays?","Usually yours — your homeowners policy covers the damage regardless of whose tree it was. If the tree was visibly dead and you'd warned the neighbor in writing, their liability coverage may apply instead."),
  ("Does homeowners insurance cover tree removal?","Only if the tree hit a covered structure or is blocking a driveway or access ramp, and only up to a limit (often $500–$1,000). A tree that falls and damages nothing is typically your cost to remove."),
  ("Does homeowners insurance cover a tree falling on my car?","No — that's the comprehensive coverage on your auto policy, not homeowners. The house is homeowners; the car is auto comprehensive."),
 ],
 cross=("/home/does-homeowners-insurance-cover.html","Does homeowners insurance cover that?")),

"does-homeowners-insurance-cover-flood-damage": dict(
 title="Does Homeowners Insurance Cover Flood Damage? (2026)",
 h1="Does homeowners insurance cover flood? No — and here's what you need instead.",
 dek="Flood is never covered by a standard homeowners policy. You need a separate NFIP or private flood policy. Here's the difference between flood and covered water damage, and how to get covered.",
 kicker="Home Basics", read="5",
 lead="<p>This is the single most expensive misunderstanding in homeowners insurance: <strong>standard homeowners policies never cover flood.</strong> Not in any state, not with any carrier. Flood is a separate policy — and the difference between \"flood\" and covered \"water damage\" is exactly where thousands of uninsured claims come from.</p>",
 sections=[
  ("The short answer","<p><strong>No.</strong> A standard homeowners policy explicitly excludes <strong>flood</strong> — defined as rising water from outside: storm surge, an overflowing river or lake, heavy rain or snowmelt that pools up from the ground, or a levee/dam failure. To be covered for flood you need a <strong>separate flood policy</strong>, either through the federal <strong>NFIP</strong> or a private flood insurer.</p>"),
  ("Flood vs. covered water damage — the critical line","<p>Homeowners <em>does</em> cover <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-water-damage.html\">sudden internal water damage</a> — a burst pipe, an overflowing appliance, rain through a storm-damaged roof. The dividing line is <strong>direction</strong>: water coming <em>down</em> or from <em>inside</em> (a pipe, the roof) is homeowners; water rising <em>up</em> from the ground or outside is flood. A hurricane that rips your roof and lets rain in = homeowners; the same hurricane's storm surge flooding your first floor = flood policy.</p>"),
  ("NFIP vs. private flood","<p><strong>NFIP</strong> (National Flood Insurance Program) is federally backed, available almost everywhere, and caps building coverage at $250,000 and contents at $100,000. <strong>Private flood</strong> policies can offer higher limits, replacement cost on contents, and sometimes lower prices for lower-risk homes. If your mortgage is in a high-risk flood zone, your lender <strong>requires</strong> flood insurance.</p>"),
  ("Do you need it if you're not in a flood zone?","<p>Probably worth it. More than <strong>a quarter of flood claims come from outside high-risk zones</strong>, where premiums are low. A few inches of water can cause tens of thousands in damage that homeowners won't touch. Flood policies also typically have a <strong>30-day waiting period</strong>, so you can't buy it as a storm approaches — get it before the season.</p>"),
  ("What to do","<ol><li><strong>Check your flood zone</strong> (FEMA's map) and whether your lender requires coverage.</li><li><strong>Quote both NFIP and private flood</strong> — prices and limits differ.</li><li><strong>Buy before you need it</strong> — mind the 30-day waiting period.</li><li><strong>Know your homeowners covers the rest</strong> — wind, roof, and internal water are still on your <a class=\"ca-link\" href=\"/home/index.html\">homeowners policy</a>.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> flood is never part of homeowners — you need a separate NFIP or private flood policy, ideally before storm season, since there's a 30-day wait. Internal water damage (burst pipes, roof leaks) stays on homeowners.",
 faq=[
  ("Does homeowners insurance cover flood damage?","No. Standard homeowners policies never cover flood (rising water from outside). You need a separate flood policy through the NFIP or a private flood insurer."),
  ("What's the difference between flood and water damage?","Water damage from inside — a burst pipe, overflowing appliance, or storm-damaged roof — is covered by homeowners. Flood is rising water from outside (surge, rivers, ground pooling) and requires a separate policy."),
  ("Do I need flood insurance if I'm not in a flood zone?","Often yes — over a quarter of flood claims come from lower-risk areas, where premiums are cheap. A few inches of water causes major damage homeowners won't cover."),
  ("How much does flood insurance cost and when should I buy it?","It varies widely by zone, but low-risk homes are often a few hundred dollars a year. Buy before storm season — flood policies typically have a 30-day waiting period before they take effect."),
 ],
 cross=("/home/does-homeowners-insurance-cover-water-damage.html","Does homeowners insurance cover water damage?")),

"does-homeowners-insurance-cover-foundation": dict(
 title="Does Homeowners Insurance Cover Foundation Repair? (2026)",
 h1="Does homeowners insurance cover foundation damage? Rarely — unless a covered peril caused it.",
 dek="Foundation cracks from settling, soil movement, or earthquake are excluded. Damage from a sudden covered peril — like a burst pipe or a plumbing leak — can be covered. Here's the narrow path.",
 kicker="Home Basics", read="5",
 lead="<p>Foundation claims are among the hardest to win, because the most common causes — <strong>settling, soil movement, and expansive clay</strong> — are all specifically excluded as \"earth movement\" or normal aging. Coverage exists, but only through a narrow door: a foundation problem that a <em>covered peril</em> caused.</p>",
 sections=[
  ("The short answer","<p><strong>Usually not.</strong> Standard homeowners excludes foundation damage from <strong>settling, cracking, shrinking, or bulging</strong>, from <strong>earth movement</strong> (soil expansion/contraction, sinkholes, earthquakes), and from <strong>hydrostatic pressure</strong> (groundwater). <strong>It can be covered</strong> when a specific covered peril causes it — most commonly a <strong>sudden plumbing leak under the slab</strong>, or an explosion, vehicle impact, or fallen tree.</p>"),
  ("When foundation damage IS covered","<ul><li><strong>A burst or leaking pipe beneath the foundation</strong> that erodes soil or cracks the slab — a covered <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-water-damage.html\">water loss</a>.</li><li><strong>A vehicle or fallen tree striking the foundation.</strong></li><li><strong>An explosion or fire.</strong></li><li><strong>Plumbing/HVAC discharge</strong> that undermines the footing.</li></ul><p>Even then, insurers often cover the <em>resulting</em> damage but not accessing the pipe — read the tear-out provisions.</p>"),
  ("When it's NOT covered (the common cases)","<ul><li><strong>Settling and normal aging</strong> — hairline cracks as a house ages.</li><li><strong>Expansive/clay soil</strong> movement (huge in TX and the Plains) — excluded earth movement.</li><li><strong>Earthquake and sinkholes</strong> — separate policies/endorsements (sinkhole coverage is mandatory-offer in FL).</li><li><strong>Poor drainage and hydrostatic pressure</strong> — groundwater pushing on the foundation.</li><li><strong>Construction defects</strong> — a builder's problem.</li></ul>"),
  ("The endorsements that help","<p>If you're in earthquake country, an <strong>earthquake endorsement/policy</strong> covers quake-driven foundation damage. In sinkhole regions, <strong>sinkhole or catastrophic-ground-collapse coverage</strong> applies. Neither is in a standard policy. There is generally <em>no</em> endorsement for ordinary settling or expansive-soil movement — that's a maintenance and drainage issue.</p>"),
  ("What to do about foundation cracks","<ol><li><strong>Get a structural engineer's report</strong> on the cause — that determines coverage far more than the crack itself.</li><li><strong>If a plumbing leak is suspected</strong>, document it — that's your covered path.</li><li><strong>Manage drainage</strong> — grading, gutters, and downspouts prevent most soil-movement damage.</li><li><strong>File only with a covered-peril cause</strong>; a settling claim will be denied and still counts against you.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> foundation damage is covered only when a covered peril (usually a burst pipe under the slab) caused it — settling, soil movement, and earthquake are excluded. The engineer's report on cause decides the claim.",
 faq=[
  ("Does homeowners insurance cover foundation repair?","Only when a covered peril caused it — most often a sudden plumbing leak under the slab, or a vehicle/tree impact or explosion. Cracks from settling, soil movement, or earthquake are excluded."),
  ("Does homeowners insurance cover foundation cracks from settling?","No. Settling, shrinking, and cracking from normal aging or expansive soil are specifically excluded as earth movement or maintenance."),
  ("Is foundation damage from a plumbing leak covered?","Usually yes — a sudden leak under the foundation is a covered water loss, so the resulting damage is typically covered (though accessing the pipe may be limited). Document the leak as the cause."),
  ("Does homeowners insurance cover foundation damage from earthquakes or sinkholes?","No — both are excluded from standard policies. Earthquake needs a separate endorsement or policy; sinkhole coverage is a separate endorsement (a mandatory offer in Florida)."),
 ],
 cross=("/home/does-homeowners-insurance-cover.html","Does homeowners insurance cover that?")),

"does-homeowners-insurance-cover-sewer-backup": dict(
 title="Does Homeowners Insurance Cover Sewer Backup? (2026)",
 h1="Does homeowners insurance cover sewer backup? Not without the endorsement.",
 dek="Sewer and drain backup is excluded from standard homeowners — but a cheap water-backup endorsement adds it. Here's what it covers, what it costs, and why it's one of the most common basement claims.",
 kicker="Home Basics", read="5",
 lead="<p>Sewer backup is the classic \"I thought I was covered\" claim. A standard homeowners policy <strong>excludes water that backs up through sewers, drains, or a failed sump pump</strong> — even though it's one of the most common and messiest basement losses. The fix is a specific, inexpensive endorsement most homeowners don't know to ask for.</p>",
 sections=[
  ("The short answer","<p><strong>No — not by default.</strong> Standard homeowners specifically excludes damage from <strong>water that backs up through sewers or drains</strong> and from <strong>sump-pump failure</strong>. To be covered you add a <strong>water-backup endorsement</strong> (sometimes called sewer/drain backup or sump-pump coverage), typically <strong>$50–$100/year</strong> for $5,000–$25,000 of coverage. It's separate from both regular water damage and flood.</p>"),
  ("Why it's excluded — and what the endorsement adds","<p>Insurers carve backup out of the base policy because it's frequent and tied to aging municipal sewers and sump pumps homeowners don't maintain. The <strong>water-backup endorsement</strong> covers: sewage or water that <strong>backs up through drains</strong>, <strong>overflow from a sump pump or sump-pump failure</strong>, and the resulting cleanup and property damage. Some insurers bundle it with <strong>service-line coverage</strong> (the buried pipe from the street to your home).</p>"),
  ("Sewer backup vs. flood vs. water damage","<p>Three different things, three different rules: <strong>sudden internal water</strong> (a burst pipe) is covered by base homeowners (see <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-water-damage.html\">water damage</a>); <strong>flood</strong> (rising water from outside) needs a separate <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-flood-damage.html\">flood policy</a>; <strong>sewer/drain backup</strong> needs the water-backup endorsement. A heavy storm that overwhelms the city sewer and pushes water up your basement drain is <em>backup</em>, not flood — and only the endorsement covers it.</p>"),
  ("How much coverage to buy","<p>Base endorsements often start at $5,000, which a finished basement blows through fast. If you have a finished basement, sump pump, or below-grade utilities, step up to <strong>$25,000+</strong> — it's usually only a few more dollars a year. The <a class=\"ca-link\" href=\"/home/coverage.html\">coverage calculator</a> flags backup and service-line coverage together.</p>"),
  ("Reduce the risk (and keep the claim clean)","<ol><li><strong>Install a backwater valve</strong> and maintain your sump pump (a battery backup helps).</li><li><strong>Keep the endorsement</strong> — the coverage only exists if you added it before the loss.</li><li><strong>After a backup</strong>: photograph everything, stop using drains, and get professional cleanup (sewage is a health hazard). Keep receipts.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> sewer and sump-pump backup isn't in a standard policy — add a water-backup endorsement (~$50–100/yr) and buy enough limit for a finished basement. It's separate from both flood and ordinary water damage.",
 faq=[
  ("Does homeowners insurance cover sewer backup?","Not by default — it's excluded. A water-backup endorsement (about $50–100/year) adds coverage for sewer/drain backup and sump-pump failure, typically $5,000–$25,000."),
  ("What is a water-backup endorsement?","An add-on that covers damage from water backing up through sewers or drains and from sump-pump overflow or failure — losses the base homeowners policy excludes."),
  ("Is sewer backup the same as flood?","No. Flood is rising water from outside and needs a separate flood policy. Sewer backup is water pushing up through your drains and needs the water-backup endorsement — even when a storm caused it."),
  ("How much does sewer backup coverage cost?","Usually $50–$100 per year for $5,000–$25,000 of coverage. Homes with finished basements should buy the higher limits, which add only a little."),
  ("Does homeowners insurance cover a failed sump pump?","Only if you have a water-backup/sump-pump endorsement. Damage from sump-pump failure is excluded from the base policy."),
 ],
 cross=("/home/does-homeowners-insurance-cover-water-damage.html","Does homeowners insurance cover water damage?")),

"does-homeowners-insurance-cover-dog-bites": dict(
 title="Does Homeowners Insurance Cover Dog Bites? (2026)",
 h1="Does homeowners insurance cover dog bites? Usually — with big exceptions.",
 dek="Your personal liability coverage usually pays for a dog bite — but breed exclusions, bite history, and undisclosed dogs can void it. Here's how dog-bite claims actually work.",
 kicker="Home Basics", read="5",
 lead="<p>Dog bites are one of the largest sources of homeowners liability claims — the average payout runs into the tens of thousands. The good news: your policy usually covers them. The catch: insurers have quietly built in <strong>breed exclusions, bite-history clauses, and disclosure requirements</strong> that can leave you personally on the hook for a five-figure claim.</p>",
 sections=[
  ("The short answer","<p><strong>Usually yes</strong> — a dog bite is typically covered by your <strong>personal liability</strong> coverage (the injured person's medical bills, lost wages, and your legal defense) and small injuries by <strong>medical payments</strong> coverage regardless of fault. <strong>But</strong> many insurers <strong>exclude certain breeds</strong>, exclude a dog with a <strong>prior bite</strong>, or void the claim if the dog was <strong>never disclosed</strong>. The exceptions are where people get burned.</p>"),
  ("How the two coverages work","<p><strong>Personal liability (Coverage E)</strong> handles a serious bite — the victim's medical costs, potential settlement or judgment, and your legal defense — up to your limit (commonly $100,000–$500,000). <strong>Medical payments (Coverage F)</strong> pays minor injuries ($1,000–$5,000) with no fault dispute, which can settle a small bite without a liability claim. Coverage applies whether the bite happens at your home or elsewhere (a walk, a park).</p>"),
  ("Breed restrictions and bite history","<p>This is the big one. Many insurers maintain a <strong>restricted-breed list</strong> (often pit bulls, Rottweilers, Dobermans, German Shepherds, and others) and will either <strong>exclude dog-bite liability</strong>, charge more, or <strong>decline/non-renew</strong> the policy. A few states limit breed-based underwriting. Separately, once a dog <strong>has bitten</strong>, insurers commonly exclude that specific dog going forward. Always <strong>disclose your dog</strong> — an undisclosed dog is grounds to deny the claim.</p>"),
  ("What's NOT covered","<ul><li><strong>Injuries to your own household</strong> — your policy covers third parties, not you or family members.</li><li><strong>An excluded breed or a dog with a known bite history.</strong></li><li><strong>Business/guard dogs</strong> or dogs kept for a home business.</li><li><strong>Intentional acts</strong> — commanding a dog to attack.</li><li><strong>Amounts above your liability limit</strong> — which is why an <strong>umbrella policy</strong> matters if you own a dog.</li></ul>"),
  ("Protect yourself","<ol><li><strong>Disclose the dog</strong> and confirm in writing it's covered.</li><li><strong>Carry enough liability</strong> — $300,000+ and consider a $1M umbrella; bite judgments can be large.</li><li><strong>After a bite</strong>: seek medical care for the victim, exchange info, document, and notify your insurer promptly — don't admit fault.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> dog bites are usually covered under liability, but breed exclusions, prior bites, and undisclosed dogs can void it. Disclose your dog, carry $300k+ liability (plus an umbrella), and confirm coverage in writing.",
 faq=[
  ("Does homeowners insurance cover dog bites?","Usually — personal liability coverage pays the victim's costs and your legal defense, and medical payments covers minor injuries. But breed exclusions, a prior bite, or an undisclosed dog can void the claim."),
  ("What dog breeds do insurers exclude?","It varies by insurer, but commonly pit bulls, Rottweilers, Dobermans, German Shepherds, and a few others. Some insurers exclude dog-bite liability for these breeds, charge more, or decline the policy."),
  ("What happens if my dog bites someone?","Your liability coverage generally handles the claim up to your limit. Report it to your insurer, but expect that insurer may exclude that dog going forward or non-renew after a serious bite."),
  ("How much liability coverage do I need if I own a dog?","At least $300,000, and a $1 million umbrella policy is worth it — dog-bite judgments can exceed a standard liability limit, and anything above the limit comes out of your pocket."),
  ("Will a dog bite raise my homeowners premium?","Often yes, and a serious bite can lead to that dog being excluded or the policy non-renewed. Disclosing the dog upfront is still essential — hiding it risks a denied claim."),
 ],
 cross=("/home/does-homeowners-insurance-cover.html","Does homeowners insurance cover that?")),

"does-homeowners-insurance-cover-storm-damage": dict(
 title="Does Homeowners Insurance Cover Wind, Hail &amp; Storm Damage? (2026)",
 h1="Does homeowners insurance cover storm damage? Wind and hail yes — with a catch.",
 dek="Wind, hail, and hurricane damage are covered perils — but a separate wind/hurricane deductible and depreciated roof payouts can shrink what you collect. Here's how storm claims really work.",
 kicker="Home Basics", read="6",
 lead="<p>Wind and hail are among the most common — and most misunderstood — homeowners claims. The damage itself is almost always covered. What surprises people is <strong>how much they pay out of pocket</strong>: many policies apply a separate, percentage-based <strong>wind or hurricane deductible</strong>, and older roofs get paid at depreciated value. Here's the full picture.</p>",
 sections=[
  ("The short answer","<p><strong>Yes.</strong> Wind, hail, and hurricane (the wind portion) are <strong>covered perils</strong> under a standard homeowners policy — damage to your roof, siding, windows, and belongings is covered. Two big catches: many policies carry a separate <strong>wind/hail or hurricane deductible</strong> (a percentage of your dwelling limit, not a flat dollar amount), and older roofs may be settled at <strong>actual cash value</strong>. The storm's <em>flooding</em> — surge and rising water — is never covered (that's <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-flood-damage.html\">flood</a>).</p>"),
  ("What's covered","<p>Damage from <strong>windstorms, thunderstorms, tornadoes, and the wind/rain of a hurricane</strong>: torn-off shingles and <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-roof-damage.html\">roof damage</a>, broken windows, damaged siding and gutters, a <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-tree-damage.html\">tree blown onto the house</a>, and interior/property damage once wind or hail breaches the structure. Hail damage to the roof and exterior is covered too.</p>"),
  ("The wind/hurricane deductible — the expensive surprise","<p>In wind- and hurricane-prone states, your policy likely has a <strong>separate deductible for wind, hail, or hurricane</strong>, expressed as a <strong>percentage of your dwelling coverage</strong> (typically 1%–5%) rather than a flat amount. On a $400,000 home, a 2% hurricane deductible is <strong>$8,000</strong> before the policy pays a cent. These trigger on named storms (hurricane) or any wind/hail loss (wind/hail deductible) depending on your policy. <strong>Check your declarations page</strong> for the percentage and trigger.</p>"),
  ("The roof depreciation catch","<p>Even with covered wind/hail damage, an older roof may be settled at <strong>actual cash value</strong> (depreciated) rather than full replacement — the same trap covered in the <a class=\"ca-link\" href=\"/home/does-homeowners-insurance-cover-roof-damage.html\">roof guide</a>. Some policies also carry a <strong>cosmetic-damage exclusion</strong> for hail dents on metal roofs or siding that don't affect function.</p>"),
  ("What's NOT covered","<ul><li><strong>Storm surge and flooding</strong> — rising water needs a separate flood policy, even during a hurricane.</li><li><strong>Wear and neglect</strong> — an old roof that fails isn't a wind claim.</li><li><strong>Cosmetic hail damage</strong>, if your policy excludes it.</li><li>Amounts below your <strong>wind/hurricane deductible.</strong></li></ul>"),
  ("What to do after a storm","<ol><li><strong>Document the date and damage</strong> — photos, and any local wind/hail reports.</li><li><strong>Make temporary repairs</strong> (tarp the roof) and keep receipts.</li><li><strong>Know which deductible applies</strong> before you file — a small claim may not clear a percentage hurricane deductible.</li><li><strong>Get an independent roofer's estimate</strong> and compare to the adjuster's.</li></ol>"),
 ],
 callout="<strong>Bottom line:</strong> wind and hail are covered, but a percentage-based wind/hurricane deductible and depreciated-roof payouts decide what you actually collect — and storm surge is flood, not homeowners. Know your deductible and roof settlement terms before the storm.",
 faq=[
  ("Does homeowners insurance cover wind damage?","Yes — wind is a covered peril, so damage to your roof, windows, siding, and belongings is covered. But a separate percentage-based wind/hurricane deductible may apply, and older roofs may be paid at depreciated value."),
  ("Does homeowners insurance cover hail damage?","Yes, hail is a covered peril. Roof and exterior hail damage is covered, though older roofs may be settled at actual cash value and some policies exclude purely cosmetic hail dents."),
  ("What is a hurricane or wind deductible?","A separate deductible for wind, hail, or hurricane losses, usually a percentage of your dwelling limit (1%–5%) instead of a flat amount. On a $400,000 home, a 2% deductible is $8,000 before coverage applies."),
  ("Does homeowners insurance cover hurricane damage?","The wind and rain damage from a hurricane is covered (subject to your hurricane deductible). Storm surge and flooding are not — those require a separate flood policy."),
  ("Why do I have a separate deductible for storms?","Insurers in wind- and hurricane-prone areas use percentage-based wind/hurricane deductibles to manage catastrophe risk. Check your declarations page for the percentage and what triggers it."),
 ],
 cross=("/home/does-homeowners-insurance-cover-roof-damage.html","Does homeowners insurance cover roof damage?")),
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
