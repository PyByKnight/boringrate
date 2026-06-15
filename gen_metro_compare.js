// Enrich auto metro pages with a genuinely metro-specific, real-data section:
// "How <Metro> compares to other <State> metros" — a ranked table of the state's
// tracked metros (this one highlighted, siblings linked). Differentiates each metro
// from its same-state siblings and strengthens internal linking. Idempotent (markers).
// Only applied to metros whose state has 2+ tracked metros.
const fs = require("fs");
const idx = fs.readFileSync("index.html", "utf8");
function grab(name, o, c){const i=idx.indexOf(name);const s=idx.indexOf(o,i);let d=0,j=s;for(;j<idx.length;j++){if(idx[j]===o)d++;else if(idx[j]===c){d--;if(!d){j++;break;}}}return idx.slice(s,j);}
const SD=eval("("+grab("const STATE_DATA","{","}")+")");
const ADJ=eval("("+grab("const STATE_CARRIER_ADJ","{","}")+")");
const CAR=eval("("+grab("const CARRIERS","[","]")+")");
const MADJ=eval("("+grab("const METRO_CARRIER_ADJ","{","}")+")");
const MN=eval("("+grab("const METRO_NAMES","{","}")+")");
const ZM=eval("("+grab("const ZIP_PREFIX_METRO","{","}")+")");
const Z3=eval("("+grab("const ZIP3_TO_STATE","{","}")+")");

const METRO_STATE={};
for(const p in ZM){const m=ZM[p];if(!METRO_STATE[m]){const st=Z3[p]||Z3[p.slice(0,2)];if(st)METRO_STATE[m]=st;}}
const SLUG_OVERRIDE={tam:"tampa",sjv:"san-jose",nfk:"norfolk",csc:"columbia-sc",gso:"greensboro",wil:"wilmington-de",mnh:"manchester-nh",bvt:"burlington-vt",riv:"riverside-inland-empire"};
const START="<!-- metro-compare-start -->", END="<!-- metro-compare-end -->";

function clean(key){return (MN[key]||key).replace(/ metro$/i,"").replace(/ \/ .*$/,"");}
function slugOf(key){
  return SLUG_OVERRIDE[key] || clean(key).toLowerCase().replace(/[–—]/g,"-").replace(/[.,/]/g,"").replace(/ & /g,"-").replace(/\s+/g,"-");
}
function metroAvg(key){
  const st=METRO_STATE[key]; if(!st||!SD[st])return null;
  const madj=MADJ[key]||{}; const mult=Object.values(madj);
  const mean=mult.length?mult.reduce((a,b)=>a+b,0)/mult.length:1;
  return Math.round(SD[st].avg*mean);
}

// group metro keys by state
const byState={};
for(const key in MADJ){const st=METRO_STATE[key];if(!st)continue;(byState[st]=byState[st]||[]).push(key);}

function ordinal(n){const s=["th","st","nd","rd"],v=n%100;return n+(s[(v-20)%10]||s[v]||s[0]);}

function block(key){
  const st=METRO_STATE[key]; const sibs=byState[st];
  if(!sibs||sibs.length<2)return null;
  const stName=SD[st].name; const stAvg=SD[st].avg;
  const ranked=sibs.map(k=>({key:k,name:clean(k),slug:slugOf(k),avg:metroAvg(k)}))
                   .filter(m=>m.avg).sort((a,b)=>a.avg-b.avg);
  const meIdx=ranked.findIndex(m=>m.key===key); if(meIdx<0)return null;
  const me=ranked[meIdx];
  const pos=ordinal(meIdx+1);
  const vsState=Math.round((me.avg/stAvg-1)*100);
  const vsTxt=vsState<=-1?`about ${Math.abs(vsState)}% below`:vsState>=1?`about ${vsState}% above`:"right around";
  const cheapest=ranked[0], priciest=ranked[ranked.length-1];
  const rows=ranked.map((m,i)=>{
    const hi=m.key===key;
    const nameCell=hi?`<strong>${m.name}</strong> <span style="font-family:var(--mono);font-size:11px;color:var(--accent);">you are here</span>`
                     :`<a href="/article/metro/${m.slug}.html" style="color:var(--accent);text-decoration:none;border-bottom:1px solid var(--rule);">${m.name}</a>`;
    return `<tr style="border-bottom:1px solid var(--rule);${hi?'background:var(--paper-deep);':''}">`
      +`<td style="padding:8px 6px;color:var(--ink-mute);">${i+1}</td>`
      +`<td style="padding:8px 6px;">${nameCell}</td>`
      +`<td style="padding:8px 6px;">$${m.avg.toLocaleString()}/yr</td></tr>`;
  }).join("");
  return `${START}
<h2>How ${me.name} compares to other ${stName} metros</h2>
<p>Among the ${ranked.length} ${stName} metros we track, <strong>${me.name} is the ${pos}-cheapest</strong> for full coverage &mdash; ${vsTxt} the statewide average of $${stAvg.toLocaleString()}/yr. ${stName} metro rates run from ${cheapest.name} ($${cheapest.avg.toLocaleString()}/yr) to ${priciest.name} ($${priciest.avg.toLocaleString()}/yr), so where you live inside the state moves your premium meaningfully.</p>
<table style="width:100%;border-collapse:collapse;font-size:16px;margin:16px 0;max-width:520px;">
<thead><tr style="text-align:left;border-bottom:2px solid var(--ink);font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;"><th style="padding:8px 6px;">#</th><th style="padding:8px 6px;">${stName} metro</th><th style="padding:8px 6px;">Avg. full coverage</th></tr></thead>
<tbody>${rows}</tbody></table>
<p style="font-size:14px;color:var(--ink-soft);max-width:660px;">These are directional metro averages from the BoringRate model &mdash; your own rate depends on your ZIP, vehicle, and profile. <a class="ca-link" href="/article/state/${stName.toLowerCase().replace(/\./g,"").replace(/\s+/g,"-")}.html">See full ${stName} rankings &rarr;</a></p>
${END}`;
}

let n=0, skip=0;
for(const key in MADJ){
  const slug=slugOf(key); const path=`article/metro/${slug}.html`;
  if(!fs.existsSync(path)){skip++;continue;}
  const blk=block(key);
  let h=fs.readFileSync(path,"utf8");
  h=h.replace(new RegExp("\\s*"+START+"[\\s\\S]*?"+END),"");   // strip prior (idempotent)
  if(!blk){continue;}                                            // single-metro state: nothing to add
  const anchorRe=/<h2>How to find the cheapest carrier in /;
  if(!anchorRe.test(h)){skip++;continue;}
  h=h.replace(anchorRe, blk+"\n    <h2>How to find the cheapest carrier in ");
  fs.writeFileSync(path,h); n++;
}
console.log("enriched",n,"metro pages | skipped",skip);
