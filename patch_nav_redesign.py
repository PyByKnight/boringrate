#!/usr/bin/env python3
"""Patch all site pages with redesigned hamburger nav.
Structure: Tools (3 direct links) + Research (4 tab panels: State, Metro, Carrier, Guides)
Also fixes the hamburger JS to use the simpler tab-based approach.
"""
import os, glob, re

ROOT = "/home/knighttyler/boringrate"

METRO_NAMES = {
    'albany':'Albany','albuquerque':'Albuquerque','anchorage':'Anchorage',
    'atlanta':'Atlanta','austin':'Austin','bakersfield':'Bakersfield',
    'baltimore':'Baltimore','baton-rouge':'Baton Rouge','billings':'Billings',
    'birmingham':'Birmingham','boise':'Boise','boston':'Boston',
    'buffalo':'Buffalo','burlington-vt':'Burlington, VT','charleston-wv':'Charleston, WV',
    'charlotte':'Charlotte','cheyenne':'Cheyenne','chicago':'Chicago',
    'cincinnati':'Cincinnati','cleveland':'Cleveland','columbia-sc':'Columbia, SC',
    'columbus':'Columbus','dallas-fort-worth':'Dallas–Ft. Worth','denver':'Denver',
    'des-moines':'Des Moines','detroit':'Detroit','el-paso':'El Paso',
    'fargo':'Fargo','fresno':'Fresno','greensboro':'Greensboro',
    'greenville-spartanburg':'Greenville, SC','hartford':'Hartford','honolulu':'Honolulu',
    'houston':'Houston','indianapolis':'Indianapolis','jackson-ms':'Jackson, MS',
    'jacksonville':'Jacksonville','kansas-city':'Kansas City','knoxville':'Knoxville',
    'las-vegas':'Las Vegas','little-rock':'Little Rock','los-angeles':'Los Angeles',
    'louisville':'Louisville','madison':'Madison','manchester-nh':'Manchester, NH',
    'memphis':'Memphis','miami':'Miami','milwaukee':'Milwaukee',
    'minneapolis-st-paul':'Minneapolis–St. Paul','nashville':'Nashville',
    'new-jersey':'New Jersey','new-orleans':'New Orleans','new-york-city':'New York City',
    'norfolk':'Norfolk','oklahoma-city':'Oklahoma City','omaha':'Omaha',
    'orlando':'Orlando','philadelphia':'Philadelphia','phoenix':'Phoenix',
    'pittsburgh':'Pittsburgh','portland':'Portland','portland-me':'Portland, ME',
    'providence':'Providence','raleigh-durham':'Raleigh–Durham','richmond':'Richmond',
    'riverside-inland-empire':'Riverside–IE','rochester':'Rochester','sacramento':'Sacramento',
    'salt-lake-city':'Salt Lake City','san-antonio':'San Antonio','san-diego':'San Diego',
    'san-jose':'San Jose','seattle':'Seattle','sioux-falls':'Sioux Falls',
    'spokane':'Spokane','st-louis':'St. Louis','syracuse':'Syracuse',
    'tampa':'Tampa','tucson':'Tucson','tulsa':'Tulsa',
    'washington-dc':'Washington, D.C.','wichita':'Wichita','wilmington-de':'Wilmington, DE',
}

