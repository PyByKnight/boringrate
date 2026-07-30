#!/usr/bin/env python3
"""Stamp carrier x state 'why did my [carrier] rate go up in [state]?' reactive
pages from the proven article shell (tennessee-rates-dropping.html).

Reactive-first content wedge (see memory boringrate-filing-data-content-strategy):
each page validates the anger with the primary-source SERFF filing, surfaces the
tier-1/2 juice (indicated-vs-taken 'more coming', within-filing max/min spread,
affected scale), then bridges to the compare tool with who's CUTTING in that state.

Config-driven: add a PAGES entry (all prose + the filing figures) and re-run. The
shared shell (CSS/nav/CTA/email/scripts) is inherited verbatim from the template,
so nav + analytics + coverage tiles stay single-source. Idempotent: rewrites files.

Every figure is a real approved filing in serff_filings.json — keep them accurate.
"""
import json, re, html

TEMPLATE = 'article/tennessee-rates-dropping.html'
SERFF = 'https://filingaccess.serff.com/sfa/search/filingSummary.xhtml?filingId='

_LEDGER = None
def _led():
    global _LEDGER
    if _LEDGER is None:
        d = json.load(open('serff_filings.json'))
        _LEDGER = {r['tracking']: r for r in (d if isinstance(d, list) else d['filings'])}
    return _LEDGER

def _ph(n):
    if not n: return '&mdash;'
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1000: return f"{round(n/1000)}K"
    return str(n)

def _eff(d):
    if not d: return '&mdash;'
    y, m, dd = d.split('-'); return f"{int(m)}/{int(dd)}/{y[2:]}"

def row(name, href, trk, fid, change, note, up):
    """Concise data row. Policyholders + Eff. Date are pulled from the ledger by
    tracking # so they can't drift from the source. `note` is retained in the
    config as per-row reference but no longer rendered (the prose carries nuance)."""
    r = _led().get(trk, {})
    cn = f'<a class="ca-link" href="{href}">{name}</a>' if href else name
    cls = 'rn up' if up else ('rn down' if '&minus;' in change else 'rn')
    return (f'          <tr>\n'
            f'            <td class="cn">{cn}</td>\n'
            f'            <td class="{cls}">{change}</td>\n'
            f'            <td class="ph">{_ph(r.get("affected"))}</td>\n'
            f'            <td class="eff">{_eff(r.get("effective_new"))}</td>\n'
            f'            <td class="fil"><a class="clink" href="{SERFF}{fid}" target="_blank" rel="noopener nofollow">{trk} &rarr;</a></td>\n'
            f'          </tr>\n')

def table(rows):
    body = ''.join(row(*r) for r in rows)
    return ('    <div id="rate-table">\n      <table class="rate-table">\n        <thead>\n'
            '          <tr><th>Carrier</th><th>Rate Change</th><th>Policyholders</th><th>Eff. Date</th><th>Filing #</th></tr>\n'
            '        </thead>\n        <tbody>\n' + body +
            '        </tbody>\n      </table>\n    </div>\n')

def thinzip(label):
    """A thin, single-row ZIP entry — small enough that the reader keeps reading."""
    return ('<div class="rz-zip"><span class="rz-zip-label">'+label+'</span>'
      '<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z)){location.href=\'/?zip=\'+z}else{this.zc.focus()}">'
      '<input class="rz-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
      '<button type="submit" class="rz-zip-btn">Compare &rarr;</button></form></div>')

