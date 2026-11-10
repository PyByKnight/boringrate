#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the TN homeowners SERFF pull (_serff/TN/_parsed.json) into serff_home_filings.json.

Run `python3 parse_ga_jackets.py TN` first. Idempotent: rows already in the ledger by
tracking are skipped. Same conventions as the GA home merge (0d7ec1d2):
  - a multi-entity filing collapses to ONE row: entity = largest by premium "(+N entities)",
    overall_pct = premium-weighted family impact, PH / premium / WP change summed,
    max/min = the widest range across entities.
  - the per-company rows are used, not the summary block: SERFF does not aggregate across
    entities, so the summary can read 0.000% (Farmers FARM-134862806 does exactly that).
"""
import append_home_jackets


# tracking -> (carrier family, product). Family names match the home roster keys or the
# ROSTER_ALIAS in apply_home_filings.py, so a TN row can actually drift.
META = {
    "ACEH-134547776": ("Chubb", "Masterpiece"),
    "ACEH-134936218": ("Chubb", "Masterpiece"),
    "ACEH-134936759": ("Chubb", "Masterpiece"),
    "ALSE-134870127": ("Allstate", "APC Homeowners"),
    "ALSE-134870166": ("Allstate", "AIC Homeowners"),
    "ALSE-134870184": ("Allstate", "AVPIC Homeowners"),
    "AMMA-134942956": ("Amica", "Homeowners"),
    "AOIC-134760296": ("Auto-Owners", "Tennessee Homeowners"),
    "CEIN-134915668": ("Celina", "Homeowners"),
    "CFPC-134566841": ("Country Financial", "Homeowners"),
    "CFPC-135003608": ("Country Financial", "Homeowners"),
    "CNNB-134553574": ("Cincinnati Insurance", "Homeowners (CCC)"),
    "DNGL-134724111": ("Donegal", "Homeowners"),
    "DNGL-134918733": ("Donegal", "Homeowners"),
    "DNGL-134922061": ("Donegal", "Homeowners"),
    "ERPP-134705628": ("Erie", "ErieSecure Home (Exchange)"),
    "ERPP-134787274": ("Erie", "ErieSecure Home"),
    "ERPP-135041201": ("Erie", "ErieSecure Home (Exchange)"),
    "FAIG-134889442": ("Farmers", "Homeowners"),
    "FAIG-135120687": ("Farmers", "Homeowners"),
    "FARM-134862806": ("Farmers", "Flex Home / Smart Plan Home"),
    "GMMX-134887365": ("Encompass", "Custom 360 Homeowners"),
    "GMMX-135016659": ("Encompass", "Custom 360 Homeowners"),
    "GRAN-134757316": ("Grange", "PinPoint Homeowners 3"),
    "GRAN-134979500": ("Grange", "PinPoint Homeowners"),
    "HART-134966085": ("The Hartford", "Home Prevail Direct"),
    "HMSS-135031365": ("Homesite", "Homeowners"),
    "HMSS-135096824": ("Homesite", "Homeowners"),
    "LBPM-134917882": ("Safeco", "Homeowners"),
    "LBPM-134918634": ("Safeco", "Homeowners"),
    "LBPM-135021598": ("Liberty Mutual", "Homeowners (Peerless)"),
    "NWPP-134558363": ("Nationwide", "Homeowners"),
    "SELC-134949915": ("Selective", "Homeowners - roof condition rating"),
    "SFMA-134620382": ("State Farm", "Homeowners (HO-48911)"),
    "SFMA-134989040": ("State Farm", "Homeowners (HO-49589)"),
    "SHEL-134848305": ("Shelter Insurance", "Homeowners"),
    "USAA-134871964": ("USAA", "Homeowners"),
}

# Downloaded but carry no rate change — recorded in _meta, not as rows.
SKIP = {
    "GRAN-134721474": "TrueCover Home new-program filing; 'Rate data does NOT apply'.",
    "HART-134742934": "Home Dimensions depopulation (form/rule); no rate effect.",
}

NOTES = {
    "ERPP-134705628": ("Closed book (Erie Insurance Exchange writes no new TN home business); "
                       "cosmetic-damage language, rate-neutral."),
    "ERPP-135041201": ("Closed book: Erie Insurance Exchange no longer writes new TN home "
                       "business, so this +10% is renewal-only. drift_exclude: the open book is "
                       "Erie Insurance Company (ERPP-134787274). Jacket prints max 8.1% / min 10.0% "
                       "(reversed as filed); stored ordered."),
    "AMMA-134942956": "Rate-neutral overall (indicated +4.4%) with a wide +22% / -18% redistribution.",
    "SFMA-134620382": "Rate-neutral revision; 526,656 policyholders in program.",
}
DRIFT_EXCLUDE = {"ERPP-134705628", "ERPP-135041201"}


def main():
    append_home_jackets.merge(
        "TN", META, skip=SKIP, notes=NOTES, drift_exclude=DRIFT_EXCLUDE,
        pull={"window": "2025-07-01..2026-11-05", "date_pulled": "2026-11-10", "scanned": 268,
              "note": ("106 rate-bearing of 268 results; 39 of the 43 Tier-1 jackets pulled. "
                       "Not yet pulled: Selective SELC-134703566 / SELC-134698561, Cincinnati "
                       "CNNB-134929303 / CNNB-134761578, and all of Tier 2 (47).")})


if __name__ == "__main__":
    main()
