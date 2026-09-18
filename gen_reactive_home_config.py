# -*- coding: utf-8 -*-
"""Per-page content for the HOME reactive pages, consumed by gen_reactive_pages.py.

Parallel to gen_reactive_config.py (auto). Every figure is a real approved filing in
serff_home_filings.json — keep them accurate; the whole value of these pages is that the
numbers are primary-source and citable.

Two things differ structurally from the auto side:

1. `ledger`/`tool` are set per page. Home pages cite serff_home_filings.json and send the
   ZIP CTA to /home/ — an auto page's /?zip= would drop a homeowner into the auto tool.
2. The home market is overwhelmingly RAISING. Auto pages could open with "meanwhile State
   Farm cut 1.4M Virginians"; in home, OH runs 11 raising to 4 cutting and VA 9 to 2. So the
   bridge is "almost everyone raised — here is the short list who didn't", which is a starker
   and more useful contrast than the auto equivalent.

USAA is the lead because it is the one carrier with a coherent multi-state story: it raised
home rates in all eight states we hold filings for, from +3.8% (VA) to +15.8% (OH). Each page
carries that context, so a reader learns their increase is a national posture, not local bad luck.
"""

H = 'https://boringrate.com/home/'
LEDGER = 'serff_home_filings.json'
TOOL = '/home/'

# USAA raised home rates in every state we hold a filing for. Reused across pages.
USAA_MULTISTATE = (
    '<p>This is not a Virginia problem or an Ohio problem. USAA raised homeowners rates in '
    '<strong>every one of the eight states we hold 2026 filings for</strong> &mdash; Ohio '
    '&plus;15.8%, Illinois &plus;12.3%, Louisiana &plus;9.2%, Texas &plus;8.5%, California '
    '&plus;6.9%, Pennsylvania &plus;6.2%, New York &plus;5.6% and Virginia &plus;3.8%. Across '
    'just the six where the filings disclose a policy count, that is about '
    '<strong>778,000 households</strong>. If your USAA homeowners premium jumped, it is a '
    'company-wide repricing, not a local surprise.</p>')

