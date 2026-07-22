#!/usr/bin/env python3
"""Add per-ENTITY rows to serff_filings.json for jackets we only stored the
dominant entity for. ADD-ONLY: never edits or deletes an existing row, so the
hand-curated annotations in IL/PA ("aggregate fake 0%", "6 cos combined") and
their deliberate multi-entity collapses survive untouched.

Skip rule: if the existing row's affected/written_premium already matches the
SUM across the jacket's entities, that row is an aggregate — adding siblings
would double-count. Only expand rows that represent a single entity.
"""
import json, sys, re
from pathlib import Path

S = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
DRY = "--emit" not in sys.argv
led = json.load(open("serff_filings.json"))
rows = led if isinstance(led, list) else led["filings"]
by_track = {}
for r in rows:
    p = r["tracking"].split("-")
    by_track.setdefault(f"{p[0]}-{p[1]}" if len(p) >= 2 else r["tracking"], []).append(r)

def close(a, b, tol=0.02):
    if not a or not b: return False
    return abs(a - b) / max(abs(a), abs(b)) < tol

added, skipped_agg, skipped_have = [], [], 0
for st in ("OH", "IL", "PA"):
    parsed = json.load(open(S / f"{st}_parsed.json"))
    for j in parsed:
        ents = [c for c in j["companies"] if c["overall_pct"] is not None]
        if len(ents) < 2: continue
        existing = by_track.get(j["tracking"], [])
        if not existing: continue
        if len(existing) > 1: skipped_have += 1; continue      # already expanded
        base = existing[0]
        sum_ph = sum(c["affected"] or 0 for c in ents)
        sum_wp = sum(c["written_premium"] or 0 for c in ents)
        if close(base.get("affected"), sum_ph) or close(base.get("written_premium"), sum_wp):
            skipped_agg.append((st, j["tracking"], base["entity"][:48])); continue
        # identify which entity the existing row already represents
        def same(c):
            return (close(c["affected"], base.get("affected")) or
                    close(c["written_premium"], base.get("written_premium")))
        missing = [c for c in ents if not same(c)]
        n = 2
        for c in missing:
            row = dict(base)
            row["tracking"] = f'{j["tracking"]}-{n}'; n += 1
            row["entity"] = c["entity"].replace("Rate Premium for ", "").strip()
            row["overall_pct"] = c["overall_pct"]
            row["indicated_pct"] = c["indicated_pct"]
            row["affected"] = c["affected"]
            row["written_premium"] = c["written_premium"]
            row["written_premium_change"] = c["written_premium_change"]
            row.pop("drift_exclude", None)
            if c["overall_pct"] == 0.0:
                row["drift_exclude"] = True
            added.append(row)

print(f"would add {len(added)} entity rows")
print(f"  skipped {len(skipped_agg)} aggregate rows (would double-count):")
for st, t, e in skipped_agg[:8]: print(f"     {st} {t}  {e}")
print(f"  skipped {skipped_have} jackets already expanded")
import collections
print("\nby state:", dict(collections.Counter(r["state"] for r in added)))
if not DRY:
    rows.extend(added)
    json.dump(led, open("serff_filings.json", "w"), indent=1)
    print(f"\nWROTE. ledger now {len(rows)} rows")
