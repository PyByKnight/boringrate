#!/usr/bin/env python3
# Build the HOME coverage calculator at home/coverage.html by adapting the clean
# renters/coverage.html scaffold (same design system + shared nav). Swaps head
# meta, body, calculator script, and FAQ JSON-LD for homeowners content.
# Preserves ZIP3_TO_STATE from the source.
import re

SRC = "renters/coverage.html"
OUT = "home/coverage.html"
h = open(SRC, encoding="utf-8").read()

ZIP3 = re.search(r"const ZIP3_TO_STATE = \{.*?\};", h, re.S).group(0)

# ── head meta: renters -> home ──
h = h.replace("https://boringrate.com/renters/coverage.html", "https://boringrate.com/home/coverage.html")
h = h.replace("How much renters insurance do you actually need? — BoringRate",
              "How much homeowners insurance do you actually need? — BoringRate")
h = h.replace("Estimate how much personal property and liability coverage you need as a renter — and what it should cost. Know what to buy and what to skip.",
              "Estimate how much dwelling, personal property, and liability coverage you need as a homeowner — and what it should cost. Know what to buy and what to skip.")

# ── BODY: page-header through cta-section ──
NEW_BODY = '''<div class="wrap-narrow">
  <div class="page-header">
    <div class="page-kicker"><a href="/home/">← BoringRate Home</a> &nbsp;·&nbsp; Coverage Guide</div>
    <h1 class="page-title">How much homeowners insurance do you actually need?</h1>
    <p class="page-dek">The single most important number is your <strong>dwelling coverage (Coverage A)</strong> — it should equal what it costs to <em>rebuild</em> your home, not its market price or what you paid. Tell us a few things and we'll show you the right level for every coverage, what to add, and roughly what it should cost.</p>
  </div>
</div>

<div class="profile-section">
  <div class="wrap-narrow">

    <div class="profile-widget">
      <div class="profile-widget-label">Your home</div>

      <div class="slider-q">
        <div class="slider-q-header">
          <div class="slider-q-label">Dwelling rebuild cost (Coverage A)</div>
          <div class="slider-q-value" id="dwellDisplay">$300,000</div>
        </div>
        <input type="range" id="dwellSlider" min="0" max="8" step="1" value="3" />
        <div class="slider-ticks"><span>$150k</span><span>$300k</span><span>$500k</span><span>$1M</span><span>$1.5M+</span></div>
      </div>

      <div class="slider-q">
        <div class="slider-q-header">
          <div class="slider-q-label">Assets to protect (net worth)</div>
          <div class="slider-q-value" id="assetsDisplay">$200,000</div>
        </div>
        <input type="range" id="assetsSlider" min="0" max="7" step="1" value="3" />
        <div class="slider-ticks"><span>&lt; $50k</span><span>$100k</span><span>$300k</span><span>$500k</span><span>$1M+</span></div>
      </div>

      <div class="zip-q">
        <div class="zip-q-header">
          <div class="zip-q-label">Your ZIP code</div>
          <div class="zip-state-badge" id="zipStateBadge"></div>
        </div>
        <div class="zip-input-row">
          <input type="text" id="zipInput" class="zip-field" maxlength="5" inputmode="numeric" placeholder="e.g. 33101" />
          <div class="zip-hint" id="zipHint">rates adjust by state</div>
        </div>
      </div>

      <div class="profile-pills-row">
        <div class="profile-pill-q">
          <div class="profile-pill-label">Deductible</div>
          <div class="pill-row">
            <button class="pill active" data-q="deductible" data-v="1000">$1,000</button>
            <button class="pill" data-q="deductible" data-v="2500">$2,500</button>
            <button class="pill" data-q="deductible" data-v="5000">$5,000</button>
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
      <div class="summary-note">Directional estimates only — not a quote. Actual premiums vary by carrier, home age, roof, and claims history. <a href="/methodology.html">How we estimate →</a></div>
    </div>

    <div class="cov-cards" id="covCards"></div>

    <div class="bottom-cta" id="bottomCta">
      <div class="bottom-cta-label">Compare home insurance rates</div>
      <div class="bottom-cta-row">
        <div class="bottom-cta-text">
          <h3>See who's cheapest<br>for your coverage.</h3>
          <p>Carriers ranked by estimated homeowners premium for your state and the coverage you picked — carried over automatically.</p>
          <div class="bottom-cta-selections" id="ctaSelectionsSummary"></div>
          <div class="bottom-zip-row">
            <input type="text" id="bottomZipInput" class="bottom-zip-input" maxlength="5" inputmode="numeric" placeholder="ZIP" />
            <a href="/home/" class="cta-btn" id="ctaBtn">Compare rates →</a>
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
      <h2 class="section-title">Every homeowners coverage, <em>actually explained.</em></h2>
    </div>

    <div class="coverage-type" id="guide-dwelling">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Dwelling (Coverage A)</h3>
        <span class="coverage-tag req">The number that matters most</span>
      </div>
      <div class="coverage-body">
        <p>This pays to <strong>rebuild your home</strong> after a covered loss — structure, built-ins, and attached features. It should equal your <strong>rebuild cost</strong>, which is what a contractor would charge to reconstruct the house today. That's <em>not</em> the market price (which includes land) and not what you paid.</p>
        <p>In hot markets rebuild cost is often well below market value; after a construction-cost spike it can be above it. <strong>Under-insuring here is the most common and most expensive mistake.</strong> Many policies also enforce an 80% rule — insure for less than 80% of rebuild cost and they pro-rate even partial claims.</p>
        <div class="callout"><p><strong>Ask your insurer to run a replacement-cost estimate</strong> (most do it free) and revisit it after any renovation or a few years of inflation.</p></div>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-otherstructures">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Other Structures (Coverage B)</h3>
        <span class="coverage-tag">Usually 10% of dwelling</span>
      </div>
      <div class="coverage-body">
        <p>Covers structures <strong>not attached to the house</strong> — a detached garage, shed, fence, deck, or pool. It defaults to 10% of your Coverage A and most homeowners never touch it.</p>
        <p>Bump it up only if you have something substantial detached: a large workshop, a guest house, or extensive fencing. Skip the increase if you don't.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-personal">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Personal Property (Coverage C)</h3>
        <span class="coverage-tag req">Buy replacement cost, not ACV</span>
      </div>
      <div class="coverage-body">
        <p>Covers your <strong>belongings</strong> — furniture, electronics, clothing, appliances. It defaults to 50% of Coverage A, which is plenty for most homes; do a quick room-by-room total to sanity-check it.</p>
        <div class="callout"><p><strong>Actual Cash Value</strong> pays depreciated value (a 5-year-old TV gets you $80). <strong>Replacement Cost</strong> pays to buy new. The upgrade adds only a few percent and is almost always worth it — don't skip it to save a little.</p></div>
        <p>Certain categories — jewelry, watches, cameras, firearms, fine art — are capped (often $1,000–$2,500). Schedule them separately if you own anything valuable.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-lossofuse">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Loss of Use (Coverage D)</h3>
        <span class="coverage-tag">Included — confirm the limit</span>
      </div>
      <div class="coverage-body">
        <p>If a covered loss makes your home unlivable, this pays for <strong>hotels, meals, and other extra living costs</strong> while you're displaced — typically up to 20–30% of Coverage A. After a fire, this is what keeps a months-long rebuild from draining your savings.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-liability">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Personal Liability (Coverage E)</h3>
        <span class="coverage-tag req">Carry at least your net worth</span>
      </div>
      <div class="coverage-body">
        <p>Covers <strong>you</strong> when someone is injured on your property or you damage someone else's — a guest's fall, a dog bite, a tree that hits a neighbor's car. It pays their costs and your legal defense.</p>
        <p>The standard limit is $100k, but $300k–$500k costs only a little more. Rule of thumb: carry <strong>at least as much as your net worth</strong>. With real assets, add a $1–2M umbrella (~$150–300/yr) on top — the cheapest liability per dollar you can buy.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-medpay">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Medical Payments (Coverage F)</h3>
        <span class="coverage-tag">Small limit, smooths small claims</span>
      </div>
      <div class="coverage-body">
        <p>Pays <strong>minor medical bills for guests hurt on your property</strong>, regardless of fault, without anyone filing a liability claim. Limits are small ($1k–$5k) and the cost is trivial — $5k is the sensible default.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-waterbackup">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Water Backup Endorsement</h3>
        <span class="coverage-tag">Cheap, commonly needed</span>
      </div>
      <div class="coverage-body">
        <p>A standard policy <strong>does not cover</strong> water that backs up through sewers or drains, or a failed sump pump — a common and messy basement claim. This endorsement adds it back, usually for $50–$100/yr.</p>
        <div class="callout"><p>If you have a finished basement or a sump pump, this is almost always worth adding.</p></div>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-scheduled">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Scheduled Personal Property</h3>
        <span class="coverage-tag">Only if you own valuables</span>
      </div>
      <div class="coverage-body">
        <p>Insures a <strong>specific high-value item</strong> — an engagement ring, a camera kit, a watch, fine art — for its appraised value, usually with no deductible and broader coverage than the capped base limit. Add it only if you own something worth scheduling; skip it otherwise.</p>
      </div>
      <a href="#covCards" class="guide-back-link">↑ Back to selection</a>
    </div>

    <div class="coverage-type" id="guide-flood">
      <div class="coverage-type-header">
        <h3 class="coverage-name">Flood &amp; Earthquake — NOT included</h3>
        <span class="coverage-tag lender">Separate policy required</span>
      </div>
      <div class="coverage-body">
        <p><strong>Homeowners insurance does not cover flood or earthquake.</strong> Flood is a separate policy through the NFIP or a private insurer; earthquake is a separate endorsement or policy. If you're in a flood-prone or seismic area, the base policy alone will leave you exposed on the very loss most likely to total your home.</p>
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
        <p>Enter ZIP to rank home insurance carriers by likely premium — adjusted for your coverage level and state.</p>
        <p style="font-size:14px;margin-top:10px;">Want the full picture? See <a href="/home/" style="color:var(--accent);text-decoration:none;border-bottom:1px solid currentColor;">home insurance rate comparison →</a></p>
      </div>
      <a href="/home/" class="cta-btn">Compare rates →</a>
    </div>
  </div>
</section>
'''

