const fs=require("fs"),{JSDOM}=require("jsdom");
const html=fs.readFileSync("home/coverage.html","utf8");const errs=[];
const dom=new JSDOM(html,{runScripts:"dangerously",url:"https://boringrate.com/home/coverage.html?zip=33101",
  beforeParse(w){ w.Element.prototype.scrollIntoView=function(){}; w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})}; }});
const w=dom.window,d=w.document;w.onerror=e=>errs.push(String(e));
setTimeout(()=>{
 const cards=d.querySelectorAll(".cov-card");
 console.log("JS errors:",errs.length?errs:"NONE");
 console.log("cards:",cards.length);
 console.log("ZIP 33101 badge:",d.getElementById("zipStateBadge").textContent);
 console.log("total:",d.getElementById("summaryTotal").textContent,"| sticky:",d.getElementById("stickyAmount").textContent,d.getElementById("stickyDelta").textContent);
 console.log("cta href:",d.getElementById("ctaBtn").href);
 console.log("cta summary:",d.getElementById("ctaSelectionsSummary").textContent);
 const ds=d.getElementById("dwellSlider"); ds.value="6"; ds.dispatchEvent(new w.Event("input"));
 console.log("after dwell->750k:",d.getElementById("summaryTotal").textContent,"| display",d.getElementById("dwellDisplay").textContent);
 const dd=d.querySelector('.pill[data-q="deductible"][data-v="5000"]'); dd.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 console.log("after ded $5k:",d.getElementById("summaryTotal").textContent);
 const wb=d.querySelector('[data-tgl="waterBackup"]'); wb.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 console.log("after water off:",d.getElementById("summaryTotal").textContent);
 const lp=d.querySelector('.pill[data-cov="liability"][data-i="2"]'); lp.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 console.log("after liab 500k:",d.getElementById("summaryTotal").textContent);
 process.exit(errs.length?1:0);
},300);
