const fs = require("fs");
const { JSDOM } = require("jsdom");
const pages = ["article/metro/colorado-springs.html", "article/metro/akron.html",
  "article/metro/chattanooga.html", "article/metro/grand-rapids.html", "article/metro/atlanta.html"];

function check(p) {
  return new Promise(resolve => {
    const errs = [];
    const dom = new JSDOM(fs.readFileSync(p, "utf8"), {
      runScripts: "dangerously", pretendToBeVisual: true, url: "https://boringrate.com/" + p,
      beforeParse(w) {
        w.IntersectionObserver = class { observe(){} disconnect(){} unobserve(){} };
        w.matchMedia = () => ({ matches:false, addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
        w.HTMLElement.prototype.scrollIntoView = () => {};
        w.supabase = { createClient: () => ({ auth:{ onAuthStateChange(){}, getSession: async()=>({data:{session:null}}) }, from:()=>({ insert:async()=>({}), select:()=>({eq:()=>({})}) }) }) };
      },
    });
    const w = dom.window;
    w.addEventListener("error", e => errs.push((e.error && e.error.message) || e.message));
    w.console.error = (...a) => errs.push("console.error:" + a.join(" "));
    setTimeout(() => {
      const d = w.document;
      const sticky = d.getElementById("articleStickyCta");
      console.log(p.split("/").pop().padEnd(22) +
        " errs=" + errs.length +
        " | sticky=\"" + (sticky ? sticky.getAttribute("aria-label") : "none") + "\"" +
        " | embedForm=" + !!d.getElementById("embedZipForm") +
        " | callouts=" + d.querySelectorAll(".callout").length +
        " | h1=\"" + (d.querySelector("h1") ? d.querySelector("h1").textContent.slice(0, 40) : "?") + "\"");
      if (errs.length) errs.forEach(e => console.log("    ! " + e));
      resolve();
    }, 250);
  });
}
(async () => { for (const p of pages) await check(p); })();
