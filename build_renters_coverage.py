#!/usr/bin/env python3
# Build the renters coverage calculator: surgically swap the auto body, calculator
# script, and FAQ JSON-LD in renters/coverage.html for renters-specific content.
# Keeps the head/styles/nav/footer scaffolding. Preserves ZIP3_TO_STATE from the file.
import re, sys

PATH = "renters/coverage.html"
h = open(PATH, encoding="utf-8").read()

# ── pull ZIP3_TO_STATE straight from the file (already correct) ──
m = re.search(r"const ZIP3_TO_STATE = \{.*?\};", h, re.S)
ZIP3 = m.group(0)

# ── 1. BODY: page-header through cta-section ──────────────────────────
NEW_BODY = '''<div class="wrap-narrow">
  <div class="page-header">
    <div class="page-kicker"><a href="/renters/">← BoringRate Renters</a> &nbsp;·&nbsp; Coverage Guide</div>
    <h1 class="page-title">How much renters insurance do you actually need?</h1>
    <p class="page-dek">Renters insurance is cheap — the national average is about <strong>$168/yr</strong>. The real question is how much personal property and liability coverage to carry, and what to skip. Tell us a few things and we'll show you what to buy and roughly what it should cost.</p>
  </div>
</div>

<div class="profile-section">
  <div class="wrap-narrow">

    <div class="profile-widget">
      <div class="profile-widget-label">Your situation</div>

      <div class="slider-q">
        <div class="slider-q-header">
          <div class="slider-q-label">Value of your stuff</div>
          <div class="slider-q-value" id="propDisplay">$30,000</div>
        </div>
        <input type="range" id="propSlider" min="0" max="10" step="1" value="3" />
        <div class="slider-ticks"><span>$10k</span><span>$30k</span><span>$75k</span><span>$150k</span><span>$300k+</span></div>
      </div>

      <div class="slider-q">
        <div class="slider-q-header">
          <div class="slider-q-label">Assets to protect (net worth)</div>
          <div class="slider-q-value" id="assetsDisplay">$100,000</div>
        </div>
        <input type="range" id="assetsSlider" min="0" max="7" step="1" value="2" />
        <div class="slider-ticks"><span>&lt; $50k</span><span>$100k</span><span>$300k</span><span>$500k</span><span>$1M+</span></div>
      </div>

      <div class="zip-q">
        <div class="zip-q-header">
          <div class="zip-q-label">Your ZIP code</div>
          <div class="zip-state-badge" id="zipStateBadge"></div>
        </div>
        <div class="zip-input-row">
          <input type="text" id="zipInput" class="zip-field" maxlength="5" inputmode="numeric" placeholder="e.g. 90210" />
          <div class="zip-hint" id="zipHint">rates adjust by state</div>
        </div>
      </div>

      <div class="profile-pills-row">
        <div class="profile-pill-q">
          <div class="profile-pill-label">Deductible</div>
          <div class="pill-row">
            <button class="pill" data-q="deductible" data-v="250">$250</button>
            <button class="pill" data-q="deductible" data-v="500">$500</button>
            <button class="pill active" data-q="deductible" data-v="1000">$1,000</button>
          </div>
        </div>
        <div class="profile-pill-q">
          <div class="profile-pill-label">Bundle with auto?</div>
          <div class="pill-row">
            <button class="pill active" data-q="bundle" data-v="no">No</button>
            <button class="pill" data-q="bundle" data-v="yes">Yes</button>
          </div>
        </div>
        <div class="profile-pill-q">
          <div class="profile-pill-label">High-value items?</div>
          <div class="pill-row">
            <button class="pill active" data-q="valuables" data-v="no">No</button>
            <button class="pill" data-q="valuables" data-v="yes">Yes</button>
          </div>
        </div>
      </div>
    </div>

    <div class="summary-bar" id="summaryBar">
      <div class="summary-total">Est. annual premium: <strong id="summaryTotal">—</strong></div>
      <div id="summaryDelta"></div>
      <div class="summary-note">Directional estimates only — not a quote. Actual premiums vary by carrier, building, and claims history. <a href="/methodology.html">How we estimate →</a></div>
    </div>

    <div class="cov-cards" id="covCards"></div>

    <div class="bottom-cta" id="bottomCta">
      <div class="bottom-cta-label">Compare renters rates</div>
      <div class="bottom-cta-row">
        <div class="bottom-cta-text">
          <h3>See who's cheapest<br>for your coverage.</h3>
          <p>Carriers ranked by estimated renters premium for your state and the coverage you picked — carried over automatically.</p>
          <div class="bottom-cta-selections" id="ctaSelectionsSummary"></div>
          <div class="bottom-zip-row">
            <input type="text" id="bottomZipInput" class="bottom-zip-input" maxlength="5" inputmode="numeric" placeholder="ZIP" />
            <a href="/renters/" class="cta-btn" id="ctaBtn">Compare rates →</a>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>

<!-- ── Static coverage primer ── -->
<section class="guide-section">
  <div class="wrap-narrow">
    <div class="guide-head">
      <div class="section-num">§ Coverage primer</div>
      <h2 class="section-title">Every renters coverage, <em>actually explained.</em></h2>
    </div>

    <div class="coverage-type" id="guide-personal">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Personal Property (Coverage C)</h3>
        <span class="coverage-tag req">The core of the policy</span>
      </div>
      <div class="coverage-body">
        <p>This pays to replace <strong>your belongings</strong> — furniture, electronics, clothing, kitchenware — when they're stolen or destroyed by a covered peril (fire, theft, most water damage, windstorm). It follows you off-premises too: a laptop stolen from your car or a hotel is usually covered.</p>
        <p>Add it up faster than you'd think: a couch, a TV, a laptop, a phone, a bed, and a closet of clothes already clears $15–20k. Most renters under-insure here. <strong>Walk through each room and total the replacement cost</strong> — that number is your Coverage C.</p>
        <div class="callout"><p><strong>Set it to what it would cost to re-buy everything new</strong>, not what you paid or what it's worth used. That's only true if you carry replacement-cost coverage (below) — otherwise you're paid depreciated value.</p></div>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-liability">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Personal Liability (Coverage E)</h3>
        <span class="coverage-tag req">Bigger than most people realize</span>
      </div>
      <div class="coverage-body">
        <p>Liability covers <strong>you</strong> when someone is hurt in your unit or you damage someone else's property — a guest slips and breaks an arm, your dog bites someone, a kitchen fire spreads to the next apartment. It pays their bills <em>and</em> your legal defense.</p>
        <p>The standard limit is $100k, but the jump to $300k or $500k costs only a few dollars a year. Rule of thumb: <strong>carry at least as much as your net worth</strong> — a judgment above your limit comes out of your savings and future wages.</p>
        <div class="callout"><p>If you have real assets to protect, a $1–2M umbrella policy (~$150–300/yr) stacks on top and is the cheapest liability you can buy per dollar of protection.</p></div>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-lossofuse">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Loss of Use (Coverage D)</h3>
        <span class="coverage-tag">Included — don't skip it</span>
      </div>
      <div class="coverage-body">
        <p>If a covered loss makes your place unlivable, Loss of Use pays for <strong>hotels, restaurant meals above your normal grocery bill, and other extra living costs</strong> while you're displaced.</p>
        <p>It's bundled into nearly every policy at roughly 20–40% of your Coverage C, so there's usually nothing to buy — just confirm the limit is there. After a fire, this is the coverage that keeps you off a friend's couch for three months.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-medpay">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Medical Payments to Others (Coverage F)</h3>
        <span class="coverage-tag">Small limit, smooths small claims</span>
      </div>
      <div class="coverage-body">
        <p>This pays <strong>minor medical bills for guests hurt in your home</strong>, regardless of fault, without anyone having to file a liability claim. Think a friend who trips and needs stitches.</p>
        <p>Limits are small ($1k–$5k) and the cost is trivial. Bumping it to $5k is usually a few dollars and avoids turning a small injury into a liability dispute.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-replacementcost">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Replacement Cost vs. Actual Cash Value</h3>
        <span class="coverage-tag req">The most important checkbox</span>
      </div>
      <div class="coverage-body">
        <p><strong>Actual Cash Value (ACV)</strong> pays what your stuff is worth used — a 5-year-old TV gets you maybe $80. <strong>Replacement Cost (RCV)</strong> pays what it costs to buy new. The difference on a full apartment can be thousands.</p>
        <div class="callout"><p>RCV typically adds only ~10–15% to the premium and is almost always worth it. On a cheap policy that's $15–25/yr to turn a depreciated payout into a full one. <strong>Don't buy ACV to save $20.</strong></p></div>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-scheduled">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Scheduled Personal Property</h3>
        <span class="coverage-tag">Only if you own valuables</span>
      </div>
      <div class="coverage-body">
        <p>Standard policies <strong>cap certain categories</strong> — jewelry, watches, cameras, bikes, firearms, fine art — often at $1,000–$2,500 total, and theft of jewelry may be capped even lower. A scheduled endorsement (a "rider") insures a specific item for its appraised value, usually with no deductible.</p>
        <p>If you own an engagement ring, a nice camera kit, or a high-end bike, schedule it. If you don't, skip this entirely — it adds cost for protection you don't need.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

  </div>
</section>

<section class="cta-section">
  <div class="wrap-narrow">
    <div class="cta-inner">
      <div class="cta-text">
        <h3>Now see who's cheapest<br>for the coverage you need.</h3>
        <p>Enter your ZIP to rank renters carriers by likely premium — adjusted for your coverage level and state.</p>
        <p style="font-size:14px;margin-top:10px;">Want the full picture? See <a href="/renters/" style="color:var(--accent);text-decoration:none;border-bottom:1px solid currentColor;">renters rate comparison →</a></p>
      </div>
      <a href="/renters/" class="cta-btn">Compare rates →</a>
    </div>
  </div>
</section>
'''

