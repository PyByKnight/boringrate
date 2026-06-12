const fs = require("fs");
const { JSDOM } = require("jsdom");
const pages = ["texas", "new-york", "washington-dc", "california", "florida", "louisiana"].map(s => "article/state/" + s + ".html");
function check(p) {
  return new Promise(res => {
    const errs = [];
    const dom = new JSDOM(fs.readFileSync(p, "utf8"), {
      runScripts: "dangerously", pretendToBeVisual: true, url: "https://boringrate.com/" + p,
      beforeParse(w) {
        w.IntersectionObserver = class { observe() {} disconnect() {} unobserve() {} };
        w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} });
        w.HTMLElement.prototype.scrollIntoView = () => {};
        w.supabase = { createClient: () => ({ auth: { onAuthStateChange() {}, getSession: async () => ({ data: { session: null } }) }, from: () => ({ insert: async () => ({}), select: () => ({ eq: () => ({}) }) }) }) };
      },
    });
    const w = dom.window;
    w.addEventListener("error", e => errs.push((e.error && e.error.message) || e.message));
    w.console.error = (...a) => errs.push("console.error:" + a.join(" "));
    setTimeout(() => {
      const d = w.document;
      console.log(p.split("/").pop().padEnd(18) + " errs=" + errs.length +
        " rankingRows=" + d.querySelectorAll(".article-body tbody tr").length +
        " hasCheapestH2=" + /Cheapest car insurance carriers/.test(d.body.textContent));
      if (errs.length) errs.forEach(e => console.log("  ! " + e));
      res();
    }, 250);
  });
}
(async () => { for (const p of pages) await check(p); })();
