#!/usr/bin/env python3
"""Build a landing page for every section directory that lacks one.

Nine of twelve section directories had no index.html, so /article/state/,
/renters/carrier/ etc. returned 404 — Googlebot path-climbs to these and
reported them in the Indexing report (2026-10-15 Coverage export). More
importantly a hub is an internal-link distribution point: the compare hub is
what de-orphaned 21 compare pages in c95ec15e.

Structure is cloned from article/rate-changes/index.html (clean shell: locked
thin rz-zip CTA, no .article-email, no .tooltiles). Only head tags and the
article-header/body region are replaced, so nav/CSS/footer stay single-source
— run build_nav.py after this, as with every other generator.

Idempotent: rewrites each hub from the scaffold every run.
"""
import re, os, glob, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))
SCAFFOLD = os.path.join(ROOT, "article/rate-changes/index.html")

# zip CTA target per line of business
CTA = {"auto": ("/?zip=",        "Compare every carrier in your ZIP:"),
       "renters": ("/renters/?zip=", "Compare every renters insurer in your ZIP:"),
       "home": ("/home/?zip=",   "Compare every home insurer in your ZIP:")}

# dir, line, <title> (<=60), h1, dek
SECTIONS = [
 ("article/state",    "auto", "Car Insurance Rates by State (2026) — All 51",
  "Car insurance rates by state",
  "Average premiums, the cheapest carriers, and what drives price in all 50 states and D.C. &mdash; modelled from public rate filings."),
 ("article/metro",    "auto", "Car Insurance Rates by Metro (2026) — 95 Cities",
  "Car insurance rates by metro",
  "City-level premium estimates for 95 U.S. metros. Rates inside a state vary more by metro than most shoppers expect."),
 ("article/carrier",  "auto", "Car Insurance Carrier Reviews (2026)",
  "Car insurance carrier reviews",
  "Rates, NAIC complaint ratios, and financial-strength grades for every carrier we track &mdash; the numbers carriers don&rsquo;t advertise."),
 ("renters/state",    "renters", "Renters Insurance Rates by State (2026) — All 51",
  "Renters insurance rates by state",
  "What renters insurance costs in each state, and which carriers are cheapest &mdash; all 50 states and D.C."),
 ("renters/metro",    "renters", "Renters Insurance Rates by Metro (2026)",
  "Renters insurance rates by metro",
  "Renters premiums for 83 U.S. metros. Your city matters more than your state for theft and water-damage risk."),
 ("renters/carrier",  "renters", "Renters Insurance Carrier Reviews (2026)",
  "Renters insurance carrier reviews",
  "Monthly cost, complaint ratios, and what each renters carrier is actually good at."),
 ("home/state",       "home", "Homeowners Insurance Rates by State (2026)",
  "Homeowners insurance rates by state",
  "Average homeowners premiums and the cheapest carriers in all 50 states and D.C., modelled from filed rates."),
 ("home/metro",       "home", "Home Insurance Rates by Metro (2026) — 28 Cities",
  "Home insurance rates by metro",
  "Metro-level homeowners premiums. Within a state, roof age and storm exposure move price more than the state average suggests."),
 ("home/carrier",     "home", "Homeowners Insurance Carrier Reviews (2026)",
  "Homeowners insurance carrier reviews",
  "Rates, complaint ratios, and financial strength for every homeowners carrier we track."),
]

def esc(s): return s.replace('"', "&quot;")

def page_name(path):
    """Display name from the page's own <title>, trimmed of the boilerplate tail."""
    t = H.unescape(re.search(r"<title>(.*?)</title>",
                   open(path, encoding="utf-8").read(4000), re.S).group(1)).strip()
    t = re.split(r"\s*[—|]\s*", t)[0]
    t = re.sub(r"\s*\(20\d\d\)\s*$", "", t).strip()
    for tail in (" Renters Insurance Rates", " Renters Insurance Review", " Renters Insurance",
                 " Homeowners Insurance Review", " Home Insurance Rates", " Car Insurance Rates",
                 " Car Insurance Requirements & Rates", " Car Insurance Minimums & Rates",
                 " Car Insurance", " Insurance Review"):
        if t.endswith(tail):
            return t[: -len(tail)].strip()
    t = re.sub(r"^Cheapest Homeowners Insurance in\s+", "", t)
    t = re.sub(r"^Is\s+(.*?)\s+Good(\s+Insurance)?\??$", r"\1", t)
    return t.strip()