start = h.index('<div class="wrap-narrow">\n  <div class="page-header">')
foot_at = h.index('<footer class="site-foot">', start)
h = h[:start] + NEW_BODY + "\n" + h[foot_at:]

# ── 2. STICKY total: relabel + renters link ──────────────────────────
old_sticky = '''<div class="sticky-total" id="stickyTotal">
  <div class="sticky-total-label">Est. median premium</div>
  <div class="sticky-total-amount" id="stickyAmount">—</div>
  <div class="sticky-total-delta" id="stickyDelta"></div>
  <a href="/" class="sticky-compare-link" id="stickyCompareLink">Compare rates →</a>
</div>'''
new_sticky = '''<div class="sticky-total" id="stickyTotal">
  <div class="sticky-total-label">Est. annual premium</div>
  <div class="sticky-total-amount" id="stickyAmount">—</div>
  <div class="sticky-total-delta" id="stickyDelta"></div>
  <a href="/renters/" class="sticky-compare-link" id="stickyCompareLink">Compare rates →</a>
</div>'''
assert old_sticky in h, "sticky block not found"
h = h.replace(old_sticky, new_sticky)

# ── 3. CALCULATOR SCRIPT ─────────────────────────────────────────────
NEW_SCRIPT = '''<script>
// ── Renters coverage calculator ──────────────────────────
const RENTERS_STATE_DATA = {
  "AL":{name:"Alabama",avg:202},"AK":{name:"Alaska",avg:149},"AZ":{name:"Arizona",avg:178},
  "AR":{name:"Arkansas",avg:194},"CA":{name:"California",avg:196},"CO":{name:"Colorado",avg:163},
  "CT":{name:"Connecticut",avg:157},"DC":{name:"Washington D.C.",avg:198},"DE":{name:"Delaware",avg:160},
  "FL":{name:"Florida",avg:258},"GA":{name:"Georgia",avg:222},"HI":{name:"Hawaii",avg:148},
  "ID":{name:"Idaho",avg:138},"IL":{name:"Illinois",avg:187},"IN":{name:"Indiana",avg:152},
  "IA":{name:"Iowa",avg:131},"KS":{name:"Kansas",avg:182},"KY":{name:"Kentucky",avg:168},
  "LA":{name:"Louisiana",avg:268},"ME":{name:"Maine",avg:127},"MD":{name:"Maryland",avg:178},
  "MA":{name:"Massachusetts",avg:185},"MI":{name:"Michigan",avg:153},"MN":{name:"Minnesota",avg:145},
  "MS":{name:"Mississippi",avg:248},"MO":{name:"Missouri",avg:192},"MT":{name:"Montana",avg:155},
  "NE":{name:"Nebraska",avg:156},"NV":{name:"Nevada",avg:202},"NH":{name:"New Hampshire",avg:127},
  "NJ":{name:"New Jersey",avg:162},"NM":{name:"New Mexico",avg:185},"NY":{name:"New York",avg:198},
  "NC":{name:"North Carolina",avg:188},"ND":{name:"North Dakota",avg:133},"OH":{name:"Ohio",avg:162},
  "OK":{name:"Oklahoma",avg:212},"OR":{name:"Oregon",avg:158},"PA":{name:"Pennsylvania",avg:162},
  "RI":{name:"Rhode Island",avg:168},"SC":{name:"South Carolina",avg:204},"SD":{name:"South Dakota",avg:138},
  "TN":{name:"Tennessee",avg:192},"TX":{name:"Texas",avg:238},"UT":{name:"Utah",avg:142},
  "VT":{name:"Vermont",avg:134},"VA":{name:"Virginia",avg:176},"WA":{name:"Washington",avg:164},
  "WV":{name:"West Virginia",avg:152},"WI":{name:"Wisconsin",avg:142},"WY":{name:"Wyoming",avg:148}
};
const NATIONAL_AVG = 168;

__ZIP3__

// ── Steps & config ──
const PROP_STEPS   = [10000,15000,20000,30000,40000,50000,75000,100000,150000,200000,300000];
const ASSET_STEPS  = [25000,50000,100000,200000,300000,500000,750000,1000000];
const LIAB_OPTS    = [100000,300000,500000];
const MEDPAY_OPTS  = [1000,5000];
const DED_FACTOR   = {250:1.15, 500:1.05, 1000:0.93};

const profile = {
  property: 30000, assets: 100000, deductible: 1000,
  bundle: false, valuables: false,
  code: null, stateName: null, stateAvg: NATIONAL_AVG
};
// selections (user-adjustable in cards)
const sels = { liability: 0, medpay: 1, rcv: true, scheduled: false };

function fmt(n){ return '$' + Math.round(n).toLocaleString(); }
function stateFromZip(z){
  if(!/^\\d/.test(z)) return null;
  const p3 = z.slice(0,3);
  return ZIP3_TO_STATE[p3] || ZIP3_TO_STATE[('00'+z).slice(0,3)] || null;
}

// ── Recommendations ──
function computeRecs(){
  let liab = 0;
  if(profile.assets > 300000) liab = 2;
  else if(profile.assets > 100000) liab = 1;
  else liab = 0;
  return { liability: liab, medpay: 1, rcv: true, scheduled: profile.valuables };
}
function applyRecs(){
  const r = computeRecs();
  sels.liability = r.liability; sels.medpay = r.medpay;
  sels.rcv = r.rcv; sels.scheduled = r.scheduled;
}

// ── Premium model (component costs) ──
function components(){
  const sm = profile.stateAvg / NATIONAL_AVG;
  const propFactor = profile.property / 30000;
  const ded = DED_FACTOR[profile.deductible] || 1.0;
  const rcMult = sels.rcv ? 1.10 : 0.92;
  const bundleMult = profile.bundle ? 0.85 : 1.0;
  // base policy = personal property + loss of use (bundled)
  let base = profile.stateAvg * propFactor * ded * rcMult * bundleMult;
  base = Math.max(78, base);
  const liabAdd = [0, 6, 15][sels.liability] * sm;
  const medpayAdd = [0, 6][sels.medpay] * sm;
  const schedAdd = sels.scheduled ? 42 : 0;
  return {
    base: base, liab: liabAdd, medpay: medpayAdd, sched: schedAdd,
    total: Math.round(base + liabAdd + medpayAdd + schedAdd)
  };
}
function totalEstimate(){ return components().total; }

// ── Cards ──
const CARDS = ['personal','liability','lossOfUse','medpay','replacementCost','scheduled'];
const META = {
  personal:        { name:'Personal Property (Coverage C)', tag:'Replace everything you own', guide:'guide-personal' },
  liability:       { name:'Personal Liability (Coverage E)', tag:'Covers injuries & damage you cause', guide:'guide-liability' },
  lossOfUse:       { name:'Loss of Use (Coverage D)', tag:'Hotels & extra costs if displaced', guide:'guide-lossofuse' },
  medpay:          { name:'Medical Payments (Coverage F)', tag:"Guests' minor medical bills", guide:'guide-medpay' },
  replacementCost: { name:'Replacement Cost', tag:'Paid new, not depreciated', guide:'guide-replacementcost' },
  scheduled:       { name:'Scheduled Items', tag:'Jewelry, cameras, bikes, art', guide:'guide-scheduled' }
};

function deltaBadge(kind, text){
  return '<div class="delta-display"><span class="delta-badge ' + kind + '">' + text + '</span></div>';
}
function pillBtns(cov, opts, labels, selIdx, recIdx){
  return '<div class="pill-row" style="margin-top:12px;">' + opts.map(function(o,i){
    const cls = 'pill' + (i===selIdx ? ' active' : '');
    const rec = i===recIdx ? ' <span style="font-size:10px;opacity:.7;">★</span>' : '';
    return '<button class="' + cls + '" data-cov="' + cov + '" data-i="' + i + '">' + labels[i] + rec + '</button>';
  }).join('') + '</div>';
}
function toggleRow(cov, on, label){
  return '<div class="cov-toggle-row"><label class="cov-toggle" data-tgl="' + cov + '">'
    + '<span class="cov-toggle-track' + (on?' on':'') + '"><span class="cov-toggle-thumb"></span></span>'
    + '<span class="cov-toggle-label">' + label + '</span></label></div>';
}
function costLine(n){
  if(n <= 0) return '<div class="cov-cost">Included in your base policy</div>';
  return '<div class="cov-cost">≈ ' + fmt(n) + '/yr of your premium</div>';
}

function renderCards(){
  const c = components();
  const recs = computeRecs();
  const lossOfUse = Math.round(profile.property * 0.30);
  let html = '';

  // Personal Property — driven by slider
  html += card('personal',
    deltaBadge('zero','Set to ' + fmt(profile.property)),
    '<div class="cov-card-desc">Cover what it would cost to <strong>re-buy everything new</strong>. Based on your slider, we suggest <strong>' + fmt(profile.property) + '</strong> of personal property. Adjust the "value of your stuff" slider above to change it.</div>'
    + costLine(c.base));

  // Liability — options
  html += card('liability',
    deltaBadge(sels.liability >= recs.liability ? 'minus' : 'plus',
      sels.liability >= recs.liability ? 'Covered' : 'Below rec'),
    '<div class="cov-card-desc">For your assets (' + fmt(profile.assets) + '), carry at least <strong>' + fmt(LIAB_OPTS[recs.liability]) + '</strong>. The jump in limits costs only a few dollars a year.</div>'
    + pillBtns('liability', LIAB_OPTS, LIAB_OPTS.map(function(v){return fmt(v);}), sels.liability, recs.liability)
    + costLine(c.liab));

  // Loss of Use — info
  html += card('lossOfUse',
    deltaBadge('zero','Included'),
    '<div class="cov-card-desc">Bundled at roughly 20–40% of your personal property — about <strong>' + fmt(lossOfUse) + '</strong> here. Confirm the limit is on your policy; there\\'s usually nothing extra to buy.</div>'
    + costLine(0));

  // Medical Payments — options
  html += card('medpay',
    deltaBadge(sels.medpay >= recs.medpay ? 'minus' : 'plus',
      sels.medpay >= recs.medpay ? 'Covered' : 'Low'),
    '<div class="cov-card-desc">Pays guests\\' minor medical bills without a liability claim. We suggest <strong>' + fmt(MEDPAY_OPTS[recs.medpay]) + '</strong> — it\\'s only a few dollars.</div>'
    + pillBtns('medpay', MEDPAY_OPTS, MEDPAY_OPTS.map(function(v){return fmt(v);}), sels.medpay, recs.medpay)
    + costLine(c.medpay));

  // Replacement Cost — toggle
  html += card('replacementCost',
    deltaBadge(sels.rcv ? 'minus' : 'plus', sels.rcv ? 'On (recommended)' : 'Off (ACV)'),
    '<div class="cov-card-desc">Get paid what it costs to <strong>buy new</strong>, not the depreciated used value. Adds ~10–15% — almost always worth it.</div>'
    + toggleRow('rcv', sels.rcv, sels.rcv ? 'Replacement cost — ON' : 'Actual cash value (cheaper, pays less)'));

  // Scheduled — toggle
  html += card('scheduled',
    deltaBadge(sels.scheduled ? 'minus' : 'zero', sels.scheduled ? 'Added' : (recs.scheduled ? 'Recommended' : 'Skip')),
    '<div class="cov-card-desc">Standard policies cap jewelry, cameras, bikes, and art. Add a rider only if you own something valuable. ' + (recs.scheduled ? 'You said you have high-value items — schedule them.' : 'You can skip this if you don\\'t.') + '</div>'
    + toggleRow('scheduled', sels.scheduled, sels.scheduled ? 'Scheduled items — ON' : 'Add scheduled items')
    + costLine(c.sched));

  document.getElementById('covCards').innerHTML = html;
}

function card(key, badge, body){
  const m = META[key];
  return '<div class="cov-card">'
    + '<div class="cov-card-top"><div>'
    + '<div class="cov-card-name">' + m.name + '</div></div>'
    + badge + '</div>'
    + '<div class="cov-card-tagline">' + m.tag + '</div>'
    + body
    + '<a href="#' + m.guide + '" class="cov-full-guide">Read more →</a>'
    + '</div>';
}

// ── Summary, sticky, CTA ──
function renderSummary(){
  const total = totalEstimate();
  document.getElementById('summaryTotal').textContent = fmt(total) + '/yr';
  const d = total - profile.stateAvg;
  const dEl = document.getElementById('summaryDelta');
  const label = profile.code ? profile.stateName : 'national';
  if(Math.abs(d) < 6){
    dEl.innerHTML = '<span style="color:var(--ink-mute);font-size:13px;">about the ' + label + ' average (' + fmt(profile.stateAvg) + '/yr)</span>';
  } else if(d < 0){
    dEl.innerHTML = '<span style="color:var(--good);font-size:13px;font-weight:600;">' + fmt(Math.abs(d)) + '/yr below the ' + label + ' average</span>';
  } else {
    dEl.innerHTML = '<span style="color:var(--accent);font-size:13px;font-weight:600;">' + fmt(d) + '/yr above the ' + label + ' average</span>';
  }
  // sticky
  document.getElementById('stickyAmount').textContent = fmt(total) + '/yr';
  const sd = document.getElementById('stickyDelta');
  if(profile.code){ sd.textContent = profile.stateName; }
  else { sd.textContent = 'national avg'; }
  updateCta();
}

function updateCta(){
  const parts = [];
  parts.push(fmt(profile.property) + ' property');
  parts.push(fmt(LIAB_OPTS[sels.liability]) + ' liability');
  parts.push(sels.rcv ? 'replacement cost' : 'actual cash value');
  if(sels.scheduled) parts.push('scheduled items');
  document.getElementById('ctaSelectionsSummary').textContent = 'Carrying over: ' + parts.join(' · ');
  refreshCtaLink();
}
function refreshCtaLink(){
  const zip = (document.getElementById('zipInput').value || '').replace(/\\D/g,'').slice(0,5);
  const q = zip.length === 5 ? ('?zip=' + zip) : '';
  ['ctaBtn','stickyCompareLink'].forEach(function(id){
    const el = document.getElementById(id); if(el) el.href = '/renters/' + q;
  });
}

// ── ZIP handling ──
function setZip(z){
  z = (z||'').replace(/\\D/g,'').slice(0,5);
  const badge = document.getElementById('zipStateBadge');
  const code = z.length >= 3 ? stateFromZip(z) : null;
  if(code && RENTERS_STATE_DATA[code]){
    profile.code = code;
    profile.stateName = RENTERS_STATE_DATA[code].name;
    profile.stateAvg = RENTERS_STATE_DATA[code].avg;
    badge.textContent = profile.stateName + ' · avg ' + fmt(profile.stateAvg) + '/yr';
    badge.style.display = '';
  } else {
    profile.code = null; profile.stateName = null; profile.stateAvg = NATIONAL_AVG;
    badge.textContent = '';
    badge.style.display = 'none';
  }
  refreshCtaLink();
  renderAll();
}

function renderAll(){ renderCards(); renderSummary(); }

// ── Events ──
function initEvents(){
  const propSlider = document.getElementById('propSlider');
  propSlider.addEventListener('input', function(){
    profile.property = PROP_STEPS[+this.value];
    document.getElementById('propDisplay').textContent = fmt(profile.property);
    renderAll();
  });
  const assetsSlider = document.getElementById('assetsSlider');
  assetsSlider.addEventListener('input', function(){
    profile.assets = ASSET_STEPS[+this.value];
    const lbl = (+this.value === 0) ? '< $50,000' : (profile.assets >= 1000000 ? '$1,000,000+' : fmt(profile.assets));
    document.getElementById('assetsDisplay').textContent = lbl;
    applyRecs();
    renderAll();
  });

  document.getElementById('zipInput').addEventListener('input', function(){
    this.value = this.value.replace(/\\D/g,'').slice(0,5);
    setZip(this.value);
  });
  const bz = document.getElementById('bottomZipInput');
  if(bz) bz.addEventListener('input', function(){
    this.value = this.value.replace(/\\D/g,'').slice(0,5);
    document.getElementById('zipInput').value = this.value;
    setZip(this.value);
  });

  // profile pills
  document.querySelectorAll('.profile-pills-row .pill').forEach(function(btn){
    btn.addEventListener('click', function(){
      const q = this.dataset.q, v = this.dataset.v;
      this.parentElement.querySelectorAll('.pill').forEach(function(p){ p.classList.remove('active'); });
      this.classList.add('active');
      if(q === 'deductible') profile.deductible = +v;
      else if(q === 'bundle') profile.bundle = (v === 'yes');
      else if(q === 'valuables'){ profile.valuables = (v === 'yes'); applyRecs(); }
      renderAll();
    });
  });

  // card option pills + toggles (delegated — cards re-render)
  document.getElementById('covCards').addEventListener('click', function(e){
    const pill = e.target.closest('.pill[data-cov]');
    if(pill){ sels[pill.dataset.cov] = +pill.dataset.i; renderAll(); return; }
    const tgl = e.target.closest('[data-tgl]');
    if(tgl){ const k = tgl.dataset.tgl; sels[k] = !sels[k]; renderAll(); return; }
  });
}

// ── Init ──
(function init(){
  applyRecs();
  initEvents();
  const params = new URLSearchParams(location.search);
  const z = params.get('zip');
  if(z && /^\\d{3,5}$/.test(z)){
    document.getElementById('zipInput').value = z.slice(0,5);
    setZip(z);
  } else {
    renderAll();
  }
})();
</script>'''
NEW_SCRIPT = NEW_SCRIPT.replace("__ZIP3__", ZIP3)

