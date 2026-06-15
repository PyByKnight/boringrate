const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
for(const f of ["article/state/texas.html","home/state/florida.html","home/carrier/usaa.html","index.html"]){
 let html;try{html=fs.readFileSync(f,"utf8")}catch(e){continue}
 const dom=new JSDOM(html,{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;dom.window.onerror=e=>errs.push(f+": "+e);
 const hs=d.querySelectorAll('#navMega a[href^="/home/state/"]').length;
 const hc=d.querySelectorAll('#navMega a[href^="/home/carrier/"]').length;
 console.log(f,"| nav home-state links:",hs,"| nav home-carrier links:",hc);
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},500);
