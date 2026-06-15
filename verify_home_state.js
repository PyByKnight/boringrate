const fs=require("fs"),{JSDOM}=require("jsdom");
const errs=[];
for(const f of ["home/state/florida.html","home/state/colorado.html","home/state/hawaii.html","home/state/oklahoma.html"]){
 const html=fs.readFileSync(f,"utf8");
 const dom=new JSDOM(html,{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;dom.window.onerror=e=>errs.push(f+": "+e);
 const rankRows=d.querySelectorAll("table tbody tr").length;
 const h1=d.querySelector("h1.article-title").textContent.slice(0,60);
 const ldjson=d.querySelectorAll('script[type="application/ld+json"]').length;
 const homeLinks=d.querySelectorAll('a[href^="/home/"]').length;
 console.log(f.split("/").pop(),"| rankRows:",rankRows,"| ld+json:",ldjson,"| /home/ links:",homeLinks,"|",h1);
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},400);
