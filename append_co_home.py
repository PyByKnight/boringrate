#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the CO homeowners SERFF pull (_serff/CO/_parsed.json) into serff_home_filings.json.

Run `python3 parse_ga_jackets.py CO` first; roll-up logic is in append_home_jackets.py.
Colorado is FILE & USE: jackets read "Filed", and the Effective Date (New/Renewal) fields
are blank - the dates come from the header's "Requested" fields, so every CO row carries
effective_is_requested. Pull list: ~/co_home_jackets.html (build_pull_list.py CO).
"""
import append_home_jackets

META = {
    "ACEH-134677743": ("Chubb", "Masterpiece"),
    "ACEH-134677834": ("Chubb", "Masterpiece"),
    "AOIC-134700341": ("Auto-Owners", "Colorado Homeowners"),
    "AOIC-134808922": ("Auto-Owners", "Colorado Homeowners"),
    "CNNB-134711097": ("Cincinnati Insurance", "Homeowner (Cincinnati Casualty)"),
    "CNNB-134734798": ("Cincinnati Insurance", "Home (Cincinnati Insurance Co)"),
    "FAIG-134966392": ("Farmers", "Homeowners (Farmers Casualty)"),
    "FAIG-135003023": ("Farmers", "Homeowners (Farmers P&C)"),
    "FAIG-135003144": ("Farmers", "Homeowners (Farmers Direct P&C)"),
    "HART-134566854": ("The Hartford", "Home Prevail"),
    "HART-134870270": ("The Hartford", "Home Prevail Direct"),
    "HART-134917211": ("The Hartford", "Home Advantage"),
    "HMSS-134529290": ("Homesite", "Homeowners"),
    "HMSS-134907670": ("Homesite", "Homeowners (Homesite Indemnity)"),
    "HMSS-134939420": ("Homesite", "Homeowners"),
    "LBPM-134814553": ("Liberty Mutual", "Homeowners (Peerless / Liberty Mutual Ins Co)"),
    "LBPM-134814588": ("Liberty Mutual", "Homeowners (Liberty Mutual Fire)"),
    "LBPM-134814602": ("Liberty Mutual", "Homeowners (Liberty Mutual Personal / LM / Liberty Ins Corp)"),
    "LBPM-134870677": ("Safeco", "Homeowners"),
    "LBPM-135005287": ("Liberty Mutual", "Homeowners (Peerless / Liberty Mutual Ins Co)"),
    "NWPP-134548272": ("Nationwide", "Homeowners"),
    "SFMA-134522369": ("State Farm", "Homeowners (HO-48041)"),
    "SFMA-134604280": ("State Farm", "Homeowners (HO-48692)"),
    "SFMA-134942134": ("State Farm", "Homeowners (HO-49485)"),
    "SHEL-134842032": ("Shelter Insurance", "Homeowners"),
    "USAA-134644521": ("USAA", "Homeowners"),
    "USAA-134737084": ("USAA", "Homeowners"),
    # page 1 of the search (pulled 2026-11-10, second batch)
    "ALSE-134603438": ("Allstate", "Homeowners (Allstate Fire & Casualty)"),
    "ALSE-134603603": ("Allstate", "Homeowners (Allstate Vehicle & Property)"),
    "ALSE-134604410": ("Allstate", "Homeowners (Allstate P&C)"),
    "ALSE-134604433": ("Allstate", "Homeowners (Allstate Insurance Co)"),
    "ALSE-134604451": ("Allstate", "Homeowners (Allstate Indemnity)"),
    "ALSE-134766565": ("Allstate", "Homeowners (Allstate North American) - landlords endorsement"),
    "ALSE-134876134": ("Allstate", "Homeowners (Allstate North American)"),
    "AMMA-134792744": ("Amica", "Homeowners"),
    "CEMC-134636064": ("Central", "Homeowners Program"),
    "CEMC-134824516": ("Central", "Homeowners Program"),
    "CFPC-134629075": ("Country Financial", "Homeowners (COUNTRY Preferred)"),
    "CFPC-134758720": ("Country Financial", "Homeowners (COUNTRY Preferred)"),
    "SFBC-134626630": ("Colorado Farm Bureau", "Homeowners"),
    "SFBC-134690984": ("Colorado Farm Bureau", "Legacy Personal Property (Homeowners, Farm Dwelling, Mobile Home, Inland Marine)"),
}

SKIP = {
    "SFMA-134641887": "State Farm HO-48909: 'Rate data does NOT apply' (no rate change).",
    "FARM-134988778": "Farmers FLEX Home: 'Rate data does NOT apply' (no rate change).",
    "SFBC-133603969": "Colorado Farm Bureau +10.0%: took effect 2023-09-01 (closed in SERFF 2026-01-20) - outside the window by effective date.",
    "SFBC-134756142": "Colorado Farm Bureau Personal Property: new rate structure for dwelling package / mobile home, 0.0% overall.",
    "SFBC-134770841": "Colorado Farm Bureau Personal Property: rate-programming corrections, 0.0%, 0 policyholders.",
}

NOTES = {
    "SFMA-134604280": "Rate-neutral revision; 545,361 policyholders in program.",
    "USAA-134737084": "Rule filing carrying zero rate data (0 policyholders affected).",
    "LBPM-135005287": "Rate-neutral overall; redistribution within the book.",
    "CNNB-134711097": "Indicated a 12.1% DECREASE; took -0.2%.",
    "AMMA-134792744": "Indicated a 24.4% DECREASE; filed 0.0% overall (redistribution +11% / -8%).",
    "ALSE-134766565": "Introduces a Landlords and Hosts endorsement; 0.0% overall.",
    "SFBC-134690984": "Legacy book: one rate change across homeowners, farm dwellings, mobile homes and inland marine.",
}

if __name__ == "__main__":
    append_home_jackets.merge(
        "CO", META, skip=SKIP, notes=NOTES,
        source_note=("CO DOI SERFF Filing Access jacket; Company Rate Information block. Colorado is "
                     "file & use: effective dates are the carrier's requested dates."),
        pull={"window": "2025-07-01..2026-11-10", "date_pulled": "2026-11-10", "scanned": 243,
              "note": ("All 3 pages of the TOI 04.0 search triaged. 41 of 46 start-here jackets pulled + 5 "
                       "Colorado Farm Bureau; not yet: Travelers TRVD-G134688466 / TRVD-G134585304, "
                       "Nationwide NWPP-G134716289, American Family AMFC-134941999 / AMFC-134776756, "
                       "Safeco LBPM-134998497 / LBPM-134879329. Rest of second tier unpulled - list in "
                       "~/co_home_jackets.html.")})