STATES = [
    ('Alabama','alabama'),('Alaska','alaska'),('Arizona','arizona'),('Arkansas','arkansas'),
    ('California','california'),('Colorado','colorado'),('Connecticut','connecticut'),
    ('Delaware','delaware'),('Florida','florida'),('Georgia','georgia'),('Hawaii','hawaii'),
    ('Idaho','idaho'),('Illinois','illinois'),('Indiana','indiana'),('Iowa','iowa'),
    ('Kansas','kansas'),('Kentucky','kentucky'),('Louisiana','louisiana'),('Maine','maine'),
    ('Maryland','maryland'),('Massachusetts','massachusetts'),('Michigan','michigan'),
    ('Minnesota','minnesota'),('Mississippi','mississippi'),('Missouri','missouri'),
    ('Montana','montana'),('Nebraska','nebraska'),('Nevada','nevada'),
    ('New Hampshire','new-hampshire'),('New Jersey','new-jersey'),('New Mexico','new-mexico'),
    ('New York','new-york'),('North Carolina','north-carolina'),('North Dakota','north-dakota'),
    ('Ohio','ohio'),('Oklahoma','oklahoma'),('Oregon','oregon'),('Pennsylvania','pennsylvania'),
    ('Rhode Island','rhode-island'),('South Carolina','south-carolina'),
    ('South Dakota','south-dakota'),('Tennessee','tennessee'),('Texas','texas'),
    ('Utah','utah'),('Vermont','vermont'),('Virginia','virginia'),('Washington','washington'),
    ('Washington D.C.','washington-dc'),('West Virginia','west-virginia'),
    ('Wisconsin','wisconsin'),('Wyoming','wyoming'),
]

NATIONAL_CARRIERS = [
    ('USAA','usaa','Military &amp; family'),
    ('GEICO','geico','Online shoppers'),
    ('State Farm','state-farm','Local agents'),
    ('Progressive','progressive','High-risk &amp; incidents'),
    ('Allstate','allstate','Accident forgiveness'),
    ('Liberty Mutual','liberty-mutual','New car replacement'),
    ('Farmers','farmers','Full-service agents'),
    ('Nationwide','nationwide','Vanishing deductible'),
    ('Erie','erie','Mid-Atlantic &amp; Midwest'),
    ('American Family','american-family','Midwest families'),
    ('Amica','amica','Claims service'),
    ('Auto-Owners','auto-owners','26-state agent'),
    ('Travelers','travelers','Homeowner bundles'),
    ('Safeco','safeco','Independent agents'),
    ('The Hartford','the-hartford','AARP &amp; 50+ drivers'),
    ('Root Insurance','root-insurance','Telematics · safe drivers'),
    ('AAA / CSAA','aaa','Members &amp; roadside'),
]

LOCAL_CARRIERS = [
    ('Texas Farm Bureau','texas-farm-bureau','Texas only'),
    ('Georgia Farm Bureau','georgia-farm-bureau','Georgia only'),
    ('Tennessee Farm Bureau','tennessee-farm-bureau','Tennessee only'),
    ('NC Farm Bureau','nc-farm-bureau','North Carolina'),
    ('Kentucky Farm Bureau','kentucky-farm-bureau','Kentucky only'),
    ('Louisiana Farm Bureau','louisiana-farm-bureau','Louisiana only'),
    ('PEMCO','pemco','WA &amp; OR'),
    ('NJM Insurance','njm','NJ / CT / PA'),
    ('Wawanesa','wawanesa','California only'),
    ('Mercury Insurance','mercury','CA &amp; 10 states'),
    ('Shelter Insurance','shelter','15-state Central'),
    ('MAPFRE Insurance','mapfre','Massachusetts'),
    ('NYCM Insurance','nycm','New York only'),
    ('Alfa Insurance','alfa','Southeast'),
    ('Country Financial','country-financial','Midwest'),
]

GUIDES = [
    ('Coverage Guide — How Much Do You Actually Need?', '/article/coverage-guide.html'),
    ('Credit Score &amp; Car Insurance — What\'s the Link?', '/article/credit-score-insurance.html'),
    ('Why Your Premium Went Up (And What To Do)', '/article/premium-went-up.html'),
    ('Car Insurance Shopping Strategy', '/article/shopping-strategy.html'),
    ('SR-22 Insurance Explained', '/article/sr22-insurance.html'),
    ('Young Driver Insurance Guide', '/article/young-drivers.html'),
    ('State-by-State Rate Rankings', '/article/state-rankings.html'),
    ('Florida Rates — What\'s Changing in 2026', '/article/florida-rates-dropping.html'),
]


