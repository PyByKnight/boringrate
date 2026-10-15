#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Derive reactive 'why did my <carrier> rate go up in <state>?' page configs
straight from the SERFF ledgers, instead of hand-writing each one.

WHY THIS EXISTS. gen_reactive_config.py is 454 lines of hand-authored prose and
has produced 14 pages. The ledgers already contain 56 auto + 78 home carrier x
state combinations with a >= 3% increase, and this is the best-converting page
type on the site (1.97% CTR at position 6.1 in the 2026-10-15 GSC pull). The
blocker was authoring cost, not data.

Every sentence here is emitted ONLY when the field backing it is present, so a
page never claims a figure the ledger does not have — the rule from
SERFF_RUNBOOK.md: publish without it rather than guess. A combo that cannot
clear MIN_PROSE distinct evidence points is skipped rather than padded.

Output is the same cfg dict shape gen_reactive_pages.build() already consumes,
so hand-written entries in gen_reactive_config.py keep working untouched and
win on conflict — this only fills combos nobody has written.

    import gen_reactive_derive as d
    cfgs = d.derive_all('serff_filings.json', line='auto', limit=20)
"""
import json, os, re, html
from gen_metro_page import STATE
import filing_guards as fg

B = 'https://boringrate.com/article/'
MIN_INCREASE = 3.0      # below this there is no "why did my rate go up" to answer
MIN_PROSE    = 2        # distinct evidence points required before a page is worth it
CONTEXT_ROWS = 5        # competitor rows shown beneath the subject carrier

_CARRIER_PAGES = None

def carrier_href(name, line='auto'):
    """/article/carrier/<slug>.html when that page exists, else no link."""
    global _CARRIER_PAGES
    if _CARRIER_PAGES is None:
        _CARRIER_PAGES = {}
        for d_ in ('article/carrier', 'home/carrier'):
            for f in os.listdir(d_) if os.path.isdir(d_) else []:
                if f.endswith('.html'):
                    _CARRIER_PAGES.setdefault(f[:-5], '/' + d_ + '/' + f)
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    for cand in (slug, slug.replace('-insurance', ''), slug.split('-')[0]):
        if cand in _CARRIER_PAGES:
            return _CARRIER_PAGES[cand]
    return ''

def _pct(v):
    """+4.2% / -6.5% with HTML entities, matching the hand-written rows."""
    return ('&plus;' if v >= 0 else '&minus;') + f'{abs(v):.1f}%'

def _n(v):
    return f'{v:,}' if isinstance(v, (int, float)) else None

def _eff_human(iso):
    if not iso:
        return None
    try:
        from datetime import date
        y, m, d = (int(x) for x in iso.split('-'))
        return date(y, m, d).strftime('%B %-d, %Y')
    except Exception:
        return iso

def _an(word):
    """'a'/'an' for a carrier name — 'An Allstate increase', 'A GEICO increase'."""
    return 'An' if word[:1].upper() in 'AEIOU' else 'A'

def _join(items):
    """Oxford-style list join: 'A', 'A and B', 'A, B, and C'."""
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    if len(items) == 2:
        return f'{items[0]} and {items[1]}'
    return ', '.join(items[:-1]) + ', and ' + items[-1]

def _subject(rows):
    """The filing that best explains an increase: biggest book among the raises."""
    ups = [r for r in rows if (r.get('overall_pct') or 0) >= MIN_INCREASE]
    if not ups:
        return None
    return max(ups, key=lambda r: (r.get('affected') or 0, r.get('effective_new') or ''))

def _context(ledger_rows, state, exclude_carrier):
    """Other carriers in the same state — cutters first, they are the reason to switch."""
    best = {}
    for r in ledger_rows:
        if r.get('state') != state or r.get('carrier') == exclude_carrier:
            continue
        if not fg.has_pct(r) or not fg.is_driftable(r) or fg.too_small(r):
            continue
        c = r['carrier']
        if c not in best or (r.get('affected') or 0) > (best[c].get('affected') or 0):
            best[c] = r
    ranked = sorted(best.values(),
                    key=lambda r: (r['overall_pct'] >= 0, -(r.get('affected') or 0)))
    return ranked[:CONTEXT_ROWS]

def _row_tuple(r, line):
    name = r['carrier']
    return (name, carrier_href(name, line), r['tracking'],
            re.sub(r'^[A-Z]+-', '', r['tracking']), _pct(r['overall_pct']),
            '', r['overall_pct'] >= 0)

def derive(carrier, state, ledger_rows, line='auto'):
    """One cfg dict, or None when the evidence is too thin to publish."""
    rows = [r for r in ledger_rows
            if r.get('carrier') == carrier and r.get('state') == state
            and fg.has_pct(r) and fg.is_driftable(r) and not fg.too_small(r)]
    subj = _subject(rows)
    if not subj or state not in STATE:
        return None

    sname, sslug, _ = STATE[state]
    pct      = subj['overall_pct']
    indicated= subj.get('indicated_pct')
    mx, mn   = subj.get('max_pct'), subj.get('min_pct')
    aff      = subj.get('affected')
    eff      = _eff_human(subj.get('effective_new') or subj.get('effective_renewal'))
    trk      = subj['tracking']
    lname    = 'home' if line == 'home' else 'auto'
    LNAME    = 'homeowners' if line == 'home' else 'auto'

    # --- evidence points: each one is a real field, none invented -------------
    evidence = []
    if indicated is not None and indicated > pct + 0.4:
        evidence.append('indicated')
    if mx is not None and mn is not None and (mx - mn) >= 10:
        evidence.append('spread')
    if aff:
        evidence.append('scale')
    ctx = _context(ledger_rows, state, carrier)
    cutters = [r for r in ctx if r['overall_pct'] < 0]
    if cutters:
        evidence.append('cutters')
    if len(evidence) < MIN_PROSE:
        return None

    slug = re.sub(r'[^a-z0-9]+', '-', carrier.lower()).strip('-')
    # matches the existing hand-written naming: why-did-my-usaa-home-rate-go-up-ohio.html
    infix = 'home-' if line == 'home' else ''
    fname = f'why-did-my-{slug}-{infix}rate-go-up-{sslug}.html'
    path  = ('home/' if line == 'home' else 'article/') + fname
    url   = 'https://boringrate.com/' + path

    big_cut = max(cutters, key=lambda r: abs(r['overall_pct'])) if cutters else None

    # ---- head ---------------------------------------------------------------
    title = f'Why did my {carrier} rate go up in {sname}?'
    desc_bits = [f'{carrier} raised {sname} {LNAME} rates {pct:+.1f}% in 2026.']
    if indicated is not None and indicated > pct + 0.4:
        desc_bits.append(f'It indicated {indicated:+.1f}% and took less.')
    if big_cut:
        desc_bits.append(f'Meanwhile {big_cut["carrier"]} cut {big_cut["overall_pct"]:+.1f}%.')
    desc_bits.append('See the filing and who to compare.')
    desc = ' '.join(desc_bits)

    alert = (f'{carrier} raised {sname} {LNAME} rates <strong>{_pct(pct)}</strong> in 2026'
             + (f' &mdash; the filing ranges {_pct(mx)} to {_pct(mn)} by '
                + ('household' if line == 'home' else 'driver') + '.'
                if mx is not None and mn is not None else '.'))

    dek = [f'{carrier} raised its {sname} {LNAME} rates <strong>{_pct(pct)}</strong> in 2026']
    if indicated is not None and indicated > pct + 0.4:
        dek.append(f' &mdash; it indicated a need for {_pct(indicated)} and took less &mdash;')
    dek.append('.' if len(dek) == 1 else '')
    if mx is not None and mn is not None:
        dek.append(f' and the filing&rsquo;s own range runs from <strong>{_pct(mx)} to {_pct(mn)}</strong>'
                   f' depending on the {"household" if line == "home" else "driver"}.')
    if big_cut:
        dek.append(f' Meanwhile {big_cut["carrier"]} cut {_pct(big_cut["overall_pct"])}.')
    dek.append(' Here&rsquo;s the filing, and who&rsquo;s cutting.')
    dek = ''.join(dek)

    # ---- prose: one section per evidence point we actually hold -------------
    who = 'household' if line == 'home' else 'driver'
    P = []
    P.append(f'    <p>If your {carrier} renewal in {sname} came in higher, this is the source: '
             f'{carrier} filed for a rate increase (SERFF <strong>{trk}</strong>) and it was approved at '
             f'<strong>{_pct(pct)}</strong>'
             + (f' on about {_n(aff)} {subj.get("count_basis") or "policyholders"}' if aff else '')
             + (f', effective {eff}' if eff else '')
             + '. The figures below are approved filings pulled from the public SERFF system '
               '&mdash; not estimates &mdash; and every one links to its filing.</p>\n')

    if 'spread' in evidence:
        # Only call the low end a "decrease" when it actually is one. A filing whose
        # min is 0% or positive raised everyone by varying amounts - saying some were
        # cut would be a figure the filing does not support.
        if mn < 0:
            low = (f'and the largest decrease about <strong>{_pct(mn)}</strong>. So inside a '
                   f'&ldquo;{_pct(pct)} average,&rdquo; some {carrier} {who}s in {sname} were raised far '
                   f'more than the headline and others were cut')
        else:
            low = (f'and the smallest about <strong>{_pct(mn)}</strong>. So inside a '
                   f'&ldquo;{_pct(pct)} average,&rdquo; some {carrier} {who}s in {sname} were raised several '
                   f'times more than the headline while others barely moved')
        P.append(f'\n    <h2>The {_pct(pct)} is an average. Your {carrier} change ranges '
                 f'{_pct(mx)} to {_pct(mn)}.</h2>\n'
                 f'    <p>A statewide rate change is one blended number, but {carrier} did not move every '
                 f'{who} by the same amount. Its own filing reports the spread: the largest increase in the '
                 f'book was about <strong>{_pct(mx)}</strong> {low}. Where you '
                 f'land depends on your ZIP, '
                 + ('home age, roof and claims history' if line == 'home'
                    else 'vehicle, age and driving record') + '.</p>\n')

    if 'indicated' in evidence:
        P.append(f'\n    <h2>{carrier} asked for more than it got.</h2>\n'
                 f'    <p>The filing shows an <strong>indicated</strong> need of {_pct(indicated)} &mdash; the '
                 f'increase {carrier}&rsquo;s own actuarial analysis said it required &mdash; against the '
                 f'<strong>{_pct(pct)}</strong> it actually took. That gap matters for what comes next: a '
                 f'carrier that took less than it indicated has an unclosed gap, and the remainder often '
                 f'arrives in a later filing rather than disappearing.</p>\n')

    if cutters:
        sel = cutters[:3]
        names = _join(f'{r["carrier"]} ({_pct(r["overall_pct"])})' for r in sel)
        verb = 'both filed' if len(sel) == 2 else ('filed' if len(sel) == 1 else 'all filed')
        P.append(f'\n    <h2>Other {sname} insurers are cutting.</h2>\n'
                 f'    <p>An increase is only worth acting on relative to the alternatives, and in {sname} '
                 f'the direction is not uniform: {names} {verb} <strong>decreases</strong> in the same '
                 f'period. {_an(carrier)} {carrier} increase alongside competitor cuts is the clearest '
                 f'signal there is that the market has moved and your renewal has not.</p>\n')

    P.append(f'\n    <p style="font-size:14px;margin:10px 0;"><a class="ca-link" '
             f'href="/article/rate-changes/{sslug}.html">See every approved {sname} '
             f'{LNAME} rate filing &rarr;</a></p>\n')
    prose = ''.join(P)

    # ---- FAQ ----------------------------------------------------------------
    faq = [(f'Why did my {carrier} rate go up in {sname} in 2026?',
            f'{carrier} filed for and received an approved {pct:+.1f}% {sname} {LNAME} rate increase '
            f'(SERFF {trk})'
            + (f', effective {eff}' if eff else '')
            + (f', on about {_n(aff)} {subj.get("count_basis") or "policyholders"}' if aff else '')
            + '.')]
    if 'spread' in evidence:
        tail = ('so many customers saw far more or far less, and some were cut.' if mn < 0
                else 'so many customers saw several times the headline figure while others barely moved.')
        faq.append((f'How much did {carrier} actually raise my {sname} rate?',
                    f'The {pct:+.1f}% is a statewide average. {carrier}’s own filing reports the change '
                    f'ranged from about {mx:+.1f}% to about {mn:+.1f}% depending on the {who}’s ZIP and '
                    f'risk profile, ' + tail))
    if 'indicated' in evidence:
        faq.append((f'Will {carrier} raise {sname} rates again?',
                    f'The filing indicates {carrier} believed it needed {indicated:+.1f}% but took '
                    f'{pct:+.1f}%. An unclosed indicated-versus-taken gap is commonly made up in a '
                    f'subsequent filing, so this may not be the last increase.'))
    if cutters:
        faq.append((f'Are other {sname} insurers cutting rates?',
                    'Yes. ' + _join(f'{r["carrier"]} filed {r["overall_pct"]:+.1f}%' for r in cutters[:3])
                    + f'. {_an(carrier)} {carrier} increase while competitors cut is a strong reason '
                      f'to compare.'))

    return {
        'path': path, 'url': url, 'title': title, 'desc': desc, 'ogdesc': desc,
        'state': sname, 'read': '4',
        'tracker': ('/home/rate-changes/' if line == 'home' else '/article/rate-changes/') + sslug + '.html',
        'alert': alert, 'h1': title, 'dek': dek,
        'rows': [_row_tuple(subj, line)] + [_row_tuple(r, line) for r in ctx],
        'prose': prose, 'faq': faq,
        'ledger': 'serff_home_filings.json' if line == 'home' else 'serff_filings.json',
        'tool': '/home/' if line == 'home' else '/',
        '_affected': aff or 0, '_derived': True,
    }

def derive_all(ledger_path, line='auto', limit=None, skip_paths=()):
    d = json.load(open(ledger_path))
    rows = d if isinstance(d, list) else d['filings']
    combos = {}
    for r in rows:
        if not fg.has_pct(r) or not fg.is_driftable(r) or fg.too_small(r):
            continue
        if (r.get('overall_pct') or 0) < MIN_INCREASE:
            continue
        if r.get('carrier') and r.get('state'):
            combos[(r['carrier'], r['state'])] = True
    out = []
    for (c, s) in combos:
        cfg = derive(c, s, rows, line=line)
        if cfg and cfg['path'] not in skip_paths:
            out.append(cfg)
    out.sort(key=lambda c: -c['_affected'])
    return out[:limit] if limit else out
