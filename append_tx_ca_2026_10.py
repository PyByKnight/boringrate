#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the 2026-10-13 TX + CA open-data feed candidates into the ledgers.

Run once, idempotent (re-running is a no-op: every row is keyed by tracking number).

    python3 append_tx_ca_2026_10.py --apply

WHAT WAS REJECTED, AND WHY. The feeds proposed 19 TX + 10 CA rows. Both scripts have since
been fixed to filter these out at source (see their module docstrings), so this list is the
record of what the unfixed feeds would have published:

  TX, 4 rejected:
    HRMN-134858222   +5.1% auto   WITHDRAWN by Horace Mann (all 3 entities). TDI sets
                                  status="Closed" on a withdrawal, so a status-only check
                                  read it as approved.
    PRGS-134716883   -4.5% auto   "TX RV 202201" — a recreational-vehicle program, filed by
                                  TDI under state_type_of_insurance = Personal Automobile.
                                  Would have published as a Progressive personal-auto CUT.
    FORE-134867705   +3.5% auto   "Motor Home Program" — same trap.
    FORE-134967365   -3.4% auto   "Travel Trailer Program" — same trap.

  CA, 8 rejected:
    FARM-134741595  +27.3%        "COMMERCIAL AUTO V1" (Truck Insurance Exchange) — commercial.
    FARM-134378915  +22.9%        "GARAGE LIABILITY" — commercial.
    SFMA-134751587  +15.5%        "Commercial Auto" — commercial.
    NWPP-G134887359 +13.5%        "Commercial Auto (Farm Operations)" — commercial.
    PERR-134402574   +7.4%        "STREET LEGAL/OFF-ROAD" — powersports, not PPA.
    SFMA-134139850  +32.8%        "RENTAL DWELLING" — landlord dwelling-fire, NOT owner-
                                  occupied homeowners. This is the +32.8% that a prior commit
                                  message reported as a State Farm home increase.
    USAA-134678302   +6.9%        Sibling tracking of USAA-134678224, already in the ledger as
    USAA-134678297   +6.9%        one aggregated row (+6.9% CA home, closed 2026-02-06). Same
                                  rate action under three tracking numbers; merging would have
                                  counted USAA's one CA home increase three times.

DRIFT NOTES.
  * CA rows carry no effective date (CDI publishes none), so apply_filed_changes.py cannot
    drift them by design. CA is coverage + the requested-vs-approved angle, not drift.
  * TX specialty/residual rows are marked drift_exclude: real filings, but not the standard
    book the tool prices.
  * The only TX rows that land post-anchor (TX anchor = 2026-06-23 default) and in the past are
    Allstate ALSE-135059215/-135071772 (both eff 2026-08-31). Horace Mann's are future-dated
    and the engine's future guard holds them until their effective date.
