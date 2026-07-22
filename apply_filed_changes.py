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
MARKET = ROOT / "market_share.json"
OUT = ROOT / "proposed_adjustments.json"

# National top-5 by market share — the default coverage-gate set. Override per state
# where a regional genuinely displaces one (e.g. TN Farm Bureau is TN's #2).
TOP5_DEFAULT = ["State Farm", "GEICO", "Progressive", "Allstate", "USAA"]
TOP5_OVERRIDE = {
    "TN": ["State Farm", "GEICO", "Progressive", "Tennessee Farm Bureau", "Allstate"],
}
GATE_MIN = 3  # majority of 5 — drift GATE stays top-5 (≈60% of market weight drives the state avg)

# TOP-10 is the SOURCING / tool-consistency completeness target (the tool ranks up to 20 carriers), NOT
# the drift gate. Reported per state so we know how much of the displayed roster is primary-sourced.
# Default = the 10 broadly-written nationals; per-state override swaps in the dominant regional(s).
TOP10_DEFAULT = ["State Farm", "GEICO", "Progressive", "Allstate", "USAA",
                 "Farmers", "Liberty Mutual", "Travelers", "Nationwide", "American Family"]
TOP10_OVERRIDE = {
    "TN": ["State Farm", "GEICO", "Progressive", "Allstate", "USAA",
           "Tennessee Farm Bureau", "Farmers", "Liberty Mutual", "Nationwide", "Erie Insurance"],
    "GA": ["State Farm", "GEICO", "Progressive", "Allstate", "USAA",
           "Georgia Farm Bureau", "Farmers", "Liberty Mutual", "Travelers", "Nationwide"],
    "TX": ["State Farm", "GEICO", "Progressive", "Allstate", "USAA",
           "Texas Farm Bureau", "Farmers", "Liberty Mutual", "Nationwide", "Travelers"],
    "CA": ["State Farm", "GEICO", "Progressive", "Allstate", "USAA",
           "Farmers", "Mercury", "AAA/CSAA", "Wawanesa", "Nationwide"],
    "FL": ["State Farm", "GEICO", "Progressive", "Allstate", "USAA",
           "Farmers", "Liberty Mutual", "Travelers", "Florida Farm Bureau", "Nationwide"],
    "NY": ["GEICO", "State Farm", "Progressive", "Allstate", "USAA",
           "Liberty Mutual", "Travelers", "Nationwide", "Erie Insurance", "NYCM"],
}
GATE10_MIN = 7  # informational completeness bar for top-10 (not enforced on drift)

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


def load_market_share():
    """NAIC PPA market share, keyed by roster name. Returns (weight_fn, floor)."""
    ms = json.load(open(MARKET))
    natl = ms["national"]
    states = ms.get("states", {})
    floor = ms["_meta"]["de_minimis_floor"]

    def weight(st, roster_carrier):
        return (states.get(st, {}).get(roster_carrier)
                or natl.get(roster_carrier)
                or floor)
    return weight


MIN_BOOK = 4000  # mirrors verify_filing_tool_consistency.py

