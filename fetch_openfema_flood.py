#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-state flood facts from FEMA's OpenFEMA API -> flood_by_state.json (small, committed).

Primary-source data for the home + renters state pages (memory boringrate-unique-content-rule):
standard home and renters policies exclude flood, and these numbers show what that gap looks
like in each state.

  NfipResidentialPenetrationRates (v1, county level, ~3.2K rows): residential NFIP policies in
      force, residential structures, penetration overall + inside the high-risk zone (SFHA),
      and the county with the most policies.
  NfipClaims (v3, ~2.7M rows): YEARS window only, streamed page by page with a 6-field $select;
      only per-state totals are kept in memory (nothing large is written to disk). Per state:
      claims, total paid (building + contents), contents paid, worst year, and the named flood
      event with the most claims.

No auth, no personal data sent. Re-run when FEMA refreshes (claims ~quarterly):
    python3 fetch_openfema_flood.py            # ~5-15 min, mostly the claims stream
"""
import json, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from datetime import date

API = "https://www.fema.gov/api/open"
YEARS = (2016, 2025)                 # ten full years of loss; the claims feed lags ~quarter
PAGE = 10000
STATE_CODES = {  # penetration rows carry full state names
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}


def get(path, **params):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params, safe="$,'() ")
    url = url.replace(" ", "%20")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "rate-research-script"}),
                                        timeout=120) as r:
                return json.load(r)
        except Exception as e:  # transient 5xx / timeouts: back off and retry
            if attempt == 4:
                raise
            time.sleep(5 * (attempt + 1))


def penetration():
    out = defaultdict(lambda: {"res_policies": 0, "res_structures": 0, "sfha_policies": 0,
                               "sfha_structures": 0, "top_county": None})
    skip = 0
    while True:
        d = get("v1/NfipResidentialPenetrationRates", **{"$top": 1000, "$skip": skip})
        rows = d["NfipResidentialPenetrationRates"]
        for r in rows:
            st = STATE_CODES.get(r["state"])
            if not st:
                continue
            o = out[st]
            o["res_policies"] += r.get("resContractsInForce") or 0
            o["res_structures"] += r.get("totalResStructures") or 0
            o["sfha_policies"] += r.get("resContractsInForceSfha") or 0
            o["sfha_structures"] += r.get("totalResStructuresSfha") or 0
            n = r.get("resContractsInForce") or 0
            if not o["top_county"] or n > o["top_county"][1]:
                o["top_county"] = (r["county"], n)
            o["as_of"] = (r.get("asOfDate") or "")[:10]
        if len(rows) < 1000:
            break
        skip += 1000
    return out


def claims():
    agg = defaultdict(lambda: {"claims": 0, "paid": 0.0, "contents_paid": 0.0,
                               "by_year": Counter(), "by_year_paid": Counter(), "events": Counter()})
    flt = f"yearOfLoss ge {YEARS[0]} and yearOfLoss le {YEARS[1]}"
    total = get("v3/NfipClaims", **{"$filter": flt, "$top": 1, "$count": "true", "$select": "id"})["metadata"]["count"]
    skip, seen = 0, 0
    while skip < total:
        d = get("v3/NfipClaims", **{"$filter": flt, "$top": PAGE, "$skip": skip, "$orderby": "id",
                                   "$select": "state,yearOfLoss,amountPaidOnBuildingClaim,amountPaidOnContentsClaim,floodEvent,id"})
        rows = d["NfipClaims"]
        if not rows:
            break
        for r in rows:
            st = r.get("state")
            if not st:
                continue
            a = agg[st]
            b = r.get("amountPaidOnBuildingClaim") or 0
            c = r.get("amountPaidOnContentsClaim") or 0
            a["claims"] += 1
            a["paid"] += b + c
            a["contents_paid"] += c
            a["by_year"][r["yearOfLoss"]] += 1
            a["by_year_paid"][r["yearOfLoss"]] += b + c
            ev = (r.get("floodEvent") or "").strip()
            if ev and ev.lower() not in ("flooding", "flood", "unknown", "other"):
                a["events"][ev] += 1
        seen += len(rows)
        skip += PAGE
        print(f"  claims {seen:,}/{total:,}", flush=True)
    return agg, total


def main():
    pen = penetration()
    print(f"penetration: {len(pen)} states")
    agg, total = claims()
    states = {}
    for st in sorted(set(pen) | set(agg)):
        p, a = pen.get(st), agg.get(st)
        row = {}
        if p:
            row.update({"res_policies": p["res_policies"], "res_structures": p["res_structures"],
                        "penetration_pct": round(100 * p["res_policies"] / p["res_structures"], 2) if p["res_structures"] else None,
                        "sfha_penetration_pct": round(100 * p["sfha_policies"] / p["sfha_structures"], 1) if p["sfha_structures"] else None,
                        "top_county": p["top_county"][0] if p["top_county"] else None,
                        "top_county_policies": p["top_county"][1] if p["top_county"] else None,
                        "penetration_as_of": p.get("as_of")})
        if a:
            wy = max(a["by_year"], key=a["by_year"].get)
            ev = a["events"].most_common(1)
            row.update({"claims": a["claims"], "paid": round(a["paid"]), "contents_paid": round(a["contents_paid"]),
                        "avg_paid": round(a["paid"] / a["claims"]) if a["claims"] else None,
                        "worst_year": wy, "worst_year_claims": a["by_year"][wy],
                        "worst_year_paid": round(a["by_year_paid"][wy]),
                        "top_event": ev[0][0] if ev else None, "top_event_claims": ev[0][1] if ev else None})
        states[st] = row
    json.dump({"_meta": {"source": "FEMA OpenFEMA: NfipResidentialPenetrationRates v1 + NfipClaims v3",
                         "source_url": "https://www.fema.gov/about/openfema/data-sets",
                         "claims_years": list(YEARS), "claims_rows": total, "fetched": date.today().isoformat(),
                         "note": "paid = amountPaidOnBuildingClaim + amountPaidOnContentsClaim, nominal dollars"},
               "states": states}, open("flood_by_state.json", "w"), indent=1)
    print(f"wrote flood_by_state.json ({len(states)} states, {total:,} claims)")


if __name__ == "__main__":
    main()