def build_nav_mega():
    # ── State panel ──
    state_links = ''.join(
        f'<a href="/article/state/{slug}.html">{name}</a>'
        for name, slug in STATES
    )

    # ── Metro panel ──
    metro_slugs = sorted(METRO_NAMES.keys())
    metro_links = ''.join(
        f'<a href="/article/metro/{slug}.html">{METRO_NAMES[slug]}</a>'
        for slug in metro_slugs
    )

    # ── Carrier panel: national then local ──
    nat_links = ''.join(
        f'<a href="/article/carrier/{slug}.html">{name} <span class="nav-mega-tag">{tag}</span></a>'
        for name, slug, tag in NATIONAL_CARRIERS
    )
    loc_links = ''.join(
        f'<a href="/article/carrier/{slug}.html">{name} <span class="nav-mega-tag">{tag}</span></a>'
        for name, slug, tag in LOCAL_CARRIERS
    )

    # ── Guides panel ──
    guide_links = ''.join(
        f'<a href="{href}">{title}</a>'
        for title, href in GUIDES
    )

    return (
        '<div class="nav-mega" id="navMega">'
        '<div class="nav-mega-inner">'

        # Tools
        '<div class="nav-section">'
        '<p class="nav-section-label">Tools</p>'
        '<div class="nav-tools">'
        '<a href="/" class="nav-tool"><span class="nav-tool-name">Rate Comparison</span><span class="nav-tool-desc">Rank every carrier for your ZIP</span></a>'
        '<a href="/coverage.html" class="nav-tool"><span class="nav-tool-name">Coverage Calculator</span><span class="nav-tool-desc">Find the right coverage level</span></a>'
        '<a href="/article/compare/index.html" class="nav-tool"><span class="nav-tool-name">Carrier Comparison</span><span class="nav-tool-desc">Head-to-head any two carriers</span></a>'
        '</div>'
        '</div>'

        # Research
        '<div class="nav-section">'
        '<p class="nav-section-label">Research</p>'
        '<div class="nav-res-tabs">'
        '<button type="button" class="nav-res-tab active" data-panel="res-state">State</button>'
        '<button type="button" class="nav-res-tab" data-panel="res-metro">Metro</button>'
        '<button type="button" class="nav-res-tab" data-panel="res-carrier">Carrier</button>'
        '<button type="button" class="nav-res-tab" data-panel="res-market">Market Share</button>'
        '<button type="button" class="nav-res-tab" data-panel="res-guides">Guides</button>'
        '</div>'
        '<div class="nav-res-panels">'

        f'<div class="nav-res-panel active" id="res-state"><div class="nav-mega-states">{state_links}</div></div>'
        f'<div class="nav-res-panel" id="res-metro"><div class="nav-res-metros">{metro_links}</div></div>'
        f'<div class="nav-res-panel" id="res-carrier">'
        f'<p class="nav-res-subhead">National carriers</p><div class="nav-res-carriers">{nat_links}</div>'
        f'<p class="nav-res-subhead" style="margin-top:14px;">Regional &amp; local</p><div class="nav-res-carriers">{loc_links}</div>'
        f'</div>'
        '<div class="nav-res-panel" id="res-market">'
        '<p class="nav-res-subhead">Rankings &amp; data</p>'
        '<div class="nav-res-guides">'
        '<a href="/article/market-share.html">National Carrier Market Share — who controls the U.S. market</a>'
        '<a href="/article/state-rankings.html">State-by-State Rate Rankings — avg. premium + top carriers per state</a>'
        '</div>'
        '</div>'
        f'<div class="nav-res-panel nav-res-guides" id="res-guides">{guide_links}</div>'

        '</div>'  # nav-res-panels
        '</div>'  # nav-section research
        '</div>'  # nav-mega-inner
        '</div>'  # nav-mega
    )


