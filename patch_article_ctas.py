# -*- coding: utf-8 -*-
"""Roll out the locked article CTA template (see memory boringrate-article-cta-template):
  - thin .rz-zip ZIP CTA #1 right after <div class="article-body">
  - remove the mid-article .tooltiles ZIP/coverage module (where present)
  - remove the bottom .article-email email-capture block
  - thin .rz-zip ZIP CTA #2 placed ABOVE the "...rates by state" compare-links section
Carrier/state/metro pages get subject-specific copy from the article-kicker; other types get generic.
Idempotent (skips anything already containing rz-zip) and DEFENSIVE (skips + logs any page whose
expected anchors don't match; never writes a partially-transformed file).

COVERS ALL THREE PRODUCT TREES (article/, renters/, home/). The original rollout reached only
article/, leaving renters and home on the superseded modules — 106 renters .tooltiles blocks and
51 home .zip-embed boxes, the latter being the dark module the owner rejected as uninviting.

★ CTA target is per-tree (tool_for). Getting this wrong is a trust break, not a cosmetic bug: rz()
originally hardcoded `/?zip=`, so rolling it into renters/ unchanged would have sent 157 renters
pages into the AUTO tool. The superseded .zip-embed CTAs already routed correctly per tree; this
preserves that.

Run:  python3 patch_article_ctas.py --dry   then   python3 patch_article_ctas.py
"""
import re, glob, sys

DRY = '--dry' in sys.argv

RZ_CSS = ('<!-- rz-cta-css --><style>'
 '.rz-zip{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:22px 0;padding:12px 16px;background:var(--paper-deep);border:1px solid var(--rule);}'
 '.rz-zip-label{font-family:var(--sans);font-size:15px;font-weight:600;color:var(--ink);}'
 '.rz-zip form{display:flex;gap:8px;margin:0;}'
 '.rz-zip-input{font-family:var(--mono);font-size:14px;padding:8px 10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:92px;}'
 '.rz-zip-btn{font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;padding:8px 16px;background:var(--accent);color:var(--paper);border:none;cursor:pointer;white-space:nowrap;}'
 '.rz-zip-btn:hover{opacity:0.9;}'
 '@media (max-width:480px){.rz-zip{flex-direction:column;align-items:flex-start;}}'
 '</style>')

def tool_for(path):
    """Which ZIP tool this page's CTA must open. Getting this wrong is a trust break:
    a renters visitor dumped into auto results sees prices for a product they did not
    ask about. The old .zip-embed CTAs already routed correctly per tree — this keeps
    that behaviour rather than inheriting article/'s hardcoded auto target."""
    p = path.replace('\\', '/')
    if p.startswith('renters/'):
        return '/renters/'
    if p.startswith('home/'):
        return '/home/'
    return '/'


def rz(label, tool='/'):
    return ('<div class="rz-zip"><span class="rz-zip-label">' + label + '</span>'
            '<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);'
            'if(/^\\d{5}$/.test(z)){location.href=\'' + tool + '?zip=\'+z}else{this.zc.focus()}">'
            '<input class="rz-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
            '<button type="submit" class="rz-zip-btn">Compare &rarr;</button></form></div>')

def kicker_parts(html):
    m = re.search(r'<div class="article-kicker">(.*?)</div>', html, re.S)
    if not m: return []
    txt = re.sub(r'<[^>]+>', '', m.group(1)).replace('&middot;', '·').replace('&nbsp;', ' ')
    return [p.strip() for p in txt.split('·') if p.strip()]

def subject(html):
    parts = kicker_parts(html)
    for i, p in enumerate(parts):
        if 'min read' in p.lower():
            return parts[i - 1] if i >= 1 else None
    return None

def carrier_name(html):
    m = re.search(r'<h1 class="article-title">([^<]*)</h1>', html)
    if not m: return None
    t = m.group(1)
    # Auto pages: "GEICO Auto Insurance Review 2026"
    t = re.sub(r'\s+Auto(\s+Insurance)?\s+Review\s+\d{4}\s*$', '', t)
    t = re.sub(r'\s+Insurance\s+Review\s+\d{4}\s*$', '', t)
    t = re.sub(r'\s+Review\s+\d{4}\s*$', '', t)
    # Renters/home pages use a different shape entirely:
    #   "Allstate homeowners insurance review (2026): broad discounts, but priced at the high end."
    # Without this the whole subtitle leaked into the CTA label ("Instantly compare Allstate
    # homeowners insurance review (2026): broad discounts... to every home insurer in your ZIP:").
    t = re.sub(r'\s+(?:homeowners|home|renters)\s+insurance\s+review\b.*$', '', t, flags=re.I)
    t = t.split(':')[0]
    return t.strip().rstrip('.') or None

LINE_NOUN = {'/': 'carrier', '/renters/': 'renters carrier', '/home/': 'home insurer'}


