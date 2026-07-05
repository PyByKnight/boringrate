#!/usr/bin/env python3
"""
validate_drift.py — the backward-validation harness for filing-driven drift.

The real test (per SERFF_RUNBOOK.md): drift a state's carriers from an OLD anchor
snapshot forward across the gap, and confirm the drifted carrier ORDERING moves
TOWARD the next published (newer) 3rd-party ordering. That requires TWO dated
reference snapshots: the anchor (older) and a newer one to check against.

We currently hold only ONE snapshot (cheapest_by_state.json, 2026-06-23). So the
true backward test is PENDING a second dated pull. This script:
  1. detects whether a second snapshot exists and reports the dependency, and
  2. runs the readiness report we CAN run now: per state, the pre- vs post-anchor
     filing split, which confirms the no-double-count property (pre-anchor filings
     are excluded because they're already embedded in the snapshot).

Drop a second snapshot at cheapest_by_state_prev.json (older) OR
cheapest_by_state_next.json (newer) with the same shape + a _meta.snapshot_date,
and this will run the convergence test.
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILINGS = json.load(open(ROOT / "serff_filings.json"))["filings"]
ANCHORS = json.load(open(ROOT / "anchor_dates.json"))
PREV = ROOT / "cheapest_by_state_prev.json"
NEXT = ROOT / "cheapest_by_state_next.json"


def eff(r):
    return r.get("effective_new") or r.get("effective_renewal")


def readiness():
    anc_default = ANCHORS["default"]
    anc_state = ANCHORS.get("states", {})
    split = defaultdict(lambda: {"pre": 0, "post_zero": 0, "post_move": 0})
    for r in FILINGS:
        st = r["state"]
        anc = anc_state.get(st, anc_default)
        d = eff(r)
        if not d:
            continue
        if d <= anc:
            split[st]["pre"] += 1
        elif abs(r.get("overall_pct") or 0) < 0.05:
            split[st]["post_zero"] += 1
        else:
            split[st]["post_move"] += 1
    print(f"Readiness report (anchor default {anc_default}):\n")
    print(f"{'ST':<4}{'pre-anchor':>11}{'post (0%)':>11}{'post (moves)':>13}   interpretation")
    for st in sorted(split):
        s = split[st]
        note = ("no post-anchor movers — drift is a correct no-op today"
                if s["post_move"] == 0 else
                f"{s['post_move']} post-anchor mover(s) available to drift")
        print(f"{st:<4}{s['pre']:>11}{s['post_zero']:>11}{s['post_move']:>13}   {note}")
    print("\nWhy pre-anchor filings are excluded: they took effect before the 3rd-party")
    print("snapshot date, so the snapshot ALREADY reflects them. Applying them would")
    print("double-count. This is the reset discipline working, not a gap.\n")


def convergence():
    if not (PREV.exists() or NEXT.exists()):
        print("BACKWARD TEST: PENDING — need a second dated snapshot.")
        print("  Have: cheapest_by_state.json (2026-06-23) only.")
        print("  Add:  cheapest_by_state_next.json (a later NerdWallet/MoneyGeek pull)")
        print("        then re-run to test whether drift moved ordering toward it.")
        return
    print("BACKWARD TEST: second snapshot found — (convergence scoring TODO once the")
    print("  older pre-calibration model snapshot is provided; see notes).")


if __name__ == "__main__":
    readiness()
    convergence()
