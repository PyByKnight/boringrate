// Pre-render a static, indexable "Cheapest carriers in [State]" ranked table into a
// state article. Uses the same state-avg × carrier-base × state-adjustment model as the
// tool (index.html). Directional (not a quote); the ZIP CTA refines. Idempotent (markers).
const fs = require("fs");

const idx = fs.readFileSync("index.html", "utf8");
function grab(name, open, close) {
  const i = idx.indexOf(name); const s = idx.indexOf(open, i); let d = 0, j = s;
  for (; j < idx.length; j++) { if (idx[j] === open) d++; else if (idx[j] === close) { d--; if (!d) { j++; break; } } }
  return idx.slice(s, j);
}
const SD = eval("(" + grab("const STATE_DATA", "{", "}") + ")");
const ADJ = eval("(" + grab("const STATE_CARRIER_ADJ", "{", "}") + ")");
const CAR = eval("(" + grab("const CARRIERS", "[", "]") + ")");
const MADJ = eval("(" + grab("const METRO_CARRIER_ADJ", "{", "}") + ")");
const MN = eval("(" + grab("const METRO_NAMES", "{", "}") + ")");
const ZM = eval("(" + grab("const ZIP_PREFIX_METRO", "{", "}") + ")");
const Z3 = eval("(" + grab("const ZIP3_TO_STATE", "{", "}") + ")");

// metro key -> state code (first ZIP prefix that maps to the metro)
const METRO_STATE = {};
for (const p in ZM) { const m = ZM[p]; if (!METRO_STATE[m]) { const st = Z3[p] || Z3[p.slice(0, 2)]; if (st) METRO_STATE[m] = st; } }
// metro key -> article slug overrides (display name doesn't match the filename)
const SLUG_OVERRIDE = { tam: "tampa", sjv: "san-jose", nfk: "norfolk", csc: "columbia-sc",
  gso: "greensboro", wil: "wilmington-de", mnh: "manchester-nh", bvt: "burlington-vt" };

const RED = "#b4321a", GREEN = "#2f6b3a";
const START = "<!-- state-rankings-start -->", END = "<!-- state-rankings-end -->";

function rankState(code) {
  const avg = SD[code].avg;
  const ranked = CAR.map(c => {
    const sm = (ADJ[code] && ADJ[code][c.name] != null) ? ADJ[code][c.name] : 1.0;
    return { name: c.name, price: Math.round(avg * c.base * sm), grade: c.csGrade };
  }).sort((a, b) => a.price - b.price);
  const top = ranked.slice(0, 10);
  const sorted = top.map(r => r.price).sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[mid] : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
  return { avg, top, median };
}

function rankMetro(key) {
  const st = METRO_STATE[key]; const avg = SD[st].avg; const madj = MADJ[key] || {};
  const ranked = CAR.map(c => {
    const sm = (ADJ[st] && ADJ[st][c.name] != null) ? ADJ[st][c.name] : 1.0;
    const mm = madj[c.name] != null ? madj[c.name] : 1.0;
    return { name: c.name, price: Math.round(avg * c.base * sm * mm) };
  }).sort((a, b) => a.price - b.price);
  const top = ranked.slice(0, 10);
  const sorted = top.map(r => r.price).sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[mid] : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
  const mult = Object.values(madj); const mean = mult.length ? mult.reduce((a, b) => a + b, 0) / mult.length : 1;
  return { avg: Math.round(avg * mean), top, median };
}

function block(name, data, avgLabel) {
  const { avg, top, median } = data;
  const rows = top.map((r, i) => {
    const d = r.price - median;
    const vs = d <= 0
      ? `<span style="color:${GREEN};font-weight:600;">Save $${Math.abs(d).toLocaleString()}</span>`
      : `<span style="color:${RED};font-weight:600;">+$${d.toLocaleString()}</span>`;
    return `<tr style="border-bottom:1px solid var(--rule);"><td style="padding:8px 6px;color:var(--ink-mute);">${i + 1}</td>`
      + `<td style="padding:8px 6px;"><strong>${r.name}</strong></td>`
      + `<td style="padding:8px 6px;">$${r.price.toLocaleString()}/yr</td><td style="padding:8px 6px;">${vs}</td></tr>`;
  }).join("");
  return `${START}
<h2>Cheapest car insurance carriers in ${name}</h2>
<p>Estimated annual full-coverage premiums for a standard driver profile, ranked cheapest first &mdash; the ${avgLabel} runs about <strong>$${avg.toLocaleString()}/yr</strong> (median of the top carriers below: $${median.toLocaleString()}/yr). Enter your ZIP for a ranking tuned to your exact area, vehicle, and coverage.</p>
<table style="width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:660px;">
<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;"><th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">Carrier</th><th style="padding:8px 6px;">Est. annual</th><th style="padding:8px 6px;">vs median</th></tr></thead>
<tbody>${rows}</tbody></table>
<p style="font-size:13px;color:var(--ink-mute);max-width:660px;">Directional estimates from public rate filings and NAIC complaint indices &mdash; not a quote. Your actual rate depends on your ZIP, vehicle, age, and credit. Enter your ZIP below for your personalized ranking.</p>
${END}`;
}

function inject(path, name, data, avgLabel) {
  if (!fs.existsSync(path)) { console.log("  ! no article:", path); return; }
  let h = fs.readFileSync(path, "utf8");
  const blk = block(name, data, avgLabel);
  if (h.includes(START)) {
    h = h.replace(new RegExp(START + "[\\s\\S]*?" + END), blk);
  } else {
    const bodyAt = h.indexOf('<div class="article-body">');
    let at = h.indexOf("<h2", bodyAt);                       // prefer before first <h2>
    if (at === -1) at = h.indexOf('<div class="zip-embed"', bodyAt);  // else before the ZIP CTA
    if (at === -1) { console.log("  ! no anchor, skipped:", path); return; }
    h = h.slice(0, at) + blk + "\n    " + h.slice(at);
  }
  fs.writeFileSync(path, h);
  console.log("  injected:", path);
}

function injectState(code) {
  const name = SD[code].name;
  const slug = name.toLowerCase().replace(/\./g, "").replace(/\s+/g, "-");
  inject(`article/state/${slug}.html`, name, rankState(code), `${name} statewide average`);
}

function injectMetro(key) {
  if (!MADJ[key] || !METRO_STATE[key] || !SD[METRO_STATE[key]]) { console.log("  ! unresolved metro:", key); return; }
  const clean = (MN[key] || key).replace(/ metro$/i, "");
  const slug = SLUG_OVERRIDE[key] || clean.toLowerCase().replace(/[–—]/g, "-").replace(/[.,/]/g, "").replace(/ & /g, "-").replace(/\s+/g, "-");
  inject(`article/metro/${slug}.html`, clean, rankMetro(key), `${clean} average`);
}

// metro articles with no distinct pricing key -> use their state's ranking
const METRO_EXTRA = { "portland-me": ["ME", "Portland, ME"] };

const args = process.argv.slice(2);
if (args[0] === "--metros") {
  Object.keys(MADJ).forEach(injectMetro);
  for (const slug in METRO_EXTRA) { const [st, nm] = METRO_EXTRA[slug]; inject(`article/metro/${slug}.html`, nm, rankState(st), `${nm} average`); }
}
else if (args[0] === "--states") Object.keys(SD).filter(c => SD[c] && SD[c].avg).forEach(injectState);
else if (args.length) args.forEach(injectState);
else console.log("usage: node gen_state_rankings.js [--states | --metros | TN CO ...]");