# Late <style> appended after the template's ca-link-style: page-specific styles
# for the thin rz-zip CTA and the 5-column rate table. (Nav dropdown CSS is NOT
# here — it's single-sourced in partials/nav-css.html and stamped by build_nav.py,
# so run build_nav.py after generating these pages.)
RZ_STYLE = (
'<!-- rz-style --><style>'
'.rz-zip{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:22px 0;padding:12px 16px;background:var(--paper-deep);border:1px solid var(--rule);}'
'.rz-zip-label{font-family:var(--sans);font-size:15px;font-weight:600;color:var(--ink);}'
'.rz-zip form{display:flex;gap:8px;margin:0;}'
'.rz-zip-input{font-family:var(--mono);font-size:14px;padding:8px 10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:92px;}'
'.rz-zip-btn{font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;padding:8px 16px;background:var(--accent);color:var(--paper);border:none;cursor:pointer;white-space:nowrap;}'
'.rz-zip-btn:hover{opacity:0.9;}'
'#rate-table{overflow-x:auto;}'
'.rate-table{max-width:none;}'
'.rate-table th{white-space:nowrap;border-bottom:2px solid var(--ink);padding:8px 18px 8px 0;}'
'.rate-table td{vertical-align:middle;padding:12px 18px 12px 0;}'
'.rate-table td.cn{font-size:16px;}'
'.rate-table td.rn{font-size:17px;color:var(--ink-mute);padding-top:12px;}'
'.rate-table td.rn.up{color:var(--accent);}'
'.rate-table td.rn.down{color:var(--good);}'
'.rate-table td.ph,.rate-table td.eff{font-family:var(--mono);font-size:13px;color:var(--ink-soft);white-space:nowrap;}'
'.rate-table td.fil a{font-family:var(--mono);font-size:11px;color:var(--ink-mute);text-decoration:none;white-space:nowrap;}'
'.rate-table td.fil a:hover{color:var(--accent);}'
'.hub-list h3{font-family:var(--serif);font-size:20px;margin:22px 0 6px;}'
'.hub-list ul{list-style:none;margin:0 0 4px;padding:0;}'
'.hub-list li{border-bottom:1px solid var(--rule);}'
'.hub-list li a{display:flex;justify-content:space-between;align-items:baseline;gap:12px;padding:10px 2px;text-decoration:none;color:var(--ink);font-size:16px;}'
'.hub-list li a:hover{color:var(--accent);}'
'.hub-chg{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--accent);white-space:nowrap;}'
'@media (max-width:480px){'
'.rz-zip{flex-direction:column;align-items:flex-start;}'
'}'
'</style>')

def breadcrumb(name, url):
    return json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"BoringRate","item":"https://boringrate.com"},
        {"@type":"ListItem","position":2,"name":name,"item":url}]}, indent=2)

def faqld(faq):
    return json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}, indent=2)