def _too_small(r):
    """A tiny sub-brand filing is not the carrier family's trajectory.
    verify_filing_tool_consistency.py has always skipped these; this script did
    NOT, so drift could move a whole family's offset off a token book -- e.g.
    GA Allstate +5.5% filed by Allstate Indemnity on 434 policyholders would
    have raised the displayed Allstate GA price $2,488 -> $2,624 for everyone."""
    aff = r.get("affected")
    return aff is not None and aff < MIN_BOOK and abs(r.get("overall_pct") or 0) >= 1


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
    ms_weight = load_market_share()
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
        top10 = TOP10_OVERRIDE.get(st, TOP10_DEFAULT)
        covered10 = [c for c in top10 if c in coverage[st]]
        missing10 = [c for c in top10 if c not in coverage[st]]

        # F(s,c) per roster carrier, only from post-anchor filings
        carriers = {}
        not_in_adj = []
        F_by_c = {}
        prem_by_c = {}
        for (s2, rc), rows in by_sc.items():
            if s2 != st:
                continue
            post = [r for r in rows if eff_date(r) and eff_date(r) > anc
                    and r.get("overall_pct") is not None
                    and not r.get("drift_exclude")  # skip segment-only filings (e.g. min-limits) that don't move the standard-coverage model
                    and not _too_small(r)]          # and sub-brand filings that aren't the family's trajectory
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

        # F̄(s): weighted mean of F across tracked (in-ADJ) carriers with post-anchor filings.
        # Weight basis (Layer B), chosen per state so the weights share one unit:
        #   - SERFF written_premium when EVERY participating carrier reports it (GA/SC/TN) — the
        #     actual book each filing covers, the most precise weight.
        #   - NAIC national market share (market_share.json) ONLY when the state has NO premium
        #     signal at all — every participating carrier's WP is null (TX, whose TDI open-data
        #     rows carry no premium). Otherwise F̄ collapses to an equal-weighted mean (a 1.3M-book
        #     State Farm cut == a tiny regional). We do NOT substitute market share when SOME
        #     carriers have WP (e.g. GA): a filing's captured WP is the actual sub-book it covers,
        #     which market share would over-weight (a $2.1M Allstate sub-program != Allstate's full
        #     ~10% GA footprint). Null-WP carriers stay weight-0 there, as before this change.
        Fbar = None
        weight_basis = None
        if F_by_c:
            if any(prem_by_c[c] > 0 for c in F_by_c):
                weights = dict(prem_by_c)
                weight_basis = "serff_written_premium"
            else:
                weights = {c: ms_weight(st, c) for c in F_by_c}
                weight_basis = "naic_market_share"
            wsum = sum(weights.values())
            if wsum > 0:
                Fbar = sum(F_by_c[c] * weights[c] for c in F_by_c) / wsum
            else:
                Fbar = sum(F_by_c.values()) / len(F_by_c)
                weight_basis = "equal"
            for c, e in carriers.items():
                e["Fbar"] = round(Fbar, 5)
                e["weight"] = round(weights.get(c, 0.0), 4)
                e["weight_basis"] = weight_basis
                e["adj_new"] = round(e["adj_old"] * e["F"] / Fbar, 4)
                e["delta"] = round(e["adj_new"] - e["adj_old"], 4)

        level = None
        if Fbar and st in stateavg:
            capped = max(0.90, min(1.10, Fbar))  # ±10%/yr cap
            level = {"stateAvg_old": stateavg[st],
                     "Fbar": round(Fbar, 5),
                     "stateAvg_drifted": round(stateavg[st] * capped, 0),
                     "capped": capped != Fbar,
                     "weight_basis": weight_basis}

        report["states"][st] = {
            "anchor_as_of": anc,
            "top5": top5,
            "top5_covered": covered,
            "gate_pass": gate_pass,
            "top10_covered": covered10,
            "top10_missing": missing10,
            "top10_complete": len(covered10) >= GATE10_MIN,
            "n_post_anchor_carriers": len(carriers) + len(not_in_adj),
            "Fbar": round(Fbar, 5) if Fbar else None,
            "weight_basis": weight_basis,
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
        c10 = "top10 OK" if s["top10_complete"] else "top10 GAP"
        print(f"   top10 {len(s['top10_covered'])}/10  {c10}"
              + (f"  |  missing: {', '.join(s['top10_missing'])}" if s["top10_missing"] else ""))
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
                  f"(F̄={ld['Fbar']}{' capped' if ld['capped'] else ''}, weight={ld['weight_basis']})")
        print()

    if emit:
        json.dump(report, open(OUT, "w"), indent=1)
        print(f"wrote {OUT.name}")
    else:
        print("(dry-run; pass --emit to write proposed_adjustments.json)")


if __name__ == "__main__":
    main()
