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

  // ─── Smart verdict tagline ─────────────────────────────────────────────────

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
    // Only apply adjustments for options the user actually selected (null = skip)
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
      return el ? el.dataset.v : null; // null = not selected
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

  // ─── Table row highlighting ────────────────────────────────────────────────

  function highlightRows(opts) {
    tableRows.forEach(function (item) {
      var lbl = item.lbl;
      var rel = false;
      if (opts.credit === 'excellent' && lbl.includes('excellent')) rel = true;
      if ((opts.credit === 'fair' || opts.credit === 'poor') && (lbl.includes('fair') || lbl.includes('poor'))) rel = true;
      if ((opts.age === 'young' || opts.youngDriver) && (lbl.includes('young') || (lbl.includes('18') && lbl.includes('24')))) rel = true;
      if (opts.age === 'senior' && lbl.includes('55')) rel = true;
      if (opts.home === 'own' && (lbl.includes('homeowner') || lbl.includes('multi') || lbl.includes('bundle'))) rel = true;
      if (opts.lapse && (lbl.includes('lapse') || (lbl.includes('gap') && lbl.includes('coverage')))) rel = true;
      if (opts.shopping !== 'any' && opts.shopping && (lbl.includes('how to buy') || (lbl.includes('buy') && lbl.length < 20))) rel = true;
      item.row.classList.toggle('pb-relevant', rel);
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

  // ─── Update summary bar + form result ─────────────────────────────────────

  function updateResult() {
    var opts = getOpts();
    var profiled = hasProfile(opts);

    highlightRows(opts);
    checkShoppingConflict(opts);

    var rA = calcRate(d.a, opts);
    var rB = calcRate(d.b, opts);
    if (!rA || !rB) return;

    var winner, loser, wRate, lRate;
    if (rA <= rB) { winner = cA; loser = cB; wRate = rA; lRate = rB; }
    else { winner = cB; loser = cA; wRate = rB; lRate = rA; }
    var save = lRate - wRate;

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

    // ── CTA link ───────────────────────────────────────────────────────────
    var cta = document.getElementById('pbCta');
    if (cta) {
      var zip = '';
      var zipEl = document.getElementById('pbZip');
      if (zipEl && /^\d{5}$/.test(zipEl.value.trim())) zip = zipEl.value.trim();
      if (!zip) { try { zip = JSON.parse(localStorage.getItem('br_profile') || '{}').zip || ''; } catch (e) {} }
      cta.href = zip ? '/?zip=' + zip : '/';
      try {
        var carrier = document.getElementById('pbCarrier') ? document.getElementById('pbCarrier').value : '';
        localStorage.setItem('br_profile', JSON.stringify({
          zip: zip, credit: opts.credit, age: opts.age, home: opts.home,
          vehicles: opts.vehicles, coverage: opts.coverage, carrier: carrier,
          from: 'compare', fromCarriers: cA + ' vs ' + cB
        }));
      } catch (e) {}
    }
  }

  // ─── Load saved profile ────────────────────────────────────────────────────

  function loadSaved() {
    try {
      var p = JSON.parse(localStorage.getItem('br_profile') || 'null');
      if (!p) return false;
      var zipEl = document.getElementById('pbZip');
      if (zipEl && p.zip) zipEl.value = p.zip;
      ['credit', 'age', 'home', 'coverage'].forEach(function (key) {
        if (!p[key]) return;
        var btn = document.querySelector('[data-pb="' + key + '"] [data-v="' + p[key] + '"]');
        if (!btn) return;
        document.querySelectorAll('[data-pb="' + key + '"] .pb-pill').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
      });
      if (p.carrier) { var sel = document.getElementById('pbCarrier'); if (sel) sel.value = p.carrier; }
      return true;
    } catch (e) { return false; }
  }

  // ─── Toggle open/close ────────────────────────────────────────────────────

  var builderEl = document.getElementById('profileBuilder');
  var customizeBtn = document.getElementById('pbCustomizeBtn');

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

  // ─── Wire events ──────────────────────────────────────────────────────────

  document.querySelectorAll('[data-pb] .pb-pill').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.closest('[data-pb]').querySelectorAll('.pb-pill').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
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

  // ─── Init ─────────────────────────────────────────────────────────────────

  // Always start with no active pills — clear any defaults baked into HTML
  document.querySelectorAll('[data-pb] .pb-pill').forEach(function (b) { b.classList.remove('active'); });

  var hadSaved = loadSaved();

  // If user has a prior saved profile, open the form and show their results
  if (hadSaved && hasProfile(getOpts())) {
    openBuilder();
  }

  updateResult(); // sets summary bar to "General rates" (or profile if restored)

})();
