#!/usr/bin/env python3
"""
calibrate_model.py — re-anchor the auto model to published rates + give regionals
per-state offsets (the "full rebuild", 2026-06-23).

Measured against cheapest_by_state.json (real published per-state cheapest), the
pre-calibration model ranked the truly-cheapest carrier at median rank ~9 and put
it in the top-5 only 36% of the time. Two causes, both fixed here:

1. NATIONAL BASES were eyeballed and wrong vs published national averages
   (national full-coverage avg = $208/mo, ValuePenguin 2026-06). base = rate/208.
   e.g. Travelers was 0.97 (real $173 -> 0.83); USAA 0.82 (real $125 -> 0.60);
   GEICO 0.80 (real $187 -> 0.90).

2. REGIONALS had flat sub-national bases (0.65-0.82, below GEICO 0.80) and NO
   per-state offset, so each one undercut the cheap nationals in EVERY state it
   appears — burying Travelers/Progressive/Nationwide. Fix = two parts:
   (a) lift regional bases to a competitive-but-not-sweeping tier (data-anchored
       where we have it: American Family 0.76, Auto-Owners 0.82, Country Financial
       0.85; everything else rescaled from [0.65,0.95] -> [0.90,1.00]);
   (b) add a HOME-TURF offset (0.82) for each regional in the states where it is
       genuinely cheapest — from the reference's per-state #1 plus each Farm
       Bureau's own state. So a regional wins on home turf and sits mid-pack
       elsewhere, the way regionals actually price. Regional offsets go into the
       same STATE_CARRIER_ADJ table (estimatePremium already multiplies by it).

Idempotent guard: aborts if it detects it already ran (USAA base == 0.60).
Run gen_state_rankings.js + audit_rates.py --sync afterward (printed at the end).
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "index.html"

# 1. National bases from published full-coverage rate / $208 (min-liability / $76
#    where full-cov was unavailable). No-data carriers keep their current value.
NATIONAL = {
    "USAA": 0.60, "GEICO": 0.90, "State Farm": 0.92, "Travelers": 0.83,
    "Progressive": 0.95, "Nationwide": 1.10, "Allstate": 1.15, "Farmers": 1.18,
    # kept (no published anchor): Liberty Mutual, Root, Safeco, The Hartford, Kemper, National General
}

# 2a. Regional bases we have published anchors for (others get rescaled).
REGIONAL_OVERRIDE = {"American Family": 0.76, "Auto-Owners": 0.82, "Country Financial": 0.85}

# 2b. Home-turf states per regional (offset 0.82). From cheapest_by_state.json #1
#     winners + each Farm Bureau's own state.
HOME_OFFSET = 0.82
HOME = {
    "Donegal Insurance": ["DE", "GA", "MD", "TN"],
    "Shelter Insurance": ["MS", "MO", "AR", "KS", "OK"],
    "Erie Insurance": ["DC", "PA", "OH", "WV"],
    "NJM Insurance": ["NJ"],
    "Louisiana Farm Bureau": ["LA"], "Texas Farm Bureau": ["TX"],
    "Virginia Farm Bureau": ["VA"], "Kentucky Farm Bureau": ["KY"],
    "Tennessee Farm Bureau": ["TN"], "Georgia Farm Bureau": ["GA"],
    "NC Farm Bureau": ["NC"], "SC Farm Bureau": ["SC"],
    "Mississippi Farm Bureau": ["MS"], "Indiana Farm Bureau": ["IN"],
    "Oklahoma Farm Bureau": ["OK"], "Kansas Farm Bureau": ["KS"],
    "Iowa Farm Bureau": ["IA"], "Arkansas Farm Bureau": ["AR"],
    "Michigan Farm Bureau": ["MI"], "Florida Farm Bureau": ["FL"],
}
# Kemper is national but the reference shows it #1 in SD/WA -> add as national offset.
HOME_NATIONAL = {"Kemper": ["SD", "WA"]}


def span(s, start, end="\n};"):
    i = s.index(start)
    j = s.index(end, i)
    return i, j


def set_base(block, name, val):
    """Replace `base: X` inside the carrier object whose name == name."""
    pat = re.compile(r'(name:\s*"%s"[^}]*?base:\s*)[0-9.]+' % re.escape(name))
    if pat.search(block):
        return pat.sub(lambda m: m.group(1) + ("%g" % val), block, count=1)
    # regional defs are keyed "Name": { base: X
    pat2 = re.compile(r'("%s":\s*\{\s*base:\s*)[0-9.]+' % re.escape(name))
    return pat2.sub(lambda m: m.group(1) + ("%g" % val), block, count=1)


def main():
    s = SRC.read_text(encoding="utf-8")
    if re.search(r'name:\s*"USAA"[^}]*?base:\s*0\.6\b', s):
        raise SystemExit("Already calibrated (USAA base==0.60). Aborting to stay idempotent.")

    # --- national bases ---
    i, j = span(s, "CARRIERS_STANDARD = [", "\n];")
    nat_block = s[i:j]
    for nm, v in NATIONAL.items():
        nat_block = set_base(nat_block, nm, v)
    s = s[:i] + nat_block + s[j:]

    # --- regional bases: override or rescale [0.65,0.95] -> [0.90,1.00] ---
    i, j = span(s, "LOCAL_CARRIER_DEFS = {")
    reg_block = s[i:j]
    cur = dict(re.findall(r'"([^"]+)":\s*\{\s*base:\s*([0-9.]+)', reg_block))
    for nm, b in cur.items():
        if nm in REGIONAL_OVERRIDE:
            nv = REGIONAL_OVERRIDE[nm]
        else:
            ob = float(b)
            nv = round(0.90 + (min(max(ob, 0.65), 0.95) - 0.65) / 0.30 * 0.10, 3)
        reg_block = set_base(reg_block, nm, nv)
    s = s[:i] + reg_block + s[j:]

    # --- home-turf offsets into STATE_CARRIER_ADJ ---
    i, j = span(s, "STATE_CARRIER_ADJ = {")
    adj_block = s[i:j]
    # state -> {carrier: offset} to add
    add = {}
    for carrier, states in {**HOME, **HOME_NATIONAL}.items():
        for st in states:
            add.setdefault(st, {})[carrier] = HOME_OFFSET
    lines = adj_block.split("\n")
    for idx, line in enumerate(lines):
        m = re.match(r'(\s*)"([A-Z]{2})":\s*\{(.*)\}(,?)\s*$', line)
        if not m:
            continue
        indent, code, inner, comma = m.groups()
        if code not in add:
            continue
        present = set(re.findall(r'"([^"]+)":', inner))
        extra = ['"%s": %s' % (c, ("%g" % v)) for c, v in add[code].items() if c not in present]
        if extra:
            inner = inner.strip()
            inner = (inner + ", " + ", ".join(extra)) if inner else ", ".join(extra)
            lines[idx] = '%s"%s": { %s }%s' % (indent, code, inner, comma)
    s = s[:i] + "\n".join(lines) + s[j:]

    SRC.write_text(s, encoding="utf-8")
    noff = sum(len(v) for v in add.values())
    print("national bases re-anchored: %d" % len(NATIONAL))
    print("regional bases: %d overridden, rest rescaled to [0.90,1.00]" % len(REGIONAL_OVERRIDE))
    print("home-turf offsets added: %d across %d states" % (noff, len(add)))
    print("\nnext: node gen_state_rankings.js --export --states --metros ; "
          "python3 audit_rates.py --product auto --sync")


if __name__ == "__main__":
    main()
