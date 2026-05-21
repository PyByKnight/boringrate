#!/usr/bin/env python3
"""Patch compare pages (pass 2):
1. Replace old 4-field profile builder HTML with full 10-field form
2. Add CSS for new form elements + table row highlighting
3. Replace inline profile builder JS with shared compare-profile.js reference
"""
import os, re, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

# ── New CSS to inject before </style> ────────────────────────────────────────
NEW_CSS = """
  .pb-row-checks{align-items:flex-start;padding-top:2px;}
  .pb-checks{display:flex;flex-direction:column;gap:8px;}
  .pb-check{display:flex;align-items:center;gap:8px;font-family:var(--mono);font-size:11px;color:var(--ink-soft);cursor:pointer;letter-spacing:0.03em;user-select:none;}
  .pb-check input[type=checkbox]{accent-color:var(--ink);width:14px;height:14px;cursor:pointer;flex-shrink:0;}
  .pb-extra-row{display:flex;gap:16px;flex-wrap:wrap;margin:14px 0 0;padding-top:14px;border-top:1px solid var(--rule);}
  .pb-extra-group{display:flex;flex-direction:column;gap:5px;}
  .pb-carrier-group{flex:1;min-width:160px;}
  .pb-extra-label{font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);}
  .pb-zip-input{font-family:var(--mono);font-size:15px;letter-spacing:0.12em;text-align:center;padding:7px 10px;width:96px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);outline:none;transition:border-color 120ms;}
  .pb-zip-input:focus{border-color:var(--ink);}
  .pb-select{font-family:var(--sans);font-size:13px;padding:7px 28px 7px 10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);outline:none;cursor:pointer;width:100%;appearance:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6'><path d='M0 0l5 6 5-6' fill='%23161512'/></svg>");background-repeat:no-repeat;background-position:right 10px center;}
  .pb-select:focus{border-color:var(--ink);}
  .pb-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:16px;padding-top:16px;border-top:1px solid var(--rule);}
  .pb-cta-alt{background:transparent!important;color:var(--ink)!important;border:1px solid var(--ink);}
  .pb-cta-alt:hover{background:var(--paper-deep)!important;}
  .pb-shopping-note{font-family:var(--mono);font-size:11px;color:var(--accent);letter-spacing:0.04em;margin-top:8px;line-height:1.55;}
  .cmp-table tr.pb-relevant{background:rgba(180,50,26,0.04);}
  .cmp-table tr.pb-relevant td:first-child{border-left:2px solid var(--accent);padding-left:10px;}"""