# replace the old calculator script
s_start = h.index('<script>\n// ── State data')
s_end = h.index('</script>', s_start) + len('</script>')
h = h[:s_start] + NEW_SCRIPT + h[s_end:]

# ── 4. FAQ JSON-LD → renters ─────────────────────────────────────────
NEW_FAQ = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much renters insurance do I need?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Set your personal property (Coverage C) to what it would cost to re-buy everything you own new — walk room by room and total it; most renters land between $20,000 and $50,000. Carry personal liability (Coverage E) of at least as much as your net worth, with $100,000 the practical minimum and $300,000 only a few dollars more. Add replacement-cost coverage so you're paid for new items rather than depreciated value. The national average renters policy is about $168 per year."
      }
    },
    {
      "@type": "Question",
      "name": "What is replacement cost vs. actual cash value on renters insurance?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Actual cash value (ACV) pays what your belongings are worth used after depreciation — a five-year-old TV might be valued at $80. Replacement cost value (RCV) pays what it costs to buy the item new. RCV typically adds only about 10–15% to the premium and is almost always worth it; do not choose ACV to save $20 a year."
      }
    },
    {
      "@type": "Question",
      "name": "Does renters insurance cover jewelry and other valuables?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Standard renters policies cap categories like jewelry, watches, cameras, bicycles, firearms, and fine art — often at $1,000 to $2,500 total, and theft of jewelry may be capped lower. To fully cover a valuable item, add a scheduled personal property endorsement (a rider) that insures it for its appraised value, usually with no deductible. If you don't own high-value items, you can skip this."
      }
    },
    {
      "@type": "Question",
      "name": "How much does renters insurance cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The national average is roughly $168 per year, or about $14 a month, but it ranges from around $127 in low-cost states to over $250 in Florida and Louisiana. Premiums are driven mainly by how much personal property you insure, your deductible, whether you carry replacement-cost coverage, and your state. Bundling renters with an auto policy typically cuts the renters premium by 10–15%."
      }
    }
  ]
}
</script>'''
f_start = h.index('<script type="application/ld+json">')
f_end = h.index('</script>', f_start) + len('</script>')
h = h[:f_start] + NEW_FAQ + h[f_end:]

open(PATH, "w", encoding="utf-8").write(h)
print("renters/coverage.html rebuilt OK")
