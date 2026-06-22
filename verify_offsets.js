// Verifies the renters/home carrier-by-state offset is LIVE: the carrier ranking
// must reorder between a low-cost and a high-cost state (pre-offset it was identical
// everywhere). Run: node verify_offsets.js
const fs = require("fs"), { JSDOM } = require("jsdom");

function load(path, url) {
  const html = fs.readFileSync(path, "utf8");
  const dom = new JSDOM(html, {
    runScripts: "dangerously", url,
    beforeParse(w) {
      w.Element.prototype.scrollIntoView = function () {};
      w.HTMLElement.prototype.scrollIntoView = function () {};
      w.supabase = { createClient: () => ({ auth: { onAuthStateChange() {}, getSession: async () => ({ data: { session: null } }) }, from: () => ({ insert: async () => ({}), select: () => ({ eq: () => ({}) }) }) }) };
    }
  });
  return dom.window;
}

// Compute the ranked carrier order for a given state code, directly from the
// page's own model (estimatePremium + carrier array), so we test the live code.
function orderFor(w, code) {
  // Run in page scope so module-level `const` (CARRIERS, STATE_DATA, STATE_CARRIER_ADJ)
  // and estimatePremium are all visible.
  return w.eval(`(function(code){
    var carriers = (typeof RENTERS_CARRIERS!=='undefined'?RENTERS_CARRIERS:HOME_CARRIERS);
    var SD = (typeof RENTERS_STATE_DATA!=='undefined'?RENTERS_STATE_DATA:HOME_STATE_DATA);
    var sd = SD[code]; stateData = sd;
    return carriers.filter(function(c){return !c.states||c.states.indexOf(code)>-1;})
      .map(function(c){return {name:c.name, price:estimatePremium(c, sd.avg)};})
      .sort(function(a,b){return a.price-b.price;})
      .map(function(r){return r.name;});
  })(${JSON.stringify(code)})`);
}

function check(label, path, url, cheap, pricey) {
  return new Promise(resolve => {
    const w = load(path, url);
    const errs = []; w.onerror = e => errs.push(String(e));
    setTimeout(() => {
      const a = orderFor(w, cheap), b = orderFor(w, pricey);
      const reordered = a.join(",") !== b.join(",");
      // spot-check: an agent carrier should rank worse (higher index) in the pricey state
      const agent = (w.HOME_CARRIERS ? "Allstate" : "Allstate");
      const aIdx = a.indexOf(agent), bIdx = b.indexOf(agent);
      console.log(`\n[${label}]`);
      console.log("  JS errors:", errs.length ? errs : "NONE");
      console.log(`  ${cheap} order top5:`, a.slice(0, 5).join(" < "));
      console.log(`  ${pricey} order top5:`, b.slice(0, 5).join(" < "));
      console.log(`  reorders between states:`, reordered);
      console.log(`  Allstate rank ${cheap}=${aIdx} -> ${pricey}=${bIdx} (expect worse/higher in pricey):`, bIdx >= aIdx);
      resolve(errs.length === 0 && reordered && bIdx >= aIdx);
    }, 250);
  });
}

(async () => {
  const r = await check("renters", "renters/index.html", "https://boringrate.com/renters/index.html", "MT", "LA");
  const h = await check("home", "home/index.html", "https://boringrate.com/home/index.html", "HI", "CO");
  console.log("\nPASS:", r && h);
  process.exit(r && h ? 0 : 1);
})();
