#!/usr/bin/env python3
# Add the two-tile paired-tool CTA to high-intent AUTO pages that have no in-body tool
# CTA: compare pages, guides, rate-change trackers, and hubs. Self-contained inline ZIP
# form (no id collisions, works without the goZip script). Idempotent.
import os, re

EXCLUDE = {"index.html","coverage.html","renters/index.html","renters/coverage.html",
           "home/index.html","home/coverage.html","cta-preview.html","methodology.html"}

CSS = ("\n.tooltiles{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:40px 0;max-width:660px;}"
 ".tile{border:1px solid var(--rule);background:var(--paper-deep);padding:22px 22px 20px;display:flex;flex-direction:column;}"
 ".tile-kicker{font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:0.12em;color:var(--accent);margin-bottom:10px;}"
 ".tile-name{font-family:var(--serif);font-size:20px;font-weight:600;letter-spacing:-0.01em;margin-bottom:6px;line-height:1.15;color:var(--ink);}"
 ".tile-desc{font-size:14px;color:var(--ink-soft);line-height:1.5;margin-bottom:18px;flex:1;}"
 ".tbtn{display:inline-flex;align-items:center;justify-content:center;gap:8px;font-family:var(--sans);font-size:14px;font-weight:600;letter-spacing:0.02em;padding:13px 18px;text-decoration:none;white-space:nowrap;border:2px solid var(--ink);transition:background 120ms,color 120ms;text-align:center;line-height:1.25;}"
 ".tbtn.secondary{background:transparent;color:var(--ink);}"
 ".tbtn.secondary:hover{background:var(--ink);color:var(--paper);}"
 ".tile-zipform{display:flex;gap:0;align-items:stretch;}"
 ".tile-zip-input{flex:1;min-width:0;font-family:var(--mono);font-size:18px;letter-spacing:0.12em;text-align:center;padding:11px 12px;border:2px solid var(--ink);border-right:none;background:var(--paper);color:var(--ink);outline:none;}"
 ".tile-zip-input::placeholder{color:var(--ink-mute);}"
 ".tile-zip-btn{font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:0 18px;border:2px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer;white-space:nowrap;}"
 ".tile-zip-btn:hover{background:#8a1f0f;}"
 "@media(max-width:560px){.tooltiles{grid-template-columns:1fr;}}\n")

ONSUBMIT = ("event.preventDefault();var z=(this.zc.value||'').replace(/\\D/g,'').slice(0,5);"
            "if(/^\\d{5}$/.test(z)){location.href='/?zip='+z}else{this.zc.focus()}")
MODULE = ('<div class="tooltiles">'
  '<div class="tile">'
  '<div class="tile-kicker">Compare rates</div>'
  '<div class="tile-name">Cheapest car insurance for your ZIP</div>'
  '<div class="tile-desc">Rank every carrier by estimated price for your exact ZIP and profile &mdash; in seconds, no calls.</div>'
  f'<form class="tile-zipform" onsubmit="{ONSUBMIT}">'
  '<input class="tile-zip-input" name="zc" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
  '<button type="submit" class="tile-zip-btn">Compare &rarr;</button>'
  '</form>'
  '</div>'
  '<div class="tile">'
  '<div class="tile-kicker">Coverage calculator</div>'
  '<div class="tile-name">Not sure how much you need?</div>'
  '<div class="tile-desc">See what to buy and what to skip &mdash; and how each choice changes your price.</div>'
  '<a class="tbtn secondary" href="/coverage.html">Help me choose my coverage options &rarr;</a>'
  '</div>'
  '</div>')

n = 0
for root, _, files in os.walk("."):
    if "/.git" in root: continue
    for fn in files:
        if not fn.endswith(".html"): continue
        p = os.path.join(root, fn); rel = p[2:]
        if rel in EXCLUDE: continue
        if not rel.startswith("article/"): continue   # auto content tree only
        s = open(p, encoding="utf-8").read()
        if 'class="tooltiles"' in s: continue
        if '<div class="article-email"' in s:
            s = s.replace('<div class="article-email"', MODULE + '\n    <div class="article-email"', 1)
        elif "<footer" in s:
            i = s.index("<footer")
            s = s[:i] + '<div class="wrap-narrow">' + MODULE + '</div>\n' + s[i:]
        else:
            continue
        if "</style>" in s:
            s = s.replace("</style>", CSS + "</style>", 1)
        open(p, "w", encoding="utf-8").write(s); n += 1
print("inserted two-tile CTA into", n, "pages")
PYEOF = None
