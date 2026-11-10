#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared merge of parsed SERFF home jackets (_serff/<ST>/_parsed.json) into serff_home_filings.json.

Each state keeps a thin config script (append_tn_home.py, append_co_home.py, ...) holding only
what is state-specific: the tracking -> (family, product) map, skips, notes, drift excludes and
the pull record. The roll-up logic lives HERE, once, so a fix lands in every state (see memory:
the filter-twin pattern - logic copied per state drifts apart).

Conventions (GA home merge 0d7ec1d2):
  - a multi-entity filing collapses to ONE row: entity = largest by premium "(+N entities)",
    overall_pct = premium-weighted family impact, PH / premium / WP change summed,
    max/min = the widest range across entities.
  - per-company rows are used, not the summary block: SERFF does not aggregate across entities,
    so the summary can read 0.000% (TN Farmers FARM-134862806).
Idempotent: trackings already in the ledger are skipped. Dry run unless --apply.
"""
import json, datetime, re, sys
import filing_dupes

LEDGER = "serff_home_filings.json"
SERFF = "https://serff-sfa.naic.org/serff/sfa/search/filingSummary.xhtml?filingId="


def iso(d):
    if not d: return None
    try: return datetime.datetime.strptime(d.strip(), "%m/%d/%Y").date().isoformat()
    except ValueError: return None


def filing_id(t):
    return re.sub(r"\D", "", t.split("-", 1)[1])   # NWPP-G134716289 -> 134716289


def collapse(comps):
    """Fold per-company rows into one family row."""
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


def merge(state, meta, skip=None, notes=None, drift_exclude=(), pull=None, source_note=None):
    skip, notes = skip or {}, notes or {}
    P = json.load(open(f"_serff/{state}/_parsed.json"))
    led = json.load(open(LEDGER))
    have = {r["tracking"] for r in led["filings"]}
    unknown = [t for t in P if t not in meta and t not in skip]
    if unknown: sys.exit(f"unmapped trackings: {unknown}")
    src = source_note or f"{state} SERFF Filing Access jacket; Company Rate Information block."

    new = []
    for t, p in sorted(P.items()):
        if t in skip or t in have: continue
        carrier, product = meta[t]
        c = collapse(p["companies"])
        if c is None: sys.exit(f"{t}: no company rate rows - add it to SKIP with the reason")
        note = []
        if c["mx"] is not None:
            # Some jackets print max/min reversed (TN Erie 8.1 / 10.0) - store ordered.
            mx, mn = max(c["mx"], c["mn"]), min(c["mx"], c["mn"])
            c["mx"], c["mn"] = mx, mn
            note.append(f"within-filing range {mx:+.1f}% to {mn:+.1f}%.")
        if c["ind"] is not None and c["ind"] - c["pct"] >= 3:
            note.append(f"Indicated {c['ind']:+.1f}%, took {c['pct']:+.1f}% — gap unclosed.")
        if t in notes: note.append(notes[t])
        row = {
            "state": state, "line": "home", "carrier": carrier, "entity": c["entity"],
            "tracking": t, "url": SERFF + filing_id(t),
            "product": product, "filing_type": "Rate/Rule",
            "disposition_date": iso(p["disposition"]),
            "effective_new": iso(p["eff_new"]), "effective_renewal": iso(p["eff_ren"]),
            "overall_pct": c["pct"], "indicated_pct": c["ind"], "prior_revision_pct": None,
            "written_premium": c["wp"], "written_premium_change": c["wpc"],
            "affected": c["aff"], "count_basis": "policyholders", "coverage_changes": None,
            "premium_as_of": None, "recorded_date": datetime.date.today().isoformat(),
            "status": p["status"], "source_note": src,
            "max_pct": c["mx"], "min_pct": c["mn"], "note": " ".join(note) or None,
        }
        if p.get("eff_requested"): row["effective_is_requested"] = True
        if t in drift_exclude: row["drift_exclude"] = True
        new.append(row)

    _, flagged = filing_dupes.annotate(new, led["filings"])
    filing_dupes.report(flagged)
    for r in sorted(new, key=lambda r: -abs(r["overall_pct"])):
        print(f"  {r['carrier']:22} {r['overall_pct']:+7.2f}%  ind {r['indicated_pct']}  "
              f"{r['affected'] or '':>8}  eff {r['effective_new']}  {r['tracking']}"
              f"{'  [drift_exclude]' if r.get('drift_exclude') else ''}")
    if "--apply" not in sys.argv:
        print(f"\n{len(new)} new rows (dry run; --apply to write)"); return new
    led["filings"] += new
    if pull and not any(p.get("state") == state and p.get("line") == "home"
                        and p.get("date_pulled") == pull.get("date_pulled") for p in led["_meta"]["pulls"]):
        pull = dict(pull, state=state, line="home", kept=len(new))
        if skip: pull["note"] = pull.get("note", "") + " Skipped: " + "; ".join(f"{k} {v}" for k, v in skip.items())
        led["_meta"]["pulls"].append(pull)
    json.dump(led, open(LEDGER, "w"), indent=1, ensure_ascii=False)
    print(f"\nappended {len(new)} {state} home rows -> {LEDGER}")
    return new
