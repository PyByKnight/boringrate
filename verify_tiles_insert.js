const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
const files=["article/compare/geico-vs-state-farm.html","article/compare/index.html","article/coverage-guide.html","article/index.html","article/market-share.html","article/state-rankings.html","article/rate-changes/texas.html"];
for(const f of files){
 const dom=new JSDOM(fs.readFileSync(f,"utf8"),{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;dom.window.onerror=e=>errs.push(f+": "+e);
 const tiles=d.querySelectorAll(".tooltiles .tile").length;
 const cov=d.querySelector('.tile .tbtn.secondary');
 const zipform=d.querySelector('.tile-zipform');
 const hasOnsubmit=zipform&&zipform.getAttribute("onsubmit")&&zipform.getAttribute("onsubmit").includes("/?zip=");
 console.log(f.replace('article/',''),"| tiles:",tiles,"| inlineZip:",!!hasOnsubmit,"| cov:",cov&&cov.getAttribute("href"));
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},400);
