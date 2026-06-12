const fs = require("fs");
const { JSDOM } = require("jsdom");
const pages = fs.readdirSync("article/rate-changes").filter(f => f.endsWith(".html")).map(f => "article/rate-changes/" + f);
function check(p) {
  return new Promise(resolve => {
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
      console.log(p.split("/").pop().padEnd(13) +
        " errs=" + errs.length +
        " tableRows=" + d.querySelectorAll("tbody tr").length +
        " sourceLinks=" + d.querySelectorAll('a[rel*="nofollow"]').length +
        " embedForm=" + !!d.getElementById("embedZipForm"));
      if (errs.length) errs.forEach(e => console.log("   ! " + e));
      resolve();
    }, 250);
  });
}
(async () => { for (const p of pages) await check(p); })();
