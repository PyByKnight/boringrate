# -*- coding: utf-8 -*-
"""Per-page content for gen_reactive_pages.py. Every figure is a real approved
filing in serff_filings.json. row tuple = (name, href, trk, fid, change, note, up)."""

B = 'https://boringrate.com/article/'

# ── shared VA / NY / GA context rows (reused across pages) ──
SF_VA  = ('State Farm','/article/carrier/state-farm.html','SFMA-134688491','134688491','&minus;6.5%',
          'Virginia&rsquo;s largest auto insurer <strong>cut</strong> &minus;6.5% on ~1.43M policyholders (an earlier filing cut &minus;4.0%). Eff. Dec 11, 2025.', False)
USAA_VA= ('USAA','/article/carrier/usaa.html','USAA-134728239','134728239','&minus;1.3%',
          'Cut &minus;1.3% across ~181,953 members. Eff. Mar 1, 2026.', False)
NW_VA  = ('Nationwide','/article/carrier/nationwide.html','NWPP-G134897540','134897540','&minus;5.0%',
          'Cut &minus;5.0% on part of its Virginia book. Eff. Jun 4, 2026.', False)
GEICO_VA=('GEICO','/article/carrier/geico.html','GECC-134876961','134876961','&plus;3.8%',
          'Raised &plus;3.8% on ~181,473 policyholders; range &plus;10% to &minus;28% by driver.', True)
PROG_VA =('Progressive','/article/carrier/progressive.html','PRGS-134458370','134458370','&plus;2.0%',
          'Raised &plus;2.0% on ~199,475 policyholders.', True)

SF_NY  = ('State Farm','/article/carrier/state-farm.html','SFMA-134399932','134399932','0.0%',
          'Held New York rates <strong>flat</strong> (0%). Eff. Nov 17, 2025.', False)
USAA_NY= ('USAA','/article/carrier/usaa.html','USAA-134556435','134556435','0.0%',
          'Held flat (0%) for members. Eff. Dec 18, 2025.', False)
ALL_NY = ('Allstate','/article/carrier/allstate.html','ALSE-134438903','134438903','0.0%',
          'Held flat (0%) on ~40,674 policyholders. Eff. Jun 21, 2025.', False)
GEICO_NY=('GEICO','/article/carrier/geico.html','GECC-134404337','134404337','&plus;4.9%',
          'Raised &plus;4.9% across ~1,530,960 policyholders against a &plus;8.1% indicated need. Eff. Mar 10, 2025.', True)
LM_NY  = ('Liberty Mutual','/article/carrier/liberty-mutual.html','LBPM-134738048','134738048','&plus;5.0%',
          'Raised &plus;5.0% on ~142,196 policyholders against a &plus;20.2% indication. Eff. Apr 29, 2026.', True)
TRV_NY = ('Travelers','/article/carrier/travelers.html','TRVD-G134680232','134680232','&plus;3.0%',
          'Raised &plus;3.0% on ~227,988 policyholders against a &plus;8.6% indication. Eff. Dec 29, 2025.', True)

CALL = ('    <div class="callout"><p><strong>The one stat that matters:</strong> {stat} '
        '<a class="ca-link" href="/?zip=&amp;utm_source={utm}">Compare every carrier for your exact ZIP &rarr;</a></p></div>')

