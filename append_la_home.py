#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the LA homeowners SERFF pull (_serff/LA/_parsed.json) into serff_home_filings.json.

Run `python3 parse_ga_jackets.py LA` first; roll-up logic is in append_home_jackets.py.
Pull list: ~/la_home_jackets.html (build_pull_list.py LA Louisiana). 13 LA filings were already
in the ledger before this pull and were left off the list.
"""
import append_home_jackets

META = {
    "ALSE-134677301": ("Allstate", "Homeowners (Allstate Indemnity)"),
    "ALSE-134945507": ("Allstate", "Homeowners/LPP (Allstate North American)"),
    "ALTR-134932762": ("Allied Trust", "HO3"),
    "AMSI-134684485": ("Progressive", "Homeowners (Progressive Property)"),
    "FARM-134611603": ("Farmers", "FSPH (Farmers Insurance Exchange)"),
    "LBPM-134927331": ("Safeco", "Homeowners"),
    "LBPM-135044493": ("Safeco", "Personal Homeowners"),
    "LBPM-134937451": ("Liberty Mutual", "Homeowners (America First / First Liberty)"),
    "SFBC-134581231": ("Louisiana Farm Bureau", "Dwelling Package"),
}

SKIP = {
    "ALSE-134628035": "Allstate Insurance Co LIGA-assessment recoupment notice; book closed to new business; 'Rate data does NOT apply'.",
    "ALSE-134894210": "Allstate Insurance Co LIGA-assessment recoupment notice; book closed to new business; 'Rate data does NOT apply'.",
    "ALSE-134551612": "Allstate North American new homeowners program (introduction, no rate change).",
    "SFBC-134610567": "Louisiana Farm Bureau specified-additional-amount endorsement; 'Rate data does NOT apply'.",
    "SFBC-134997216": ("Louisiana Farm Bureau homeowners rate change, but the jacket says 'Rate data does NOT "
                       "apply' and carries no %; the figure is only in the attachments (not pulled)."),
    "LBPM-134836833": "Safeco: 'We are not updating any of our Homeowners Rates or Forms with this filing.'",
    "LBPM-134844502": "Liberty (America First / First Liberty) rule revision; 0.0%, 0 policyholders.",
}

NOTES = {
    "ALSE-134677301": "Overall +1.0% via the reinsurance rate adjustment factor.",
    "ALSE-134945507": "Adds Landlords and Hosts, Enhanced Personal Property and Personal Injury endorsements; 0.0% overall.",
    "ALTR-134932762": "Indicated a 13.5% DECREASE; took -4.7%.",
    "FARM-134611603": "Rate-neutral (0.0%) on 412 policyholders.",
    "SFBC-134581231": "Indicated +24.0%; took +10.9%.",
}

if __name__ == "__main__":
    append_home_jackets.merge(
        "LA", META, skip=SKIP, notes=NOTES,
        pull={"window": "2025-07-01..2026-11-12", "date_pulled": "2026-11-12", "scanned": 351,
              "note": ("All 4 pages of the TOI 04.0 search triaged to 52 rate-bearing candidates; 16 "
                       "start-here jackets pulled. Not yet: Hanover HNVR-G135011922, Chubb "
                       "ACEH-134493420, and the 34-filing second tier (~/la_home_jackets.html).")})
