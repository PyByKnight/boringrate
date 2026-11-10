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
import json, datetime, sys
import filing_dupes

LEDGER = "serff_home_filings.json"
TODAY = datetime.date.today().isoformat()

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


def iso(d):
    if not d: return None
    try: return datetime.datetime.strptime(d.strip(), "%m/%d/%Y").date().isoformat()
    except ValueError: return None


def collapse(comps):
    """Fold per-company rows into one family row (GA convention)."""
    live = [c for c in comps if c.get("impact") is not None]
    if not live: return None
    wp = sum(c["wp"] or 0 for c in live)
    if wp:
        pct = sum((c["impact"] or 0) * (c["wp"] or 0) for c in live) / wp
        ind = (sum((c["indicated"] or 0) * (c["wp"] or 0) for c in live) / wp
               if all(c["indicated"] is not None for c in live) else None)
    else:
        pct = sum(c["impact"] for c in live) / len(live)
        ind = live[0]["indicated"]
    big = max(live, key=lambda c: c["wp"] or 0)
    ent = big["entity"] + (f" (+{len(live)-1} entities)" if len(live) > 1 else "")
    rng = [v for c in live for v in (c["max_pct"], c["min_pct"]) if v is not None]
    aff = sum(c["affected"] or 0 for c in live)
    wpc = [c["wp_change"] for c in live if c["wp_change"] is not None]
    return dict(entity=ent, pct=round(pct, 3), ind=None if ind is None else round(ind, 3),
                wp=wp or None, aff=aff or None, wpc=sum(wpc) if wpc else None,
                mx=max(rng) if rng else None, mn=min(rng) if rng else None)


def main():
    P = json.load(open("_serff/TN/_parsed.json"))
    led = json.load(open(LEDGER))
    have = {r["tracking"] for r in led["filings"]}
    unknown = [t for t in P if t not in META and t not in SKIP]
    if unknown: sys.exit(f"unmapped trackings: {unknown}")

    new = []
    for t, p in sorted(P.items()):
        if t in SKIP or t in have: continue
        carrier, product = META[t]
        c = collapse(p["companies"])
        if c is None: sys.exit(f"{t}: no company rate rows")
        note = []
        if c["mx"] is not None:
            note.append(f"within-filing range {c['mx']:+.1f}% to {c['mn']:+.1f}%.")
        if c["ind"] is not None and c["ind"] - c["pct"] >= 3:
            note.append(f"Indicated {c['ind']:+.1f}%, took {c['pct']:+.1f}% — gap unclosed.")
        if t in NOTES: note.append(NOTES[t])
        row = {
            "state": "TN", "line": "home", "carrier": carrier, "entity": c["entity"],
            "tracking": t,
            "url": f"https://serff-sfa.naic.org/serff/sfa/search/filingSummary.xhtml?filingId={t.split('-')[1]}",
            "product": product, "filing_type": "Rate/Rule",
            "disposition_date": iso(p["disposition"]),
            "effective_new": iso(p["eff_new"]), "effective_renewal": iso(p["eff_ren"]),
            "overall_pct": c["pct"], "indicated_pct": c["ind"], "prior_revision_pct": None,
            "written_premium": c["wp"], "written_premium_change": c["wpc"],
            "affected": c["aff"], "count_basis": "policyholders", "coverage_changes": None,
            "premium_as_of": None, "recorded_date": TODAY, "status": p["status"],
            "source_note": "TN SERFF Filing Access jacket; Company Rate Information block.",
            "max_pct": c["mx"], "min_pct": c["mn"], "note": " ".join(note) or None,
        }
        if t in DRIFT_EXCLUDE: row["drift_exclude"] = True
        new.append(row)

    _, flagged = filing_dupes.annotate(new, led["filings"])
    filing_dupes.report(flagged)
    for r in sorted(new, key=lambda r: -abs(r["overall_pct"])):
        print(f"  {r['carrier']:20} {r['overall_pct']:+7.2f}%  ind {r['indicated_pct']}  "
              f"{r['affected'] or '':>8}  {r['tracking']}{'  [drift_exclude]' if r.get('drift_exclude') else ''}")
    if "--apply" not in sys.argv:
        print(f"\n{len(new)} new rows (dry run; --apply to write)"); return
    led["filings"] += new
    if not any(p.get("state") == "TN" and p.get("line") == "home" for p in led["_meta"]["pulls"]):
        led["_meta"]["pulls"].append({
            "state": "TN", "line": "home", "window": "2025-07-01..2026-11-05",
            "date_pulled": TODAY, "scanned": 268, "kept": len(new),
            "note": ("106 rate-bearing of 268 results; 39 of the 43 Tier-1 jackets pulled. "
                     "Not yet pulled: Selective SELC-134703566 / SELC-134698561, Cincinnati "
                     "CNNB-134929303 / CNNB-134761578, and all of Tier 2 (47). Skipped: "
                     + "; ".join(f"{k} {v}" for k, v in SKIP.items())),
        })
    json.dump(led, open(LEDGER, "w"), indent=1, ensure_ascii=False)
    print(f"\nappended {len(new)} TN home rows -> {LEDGER}")


if __name__ == "__main__":
    main()
