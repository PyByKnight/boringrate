#!/usr/bin/env python3
"""
build_reference.py — assemble cheapest_by_state.json from MULTIPLE published sources.

The per-state single cheapest carrier is highly source-dependent (full- vs
minimum-coverage, driver profile): NerdWallet (full cov) and MoneyGeek (min cov)
agree on the in-roster #1 in only ~7 of 51 states. So instead of one noisy #1 we
record BOTH sources per state and derive an in-roster "cheap set" (the carriers
EITHER source names cheapest that BoringRate actually carries). Accuracy is then
measured as tier overlap (does the model rank a real cheap-tier carrier high),
which is robust to single-source noise. Names are normalized to roster spelling.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Source A: NerdWallet, cheapest full-coverage by state (2026-06-23).
NERDWALLET = {
    "AL": "Travelers", "AK": "GEICO", "AZ": "Travelers", "AR": "Travelers", "CA": "GEICO",
    "CO": "American National", "CT": "Travelers", "DE": "Donegal", "FL": "State Farm",
    "GA": "Donegal", "HI": "GEICO", "ID": "Travelers", "IL": "Travelers", "IN": "Progressive",
    "IA": "Travelers", "KS": "Travelers", "KY": "State Farm", "LA": "Louisiana Farm Bureau",
    "ME": "Progressive", "MD": "Donegal", "MA": "GEICO", "MI": "GEICO", "MN": "Travelers",
    "MS": "Shelter", "MO": "Shelter", "MT": "State Farm", "NE": "American National",
    "NV": "Progressive", "NH": "GEICO", "NJ": "GEICO", "NM": "Central Insurance",
    "NY": "Progressive", "NC": "Progressive", "ND": "Nationwide", "OH": "Central Insurance",
    "OK": "Progressive", "OR": "State Farm", "PA": "Encova", "RI": "Travelers",
    "SC": "American National", "SD": "Kemper", "TN": "Donegal", "TX": "Texas Farm Bureau",
    "UT": "Nationwide", "VT": "Union Mutual", "VA": "Virginia Farm Bureau", "WA": "Kemper",
    "DC": "Erie", "WV": "Encova", "WI": "Travelers", "WY": "American National",
}
# Source B: MoneyGeek, cheapest minimum-coverage by state (2026-06-23).
MONEYGEEK = {
    "AL": "AIG", "AK": "GEICO", "AZ": "Travelers", "AR": "Arkansas Farm Bureau", "CA": "GEICO",
    "CO": "American National", "CT": "GEICO", "DE": "Travelers", "DC": "Chubb", "FL": "Travelers",
    "GA": "GEICO", "HI": "GEICO", "ID": "State Farm", "IL": "GEICO", "IN": "Hastings",
    "IA": "State Farm", "KS": "GEICO", "KY": "Travelers", "LA": "GEICO", "ME": "MMG Insurance",
    "MD": "GEICO", "MA": "Plymouth Rock", "MI": "Travelers", "MN": "Westfield",
    "MS": "Mississippi Farm Bureau", "MO": "Auto-Owners", "MT": "State Farm",
    "NE": "Farmers Mutual NE", "NV": "Travelers", "NH": "Safety", "NJ": "Plymouth Rock",
    "NM": "Central Insurance", "NY": "NYCM", "NC": "State Farm", "ND": "North Star",
    "OH": "Auto-Owners", "OK": "Progressive", "OR": "State Farm", "PA": "Westfield",
    "RI": "State Farm", "SC": "American National", "SD": "Farmers Mutual NE",
    "TN": "Tennessee Farm Bureau", "TX": "State Farm", "UT": "GEICO", "VT": "Co-operative",
    "VA": "Travelers", "WA": "State Farm", "WV": "Westfield", "WI": "GEICO", "WY": "GEICO",
}

# Map a source's carrier name -> our roster name, or None if we don't carry it.
ALIAS = {
    "Donegal": "Donegal Insurance", "Shelter": "Shelter Insurance", "Erie": "Erie Insurance",
    "Hastings": "Hastings Mutual", "MMG Insurance": "MMG Insurance", "Westfield": "Westfield Insurance",
    "Plymouth Rock": "Plymouth Rock Assurance", "NYCM": "NYCM Insurance", "Auto-Owners": "Auto-Owners",
}
NOT_CARRIED = {"American National", "Central Insurance", "Encova", "Union Mutual", "AIG", "Chubb",
               "Safety", "Co-operative", "North Star", "Farmers Mutual NE"}


def roster_names():
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    def blk(a, e="\n};"):
        i = s.index(a); return s[i + len(a):s.index(e, i)]
    nat = set(re.findall(r'name:\s*"([^"]+)"', blk("CARRIERS_STANDARD = [", "\n];")))
    reg = set(re.findall(r'"([^"]+)":\s*\{\s*base:', blk("LOCAL_CARRIER_DEFS = {")))
    return nat | reg


def to_roster(name, roster):
    if name in NOT_CARRIED:
        return None
    cand = ALIAS.get(name, name)
    if cand in roster:
        return cand
    hit = [r for r in roster if cand.lower() in r.lower() or r.lower() in cand.lower()]
    return hit[0] if hit else None


def main():
    roster = roster_names()
    states = {}
    agree = 0
    for code in NERDWALLET:
        nw, mg = NERDWALLET[code], MONEYGEEK.get(code)
        nw_r, mg_r = to_roster(nw, roster), to_roster(mg, roster) if mg else None
        cheap = sorted({x for x in (nw_r, mg_r) if x})
        same = bool(nw_r and nw_r == mg_r)
        agree += same
        states[code] = {
            "nerdwallet_fullcov": nw, "moneygeek_mincov": mg,
            "roster_cheap": cheap, "sources_agree": same,
        }
    out = {
        "_meta": {
            "purpose": "Real external cheapest-by-state reference (multi-source) for verify_model_accuracy.py.",
            "sources": [
                "NerdWallet, cheapest full-coverage by state, 2026-06-23: https://www.nerdwallet.com/insurance/auto/cheapest-car-insurance",
                "MoneyGeek, cheapest minimum-coverage by state, 2026-06-23: https://www.moneygeek.com/insurance/auto/cheapest-car-insurance-companies/",
                "Cross-check (aggregate): ValuePenguin https://www.valuepenguin.com/best-cheap-full-coverage-auto-insurance",
            ],
            "noise_note": "The two sources agree on the in-roster #1 in only %d/51 states — the exact per-state #1 flips with coverage level/profile. Score on 'roster_cheap' tier overlap, NOT single-#1 match, and do not tune to 100%%." % agree,
            "roster_cheap": "in-roster carriers that EITHER source named cheapest (the cheap tier we can actually rank); null-source winners (carriers we don't carry) are dropped.",
            "date": "2026-06-23",
        },
        "states": states,
    }
    (ROOT / "cheapest_by_state.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("wrote cheapest_by_state.json: %d states, sources agree on in-roster #1 in %d" % (len(states), agree))
    print("states with >=1 in-roster cheap carrier:", sum(1 for v in states.values() if v["roster_cheap"]))


if __name__ == "__main__":
    main()
