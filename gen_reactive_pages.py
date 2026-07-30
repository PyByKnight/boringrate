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

def thinzip(label):
    """A thin, single-row ZIP entry — small enough that the reader keeps reading."""
    return ('<div class="rz-zip"><span class="rz-zip-label">'+label+'</span>'
      '<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\').replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z)){location.href=\'/?zip=\'+z}else{this.zc.focus()}">'
      '<input class="rz-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
      '<button type="submit" class="rz-zip-btn">Compare &rarr;</button></form></div>')

# Late <style> appended after the template's ca-link-style. Two fixes:
#  (1) nav — article-page inline CSS predates the dropdown nav, so the base
#      (desktop) .nav-dd-* styling is missing and build_nav's Tools/Product
#      buttons render unstyled. Port the tool-page rules (base + <=480 inline row).
#  (2) rz-zip — the thin inline ZIP component that replaces the big two-tile module.
NAVZIP_STYLE = (
'<!-- nav-desktop-fix + rz-zip --><style>'
'nav.primary{align-items:center;gap:20px;margin-left:auto;}'
'.nav-dd-group{position:relative;}'
'.nav-dd-btn{font-family:var(--mono);font-size:11px;letter-spacing:0.07em;text-transform:uppercase;color:var(--ink-soft);background:none;border:1px solid var(--rule);padding:6px 12px;cursor:pointer;white-space:nowrap;transition:all 120ms;}'
'.nav-dd-btn:hover,.nav-dd-btn[aria-expanded="true"]{color:var(--ink);border-color:var(--ink);background:var(--paper-deep);}'
'.nav-dd-panel{display:none;position:absolute;top:calc(100% + 6px);left:0;background:var(--paper);border:1px solid var(--ink);min-width:180px;z-index:200;box-shadow:0 4px 16px rgba(0,0,0,0.08);}'
'.nav-dd-panel.open{display:flex;flex-direction:column;}'
'.nav-dd-panel a{font-family:var(--mono);font-size:11px;letter-spacing:0.06em;text-transform:uppercase;color:var(--ink-soft);text-decoration:none;padding:9px 14px;border-bottom:1px solid var(--rule);white-space:nowrap;transition:background 100ms,color 100ms;}'
'.nav-dd-panel a:last-child{border-bottom:none;}'
'.nav-dd-panel a:hover{background:var(--paper-deep);color:var(--ink);}'
'.nav-dd-panel a.active{background:var(--ink);color:var(--paper);}'
'.rz-zip{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:22px 0;padding:12px 16px;background:var(--paper-deep);border:1px solid var(--rule);}'
'.rz-zip-label{font-family:var(--sans);font-size:15px;font-weight:600;color:var(--ink);}'
'.rz-zip form{display:flex;gap:8px;margin:0;}'
'.rz-zip-input{font-family:var(--mono);font-size:14px;padding:8px 10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:92px;}'
'.rz-zip-btn{font-family:var(--mono);font-size:12px;text-transform:uppercase;letter-spacing:0.06em;padding:8px 16px;background:var(--accent);color:var(--paper);border:none;cursor:pointer;white-space:nowrap;}'
'.rz-zip-btn:hover{opacity:0.9;}'
'@media (max-width:480px){'
'.nav-dd-group{display:none;}'
'.nav-dd-group:has(#navDdProductPanel){display:flex;order:10;width:100%;border-top:1px solid var(--rule);margin-top:8px;}'
'.nav-dd-group:has(#navDdProductPanel) > .nav-dd-btn{display:none;}'
'.nav-dd-group:has(#navDdProductPanel) > .nav-dd-panel{display:flex !important;position:static;border:1px solid var(--rule);box-shadow:none;background:transparent;width:100%;min-width:0;}'
'.nav-dd-group:has(#navDdProductPanel) > .nav-dd-panel a{flex:1;text-align:center;border-right:1px solid var(--rule);border-bottom:none;padding:7px 4px;font-size:10px;}'
'.nav-dd-group:has(#navDdProductPanel) > .nav-dd-panel a:last-child{border-right:none;}'
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
    s = s.replace(CALINK, CALINK + NAVZIP_STYLE, 1)
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
    body = (header + thinzip(top) + '\n\n' + table(cfg["rows"]) + '\n' + cfg["prose"]
            + '\n\n    ' + thinzip(bot) + '\n\n  </div>\n</div>\n\n')
    i0 = s.index('<div class="article-header">'); i1 = s.index('<footer>')
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
