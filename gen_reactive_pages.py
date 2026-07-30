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

def row(name, href, trk, fid, change, note, up):
    cl = ' style="color:var(--accent);"' if up else ''
    cn = f'<a class="ca-link" href="{href}">{name}</a>' if href else name
    return (f'          <tr>\n'
            f'            <td class="cn">{cn}<br><a class="clink" href="{SERFF}{fid}" target="_blank" rel="noopener nofollow">SERFF {trk} &rarr;</a></td>\n'
            f'            <td class="rn"{cl}>{change}</td>\n'
            f'            <td class="note">{note}</td>\n'
            f'          </tr>\n')

def table(rows):
    body = ''.join(row(*r) for r in rows)
    return ('    <div id="rate-table">\n      <table class="rate-table">\n        <thead>\n'
            '          <tr><th>Carrier</th><th>Latest approved change</th><th>What the filing says</th></tr>\n'
            '        </thead>\n        <tbody>\n' + body +
            '        </tbody>\n      </table>\n    </div>\n')

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
    # ---- site-alert banner ----
    s = s.replace('      <span class="site-alert-tag">Tennessee</span>\n      <span class="site-alert-text">State Farm cut Tennessee auto rates twice in a year &mdash; see every approved 2026 filing.</span>',
                  f'      <span class="site-alert-tag">{cfg["state"]}</span>\n      <span class="site-alert-text">{cfg["alert"]}</span>')
    # ---- email heading ----
    s = s.replace('<strong>Get a Boring Reminder when Tennessee rates move again.</strong>',
                  f'<strong>Get a Boring Reminder when {cfg["state"]} rates move again.</strong>')
    # ---- body region ----
    tooltiles = ('<div class="tooltiles"><div class="tile"><div class="tile-kicker">Compare rates</div>'
      '<div class="tile-name">Cheapest car insurance for your ZIP</div><div class="tile-desc">Rank every '
      'carrier by estimated price for your exact ZIP and profile &mdash; in seconds, no calls.</div>'
      '<form class="tile-zipform" onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z)){location.href=\'/?zip=\'+z}else{this.zc.focus()}">'
      '<input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
      '<button type="submit" class="tile-zip-btn">Compare &rarr;</button></form></div>'
      '<div class="tile"><div class="tile-kicker">Coverage calculator</div><div class="tile-name">Not sure how much you need?</div>'
      '<div class="tile-desc">See what to buy and what to skip &mdash; and how each choice changes your price.</div>'
      '<a class="tbtn secondary" href="/coverage.html">Help me choose my coverage options &rarr;</a></div></div>')
    header = (f'<div class="article-header">\n'
      f'    <div class="article-kicker"><a href="{cfg["tracker"]}">Rate Tracker</a> &nbsp;&middot;&nbsp; {cfg["state"]} &nbsp;&middot;&nbsp; {cfg["read"]} min read</div>\n'
      f'    <h1 class="article-title">{cfg["h1"]}</h1>\n'
      f'    <p class="article-dek">{cfg["dek"]}</p>\n'
      f'    <div class="article-byline">BoringRate Editorial &nbsp;&middot;&nbsp; July 2026</div>\n'
      f'  </div>\n\n  <div class="article-body">\n')
    body = header + tooltiles + '\n\n' + table(cfg["rows"]) + '\n' + cfg["prose"] + '\n\n    '
    i0 = s.index('<div class="article-header">'); i1 = s.index('<div class="article-email">')
    s = s[:i0] + body + s[i1:]
    open(cfg["path"], 'w', encoding='utf-8').write(s)
    # leftover guard
    bad = [w for w in ('Tennessee','Shelter') if w.lower() in re.sub(r'(?s)<div class="nav-mega".*?</div></div></div></div>', '', s).lower()
           and w.lower() in cfg["prose"].lower()]
    print(f'  wrote {cfg["path"]} ({len(s)} bytes)')

PAGES = []  # populated by gen_reactive_config.py import below

if __name__ == '__main__':
    from gen_reactive_config import PAGES
    print(f'stamping {len(PAGES)} reactive pages from {TEMPLATE}')
    for cfg in PAGES:
        build(cfg)
