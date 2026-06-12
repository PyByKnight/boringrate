// Headless funnel verification via jsdom. Loads a tool page, runs its JS, simulates
// a ZIP search, and inspects the rendered DOM. Not a CSS/visual check — a functional one.
const fs = require("fs");
const { JSDOM } = require("jsdom");

function run(file, zip, product) {
  const html = fs.readFileSync(file, "utf8");
  const errors = [];
  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    pretendToBeVisual: true,
    url: "https://boringrate.com/" + (product === "auto" ? "" : product + "/"),
    beforeParse(window) {
      // stub APIs jsdom lacks / external libs we don't load
      window.IntersectionObserver = class { observe(){} unobserve(){} disconnect(){} };
      window.matchMedia = () => ({ matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
      window.scrollTo = () => {};
      window.HTMLElement.prototype.scrollIntoView = () => {};
      window.plausible = () => {};
      const fakeSb = { auth: { signInWithOtp: async () => ({ error: null }), getSession: async () => ({ data:{session:null} }), onAuthStateChange(){} },
        from: () => ({ insert: async () => ({error:null}), select: () => ({ eq: () => ({ data:[], error:null }) }) }) };
      window.supabase = { createClient: () => fakeSb };
    },
  });
  const w = dom.window;
  w.addEventListener("error", e => errors.push("window.error: " + (e.error && e.error.stack || e.message)));
  w.console.error = (...a) => errors.push("console.error: " + a.join(" "));

  // let inline scripts run
  return new Promise(resolve => {
    w.document.addEventListener("DOMContentLoaded", () => {});
    setTimeout(() => {
      const d = w.document;
      const out = { file, errorsAtLoad: errors.slice() };
      // simulate ZIP search
      const zi = d.getElementById("zipInput");
      const zf = d.getElementById("zipForm");
      if (zi && zf) {
        zi.value = zip;
        zf.dispatchEvent(new w.Event("submit", { bubbles:true, cancelable:true }));
      } else out.noForm = true;

      const result = d.getElementById("result");
      const rows = d.querySelectorAll("#rankList .rank-row");
      const first = rows[0];
      out.resultActive = result && result.classList.contains("active");
      out.resultDemo = result && result.classList.contains("demo");
      out.rankRows = rows.length;
      if (first) {
        out.firstCarrier = (first.querySelector(".rank-name") || {}).textContent;
        out.firstPremium = (first.querySelector(".rank-premium") || {}).textContent;
        out.firstSave = (first.querySelector(".qcta-save") || {}).textContent;
        out.firstQuoteHref = (first.querySelector(".rank-quote-cta") || {}).getAttribute && first.querySelector(".rank-quote-cta").getAttribute("href");
      }
      const mt = d.querySelector(".rank-median-top");
      out.medianTop = mt ? mt.textContent.replace(/\s+/g, " ").trim() : "(none)";
      const cs = d.getElementById("crossSellRenters") || d.getElementById("crossSellAuto");
      if (cs) out.crossSell = { id: cs.id, href: cs.getAttribute("href"), state: (d.getElementById("crossSellState")||d.getElementById("crossSellAutoState")||{}).textContent };
      const ez = d.getElementById("emailZipInput");
      out.emailZipPrefill = ez ? ez.value : "(no field)";
      out.trackEvents = (w.brEvents || []).map(e => e.name + (e.props && e.props.zip ? "("+e.props.zip+")" : ""));
      out.errorsAfter = errors.slice(out.errorsAtLoad.length);
      resolve(out);
    }, 300);
  });
}

(async () => {
  const cases = [
    ["index.html", "80905", "auto"],     // Colorado Springs (new metro)
    ["index.html", "30301", "auto"],     // Atlanta (existing)
    ["renters/index.html", "33101", "renters"],
    ["home/index.html", "75201", "home"],
  ];
  for (const c of cases) {
    const r = await run(...c);
    console.log("\n=== " + r.file + "  zip=" + c[1] + " ===");
    console.log(JSON.stringify(r, null, 1));
  }
})();
