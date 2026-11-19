#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-state severe-weather facts from NOAA NCEI -> disasters_by_state.json (small, committed).

Two primary sources, both public, no auth:
  1. Billion-Dollar Weather and Climate Disasters, per-state event lists
     (ncei.noaa.gov/access/billions/events-<ST>-<Y0>-<Y1>.csv). NOAA retired the product in 2025;
     the archive ends at 2024. Event costs cover the WHOLE multi-state event, so only COUNTS by
     type are used per state - never a cost attributed to one state.
  2. Storm Events Database detail files (ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/),
     current. Each yearly .csv.gz is streamed and aggregated in memory (nothing large on disk):
     tornadoes, large-hail reports (>= 2.0 in), and reported property damage by event type.

    python3 fetch_noaa_disasters.py        # ~5-10 min; re-run yearly (Storm Events updates monthly)
"""
import csv, gzip, io, json, re, time, urllib.request
from collections import Counter, defaultdict
from datetime import date

BD_YEARS = (2015, 2024)               # billion-dollar archive ends 2024
SE_YEARS = (2016, 2025)               # ten full storm-event years
SE_DIR = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
UA = {"User-Agent": "rate-research-script"}
STATES = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY",
          "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
          "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
SE_NAME = {"DISTRICT OF COLUMBIA": "DC"}   # Storm Events uses upper-case full names


def fetch(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(5 * (i + 1))


def billion_dollar():
    out = {}
    for st in STATES:
        raw = fetch(f"https://www.ncei.noaa.gov/access/billions/events-{st}-{BD_YEARS[0]}-{BD_YEARS[1]}.csv")
        lines = raw.decode("utf-8", "replace").splitlines()
        hdr = next(i for i, l in enumerate(lines) if l.startswith("Name,Disaster"))
        rows = list(csv.DictReader(lines[hdr:]))
        types = Counter(r["Disaster"] for r in rows)
        by_year = Counter(r["Begin Date"][:4] for r in rows)
        out[st] = {"events": len(rows), "by_type": dict(types.most_common()),
                   "busiest_year": int(max(by_year, key=by_year.get)) if by_year else None,
                   "busiest_year_events": max(by_year.values()) if by_year else 0}
        time.sleep(0.3)
    return out


def _dmg(s):
    m = re.match(r"^\s*([\d.]+)\s*([KMB]?)\s*$", s or "")
    if not m:
        return 0.0
    return float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2)]


def main():
    from state_compare import model
    states, _, _ = model("home")
    # Storm Events names states in full upper case; map them via the tool's own state list
    se_map = {v[0].upper(): k for k, v in states.items()}
    se_map.update(SE_NAME)
    bd = billion_dollar()
    print(f"billion-dollar: {len(bd)} states")
    se, years = storm_events(se_map)
    out = {}
    for st in STATES:
        row = {}
        if st in bd:
            row.update({"bd_events": bd[st]["events"], "bd_by_type": bd[st]["by_type"],
                        "bd_busiest_year": bd[st]["busiest_year"], "bd_busiest_year_events": bd[st]["busiest_year_events"]})
        if st in se:
            a = se[st]
            top = a["damage"].most_common(1)
            row.update({"tornadoes": a["tornadoes"], "big_hail": a["big_hail"],
                        "property_damage": round(sum(a["damage"].values())),
                        "top_damage_type": top[0][0] if top and top[0][1] > 0 else None,
                        "top_damage": round(top[0][1]) if top else 0})
        out[st] = row
    json.dump({"_meta": {"billion_dollar_source": "NOAA NCEI Billion-Dollar Weather and Climate Disasters (archive, retired 2025)",
                         "billion_dollar_url": "https://www.ncei.noaa.gov/access/billions/",
                         "billion_dollar_years": list(BD_YEARS),
                         "storm_events_source": "NOAA NCEI Storm Events Database",
                         "storm_events_url": "https://www.ncei.noaa.gov/stormevents/",
                         "storm_events_years": [years[0], years[-1]] if years else None,
                         "fetched": date.today().isoformat(),
                         "note": "bd_* are counts of billion-dollar events that affected the state (costs are multi-state, "
                                 "not used). property_damage = sum of Storm Events DAMAGE_PROPERTY estimates, nominal $."},
               "states": out}, open("disasters_by_state.json", "w"), indent=1)
    print(f"wrote disasters_by_state.json ({len(out)} states)")


def storm_events(name_map):
    """Stream each year's details file; aggregate per state in memory."""
    listing = fetch(SE_DIR).decode()
    names = {}
    for f in re.findall(r'StormEvents_details-ftp_v1\.0_d(\d{4})_c(\d{8})\.csv\.gz', listing):
        y, c = int(f[0]), f[1]
        if SE_YEARS[0] <= y <= SE_YEARS[1] and (y not in names or c > names[y][1]):
            names[y] = (f"StormEvents_details-ftp_v1.0_d{y}_c{c}.csv.gz", c)
    agg = defaultdict(lambda: {"tornadoes": 0, "big_hail": 0, "damage": Counter()})
    for y in sorted(names):
        raw = fetch(SE_DIR + names[y][0])            # gz bytes only; decompressed as a stream
        for r in csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw)), encoding="latin-1")):
            code = name_map.get(r["STATE"].strip().upper())
            if not code:
                continue
            a = agg[code]
            et = r["EVENT_TYPE"].strip()
            if et == "Tornado":
                a["tornadoes"] += 1
            elif et == "Hail":
                try:
                    if float(r["MAGNITUDE"] or 0) >= 2.0:
                        a["big_hail"] += 1
                except ValueError:
                    pass
            a["damage"][et] += _dmg(r["DAMAGE_PROPERTY"])
        print(f"  storm events {y} done", flush=True)
        del raw
    return agg, sorted(names)


if __name__ == "__main__":
    main()
