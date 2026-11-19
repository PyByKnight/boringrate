#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'Weather damage in <state>' section for home + renters state pages, from disasters_by_state.json
(NOAA NCEI, fetched by fetch_noaa_disasters.py). Measured counts in place of the hand-written
peril sentence alone (memory boringrate-unique-content-rule). Billion-dollar events are COUNTED
per state, never costed: NOAA's cost figures cover the whole multi-state event.

    block(line, code, name) -> HTML ("" when no data)
    inject(html, line, code, name, before) -> (html, ok)   idempotent
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
START, END = "<!-- disaster-facts-start -->", "<!-- disaster-facts-end -->"
TYPE = {"Severe Storm": ("severe storm", "severe storms"), "Tropical Cyclone": ("hurricane or tropical storm", "hurricanes and tropical storms"),
        "Flooding": ("flood", "floods"), "Drought": ("drought", "droughts"), "Winter Storm": ("winter storm", "winter storms"),
        "Wildfire": ("wildfire", "wildfires"), "Freeze": ("freeze", "freezes")}
DMG = {"Hail": "hail", "Tornado": "tornadoes", "Flash Flood": "flash flooding", "Flood": "flooding",
       "Hurricane (Typhoon)": "hurricanes", "Hurricane": "hurricanes", "Storm Surge/Tide": "storm surge",
       "Thunderstorm Wind": "thunderstorm wind", "High Wind": "high wind", "Wildfire": "wildfire",
       "Winter Storm": "winter storms", "Ice Storm": "ice storms", "Tropical Storm": "tropical storms",
       "Strong Wind": "strong wind", "Coastal Flood": "coastal flooding", "Heavy Rain": "heavy rain",
       "Debris Flow": "debris flows", "Blizzard": "blizzards", "Lightning": "lightning", "Drought": "drought"}
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        p = os.path.join(ROOT, "disasters_by_state.json")
        _DATA = json.load(open(p)) if os.path.exists(p) else {"_meta": {}, "states": {}}
    return _DATA


def _money(x):
    return f"${x / 1e9:.1f} billion" if x >= 1e9 else f"${x / 1e6:.0f} million" if x >= 1e6 else f"${x:,.0f}"


def _n(k, typ):
    one, many = TYPE.get(typ, (typ.lower(), typ.lower()))
    return f"{k} {one if k == 1 else many}"


def block(line, code, name):
    d = data(); m = d["_meta"]; s = d["states"].get(code)
    if not s:
        return ""
    out = []
    if s.get("bd_events"):
        y0, y1 = m.get("billion_dollar_years", [2015, 2024])
        kinds = [_n(k, t) for t, k in list(s["bd_by_type"].items())[:3]]
        kinds_txt = kinds[0] if len(kinds) == 1 else ", ".join(kinds[:-1]) + " and " + kinds[-1]
        t = (f"NOAA counted <strong>{s['bd_events']}</strong> billion-dollar weather disaster{'s' if s['bd_events'] != 1 else ''} that hit {name} "
             f"from {y0} to {y1}: {kinds_txt}")
        if s.get("bd_busiest_year_events", 0) >= 3:
            t += f", with {s['bd_busiest_year_events']} in {s['bd_busiest_year']} alone"
        out.append(t + ".")
    if "tornadoes" in s:
        y0, y1 = m.get("storm_events_years", [2016, 2025])
        bits = []
        if s["tornadoes"]:
            bits.append(f"<strong>{s['tornadoes']:,}</strong> tornado{'es' if s['tornadoes'] != 1 else ''}")
        if s["big_hail"]:
            bits.append(f"{s['big_hail']:,} reports of hail 2 inches or larger")
        if bits:
            out.append(f"NOAA&rsquo;s storm database logged {' and '.join(bits)} in {name} from {y0} to {y1}.")
        if s.get("top_damage_type") and s.get("top_damage", 0) >= 1e7:
            out.append(f"Of the property damage it recorded there, the largest share came from "
                       f"{DMG.get(s['top_damage_type'], s['top_damage_type'].lower())} ({_money(s['top_damage'])}).")
    if not out:
        return ""
    return (f"{START}\n    <h2>Weather damage in {name}</h2>\n    <p>" + " ".join(out) + "</p>\n"
            f'    <p style="font-size:13px;color:var(--ink-mute);">Source: NOAA NCEI Billion-Dollar Disasters archive '
            f'and Storm Events Database.</p>\n    {END}')


def inject(html, line, code, name, before):
    html = re.sub(r"\s*" + re.escape(START) + r"[\s\S]*?" + re.escape(END), "", html)
    blk = block(line, code, name)
    if not blk or before not in html:
        return html, False
    i = html.index(before)
    return html[:i] + blk + "\n\n    " + html[i:], True