"""
import argparse, json, datetime, sys

TODAY = datetime.date.today().isoformat()

# tracking -> editorial note. Presence here = KEEP. Absence = rejected above.
TX_KEEP = {
    # ---- auto ----
    "GECC-134796944": "GEICO's TX County Mutual entity, +8.9% effective Feb 26, 2026 — the "
                      "largest TX auto increase in this batch. Prior TX GEICO County Mutual "
                      "filings were all 0%, so this is a real change of posture.",
    "ALSE-135059215": "Allstate North American (ANAIC), +6.9% effective Aug 31, 2026. Filed "
                      "alongside ALSE-135071772 (+5.5%, Allstate County Mutual) the same day — "
                      "one rate action across two TX entities.",
    "ALSE-135071772": "Allstate County Mutual (ACM), +5.5% effective Aug 31, 2026. Sibling of "
                      "ALSE-135059215 (+6.9%, ANAIC).",
    "PRCA-134883893": "American Family Connect private passenger auto, +4.8%. TDI publishes no "
                      "effective date for this filing.",
    "FAIG-134926549": "Farmers Property & Casualty 'Automobile' program, -4.4% effective "
                      "May 8, 2026 — a cut, against Allstate's increases in the same state.",
    "HRMN-134950957": "Horace Mann, +4.2% effective Nov 16, 2026 (3 entities, +4.1% to +4.2%). "
                      "Not in the TX tool roster. Note Horace Mann WITHDREW its earlier "
                      "Sep 1, 2026 filing (HRMN-134858222, +5.1%) and refiled lower.",
    "MRTN-134882041": None,   # keeps the feed's own specialty note
    "BRWS-134861015": "Foremost County Mutual 'Select 4.0' nonstandard auto, -6.8% effective "
                      "Mar 13, 2026. Farmers-owned but a separate nonstandard book — not the "
                      "Farmers exchange, so it must not drift the Farmers TX offset.",
    "BRWS-134993638": "Foremost County Mutual 'Select 4.0' nonstandard auto, +5.6% effective "
                      "Jul 17, 2026 — reversing its own March cut within four months.",
    # ---- home ----
    "ALSE-134802108": "Allstate Vehicle & Property (AVPIC), +8.0% effective Jan 26, 2026 — the "
                      "largest TX home increase here from a roster carrier.",
    "FARM-134961095": "Farmers TX home, +6.2% effective May 26, 2026. Four entities spanning "
                      "+2.2% to +6.2%; Texas Farmers and Farmers Exchange both at +6.2%.",
    "HRMN-134962356": "Horace Mann TX home, +4.4% effective Dec 1, 2026 (2 entities, both "
                      "+4.4%). Not in the TX home roster.",
    "MERY-134700067": "Mercury Insurance Company of Texas home, -3.3% effective Feb 25, 2026 — "
                      "a cut in a raising market. Not in the TX home roster.",
    "TWIA-134850628": None,   # keeps the feed's own residual-market note
    "TWIA-134850657": None,
}

CA_KEEP = {
    "SFMA-134139896": "State Farm General 'Homeowners - Non-Tenant', approved +17.0% against a "
                      "REQUESTED +30.0% — California is prior-approval (Prop 103) and CDI cut "
                      "the ask nearly in half. State Farm General is California's largest home "
                      "writer and had no row in this ledger before. CDI publishes no effective "
                      "date, so this cannot drift the model.",
    "IACA-134917540": "Interinsurance Exchange of the Automobile Club (Auto Club of Southern "
                      "California) homeowners, +3.3% approved as requested. A DIFFERENT insurer "
                      "from CSAA Insurance Exchange (AAA Northern California, WSUN-133917622 in "
                      "this ledger) — the two AAA clubs are territorial and do not compete.",
}

AUTO_LEDGER, HOME_LEDGER = "serff_filings.json", "serff_home_filings.json"
CHANGES = "rate_changes.json"

# TX auto movers worth a row on the DISPLAY tracker (rate_changes.json is the AUTO tracker's
# source; home movers flow from serff_home_filings.json via gen_home_rate_tracker instead).
# Specialty/nonstandard books are deliberately left off the consumer-facing tracker.
TRACKER = {
    "GECC-134796944": ("GEICO", 8.9, "increase", "2026-02-26", None,
                       "GEICO Texas County Mutual, +8.9% effective Feb 26, 2026 (TDI filing "
                       "GECC-134796944). TX open data publishes no policyholder counts."),
    "ALSE-135059215": ("Allstate", 6.9, "increase", "2026-08-31", None,
                       "Allstate North American +6.9% effective Aug 31, 2026; Allstate County "
                       "Mutual filed +5.5% the same day (ALSE-135071772). TDI filing "
                       "ALSE-135059215."),
    "PRCA-134883893": ("American Family", 4.8, "increase", "approved 2026-03", None,
                       "American Family Connect private passenger auto, +4.8% (TDI filing "
                       "PRCA-134883893). TDI publishes no effective date for this filing."),
    "FAIG-134926549": ("Farmers", 4.4, "decrease", "2026-05-08", None,
                       "Farmers Property & Casualty 'Automobile' program, -4.4% effective "
                       "May 8, 2026 (TDI filing FAIG-134926549)."),
}


def strip_keys(row, drop):
    return {k: v for k, v in row.items() if k not in drop}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the ledgers (default: dry run)")
    args = ap.parse_args()

    cands = []
    for path in ("tx_filings_new.json", "ca_filings_new.json"):
        try:
            cands += json.load(open(path))["filings"]
        except FileNotFoundError:
            sys.exit(f"{path} missing — run the fetch scripts with --write first")

    keep = {**TX_KEEP, **CA_KEEP}
    auto = json.load(open(AUTO_LEDGER))
    home = json.load(open(HOME_LEDGER))
    changes = json.load(open(CHANGES))
    have_auto = {r["tracking"] for r in auto["filings"]}
    have_home = {r["tracking"] for r in home["filings"]}
    have_chg = {c.get("source", "") for c in changes["changes"]}

    added_auto, added_home, added_chg, skipped = [], [], [], []
    for c in cands:
        trk = c["tracking"]
        if trk not in keep:
            skipped.append(trk)
            continue
        row = strip_keys(c, {"subtype", "possible_duplicate_of"})
        if keep[trk]:
            row["note"] = keep[trk]
        row["recorded_date"] = TODAY
        if c["line"] == "auto":
            # serff_filings.json IS the auto ledger: no `line` key, and no `status` key.
            row = strip_keys(row, {"line", "status"})
            if trk not in have_auto:
                auto["filings"].append(row)
                added_auto.append(trk)
        else:
            if trk not in have_home:
                home["filings"].append(row)
                added_home.append(trk)

        if trk in TRACKER:
            carrier, pct, direction, eff, renewal, note = TRACKER[trk]
            source = f"TX TDI rate filing {trk} (data.texas.gov)"
            if source not in have_chg:
                entry = {"carrier": carrier, "state": "TX", "pct": pct, "dir": direction,
                         "effective": eff, "source": source,
                         "url": "https://data.texas.gov/d/iubg-btfs", "note": note}
                if renewal:
                    entry["renewal"] = renewal
                changes["changes"].append(entry)
                added_chg.append(trk)

    pull = {"state": "TX+CA", "window": "2026-01-01 .. 2026-10-13",
            "date_pulled": TODAY, "method": "open data (TDI Socrata + CDI YTD xlsx)",
            "scanned": len(cands), "kept": len(added_auto) + len(added_home),
            "note": "Feed candidates triaged by append_tx_ca_2026_10.py; 12 rejected as "
                    "withdrawn, commercial, RV/specialty or sibling duplicates."}
    auto.setdefault("_meta", {}).setdefault("pulls", []).append(pull)
    home.setdefault("_meta", {}).setdefault("pulls", []).append(dict(pull))
    auto["_meta"]["last_updated"] = TODAY
    home["_meta"]["last_updated"] = TODAY

    print(f"candidates: {len(cands)}   rejected: {len(skipped)}")
    print(f"auto ledger  += {len(added_auto)}  -> {len(auto['filings'])} rows")
    print(f"home ledger  += {len(added_home)}  -> {len(home['filings'])} rows")
    print(f"rate_changes += {len(added_chg)}  -> {len(changes['changes'])} rows")
    for t in added_auto + added_home:
        print(f"  + {t}")
    if not args.apply:
        print("\ndry run — pass --apply to write")
        return
    # These three files do NOT share an escaping convention: serff_filings.json stores
    # literal em-dashes, serff_home_filings.json and rate_changes.json store —. Guessing
    # either way reformats every line containing one in two of the three files, burying a
    # 17-row change in a 440-line cosmetic diff. So match whatever each file already does.
    for path, blob in ((AUTO_LEDGER, auto), (HOME_LEDGER, home), (CHANGES, changes)):
        escaped = "\\u" in open(path, encoding="utf-8").read()
        json.dump(blob, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=escaped)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
