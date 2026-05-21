/* compare-profile.js — carrier compare pages: profile builder + smart verdict */
(function () {
  'use strict';

  var tbl = document.querySelector('.cmp-table');
  if (!tbl) return;

  var ths = tbl.querySelectorAll('thead th');
  var cA = ths[1] ? ths[1].textContent.trim() : '';
  var cB = ths[2] ? ths[2].textContent.trim() : '';

  function num(s) {
    var m = (s || '').match(/[\d,]+/);
    return m ? parseInt(m[0].replace(',', ''), 10) : null;
  }
  function pct(s) {
    var m = (s || '').match(/([+-]?\d+(?:\.\d+)?)%/);
    return m ? parseFloat(m[1]) / 100 : null;
  }

  var d = { a: { cFair: null, home: null }, b: { cFair: null, home: null } };
  var aWinThemes = [], bWinThemes = [];
  var telA = '', telB = '', buyA = '', buyB = '';
  var tableRows = [];
  var avgAnnualRow = null, avgOrigA = '', avgOrigB = '';

  tbl.querySelectorAll('tbody tr').forEach(function (row) {
    var cells = row.querySelectorAll('td');
    if (cells.length < 3) return;
    var lbl = cells[0].textContent.toLowerCase().trim();
    var vA = cells[1].textContent, vB = cells[2].textContent;
    var isAWin = row.classList.contains('row-win-a');
    var isBWin = row.classList.contains('row-win-b');

    if (lbl.includes('telematics')) { telA = vA.trim(); telB = vB.trim(); }
    if (lbl.includes('how to buy') || (lbl.includes('buy') && lbl.length < 20)) {
      buyA = vA.trim().toLowerCase(); buyB = vB.trim().toLowerCase();
    }

    tableRows.push({ lbl: lbl, row: row, isAWin: isAWin, isBWin: isBWin });

    var theme = null;
    if (lbl.includes('avg annual')) {
      d.a.base = num(vA); d.b.base = num(vB);
      avgAnnualRow = { row: row, cells: cells };
      avgOrigA = cells[1].textContent;
      avgOrigB = cells[2].textContent;
      theme = 'overall base rates';
    } else if (lbl.includes('excellent') && lbl.includes('credit')) {
      d.a.cExc = pct(vA); d.b.cExc = pct(vB);
      theme = 'drivers with excellent credit';
    } else if ((lbl.includes('fair') || lbl.includes('poor')) && lbl.includes('credit')) {
      if (d.a.cFair === null) { d.a.cFair = pct(vA); d.b.cFair = pct(vB); }
      theme = 'drivers with fair or poor credit';
    } else if (lbl.includes('young') || (lbl.includes('18') && lbl.includes('24'))) {
      d.a.young = pct(vA); d.b.young = pct(vB);
      theme = 'young drivers';
    } else if (lbl.includes('55') && (lbl.includes('+') || lbl.includes('driver') || lbl.includes('senior'))) {
      d.a.senior = pct(vA); d.b.senior = pct(vB);
      theme = 'drivers 55 and older';
    } else if (lbl.includes('homeowner') && !lbl.includes('multi') && !lbl.includes('bundle')) {
      if (d.a.home === null) { d.a.home = pct(vA); d.b.home = pct(vB); }
      theme = 'homeowner bundlers';
    } else if (lbl.includes('multi') || (lbl.includes('bundle') && lbl.includes('policy'))) {
      d.a.multi = pct(vA); d.b.multi = pct(vB);
      theme = 'multi-policy customers';
    } else if (lbl.includes('lapse') || (lbl.includes('gap') && lbl.includes('coverage'))) {
      d.a.lapse = pct(vA); d.b.lapse = pct(vB);
      theme = 'those recovering after a coverage gap';
    } else if (lbl.includes('complaint') || lbl.includes('naic')) {
      theme = 'customer satisfaction';
    }

    if (theme) {
      if (isAWin) aWinThemes.push(theme);
      if (isBWin) bWinThemes.push(theme);
    }
  });

  // ─── Smart verdict tagline (updates .cmp-verdict-sub if still present) ──────

  function applyCarrierContext(carrier, themes, telInfo) {
    if (carrier.toLowerCase().includes('root')) {
      var req = (telInfo || '').toLowerCase().includes('required');
      return themes.map(function (t) {
        if (t === 'overall base rates')
          return req ? 'safe drivers using its required RootApp telematics' : 'telematics-savvy safe drivers';
        return t;
      });
    }
    if (carrier.toLowerCase().includes('usaa')) {
      return themes.map(function (t) {
        if (t === 'overall base rates') return 'military members and veterans';
        return t;
      });
    }
    return themes;
  }

  var aThemes = applyCarrierContext(cA, aWinThemes, telA);
  var bThemes = applyCarrierContext(cB, bWinThemes, telB);
  function top2(arr) { return arr.slice(0, 2).join(' and '); }

  var verdictText = '';
  if (aThemes.length > 0 && bThemes.length > 0) {
    if (aThemes.length >= bThemes.length) {
      verdictText = 'While ' + cB + ' wins for ' + top2(bThemes) + ', ' + cA + ' is better for ' + top2(aThemes) + '.';
    } else {
      verdictText = 'While ' + cA + ' wins for ' + top2(aThemes) + ', ' + cB + ' is better for ' + top2(bThemes) + '.';
    }
  } else if (aThemes.length > 0) {
    verdictText = cA + ' leads across most profiles, especially for ' + top2(aThemes) + '.';
  } else if (bThemes.length > 0) {
    verdictText = cB + ' leads across most profiles, especially for ' + top2(bThemes) + '.';
  }
  var subEl = document.querySelector('.cmp-verdict-sub');
  if (subEl && verdictText) subEl.textContent = verdictText;

  // ─── Rate calculator ───────────────────────────────────────────────────────

  function calcRate(carrier, opts) {
    var r = carrier.base;
    if (!r) return null;
    if (opts.credit === 'excellent' && carrier.cExc != null) r *= (1 + carrier.cExc);
    else if (opts.credit === 'fair' && carrier.cFair != null) r *= (1 + carrier.cFair);
    else if (opts.credit === 'poor' && carrier.cFair != null) r *= (1 + carrier.cFair * 1.5);

    if (opts.age === 'young' && carrier.young != null) r *= (1 + carrier.young);
    else if (opts.age === 'young2') r *= 1.035;
    else if (opts.age === 'senior' && carrier.senior != null) r *= (1 + carrier.senior);

    if (opts.home === 'own' && carrier.home != null) r *= (1 + carrier.home);
    if (opts.home === 'own' && carrier.multi != null) r *= (1 + carrier.multi);

    if (opts.youngDriver && opts.age !== 'young' && carrier.young != null)
      r *= (1 + carrier.young * 0.5);

    if (opts.lapse && carrier.lapse != null) r *= (1 + carrier.lapse);
    if (opts.suspended) r *= 1.28;

    return Math.round(r);
  }

  function getOpts() {
    function pill(name) {
      var el = document.querySelector('[data-pb="' + name + '"] .pb-pill.active');
      return el ? el.dataset.v : null;
    }
    function chk(id) { var el = document.getElementById(id); return el ? el.checked : false; }
    return {
      credit: pill('credit'),
      age: pill('age'),
      home: pill('home'),
      vehicles: pill('vehicles'),
      coverage: pill('coverage'),
      shopping: pill('shopping'),
      youngDriver: chk('pbYoungDriver'),
      lapse: chk('pbLapsed'),
      suspended: chk('pbSuspended')
    };
  }

  function hasProfile(opts) {
    return !!(opts.credit || opts.age || opts.home || opts.youngDriver || opts.lapse || opts.suspended);
  }

  // ─── Table row muting ──────────────────────────────────────────────────────

  function muteRows(opts) {
    var active = hasProfile(opts);
    tableRows.forEach(function (item) {
      var lbl = item.lbl;
      var muted = false;
      if (active) {
        if (opts.credit === 'excellent' && (lbl.includes('fair') || lbl.includes('poor'))) muted = true;
        if ((opts.credit === 'fair' || opts.credit === 'poor') && lbl.includes('excellent')) muted = true;
        if ((opts.age === 'young' || opts.youngDriver) && (lbl.includes('55') || lbl.includes('senior'))) muted = true;
        if (opts.age === 'senior' && (lbl.includes('young') || (lbl.includes('18') && lbl.includes('24')))) muted = true;
        if (opts.home === 'rent' && (lbl.includes('homeowner') || (lbl.includes('bundle') && lbl.includes('home')))) muted = true;
        // Coverage gap: mute unless user explicitly checked it
        if (!opts.lapse && (lbl.includes('lapse') || (lbl.includes('gap') && lbl.includes('coverage')))) muted = true;
      }
      item.row.classList.toggle('pb-muted', muted);
    });
  }

  // ─── Shopping conflict note ────────────────────────────────────────────────

  function checkShoppingConflict(opts) {
    var noteEl = document.getElementById('pbShoppingNote');
    if (!noteEl) return;
    var note = '';
    if (opts.shopping === 'online') {
      if (buyA && buyA.includes('agent') && !buyA.includes('online')) note = '⚠ ' + cA + ' is available through agents only — not direct online.';
      else if (buyB && buyB.includes('agent') && !buyB.includes('online')) note = '⚠ ' + cB + ' is available through agents only — not direct online.';
    } else if (opts.shopping === 'agent') {
      if (buyA && !buyA.includes('agent')) note = '⚠ ' + cA + ' does not sell through agents — online / phone only.';
      else if (buyB && !buyB.includes('agent')) note = '⚠ ' + cB + ' does not sell through agents — online / phone only.';
    }
    noteEl.textContent = note;
    noteEl.style.display = note ? 'block' : 'none';
  }

  // ─── Winner column highlight ───────────────────────────────────────────────

  var thA = ths[1] || null;
  var thB = ths[2] || null;

  function updateWinnerColumn(rA, rB, profiled) {
    if (!thA || !thB || !rA || !rB) return;
    var aWins = rA <= rB;
    thA.classList.toggle('pb-col-winner', aWins);
    thB.classList.toggle('pb-col-winner', !aWins);
    var badge = profiled ? 'Best for your profile' : 'Best price';
    var winTh = aWins ? thA : thB;
    var loseTh = aWins ? thB : thA;
    var wBadge = winTh.querySelector('.pb-best-badge');
    var lBadge = loseTh.querySelector('.pb-best-badge');
    if (!wBadge) {
      wBadge = document.createElement('span');
      wBadge.className = 'pb-best-badge';
      winTh.appendChild(wBadge);
    }
    wBadge.textContent = badge;
    if (lBadge) lBadge.remove();
  }

  // ─── Update avg annual row in table ───────────────────────────────────────

  function updateAvgRow(rA, rB, profiled) {
    if (!avgAnnualRow) return;
    var cells = avgAnnualRow.cells;
    if (profiled && rA && rB) {
      if (cells[1]) cells[1].textContent = '$' + rA.toLocaleString();
      if (cells[2]) cells[2].textContent = '$' + rB.toLocaleString();
      avgAnnualRow.row.classList.toggle('row-win-a', rA <= rB);
      avgAnnualRow.row.classList.toggle('row-win-b', rB < rA);
    } else {
      if (cells[1]) cells[1].textContent = avgOrigA;
      if (cells[2]) cells[2].textContent = avgOrigB;
      avgAnnualRow.row.classList.toggle('row-win-a', (d.a.base || 0) <= (d.b.base || 0));
      avgAnnualRow.row.classList.toggle('row-win-b', (d.b.base || 0) < (d.a.base || 0));
    }
  }

  // ─── Update summary bar + form result ─────────────────────────────────────

  function updateResult() {
    var opts = getOpts();
    var profiled = hasProfile(opts);

    muteRows(opts);
    checkShoppingConflict(opts);

    var rA = calcRate(d.a, opts);
    var rB = calcRate(d.b, opts);
    if (!rA || !rB) return;

    var winner, loser, wRate, lRate;
    if (rA <= rB) { winner = cA; loser = cB; wRate = rA; lRate = rB; }
    else { winner = cB; loser = cA; wRate = rB; lRate = rA; }
    var save = lRate - wRate;

    updateAvgRow(rA, rB, profiled);
    updateWinnerColumn(rA, rB, profiled);

    // ── Clear button visibility ────────────────────────────────────────────
    if (clearBtn) clearBtn.style.display = profiled ? 'inline-block' : 'none';

    // ── Summary bar (always visible) ──────────────────────────────────────
    var labelEl = document.getElementById('pbSummaryLabel');
    var ratesEl = document.getElementById('pbSummaryRates');
    if (profiled) {
      if (labelEl) labelEl.textContent = 'Your profile';
      if (ratesEl) ratesEl.textContent = winner + ' wins — saves ~$' + save + '/yr vs ' + loser;
    } else {
      if (labelEl) labelEl.textContent = 'General rates';
      if (ratesEl) ratesEl.textContent = cA + ' ~$' + (d.a.base || 0).toLocaleString() + '/yr · ' + cB + ' ~$' + (d.b.base || 0).toLocaleString() + '/yr';
    }

    // ── Form result (visible only when form is open) ───────────────────────
    var winnerEl = document.getElementById('pbWinner');
    var detailEl = document.getElementById('pbDetail');
    if (!profiled) {
      if (winnerEl) winnerEl.textContent = '';
      if (detailEl) {
        detailEl.textContent = 'Select options above to see rates for your profile.';
        detailEl.style.color = 'var(--ink-mute)';
      }
    } else {
      if (winnerEl) winnerEl.textContent = winner + ' wins for your profile';
      if (detailEl) {
        detailEl.textContent = '~$' + wRate.toLocaleString() + '/yr vs ~$' + lRate.toLocaleString() + '/yr — saves ~$' + save + '/yr vs ' + loser;
        detailEl.style.color = '';
      }
    }

    // ── CTA link + profile persistence ────────────────────────────────────
    var cta = document.getElementById('pbCta');
    var zipEl2 = document.getElementById('pbZip');
    var zip = zipEl2 && /^\d{5}$/.test(zipEl2.value.trim()) ? zipEl2.value.trim() : '';
    if (!zip) { try { zip = JSON.parse(localStorage.getItem('br_profile') || '{}').zip || ''; } catch (e) {} }

    // Mirror ZIP to the zip-embed form at the bottom of the page
    var embedZip = document.getElementById('embedZipInput');
    if (embedZip && zip) embedZip.value = zip;

    if (cta) cta.href = zip ? '/?zip=' + zip : '/';

    // Save in the format index.html expects: {zip, refinement: {...}}
    try {
      var ageMap = { young: '18-24', young2: '25-34', mid: '35-54', senior: '55+' };
      var carrier = document.getElementById('pbCarrier') ? document.getElementById('pbCarrier').value : '';
      localStorage.setItem('br_profile', JSON.stringify({
        zip: zip,
        refinement: {
          own: opts.home || null,
          vehicles: opts.vehicles === '2' ? '2+' : (opts.vehicles || null),
          age: opts.age ? (ageMap[opts.age] || null) : null,
          credit: opts.credit || null,
          coverage: opts.coverage || null,
          youngDriver: opts.youngDriver || false,
          insured: !opts.lapse,
          srRequired: opts.suspended || false,
          curCarrier: carrier || ''
        }
      }));
    } catch (e) {}
  }

  // ─── Load saved profile ────────────────────────────────────────────────────

  var ageUnmap = { '18-24': 'young', '25-34': 'young2', '35-54': 'mid', '55+': 'senior' };

  function loadSaved() {
    try {
      var p = JSON.parse(localStorage.getItem('br_profile') || 'null');
      if (!p) return false;
      var r = p.refinement || {};
      var zipEl = document.getElementById('pbZip');
      if (zipEl && p.zip) zipEl.value = p.zip;
      // Restore pills: map index keys → compare data-v values
      var pillMap = {
        credit: r.credit || null,
        age: r.age ? (ageUnmap[r.age] || null) : null,
        home: r.own || null,
        vehicles: r.vehicles === '2+' ? '2' : (r.vehicles || null),
        coverage: r.coverage || null
      };
      Object.keys(pillMap).forEach(function (key) {
        var val = pillMap[key];
        if (!val) return;
        var grp = document.querySelector('[data-pb="' + key + '"]');
        var btn = grp ? grp.querySelector('[data-v="' + val + '"]') : null;
        if (!btn) return;
        grp.querySelectorAll('.pb-pill').forEach(function (b) { b.classList.remove('active'); });
        grp.classList.add('has-selection');
        btn.classList.add('active');
      });
      if (r.curCarrier) { var sel = document.getElementById('pbCarrier'); if (sel) sel.value = r.curCarrier; }
      if (r.youngDriver) { var yd = document.getElementById('pbYoungDriver'); if (yd) yd.checked = true; }
      if (r.insured === false) { var lp = document.getElementById('pbLapsed'); if (lp) lp.checked = true; }
      if (r.srRequired) { var sr = document.getElementById('pbSuspended'); if (sr) sr.checked = true; }
      return true;
    } catch (e) { return false; }
  }

  // ─── Clear button ─────────────────────────────────────────────────────────

  var clearBtn = document.getElementById('pbClearBtn');

  function clearProfile() {
    document.querySelectorAll('[data-pb] .pb-pill').forEach(function (b) { b.classList.remove('active'); });
    document.querySelectorAll('[data-pb]').forEach(function (g) { g.classList.remove('has-selection'); });
    ['pbYoungDriver', 'pbLapsed', 'pbSuspended'].forEach(function (id) {
      var el = document.getElementById(id); if (el) el.checked = false;
    });
    var zipEl2 = document.getElementById('pbZip'); if (zipEl2) zipEl2.value = '';
    var carSel2 = document.getElementById('pbCarrier'); if (carSel2) carSel2.value = '';
    try { localStorage.removeItem('br_profile'); } catch (e) {}
    if (clearBtn) clearBtn.style.display = 'none';
    // Restore table state
    if (avgAnnualRow) {
      var cells = avgAnnualRow.cells;
      if (cells[1]) cells[1].textContent = avgOrigA;
      if (cells[2]) cells[2].textContent = avgOrigB;
    }
    tableRows.forEach(function (item) { item.row.classList.remove('pb-muted'); });
    updateResult();
  }

  if (clearBtn) clearBtn.addEventListener('click', clearProfile);

  // ─── Toggle open/close ────────────────────────────────────────────────────

  var builderEl = document.getElementById('profileBuilder');
  var customizeBtn = document.getElementById('pbCustomizeBtn');
  var closeBottomBtn = document.getElementById('pbCloseBottom');

  function openBuilder() {
    if (!builderEl) return;
    builderEl.style.display = 'block';
    if (customizeBtn) {
      customizeBtn.textContent = 'Hide ▲';
      customizeBtn.classList.add('open');
    }
  }

  function closeBuilder() {
    if (!builderEl) return;
    builderEl.style.display = 'none';
    if (customizeBtn) {
      customizeBtn.textContent = 'Customize for your profile ▾';
      customizeBtn.classList.remove('open');
    }
  }

  if (customizeBtn) {
    customizeBtn.addEventListener('click', function () {
      var isOpen = builderEl && builderEl.style.display !== 'none';
      isOpen ? closeBuilder() : openBuilder();
    });
  }
  if (closeBottomBtn) closeBottomBtn.addEventListener('click', closeBuilder);

  // ─── Wire events ──────────────────────────────────────────────────────────

  document.querySelectorAll('[data-pb] .pb-pill').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var group = btn.closest('[data-pb]');
      group.querySelectorAll('.pb-pill').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      group.classList.add('has-selection');
      updateResult();
    });
  });

  ['pbYoungDriver', 'pbLapsed', 'pbSuspended'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('change', updateResult);
  });

  var zipEl = document.getElementById('pbZip');
  if (zipEl) zipEl.addEventListener('input', function (e) {
    e.target.value = e.target.value.replace(/\D/g, '').substring(0, 5);
    updateResult();
  });

  var carSel = document.getElementById('pbCarrier');
  if (carSel) carSel.addEventListener('change', updateResult);

  // ─── Why you might choose ─────────────────────────────────────────────────

  var CARRIER_WHY = {
    'GEICO': [
      'Lowest base rates among major national carriers — particularly strong for clean-record drivers',
      'Fully online — fast quotes, easy policy management, and claims handled through the app',
      'Military and federal employee discounts available on top of standard savings'
    ],
    'Progressive': [
      'Snapshot telematics can significantly cut your rate if you drive carefully and not often',
      'More lenient than most carriers on drivers with tickets, incidents, or prior coverage gaps',
      'Name Your Price tool lets you set a budget and find coverage that fits'
    ],
    'State Farm': [
      'Drive Safe & Save telematics can reduce your rate by up to 30% for safe, low-mileage driving',
      'Largest local agent network in the country — ideal if you prefer hands-on, in-person support',
      'Strong youth discounts including good student and distant student programs for families'
    ],
    'Allstate': [
      'Drivewise telematics earns ongoing cash-back rewards for safe driving habits',
      'Home + auto bundling can save 10–25% if you own your home and insure it with the same carrier',
      'Accident forgiveness keeps your rate stable after a first at-fault claim'
    ],
    'USAA': [
      'Among the lowest rates in most states — exclusive to active military, veterans, and their families',
      'SafePilot telematics stacks an additional 10–30% discount on already-low base rates',
      'Consistently top-rated for claims satisfaction and overall customer experience'
    ],
    'Liberty Mutual': [
      'RightTrack telematics can earn up to 30% off for safe, low-mileage driving habits',
      'New car replacement covers full original value — not depreciated cost — after a total loss',
      'Accident forgiveness prevents a rate hike after your first at-fault accident'
    ],
    'Farmers': [
      'Signal telematics app rewards smooth, accident-free driving with meaningful discounts',
      'Multi-policy bundle savings when combining home and auto with the same carrier',
      'Wide local agent network for drivers who prefer in-person coverage guidance'
    ],
    'Nationwide': [
      'SmartRide telematics delivers consistent savings for low-mileage, safe drivers',
      'Vanishing deductible reduces your out-of-pocket cost by $100 for every claim-free year',
      'Competitive rates for drivers 55+ through its dedicated mature driver discount'
    ],
    'Travelers': [
      'IntelliDrive telematics rewards low mileage and smooth, consistent driving behavior',
      'Strong multi-policy savings when bundling home and auto coverage together',
      'One of the most financially stable carriers in the industry — confidence at claims time'
    ],
    'Root Insurance': [
      'Telematics-only pricing — safe drivers consistently pay 20–40% below market averages',
      'Credit score is not used in rate calculation, making it strong for fair or poor credit',
      'Fully digital — no agents, straightforward app-based quotes, policy management, and claims'
    ],
    'Safeco': [
      'RightTrack telematics provides ongoing safe-driver savings, not just a sign-up discount',
      'Strong home + auto bundle discount for customers insuring both with the same carrier',
      'Diminishing deductible rewards each claim-free year with lower out-of-pocket exposure'
    ],
    'The Hartford': [
      'AARP partnership consistently delivers the lowest rates for drivers 50 and older',
      'RecoverCare benefit covers household help — cleaning, cooking, errands — after an accident',
      'Lifetime renewability guarantee means AARP members cannot be dropped for claims frequency'
    ]
  };

  function buildWhySection() {
    if (document.querySelector('.pb-why')) return;
    var whyA = CARRIER_WHY[cA];
    var whyB = CARRIER_WHY[cB];
    if (!whyA && !whyB) return;

    var section = document.createElement('div');
    section.className = 'pb-why';

    function makeCol(name, bullets) {
      var col = document.createElement('div');
      col.className = 'pb-why-col';
      col.innerHTML =
        '<p class="pb-why-kicker">Why you might choose</p>' +
        '<p class="pb-why-name">' + name + '</p>' +
        '<ul class="pb-why-list">' +
        bullets.map(function (b) { return '<li class="pb-why-item">' + b + '</li>'; }).join('') +
        '</ul>';
      return col;
    }

    if (whyA) section.appendChild(makeCol(cA, whyA));
    if (whyB) section.appendChild(makeCol(cB, whyB));

    var actions = document.querySelector('.pb-standalone-actions');
    if (actions && actions.parentNode) {
      actions.parentNode.insertBefore(section, actions);
    }
  }

  // ─── Init ─────────────────────────────────────────────────────────────────

  document.querySelectorAll('[data-pb] .pb-pill').forEach(function (b) { b.classList.remove('active'); });

  var hadSaved = loadSaved();

  if (hadSaved && hasProfile(getOpts())) {
    openBuilder();
  }

  buildWhySection();
  updateResult();

})();