def labels(path, html):
    noun = LINE_NOUN[tool_for(path)]
    if '/carrier/' in path:
        subj = carrier_name(html)
        slug = path.rsplit('/', 1)[-1][:-5]
        if subj and slug.endswith('-auto') and not subj.lower().endswith('auto'):
            subj = subj + ' Auto'  # name genuinely ends in "Auto" (Direct Auto, Safe Auto)
        if subj:
            return (f'Instantly compare {subj} to every {noun} in your ZIP:',
                    f'Ready to stop overpaying? Compare {subj} to every {noun} in your ZIP:')
    elif '/state/' in path or '/metro/' in path:
        subj = subject(html)
        if subj:
            return (f'Instantly compare every {noun} in {subj} for your ZIP:',
                    f'Ready to stop overpaying? Compare every {noun} in {subj} for your ZIP:')
    return (f'Instantly compare every {noun} in your ZIP:',
            f'Ready to stop overpaying? Compare every {noun} in your ZIP:')

EMAIL_RE = re.compile(r'<div class="article-email">.*?id="articleEmailThanks"[^>]*>.*?</div>\s*</div>', re.S)
TILES_RE = re.compile(r'(?m)^[ \t]*<div class="tooltiles">.*</div></div>[ \t]*\n')
EMBED_RE = re.compile(r'[ \t]*<div class="zip-embed">.*?</form>\s*</div>\n?', re.S)
BYSTATE_RE = re.compile(r'<h2[^>]*>[^<]*rates by state[^<]*</h2>')
# The compare-links section heading near the bottom of state pages ("Metro-level rate
# breakdowns"). Kept as a simple, NON-spanning text match — an earlier lookahead-to-
# internal-links version backtracked across the whole article and matched the first h2.
COMPARE_H2_RE = re.compile(r'<h2[^>]*>[^<]*rate breakdowns[^<]*</h2>')
FOOT_RE = re.compile(r'(\n[ \t]*</div>\s*</div>\s*<footer>)')

def transform(path, html):
    """Pure: returns (status, new_html_or_None, where). Shared by the batch patcher
    and by generators that want to bake the template into their output."""
    if 'class="rz-zip"' in html: return ('skip-has-rz', None, None)
    if '<div class="article-body">' not in html: return ('skip-no-body', None, None)
    if '</head>' not in html: return ('skip-no-head', None, None)
    # NOTE: no email-block gate — guides have no .article-email; email removal below is a
    # no-op when absent. Safety is preserved by requiring a valid CTA#2 anchor (skips otherwise).
    la, lb = labels(path, html)
    tool = tool_for(path)
    # 1. CSS (idempotent)
    if '<!-- rz-cta-css -->' not in html:
        html = html.replace('</head>', RZ_CSS + '</head>', 1)
    # 2. CTA #1 right after article-body open
    html = html.replace('<div class="article-body">', '<div class="article-body">\n' + rz(la, tool), 1)
    # 3. remove the old mid-article modules: .tooltiles two-tile block and .zip-embed dark box
    html = TILES_RE.sub('', html)
    html = EMBED_RE.sub('', html)
    # 4. remove email-capture block
    html = EMAIL_RE.sub('', html, count=1)
    # 5. CTA #2 above the compare-links section (carrier: "...rates by state"; state pages:
    #    "Metro-level rate breakdowns" — both are an <h2> immediately before an internal-links block),
    #    else just before article-body/wrap close.
    m = BYSTATE_RE.search(html) or COMPARE_H2_RE.search(html)
    if m:
        html = html[:m.start()] + rz(lb, tool) + '\n    ' + html[m.start():]
        where = 'above-compare-links'
    else:
        html, n = FOOT_RE.subn(lambda mm: '\n' + rz(lb, tool) + mm.group(1), html, count=1)
        if n == 0: return ('skip-no-cta2-anchor', None, None)
        where = 'end-of-body'
    return ('patched', html, where)

def process(path):
    html = open(path, encoding='utf-8').read()
    status, new_html, where = transform(path, html)
    if new_html is None: return (status, path)
    if not DRY:
        open(path, 'w', encoding='utf-8').write(new_html)
    la, _ = labels(path, html)
    return ('would-patch' if DRY else 'patched', path, where, la)

def main():
    files = sorted(glob.glob('article/**/*.html', recursive=True)
                    + glob.glob('renters/**/*.html', recursive=True)
                    + glob.glob('home/**/*.html', recursive=True))
    from collections import Counter
    c = Counter(); samples = []
    for f in files:
        r = process(f)
        c[r[0]] += 1
        if r[0] in ('would-patch', 'patched') and len(samples) < 12:
            samples.append(r)
    print('MODE:', 'DRY' if DRY else 'LIVE', '| files scanned:', len(files))
    for k, v in sorted(c.items()): print(f'  {k}: {v}')
    print('--- samples ---')
    for s in samples: print(' ', s[1], '|', s[2], '|', s[3])

if __name__ == '__main__':
    main()
