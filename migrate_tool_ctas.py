#!/usr/bin/env python3
# Replace the dark in-article "zip-embed" CTA with a clean two-tile paired-tool module
# (Option B): a Rate tile with a working ZIP box + a Coverage tile. Product-aware
# (auto/renters/home). Keeps embedZipForm/embedZipInput IDs so the existing per-page
# redirect script still wires the ZIP box to the correct rate tool. Idempotent.
import os, re

ZIP_EMBED = re.compile(r'<div class="zip-embed">.*?</form>\s*</div>', re.S)

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

def product(path):
    if "/renters/" in path: return ("renters insurance", "/renters/coverage.html")
    if "/home/" in path:    return ("home insurance", "/home/coverage.html")
    return ("car insurance", "/coverage.html")

def module(path):
    label, cov = product(path)
    return ('<div class="tooltiles">'
      '<div class="tile">'
      '<div class="tile-kicker">Compare rates</div>'
      f'<div class="tile-name">Cheapest {label} for your ZIP</div>'
      '<div class="tile-desc">Rank every carrier by estimated price for your exact ZIP and profile &mdash; in seconds, no calls.</div>'
      '<form class="tile-zipform" id="embedZipForm" autocomplete="off">'
      '<input class="tile-zip-input" id="embedZipInput" type="text" maxlength="5" inputmode="numeric" placeholder="ZIP" aria-label="ZIP code" />'
      '<button type="submit" class="tile-zip-btn">Compare &rarr;</button>'
      '</form>'
      '</div>'
      '<div class="tile">'
      '<div class="tile-kicker">Coverage calculator</div>'
      '<div class="tile-name">Not sure how much you need?</div>'
      '<div class="tile-desc">See what to buy and what to skip &mdash; and how each choice changes your price.</div>'
      f'<a class="tbtn secondary" href="{cov}">Help me choose my coverage options &rarr;</a>'
      '</div>'
      '</div>')

n = 0
for root, _, files in os.walk("."):
    if "/.git" in root: continue
    for fn in files:
        if not fn.endswith(".html"): continue
        p = os.path.join(root, fn)
        s = open(p, encoding="utf-8").read()
        if 'class="tooltiles"' in s: continue          # already migrated
        if '<div class="zip-embed">' not in s: continue
        s2, cnt = ZIP_EMBED.subn(lambda _m: module(p), s)
        if cnt == 0: continue
        if "</style>" in s2:                            # inject CSS once
            s2 = s2.replace("</style>", CSS + "</style>", 1)
        open(p, "w", encoding="utf-8").write(s2)
        n += 1
print("migrated", n, "pages (zip-embed -> two-tile module)")
