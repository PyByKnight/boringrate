#!/usr/bin/env python3
"""
apply_filed_changes.py — turn primary-source SERFF filings into renormalized drift
on the relative layer (STATE_CARRIER_ADJ), per SERFF_RUNBOOK.md "Feeding filings
into the rate tool".

Design (unchanged from runbook):
  F(s,c)   = Π (1 + approved_pct/100) over that carrier family's filings whose
             effective date is AFTER the state's anchor_as_of (earlier filings are
             already embedded in the 3rd-party snapshot → skipping them avoids
             double-counting). Multiple entities in a filing are premium-weighted.
  F̄(s)     = premium-weighted mean of F across the tracked carriers that carry a
             STATE_CARRIER_ADJ entry (the set we can renormalize).
  ADJ'(s,c)= ADJ(s,c) × F(s,c) / F̄(s)          (shifts ORDERING, not level)
  level    = stateAvg'(s) = stateAvg(s) × F̄(s), capped ±10%/yr (reported only).
  GATE     = only apply in a state once filings cover a majority (>=3) of its top-5
             carriers; otherwise store, don't apply.

This script is SIDE-EFFECT SAFE: it never edits index.html. It reads the model,
computes the proposed drift, and (with --emit) writes a proposed-patch +
provenance sidecar (proposed_adjustments.json). Applying to index.html is a
separate, deliberate step (and gated on validation).

Usage:
  python3 apply_filed_changes.py            # dry-run report to stdout
  python3 apply_filed_changes.py --emit     # also write proposed_adjustments.json
"""
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
FILINGS = ROOT / "serff_filings.json"
ANCHORS = ROOT / "anchor_dates.json"
OUT = ROOT / "proposed_adjustments.json"

# National top-5 by market share — the default coverage-gate set. Override per state
# where a regional genuinely displaces one (e.g. TN Farm Bureau is TN's #2).
TOP5_DEFAULT = ["State Farm", "GEICO", "Progressive", "Allstate", "USAA"]
TOP5_OVERRIDE = {
    "TN": ["State Farm", "GEICO", "Progressive", "Tennessee Farm Bureau", "Allstate"],
}
GATE_MIN = 3  # majority of 5

# serff carrier family name -> STATE_CARRIER_ADJ roster key (only where they differ).
ROSTER_ALIAS = {
    "Root": "Root Insurance",
    "Shelter": "Shelter Insurance",
    "Erie": "Erie Insurance",
    "Donegal": "Donegal Insurance",
}


def roster_name(carrier, entity):
    """Map a serff carrier family (+entity) to the STATE_CARRIER_ADJ roster key."""
    if carrier == "Liberty Mutual":
        # TN entity is Safeco Insurance Company of Illinois -> the roster carries Safeco.
        return "Safeco" if entity and "Safeco" in entity else "Liberty Mutual"
    return ROSTER_ALIAS.get(carrier, carrier)


def load_model():
    """Parse STATE_CARRIER_ADJ and the per-state avg premium out of index.html."""
    html = INDEX.read_text(encoding="utf-8")
    # STATE_CARRIER_ADJ: each state line is a JSON-valid object literal.
    adj = {}
    block = re.search(r"const STATE_CARRIER_ADJ\s*=\s*\{(.*?)\n\};", html, re.DOTALL)
    if not block:
        sys.exit("could not locate STATE_CARRIER_ADJ in index.html")
    for m in re.finditer(r'"([A-Z]{2})":\s*(\{[^}]*\})', block.group(1)):
        adj[m.group(1)] = json.loads(m.group(2))
    # per-state avg premium: '"TN": { name: "...", avg: 2124, code: "TN" }'
    stateavg = {}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{[^}]*?\bavg:\s*(\d+(?:\.\d+)?)', html):
        stateavg[m.group(1)] = float(m.group(2))
    if not adj:
        sys.exit("STATE_CARRIER_ADJ parsed empty — index.html format may have changed.")
    if not stateavg:
        print("WARN: no per-state avg parsed; level drift will be skipped.", file=sys.stderr)
    return adj, stateavg


def eff_date(row):
    return row.get("effective_new") or row.get("effective_renewal")


