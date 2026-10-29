#!/usr/bin/env python3
"""State-level 'who cut and who raised in [state] 2026' narrative features — the
higher-volume, cut-market-proof lane (model: tennessee-rates-dropping.html). Built
via gen_reactive_pages.build() for a consistent shell + the 5-col rate table, but
kept OUT of gen_reactive_config.PAGES so they don't pollute the reactive hub /
contextual-link manifest. Every figure links to its approved SERFF filing."""
from gen_reactive_pages import build
from gen_reactive_config import CALL

FEATURES = [
{
 'path':'home/illinois-home-insurance-increases.html',
 'url':'https://boringrate.com/home/illinois-home-insurance-increases.html',
 'title':'Illinois home insurance rose 54% in three years',
 'desc':'State Farm has raised Illinois homeowners rates three times since 2023, compounding to +54% across 1.49 million policyholders. Every filing, from the state\'s own records - and who raised less.',
 'ogdesc':'Three State Farm filings since 2023 compound to +54% on 1.49 million Illinois homeowners. The filings, the amounts, and which carriers moved least.',
 'state':'Illinois','read':'5','tracker':'/home/rate-changes/illinois.html',
 'ledger':'serff_home_filings.json','tool':'/home/',
 'alert':'Illinois home rates: State Farm has compounded <strong>&plus;54%</strong> across 1.49 million policyholders since 2023.',
 'h1':'Illinois home insurance rose 54% in three years',
 'dek':'Three State Farm filings since 2023 compound to <strong>&plus;54%</strong> on <strong>1.49 million</strong> Illinois homeowners &mdash; and each one was approved for less than the company said it needed. Every figure below comes from Illinois&rsquo; own public filing records.',
 'rows':[
   ('State Farm','/home/carrier/state-farm.html','SFMA-135045614','135045614','&plus;7.9%','', True),
   ('Erie','/home/carrier/erie.html','ERPP-135045878','135045878','&plus;8.9%','', True),
   ('American Family','/home/carrier/american-family.html','AMFC-135002345','135002345','0.0%','', False)],
 'prose':
"""    <p>Illinois publishes more rate detail than almost any state. Its Department of Insurance runs
    its own filing database &mdash; not SERFF &mdash; carrying each filing&rsquo;s indicated change,
    the change actually taken, the policyholder count and the spread. That makes it possible to do
    something you normally cannot: follow one company&rsquo;s book, filing by filing, over years.</p>

    <h2>State Farm: three filings, &plus;54% compounded</h2>
    <p>State Farm is the largest home insurer in Illinois by a wide margin &mdash; roughly
    <strong>1.49 million policyholders</strong>. Since late 2023 it has filed three times:</p>
    <table style="width:100%;border-collapse:collapse;font-size:15px;margin:14px 0;max-width:660px;">
    <thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;">
    <th style="padding:8px 6px;">Filed</th><th style="padding:8px 6px;">Taken</th><th style="padding:8px 6px;">Wanted</th><th style="padding:8px 6px;">Running total</th></tr></thead>
    <tbody>
    <tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;">Feb 2024</td><td style="padding:8px 6px;"><strong>&plus;12.3%</strong></td><td style="padding:8px 6px;color:var(--ink-mute);">&plus;13.6%</td><td style="padding:8px 6px;">&plus;12.3%</td></tr>
    <tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;">Jun 2025</td><td style="padding:8px 6px;"><strong>&plus;27.2%</strong></td><td style="padding:8px 6px;color:var(--ink-mute);">&plus;32.5%</td><td style="padding:8px 6px;">&plus;42.8%</td></tr>
    <tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;">Aug 2026</td><td style="padding:8px 6px;"><strong>&plus;7.9%</strong></td><td style="padding:8px 6px;color:var(--ink-mute);">&plus;12.5%</td><td style="padding:8px 6px;"><strong>&plus;54.1%</strong></td></tr>
    </tbody></table>
    <p>Rate changes stack. A renewal notice shows only the latest one, so a household that has been
    with State Farm since 2023 has absorbed all three &mdash; <strong>&plus;54%</strong> compounded,
    not the &plus;7.9% on this year&rsquo;s letter.</p>

    <h2>Every one was approved for less than requested</h2>
    <p>In all three filings State Farm&rsquo;s own analysis called for more than it took:
    &plus;13.6% against &plus;12.3%, &plus;32.5% against &plus;27.2%, &plus;12.5% against
    &plus;7.9%. A carrier that repeatedly takes less than its indication is carrying an unclosed
    gap, and that gap is the single best predictor that another filing is coming.</p>
    <p>The 2026 filing also reports its own spread: individual changes ran from
    <strong>&plus;36.5% to &minus;9.4%</strong>. The &ldquo;&plus;7.9% average&rdquo; is a blend, and
    which end you landed on depends on your ZIP, roof and claims history.</p>

    <h2>Not every Illinois insurer moved like this</h2>
    <p>The three-year picture varies more than the headlines suggest. <strong>American Family</strong>
    compounded <strong>&plus;43.9%</strong> over four filings on about 69,000 policyholders, and
    <strong>Erie</strong> &plus;18.3%. On the auto side the spread is wider still: <strong>Kemper</strong>
    has compounded <strong>&plus;139%</strong> in three years across four filings, while
    <strong>Allstate</strong> &mdash; a far larger Illinois book at roughly 371,000 drivers &mdash;
    moved only <strong>&plus;7.7%</strong> over the same period.</p>
    <p>That dispersion is the practical point. These carriers price the same state, the same weather
    and the same repair costs, and over three years they have diverged by tens of percentage points.
    Staying put through a stretch like that is a decision, even when it does not feel like one.</p>
    <p style="font-size:14px;margin:10px 0;"><a class="ca-link" href="/home/rate-changes/illinois.html">See every approved Illinois home rate filing &rarr;</a></p>
""",
 'faq':[
  ('How much have Illinois home insurance rates gone up?',
   'State Farm, the largest home insurer in Illinois with about 1.49 million policyholders, has filed three rate increases since late 2023: +12.3% in February 2024, +27.2% in June 2025 and +7.9% in August 2026. Compounded, that is +54.1%. Other carriers vary widely - American Family compounded +43.9% over the same period and Erie +18.3%.'),
  ('Why is my increase bigger than the percentage in the filing?',
   'Two reasons. Rate changes compound, and your renewal notice shows only the most recent one - a household with State Farm since 2023 has absorbed all three filings, not just the latest. And a statewide figure is an average: State Farm\'s 2026 filing reports individual changes ranging from +36.5% to -9.4% depending on ZIP, roof and claims history.'),
  ('Where does this data come from?',
   'The Illinois Department of Insurance publishes its own Company Rate Information database, separate from SERFF, which records each filing\'s indicated change, the change taken, the policyholder count and the minimum and maximum change. Every figure on this page comes from that record.'),
 ],
},
{
 'path':'home/georgia-farm-bureau-rate-cut-blocked.html',
 'url':'https://boringrate.com/home/georgia-farm-bureau-rate-cut-blocked.html',
 'title':'Georgia blocked a home insurance rate CUT in 2026',
 'desc':'Georgia Farm Bureau asked to cut homeowners rates 5.2% - a $7.8M reduction across 90,296 households - and the state said no. The reason: the cut was paid for with a mandatory deductible above $1,500.',
 'ogdesc':'Georgia Farm Bureau filed to CUT home rates 5.2% for 90,296 households. The Department disapproved it, because the saving came from forcing a higher mandatory deductible. The filing, in full.',
 'state':'Georgia','read':'5','tracker':'/home/rate-changes/georgia.html',
 'ledger':'serff_home_filings.json','tool':'/home/',
 'alert':'Georgia&rsquo;s largest home insurer asked to <strong>cut</strong> rates 5.2%. The state disapproved it.',
 'h1':'Georgia blocked a home insurance rate cut in 2026',
 'dek':'Georgia Farm Bureau filed to <strong>lower</strong> homeowners premiums by 5.2% &mdash; nearly <strong>$7.8 million</strong> across <strong>90,296 households</strong> &mdash; and the Department of Insurance <strong>disapproved it</strong>. The objection was not the price. It was how the saving was paid for.',
 'rows':[
   ('Georgia Farm Bureau','/article/carrier/georgia-farm-bureau.html','GFBR-134795612','134795612','&minus;5.2%',
    'Disapproved 03/23/2026. Requested effective 02/01/2027.', False),
   ('Georgia Farm Bureau','/article/carrier/georgia-farm-bureau.html','GFBR-134859106','134859106','0.0%','', False),
   ('Georgia Farm Bureau','/article/carrier/georgia-farm-bureau.html','GFBR-134707855','134707855','0.0%','', False),
   ('American Family','/home/carrier/american-family.html','AMFC-134883419','134883419','&plus;7.6%','', True),
   ('Amica','/home/carrier/amica.html','AMMA-134467010','134467010','&plus;9.8%','', True),
   ('Safeco','/home/carrier/safeco.html','LBPM-134861427','134861427','&plus;9.9%','', True)],
 'prose':
"""    <p>On 23 March 2026 the Georgia Department of Insurance disapproved a rate filing from
    <strong>Georgia Farm Bureau Mutual</strong>, the state&rsquo;s largest home insurer. That is
    unusual on its own &mdash; disapprovals are rare. What makes this one worth reading is the
    direction: the filing asked to make insurance <em>cheaper</em>.</p>

    <h2>The carrier asked for less than its own analysis said it needed</h2>
    <p>Filing <strong>GFBR-134795612</strong> covers Compass Homeowners, Georgia Farm Bureau&rsquo;s
    owner-occupied program. Its own actuarial indication said the book needed
    <strong>&plus;5.1%</strong>. The company instead requested <strong>&minus;5.2%</strong> &mdash; a
    premium reduction of <strong>$7,786,865</strong> across <strong>90,296 policyholders</strong>,
    with individual changes running from no change down to <strong>&minus;13.3%</strong>.</p>

    <h2>The Department&rsquo;s reason, in full</h2>
    <div class="callout"><p>&ldquo;The Department has taken the position of not allowing mandatory
    deductibles higher than $1,500.&rdquo;<br>
    <span style="font-size:13px;color:var(--ink-mute);">&mdash; Georgia Department of Insurance,
    disposition dated 23 March 2026</span></p></div>
    <p>That single line is the whole decision. The regulator did not object to the price. It objected
    to how the price was reached: the lower premium was financed by moving policyholders onto a
    <strong>mandatory deductible above $1,500</strong>. A homeowner would pay less each year and more
    at the moment of a claim.</p>
    <p>Read that way the decision is a judgment about what counts as a saving. A cut that shifts risk
    onto the household is not the same product at a lower price &mdash; it is a cheaper, thinner
    product. Georgia decided homeowners should not be moved onto one without a choice.</p>

    <h2>What it means for the rest of the market</h2>
    <p>Georgia Farm Bureau has filed four times on this book in the current window. Three were
    approved at <strong>0.0%</strong>; the fourth, the cut above, was disapproved. So the carrier
    that looks like it is simply holding rates steady is in fact the one carrier that tried to move
    them <em>down</em> and was stopped.</p>
    <p>Everyone else moved the other way. Twelve Georgia home insurers raised rates in the same
    period and none cut &mdash; American Family &plus;7.6% on 28,722 households, Amica &plus;9.8%,
    Safeco &plus;9.9%, Homesite &plus;12.9%. Against that backdrop, a blocked 5.2% decrease is the
    only downward pressure the Georgia home market saw this year.</p>

    <h2>What to do with this</h2>
    <p>If you are insured with Georgia Farm Bureau, your rate did not change &mdash; and the reduction
    you might have received in February 2027 is not coming in its current form. If you are with one
    of the carriers that raised, the gap between you and the market has widened. Either way the
    comparison is worth running.</p>
    <p style="font-size:14px;margin:10px 0;"><a class="ca-link" href="/home/rate-changes/georgia.html">See every approved Georgia home rate filing &rarr;</a></p>
""",
 'faq':[
  ('Why did Georgia disapprove a rate decrease?',
   'The Department of Insurance objected to the mechanism, not the price. Georgia Farm Bureau proposed funding the 5.2% premium reduction by moving policyholders onto a mandatory deductible above $1,500, and the Department stated it does not allow mandatory deductibles at that level. The disposition is dated 23 March 2026.'),
  ('How much would Georgia Farm Bureau customers have saved?',
   'The filing requested a 5.2% decrease worth $7,786,865 in total premium across 90,296 policyholders, with individual changes ranging from no change to a 13.3% reduction. It would have taken effect 1 February 2027 had it been approved.'),
  ('Is Georgia Farm Bureau raising home rates?',
   'No. Its other three filings in this window were all approved at 0.0%, so its rates are unchanged. That is notable because twelve other Georgia home insurers raised rates in the same period and none cut - including American Family at +7.6%, Amica at +9.8% and Safeco at +9.9%.'),
 ],
},
{
 'path':'article/virginia-car-insurance-rate-changes-2026.html',
 'url':'https://boringrate.com/article/virginia-car-insurance-rate-changes-2026.html',
 'title':'Virginia car insurance rate changes in 2026: who cut and who raised',
 'desc':'Virginia\'s biggest auto insurer cut rates for 1.4 million drivers in 2026, while GEICO, Erie, Allstate and Liberty Mutual raised. Every approved SERFF filing - who cut, who raised, and whether your renewal reflects it.',
 'ogdesc':'State Farm cut 1.4M Virginia drivers -6.5% in 2026 while GEICO, Erie and Allstate nudged up - several below what their actuaries wanted. See every approved filing and compare.',
 'state':'Virginia','read':'6','tracker':'/article/rate-changes/virginia.html',
 'alert':'Virginia 2026: State Farm cut 1.4M drivers &minus;6.5% while GEICO, Erie and Allstate nudged up.',
 'h1':'Virginia car insurance rate changes in 2026: who cut and who raised',
 'dek':'Virginia&rsquo;s biggest auto insurer cut rates for <strong>1.4 million drivers</strong> in 2026 &mdash; but several large carriers went the other way, and a few held well below what their own actuaries said they needed. Every figure below links to its approved SERFF filing.',
 'rows':[
   ('State Farm','/article/carrier/state-farm.html','SFMA-134688491','134688491','&minus;6.5%','', False),
   ('USAA','/article/carrier/usaa.html','USAA-134728239','134728239','&minus;1.3%','', False),
   ('Nationwide','/article/carrier/nationwide.html','NWPP-G134897540','134897540','&minus;5.0%','', False),
   ('GEICO','/article/carrier/geico.html','GECC-134876961','134876961','&plus;3.8%','', True),
   ('Erie','/article/carrier/erie.html','ERAP-134691371','134691371','&plus;4.2%','', True),
   ('Progressive','/article/carrier/progressive.html','PRGS-134458370','134458370','&plus;2.0%','', True),
   ('Allstate','/article/carrier/allstate.html','ALSE-134970309','134970309','&plus;3.0%','', True),
   ('Liberty Mutual','/article/carrier/liberty-mutual.html','LBPM-134893945','134893945','&plus;4.0%','', True)],
 'prose':
'''    <p>These are approved <strong>Virginia Bureau of Insurance</strong> filings, pulled from the public SERFF system &mdash; not estimates. Every figure above links to its filing by tracking number. The headline: Virginia&rsquo;s largest auto insurer cut rates hard, several big carriers raised modestly, and the changes reach drivers at renewal &mdash; not all at once.</p>

    <h2>The State Farm story</h2>
    <p><a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a> is the biggest auto insurer in Virginia, and it <strong>cut &minus;6.5%</strong> on roughly <strong>1.43 million</strong> policyholders (SFMA-134688491), on top of an earlier &minus;4.0% cut. That is the single largest rate action in the state this year, and it moves the market: when the biggest book gets cheaper, every other carrier&rsquo;s price looks higher by comparison. <a class="ca-link" href="/article/carrier/usaa.html">USAA</a> trimmed &minus;1.3% across ~182,000 members, and part of <a class="ca-link" href="/article/carrier/nationwide.html">Nationwide</a>&rsquo;s book came down &minus;5.0%.</p>

    <h2>Who raised &mdash; and who held back</h2>
    <p>Several large carriers went up, but modestly, and the filings show most took <em>less</em> than their own actuaries said they needed &mdash; which usually means more is coming. <a class="ca-link" href="/article/carrier/erie.html">Erie</a> raised &plus;4.2% against a &plus;6.9% indication; <a class="ca-link" href="/article/carrier/allstate.html">Allstate</a> took &plus;3.0% against a &plus;10% indication; <a class="ca-link" href="/article/carrier/geico.html">GEICO</a> took exactly its indicated &plus;3.8%. <a class="ca-link" href="/article/carrier/progressive.html">Progressive</a> came in at &plus;2.0%. None of these is a spike &mdash; Virginia in 2026 is a long way from the double-digit increases of 2025 &mdash; but the unfilled indications at Erie and Allstate point to continued upward pressure at renewal.</p>

    <div class="callout"><p><strong>The backdrop:</strong> auto rates nationally are rising far more slowly in 2026 than the ~18% spike of 2025, and many carriers are now filing outright decreases. Virginia is a clear example: the biggest book cut, and the raises are small. If your carrier is one of the ones that went up, the odds a competitor is cheaper are unusually good right now.</p></div>

    <h2>The widest spread: Liberty Mutual, &plus;82% to &minus;18%</h2>
    <p>A statewide average hides how differently drivers are treated. <a class="ca-link" href="/article/carrier/liberty-mutual.html">Liberty Mutual</a>&rsquo;s &plus;4.0% filing ranged from about <strong>&plus;82%</strong> at the top to about <strong>&minus;18%</strong> at the bottom &mdash; one of the widest spreads in the state. GEICO&rsquo;s &plus;3.8% ran &plus;10% to &minus;28%; Erie&rsquo;s &plus;4.2% ran &plus;34% to &minus;30%. In other words, two drivers with the same carrier can see wildly different renewals depending on ZIP, vehicle, age and history. The average describes the book, not you.</p>

    <h2>Why your renewal might not reflect this yet</h2>
    <p>Approved changes are statewide averages, and they apply <strong>at renewal, not mid-term</strong> &mdash; and a cut usually reaches <em>new</em> customers first. So two identical drivers can pay different rates for months purely on renewal timing. Your renewal notice shows your carrier&rsquo;s price for your coverage; it does not tell you what a competitor would charge for the same coverage today.</p>

'''+CALL.format(stat='Virginia&rsquo;s biggest insurer just cut 1.4 million drivers while others raised &mdash; the gap between what you pay and the best price is unusually wide.', utm='va-feature')+'''

    <h2>What to do</h2>
    <p>If State Farm, USAA or Nationwide cut and you&rsquo;re with a carrier that raised, you are the exact driver who benefits from shopping. And even if your carrier cut, the spread means your individual change may not match the headline. Comparing every carrier for your ZIP and profile is free and takes a couple of minutes &mdash; the only way to know whether you&rsquo;re on the best current Virginia price.</p>''',
 'faq':[
  ('Did Virginia car insurance rates go up or down in 2026?',
   'Both, depending on the carrier. State Farm - Virginia\'s largest auto insurer - cut -6.5% on about 1.43 million policyholders (after an earlier -4.0% cut), USAA cut -1.3%, and part of Nationwide\'s book fell -5.0%. Meanwhile GEICO raised +3.8%, Erie +4.2%, Allstate +3.0%, Liberty Mutual +4.0% and Progressive +2.0%. These are approved Virginia Bureau of Insurance filings.'),
  ('Which Virginia insurer cut rates the most?',
   'State Farm, the state\'s largest, cut -6.5% on roughly 1.43 million policyholders (SERFF SFMA-134688491), on top of an earlier -4.0% cut - the biggest rate action in Virginia in 2026.'),
  ('If my Virginia carrier cut rates, will my bill go down automatically?',
   'Not necessarily. Approved changes are statewide averages and apply at renewal, not mid-term, and often reach new customers before existing ones. Individual changes also vary widely - some carriers\' filings ranged from large increases to large cuts by driver. Re-shopping is the reliable way to capture the lowest current rate.'),
 ],
},
# ────────────────────────────── OHIO ──────────────────────────────
{
 'path':'article/ohio-car-insurance-rate-changes-2026.html',
 'url':'https://boringrate.com/article/ohio-car-insurance-rate-changes-2026.html',
 'title':'Ohio car insurance rate changes in 2026: who cut and who raised',
 'desc':'Almost every big Ohio auto insurer cut rates in 2026 - State Farm -4.2%, GEICO -4.9%, Progressive -4.4%, Erie -3.8%. A couple raised. Every approved SERFF filing, and whether your renewal reflects it.',
 'ogdesc':'Ohio\'s biggest auto carriers cut in 2026 - State Farm, GEICO, Progressive and Erie all down. See every approved filing and compare.',
 'state':'Ohio','read':'6','tracker':'/article/rate-changes/ohio.html',
 'alert':'Ohio 2026: State Farm, GEICO, Progressive and Erie all cut rates &mdash; a broadly cheaper market.',
 'h1':'Ohio car insurance rate changes in 2026: who cut and who raised',
 'dek':'Almost every big auto insurer in Ohio cut rates in 2026 &mdash; State Farm, GEICO, Progressive and Erie all moved down. A couple nudged up, and one held back a double-digit increase. Every figure below links to its approved SERFF filing.',
 'rows':[
   ('GEICO','/article/carrier/geico.html','GECC-134888669','134888669','&minus;4.9%','', False),
   ('State Farm','/article/carrier/state-farm.html','SFMA-134699767','134699767','&minus;4.2%','', False),
   ('Progressive','/article/carrier/progressive.html','PRGS-134729388','134729388','&minus;4.4%','', False),
   ('Erie','/article/carrier/erie.html','ERAP-134872060','134872060','&minus;3.8%','', False),
   ('Allstate','/article/carrier/allstate.html','ALSE-134879528','134879528','&minus;3.0%','', False),
   ('Auto-Owners','/article/carrier/auto-owners.html','AOIC-134774421','134774421','&minus;1.3%','', False),
   ('Grange',None,'GRAN-134743417','134743417','&plus;1.9%','', True),
   ('Liberty Mutual','/article/carrier/liberty-mutual.html','LBPM-134878625','134878625','&plus;2.0%','', True)],
 'prose':
'''    <p>These are approved <strong>Ohio Department of Insurance</strong> filings, pulled from the public SERFF system &mdash; not estimates. Every figure above links to its filing by tracking number. The headline: Ohio in 2026 is a broadly <em>cheaper</em> market, with nearly every large carrier cutting.</p>

    <h2>A broadly cheaper market</h2>
    <p>The cuts are led by the biggest books. <a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a> cut &minus;4.2% on roughly <strong>2.3 million</strong> policyholders; <a class="ca-link" href="/article/carrier/geico.html">GEICO</a> cut &minus;4.9% (against a &minus;11.5% indication &mdash; it could have cut more); <a class="ca-link" href="/article/carrier/progressive.html">Progressive</a> cut &minus;4.4%; <a class="ca-link" href="/article/carrier/erie.html">Erie</a> &minus;3.8%; <a class="ca-link" href="/article/carrier/allstate.html">Allstate</a> &minus;3.0%. When this many large carriers move down at once, staying on an old policy is the expensive choice &mdash; new-business rates are where the cuts land first.</p>

    <h2>Who raised &mdash; and the one holding back</h2>
    <p>A few carriers went up. <a class="ca-link" href="/article/carrier/liberty-mutual.html">Liberty Mutual</a> raised &plus;2.0%. The one to watch is Grange: it took only &plus;1.9%, but its filing indicated a need of <strong>&plus;17.1%</strong> &mdash; a fifteen-point gap between what its actuaries said it needed and what it took. Gaps that large tend to close through follow-up filings, so Grange customers should expect continued increases even though this one was small.</p>

    <div class="callout"><p><strong>The backdrop:</strong> auto rates nationally are rising far more slowly in 2026 than the ~18% spike of 2025, and many carriers are now filing outright decreases. Ohio is one of the clearest examples &mdash; the biggest books are cutting, so if you haven&rsquo;t re-shopped, your renewal is likely higher than it needs to be.</p></div>

    <h2>Your change isn&rsquo;t the statewide average</h2>
    <p>Every figure above is a book-wide average, but carriers reprice individually &mdash; the same filing can range from a double-digit increase to a double-digit cut depending on your ZIP, vehicle, age and history. A carrier that cut &minus;4% on average may still have raised <em>your</em> profile, and vice versa. The only way to know where you land is to compare for your exact situation.</p>

'''+CALL.format(stat='Nearly every big Ohio carrier cut rates in 2026 &mdash; if you haven&rsquo;t re-shopped, you&rsquo;re likely on an old, higher price.', utm='oh-feature')+'''

    <h2>Why your renewal might not reflect this yet</h2>
    <p>Approved cuts are statewide averages and apply <strong>at renewal, not mid-term</strong>, usually reaching new customers before existing ones. So two identical drivers can pay different rates for months on timing alone. Your renewal shows your carrier&rsquo;s price; it doesn&rsquo;t tell you what a competitor would charge for the same coverage today &mdash; and in a market cutting this broadly, that gap is worth checking. It&rsquo;s free and takes a couple of minutes.</p>''',
 'faq':[
  ('Did Ohio car insurance rates go down in 2026?',
   'For most large carriers, yes. Approved Ohio Department of Insurance filings show State Farm cut -4.2% on about 2.3 million policyholders, GEICO -4.9%, Progressive -4.4%, Erie -3.8% and Allstate -3.0%. A few raised: Liberty Mutual +2.0% and Grange +1.9% (though Grange indicated it needed +17.1%).'),
  ('Which Ohio insurer cut rates the most?',
   'Among large carriers, GEICO cut the most at -4.9% (its indication was -11.5%, so it could have cut further), followed by Progressive -4.4% and State Farm -4.2% on its ~2.3 million-policyholder book.'),
  ('If my Ohio carrier cut rates, will my bill go down automatically?',
   'Not necessarily. Approved cuts are statewide averages, apply at renewal rather than mid-term, and often reach new customers first. Your individual change also depends on your profile. Re-shopping is the reliable way to capture the lowest current Ohio rate.'),
 ],
},
# ────────────────────────────── MICHIGAN ──────────────────────────────
{
 'path':'article/michigan-car-insurance-rate-changes-2026.html',
 'url':'https://boringrate.com/article/michigan-car-insurance-rate-changes-2026.html',
 'title':'Michigan car insurance rate changes in 2026: who cut and who raised',
 'desc':'Michigan - the most expensive auto insurance state - saw State Farm cut 1.3M drivers -4.9% in 2026, with mostly small moves elsewhere and a few regional raises. Every approved SERFF filing.',
 'ogdesc':'Michigan 2026: State Farm cut 1.3M drivers -4.9%, most other moves were small, and regional insurers like Frankenmuth raised. See every filing and compare.',
 'state':'Michigan','read':'6','tracker':'/article/rate-changes/michigan.html',
 'alert':'Michigan 2026: State Farm cut 1.3M drivers &minus;4.9%; most other moves were small.',
 'h1':'Michigan car insurance rate changes in 2026: who cut and who raised',
 'dek':'Michigan has the most expensive car insurance in the country, so every rate change matters. In 2026 State Farm cut <strong>1.3 million</strong> drivers &minus;4.9%, most big carriers made small moves, and a few regional insurers raised. Every figure below links to its approved SERFF filing.',
 'rows':[
   ('State Farm','/article/carrier/state-farm.html','SFMA-134697302','134697302','&minus;4.9%','', False),
   ('Progressive','/article/carrier/progressive.html','PRGS-134782430','134782430','&minus;2.8%','', False),
   ('Auto-Owners','/article/carrier/auto-owners.html','AOIC-134765723','134765723','&minus;0.9%','', False),
   ('Allstate','/article/carrier/allstate.html','ALSE-134840116','134840116','&minus;0.5%','', False),
   ('National General',None,'GMMX-134756538','134756538','&minus;0.9%','', False),
   ('The Hanover',None,'HNVR-G134685654','134685654','&plus;0.9%','', True),
   ('Bristol West','/article/carrier/bristol-west.html','BRWS-134728991','134728991','&plus;2.1%','', True),
   ('Frankenmuth',None,'FRNK-134683592','134683592','&plus;4.6%','', True)],
 'prose':
'''    <p>These are approved <strong>Michigan Department of Insurance and Financial Services</strong> filings, pulled from the public SERFF system &mdash; not estimates. Every figure above links to its filing by tracking number. Because Michigan has the highest premiums in the country, even a small percentage change is real money.</p>

    <h2>State Farm leads the cuts</h2>
    <p><a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, Michigan&rsquo;s largest auto insurer, cut &minus;4.9% on roughly <strong>1.3 million</strong> policyholders. <a class="ca-link" href="/article/carrier/progressive.html">Progressive</a> cut &minus;2.8%, and <a class="ca-link" href="/article/carrier/auto-owners.html">Auto-Owners</a> and <a class="ca-link" href="/article/carrier/allstate.html">Allstate</a> made smaller trims. On the country&rsquo;s most expensive book, a &minus;4.9% State Farm cut is a larger dollar move than a bigger percentage would be almost anywhere else.</p>

    <h2>Small moves and regional raises</h2>
    <p>Most of the market barely moved, but a few regional carriers went up: Frankenmuth raised &plus;4.6% (against an &plus;11.3% indication, so more may follow), <a class="ca-link" href="/article/carrier/bristol-west.html">Bristol West</a> &plus;2.1%, and The Hanover &plus;0.9%. In a high-premium state, a modest raise from your carrier while State Farm cuts is exactly the situation where switching can save real money.</p>

    <div class="callout"><p><strong>One Michigan caveat:</strong> since the 2019 no-fault reform, your premium depends heavily on the <strong>PIP medical coverage level</strong> you chose (unlimited, $500k, $250k, $50k or opt-out). A statewide-average rate change applies across those tiers, so your actual price and change can differ more than in other states. Comparing carriers at <em>your</em> PIP level is the only apples-to-apples read.</p></div>

    <h2>Your change isn&rsquo;t the statewide average</h2>
    <p>Every figure above is a book-wide average; carriers reprice individually on your ZIP, vehicle, age, history and PIP choice. A carrier that cut on average may still have raised your profile. The only way to know where you land &mdash; and whether a competitor is cheaper &mdash; is to compare for your exact situation.</p>

'''+CALL.format(stat='Michigan has the country&rsquo;s highest premiums, so even a small rate gap between carriers is real money &mdash; compare yours.', utm='mi-feature')+'''

    <h2>What to do with your renewal</h2>
    <p>Approved changes apply <strong>at renewal, not mid-term</strong>, and usually reach new customers first. Your renewal shows your carrier&rsquo;s price for your coverage and PIP level; it doesn&rsquo;t tell you what a competitor would charge. On the most expensive book in the country, running your ZIP against every carrier is worth doing before you renew &mdash; it&rsquo;s free and takes a couple of minutes.</p>''',
 'faq':[
  ('Did Michigan car insurance rates go down in 2026?',
   'The biggest carrier did: State Farm cut -4.9% on about 1.3 million Michigan policyholders. Progressive cut -2.8% and Auto-Owners and Allstate made smaller trims. A few regional insurers raised, including Frankenmuth +4.6%, Bristol West +2.1% and The Hanover +0.9%. These are approved Michigan DIFS filings.'),
  ('Why is Michigan car insurance so expensive?',
   'Michigan has historically had the highest auto premiums in the country, largely due to its no-fault system and unlimited personal injury protection (PIP). The 2019 reform let drivers choose lower PIP levels, so your premium now depends heavily on the PIP coverage you select - which also means statewide-average rate changes affect drivers differently.'),
  ('If my Michigan carrier cut rates, will my bill go down automatically?',
   'Not necessarily. Approved cuts are statewide averages, apply at renewal rather than mid-term, and often reach new customers first. Your change also depends on your ZIP, profile and PIP level. Re-shopping at your PIP level is the reliable way to capture the lowest current rate.'),
 ],
},
# ────────────────────────────── GEORGIA ──────────────────────────────
{
 'path':'article/georgia-car-insurance-rate-changes-2026.html',
 'url':'https://boringrate.com/article/georgia-car-insurance-rate-changes-2026.html',
 'title':'Georgia car insurance rate changes in 2026: who cut and who raised',
 'desc':'Georgia split in 2026 - State Farm cut 2M drivers -3% and Travelers cut -10%, while USAA raised +9.9% and GEICO +4.6%. Every approved SERFF filing, and who to compare.',
 'ogdesc':'Georgia 2026 split: State Farm cut 2M drivers and Travelers cut -10%, while USAA raised +9.9% and GEICO +4.6%. See every filing and compare.',
 'state':'Georgia','read':'5','tracker':'/article/rate-changes/georgia.html',
 'alert':'Georgia 2026: State Farm cut 2M drivers and Travelers cut &minus;10%, while USAA and GEICO raised.',
 'h1':'Georgia car insurance rate changes in 2026: who cut and who raised',
 'dek':'Georgia&rsquo;s 2026 market split cleanly: State Farm cut <strong>two million</strong> drivers and Travelers cut ten percent, while USAA and GEICO went the other way. Which side your carrier landed on decides whether shopping pays off. Every figure links to its approved SERFF filing.',
 'rows':[
   ('State Farm','/article/carrier/state-farm.html','SFMA-134677514','134677514','&minus;3.0%','', False),
   ('Travelers','/article/carrier/travelers.html','TRVD-G134911970','134911970','&minus;10.1%','', False),
   ('GEICO','/article/carrier/geico.html','GECC-134514872','134514872','&plus;4.6%','', True),
   ('USAA','/article/carrier/usaa.html','USAA-134985185','134985185','&plus;9.9%','', True)],
 'prose':
'''    <p>These are approved <strong>Georgia Office of Insurance</strong> filings, pulled from the public SERFF system &mdash; not estimates. Every figure above links to its filing by tracking number. Unlike most states in 2026, Georgia did not move in one direction: its biggest books cut, while two major carriers raised.</p>

    <h2>The cutters: State Farm and Travelers</h2>
    <p><a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, Georgia&rsquo;s largest auto insurer, cut &minus;3.0% on more than <strong>2 million</strong> policyholders. <a class="ca-link" href="/article/carrier/travelers.html">Travelers</a> cut the hardest at <strong>&minus;10.1%</strong> &mdash; and even that was less than its &minus;24% indication, meaning its own math supported an even deeper cut. When the largest book and the biggest cutter are both moving down, the market&rsquo;s floor is dropping.</p>

    <h2>The raisers: USAA and GEICO</h2>
    <p>Two major carriers went the other way. <a class="ca-link" href="/article/why-did-my-usaa-rate-go-up-georgia.html">USAA raised &plus;9.9%</a> &mdash; one of the steepest large-carrier increases in the state &mdash; and <a class="ca-link" href="/article/why-did-my-geico-rate-go-up-georgia.html">GEICO raised &plus;4.6%</a> (against a &plus;7.7% indication, so more may follow). If you&rsquo;re with USAA or GEICO in Georgia, you raised while the market&rsquo;s biggest books cut &mdash; the widest possible gap between your renewal and the best available price.</p>

    <div class="callout"><p><strong>Why the split matters:</strong> in a market where some carriers cut and others raise, your savings from shopping are larger than usual &mdash; you&rsquo;re not comparing against a market that all moved together. A Georgia driver whose carrier raised can often find a competitor that just cut.</p></div>

    <h2>Your change isn&rsquo;t the statewide average</h2>
    <p>Every figure above is a book-wide average; carriers reprice individually on your ZIP, vehicle, age and history, so your actual change may be higher or lower. The only way to know whether you&rsquo;re on a competitive Georgia price is to compare carriers for your specific profile.</p>

'''+CALL.format(stat='Georgia split in 2026 &mdash; State Farm and Travelers cut while USAA and GEICO raised. If your carrier raised, a competitor likely cut.', utm='ga-feature')+'''

    <h2>What to do with your renewal</h2>
    <p>Approved changes apply <strong>at renewal, not mid-term</strong>, and usually reach new customers first. Your renewal shows your carrier&rsquo;s price; it doesn&rsquo;t tell you what State Farm, Travelers or anyone else would charge for the same coverage today. With Georgia&rsquo;s market split, running your ZIP against every carrier is unusually likely to pay off &mdash; it&rsquo;s free and takes a couple of minutes.</p>''',
 'faq':[
  ('Did Georgia car insurance rates go up or down in 2026?',
   'Both, split by carrier. State Farm cut -3.0% on more than 2 million policyholders and Travelers cut -10.1%, while USAA raised +9.9% and GEICO +4.6%. These are approved Georgia Office of Insurance filings.'),
  ('Which Georgia insurer cut rates the most?',
   'Travelers cut the most at -10.1% - and its indication was -24%, so its own data supported an even deeper cut. State Farm, the largest insurer, cut -3.0% across more than 2 million policyholders.'),
  ('My USAA or GEICO rate went up in Georgia - should I switch?',
   'It is worth comparing. USAA raised +9.9% and GEICO +4.6% while State Farm and Travelers cut, so the gap between what you pay and the best available price is unusually wide. Compare every carrier for your exact ZIP and profile to see your lowest current rate.'),
 ],
},
# ────────────────────────────── ILLINOIS ──────────────────────────────
{
 'path':'article/illinois-car-insurance-rate-changes-2026.html',
 'url':'https://boringrate.com/article/illinois-car-insurance-rate-changes-2026.html',
 'title':'Illinois car insurance rate changes in 2026: who cut and who raised',
 'desc':'Illinois was one of 2026\'s biggest cutting markets - State Farm cut 3.3M drivers -9.4%, Country Financial -6%, American Family -5%. But Kemper raised +41.5%. Every approved SERFF filing.',
 'ogdesc':'Illinois 2026: State Farm cut 3.3M drivers -9.4% and most carriers cut - but Kemper raised +41.5%. See every filing and compare.',
 'state':'Illinois','read':'6','tracker':'/article/rate-changes/illinois.html',
 'alert':'Illinois 2026: State Farm cut 3.3M drivers &minus;9.4% and most carriers cut &mdash; but Kemper raised &plus;41.5%.',
 'h1':'Illinois car insurance rate changes in 2026: who cut and who raised',
 'dek':'Illinois was one of the biggest cutting markets of 2026 &mdash; State Farm cut <strong>3.3 million</strong> drivers &minus;9.4%, and Country Financial, American Family, Travelers and Shelter all followed. One carrier went the other way, hard: <a class="ca-link" href="/article/why-did-my-kemper-rate-go-up-illinois.html">Kemper raised &plus;41.5%</a>. Every figure links to its approved SERFF filing.',
 'rows':[
   ('State Farm','/article/carrier/state-farm.html','SFMA-134704563','134704563','&minus;9.4%','', False),
   ('Country Financial','/article/carrier/country-financial.html','CFPC-134703367','134703367','&minus;6.0%','', False),
   ('American Family','/article/carrier/american-family.html','AMFC-134924309','134924309','&minus;5.0%','', False),
   ('Travelers','/article/carrier/travelers.html','TRVD-G134637362','134637362','&minus;3.0%','', False),
   ('Shelter','/article/carrier/shelter.html','SHEL-134682271','134682271','&minus;2.8%','', False),
   ('Progressive','/article/carrier/progressive.html','PRGS-134970180','134970180','&minus;1.7%','', False),
   ('Farmers','/article/carrier/farmers.html','FARM-134792823','134792823','&plus;2.3%','', True),
   ('GEICO','/article/carrier/geico.html','GECC-134888662','134888662','&plus;1.0%','', True)],
 'prose':
'''    <p>These are approved <strong>Illinois Department of Insurance</strong> filings, pulled from the public SERFF system &mdash; not estimates. Every figure above links to its filing by tracking number. Illinois was one of the most one-sided markets of 2026: almost everyone cut, and the cuts were deep.</p>

    <h2>State Farm leads a broad, deep cut</h2>
    <p><a class="ca-link" href="/article/carrier/state-farm.html">State Farm</a>, the state&rsquo;s largest insurer, cut <strong>&minus;9.4%</strong> across <strong>3.3 million</strong> Illinois policyholders &mdash; one of the single largest rate actions in the country this year. <a class="ca-link" href="/article/carrier/country-financial.html">Country Financial</a> cut &minus;6.0%, <a class="ca-link" href="/article/carrier/american-family.html">American Family</a> &minus;5.0%, <a class="ca-link" href="/article/carrier/travelers.html">Travelers</a> &minus;3.0% and <a class="ca-link" href="/article/carrier/shelter.html">Shelter</a> &minus;2.8%. When the biggest book drops nearly ten percent and the rest of the market follows, an unshopped renewal is almost certainly overpriced.</p>

    <h2>The exception: Kemper, &plus;41.5%</h2>
    <p>One carrier went the opposite way, and dramatically. <a class="ca-link" href="/article/why-did-my-kemper-rate-go-up-illinois.html">Kemper raised &plus;41.5%</a> &mdash; and its own actuaries backed it (a &plus;41.7% indication), meaning its loss experience on that book ran far ahead of its prices. If you&rsquo;re a Kemper customer in Illinois, you were repriced hard in a market where nearly everyone else was cutting &mdash; the strongest shop-now signal there is.</p>

    <div class="callout"><p><strong>The backdrop:</strong> auto rates nationally are rising far more slowly in 2026 than the ~18% spike of 2025, and Illinois went further than most &mdash; a broad, deep round of cuts led by State Farm. If you haven&rsquo;t re-shopped, the gap between your price and the market is unusually wide.</p></div>

    <h2>Your change isn&rsquo;t the statewide average</h2>
    <p>Every figure above is a book-wide average; carriers reprice individually on your ZIP, vehicle, age and history, so your actual change may be higher or lower. A carrier that cut on average may still have raised your profile. Comparing for your exact situation is the only way to know where you land.</p>

'''+CALL.format(stat='State Farm cut 3.3 million Illinoisans &minus;9.4% and most carriers followed &mdash; an unshopped renewal is almost certainly overpriced.', utm='il-feature')+'''

    <h2>What to do with your renewal</h2>
    <p>Approved cuts apply <strong>at renewal, not mid-term</strong>, and usually reach new customers first. Your renewal shows your carrier&rsquo;s price; it doesn&rsquo;t tell you what a competitor would charge for the same coverage today. In a market that cut this broadly, running your ZIP against every carrier is worth doing before you renew &mdash; it&rsquo;s free and takes a couple of minutes.</p>''',
 'faq':[
  ('Did Illinois car insurance rates go down in 2026?',
   'For nearly every large carrier, yes, and steeply. State Farm cut -9.4% on about 3.3 million policyholders, Country Financial -6.0%, American Family -5.0%, Travelers -3.0% and Shelter -2.8%. The exception was Kemper, which raised +41.5%. These are approved Illinois Department of Insurance filings.'),
  ('Which Illinois insurer cut rates the most?',
   'Among large carriers, State Farm cut the most in scale at -9.4% across about 3.3 million policyholders - one of the largest rate actions in the country in 2026 - followed by Country Financial -6.0% and American Family -5.0%.'),
  ('Why did my Kemper rate go up in Illinois when everyone else cut?',
   'Kemper raised +41.5% (a +41.7% indication) because its loss experience on that Illinois book ran far ahead of its prices - the kind of correction seen on higher-risk books. In a market where almost everyone else cut, it is a strong signal to compare competitors. See our full explainer on the Kemper Illinois filing.'),
 ],
},
]

if __name__ == '__main__':
    for cfg in FEATURES:
        build(cfg); print(f"  wrote {cfg['path']}")
