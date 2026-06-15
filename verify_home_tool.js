const fs=require("fs"),{JSDOM}=require("jsdom");
const html=fs.readFileSync("home/index.html","utf8");const errs=[];
const dom=new JSDOM(html,{runScripts:"dangerously",url:"https://boringrate.com/home/index.html",
  beforeParse(w){ w.Element.prototype.scrollIntoView=function(){};w.HTMLElement.prototype.scrollIntoView=function(){};w.supabase={createClient:()=>({auth:{onAuthStateChange(){},getSession:async()=>({data:{session:null}})},from:()=>({insert:async()=>({}),select:()=>({eq:()=>({})})})})}; }});
const w=dom.window,d=w.document;w.onerror=e=>errs.push(String(e));
setTimeout(()=>{
 const zi=d.getElementById("zipInput");zi.value="33101";
 const f=zi.closest("form");
 if(f) f.dispatchEvent(new w.Event("submit",{bubbles:true,cancelable:true}));
 setTimeout(()=>{
  const rows=d.querySelectorAll("[class*=rank-row], .carrier-row, .result-row");
  console.log("JS errors:",errs.length?errs:"NONE");
  console.log("rows after ZIP submit:",rows.length);
  console.log("mentions Florida:", /Florida/.test(d.body.textContent));
  process.exit(errs.length?1:0);
 },150);
},200);
