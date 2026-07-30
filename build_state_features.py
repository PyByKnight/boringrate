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
]

if __name__ == '__main__':
    for cfg in FEATURES:
        build(cfg); print(f"  wrote {cfg['path']}")
