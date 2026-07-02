#!/usr/bin/env python3
"""
calibrate_model_rh.py — renters/home twin of calibrate_model.py (auto's pass).

BASE re-anchor: NerdWallet publishes national average annual rates by company
for both products; base := published_rate / published_national_avg (same-source
ratio, the exact method auto used with rate/$208). Carriers without a published
national anchor keep their base unless the reference tables show they're
systematically wrong (Toggle/Assurant were fantasy-cheap: our #1-2 in most
states, never named cheapest by any source).

HOME-TURF offsets: where a source names an in-roster carrier cheapest in a
state, that carrier gets a STATE_CARRIER_ADJ entry there (0.75-0.85). Both the
tools' estimatePremium and the static generators apply adj to every carrier.

Deliberate non-fix: home Chubb stays base 1.4 — MoneyGeek's ~12 Chubb wins are
a $250k-dwelling-profile quirk (NerdWallet's $400k table never names Chubb);
chasing them would wreck Chubb's price realism everywhere else.

Anchors (fetched 2026-07-02):
  renters — NerdWallet natl avg $151: SF $110, Lemonade $118, Auto-Owners $132,
    Allstate $143, USAA $146, Travelers $155, AmFam $182, Country $183,
    Nationwide $193, Farmers $202. Amica $116 (US News).
  home — NerdWallet natl avg $2,490: USAA $1,940, SF $2,415, Progressive $2,580,
    Travelers $2,710, Allstate $2,715.
Idempotent: bases are set (not scaled); offsets are upserted per state map.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RENTERS_BASES = {
    "State Farm": 0.73,        # 110/151
    "Lemonade": 0.78,          # 118/151 (was 0.52 — fantasy-cheap everywhere)
    "Auto-Owners": 0.87,       # 132/151
    "Allstate": 0.95,          # 143/151
    "USAA": 0.90,              # 146/151 pub, MoneyGeek shows cheaper; split + turf
    "Travelers": 1.03,         # 155/151
    "American Family": 1.21,   # 182/151
    "Country Financial": 1.21, # 183/151
    "Nationwide": 1.28,        # 193/151
    "Farmers": 1.34,           # 202/151
    "Amica": 0.78,             # $116/yr (US News), NW cheapest CT/NH/RI
    "Cincinnati Insurance": 0.85,  # NW cheapest AL/MI/VA
    "CSAA / AAA": 0.85,        # NW CA, MG MN/WI
    "Toggle": 0.85,            # never named cheapest by any source (was 0.58)
    "Assurant": 1.00,          # never named cheapest; per-value pricey (was 0.72)
    "GEICO": 0.90,             # partner-underwritten, mid-price (was 0.80)
    "Progressive": 0.95,
    "Liberty Mutual": 1.10,
    "Erie": 0.80,
}
RENTERS_TURF = {  # carrier -> {state: offset}; source-named cheapest states only
    "USAA": dict.fromkeys(["ID", "IN", "KY", "MD", "MO", "MS", "OH", "WY"], 0.85),  # MoneyGeek
    "Amica": dict.fromkeys(["CT", "NH", "RI"], 0.85),                    # NW (+MG NH)
    "Cincinnati Insurance": dict.fromkeys(["AL", "MI", "VA"], 0.75),     # NW (+MG AL)
    "CSAA / AAA": dict.fromkeys(["CA", "MN", "WI", "IL", "MO"], 0.75),   # NW CA/IL/MO, MG MN/WI
    "Travelers": {"MD": 0.75},                                           # NW
    "Nationwide": {"WY": 0.65},                                          # NW
}

HOME_BASES = {
    "USAA": 0.78,       # 1940/2490
    "State Farm": 0.97, # 2415/2490
    "Travelers": 1.09,  # 2710/2490 (was 0.91)
    "Allstate": 1.09,   # 2715/2490 (was 1.15)
    # Progressive 1.04 == 2580/2490 already exact — untouched
}
_SF_HOME = ["AL", "AR", "AZ", "CA", "CT", "DE", "FL", "ID", "KS", "LA", "MS", "MT",
            "NE", "NM", "NV", "NY", "NC", "OK", "SD", "TX", "WV"]  # NW ∪ MG winners
HOME_TURF = {
    "State Farm": dict.fromkeys(_SF_HOME, 0.80),
    "Travelers": dict.fromkeys(["AR", "DE", "MD", "UT", "DC"], 0.75),        # NW
    "Allstate": dict.fromkeys(["IL", "TN", "WI"], 0.75),                     # NW
    "American Family": dict.fromkeys(["AZ", "ID", "IN", "NE", "OR", "UT"], 0.78),  # MG
    "Auto-Owners": dict.fromkeys(["GA", "MI", "CO", "IA", "KS", "KY", "OH", "SD"], 0.78),  # both GA/MI
    "Amica Mutual": dict.fromkeys(["CT", "NH"], 0.78),                       # MG
    "Erie Insurance": dict.fromkeys(["PA", "WV"], 0.80),                     # MG
    "Nationwide": {"WY": 0.72},                                              # NW
    "Mercury Insurance": {"TX": 0.75},                                       # NW
    "CSAA / AAA": {"MO": 0.75},                                              # both (AAA clubs)
    "Auto Club Group (AAA)": {"MO": 0.75},
}


def set_bases(s, carriers_key, bases):
    i = s.index(carriers_key)
    j = s.index("\n];", i)
    block = s[i:j]
    for name, base in bases.items():
        pat = re.compile(r'(name:\s*"%s",\s*base:)\s*[0-9.]+' % re.escape(name))
        block, n = pat.subn(r"\g<1>%s" % base, block)
        assert n == 1, f"base for {name}: {n} matches"
    return s[:i] + block + s[j:]


def set_turf(s, turf):
    i = s.index("const STATE_CARRIER_ADJ = {")
    j = s.index("\n};", i)
    block = s[i:j]
    by_state = {}
    for carrier, states in turf.items():
        for st, v in states.items():
            by_state.setdefault(st, {})[carrier] = v
    for st, entries in by_state.items():
        m = re.search(r'("%s":\s*\{)([^}]*)(\})' % st, block)
        if m:
            row = m.group(2)
            for carrier, v in entries.items():
                cpat = re.compile(r'"%s":\s*[0-9.]+' % re.escape(carrier))
                if cpat.search(row):
                    row = cpat.sub('"%s": %s' % (carrier, v), row)
                else:
                    row = ' "%s": %s,%s' % (carrier, v, row)
            block = block[:m.start(2)] + row + block[m.end(2):]
        else:  # state absent from ADJ — add a fresh row after the opening brace
            cells = ", ".join('"%s": %s' % (c, v) for c, v in entries.items())
            head = "const STATE_CARRIER_ADJ = {"
            k = block.index(head) + len(head)
            block = block[:k] + '\n  "%s": { %s },' % (st, cells) + block[k:]
    return s[:i] + block + s[j:]


def run(page, carriers_key, bases, turf):
    p = ROOT / page
    s = p.read_text(encoding="utf-8")
    s = set_bases(s, carriers_key, bases)
    s = set_turf(s, turf)
    p.write_text(s, encoding="utf-8")
    print(f"{page}: {len(bases)} bases set, turf offsets in "
          f"{len({st for c in turf.values() for st in c})} states")


if __name__ == "__main__":
    run("renters/index.html", "RENTERS_CARRIERS = [", RENTERS_BASES, RENTERS_TURF)
    run("home/index.html", "HOME_CARRIERS = [", HOME_BASES, HOME_TURF)
