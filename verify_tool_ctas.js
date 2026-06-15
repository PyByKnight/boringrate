const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
const files=["article/state/texas.html","article/carrier/geico.html","article/metro/houston.html",
 "renters/state/colorado.html","home/state/florida.html","home/carrier/usaa.html"];
for(const f of files){
 const dom=new JSDOM(fs.readFileSync(f,"utf8"),{runScripts:"dangerously",url:"https://boringrate.com/"+f,
  beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
 const d=dom.window.document;dom.window.onerror=e=>errs.push(f+": "+e);
 const tiles=d.querySelectorAll(".tooltiles .tile").length;
 const cov=d.querySelector('.tile .tbtn.secondary');
 const hasZip=!!(d.getElementById("embedZipForm")&&d.getElementById("embedZipInput"));
 const covText=cov?cov.textContent.trim():"(none)";
 console.log(f.split("/").slice(-2).join("/"),"| tiles:",tiles,"| zipbox:",hasZip,"| cov:",cov&&cov.getAttribute("href"),"|",covText);
}
setTimeout(()=>{console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);},400);