# ── New profile builder HTML (replaces old 4-row builder) ────────────────────
NEW_PROFILE_HTML = """    <a href="/article/compare/index.html" class="hub-back">Compare hub</a>
    <h2>Who wins for your profile?</h2>
    <div class="profile-builder" id="profileBuilder">
      <div class="pb-row">
        <div class="pb-row-label">Age</div>
        <div class="pb-pills" data-pb="age">
          <button type="button" class="pb-pill" data-v="young">18&ndash;24</button>
          <button type="button" class="pb-pill" data-v="young2">25&ndash;34</button>
          <button type="button" class="pb-pill active" data-v="mid">35&ndash;54</button>
          <button type="button" class="pb-pill" data-v="senior">55+</button>
        </div>
      </div>
      <div class="pb-row">
        <div class="pb-row-label">Credit</div>
        <div class="pb-pills" data-pb="credit">
          <button type="button" class="pb-pill" data-v="excellent">Excellent</button>
          <button type="button" class="pb-pill active" data-v="good">Good</button>
          <button type="button" class="pb-pill" data-v="fair">Fair</button>
          <button type="button" class="pb-pill" data-v="poor">Poor</button>
        </div>
      </div>
      <div class="pb-row">
        <div class="pb-row-label">Home</div>
        <div class="pb-pills" data-pb="home">
          <button type="button" class="pb-pill active" data-v="rent">Rent</button>
          <button type="button" class="pb-pill" data-v="own">Own</button>
        </div>
      </div>
      <div class="pb-row">
        <div class="pb-row-label">Vehicles</div>
        <div class="pb-pills" data-pb="vehicles">
          <button type="button" class="pb-pill active" data-v="1">1</button>
          <button type="button" class="pb-pill" data-v="2">2+</button>
        </div>
      </div>
      <div class="pb-row">
        <div class="pb-row-label">Coverage</div>
        <div class="pb-pills" data-pb="coverage">
          <button type="button" class="pb-pill" data-v="minimum">Minimum</button>
          <button type="button" class="pb-pill active" data-v="standard">Standard</button>
          <button type="button" class="pb-pill" data-v="premium">Premium</button>
        </div>
      </div>
      <div class="pb-row">
        <div class="pb-row-label">Shopping</div>
        <div class="pb-pills" data-pb="shopping">
          <button type="button" class="pb-pill active" data-v="any">Any way</button>
          <button type="button" class="pb-pill" data-v="online">Online</button>
          <button type="button" class="pb-pill" data-v="agent">Agent</button>
        </div>
      </div>
      <div class="pb-row pb-row-checks">
        <div class="pb-row-label">Other</div>
        <div class="pb-checks">
          <label class="pb-check"><input type="checkbox" id="pbYoungDriver" /> Driver under 25 on policy</label>
          <label class="pb-check"><input type="checkbox" id="pbLapsed" /> Had a coverage gap</label>
          <label class="pb-check"><input type="checkbox" id="pbSuspended" /> Suspended / revoked license</label>
        </div>
      </div>
      <div class="pb-extra-row">
        <div class="pb-extra-group">
          <label class="pb-extra-label">ZIP code</label>
          <input type="text" class="pb-zip-input" id="pbZip" maxlength="5" inputmode="numeric" placeholder="12345" autocomplete="postal-code" />
        </div>
        <div class="pb-extra-group pb-carrier-group">
          <label class="pb-extra-label">Current carrier</label>
          <select class="pb-select" id="pbCarrier">
            <option value="">Current carrier (optional)</option>
            <option>State Farm</option><option>GEICO</option><option>Progressive</option><option>Allstate</option>
            <option>USAA</option><option>Liberty Mutual</option><option>Farmers</option><option>Travelers</option>
            <option>Nationwide</option><option>American Family</option><option>Erie</option>
            <option>Root Insurance</option><option>Safeco</option><option>The Hartford</option><option>Amica</option>
            <option>Other</option><option value="none">No insurance / lapsed</option>
          </select>
        </div>
      </div>
      <div class="pb-result" id="pbResult">
        <div class="pb-result-winner" id="pbWinner"></div>
        <div class="pb-result-detail" id="pbDetail"></div>
        <div id="pbShoppingNote" class="pb-shopping-note" style="display:none;"></div>
      </div>
      <div class="pb-actions">
        <a href="/" class="pb-cta" id="pbCta">Compare all carriers for your profile &rarr;</a>
        <a href="/article/compare/index.html" class="pb-cta pb-cta-alt">Return to Compare Hub &rarr;</a>
      </div>
    </div>"""

SHARED_SCRIPT = '<script src="/article/compare/compare-profile.js"></script>'


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # 1. Add new CSS before </style> (only if not already upgraded)
    if 'pb-row-checks' not in html:
        html = html.replace('\n</style>', NEW_CSS + '\n</style>', 1)

    # 2. Replace old profile builder HTML with new expanded form
    #    Pattern: from the hub-back link through end of profileBuilder div
    profile_html_pattern = re.compile(
        r'<a href="/article/compare/index\.html" class="hub-back">Compare hub</a>.*?</div>\s*(?=\s*<div class="(?:zip-embed|article-email)">)',
        re.DOTALL
    )
    if profile_html_pattern.search(html):
        html = profile_html_pattern.sub(NEW_PROFILE_HTML + '\n\n    ', html)

    # 3. Replace inline profile builder JS with shared script reference
    #    Identify by presence of pbWinner inside the script block
    if SHARED_SCRIPT not in html:
        lines = html.split('\n')
        start_i = None
        end_i = None
        in_target = False
        for i, line in enumerate(lines):
            if '<script>' in line and start_i is None:
                start_i = i
                in_target = False
            if start_i is not None and 'pbWinner' in line:
                in_target = True
            if '</script>' in line and start_i is not None:
                if in_target:
                    end_i = i
                    break
                else:
                    start_i = None  # reset, this wasn't the right script
        if start_i is not None and end_i is not None:
            lines[start_i:end_i + 1] = [SHARED_SCRIPT]
            html = '\n'.join(lines)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


files = sorted(glob.glob(os.path.join(COMPARE_DIR, "*.html")))
files = [f for f in files if not f.endswith('/index.html')]

patched = skipped = 0
for f in files:
    if patch_file(f):
        patched += 1
    else:
        skipped += 1
        print(f"SKIPPED: {os.path.basename(f)}")

print(f"\nDone: {patched} patched, {skipped} unchanged, {len(files)} total.")
