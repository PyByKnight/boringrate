const fs=require("fs"),{JSDOM}=require("jsdom");
function load(url){
  const errs=[];
  const dom=new JSDOM(fs.readFileSync("index.html","utf8"),{runScripts:"dangerously",url,
    beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.matchMedia=w.matchMedia||function(){return{matches:false,addEventListener(){},addListener(){}}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
  dom.window.onerror=e=>errs.push(String(e));
  return {dom,errs};
}
function topRows(d){
  return [...d.querySelectorAll("[class*=rank-row]")].slice(0,3).map(r=>{
    const n=r.querySelector("[class*=name],[class*=carrier]"); return n?n.textContent.trim().split("\n")[0]:"?";
  });
}
const results={};
const cases=["", "&sit=accident","&sit=sr22","&sit=young","&sit=senior"];
let i=0;
(function run(){
  if(i>=cases.length){
    console.log(JSON.stringify(results,null,0));
    process.exit(0);
  }
  const c=cases[i++];
  const {dom,errs}=load("https://boringrate.com/?zip=30301"+c);
  setTimeout(()=>{
    const d=dom.window.document;
    results[c||"baseline"]={errs:errs.length,top3:topRows(d)};
    run();
  },250);
})();