def build(cfg):
    s = open(TEMPLATE, encoding='utf-8').read()
    # ---- head (swap the 8 TN-specific tags by their exact template strings) ----
    HEAD = {
      '<link rel="canonical" href="https://boringrate.com/article/tennessee-rates-dropping.html" />':
        f'<link rel="canonical" href="{cfg["url"]}" />',
      '<title>Tennessee auto insurance rate changes in 2026: who cut and who raised — BoringRate</title>':
        f'<title>{cfg["title"]} — BoringRate</title>',
      '<meta name="description" content="State Farm cut twice (-10.7% then -6.8%), Progressive -4.3%, Shelter -3.4%. See every approved 2026 Tennessee auto insurance rate filing - who cut, who raised, and whether your renewal reflects it." />':
        f'<meta name="description" content="{cfg["desc"]}" />',
      '<meta property="og:url" content="https://boringrate.com/article/tennessee-rates-dropping.html" />':
        f'<meta property="og:url" content="{cfg["url"]}" />',
      '<meta property="og:title" content="Tennessee auto insurance rate changes in 2026: who cut and who raised — BoringRate" />':
        f'<meta property="og:title" content="{cfg["title"]} — BoringRate" />',
      '<meta name="twitter:title" content="Tennessee auto insurance rate changes in 2026: who cut and who raised — BoringRate" />':
        f'<meta name="twitter:title" content="{cfg["title"]} — BoringRate" />',
    }
    for k,v in HEAD.items():
        assert k in s, f'head miss: {k[:50]}'
        s = s.replace(k, v)
    # og:description + twitter:description (share cfg['ogdesc'])
    s = re.sub(r'<meta property="og:description" content="[^"]*" />',
               f'<meta property="og:description" content="{cfg["ogdesc"]}" />', s, count=1)
    s = re.sub(r'<meta name="twitter:description" content="[^"]*" />',
               f'<meta name="twitter:description" content="{cfg["ogdesc"]}" />', s, count=1)
    # ---- JSON-LD (regenerate both blocks) ----
    s = re.sub(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "BreadcrumbList".*?</script>',
               '<script type="application/ld+json">\n'+breadcrumb(cfg["title"], cfg["url"])+'\n</script>', s, count=1, flags=re.S)
    s = re.sub(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "FAQPage".*?</script>',
               '<script type="application/ld+json">\n'+faqld(cfg["faq"])+'\n</script>', s, count=1, flags=re.S)
    # ---- append nav-fix + rz-zip style after the template's ca-link-style ----
    CALINK = '.article-body a.ca-link:hover{border-bottom-color:var(--accent);}</style>'
    assert CALINK in s, 'ca-link-style anchor missing'
    s = s.replace(CALINK, CALINK + RZ_STYLE, 1)
    # ---- site-alert banner ----
    s = s.replace('      <span class="site-alert-tag">Tennessee</span>\n      <span class="site-alert-text">State Farm cut Tennessee auto rates twice in a year &mdash; see every approved 2026 filing.</span>',
                  f'      <span class="site-alert-tag">{cfg["state"]}</span>\n      <span class="site-alert-text">{cfg["alert"]}</span>')
    # ---- body region: thin ZIP (no coverage tile), then article; a 2nd thin ZIP
    #      CTA at the end (email block dropped — its shared JS null-guards, so
    #      leaving the untouched <script> is safe). Region runs header -> <footer>,
    #      so this new body also supplies the closing article-body + wrap-narrow divs.
    top = cfg.get('topzip', "See who&rsquo;s actually cheapest in your ZIP:")
    bot = cfg.get('botzip', "Ready to stop overpaying? Compare every carrier for your ZIP:")
    header = (f'<div class="article-header">\n'
      f'    <div class="article-kicker"><a href="{cfg["tracker"]}">Rate Tracker</a> &nbsp;&middot;&nbsp; {cfg["state"]} &nbsp;&middot;&nbsp; {cfg["read"]} min read</div>\n'
      f'    <h1 class="article-title">{cfg["h1"]}</h1>\n'
      f'    <p class="article-dek">{cfg["dek"]}</p>\n'
      f'    <div class="article-byline">BoringRate Editorial &nbsp;&middot;&nbsp; July 2026</div>\n'
      f'  </div>\n\n  <div class="article-body">\n')
    mid = cfg['hub_body'] if cfg.get('hub_body') else (table(cfg["rows"]) + '\n' + cfg["prose"])
    body = (header + thinzip(top) + '\n\n' + mid
            + '\n\n    ' + thinzip(bot) + '\n\n  </div>\n</div>\n\n')
    i0 = s.index('<div class="article-header">'); i1 = s.index('<footer>')
    s = s[:i0] + body + s[i1:]
    open(cfg["path"], 'w', encoding='utf-8').write(s)
    # leftover guard
    bad = [w for w in ('Tennessee','Shelter') if w.lower() in re.sub(r'(?s)<div class="nav-mega".*?</div></div></div></div>', '', s).lower()
           and w.lower() in cfg["prose"].lower()]
    print(f'  wrote {cfg["path"]} ({len(s)} bytes)')

PAGES = []  # populated by gen_reactive_config.py import below

