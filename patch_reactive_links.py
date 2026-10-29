#!/usr/bin/env python3
"""Contextual internal links TO the reactive 'why did my [carrier] rate go up in
[state]' explainers, so they aren't orphaned (orphan pages barely rank).

- Carrier page  article/carrier/<slug>.html  -> that carrier's explainers (all states)
- State page    article/state/<slug>.html     -> that state's explainers (all carriers)

Marker-guarded + idempotent (replaces the <!-- reactive-links --> region if present,
else inserts a self-contained block before <footer>). Insert-only, never replaces a
<script> block (CLAUDE.md). Runs in the cascade AFTER the page generators so it
survives regeneration — add to rebuild.sh SHARED tail.
"""
import os, re
from gen_reactive_config import PAGES
from build_state_features import FEATURES   # state-level narrative features (kept out of PAGES)

def slug(s): return s.lower().replace(' ', '-')

STYLE = ('<style>.rxl{max-width:720px;margin:34px auto;padding:0 28px;}'
 '.rxl h2{font-family:var(--serif);font-weight:500;font-size:22px;margin-bottom:8px;}'
 '.rxl p.sub{color:var(--ink-mute);font-size:14px;margin-bottom:10px;}'
 '.rxl ul{list-style:none;margin:0;padding:0;}.rxl li{border-bottom:1px solid var(--rule);}'
 '.rxl li a{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:9px 2px;text-decoration:none;color:var(--ink);font-size:16px;}'
 '.rxl li a:hover{color:var(--accent);}'
 '.rxl .c{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--accent);white-space:nowrap;}</style>')

RE_BLOCK = re.compile(r'<!-- reactive-links -->.*?<!-- /reactive-links -->', re.S)

def block(heading, sub, items):
    lis = ''.join(f'<li><a href="{href}">{label} <span class="c">{chg}</span></a></li>'
                  for label, chg, href in items)
    return (f'<!-- reactive-links -->{STYLE}<div class="rxl"><h2>{heading}</h2>'
            f'<p class="sub">{sub}</p><ul>{lis}</ul></div><!-- /reactive-links -->')

def apply(path, blk):
    if not os.path.exists(path): return False
    s = open(path, encoding='utf-8').read(); o = s
    if RE_BLOCK.search(s):
        s = RE_BLOCK.sub(lambda _m: blk, s, count=1)
    elif '<footer' in s:
        s = s.replace('<footer', blk + '\n<footer', 1)
    else:
        return False
    if s != o:
        open(path, 'w', encoding='utf-8').write(s); return True
    return False

# manifest
by_carrier, by_state = {}, {}
for c in PAGES:
    car, _h, _t, _f, chg, _n, _u = c['rows'][0]
    href = c['url'].replace('https://boringrate.com', '')
    by_carrier.setdefault(car, []).append((c['state'], chg, href))
    by_state.setdefault(c['state'], []).append((car, chg, href))

n = 0
for car, items in by_carrier.items():
    items = sorted(items)
    blk = block(f'See the filing behind your {car} increase',
                f'The actual approved rate change {car} filed in your state &mdash; and who&rsquo;s cutting.',
                [(f'Why did my {car} rate go up in {st}?', chg, href) for st, chg, href in items])
    if apply(f'article/carrier/{slug(car)}.html', blk): n += 1
# Key by (state, line), not state alone: Georgia now has BOTH an auto feature and a
# home one, and a state-only key silently dropped whichever came second. `line` is
# taken from the feature's own ledger field, defaulting to auto.
def _line(fe):
    return 'home' if fe.get('ledger', '').startswith('serff_home') else 'auto'
feat = {(fe['state'], _line(fe)): (fe['url'].replace('https://boringrate.com', ''), fe['title'])
        for fe in FEATURES}
for st in sorted(set(by_state) | {k[0] for k in feat}):
    items = []
    if (st, 'auto') in feat:                             # lead with the full state report
        url, title = feat[(st, 'auto')]
        items.append((title, '2026 report', url))
    for car, chg, href in sorted(by_state.get(st, [])):
        items.append((f'Why did my {car} rate go up in {st}?', chg, href))
    blk = block(f'{st} rate changes &mdash; see the filings',
                f'The full {st} rate report and primary-source explainers &mdash; who raised, who cut, and by how much.',
                items)
    if apply(f'article/state/{slug(st)}.html', blk): n += 1

# home-line features get their own block on the HOME state page, which the loop
# above never touched - that left the GA home feature an orphan on first build.
for (st, ln), (url, title) in sorted(feat.items()):
    if ln != 'home':
        continue
    blk = block(f'{st} home rate changes &mdash; see the filings',
                f'The full {st} homeowners rate report &mdash; who raised, who cut, and what the '
                f'state approved.',
                [(title, '2026 report', url)])
    if apply(f'home/state/{slug(st)}.html', blk): n += 1
print(f'reactive-links: patched {n} carrier/state pages')
