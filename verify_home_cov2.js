const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
const dom=new JSDOM(fs.readFileSync("home/coverage.html","utf8"),{runScripts:"dangerously",url:"https://boringrate.com/home/coverage.html?zip=43004",
 beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.matchMedia=w.matchMedia||function(){return{matches:false,addEventListener(){},addListener(){}}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
const w=dom.window,d=w.document;w.onerror=e=>errs.push(String(e));
setTimeout(()=>{
 const cards=d.querySelectorAll(".cov-card");
 const total=d.getElementById("summaryTotal").textContent;
 // price chip on personal property (RCV) before
 function chip(name){const cs=[...d.querySelectorAll('.cov-card')];const c=cs.find(x=>x.textContent.includes(name));return c?c.querySelector('.delta-badge').textContent:'?';}
 const ppBefore=chip("Personal Property");
 // toggle RCV off
 const rcv=d.querySelector('[data-tgl="contentsRcv"]'); rcv.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 const ppAfter=chip("Personal Property"), totalAfter=d.getElementById("summaryTotal").textContent;
 // inline expand on dwelling
 const exp=d.querySelector('[data-exp="dwelling"]'); const body=d.getElementById("exp-dwelling");
 const beforeDisp=body.style.display; exp.dispatchEvent(new w.MouseEvent("click",{bubbles:true})); const afterDisp=body.style.display;
 // other structures pill 20%
 const os=d.querySelector('.pill[data-cov="osPct"][data-i="1"]'); os.dispatchEvent(new w.MouseEvent("click",{bubbles:true}));
 const osChip=chip("Other Structures"), totalOs=d.getElementById("summaryTotal").textContent;
 // sticky zip synced from ?zip=43004
 const sz=d.getElementById("stickyZip"), bz=d.getElementById("bottomZipInput");
 console.log("cards:",cards.length,"| total:",total);
 console.log("PP chip RCV-on:",ppBefore,"-> RCV-off:",ppAfter,"| total",total,"->",totalAfter);
 console.log("dwelling expand:",beforeDisp,"->",afterDisp);
 console.log("OtherStructures 20% chip:",osChip,"| total ->",totalOs);
 console.log("sticky zip:",JSON.stringify(sz.value),"| bottom zip:",JSON.stringify(bz.value),"| sticky cta href:",d.getElementById("stickyCompareLink").href);
 console.log("tooltips(i):",d.querySelectorAll(".lbl-i").length,"| guide-section removed:",d.querySelectorAll(".guide-section").length===0);
 console.log("JS errors:",errs.length?errs:"NONE");
 process.exit(errs.length?1:0);
},300);
