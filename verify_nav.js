const fs=require("fs"),{JSDOM}=require("jsdom");
const errs=[];
for(const f of ["article/state/texas.html","article/carrier/geico.html","home/coverage.html","renters/coverage.html"]){
 const html=fs.readFileSync(f,"utf8");
 const dom=new JSDOM(html,{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{constructor(){}observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;
 dom.window.onerror=e=>errs.push(f+": "+e);
 const dd=d.querySelectorAll('#navDdToolsPanel a[href*="coverage"]').length;
 const home=!!d.querySelector('#navDdProductPanel a[href="/home/index.html"]');
 console.log(f,"| tools-dropdown coverage links:",dd,"| home in product dd:",home);
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},400);