NEW_NAV_CSS = """
  .nav-mega-inner{display:block;padding:24px 28px;max-width:1180px;margin:0 auto;}
  .nav-section{margin-bottom:22px;}
  .nav-section:last-child{margin-bottom:0;}
  .nav-section-label{font-family:var(--mono);font-size:10px;letter-spacing:0.16em;text-transform:uppercase;color:rgba(246,241,232,0.35);margin:0 0 10px;padding-bottom:8px;border-bottom:1px solid rgba(246,241,232,0.12);}
  .nav-tools{display:flex;gap:2px;flex-wrap:wrap;}
  .nav-tool{display:flex;flex-direction:column;gap:3px;padding:11px 14px;text-decoration:none;color:var(--paper);flex:1;min-width:150px;background:rgba(246,241,232,0.04);border:1px solid rgba(246,241,232,0.08);transition:background 120ms;}
  .nav-tool:hover{background:rgba(246,241,232,0.1);}
  .nav-tool-name{font-family:var(--sans);font-size:13px;font-weight:500;color:var(--paper);}
  .nav-tool-desc{font-family:var(--mono);font-size:10px;color:rgba(246,241,232,0.38);letter-spacing:0.03em;}
  .nav-res-tabs{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:14px;}
  .nav-res-tab{font-family:var(--mono);font-size:11px;letter-spacing:0.08em;text-transform:uppercase;background:none;border:1px solid rgba(246,241,232,0.15);color:rgba(246,241,232,0.5);padding:6px 12px;cursor:pointer;transition:all 120ms;}
  .nav-res-tab:hover,.nav-res-tab.active{color:var(--paper);border-color:rgba(246,241,232,0.4);background:rgba(246,241,232,0.08);}
  .nav-res-panel{display:none;}
  .nav-res-panel.active{display:block;}
  .nav-mega-states{display:grid;grid-template-columns:repeat(5,1fr);gap:2px 0;}
  .nav-mega-states a{font-family:var(--mono);font-size:11px;color:rgba(246,241,232,0.65);text-decoration:none;padding:3px 0;transition:color 120ms;letter-spacing:0.02em;}
  .nav-mega-states a:hover{color:var(--paper);}
  .nav-res-metros{display:grid;grid-template-columns:repeat(7,1fr);gap:1px 0;}
  .nav-res-metros a{font-family:var(--mono);font-size:11px;color:rgba(246,241,232,0.65);text-decoration:none;padding:3px 0;transition:color 120ms;letter-spacing:0.02em;}
  .nav-res-metros a:hover{color:var(--paper);}
  .nav-res-subhead{font-family:var(--mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;color:rgba(246,241,232,0.3);margin:0 0 6px;}
  .nav-res-carriers{display:grid;grid-template-columns:repeat(4,1fr);gap:0 16px;}
  .nav-res-carriers a{font-family:var(--sans);font-size:12px;color:rgba(246,241,232,0.72);text-decoration:none;padding:5px 0;border-bottom:1px solid rgba(246,241,232,0.06);display:flex;justify-content:space-between;transition:color 120ms;}
  .nav-res-carriers a:hover{color:var(--paper);}
  .nav-res-guides a{display:block;font-family:var(--sans);font-size:13px;color:rgba(246,241,232,0.75);text-decoration:none;padding:7px 0;border-bottom:1px solid rgba(246,241,232,0.08);transition:color 120ms;}
  .nav-res-guides a:last-child{border-bottom:none;}
  .nav-res-guides a:hover{color:var(--paper);}"""

NEW_NAV_CSS_MOBILE = """
  @media(max-width:900px){
    .nav-mega-inner{padding:0;}
    .nav-section{margin:0;border-bottom:1px solid rgba(246,241,232,0.12);}
    .nav-section-label{padding:14px 20px;margin:0;border-bottom:none;}
    .nav-tools{flex-direction:column;gap:0;}
    .nav-tool{border:none;border-bottom:1px solid rgba(246,241,232,0.06);min-width:0;padding:12px 20px;}
    .nav-res-tabs{flex-direction:column;gap:0;margin:0;padding:0 20px 10px;}
    .nav-res-tab{border:none;border-bottom:1px solid rgba(246,241,232,0.08);text-align:left;padding:12px 0;}
    .nav-res-panel{padding:0 20px 14px;}
    .nav-mega-states{grid-template-columns:repeat(3,1fr);}
    .nav-res-metros{grid-template-columns:repeat(2,1fr);}
    .nav-res-carriers{grid-template-columns:1fr 1fr;gap:0 10px;}
  }
  @media(max-width:480px){
    .nav-mega-states{grid-template-columns:repeat(2,1fr);}
    .nav-res-metros{grid-template-columns:repeat(2,1fr);}
    .nav-res-carriers{grid-template-columns:1fr;}
  }"""