def build(dirname, line, title, h1, dek, scaffold):
    entries = []
    for p in sorted(glob.glob(os.path.join(ROOT, dirname, "*.html"))):
        base = os.path.basename(p)
        if base == "index.html":
            continue
        entries.append((base, page_name(p)))
    entries.sort(key=lambda e: e[1].lower())

    url = f"https://boringrate.com/{dirname}/"
    s = scaffold
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf'\g<1>{url}\g<2>', s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{url}\g<2>', s)
    s = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", s)
    for tag, val in (('<meta name="description" content="', dek),
                     ('<meta property="og:title" content="', h1),
                     ('<meta property="og:description" content="', dek),
                     ('<meta name="twitter:title" content="', h1),
                     ('<meta name="twitter:description" content="', dek)):
        s = re.sub(re.escape(tag) + r'[^"]*(")',
                   lambda m, v=val: tag + esc(re.sub("<[^>]+>", "", v)) + '"', s, count=1)

    href, label = CTA[line]
    cta = ('<div class="rz-zip"><span class="rz-zip-label">' + label + '</span>'
           '<form onsubmit="event.preventDefault();var z=(this.zc.value||\'\')'
           '.replace(/\\D/g,\'\').slice(0,5);if(/^\\d{5}$/.test(z))'
           '{location.href=\'' + href + '\'+z}else{this.zc.focus()}">'
           '<input class="rz-zip-input" name="zc" type="text" maxlength="5" '
           'inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
           '<button type="submit" class="rz-zip-btn">Compare &rarr;</button></form></div>')

    links = "".join(f'<a href="/{dirname}/{b}">{H.escape(n)}</a>' for b, n in entries)
    grid = ('<div class="hub-grid">' + links + "</div>")

    body = f"""
  <div class="article-header">
    <div class="article-kicker"><a href="/">BoringRate</a> &nbsp;&middot;&nbsp; Index &nbsp;&middot;&nbsp; {len(entries)} pages</div>
    <h1 class="article-title">{h1}</h1>
    <p class="article-dek">{dek}</p>
    <div class="article-byline">BoringRate Editorial &nbsp;&middot;&nbsp; modelled from public rate filings</div>
  </div>
  <div class="article-body">
{cta}
{grid}
{cta}
  </div>
</div>
"""
    i = s.find('<div class="wrap-narrow">')
    j = s.find("<footer")
    assert i > 0 and j > i, dirname
    s = s[: i + len('<div class="wrap-narrow">')] + body + s[j:]

    css = ('<style>/* section hub index */\n'
           '.hub-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px 24px;margin:22px 0;}\n'
           '.hub-grid a{font-family:var(--mono);font-size:12px;color:var(--ink-soft);'
           'text-decoration:none;padding:4px 0;border-bottom:1px solid transparent;}\n'
           '.hub-grid a:hover{color:var(--ink);border-bottom-color:var(--rule);}\n'
           '@media (max-width:760px){.hub-grid{grid-template-columns:1fr 1fr;}}\n'
           '@media (max-width:480px){.hub-grid{grid-template-columns:1fr;}}\n'
           "</style>\n")
    k = s.find("</head>")
    s = s[:k] + css + s[k:]

    out = os.path.join(ROOT, dirname, "index.html")
    open(out, "w", encoding="utf-8").write(s)
    return out, len(entries)

def main():
    scaffold = open(SCAFFOLD, encoding="utf-8").read()
    # the scaffold is itself a hub; strip its body so only the shell is reused
    total = 0
    for dirname, line, title, h1, dek in SECTIONS:
        out, n = build(dirname, line, title, h1, dek, scaffold)
        print(f"  {out.replace(ROOT+'/',''):32} {n:3} links   title[{len(title)}]")
        total += n
    print(f"\n{len(SECTIONS)} hubs, {total} internal links created")

if __name__ == "__main__":
    main()
