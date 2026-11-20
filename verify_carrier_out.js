// Verifies outbound carrier links route through js/carrier-out.js in all 3 tools:
// non-partner → canonical + UTM, label = carrier domain; a fake partner → sponsored link,
// partner note shown, label still the carrier domain, rank ORDER unchanged.
const fs = require("fs"), { JSDOM } = require("jsdom");
const OUT = fs.readFileSync("js/carrier-out.js", "utf8");
const TOOLS = [["index.html", "", "auto"], ["home/index.html", "home/", "home"], ["renters/index.html", "renters/", "renters"]];
function load(file, path, partnerName) {
  let code = OUT;
  if (partnerName) code = code.replace("var PARTNERS = {", 'var PARTNERS = {"' + partnerName + '": {url: "https://track.example/c/1?subId1={product}&subId2={state}&subId3={source}"},');
  const html = fs.readFileSync(file, "utf8").replace('<script src="/js/carrier-out.js"></script>', "<script>" + code + "</script>");
  const errors = [];
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "https://boringrate.com/" + path,
    beforeParse(w) { w.IntersectionObserver = class { observe(){} unobserve(){} disconnect(){} };
      w.matchMedia = () => ({ matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
      w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = () => {};
      w.supabase = { createClient: () => ({ auth: { onAuthStateChange(){}, getSession: async () => ({ data:{session:null} }) }, from: () => ({ insert: async () => ({}) }) }) }; } });
  dom.window.addEventListener("error", e => errors.push(e.message));
  return new Promise(res => setTimeout(() => {
    const d = dom.window.document, zi = d.getElementById("zipInput"), zf = d.getElementById("zipForm");
    zi.value = "30301"; zf.dispatchEvent(new dom.window.Event("submit", { bubbles:true, cancelable:true }));
    setTimeout(() => {
      const rows = [...d.querySelectorAll("#rankList [data-carrier]")].map(r => {
        const a = r.querySelector(".rank-quote-cta");
        return { name: r.dataset.carrier, href: a && a.href, rel: a && a.rel, partner: a && a.dataset.partner, label: a && (a.querySelector(".qcta-action") || {}).textContent };
      });
      res({ rows, foot: d.getElementById("rankFoot").innerHTML, errors });
    }, 600);
  }, 600));
}
(async () => {
  let fail = 0;
  const bad = m => { console.log("  FAIL", m); fail++; };
  for (const [file, path, prod] of TOOLS) {
    const base = await load(file, path);
    console.log(file, "rows:", base.rows.length, "errors:", base.errors.length);
    if (!base.rows.length) bad("no rows");
    base.errors.forEach(e => bad(e));
    for (const r of base.rows) {
      if (r.partner !== "0") bad(r.name + " partner flag " + r.partner);
      if (!/utm_source=boringrate&utm_medium=referral&utm_campaign=/.test(r.href) && !/#$/.test(r.href)) bad(r.name + " no UTM " + r.href);
      if (!/noreferrer/.test(r.rel)) bad(r.name + " rel " + r.rel);
    }
    if (/rank-partner-note/.test(base.foot)) bad("partner note shown with no partners");
    const target = base.rows[2].name;
    const p = await load(file, path, target);
    const order0 = base.rows.map(r => r.name).join("|"), order1 = p.rows.map(r => r.name).join("|");
    if (order0 !== order1) bad("ORDER CHANGED with partner");
    const pr = p.rows.find(r => r.name === target);
    if (!pr || pr.partner !== "1" || !/^https:\/\/track\.example\/c\/1\?subId1=/.test(pr.href) || !/sponsored/.test(pr.rel)) bad("partner row wrong " + JSON.stringify(pr));
    else console.log("  partner:", target, pr.href, "| label:", pr.label.trim());
    if (pr && pr.label.indexOf("example") > -1) bad("label shows tracking domain");
    if (!/rank-partner-note/.test(p.foot)) bad("partner note missing");
    console.log("  sample:", base.rows[0].name, base.rows[0].href);
  }
  console.log(fail ? fail + " FAIL" : "ALL OK"); process.exit(fail ? 1 : 0);
})();
