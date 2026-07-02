#!/usr/bin/env python3
"""
build_reference_rh.py — renters + home equivalents of build_reference.py.

Assembles cheapest_by_state_renters.json / cheapest_by_state_home.json from two
published sources each (NerdWallet + MoneyGeek, both Quadrant-derived but with
different profiles/coverage levels). Same tier logic as auto: record BOTH
sources per state, derive the in-roster "cheap set" (carriers EITHER source
names cheapest that the product roster actually carries). Score tier overlap,
not single-#1 (the sources agree per-state even less than auto's did).

Unlike auto, USAA is NOT excluded here — MoneyGeek's renters tables include it.
AAA club entities (CSAA, Auto Club Group, Auto Club of SoCal) are collapsed to
the roster's AAA entry; the verifier's footprint filter decides availability.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# ---------------- RENTERS ----------------
# NerdWallet, cheapest renters insurance by state, 2026-01-05 (30yo, $30K property,
# $100K liability, $500 ded): https://www.nerdwallet.com/insurance/renters/cheap-renters-insurance
NW_RENTERS = {
    "AL": "Cincinnati Insurance", "AK": "Allstate", "AZ": "State Farm", "AR": "Arkansas Farm Bureau",
    "CA": "CSAA / AAA", "CO": "Lemonade", "CT": "Amica", "DE": "State Farm", "FL": "State Farm",
    "GA": "The Hanover", "HI": "State Farm", "ID": "State Farm", "IL": "Auto Club Group (AAA)",
    "IN": "Lemonade", "IA": "Auto-Owners", "KS": "State Farm", "KY": "Grange", "LA": "The Hanover",
    "ME": "State Farm", "MD": "Travelers", "MA": "Quincy Mutual", "MI": "Cincinnati Insurance",
    "MN": "State Farm", "MS": "State Farm", "MO": "Auto Club of SoCal (AAA)", "MT": "State Farm",
    "NE": "State Farm", "NV": "Lemonade", "NH": "Amica", "NJ": "Lemonade",
    "NM": ["Lemonade", "State Farm"], "NY": "Lemonade", "NC": "NC Farm Bureau", "ND": "State Farm",
    "OH": "Western Reserve", "OK": "State Farm", "OR": "Lemonade", "PA": "Penn National",
    "RI": "Amica", "SC": "Central Insurance", "SD": "State Farm", "TN": "Lemonade",
    "TX": "State Farm", "UT": "State Farm", "VT": "State Farm", "VA": "Cincinnati Insurance",
    "WA": "Pemco", "DC": "Lemonade", "WV": "State Farm", "WI": "Encova", "WY": "Nationwide",
}
# MoneyGeek, cheapest renters insurance by state, 2026 (Quadrant; $20K/$100K, $1k ded):
# https://www.moneygeek.com/insurance/renters/cheap-renters-insurance-coverage/
MG_RENTERS = {
    "AK": "Allstate", "AL": "Cincinnati Insurance", "AR": "Farm Bureau", "AZ": "Lemonade",
    "CA": "Capital Insurance", "CO": "Lemonade", "CT": "Lemonade", "DC": "Lemonade",
    "DE": "State Farm", "FL": "Citizens Property Insurance", "GA": "Farm Bureau", "HI": "State Farm",
    "IA": "Shelter", "ID": "USAA", "IL": "Lemonade", "IN": "USAA", "KS": "State Farm",
    "KY": "USAA", "LA": "The Hanover", "MA": "Vermont Mutual", "MD": "USAA", "ME": "State Farm",
    "MI": "Auto-Owners", "MN": "CSAA / AAA", "MO": "USAA", "MS": "USAA", "MT": "State Farm",
    "NC": "Farm Bureau", "ND": "Farm Bureau", "NE": "State Farm", "NH": "Amica",
    "NJ": "NJM Insurance", "NM": "Lemonade", "NV": "Lemonade", "NY": "Lemonade", "OH": "USAA",
    "OK": "Lemonade", "OR": "Lemonade", "PA": "Lemonade", "RI": "Lemonade", "SC": "Auto-Owners",
    "SD": "State Farm", "TN": "Lemonade", "TX": "Lemonade", "UT": "State Farm", "VA": "Lemonade",
    "VT": "State Farm", "WA": "Lemonade", "WI": "CSAA / AAA", "WV": "State Farm", "WY": "USAA",
}

# ---------------- HOME ----------------
# NerdWallet, cheapest homeowners insurance by state, 2026-02-20 ($400k dwelling):
# https://www.nerdwallet.com/insurance/homeowners/cheap-home-insurance
NW_HOME = {
    "AL": "Centauri", "AK": "Umialik", "AZ": "State Farm", "AR": "Travelers", "CA": "Pacific Specialty",
    "CO": "Grange Insurance Association", "CT": "State Farm", "DE": "Travelers", "FL": "People's Trust",
    "GA": "Auto-Owners", "HI": "DB Insurance", "ID": "State Farm", "IL": "Allstate", "IN": "Buckeye",
    "IA": "Integrity", "KS": "State Farm", "KY": "Cincinnati Insurance", "LA": "Centauri",
    "ME": "Vermont Mutual", "MD": "Travelers", "MA": "N&D Group", "MI": "Auto-Owners",
    "MN": "Western National", "MS": "State Farm", "MO": "Auto Club of SoCal (AAA)", "MT": "State Farm",
    "NE": "State Farm", "NV": "CIG", "NH": "Vermont Mutual", "NJ": "Cumberland Mutual",
    "NM": "State Farm", "NY": "Preferred Mutual", "NC": "Lititz Mutual", "ND": "North Star",
    "OH": "Buckeye", "OK": "State Farm", "OR": "Grange Insurance Association", "PA": "Selective",
    "RI": "NLC Insurance", "SC": "Cincinnati Insurance", "SD": "Auto-Owners", "TN": "Allstate",
    "TX": "Mercury", "UT": "Travelers", "VT": "Vermont Mutual", "VA": "Cincinnati Insurance",
    "WA": "Grange Insurance Association", "DC": "Travelers", "WV": "State Farm", "WI": "Allstate",
    "WY": "Nationwide",
}
# MoneyGeek, cheapest homeowners insurance by state, updated 2026-07-01 (Quadrant;
# $250k dwelling): https://www.moneygeek.com/insurance/homeowners/cheap-homeowners-insurance/
# (TN absent from their table.)
MG_HOME = {
    "AL": "State Farm", "AK": "Umialik", "AZ": "American Family", "AR": "State Farm",
    "CA": "State Farm", "CO": "Auto-Owners", "CT": "Amica", "DE": "State Farm", "DC": "Chubb",
    "FL": "State Farm", "GA": "Auto-Owners", "HI": "AIG", "ID": "American Family", "IL": "Chubb",
    "IN": "American Family", "IA": "Auto-Owners", "KS": "Auto-Owners", "KY": "Auto-Owners",
    "LA": "State Farm", "ME": "Chubb", "MD": "Chubb", "MA": "Chubb", "MI": "Auto-Owners",
    "MN": "Chubb", "MS": "State Farm", "MO": "CSAA / AAA", "MT": "Chubb", "NE": "American Family",
    "NV": "State Farm", "NH": "Amica", "NJ": "New Jersey Skylands", "NM": "State Farm",
    "NY": "State Farm", "NC": "State Farm", "ND": "Agraria", "OH": "Auto-Owners", "OK": "Chubb",
    "OR": "American Family", "PA": "Erie Insurance", "RI": "PURE", "SC": "Chubb",
    "SD": "State Farm", "TN": None, "TX": "State Farm", "UT": "American Family",
    "VT": "Concord Group", "VA": "Chubb", "WA": "Chubb", "WV": "Erie Insurance", "WI": "Chubb",
    "WY": "AMCO",
}

# source name -> roster name (per product); names not listed fall through to
# exact/substring match against the parsed roster, else dropped as not-carried.
ALIAS_RENTERS = {
    "CSAA / AAA": "CSAA / AAA", "Auto Club Group (AAA)": "CSAA / AAA",
    "Auto Club of SoCal (AAA)": "CSAA / AAA", "Auto-Owners": "Auto-Owners",
    "Cincinnati Insurance": "Cincinnati Insurance", "NJM Insurance": "NJM Insurance",
    "Shelter": None,  # Shelter not in the renters roster
}
ALIAS_HOME = {
    "Auto Club of SoCal (AAA)": "Auto Club Group (AAA)", "CSAA / AAA": "CSAA / AAA",
    "Amica": "Amica Mutual", "Erie Insurance": "Erie Insurance", "Mercury": "Mercury Insurance",
    "Auto-Owners": "Auto-Owners", "Cincinnati Insurance": "Cincinnati Insurance",
}
NOT_CARRIED = {
    "Arkansas Farm Bureau", "The Hanover", "Grange", "Quincy Mutual", "Western Reserve",
    "Penn National", "Central Insurance", "Pemco", "Encova", "NC Farm Bureau", "Farm Bureau",
    "Capital Insurance", "Citizens Property Insurance", "Vermont Mutual",
    "Centauri", "Umialik", "Pacific Specialty", "Grange Insurance Association", "People's Trust",
    "DB Insurance", "Buckeye", "Integrity", "N&D Group", "Western National", "CIG",
    "Cumberland Mutual", "Preferred Mutual", "Lititz Mutual", "North Star", "Selective",
    "NLC Insurance", "AIG", "New Jersey Skylands", "Agraria", "PURE", "Concord Group", "AMCO",
}


def roster_names(page, key):
    s = (ROOT / page).read_text(encoding="utf-8")
    i = s.index(key)
    return set(re.findall(r'name:\s*"([^"]+)"', s[i:s.index("\n];", i)]))


def to_roster(name, roster, alias):
    if name is None or name in NOT_CARRIED:
        return None
    if name in alias:
        cand = alias[name]
        return cand if cand in roster else None
    if name in roster:
        return name
    hit = [r for r in roster if name.lower() in r.lower() or r.lower() in name.lower()]
    return hit[0] if hit else None


def build(product, nw, mg, page, key, alias, srcs):
    roster = roster_names(page, key)
    states, agree = {}, 0
    for code in nw:
        nw_raw = nw[code] if isinstance(nw[code], list) else [nw[code]]
        mg_raw = mg.get(code)
        nw_r = [to_roster(n, roster, alias) for n in nw_raw]
        mg_r = to_roster(mg_raw, roster, alias)
        cheap = sorted({x for x in nw_r + [mg_r] if x})
        same = bool(mg_r and mg_r in nw_r)
        agree += same
        states[code] = {"nerdwallet": nw[code], "moneygeek": mg_raw,
                        "roster_cheap": cheap, "sources_agree": same}
    out = {
        "_meta": {
            "purpose": f"External cheapest-by-state reference ({product}) for verify_model_accuracy_rh.py.",
            "sources": srcs,
            "noise_note": "Sources agree on the in-roster #1 in only %d/51 states — score tier overlap "
                          "(roster_cheap), never single-#1; do not tune to 100%%." % agree,
            "usaa_note": "USAA is NOT excluded (MoneyGeek's tables include it).",
            "date": "2026-07-02",
        },
        "states": states,
    }
    f = ROOT / f"cheapest_by_state_{product}.json"
    f.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    covered = sum(1 for v in states.values() if v["roster_cheap"])
    print(f"{f.name}: {len(states)} states, in-roster cheap set in {covered}, sources agree {agree}")


def main():
    build("renters", NW_RENTERS, MG_RENTERS, "renters/index.html", "RENTERS_CARRIERS = [",
          ALIAS_RENTERS,
          ["NerdWallet, cheapest renters insurance by state, 2026-01-05: https://www.nerdwallet.com/insurance/renters/cheap-renters-insurance",
           "MoneyGeek, cheapest renters insurance by state, 2026 (Quadrant): https://www.moneygeek.com/insurance/renters/cheap-renters-insurance-coverage/"])
    build("home", NW_HOME, MG_HOME, "home/index.html", "HOME_CARRIERS = [",
          ALIAS_HOME,
          ["NerdWallet, cheapest homeowners insurance by state, 2026-02-20: https://www.nerdwallet.com/insurance/homeowners/cheap-home-insurance",
           "MoneyGeek, cheapest homeowners insurance by state, upd. 2026-07-01 (Quadrant): https://www.moneygeek.com/insurance/homeowners/cheap-homeowners-insurance/"])


if __name__ == "__main__":
    main()