PAGES = [
# ─────────────────────────────── USAA · OHIO ───────────────────────────────
{
 'ledger': LEDGER, 'tool': TOOL,
 'path': 'home/why-did-my-usaa-home-rate-go-up-ohio.html',
 'url': H + 'why-did-my-usaa-home-rate-go-up-ohio.html',
 'title': 'Why did my USAA home insurance rate go up in Ohio?',
 'desc': 'USAA raised Ohio homeowners rates +15.8% in 2026 across ~105,620 households - and the '
         'filing ranges +63.7% to -25.8% by home. See the approved filing and who is cutting Ohio home rates.',
 'ogdesc': 'USAA raised Ohio home insurance rates +15.8% on ~105,620 households, with a +63.7% to '
           '-25.8% spread by home. See the filing and who is cutting in Ohio.',
 'state': 'Ohio', 'read': '5', 'tracker': '/home/rate-changes/ohio.html',
 'alert': 'USAA raised Ohio home insurance rates &plus;15.8% in 2026 &mdash; the filing ranges '
          '&plus;63.7% to &minus;25.8% by home.',
 'h1': 'Why did my USAA home insurance rate go up in Ohio?',
 'dek': 'USAA raised its Ohio homeowners rates <strong>&plus;15.8%</strong> in 2026 across about '
        '105,620 households &mdash; the largest home increase we have recorded in the state &mdash; '
        'and the filing&rsquo;s own range runs from a <strong>&plus;63.7% increase to a 25.8% '
        'cut</strong> depending on the house. Here is the filing, why your bill may have moved far '
        'more than 15.8%, and the four carriers that cut Ohio home rates instead.',
 'topzip': 'See what every home insurer would charge for your ZIP:',
 'rows': [
   ('USAA', '/home/carrier/usaa.html', 'USAA-134785241', '134785241', '&plus;15.8%',
    'The filing behind your increase. Approved &plus;15.8% on ~105,620 households; the range runs '
    '&plus;63.7% to &minus;25.8% by home. Eff. Mar 16, 2026.', True),
   ('Grange', '', 'GRAN-134602478', '134602478', '&plus;5.7%',
    'Raised &plus;5.7% on ~99,058 households against an &plus;11.7% indicated need.', True),
   ('Ohio Mutual', '', 'OHMG-134556446', '134556446', '&plus;7.3%',
    'Raised &plus;7.3% on ~32,269 households &mdash; exactly its indicated need.', True),
   ('Westfield Insurance', '', 'WSFG-G134594507', '134594507', '&plus;6.5%',
    'Raised &plus;6.5% on ~36,278 households.', True),
   ('Erie', '/home/carrier/erie.html', 'ERPP-134602360', '134602360', '&plus;2.3%',
    'Raised a comparatively mild &plus;2.3% on ~44,036 households.', True),
   ('Nationwide', '/home/carrier/nationwide.html', 'NWPP-134566078', '134566078', '0.0%',
    'Held Ohio home rates flat on ~153,888 households &mdash; the largest book in the state.', False),
   ('Auto-Owners', '/home/carrier/auto-owners.html', 'AOIC-134804388', '134804388', '0.0%',
    'Held flat on ~141,511 households.', False),
   ('Liberty Mutual', '/home/carrier/liberty-mutual.html', 'LBPM-134602374', '134602374', '&minus;5.0%',
    'Cut &minus;5.0% on ~19,371 households &mdash; the biggest Ohio home cut we have recorded.', False),
   ('Celina', '', 'CEIN-134649665', '134649665', '&minus;4.0%',
    'Cut &minus;4.0% on ~7,234 households.', False),
   ('Allstate', '/home/carrier/allstate.html', 'ALSE-134545764', '134545764', '&minus;3.0%',
    'Cut &minus;3.0% on ~7,802 households.', False),
 ],
 'prose': '''    <h2>What the filing actually says</h2>
    <p>USAA&rsquo;s approved Ohio homeowners increase is <strong>&plus;15.8%</strong>, effective
    March 16, 2026, on roughly <strong>105,620 households</strong>. That is the headline number, and
    it is the number that will be quoted anywhere this filing gets mentioned. It is also not
    your rate.</p>
    <p>The filing discloses its own spread: individual policies move anywhere from
    <strong>&plus;63.7%</strong> to <strong>&minus;25.8%</strong>. A statewide average of &plus;15.8%
    is the weighted midpoint of that range, so whether you landed near the top or the bottom depends
    on your roof age, construction, claims history, protection class, and where in Ohio the house
    sits. If your renewal jumped far more than 15.8%, the filing is not contradicting you &mdash; it
    explicitly allows for it.</p>
''' + USAA_MULTISTATE + '''
    <h2>Who is cutting Ohio home rates</h2>
    <p>Ohio&rsquo;s home market is not uniformly rising, but the cutters are the minority: we
    recorded <strong>eleven carriers raising and four cutting</strong>. The cuts are real, though,
    and they are concentrated in carriers with smaller Ohio books &mdash; which is usually a sign of
    a carrier trying to grow rather than one retreating.</p>
    <p><strong>Liberty Mutual</strong> cut <strong>&minus;5.0%</strong> on about 19,371 Ohio
    households, the largest home cut in the state we have on file. <strong>Celina</strong> cut
    &minus;4.0% and <strong>Allstate</strong> cut &minus;3.0%. Just as usefully,
    <strong>Nationwide</strong> and <strong>Auto-Owners</strong> &mdash; who together carry nearly
    300,000 Ohio households, far more than USAA &mdash; both held rates <strong>flat</strong>. A
    carrier holding flat while your carrier takes &plus;15.8% is a real competitive gap.</p>
    <h2>Does USAA eligibility change the math?</h2>
    <p>USAA only writes for military members, veterans and their families, and it consistently
    scores near the top on claims satisfaction. That combination means many members never shop, and
    USAA&rsquo;s pricing reflects an unusually loyal book. It is worth knowing that USAA&rsquo;s
    reputation is earned on <em>service</em>, not on being the cheapest &mdash; and a
    &plus;15.8% year is exactly when that distinction shows up on the bill. Comparing costs you
    nothing and does not affect your eligibility to come back.</p>
    <h2>What to do about it</h2>
    <p>A homeowners rate change lands at renewal, so the increase is already in the premium you were
    quoted. Three things worth doing before you pay it: check your <strong>dwelling coverage
    amount</strong> is still right (rebuild costs rose sharply, but so did some carriers&rsquo;
    automatic inflation adjustments &mdash; you may be insured above replacement cost), ask what a
    <strong>higher deductible</strong> does to the premium, and get comparison quotes from the
    carriers above that cut or held flat. Bundling auto and home with one carrier is often the single
    largest discount available, so price the pair together rather than each alone.</p>
''',
 'faq': [
   ('How much did USAA raise home insurance rates in Ohio?',
    'USAA received approval for a +15.8% statewide average homeowners rate increase in Ohio '
    '(SERFF USAA-134785241), effective March 16, 2026, affecting about 105,620 households. The '
    'filing discloses that individual policies move between +63.7% and -25.8%, so a specific '
    'home can be far above or below the 15.8% average.'),
   ('Why did my USAA home premium go up more than 15.8%?',
    'Because 15.8% is a statewide average, not a per-policy change. USAA’s own filing states '
    'the range runs from +63.7% to -25.8% depending on the individual home — roof age, '
    'construction type, protection class, claims history and location within Ohio all shift where '
    'a given policy lands in that range.'),
   ('Which home insurers cut rates in Ohio?',
    'Liberty Mutual cut -5.0% on about 19,371 Ohio households, Celina cut -4.0% and Allstate cut '
    '-3.0%. Nationwide (~153,888 households) and Auto-Owners (~141,511) both held Ohio home rates '
    'flat. Eleven carriers raised rates in the same period, so the cutters are a minority.'),
   ('Is USAA still worth it if the rate went up?',
    'USAA scores consistently well on claims handling and is restricted to military members, '
    'veterans and their families. Those are real reasons members stay. But a +15.8% increase is '
    'precisely when it is worth pricing alternatives — comparing quotes does not affect your '
    'USAA eligibility, and carriers that just held flat or cut may now be materially cheaper.'),
 ],
},
# ───────────────────────────── USAA · VIRGINIA ─────────────────────────────
{
 'ledger': LEDGER, 'tool': TOOL,
 'path': 'home/why-did-my-usaa-home-rate-go-up-virginia.html',
 'url': H + 'why-did-my-usaa-home-rate-go-up-virginia.html',
 'title': 'Why did my USAA home insurance rate go up in Virginia?',
 'desc': 'USAA raised Virginia homeowners rates +3.8% in 2026 across ~307,356 households - but the '
         'filing ranges +36.5% to -31.0% by home. See the approved filing and who is cutting Virginia home rates.',
 'ogdesc': 'USAA raised Virginia home rates +3.8% on ~307,356 households, with a +36.5% to -31.0% '
           'spread by home. See the filing and who is cutting.',
 'state': 'Virginia', 'read': '5', 'tracker': '/home/rate-changes/virginia.html',
 'alert': 'USAA raised Virginia home insurance rates &plus;3.8% across ~307,356 households &mdash; '
          'the filing ranges &plus;36.5% to &minus;31.0% by home.',
 'h1': 'Why did my USAA home insurance rate go up in Virginia?',
 'dek': 'USAA raised its Virginia homeowners rates <strong>&plus;3.8%</strong> in 2026 across about '
        '<strong>307,356 households</strong> &mdash; its largest home book in any state we track. '
        'The average sounds mild; the filing&rsquo;s own range runs <strong>&plus;36.5% to '
        '&minus;31.0%</strong> by home. Here is the filing, and the two Virginia carriers that cut '
        'instead.',
 'topzip': 'See what every home insurer would charge for your ZIP:',
 'rows': [
   ('USAA', '/home/carrier/usaa.html', 'USAA-134827676', '134827676', '&plus;3.8%',
    'The filing behind your increase. Approved &plus;3.8% (premium-weighted across four USAA '
    'entities) on ~307,356 households against a &plus;4.5% indicated need; range &plus;36.5% to '
    '&minus;31.0%. Eff. Apr 20, 2026.', True),
   ('Progressive', '/home/carrier/progressive.html', 'AMSI-134485084', '134485084', '&plus;10.0%',
    'Raised &plus;10.0% on ~48,058 households against a &plus;13.1% indication &mdash; the steepest '
    'Virginia home increase we recorded.', True),
   ('Erie', '/home/carrier/erie.html', 'ERPP-134682697', '134682697', '&plus;8.0%',
    'Raised &plus;8.0% on ~167,000 households against an &plus;11.0% indication; range &plus;40.0% '
    'to &minus;48.2%.', True),
   ('Auto-Owners', '/home/carrier/auto-owners.html', 'AOIC-134474539', '134474539', '&plus;6.7%',
    'Raised &plus;6.7% on ~32,641 households.', True),
   ('Virginia Farm Bureau', '', 'VRFB-134994651', '134994651', '&plus;3.8%',
    'Raised &plus;3.8% on ~60,100 households against a &plus;5.4% indication.', True),
   ('Nationwide', '/home/carrier/nationwide.html', 'NWPP-134558137', '134558137', '&plus;3.6%',
    'Raised &plus;3.6% on ~110,801 households; the widest spread in the state at &plus;92.9% to '
    '&minus;82.2%.', True),
   ('State Farm', '/home/carrier/state-farm.html', 'SFMA-134760355', '134760355', '&plus;1.7%',
    'Virginia&rsquo;s largest home insurer raised just &plus;1.7% on ~608,900 households.', True),
   ('Allstate', '/home/carrier/allstate.html', 'ALSE-134728018', '134728018', '&plus;0.6%',
    'Raised &plus;0.6% on ~124,116 households &mdash; effectively flat.', True),
   ('Homesite', '', 'HMSS-134894183', '134894183', '&minus;0.4%',
    'Cut &minus;0.4% on ~64,917 households.', False),
   ('Amica', '/home/carrier/amica.html', 'AMMA-134932424', '134932424', '&minus;3.0%',
    'Cut &minus;3.0% on ~11,079 households &mdash; its own analysis indicated it could have cut '
    '&minus;8.0%.', False),
 ],
 'prose': '''    <h2>What the filing actually says</h2>
    <p>USAA&rsquo;s approved Virginia homeowners increase is <strong>&plus;3.8%</strong>, effective
    April 20, 2026. That figure is a premium-weighted average across USAA&rsquo;s four Virginia
    entities &mdash; United Services Automobile Association, USAA Casualty, USAA General Indemnity
    and Garrison &mdash; which between them cover about <strong>307,356 households</strong>. It is
    the largest USAA home book in any state we track.</p>
    <p>&plus;3.8% reads like a quiet year. The filing&rsquo;s own disclosed range says otherwise:
    individual policies move from <strong>&plus;36.5%</strong> to <strong>&minus;31.0%</strong>.
    That is a 67-point spread sitting underneath a 3.8% headline. USAA also indicated it needed
    &plus;4.5% and filed slightly below that &mdash; a carrier pricing under its own indication is
    usually one that comes back.</p>
''' + USAA_MULTISTATE + '''
    <h2>Virginia&rsquo;s home market: nearly everyone raised</h2>
    <p>We recorded <strong>nine carriers raising Virginia home rates and two cutting</strong>. In
    that context &plus;3.8% is genuinely middling &mdash; and two of Virginia&rsquo;s biggest
    insurers did better. <strong>State Farm</strong>, the largest home writer in the state with
    about 608,900 households, raised only <strong>&plus;1.7%</strong>. <strong>Allstate</strong>
    raised <strong>&plus;0.6%</strong>, effectively flat.</p>
    <p>At the other end, <strong>Progressive</strong> took <strong>&plus;10.0%</strong> and
    <strong>Erie</strong> <strong>&plus;8.0%</strong>. Only two carriers cut:
    <strong>Amica</strong> at <strong>&minus;3.0%</strong> &mdash; notable because its own analysis
    indicated it could have cut a full &minus;8.0% &mdash; and <strong>Homesite</strong> at
    &minus;0.4%.</p>
    <p>One number in the table deserves its own mention. <strong>Nationwide</strong>&rsquo;s
    &plus;3.6% average carries a range of <strong>&plus;92.9% to &minus;82.2%</strong>. That is the
    widest spread in any Virginia home filing we hold, and a reminder that a carrier&rsquo;s
    statewide average can tell you almost nothing about what it will quote your particular house.</p>
    <h2>What to do about it</h2>
    <p>Check three things before paying the renewal. First, your <strong>dwelling coverage
    amount</strong> &mdash; rebuild costs rose sharply and many carriers apply automatic inflation
    adjustments, so it is worth confirming you are not insured well above replacement cost. Second,
    what a <strong>higher deductible</strong> does to the premium. Third, quotes from State Farm,
    Allstate, Amica and Homesite, all of which either cut or came in far below USAA this cycle.
    Bundling home and auto together is usually the largest single discount available, so price the
    pair rather than the home policy alone.</p>
''',
 'faq': [
   ('How much did USAA raise home insurance rates in Virginia?',
    'USAA received approval for a +3.8% premium-weighted average homeowners increase in Virginia '
    '(SERFF USAA-134827676), effective April 20, 2026, across about 307,356 households in four '
    'USAA entities. The filing discloses a range of +36.5% to -31.0% for individual policies.'),
   ('Why did my USAA home premium rise more than 3.8%?',
    'The 3.8% is a statewide, premium-weighted average across USAA’s four Virginia companies. '
    'USAA’s filing states individual policies move between +36.5% and -31.0% depending on the '
    'home — roof age, construction, claims history and location all determine where a given '
    'policy lands.'),
   ('Which home insurers raised Virginia rates the least?',
    'State Farm, the state’s largest home insurer with about 608,900 households, raised only '
    '+1.7%. Allstate raised +0.6%. Amica cut -3.0% and Homesite cut -0.4%. At the other end '
    'Progressive raised +10.0% and Erie +8.0%.'),
   ('Did USAA ask Virginia for more than it received?',
    'USAA’s actuarial analysis indicated a +4.5% need and it filed +3.8%, slightly below its '
    'own indication. A carrier pricing below its indicated need is under-earning on the book, which '
    'often means a further filing follows.'),
 ],
},
# ─────────────────────────── STATE FARM · LOUISIANA ────────────────────────
{
 'ledger': LEDGER, 'tool': TOOL,
 'path': 'home/why-did-my-state-farm-home-rate-go-up-louisiana.html',
 'url': H + 'why-did-my-state-farm-home-rate-go-up-louisiana.html',
 'title': 'Why did my State Farm home insurance rate go up in Louisiana?',
 'desc': 'State Farm raised Louisiana homeowners rates +9.7% in 2026 across ~303,638 households - '
         'the largest home book in the state. See the approved filing and the two carriers cutting Louisiana home rates.',
 'ogdesc': 'State Farm raised Louisiana home rates +9.7% on ~303,638 households. See the approved '
           'filing and who is cutting in Louisiana.',
 'state': 'Louisiana', 'read': '5', 'tracker': '/home/rate-changes/louisiana.html',
 'alert': 'State Farm raised Louisiana home insurance rates &plus;9.7% across ~303,638 households '
          'in 2026.',
 'h1': 'Why did my State Farm home insurance rate go up in Louisiana?',
 'dek': 'State Farm raised its Louisiana homeowners rates <strong>&plus;9.7%</strong> in 2026 across '
        'about <strong>303,638 households</strong> &mdash; the largest home book in the state, and '
        'close to the &plus;10.3% its own analysis said it needed. Louisiana&rsquo;s home market is '
        'the hardest we track. Here is the filing, and the two carriers cutting anyway.',
 'topzip': 'See what every home insurer would charge for your ZIP:',
 'rows': [
   ('State Farm', '/home/carrier/state-farm.html', 'SFMA-134661164', '134661164', '&plus;9.7%',
    'The filing behind your increase. Approved &plus;9.7% on ~303,638 households against a '
    '&plus;10.3% indicated need. Eff. Oct 15, 2025.', True),
   ('Louisiana Farm Bureau', '', 'SFBC-134582157', '134582157', '&plus;14.8%',
    'Raised &plus;14.8% on ~7,321 households against a &plus;17.8% indication &mdash; the steepest '
    'Louisiana home increase we recorded.', True),
   ('USAA', '/home/carrier/usaa.html', 'USAA-134777840', '134777840', '&plus;9.2%',
    'Raised &plus;9.2% on ~76,209 households; range &plus;44.7% to &minus;38.8%.', True),
   ('Allstate', '/home/carrier/allstate.html', 'ALSE-134740068', '134740068', '&plus;3.8%',
    'Raised &plus;3.8% on ~102,421 households &mdash; but the range runs &plus;125.3% to '
    '&minus;24.2%.', True),
   ('Farmers', '/home/carrier/farmers.html', 'FAIG-134637040', '134637040', '0.0%',
    'Held Louisiana home rates flat on ~4,329 households.', False),
   ('Hanover', '', 'HNVR-G134780663', '134780663', '&minus;1.8%',
    'Cut &minus;1.8% on ~4,056 households despite indicating it needed &plus;0.6%.', False),
   ('Allied Trust', '', 'ALTR-134663183', '134663183', '&minus;2.3%',
    'Cut &minus;2.3% on ~22,038 households &mdash; the largest Louisiana home cut we recorded.', False),
 ],
 'prose': '''    <h2>What the filing actually says</h2>
    <p>State Farm&rsquo;s approved Louisiana homeowners increase is <strong>&plus;9.7%</strong>,
    effective October 15, 2025, on roughly <strong>303,638 households</strong>. Its own actuarial
    analysis indicated it needed <strong>&plus;10.3%</strong>, so it filed very close to its full
    indication &mdash; this was not a carrier holding back.</p>
    <p>Scale matters here. State Farm&rsquo;s Louisiana home book is larger than the next three
    carriers&rsquo; combined, so a &plus;9.7% move by State Farm repriced more Louisiana households
    than every other home filing in the state put together.</p>
    <h2>Louisiana is the hardest home market we track</h2>
    <p>This is not a State Farm story so much as a Louisiana story. We recorded <strong>five
    carriers raising and two cutting</strong>, and the increases are steep across the board:
    <strong>Louisiana Farm Bureau</strong> at <strong>&plus;14.8%</strong>, <strong>USAA</strong>
    at <strong>&plus;9.2%</strong>, State Farm at &plus;9.7%. Hurricane exposure, reinsurance
    costs and litigation have all pushed Gulf Coast property rates hard, and Louisiana absorbs more
    of that than anywhere else in our data.</p>
    <p>The spreads are extreme too. <strong>Allstate</strong>&rsquo;s comparatively modest
    &plus;3.8% average conceals a range of <strong>&plus;125.3% to &minus;24.2%</strong> &mdash;
    meaning some Allstate households saw their premium more than double while others fell. In a
    market like this, a carrier&rsquo;s statewide average is close to meaningless for predicting
    your own bill.</p>
    <h2>Who is cutting Louisiana home rates</h2>
    <p>Two carriers cut, and both are worth a quote. <strong>Allied Trust</strong> cut
    <strong>&minus;2.3%</strong> on about 22,038 households, the largest Louisiana home cut we have
    on file. <strong>Hanover</strong> cut <strong>&minus;1.8%</strong> on about 4,056 households
    &mdash; notable because its own analysis indicated it needed a small <em>increase</em> of
    &plus;0.6% and it cut anyway, which is what a carrier does when it wants to grow.
    <strong>Farmers</strong> held flat.</p>
    <p>These are smaller books than State Farm&rsquo;s, and in a hard market smaller regional and
    specialty writers are often the ones still competing for new business while the nationals
    reprice. That is exactly the situation where shopping pays.</p>
    <h2>What to do about it</h2>
    <p>In a Gulf Coast market, check your <strong>wind and hail deductible</strong> first &mdash; it
    is often a percentage of dwelling coverage rather than a flat dollar amount, and it is the
    single biggest lever on a Louisiana home premium. Confirm your <strong>dwelling coverage</strong>
    still matches replacement cost rather than an inflated automatic adjustment. Then get quotes
    from Allied Trust, Hanover and Farmers, and price your auto policy alongside it &mdash; bundling
    is usually the largest discount available, and it matters more when the base premium is this high.</p>
''',
 'faq': [
   ('How much did State Farm raise home insurance rates in Louisiana?',
    'State Farm received approval for a +9.7% statewide average homeowners increase in Louisiana '
    '(SERFF SFMA-134661164), effective October 15, 2025, affecting about 303,638 households. Its '
    'own actuarial analysis indicated it needed +10.3%, so it filed close to its full indication.'),
   ('Why are Louisiana home insurance rates rising so fast?',
    'Hurricane exposure, reinsurance costs and litigation have pushed Gulf Coast property rates '
    'harder than anywhere else in our data. We recorded five Louisiana carriers raising home rates '
    'and only two cutting, with increases including Louisiana Farm Bureau +14.8%, State Farm +9.7% '
    'and USAA +9.2%.'),
   ('Which home insurers cut rates in Louisiana?',
    'Allied Trust cut -2.3% on about 22,038 households and Hanover cut -1.8% on about 4,056 — '
    'Hanover notably cut despite indicating it needed a +0.6% increase. Farmers held rates flat.'),
   ('What most affects a Louisiana home insurance premium?',
    'The wind and hail deductible, which in coastal states is often a percentage of your dwelling '
    'coverage rather than a flat dollar amount. Raising it can move the premium substantially. '
    'Dwelling coverage amount and bundling with auto are the next two largest levers.'),
 ],
},
]
