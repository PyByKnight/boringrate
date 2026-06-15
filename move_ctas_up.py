#!/usr/bin/env python3
# Promote the two-tile paired CTA to HIGH on each SEO page and de-dupe:
#  - state/metro pages (have the ranking block): drop the ranking's small inline ZIP
#    form + the tiny coverage text-link, and place the two-tile right under the table.
#  - carrier pages (no ranking, have a TLDR): place the two-tile right after the TLDR.
#  - otherwise: keep the tile where it is (re-inserted before the email block).
# Tile uses a self-contained inline ZIP form (product-aware), no id/script dependency.
import os, re, sys

TILE_RE = re.compile(r'<div class="tooltiles">.*?Help me choose my coverage options &rarr;</a></div></div>', re.S)
RANK_FORM_RE = re.compile(r'<form onsubmit="event\.preventDefault.*?</form>\s*', re.S)
COV_LINK_RE = re.compile(r'<p[^>]*>Not sure how much coverage you need\?.*?</p>\s*', re.S)
TLDR_RE = re.compile(r'<div class="tldr-card">.*?</ul>\s*</div>', re.S)

def prod_of(path):
    if "/renters/" in path: return "renters"
    if "/home/" in path: return "home"
    return "auto"

def tile(prod):
    rate = {"auto":"/","renters":"/renters/","home":"/home/"}[prod]
    cov  = {"auto":"/coverage.html","renters":"/renters/coverage.html","home":"/home/coverage.html"}[prod]
    label= {"auto":"car insurance","renters":"renters insurance","home":"home insurance"}[prod]
    onsub=("event.preventDefault();var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);"
           "if(/^\\d{5}$/.test(z)){location.href='"+rate+"?zip='+z}else{this.zc.focus()}")
    return ('<div class="tooltiles">'
      '<div class="tile"><div class="tile-kicker">Compare rates</div>'
      f'<div class="tile-name">Cheapest {label} for your ZIP</div>'
      '<div class="tile-desc">Rank every carrier by estimated price for your exact ZIP and profile &mdash; in seconds, no calls.</div>'
      f'<form class="tile-zipform" onsubmit="{onsub}"><input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" /><button type="submit" class="tile-zip-btn">Compare &rarr;</button></form>'
      '</div>'
      '<div class="tile"><div class="tile-kicker">Coverage calculator</div>'
      '<div class="tile-name">Not sure how much you need?</div>'
      '<div class="tile-desc">See what to buy and what to skip &mdash; and how each choice changes your price.</div>'
      f'<a class="tbtn secondary" href="{cov}">Help me choose my coverage options &rarr;</a>'
      '</div></div>')

def process(s, path):
    if 'class="tooltiles"' not in s: return s, "no-tile"
    prod = prod_of(path)
    T = tile(prod)
    s = TILE_RE.sub("", s, count=1)            # remove existing tile
    if "<!-- state-rankings-end -->" in s:
        # de-dupe the ranking's inline form + coverage text-link, then place tile under the table
        head, _, tail = s.partition("<!-- state-rankings-end -->")
        # operate only within the ranking region (before the end marker)
        rs = head.rfind("<!-- state-rankings-start -->")
        block = head[rs:]
        block = RANK_FORM_RE.sub("", block, count=1)
        block = COV_LINK_RE.sub("", block, count=1)
        block = block.replace("</table>", "</table>\n" + T + "\n", 1)
        s = head[:rs] + block + "<!-- state-rankings-end -->" + tail
        return s, "ranking"
    m = TLDR_RE.search(s)
    if m:
        s = s[:m.end()] + "\n" + T + "\n" + s[m.end():]
        return s, "tldr"
    # fallback: put it back before the email block / footer
    if '<div class="article-email"' in s:
        s = s.replace('<div class="article-email"', T + '\n    <div class="article-email"', 1)
    elif "<footer" in s:
        i = s.index("<footer"); s = s[:i] + '<div class="wrap-narrow">' + T + '</div>\n' + s[i:]
    return s, "fallback"

if __name__ == "__main__":
    targets = sys.argv[1:] or None
    counts = {}
    files = []
    if targets:
        files = targets
    else:
        for root,_,fs in os.walk("."):
            if "/.git" in root: continue
            for fn in fs:
                if fn.endswith(".html"): files.append(os.path.join(root,fn))
    n=0
    for p in files:
        s=open(p,encoding="utf-8").read()
        s2,how=process(s,p)
        counts[how]=counts.get(how,0)+1
        if s2!=s:
            open(p,"w",encoding="utf-8").write(s2); n+=1
    print("processed", n, "files |", counts)
