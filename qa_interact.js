// Interaction QA — submits a ZIP on each of the three tool pages and asserts that
// results actually render with no uncaught error.
//
// WHY THIS EXISTS: qa_sweep.js only LOADS pages, so it cannot catch a break in the
// post-search render path. Removing the Supabase integration left
// `document.getElementById("emailSection").style.display` on a deleted node in
// renters/ and home/ — a TypeError that fired on every search while qa_sweep stayed
// green at 614/0. Run this alongside qa_sweep after touching tool JS.
//
//   node qa_interact.js
const fs=require("fs"),{JSDOM,VirtualConsole}=require("jsdom");
const tests=[["index.html","30303"],["renters/index.html","30303"],["home/index.html","30303"]];
(async()=>{
for(const [f,zip] of tests){
  const errs=[];
  const vc=new VirtualConsole();
  vc.on("jsdomError",e=>errs.push(String(e.message||e).split("\n")[0]));
  const dom=new JSDOM(fs.readFileSync(f,"utf8"),{runScripts:"dangerously",pretendToBeVisual:true,virtualConsole:vc,url:"https://boringrate.com/"+f});
  const w=dom.window;
  w.Element.prototype.scrollIntoView=function(){};
  w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};
  await new Promise(r=>setTimeout(r,400));
  const inp=w.document.getElementById("zipInput");
  if(!inp){console.log(f.padEnd(20),"NO #zipInput");continue;}
  inp.value=zip;
  const form=inp.closest("form");
  const before=errs.length;
  if(form) form.dispatchEvent(new w.Event("submit",{bubbles:true,cancelable:true}));
  await new Promise(r=>setTimeout(r,800));
  const txt=w.document.body.textContent;
  const hasPrice=/\$\d{3,}/.test(txt);
  const cards=w.document.querySelectorAll('[class*="rank"],[class*="card"]').length;
  console.log(f.padEnd(20),"errs:",errs.length-before,"| $ prices rendered:",hasPrice,"| elements:",cards);
  errs.slice(before,before+4).forEach(e=>console.log("    !",e));
  w.close();
}
})();
