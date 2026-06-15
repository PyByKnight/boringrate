const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
for(const f of ["article/cheapest-car-insurance-young-drivers.html","article/cheapest-car-insurance-after-accident.html","article/cheapest-car-insurance-after-dui.html","article/cheapest-car-insurance-bad-credit.html","article/cheapest-car-insurance-for-seniors.html"]){
 const dom=new JSDOM(fs.readFileSync(f,"utf8"),{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;dom.window.onerror=e=>errs.push(f+": "+e);
 const rows=d.querySelectorAll("table tbody tr").length;
 const cta=d.querySelector('.tile-zipform');
 const sit=cta&&/sit=/.test(cta.getAttribute("onsubmit"));
 console.log(f.replace('article/',''),"| top3 rows:",rows,"| sit-CTA:",!!sit,"| h1:",d.querySelector("h1").textContent.slice(0,40));
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},400);
