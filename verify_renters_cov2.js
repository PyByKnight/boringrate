const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
const dom=new JSDOM(fs.readFileSync("renters/coverage.html","utf8"),{runScripts:"dangerously",url:"https://boringrate.com/renters/coverage.html?zip=80202",
 beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.matchMedia=w.matchMedia||function(){return{matches:false,addEventListener(){},addListener(){}}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
const w=dom.window,d=w.document;w.onerror=e=>errs.push(String(e));
setTimeout(()=>{
 function chip(name){const c=[...d.querySelectorAll('.cov-card')].find(x=>x.textContent.includes(name));return c?c.querySelector('.delta-badge').textContent:'?';}
 const cards=d.querySelectorAll(".cov-card").length, total=d.getElementById("summaryTotal").textContent;
 const rcvBefore=chip("Replacement Cost");
 const rcv=d.querySelector('[data-tgl="rcv"]'); rcv.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 const rcvAfter=chip("Replacement Cost"), totalAfter=d.getElementById("summaryTotal").textContent;
 const exp=d.querySelector('[data-exp="personal"]'),body=d.getElementById("exp-personal");
 const bD=body.style.display; exp.dispatchEvent(new w.MouseEvent("click",{bubbles:true})); const aD=body.style.display;
 const lou=d.querySelector('.pill[data-cov="louPct"][data-i="0"]'); lou.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 console.log("cards:",cards,"| total:",total);
 console.log("RCV chip on:",rcvBefore,"-> off:",rcvAfter,"| total",total,"->",totalAfter);
 console.log("personal expand:",bD,"->",aD,"| LoU 20% chip:",chip("Loss of Use"));
 console.log("sticky zip:",JSON.stringify(d.getElementById("stickyZip").value),"| sticky href:",d.getElementById("stickyCompareLink").href);
 console.log("tooltips:",d.querySelectorAll(".lbl-i").length,"| primer removed:",d.querySelectorAll(".guide-section").length===0);
 console.log("JS errors:",errs.length?errs:"NONE");
 process.exit(errs.length?1:0);
},300);
