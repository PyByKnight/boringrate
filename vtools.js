const fs=require("fs"),{JSDOM}=require("jsdom");const errs=[];
const files=["index.html","renters/index.html","home/index.html","coverage.html","renters/coverage.html","home/coverage.html"];
let i=0;(function n(){if(i>=files.length){console.log("JS errors:",errs.length?errs:"NONE");process.exit(errs.length?1:0);return;}
const f=files[i++];
const dom=new JSDOM(fs.readFileSync(f,"utf8"),{runScripts:"dangerously",url:"https://boringrate.com/"+f,
 beforeParse(w){w.Element.prototype.scrollIntoView=function(){};w.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};w.matchMedia=w.matchMedia||function(){return{matches:false,addEventListener(){},addListener(){}}};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({})})})};}});
dom.window.onerror=e=>errs.push(f+": "+e);
setTimeout(()=>{console.log(f,"ok");n();},120);})();
