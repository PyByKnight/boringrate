const fs=require("fs"),{JSDOM}=require("jsdom");
const errs=[];
for(const f of ["home/carrier/usaa.html","home/carrier/state-farm.html","home/carrier/allstate.html","home/carrier/erie.html"]){
 const html=fs.readFileSync(f,"utf8");
 const dom=new JSDOM(html,{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;dom.window.onerror=e=>errs.push(f+": "+e);
 const h1=d.querySelector("h1.article-title").textContent.slice(0,55);
 const pros=d.querySelectorAll(".pros-cons .pros li").length, cons=d.querySelectorAll(".pros-cons .cons li").length;
 const ld=d.querySelectorAll('script[type="application/ld+json"]').length;
 const stateLinks=d.querySelectorAll('.internal-links a[href^="/home/state/"]').length;
 console.log(f.split("/").pop(),"| pros/cons:",pros+"/"+cons,"| ld:",ld,"| stateLinks:",stateLinks,"|",h1);
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},400);