def hub_body(pages):
    """Grouped link list for the hub — auto-updates as reactive pages are added."""
    from collections import defaultdict
    by_state = defaultdict(list)
    for c in pages:
        car, _h, _t, _f, chg, _n, _u = c['rows'][0]           # first row = target carrier
        by_state[c['state']].append((car, chg, c['url'].replace('https://boringrate.com', '')))
    out = ['<p>If your car insurance renewal jumped, you are not imagining it &mdash; and unlike most '
           'sites, we can show you the <strong>actual approved rate filing</strong> behind it. Find your '
           'carrier and state below. Each explainer breaks down how much the carrier raised, how the '
           'increase varies by driver, and &mdash; the part your renewal notice never mentions &mdash; '
           'which competitors are <em>cutting</em> rates in your state right now.</p>',
           '<h2>Find your carrier and state</h2>', '<div class="hub-list">']
    for st in sorted(by_state):
        out.append(f'<h3>{st}</h3>\n<ul>')
        for car, chg, href in sorted(by_state[st]):
            out.append(f'<li><a href="{href}">Why did my {car} rate go up in {st}? '
                       f'<span class="hub-chg">{chg}</span></a></li>')
        out.append('</ul>')
    out.append('</div>')
    out.append('<p>Don&rsquo;t see your carrier or state yet? We add explainers as we pull each '
               'state&rsquo;s filings. In the meantime, the <a class="ca-link" href="/article/rate-changes/">'
               '2026 Rate Change Tracker</a> shows every approved change we&rsquo;ve recorded, and '
               '<a class="ca-link" href="/article/premium-went-up.html">Why Your Premium Went Up</a> '
               'explains the forces behind rising rates &mdash; or just compare every carrier for your ZIP above.</p>')
    return '\n'.join(out)

def hub_cfg(pages):
    return {
     'path': 'article/why-your-rate-went-up.html',
     'url': 'https://boringrate.com/article/why-your-rate-went-up.html',
     'title': 'Why did my car insurance rate go up? Find your carrier and state',
     'desc': 'Your carrier raised your rate? Find the actual approved SERFF filing behind it - how much, the range by driver, and which competitors are cutting rates in your state right now.',
     'ogdesc': 'Find the actual approved rate filing behind your car insurance increase - by carrier and state - plus who is cutting rates near you. Primary-source, no estimates.',
     'state': 'Rate increases', 'read': '2', 'tracker': '/article/rate-changes/',
     'alert': 'Your rate went up? Find the actual approved filing behind it &mdash; by carrier and state.',
     'h1': 'Why did my car insurance rate go up?',
     'dek': 'Your renewal jumped and no claim explains it. Find your carrier and state below for the <strong>actual approved rate filing</strong> &mdash; how much they raised, how it varies by driver, and who&rsquo;s cutting rates near you.',
     'topzip': "See who&rsquo;s cheapest in your ZIP right now:",
     'hub_body': hub_body(pages), 'rows': [], 'prose': '',
     'faq': [
       ('Why did my car insurance rate go up if I did not file a claim?',
        'Auto rates are set at the book level, not per customer: your carrier files a statewide rate change with the insurance department based on its overall loss costs, and it applies to you at renewal regardless of your own claims. Our explainers link the actual approved filing for your carrier and state so you can see the exact figure and reasoning.'),
       ('How do I find the exact filing behind my increase?',
        'Pick your carrier and state from the list on this page. Each explainer cites the approved SERFF filing by tracking number - the size of the increase, how it varies by driver, and which competitors cut rates in the same state.'),
       ('Does a rate increase mean I should switch carriers?',
        'Often, yes - especially when other carriers in your state are cutting. A rate change applies at renewal, and a carrier that raised you can be more expensive than a competitor. Comparing every carrier for your exact ZIP and profile is the only way to know your lowest current price.'),
     ],
    }

if __name__ == '__main__':
    from gen_reactive_config import PAGES
    print(f'stamping {len(PAGES)} reactive pages + hub from {TEMPLATE}')
    for cfg in PAGES:
        build(cfg)
    build(hub_cfg(PAGES))
    print('  wrote article/why-your-rate-went-up.html (hub)')
