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
    "LBPM-134879329": ("Safeco", "Homeowners (American Economy)"),
    "LBPM-134998497": ("Safeco", "Homeowners (American Economy)"),
    # second tier (pulled 2026-11-12)
    "ACUT-134512267": ("Acuity", "Homeowners"),
    "ACUT-134713041": ("Acuity", "Homeowners"),
    "AMSI-134363401": ("Progressive", "Homeowners (American Strategic / ASI)"),
    "AMSI-134594846": ("Progressive", "Homeowners (American Strategic / ASI)"),
    "AMSI-134638649": ("Progressive", "Homeowners (American Strategic / ASI)"),
    "CALC-134599582": ("California Casualty", "Homeowners"),
    "FAIG-134762154": ("Farmers", "Homeowners (Farmers Casualty)"),
    "FAIG-134848115": ("Farmers", "Homeowners (Farmers Casualty)"),
    "FARM-134840145": ("Farmers", "LHO/NGHO/FSPH/SPRC/FLEX Home (Farmers exchanges)"),
    "FDLY-134709915": ("Stillwater", "Homeowners"),
    "FDLY-134988992": ("Stillwater", "Homeowners"),
    "GRIA-134641318": ("Grange Insurance Association", "Homeowners"),
    "HIPO-134574228": ("Hippo", "HO3 (Spinnaker) - water risk"),
    "HRMN-134642398": ("Horace Mann", "Homeowners"),
    "KINN-134732328": ("Kin", "House & Property"),
    "MWFM-134640317": ("Midwest Family", "First Class Portfolio Homeowners"),
}

SKIP = {
    "SFMA-134641887": "State Farm HO-48909: 'Rate data does NOT apply' (no rate change).",
    "FARM-134988778": "Farmers FLEX Home: 'Rate data does NOT apply' (no rate change).",
    "SFBC-133603969": "Colorado Farm Bureau +10.0%: took effect 2023-09-01 (closed in SERFF 2026-01-20) - outside the window by effective date.",
    "SFBC-134756142": "Colorado Farm Bureau Personal Property: new rate structure for dwelling package / mobile home, 0.0% overall.",
    "SFBC-134770841": "Colorado Farm Bureau Personal Property: rate-programming corrections, 0.0%, 0 policyholders.",
    "FAIG-134502404": "Farmers A360: new 2025-04-25 / renewal 2025-06-19 - outside the window by effective date.",
    "FDLY-134295662": "Stillwater +11.75%: new 2024-11-29 / renewal 2025-01-15 - outside the window by effective date.",
    "FDLY-134490397": "Stillwater +0.04%: effective 2025-05-09 - outside the window by effective date.",
    "FARM-134518705": "Farmers FLEX Home 0.0%: effective 2025-06-09 - outside the window by effective date.",
    "FARM-134581069": "Farmers FLEX Home rate transition plan: 'Rate data does NOT apply'.",
    "FARM-134667665": "Farmers expense exhibit: 'Rate data does NOT apply'.",
    "LEMO-134519839": "Metromile/Lemonade by-peril segmentation: 'Rate data does NOT apply'.",
    "KINN-134494338": "Kin initial program filing (new program, no rate change).",
    "WOOD-134708186": "MSI Wingsail new homeowner program (no rate change).",
    "WSMU-135120665": "Western/Residence Mutual withdrawing the homeowners manual (no rate change).",
}

NOTES = {
    "SFMA-134604280": "Rate-neutral revision; 545,361 policyholders in program.",
    "USAA-134737084": "Rule filing carrying zero rate data (0 policyholders affected).",
    "LBPM-135005287": "Rate-neutral overall; redistribution within the book.",
    "CNNB-134711097": "Indicated a 12.1% DECREASE; took -0.2%.",
    "AMMA-134792744": "Indicated a 24.4% DECREASE; filed 0.0% overall (redistribution +11% / -8%).",
    "ALSE-134766565": "Introduces a Landlords and Hosts endorsement; 0.0% overall.",
    "SFBC-134690984": "Legacy book: one rate change across homeowners, farm dwellings, mobile homes and inland marine.",
    "FAIG-134848115": "Rate-neutral revision (0.0%) on 5,299 policyholders.",
    "HIPO-134574228": "Water-risk rate/rule revision, 0.0% overall.",
    "KINN-134732328": "Young program (149 policies): -24.0% overall.",
    "MWFM-134640317": "Indicated +71.4%; took +21.5%.",
    "ACUT-134512267": "Indicated a 9.1% DECREASE; filed 0.0% overall.",
    "ACUT-134713041": "Indicated a 6.0% DECREASE; took -0.04%.",
}

if __name__ == "__main__":
    append_home_jackets.merge(
        "CO", META, skip=SKIP, notes=NOTES,
        source_note=("CO DOI SERFF Filing Access jacket; Company Rate Information block. Colorado is "
                     "file & use: effective dates are the carrier's requested dates."),
        pull={"window": "2025-07-01..2026-11-12", "date_pulled": "2026-11-12", "scanned": 243,
              "note": ("Second tier: 26 jackets pulled (Acuity, Progressive/ASI, California Casualty, "
                       "Farmers, Stillwater, Grange Insurance Association, Hippo, Horace Mann, Kin, "
                       "Midwest Family, Lemonade, MSI, Western Mutual). Still filer-restricted on CO "
                       "public access: Travelers x2, American Family x2, Nationwide NWPP-G134716289.")})
