#!/usr/bin/env python3
"""Patch all 66 carrier compare pages:
1. Make 'Carrier Compare' breadcrumb a link back to the compare hub
2. Replace static profile-grid with dynamic JS profile builder
3. Add profile builder CSS + JS
"""
import os, re, glob

COMPARE_DIR = "/home/knighttyler/boringrate/article/compare"

# New CSS block to inject before </style>
NEW_CSS = """
  .hub-back{display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-size:11px;letter-spacing:0.07em;text-transform:uppercase;color:var(--accent);text-decoration:none;margin-bottom:20px;}
  .hub-back:hover{color:var(--ink);}
  .hub-back::before{content:"←";margin-right:2px;}
  .profile-builder{border:1px solid var(--rule);padding:22px 24px;max-width:660px;margin:0 0 36px;background:var(--paper-deep);}
  .pb-row{display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap;}
  .pb-row-label{font-family:var(--mono);font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink-mute);min-width:72px;flex-shrink:0;}
  .pb-pills{display:flex;gap:6px;flex-wrap:wrap;}
  .pb-pill{font-family:var(--mono);font-size:11px;letter-spacing:0.05em;padding:5px 12px;border:1px solid var(--rule);background:var(--paper);color:var(--ink-soft);cursor:pointer;transition:all 120ms;border-radius:2px;}
  .pb-pill.active{background:var(--ink);color:var(--paper);border-color:var(--ink);}
  .pb-result{margin-top:18px;padding-top:18px;border-top:1px solid var(--rule);}
  .pb-result-winner{font-family:var(--serif);font-size:22px;font-weight:600;letter-spacing:-0.02em;margin-bottom:4px;}
  .pb-result-detail{font-family:var(--mono);font-size:11px;color:var(--ink-mute);letter-spacing:0.04em;line-height:1.6;margin-bottom:16px;}
  .pb-cta{display:inline-block;font-family:var(--sans);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:10px 20px;background:var(--ink);color:var(--paper);text-decoration:none;transition:background 120ms;}
  .pb-cta:hover{background:var(--accent);}"""

# New profile builder HTML (replaces h2 + profile-grid)
NEW_PROFILE_HTML = """    <a href="/article/compare/index.html" class="hub-back">Compare hub</a>
    <h2>Who wins for your profile?</h2>
    <div class="profile-builder" id="profileBuilder">
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
        <div class="pb-row-label">Age</div>
        <div class="pb-pills" data-pb="age">
          <button type="button" class="pb-pill" data-v="young">18&ndash;24</button>
          <button type="button" class="pb-pill active" data-v="mid">25&ndash;54</button>
          <button type="button" class="pb-pill" data-v="senior">55+</button>
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
        <div class="pb-row-label">Lapsed?</div>
        <div class="pb-pills" data-pb="lapse">
          <button type="button" class="pb-pill active" data-v="no">No gap</button>
          <button type="button" class="pb-pill" data-v="yes">Had a gap</button>
        </div>
      </div>
      <div class="pb-result" id="pbResult">
        <div class="pb-result-winner" id="pbWinner"></div>
        <div class="pb-result-detail" id="pbDetail"></div>
        <a href="/" class="pb-cta" id="pbCta">View all carrier rates &rarr;</a>
      </div>
    </div>"""

