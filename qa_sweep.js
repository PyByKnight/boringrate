const fs = require("fs"), path = require("path"), { JSDOM, VirtualConsole } = require("jsdom");
function walk(d, acc) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    if (e.name === ".git" || e.name === "node_modules") continue;
    const fp = path.join(d, e.name);
    if (e.isDirectory()) walk(fp, acc);
    else if (e.name.endsWith(".html") && e.name !== "cta-preview.html") acc.push(fp);
  }
  return acc;
}
function stub(w) {
  w.Element.prototype.scrollIntoView = function () {};
  w.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
  w.matchMedia = w.matchMedia || function () { return { matches: false, addEventListener() {}, addListener() {} }; };
  const sb = { auth: { onAuthStateChange() {}, getSession: async () => ({ data: { session: null } }) }, from: () => ({ insert: async () => ({}), select: () => ({ eq: () => ({}) }) }) };
  w.supabase = { createClient: () => sb };
}
const files = walk(".", []);
const bad = [];
function check(f) {
  return new Promise((res) => {
    const errs = [];
    // jsdom routes uncaught script exceptions to the virtualConsole as "jsdomError",
    // NOT to window.onerror — so capture both or hard ReferenceErrors slip through.
    const vc = new VirtualConsole();
    vc.on("jsdomError", (e) => errs.push(String(e.message || e)));
    try {
      const dom = new JSDOM(fs.readFileSync(f, "utf8"), { runScripts: "dangerously", url: "https://boringrate.com/" + f.slice(2), beforeParse: stub, virtualConsole: vc });
      dom.window.onerror = (e) => errs.push(String(e));
    } catch (e) { errs.push("PARSE:" + e.message); }
    setTimeout(() => { if (errs.length) bad.push([f, errs[0]]); res(); }, 60);
  });
}
(async () => {
  let done = 0;
  for (const f of files) { await check(f); done++; }
  console.log("swept", done, "pages |", bad.length, "with JS errors");
  bad.slice(0, 50).forEach(([f, e]) => console.log("  ", f, "=>", String(e).slice(0, 90)));
  process.exitCode = bad.length ? 1 : 0;  // gate: nonzero if any page threw
})();