start = h.index('<div class="wrap-narrow">\n  <div class="page-header">')
foot_at = h.index('<footer class="site-foot">', start)
h = h[:start] + NEW_BODY + "\n" + h[foot_at:]

# ── sticky labels + links ──
h = h.replace('<a href="/renters/" class="sticky-compare-link"', '<a href="/home/" class="sticky-compare-link"')

# ── CALCULATOR SCRIPT ──
NEW_SCRIPT = '''<script>
// ── Home coverage calculator ──
const HOME_STATE_DATA = {
  "AL":{name:"Alabama",avg:2150},"AK":{name:"Alaska",avg:1245},"AZ":{name:"Arizona",avg:1680},
  "AR":{name:"Arkansas",avg:2280},"CA":{name:"California",avg:1840},"CO":{name:"Colorado",avg:2820},
  "CT":{name:"Connecticut",avg:1540},"DC":{name:"Washington D.C.",avg:1310},"DE":{name:"Delaware",avg:1090},
  "FL":{name:"Florida",avg:4218},"GA":{name:"Georgia",avg:1976},"HI":{name:"Hawaii",avg:1118},
  "ID":{name:"Idaho",avg:1155},"IL":{name:"Illinois",avg:1862},"IN":{name:"Indiana",avg:1750},
  "IA":{name:"Iowa",avg:1630},"KS":{name:"Kansas",avg:2860},"KY":{name:"Kentucky",avg:2170},
  "LA":{name:"Louisiana",avg:3635},"ME":{name:"Maine",avg:1295},"MD":{name:"Maryland",avg:1490},
  "MA":{name:"Massachusetts",avg:1650},"MI":{name:"Michigan",avg:1680},"MN":{name:"Minnesota",avg:2090},
  "MS":{name:"Mississippi",avg:2480},"MO":{name:"Missouri",avg:2050},"MT":{name:"Montana",avg:1880},
  "NE":{name:"Nebraska",avg:2480},"NV":{name:"Nevada",avg:1380},"NH":{name:"New Hampshire",avg:1070},
  "NJ":{name:"New Jersey",avg:1492},"NM":{name:"New Mexico",avg:1860},"NY":{name:"New York",avg:1676},
  "NC":{name:"North Carolina",avg:1845},"ND":{name:"North Dakota",avg:1635},"OH":{name:"Ohio",avg:1580},
  "OK":{name:"Oklahoma",avg:3285},"OR":{name:"Oregon",avg:1200},"PA":{name:"Pennsylvania",avg:1492},
  "RI":{name:"Rhode Island",avg:1760},"SC":{name:"South Carolina",avg:1890},"SD":{name:"South Dakota",avg:1860},
  "TN":{name:"Tennessee",avg:2090},"TX":{name:"Texas",avg:3429},"UT":{name:"Utah",avg:1280},
  "VT":{name:"Vermont",avg:1140},"VA":{name:"Virginia",avg:1558},"WA":{name:"Washington",avg:1250},
  "WV":{name:"West Virginia",avg:1560},"WI":{name:"Wisconsin",avg:1090},"WY":{name:"Wyoming",avg:1390}
};
const NATIONAL_AVG = 1915;

__ZIP3__

const DWELL_STEPS  = [150000,200000,250000,300000,400000,500000,750000,1000000,1500000];
const ASSET_STEPS  = [25000,50000,100000,200000,300000,500000,750000,1000000];
const LIAB_OPTS    = [100000,300000,500000];
const MEDPAY_OPTS  = [1000,5000];
const DED_FACTOR   = {1000:1.0, 2500:0.90, 5000:0.82};

const profile = {
  dwelling: 300000, assets: 200000, deductible: 1000,
  bundle: false, valuables: false,
  code: null, stateName: null, stateAvg: NATIONAL_AVG
};
const sels = { liability: 0, medpay: 1, contentsRcv: true, waterBackup: true, scheduled: false };

function fmt(n){ return '$' + Math.round(n).toLocaleString(); }
function stateFromZip(z){
  if(!/^\\d/.test(z)) return null;
  const p3 = z.slice(0,3);
  return ZIP3_TO_STATE[p3] || ZIP3_TO_STATE[('00'+z).slice(0,3)] || null;
}

function computeRecs(){
  let liab = 0;
  if(profile.assets > 300000) liab = 2;
  else if(profile.assets > 100000) liab = 1;
  return { liability: liab, medpay: 1, contentsRcv: true, waterBackup: true, scheduled: profile.valuables };
}
function applyRecs(){
  const r = computeRecs();
  sels.liability = r.liability; sels.medpay = r.medpay;
  sels.contentsRcv = r.contentsRcv; sels.waterBackup = r.waterBackup; sels.scheduled = r.scheduled;
}

function components(){
  const sm = profile.stateAvg / NATIONAL_AVG;
  const dwellFactor = profile.dwelling / 300000;
  const ded = DED_FACTOR[profile.deductible] || 1.0;
  const contentsMult = sels.contentsRcv ? 1.0 : 0.93;
  const bundleMult = profile.bundle ? 0.88 : 1.0;
  // base policy = dwelling + other structures + personal property + loss of use
  let base = profile.stateAvg * dwellFactor * ded * contentsMult * bundleMult;
  base = Math.max(400, base);
  const liabAdd = [0, 12, 28][sels.liability] * sm;
  const medpayAdd = [0, 8][sels.medpay] * sm;
  const waterAdd = sels.waterBackup ? 60 : 0;
  const schedAdd = sels.scheduled ? 50 : 0;
  return {
    base: base, liab: liabAdd, medpay: medpayAdd, water: waterAdd, sched: schedAdd,
    total: Math.round(base + liabAdd + medpayAdd + waterAdd + schedAdd)
  };
}
function totalEstimate(){ return components().total; }

const CARDS = ['dwelling','otherStructures','personalProperty','lossOfUse','liability','medpay','waterBackup','scheduled'];
const META = {
  dwelling:         { name:'Dwelling (Coverage A)', tag:'Rebuild cost of your home', guide:'guide-dwelling' },
  otherStructures:  { name:'Other Structures (Coverage B)', tag:'Detached garage, shed, fence', guide:'guide-otherstructures' },
  personalProperty: { name:'Personal Property (Coverage C)', tag:'Your belongings', guide:'guide-personal' },
  lossOfUse:        { name:'Loss of Use (Coverage D)', tag:'Hotels & extra costs if displaced', guide:'guide-lossofuse' },
  liability:        { name:'Personal Liability (Coverage E)', tag:'Injuries & damage you cause', guide:'guide-liability' },
  medpay:           { name:'Medical Payments (Coverage F)', tag:"Guests' minor medical bills", guide:'guide-medpay' },
  waterBackup:      { name:'Water Backup Endorsement', tag:'Sewer/drain backup & sump failure', guide:'guide-waterbackup' },
  scheduled:        { name:'Scheduled Items', tag:'Jewelry, cameras, art', guide:'guide-scheduled' }
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
  const A = profile.dwelling;
  const covB = Math.round(A * 0.10);
  const covC = Math.round(A * 0.50);
  const covD = Math.round(A * 0.30);
  let html = '';

  html += card('dwelling',
    deltaBadge('zero','Set to ' + fmt(A)),
    '<div class="cov-card-desc">Set this to your <strong>rebuild cost</strong> — what a contractor would charge to reconstruct your home today, <em>not</em> its market price. Based on your slider we\\'re using <strong>' + fmt(A) + '</strong>. Adjust the dwelling slider above to change it.</div>'
    + costLine(c.base));

  html += card('otherStructures',
    deltaBadge('zero','Auto: ' + fmt(covB)),
    '<div class="cov-card-desc">Defaults to 10% of dwelling — about <strong>' + fmt(covB) + '</strong>. Enough for most homes; raise it only for a large detached garage, workshop, or guest house.</div>'
    + costLine(0));

  html += card('personalProperty',
    deltaBadge(sels.contentsRcv ? 'minus' : 'plus', sels.contentsRcv ? 'Replacement cost' : 'ACV (pays less)'),
    '<div class="cov-card-desc">Defaults to 50% of dwelling — about <strong>' + fmt(covC) + '</strong>. Choose <strong>replacement cost</strong> so you\\'re paid to buy new, not depreciated value.</div>'
    + toggleRow('contentsRcv', sels.contentsRcv, sels.contentsRcv ? 'Replacement cost — ON' : 'Actual cash value (cheaper, pays less)'));

  html += card('lossOfUse',
    deltaBadge('zero','Auto: ' + fmt(covD)),
    '<div class="cov-card-desc">Bundled at roughly 30% of dwelling — about <strong>' + fmt(covD) + '</strong>. Covers hotels and extra living costs during a rebuild; usually nothing extra to buy.</div>'
    + costLine(0));

  html += card('liability',
    deltaBadge(sels.liability >= recs.liability ? 'minus' : 'plus',
      sels.liability >= recs.liability ? 'Covered' : 'Below rec'),
    '<div class="cov-card-desc">For your assets (' + fmt(profile.assets) + '), carry at least <strong>' + fmt(LIAB_OPTS[recs.liability]) + '</strong>. Higher limits cost only a little more.</div>'
    + pillBtns('liability', LIAB_OPTS, LIAB_OPTS.map(function(v){return fmt(v);}), sels.liability, recs.liability)
    + costLine(c.liab));

  html += card('medpay',
    deltaBadge(sels.medpay >= recs.medpay ? 'minus' : 'plus',
      sels.medpay >= recs.medpay ? 'Covered' : 'Low'),
    '<div class="cov-card-desc">Pays guests\\' minor medical bills without a liability claim. <strong>' + fmt(MEDPAY_OPTS[recs.medpay]) + '</strong> is the sensible default — only a few dollars.</div>'
    + pillBtns('medpay', MEDPAY_OPTS, MEDPAY_OPTS.map(function(v){return fmt(v);}), sels.medpay, recs.medpay)
    + costLine(c.medpay));

  html += card('waterBackup',
    deltaBadge(sels.waterBackup ? 'minus' : (recs.waterBackup ? 'plus' : 'zero'), sels.waterBackup ? 'Added' : 'Recommended'),
    '<div class="cov-card-desc">A standard policy <strong>excludes</strong> sewer/drain backup and sump-pump failure — a common basement claim. Add it for ~$50–100/yr.</div>'
    + toggleRow('waterBackup', sels.waterBackup, sels.waterBackup ? 'Water backup — ON' : 'Add water backup')
    + costLine(c.water));

  html += card('scheduled',
    deltaBadge(sels.scheduled ? 'minus' : 'zero', sels.scheduled ? 'Added' : (recs.scheduled ? 'Recommended' : 'Skip')),
    '<div class="cov-card-desc">Standard policies cap jewelry, cameras, and art. Schedule a specific item for its appraised value. ' + (recs.scheduled ? 'You said you have high-value items — schedule them.' : 'Skip this if you don\\'t own anything valuable.') + '</div>'
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

function renderSummary(){
  const total = totalEstimate();
  document.getElementById('summaryTotal').textContent = fmt(total) + '/yr';
  const d = total - profile.stateAvg;
  const dEl = document.getElementById('summaryDelta');
  const label = profile.code ? profile.stateName : 'national';
  if(Math.abs(d) < 40){
    dEl.innerHTML = '<span style="color:var(--ink-mute);font-size:13px;">about the ' + label + ' average (' + fmt(profile.stateAvg) + '/yr)</span>';
  } else if(d < 0){
    dEl.innerHTML = '<span style="color:var(--good);font-size:13px;font-weight:600;">' + fmt(Math.abs(d)) + '/yr below the ' + label + ' average</span>';
  } else {
    dEl.innerHTML = '<span style="color:var(--accent);font-size:13px;font-weight:600;">' + fmt(d) + '/yr above the ' + label + ' average</span>';
  }
  document.getElementById('stickyAmount').textContent = fmt(total) + '/yr';
  const sd = document.getElementById('stickyDelta');
  sd.textContent = profile.code ? profile.stateName : 'national avg';
  updateCta();
}

function updateCta(){
  const parts = [];
  parts.push(fmt(profile.dwelling) + ' dwelling');
  parts.push(fmt(LIAB_OPTS[sels.liability]) + ' liability');
  parts.push(sels.contentsRcv ? 'replacement cost' : 'actual cash value');
  if(sels.waterBackup) parts.push('water backup');
  if(sels.scheduled) parts.push('scheduled items');
  document.getElementById('ctaSelectionsSummary').textContent = 'Carrying over: ' + parts.join(' · ');
  refreshCtaLink();
}
function refreshCtaLink(){
  const zip = (document.getElementById('zipInput').value || '').replace(/\\D/g,'').slice(0,5);
  const q = zip.length === 5 ? ('?zip=' + zip) : '';
  ['ctaBtn','stickyCompareLink'].forEach(function(id){
    const el = document.getElementById(id); if(el) el.href = '/home/' + q;
  });
}

function setZip(z){
  z = (z||'').replace(/\\D/g,'').slice(0,5);
  const badge = document.getElementById('zipStateBadge');
  const code = z.length >= 3 ? stateFromZip(z) : null;
  if(code && HOME_STATE_DATA[code]){
    profile.code = code;
    profile.stateName = HOME_STATE_DATA[code].name;
    profile.stateAvg = HOME_STATE_DATA[code].avg;
    badge.textContent = profile.stateName + ' · avg ' + fmt(profile.stateAvg) + '/yr';
    badge.style.display = '';
  } else {
    profile.code = null; profile.stateName = null; profile.stateAvg = NATIONAL_AVG;
    badge.textContent = ''; badge.style.display = 'none';
  }
  refreshCtaLink();
  renderAll();
}

function renderAll(){ renderCards(); renderSummary(); }

function initEvents(){
  const dwellSlider = document.getElementById('dwellSlider');
  dwellSlider.addEventListener('input', function(){
    profile.dwelling = DWELL_STEPS[+this.value];
    document.getElementById('dwellDisplay').textContent = fmt(profile.dwelling);
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

  document.getElementById('covCards').addEventListener('click', function(e){
    const pill = e.target.closest('.pill[data-cov]');
    if(pill){ sels[pill.dataset.cov] = +pill.dataset.i; renderAll(); return; }
    const tgl = e.target.closest('[data-tgl]');
    if(tgl){ const k = tgl.dataset.tgl; sels[k] = !sels[k]; renderAll(); return; }
  });
}

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

s_start = h.index('<script>\n// ── Renters coverage calculator')
s_end = h.index('</script>', s_start) + len('</script>')
h = h[:s_start] + NEW_SCRIPT + h[s_end:]

# ── FAQ JSON-LD ──
NEW_FAQ = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How much dwelling coverage (Coverage A) do I need?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Set Coverage A to your home's rebuild cost — what a contractor would charge to reconstruct it today — not its market price (which includes land) and not what you paid. In fast-rising markets rebuild cost is often below market value; after a construction-cost spike it can be higher. Under-insuring here is the most common and costliest mistake, and many policies pro-rate even partial claims if you insure for less than 80% of rebuild cost. Ask your insurer to run a free replacement-cost estimate and update it after renovations."
      }
    },
    {
      "@type": "Question",
      "name": "What do Coverage B, C, D, E, and F mean on a homeowners policy?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Coverage B (Other Structures) covers detached structures like a garage, shed, or fence, usually defaulting to 10% of dwelling. Coverage C (Personal Property) covers your belongings, usually 50% of dwelling. Coverage D (Loss of Use) pays hotel and extra living costs if your home is unlivable, typically 20–30% of dwelling. Coverage E (Personal Liability) covers injuries or damage you cause, with $100,000 the minimum and $300,000–$500,000 recommended. Coverage F (Medical Payments) pays small medical bills for injured guests, usually $1,000–$5,000."
      }
    },
    {
      "@type": "Question",
      "name": "Does homeowners insurance cover flood or sewer backup?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Standard homeowners insurance does not cover flood or earthquake — those require separate policies (flood through the NFIP or a private insurer, earthquake as a separate policy or endorsement). It also excludes water that backs up through sewers or drains and sump-pump failure unless you add a water backup endorsement, which typically costs $50–$100 per year and is worth it if you have a finished basement or sump pump."
      }
    },
    {
      "@type": "Question",
      "name": "How much does homeowners insurance cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The national average runs roughly $1,900–$2,500 per year for about $300,000 in dwelling coverage, but it ranges enormously — from around $1,100 in low-risk states like Hawaii and Vermont to over $4,000 in Florida, Oklahoma, and other catastrophe-prone states. Premiums are driven mainly by your dwelling amount, your state and local risk, your deductible, your home's age and roof, and your claims history. Bundling with auto and raising your deductible are the two biggest levers."
      }
    }
  ]
}
</script>'''
f_start = h.index('<script type="application/ld+json">')
f_end = h.index('</script>', f_start) + len('</script>')
h = h[:f_start] + NEW_FAQ + h[f_end:]

open(OUT, "w", encoding="utf-8").write(h)
print("home/coverage.html built OK")