# Profile builder JS to inject before </body>
PROFILE_JS = """<script>
(function(){
  var tbl=document.querySelector('.cmp-table');
  if(!tbl)return;
  var ths=tbl.querySelectorAll('thead th');
  var cA=ths[1]?ths[1].textContent.trim():'';
  var cB=ths[2]?ths[2].textContent.trim():'';
  function num(s){var m=(s||'').match(/[\d,]+/);return m?parseInt(m[0].replace(',',''),10):null;}
  function pct(s){var m=(s||'').match(/([+-]?\d+)%/);return m?parseInt(m[1],10)/100:null;}
  var d={a:{},b:{}};
  tbl.querySelectorAll('tbody tr').forEach(function(r){
    var c=r.querySelectorAll('td');if(c.length<3)return;
    var lbl=c[0].textContent.toLowerCase();
    var vA=c[1].textContent,vB=c[2].textContent;
    if(lbl.includes('avg annual')){d.a.base=num(vA);d.b.base=num(vB);}
    else if(lbl.includes('excellent')&&lbl.includes('credit')){d.a.cExc=pct(vA);d.b.cExc=pct(vB);}
    else if((lbl.includes('fair')||lbl.includes('poor'))&&lbl.includes('credit')){if(d.a.cFair==null){d.a.cFair=pct(vA);d.b.cFair=pct(vB);}}
    else if(lbl.includes('18')||lbl.includes('young')){d.a.young=pct(vA);d.b.young=pct(vB);}
    else if(lbl.includes('55')||lbl.includes('senior')){d.a.senior=pct(vA);d.b.senior=pct(vB);}
    else if(lbl.includes('homeowner')&&!lbl.includes('multi')&&!lbl.includes('bundle')){if(d.a.home==null){d.a.home=pct(vA);d.b.home=pct(vB);}}
    else if(lbl.includes('lapse')||lbl.includes('gap')){d.a.lapse=pct(vA);d.b.lapse=pct(vB);}
  });
  function calc(carrier,credit,age,home,lapse){
    var r=carrier.base;if(!r)return null;
    if(credit==='excellent'&&carrier.cExc!=null)r*=(1+carrier.cExc);
    else if(credit==='fair'&&carrier.cFair!=null)r*=(1+carrier.cFair);
    else if(credit==='poor'&&carrier.cFair!=null)r*=(1+carrier.cFair*1.5);
    if(age==='young'&&carrier.young!=null)r*=(1+carrier.young);
    else if(age==='senior'&&carrier.senior!=null)r*=(1+carrier.senior);
    if(home==='own'&&carrier.home!=null)r*=(1+carrier.home);
    if(lapse==='yes'&&carrier.lapse!=null)r*=(1+carrier.lapse);
    return Math.round(r);
  }
  function sel(name){var el=document.querySelector('[data-pb="'+name+'"] .pb-pill.active');return el?el.dataset.v:null;}
  function update(){
    var credit=sel('credit')||'good',age=sel('age')||'mid',home=sel('home')||'rent',lapse=sel('lapse')||'no';
    var rA=calc(d.a,credit,age,home,lapse),rB=calc(d.b,credit,age,home,lapse);
    if(!rA||!rB)return;
    var winner,loser,wRate,lRate;
    if(rA<=rB){winner=cA;loser=cB;wRate=rA;lRate=rB;}else{winner=cB;loser=cA;wRate=rB;lRate=rA;}
    var save=lRate-wRate;
    document.getElementById('pbWinner').textContent=winner+' wins for your profile';
    document.getElementById('pbDetail').textContent=
      '~$'+wRate.toLocaleString()+'/yr vs ~$'+lRate.toLocaleString()+'/yr — saves ~$'+save+'/yr vs '+loser;
    var cta=document.getElementById('pbCta');
    if(cta){try{var z=JSON.parse(localStorage.getItem('br_profile')||'{}').zip;cta.href=z?'/?zip='+z:'/';}catch(e){}}
  }
  document.querySelectorAll('[data-pb]').forEach(function(group){
    group.querySelectorAll('.pb-pill').forEach(function(btn){
      btn.addEventListener('click',function(){
        group.querySelectorAll('.pb-pill').forEach(function(b){b.classList.remove('active');});
        btn.classList.add('active');
        update();
      });
    });
  });
  update();
})();
</script>"""


def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # 1. Add hub link CSS before </style>
    if 'hub-back' not in html:
        html = html.replace('\n</style>', NEW_CSS + '\n</style>', 1)

    # 2. Make "Carrier Compare" in breadcrumb a link (if not already)
    html = re.sub(
        r'Carrier Compare &nbsp;&middot;&nbsp; 3 min read',
        '<a href="/article/compare/index.html">Carrier Compare</a> &nbsp;&middot;&nbsp; 3 min read',
        html
    )

    # 3. Replace the old profile section (h2 + profile-grid) with new builder
    # Pattern: from the h2 through the end of .profile-grid div, up to the next sibling
    # We'll replace everything between the h2 and the <div class="zip-embed"> tag
    profile_pattern = re.compile(
        r'<h2>Who wins by driver profile</h2>\s*<div class="profile-grid">.*?</div>\s*(?=<div class="zip-embed"|<div class="article-email">)',
        re.DOTALL
    )
    if profile_pattern.search(html):
        html = profile_pattern.sub(NEW_PROFILE_HTML + '\n\n    ', html)

    # 4. Add profile JS before </body> (only if not already present)
    if 'pbWinner' not in html:
        html = html.replace('</body>', PROFILE_JS + '\n</body>', 1)

    if html != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


files = sorted(glob.glob(os.path.join(COMPARE_DIR, "*.html")))
files = [f for f in files if not f.endswith('/index.html')]

patched = 0
skipped = 0
for f in files:
    result = patch_file(f)
    if result:
        patched += 1
    else:
        skipped += 1
        print(f"SKIPPED (no change): {os.path.basename(f)}")

print(f"\nDone: {patched} patched, {skipped} skipped out of {len(files)} files.")
