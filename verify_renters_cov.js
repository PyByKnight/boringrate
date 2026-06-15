const fs = require("fs");
const { JSDOM } = require("jsdom");
const html = fs.readFileSync("renters/coverage.html", "utf8");
const errors = [];
const dom = new JSDOM(html, { runScripts: "dangerously", url: "https://boringrate.com/renters/coverage.html?zip=33101" });
const w = dom.window, d = w.document;
w.onerror = (e) => errors.push(String(e));
setTimeout(() => {
  const cards = d.querySelectorAll(".cov-card");
  const total = d.getElementById("summaryTotal").textContent;
  const badge = d.getElementById("zipStateBadge").textContent;
  console.log("JS errors:", errors.length ? errors : "NONE");
  console.log("cards rendered:", cards.length);
  console.log("ZIP 33101 badge:", badge);
  console.log("summary total:", total);
  console.log("sticky:", d.getElementById("stickyAmount").textContent, "/", d.getElementById("stickyDelta").textContent);
  console.log("cta href:", d.getElementById("ctaBtn").href);
  console.log("cta summary:", d.getElementById("ctaSelectionsSummary").textContent);
  // simulate slider change
  const ps = d.getElementById("propSlider"); ps.value = "8"; ps.dispatchEvent(new w.Event("input"));
  console.log("after prop->150k:", d.getElementById("summaryTotal").textContent, "| propDisplay", d.getElementById("propDisplay").textContent);
  // toggle ACV
  const tgl = d.querySelector('[data-tgl="rcv"]'); tgl.dispatchEvent(new w.MouseEvent("click", {bubbles:true}));
  console.log("after RCV off:", d.getElementById("summaryTotal").textContent);
  // liability option
  const lp = d.querySelector('.pill[data-cov="liability"][data-i="2"]'); lp.dispatchEvent(new w.MouseEvent("click", {bubbles:true}));
  console.log("after liab $500k:", d.getElementById("summaryTotal").textContent);
  process.exit(errors.length ? 1 : 0);
}, 300);