NEW_HAMBURGER_JS = (
    '<script>(function(){'
    'var btn=document.getElementById(\'navHamburger\');'
    'var mega=document.getElementById(\'navMega\');'
    'if(!btn||!mega)return;'
    'btn.addEventListener(\'click\',function(e){e.stopPropagation();var open=!mega.classList.contains(\'open\');mega.classList.toggle(\'open\',open);btn.classList.toggle(\'open\',open);btn.setAttribute(\'aria-expanded\',String(open));});'
    'document.addEventListener(\'click\',function(e){if(!btn.contains(e.target)&&!mega.contains(e.target)){mega.classList.remove(\'open\');btn.classList.remove(\'open\');btn.setAttribute(\'aria-expanded\',\'false\');}});'
    'mega.addEventListener(\'click\',function(e){var tab=e.target.closest(\'.nav-res-tab\');if(!tab)return;e.stopPropagation();var pid=tab.dataset.panel;var isActive=tab.classList.contains(\'active\');mega.querySelectorAll(\'.nav-res-tab\').forEach(function(t){t.classList.remove(\'active\');});mega.querySelectorAll(\'.nav-res-panel\').forEach(function(p){p.classList.remove(\'active\');});if(!isActive&&pid){tab.classList.add(\'active\');var panel=document.getElementById(pid);if(panel)panel.classList.add(\'active\');}});'
    '})();</script>'
)

OLD_HAMBURGER_JS_START = '<script>(function(){var btn=document.getElementById(\'navHamburger\')'


def replace_nav_mega(html, new_nav):
    """Replace the entire nav-mega div using depth counting."""
    open_tag = '<div class="nav-mega" id="navMega">'
    start = html.find(open_tag)
    if start == -1:
        return html
    depth = 0
    i = start
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return html[:start] + new_nav + html[i+6:]
            i += 6
        else:
            i += 1
    return html


def replace_hamburger_js(html, new_js):
    """Replace the hamburger script block."""
    start = html.find(OLD_HAMBURGER_JS_START)
    if start == -1:
        return html
    end = html.find('</script>', start)
    if end == -1:
        return html
    return html[:start] + new_js + html[end+9:]


def patch_file(path, new_nav):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    original = html

    # 1. Replace nav-mega HTML
    html = replace_nav_mega(html, new_nav)

    # 2. Add new nav CSS (override old nav-mega-inner and add new classes)
    if '.nav-section-label{' not in html:
        html = html.replace('\n</style>', NEW_NAV_CSS + NEW_NAV_CSS_MOBILE + '\n</style>', 1)

    # 3. Replace hamburger JS
    html = replace_hamburger_js(html, NEW_HAMBURGER_JS)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


# Collect all HTML files
all_files = (
    glob.glob(os.path.join(ROOT, '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'compare', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'state', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'carrier', '*.html')) +
    glob.glob(os.path.join(ROOT, 'article', 'metro', '*.html'))
)
# Exclude article/compare/index.html from nav update? No, include it.
all_files = sorted(set(all_files))

new_nav = build_nav_mega()

patched = skipped = 0
for path in all_files:
    if patch_file(path, new_nav):
        patched += 1
    else:
        skipped += 1
        print(f'SKIPPED: {os.path.relpath(path, ROOT)}')

print(f'\nDone: {patched} patched, {skipped} unchanged out of {len(all_files)} files.')
