#!/usr/bin/env python3
"""Derive recent_filed_activity.json from serff_filings.json — the shared feed for
surfacing PRIMARY-SOURCE filing callouts on carrier/state/tool pages ("what your
carrier actually filed"). Read-only over serff_filings; never touches index.html.
One entry per (state, carrier) = that carrier's most recent MATERIAL filed change
(|overall_pct|>=1), plus a 'flat' flag for carriers on record holding steady."""
import json, collections
d=json.load(open("serff_filings.json"))
rows=[r for r in d["filings"] if r.get("overall_pct") is not None]
def eff(r): return r.get("effective_new") or r.get("effective_renewal") or r.get("disposition_date") or ""
by=collections.defaultdict(list)
for r in rows:
    by[(r["state"], r["carrier"])].append(r)
out=[]
for (st,car),rs in by.items():
    rs.sort(key=eff, reverse=True)
    # exclude segment-only filings (e.g. min-limits) from the headline pick — same rule as the drift engine
    material=[r for r in rs if abs(r["overall_pct"])>=1.0 and not r.get("drift_exclude")]
    pick=material[0] if material else next((r for r in rs if not r.get("drift_exclude")), rs[0])
    out.append({
        "state":st,"carrier":car,
        "pct":pick["overall_pct"],
        "dir":("decrease" if pick["overall_pct"]<0 else "increase" if pick["overall_pct"]>0 else "flat"),
        "flat": not material,
        "effective":eff(pick),
        "tracking":pick["tracking"],
        "url":pick.get("url"),
        "n_filings":len(rs),
    })
out.sort(key=lambda x:(x["state"], -abs(x["pct"])))
res={"_meta":{"purpose":"Per carrier×state most-recent MATERIAL filed change (or flat), derived from serff_filings.json. Feed for primary-source filing callouts on pages. Regenerate after each serff_filings update.","generated":d["_meta"].get("last_updated"),"source":"serff_filings.json"},"activity":out}
json.dump(res,open("recent_filed_activity.json","w"),indent=1)
mv=[x for x in out if not x["flat"]]
print(f"wrote recent_filed_activity.json: {len(out)} carrier×state entries ({len(mv)} with a material move, {len(out)-len(mv)} flat)")
for st in sorted({x["state"] for x in out}):
    ms=[x for x in mv if x["state"]==st]
    label=", ".join("%s %+g%%"%(x["carrier"],x["pct"]) for x in ms[:6])
    print("  %s: %d movers -> %s%s"%(st,len(ms),label," ..." if len(ms)>6 else ""))
