// Pre-render a static, indexable "Cheapest renters carriers in [State]" ranked table
// into each renters state article. Mirrors gen_state_rankings.js but uses the RENTERS
// model in renters/index.html (avg × base, filtered by carrier availability).
const fs = require("fs");
const src = fs.readFileSync("renters/index.html", "utf8");
function grab(name, open, close) {
  const i = src.indexOf(name); const s = src.indexOf(open, i); let d = 0, j = s;
  for (; j < src.length; j++) { if (src[j] === open) d++; else if (src[j] === close) { d--; if (!d) { j++; break; } } }
  return src.slice(s, j);
}
const SD = eval("(" + grab("const RENTERS_STATE_DATA", "{", "}") + ")");
const CAR = eval("(" + grab("const RENTERS_CARRIERS", "[", "]") + ")");

const RED = "#b4321a", GREEN = "#2f6b3a";
const START = "<!-- state-rankings-start -->", END = "<!-- state-rankings-end -->";

function rankState(code) {
  const avg = SD[code].avg;
  const ranked = CAR.filter(c => !c.states || c.states.includes(code))
    .map(c => ({ name: c.name, price: Math.round(avg * c.base) }))
    .sort((a, b) => a.price - b.price);
  const top = ranked.slice(0, 10);
  const sorted = top.map(r => r.price).sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  const median = sorted.length % 2 ? sorted[mid] : Math.round((sorted[mid - 1] + sorted[mid]) / 2);
  return { avg, top, median };
}

function block(name, data) {
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
<h2>Cheapest renters insurance carriers in ${name}</h2>
<p>Estimated annual renters premiums for a standard policy (~$30k personal property), ranked cheapest first &mdash; ${name} averages about <strong>$${avg.toLocaleString()}/yr</strong> (median of the carriers below: $${median.toLocaleString()}/yr). Enter your ZIP for a ranking tuned to your coverage and deductible.</p>
<table style="width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:660px;">
<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;"><th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">Carrier</th><th style="padding:8px 6px;">Est. annual</th><th style="padding:8px 6px;">vs median</th></tr></thead>
<tbody>${rows}</tbody></table>
<p style="margin:14px 0 8px;"><a href="#embedZipForm" style="display:inline-block;background:var(--accent);color:#fff;font-family:var(--mono);font-size:13px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;padding:13px 24px;text-decoration:none;border-radius:2px;">Enter your ZIP for your exact rate &rarr;</a></p>
<p style="font-size:13px;color:var(--ink-mute);max-width:660px;">Directional estimates from public filings and NAIC complaint indices &mdash; not a quote. Your actual rate depends on coverage amount, deductible, and ZIP.</p>
${END}`;
}

function inject(code) {
  const name = SD[code].name; const slug = SD[code].slug;
  const path = `renters/state/${slug}.html`;
  if (!fs.existsSync(path)) { console.log("  ! no article:", path); return; }
  let h = fs.readFileSync(path, "utf8");
  h = h.replace(new RegExp("\\s*" + START + "[\\s\\S]*?" + END), "");
  const marker = '<div class="article-body">';
  const at = h.indexOf(marker);
  if (at === -1) { console.log("  ! no article-body:", path); return; }
  const pos = at + marker.length;
  h = h.slice(0, pos) + "\n" + block(name, rankState(code)) + h.slice(pos);
  fs.writeFileSync(path, h);
  console.log("  injected:", path);
}

const args = process.argv.slice(2);
const codes = args.length && args[0] !== "--all" ? args : Object.keys(SD).filter(c => SD[c] && SD[c].avg);
codes.forEach(inject);
console.log(codes.length, "renters state pages");