def base_tracking(t):
    """'GECC-134888920-2' -> 'GECC-134888920' (strip our entity suffix), robustly."""
    parts = t.split("-")
    return f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else t


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print("usage: apply_filed_changes.py [--emit] [--reach-movers]\n"
              "  (no flags)      dry-run drift report to stdout; never edits index.html\n"
              "  --emit          also write proposed_adjustments.json (patch + provenance sidecar)\n"
              "  --reach-movers  initialize a 1.0 ADJ entry for tracked carriers with post-anchor\n"
              "                  filings but no offset, so drift can reach them (proposes NEW entries)")
        return
    emit = "--emit" in sys.argv
    reach = "--reach-movers" in sys.argv  # Finding 2 option (b): initialize a 1.0 ADJ entry for
    #   tracked carriers that have filings but no STATE_CARRIER_ADJ entry, so drift can reach them.
    #   Off by default (conservative). Still never writes index.html.
    adj, stateavg = load_model()
    filings = json.load(open(FILINGS))["filings"]
    anchors = json.load(open(ANCHORS))
    anchor_default = anchors["default"]
    anchor_state = anchors.get("states", {})

    # group filings by (state, roster carrier)
    by_sc = defaultdict(list)
    coverage = defaultdict(set)   # state -> set of serff carrier families present (any date)
    for r in filings:
        st = r["state"]
        rc = roster_name(r["carrier"], r.get("entity"))
        by_sc[(st, rc)].append(r)
        coverage[st].add(rc)   # store roster names so the gate compares like-for-like

    report = {"_meta": {
        "generated": date.today().isoformat(),
        "purpose": "Proposed renormalized drift on STATE_CARRIER_ADJ from SERFF filings. "
                   "PROPOSED ONLY — not applied to index.html. Provenance keyed by tracking #.",
        "anchor_source": anchors["_meta"]["default_source"],
        "gate_rule": f">= {GATE_MIN} of the state's top-5 carriers must have a filing",
    }, "states": {}}

    states = sorted({st for (st, _) in by_sc})
    for st in states:
        anc = anchor_state.get(st, anchor_default)
        top5 = TOP5_OVERRIDE.get(st, TOP5_DEFAULT)
        covered = [c for c in top5 if c in coverage[st]]  # coverage[st] holds roster names
        gate_pass = len(covered) >= GATE_MIN

        # F(s,c) per roster carrier, only from post-anchor filings
        carriers = {}
        not_in_adj = []
        F_by_c = {}
        prem_by_c = {}
        for (s2, rc), rows in by_sc.items():
            if s2 != st:
                continue
            post = [r for r in rows if eff_date(r) and eff_date(r) > anc
                    and r.get("overall_pct") is not None]
            if not post:
                continue
            num = den = 0.0
            for r in post:
                wp = r.get("written_premium") or 0
                num += r["overall_pct"] * wp
                den += wp
            wavg = (num / den) if den else sum(r["overall_pct"] for r in post) / len(post)
            F = 1.0 + wavg / 100.0
            entry = {
                "wavg_pct": round(wavg, 3),
                "F": round(F, 5),
                "written_premium": den or None,
                "trackings": sorted({base_tracking(r["tracking"]) for r in post}),
                "effective": sorted({eff_date(r) for r in post}),
            }
            in_adj = rc in adj.get(st, {})
            if in_adj or reach:
                entry["adj_old"] = adj.get(st, {}).get(rc, 1.0)
                entry["new_entry"] = not in_adj  # flag carriers we'd be ADDING to the ADJ table
                F_by_c[rc] = F
                prem_by_c[rc] = den or 0.0
                carriers[rc] = entry
            else:
                entry["carrier"] = rc
                not_in_adj.append(entry)

        # F̄(s): premium-weighted mean of F across tracked (in-ADJ) carriers w/ filings
        Fbar = None
        if F_by_c:
            wsum = sum(prem_by_c.values())
            if wsum > 0:
                Fbar = sum(F_by_c[c] * prem_by_c[c] for c in F_by_c) / wsum
            else:
                Fbar = sum(F_by_c.values()) / len(F_by_c)
            for c, e in carriers.items():
                e["Fbar"] = round(Fbar, 5)
                e["adj_new"] = round(e["adj_old"] * e["F"] / Fbar, 4)
                e["delta"] = round(e["adj_new"] - e["adj_old"], 4)

        level = None
        if Fbar and st in stateavg:
            capped = max(0.90, min(1.10, Fbar))  # ±10%/yr cap
            level = {"stateAvg_old": stateavg[st],
                     "Fbar": round(Fbar, 5),
                     "stateAvg_drifted": round(stateavg[st] * capped, 0),
                     "capped": capped != Fbar}

        report["states"][st] = {
            "anchor_as_of": anc,
            "top5": top5,
            "top5_covered": covered,
            "gate_pass": gate_pass,
            "n_post_anchor_carriers": len(carriers) + len(not_in_adj),
            "Fbar": round(Fbar, 5) if Fbar else None,
            "applied_carriers": carriers if gate_pass else {},
            "held_carriers_gate_closed": {} if gate_pass else carriers,
            "filings_not_in_roster_adj": not_in_adj,
            "level_drift": level if gate_pass else None,
        }

    # ---- human-readable dry-run ----
    print(f"anchor (default): {anchor_default}   |   gate: >={GATE_MIN}/5 top carriers\n")
    for st in states:
        s = report["states"][st]
        gate = "GATE PASS" if s["gate_pass"] else "gate CLOSED"
        print(f"== {st} ==  anchor {s['anchor_as_of']}  |  top5 covered "
              f"{len(s['top5_covered'])}/5 {s['top5_covered']}  |  {gate}")
        applied = s["applied_carriers"] if s["gate_pass"] else s["held_carriers_gate_closed"]
        if not applied and not s["filings_not_in_roster_adj"]:
            print("   no post-anchor filings — nothing to drift (already in the snapshot).\n")
            continue
        for c, e in sorted(applied.items(), key=lambda kv: kv[1]["wavg_pct"]):
            if "adj_new" in e:
                tag = " NEW" if e.get("new_entry") else ""
                print(f"   {c:22} {e['wavg_pct']:+6.2f}%  ADJ {e['adj_old']} -> {e['adj_new']} "
                      f"(Δ{e['delta']:+}){tag}  [{','.join(e['trackings'])}]")
            else:
                print(f"   {c:22} {e['wavg_pct']:+6.2f}%  (gate closed — held)")
        for e in sorted(s["filings_not_in_roster_adj"], key=lambda x: x["wavg_pct"]):
            print(f"   {e['carrier']:22} {e['wavg_pct']:+6.2f}%  NOT in STATE_CARRIER_ADJ "
                  f"(would need an entry)  [{','.join(e['trackings'])}]")
        if s["level_drift"]:
            ld = s["level_drift"]
            print(f"   level: stateAvg {ld['stateAvg_old']:.0f} -> {ld['stateAvg_drifted']:.0f} "
                  f"(F̄={ld['Fbar']}{' capped' if ld['capped'] else ''})")
        print()

    if emit:
        json.dump(report, open(OUT, "w"), indent=1)
        print(f"wrote {OUT.name}")
    else:
        print("(dry-run; pass --emit to write proposed_adjustments.json)")


if __name__ == "__main__":
    main()