PAGES = [
# ────────────────────────────── VA ERIE ──────────────────────────────
{
 'path':'article/why-did-my-erie-rate-go-up-virginia.html',
 'url': B+'why-did-my-erie-rate-go-up-virginia.html',
 'title':'Why did my Erie rate go up in Virginia?',
 'desc':'Erie raised Virginia auto rates +4.2% in 2026 - it indicated +6.9%, and the filing ranged +34% to -30% by driver. Meanwhile State Farm cut 1.4M Virginians -6.5%. The filing, and who to compare.',
 'ogdesc':'Erie raised Virginia auto rates +4.2% (it wanted +6.9%), with a +34% to -30% spread by driver - while State Farm cut 1.4M Virginians. See the filing and compare.',
 'state':'Virginia','read':'5','tracker':'/article/rate-changes/virginia.html',
 'alert':'Erie raised Virginia auto rates &plus;4.2% in 2026 &mdash; but the filing ranges &plus;34% to &minus;30% by driver.',
 'h1':'Why did my Erie rate go up in Virginia?',
 'dek':'Erie raised its Virginia auto rates <strong>&plus;4.2%</strong> in 2026 &mdash; it indicated a need for &plus;6.9% and took less &mdash; and the filing&rsquo;s own range runs from a <strong>&plus;34% increase to a 30% cut</strong> depending on the driver. Meanwhile State Farm cut 1.4 million Virginians. Here&rsquo;s the filing, and who&rsquo;s cutting.',
 'rows':[
   ('Erie','/article/carrier/erie.html','ERAP-134691371','134691371','&plus;4.2%',
    'The filing behind your increase. Approved &plus;4.2% on ~217,857 policyholders against a &plus;6.9% indicated need; the range runs <strong>&plus;34.2% to &minus;30.0%</strong> by driver. Eff. Jan 1, 2026. A <em>later</em> Erie filing then cut &minus;1.3%.', True),
   SF_VA, USAA_VA, NW_VA, GEICO_VA, PROG_VA],
 'prose':
'''    <p>If your Erie renewal in Virginia came in higher, this is the source: Erie filed for a rate increase (SERFF <strong>ERAP-134691371</strong>) and the <strong>Virginia Bureau of Insurance</strong> approved &plus;4.2%. The figures above are approved filings pulled from the public SERFF system &mdash; not estimates &mdash; and every one links to its filing.</p>

    <h2>The &plus;4.2% is an average. Your Erie change ranges &plus;34% to &minus;30%.</h2>
    <p>A statewide rate change is one blended number, but Erie didn&rsquo;t move every driver by the same amount. Its own filing reports the spread: the largest increase in the book was about <strong>&plus;34%</strong>, and the largest <em>decrease</em> was about <strong>&minus;30%</strong>. So inside a &ldquo;&plus;4.2% average,&rdquo; some Virginia Erie drivers were raised by a third and others were cut by nearly as much. Where you land depends on your ZIP, vehicle, age, claims and coverage &mdash; which is exactly why the headline average can&rsquo;t tell you whether your increase is reasonable.</p>

    <h2>Erie took less than it asked for &mdash; then started cutting</h2>
    <p>Filings separate the <em>indicated</em> change (what the actuaries said the loss data justified) from the <em>approved</em> change (what the state allowed). Erie indicated <strong>&plus;6.9%</strong> and took <strong>&plus;4.2%</strong> &mdash; it held below its own number. And a <em>later</em> Erie Virginia filing actually <strong>cut &minus;1.3%</strong>. So Erie&rsquo;s trajectory here is a carrier fine-tuning, not one racing to catch up with runaway losses &mdash; the sign of a market that has largely stabilized.</p>

'''+CALL.format(stat='Erie&rsquo;s Virginia filing ranged from <strong>&plus;34% to &minus;30%</strong> around a &plus;4.2% average. A carrier that raised you can be cutting the driver one ZIP over.', utm='va-erie')+'''

    <h2>Meanwhile, Virginia&rsquo;s biggest insurer <em>cut</em> rates</h2>
    <p>Here is what your renewal notice won&rsquo;t mention. While Erie nudged up, <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a> &mdash; the largest auto insurer in Virginia &mdash; <strong>cut &minus;6.5%</strong> on roughly 1.43 million policyholders, after an earlier &minus;4.0% cut. <a class="ca-link" href="/article/carrier/usaa.html">USAA</a> trimmed &minus;1.3% and part of <a class="ca-link" href="/article/carrier/nationwide.html">Nationwide</a>&rsquo;s book came down &minus;5.0%. Some of Virginia&rsquo;s biggest books moved <em>down</em> &mdash; so an Erie increase is a strong reason to see what a competitor would charge you today.</p>

    <h2>What to do with your renewal</h2>
    <p>Approved changes apply <strong>at renewal, not mid-term</strong>, and usually reach new customers before existing ones &mdash; so two identical drivers can pay different rates for months on timing alone. Your renewal shows Erie&rsquo;s price for your coverage; it does not tell you what State Farm, USAA or anyone else would charge for the same coverage. Running your ZIP against every carrier takes a couple of minutes and costs nothing.</p>''',
 'faq':[
  ('Why did my Erie rate go up in Virginia in 2026?',
   'Erie filed for and received an approved +4.2% Virginia auto rate increase (SERFF ERAP-134691371), effective January 1, 2026, on about 217,857 policyholders. Erie indicated it needed +6.9% but took less, and the Virginia Bureau of Insurance approved it. A later Erie filing then cut rates -1.3%.'),
  ('How much did Erie actually raise my Virginia rate?',
   'The +4.2% is a statewide average. Erie\'s own filing reports the change ranged from about +34% to about -30% depending on the driver\'s ZIP, vehicle, age and history - so many Virginia Erie drivers saw far more or far less than 4.2%, and some were cut.'),
  ('Are other Virginia auto insurers cutting rates?',
   'Yes. While Erie raised +4.2%, State Farm - Virginia\'s largest auto insurer - cut -6.5% on about 1.43 million policyholders, on top of an earlier -4.0% cut. USAA cut -1.3% and part of Nationwide\'s book fell -5.0%. An Erie increase is a strong reason to compare competitors.'),
  ('Will shopping lower my bill if Erie raised me?',
   'Possibly. Rate changes apply at renewal, not mid-term, and a carrier that raised you can be more expensive than a competitor cutting rates in your ZIP. Comparing every carrier for your exact ZIP and profile is the only way to know your lowest current price.'),
 ],
},
# ────────────────────────────── GA USAA ──────────────────────────────
{
 'path':'article/why-did-my-usaa-rate-go-up-georgia.html',
 'url': B+'why-did-my-usaa-rate-go-up-georgia.html',
 'title':'Why did my USAA rate go up in Georgia?',
 'desc':'USAA has an approved +9.9% Georgia auto increase - one of the steepest in the state - taking effect in 2026. Meanwhile State Farm cut 2 million Georgians -3% and Travelers cut -10%. The filing, and who to compare.',
 'ogdesc':'USAA\'s approved +9.9% Georgia increase is one of the steepest in the state - while State Farm cut 2M Georgians and Travelers cut -10%. See the filing and compare.',
 'state':'Georgia','read':'5','tracker':'/article/rate-changes/georgia.html',
 'alert':'USAA has an approved &plus;9.9% Georgia increase &mdash; while State Farm cut 2M Georgians and Travelers cut &minus;10%.',
 'h1':'Why did my USAA rate go up in Georgia?',
 'dek':'USAA has an approved <strong>&plus;9.9%</strong> Georgia auto increase &mdash; one of the steepest recent moves by any large carrier in the state. And the timing stands out: while USAA went up nearly ten percent, State Farm cut <strong>two million</strong> Georgians and Travelers cut ten percent. Here&rsquo;s the filing, and who&rsquo;s cutting.',
 'rows':[
   ('USAA','/article/carrier/usaa.html','USAA-134985185','134985185','&plus;9.9%',
    'The filing behind your increase. Approved &plus;9.9% on ~335,141 Georgia members &mdash; one of the steepest large-carrier moves in the state. Eff. new business Sep 21, 2026.', True),
   ('State Farm','/article/carrier/state-farm.html','SFMA-134677514','134677514','&minus;3.0%',
    'Georgia&rsquo;s largest auto insurer <strong>cut</strong> &minus;3.0% on ~2,069,411 policyholders. Eff. Nov 28, 2025.', False),
   ('Travelers','/article/carrier/travelers.html','TRVD-G134911970','134911970','&minus;10.1%',
    'Cut &minus;10.1% on ~109,120 policyholders &mdash; the biggest Georgia cut in our data. Eff. May 8, 2026.', False),
   ('Progressive','/article/carrier/progressive.html','PRGS-134655228','134655228','&minus;4.1%',
    'Cut &minus;4.1%. Eff. Dec 5, 2025.', False),
   ('GEICO','/article/carrier/geico.html','GECC-134514872','134514872','&plus;4.6%',
    'Raised &plus;4.6% on ~176,619 policyholders against a &plus;7.7% indication.', True)],
 'prose':
'''    <p>If your USAA renewal in Georgia is climbing, here is the source: USAA filed for a rate increase (SERFF <strong>USAA-134985185</strong>) and Georgia regulators approved <strong>&plus;9.9%</strong>. These are approved filings from the public SERFF system &mdash; not estimates &mdash; and each links to its filing.</p>

    <h2>A &plus;9.9% increase while the rest of the market is cutting</h2>
    <p>What makes USAA&rsquo;s Georgia increase notable isn&rsquo;t just the size &mdash; it&rsquo;s the timing. Georgia auto rates are broadly <em>softening</em> in 2026. <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, the state&rsquo;s largest insurer, <strong>cut &minus;3.0%</strong> across more than <strong>2 million</strong> policyholders; <a class="ca-link" href="/article/carrier/travelers.html">Travelers</a> cut <strong>&minus;10.1%</strong>; <a class="ca-link" href="/article/carrier/progressive.html">Progressive</a> cut &minus;4.1%. USAA moving up nearly ten percent against that backdrop is the exception, not the trend &mdash; which makes comparing your options unusually worthwhile right now.</p>

    <h2>Your increase isn&rsquo;t the average</h2>
    <p>A statewide &plus;9.9% is a blended figure; USAA reprices individually on your ZIP, vehicle, age, claims and coverage, so your actual change may be higher or lower. USAA is often among the cheapest carriers for the members it serves, and it may still be competitive for you even after this increase &mdash; but the only way to know is to compare it against the carriers that just cut.</p>

'''+CALL.format(stat='USAA is raising Georgia &plus;9.9% while State Farm cut 2 million Georgians and Travelers cut &minus;10.1%.', utm='ga-usaa')+'''

    <h2>When it hits you</h2>
    <p>USAA&rsquo;s increase takes effect for <strong>new business on Sep 21, 2026</strong>, and reaches existing members <strong>at renewal</strong> after that &mdash; not mid-term. So members renewing this fall and winter will see it first, and two identical members can pay different rates for months purely on renewal timing. Your renewal notice shows USAA&rsquo;s price; it doesn&rsquo;t tell you what State Farm, Progressive or Travelers would charge for the same coverage today.</p>

    <h2>What to do with your renewal</h2>
    <p>Given that Georgia&rsquo;s biggest books are moving <em>down</em> while USAA moves up, this is a good moment to run your ZIP and profile against every carrier. It&rsquo;s free and takes a couple of minutes &mdash; and if USAA is still your best price, you&rsquo;ll have confirmed it rather than guessed.</p>''',
 'faq':[
  ('Why did my USAA rate go up in Georgia in 2026?',
   'USAA filed for and received an approved +9.9% Georgia auto rate increase (SERFF USAA-134985185), effective for new business September 21, 2026, on about 335,141 members. It is one of the steepest recent large-carrier increases in the state, and Georgia regulators approved it.'),
  ('Is +9.9% a big USAA increase for Georgia?',
   'Yes, especially in context. Most large Georgia carriers are cutting in 2026: State Farm cut -3.0% across more than 2 million policyholders, Travelers cut -10.1%, and Progressive cut -4.1%. USAA raising nearly 10% is the exception, which makes comparing your options unusually valuable.'),
  ('Should I switch from USAA after this increase?',
   'Not necessarily. USAA is often among the cheapest carriers for the members it serves, so it may still be competitive even after +9.9%. The way to know is to compare USAA against the carriers that just cut Georgia rates for your exact ZIP and profile.'),
  ('When does the USAA Georgia increase take effect?',
   'It applies to new business starting September 21, 2026, and reaches existing members at renewal after that - not mid-term. Members renewing in late 2026 will see it first, so two identical members can pay different rates for months based on renewal timing.'),
 ],
},
# ────────────────────────────── NY GEICO ──────────────────────────────
{
 'path':'article/why-did-my-geico-rate-go-up-new-york.html',
 'url': B+'why-did-my-geico-rate-go-up-new-york.html',
 'title':'Why did my GEICO rate go up in New York?',
 'desc':'GEICO\'s most recent approved New York auto increase was +4.9% - but its actuaries indicated +8.1%, so more may be coming. Meanwhile State Farm, USAA and Allstate held New York rates flat. The filing, and who to compare.',
 'ogdesc':'GEICO raised New York auto rates +4.9% across 1.5M policyholders - and indicated it needed +8.1%. State Farm, USAA and Allstate held flat. See the filing and compare.',
 'state':'New York','read':'5','tracker':'/article/rate-changes/new-york.html',
 'alert':'GEICO raised New York auto rates &plus;4.9% across 1.5M drivers &mdash; and its own math said &plus;8.1%.',
 'h1':'Why did my GEICO rate go up in New York?',
 'dek':'GEICO&rsquo;s most recent approved New York auto increase was <strong>&plus;4.9%</strong> across roughly 1.5 million policyholders &mdash; and the state approved it. But GEICO&rsquo;s own actuaries said it needed <strong>&plus;8.1%</strong>, so it took less than the full indication, and the gap tends to return. Here&rsquo;s the filing, and which big New York carriers held flat.',
 'rows':[ GEICO_NY, LM_NY, TRV_NY, SF_NY, USAA_NY, ALL_NY ],
 'prose':
'''    <p>If your GEICO renewal in New York came in higher, here is the source: GEICO filed for a rate increase (SERFF <strong>GECC-134404337</strong>) and the <strong>New York Department of Financial Services</strong> approved &plus;4.9%. These are approved filings from the public SERFF system &mdash; not estimates &mdash; and each links to its filing.</p>

    <h2>GEICO took less than it asked for &mdash; which usually means more is coming</h2>
    <p>Filings separate the <em>indicated</em> change (what GEICO&rsquo;s actuaries said the loss data justified) from the <em>approved</em> change (what the state allowed). GEICO indicated <strong>&plus;8.1%</strong> and took <strong>&plus;4.9%</strong> &mdash; leaving roughly three points of its own indicated need unfilled. Carriers typically return with a follow-up filing to close a gap like that, so a New York GEICO customer should expect continued upward pressure. That is a reason to lock in a better price now rather than after the next increase lands.</p>

    <h2>Your increase isn&rsquo;t the average</h2>
    <p>A statewide &plus;4.9% is a blended figure. GEICO reprices individually on your ZIP, vehicle, age, claims and coverage, so your actual change can be higher or lower than the headline. The only way to know whether your number is competitive is to compare carriers for your specific profile.</p>

'''+CALL.format(stat='GEICO&rsquo;s indicated need was &plus;8.1% but it only took &plus;4.9% &mdash; the gap tends to show up in a later filing.', utm='ny-geico')+'''

    <h2>Meanwhile, New York&rsquo;s other big insurers held flat</h2>
    <p>Not everyone raised. While GEICO, <a class="ca-link" href="/article/carrier/liberty-mutual.html">Liberty Mutual</a> (&plus;5.0%) and <a class="ca-link" href="/article/carrier/travelers.html">Travelers</a> (&plus;3.0%) moved up, <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, <a class="ca-link" href="/article/carrier/usaa.html">USAA</a> and <a class="ca-link" href="/article/carrier/allstate.html">Allstate</a> all filed New York rates <strong>flat at 0%</strong>. A carrier that held flat while GEICO raised you may now be cheaper for the same coverage &mdash; and you won&rsquo;t know unless you check.</p>

    <h2>What to do with your renewal</h2>
    <p>Approved changes apply <strong>at renewal, not mid-term</strong>, and usually reach new customers before existing ones. Your renewal shows GEICO&rsquo;s price for your coverage; it does not tell you what State Farm, USAA or Allstate would charge for the same coverage today. Running your ZIP against every carrier takes a couple of minutes and costs nothing &mdash; and with GEICO&rsquo;s indicated need still unfilled, it&rsquo;s worth doing before you renew.</p>''',
 'faq':[
  ('Why did my GEICO rate go up in New York?',
   'GEICO filed for and received an approved +4.9% New York auto rate increase (SERFF GECC-134404337), effective for new business March 10, 2025, across about 1.53 million policyholders. Its actuarial indication was +8.1%, so GEICO took less than its own data justified, and the New York Department of Financial Services approved it.'),
  ('Is GEICO going to raise my New York rate again?',
   'Possibly. GEICO indicated it needed +8.1% but took only +4.9%, leaving about three points of its own indicated need unfilled. Carriers commonly return with a follow-up filing to close that gap, so continued upward pressure is likely.'),
  ('Did other New York insurers raise rates too?',
   'Some did and some did not. Liberty Mutual raised +5.0% and Travelers +3.0%, but State Farm, USAA and Allstate all held their New York rates flat at 0%. A carrier that held flat may now be cheaper than GEICO for the same coverage.'),
  ('Will shopping lower my bill if GEICO raised me?',
   'It can. Rate changes apply at renewal, not mid-term, and competitors that held flat can undercut a carrier that just raised you. Comparing every carrier for your exact ZIP and profile is the only way to know your lowest current price.'),
 ],
},
# ────────────────────────── NY LIBERTY MUTUAL ─────────────────────────
{
 'path':'article/why-did-my-liberty-mutual-rate-go-up-new-york.html',
 'url': B+'why-did-my-liberty-mutual-rate-go-up-new-york.html',
 'title':'Why did my Liberty Mutual rate go up in New York?',
 'desc':'Liberty Mutual raised New York auto rates +5.0% in 2026 - but its filing indicated +20.2%, so a large gap remains unfilled. Meanwhile State Farm, USAA and Allstate held flat. The filing, and who to compare.',
 'ogdesc':'Liberty Mutual asked New York for +20.2% and was approved for +5.0% - a big unfilled gap that points to more increases. State Farm and USAA held flat. See the filing and compare.',
 'state':'New York','read':'5','tracker':'/article/rate-changes/new-york.html',
 'alert':'Liberty Mutual asked New York for &plus;20.2% and got &plus;5.0% &mdash; the gap usually means more is coming.',
 'h1':'Why did my Liberty Mutual rate go up in New York?',
 'dek':'Liberty Mutual raised its New York auto rates <strong>&plus;5.0%</strong> in 2026 &mdash; but the filing shows it actually indicated a need for <strong>&plus;20.2%</strong>. That four-fold gap between what it asked for and what it took is the real story, and it points one direction. Here&rsquo;s the filing, and which New York carriers held flat.',
 'rows':[ LM_NY, GEICO_NY, TRV_NY, SF_NY, USAA_NY, ALL_NY ],
 'prose':
'''    <p>If your Liberty Mutual renewal in New York climbed, here is the source: Liberty Mutual filed for a rate increase (SERFF <strong>LBPM-134738048</strong>) and the <strong>New York Department of Financial Services</strong> approved &plus;5.0%. These are approved filings from the public SERFF system &mdash; not estimates &mdash; and each links to its filing.</p>

    <h2>Liberty Mutual asked for &plus;20.2% and got &plus;5.0%</h2>
    <p>Filings separate the <em>indicated</em> change (what the actuaries said the loss data justified) from the <em>approved</em> change (what the state allowed). Liberty Mutual indicated <strong>&plus;20.2%</strong> and was held to <strong>&plus;5.0%</strong> &mdash; roughly a quarter of what its own math called for. That doesn&rsquo;t mean its costs are covered; it means about fifteen points of indicated need are still <em>unfilled</em>. Carriers refile to close a gap that size, so a New York Liberty Mutual customer should plan on continued increases &mdash; which is a strong reason to see what a competitor charges before the next one arrives.</p>

    <h2>Your &plus;5.0% isn&rsquo;t the average for everyone</h2>
    <p>A statewide &plus;5.0% is blended; Liberty Mutual reprices individually on your ZIP, vehicle, age, claims and coverage, so your actual change may be higher or lower. The headline number can&rsquo;t tell you whether you&rsquo;re on a competitive price &mdash; only a comparison for your profile can.</p>

'''+CALL.format(stat='Liberty Mutual indicated <strong>&plus;20.2%</strong> in New York but took only &plus;5.0% &mdash; the unfilled gap tends to return as another increase.', utm='ny-liberty')+'''

    <h2>Meanwhile, New York&rsquo;s biggest insurers held flat</h2>
    <p>Not everyone raised. While Liberty Mutual, <a class="ca-link" href="/article/carrier/geico.html">GEICO</a> (&plus;4.9%) and <a class="ca-link" href="/article/carrier/travelers.html">Travelers</a> (&plus;3.0%) moved up, <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, <a class="ca-link" href="/article/carrier/usaa.html">USAA</a> and <a class="ca-link" href="/article/carrier/allstate.html">Allstate</a> all filed New York rates <strong>flat at 0%</strong>. Against a carrier that just took +5% with +15 points still to come, a competitor holding flat can look very different at renewal.</p>

    <h2>What to do with your renewal</h2>
    <p>Approved changes apply <strong>at renewal, not mid-term</strong>, and usually reach new customers first. Your renewal shows Liberty Mutual&rsquo;s price for your coverage; it does not tell you what State Farm, USAA or GEICO would charge for the same coverage today. Running your ZIP against every carrier is free and takes a couple of minutes &mdash; and with a large indicated gap unfilled, it&rsquo;s worth doing now.</p>''',
 'faq':[
  ('Why did my Liberty Mutual rate go up in New York in 2026?',
   'Liberty Mutual filed for and received an approved +5.0% New York auto rate increase (SERFF LBPM-134738048), effective April 29, 2026, on about 142,196 policyholders. Its actuarial indication was +20.2%, so the state held it to about a quarter of what its own data called for.'),
  ('Liberty Mutual asked for how much in New York?',
   'Liberty Mutual indicated it needed +20.2% but was approved for only +5.0%. That leaves roughly fifteen points of its own indicated need unfilled - a gap carriers typically try to close with follow-up filings.'),
  ('Will Liberty Mutual raise my New York rate again?',
   'It is likely. With about fifteen points of indicated need still unfilled after this +5.0% increase, continued upward pressure is probable. Comparing competitors now, before the next filing, is the reliable move.'),
  ('Did other New York insurers raise rates too?',
   'Some did and some did not. GEICO raised +4.9% and Travelers +3.0%, but State Farm, USAA and Allstate held their New York rates flat at 0%. A carrier that held flat may now be cheaper than Liberty Mutual for the same coverage.'),
 ],
},
]
