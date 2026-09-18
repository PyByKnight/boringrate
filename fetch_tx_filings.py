#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch Texas rate filings from the TDI open-data API — no clicking, no portal session.

WHY THIS EXISTS: 618 of our 677 filings were pulled by hand through SERFF Filing Access, one
state at a time. Texas does not require that. TDI publishes every personal auto and homeowners
rate filing to `data.texas.gov` as a plain Socrata dataset (`iubg-btfs`) with no terms barrier
and no session — 18,043 rows, updated continuously. We were hand-pulling a state that has an API.

SCOPE, HONESTLY: this is NOT a replacement for the SERFF jacket. The TDI feed carries company,
percent change, effective dates, SERFF id and status — and nothing else. No policyholders
affected, no written premium, no indicated-vs-taken, no max/min spread, no filing narrative. So
Texas rows are thinner than hand-pulled states by design, which is already true of the 36 TX rows
in the ledger. What this buys is COVERAGE and FRESHNESS at zero marginal effort.

DELIBERATELY NOT AUTO-COMMITTING. The ledgers are curated — carrier-family mapping, editorial
notes, and the tool<->filing consistency rule all need judgement. This writes a review file and
prints a diff against what we already hold; appending stays a human decision.

  python3 fetch_tx_filings.py                  # material 2026 filings, report only
  python3 fetch_tx_filings.py --since 2026-01-01 --min-pct 3
  python3 fetch_tx_filings.py --write          # write tx_filings_new.json for review
"""
import argparse, json, urllib.request, urllib.parse, datetime, re, sys, collections

API = "https://data.texas.gov/resource/iubg-btfs.json"
PORTAL = "https://data.texas.gov/d/iubg-btfs"
LINES = {"Personal Automobile": ("auto", "PPA"), "Homeowners": ("home", "HO")}

# company name -> carrier family. Deliberately conservative: an unmapped company is REPORTED,
# not guessed, because a wrong family silently corrupts the tool's drift layer.
FAMILY = [
    ("state farm", "State Farm"), ("geico", "GEICO"), ("government employees", "GEICO"),
    ("progressive", "Progressive"), ("allstate", "Allstate"), ("usaa", "USAA"),
    ("garrison", "USAA"), ("farmers", "Farmers"), ("fire insurance exchange", "Farmers"),
    ("mid-century", "Farmers"), ("foremost", "Farmers"), ("bristol west", "Farmers"),
    ("horace mann", "Horace Mann"), ("teachers insurance", "Horace Mann"),
    ("liberty", "Liberty Mutual"), ("safeco", "Safeco"), ("nationwide", "Nationwide"),
    ("allied", "Nationwide"), ("travelers", "Travelers"), ("american family", "American Family"),
    ("homesite", "Homesite"), ("amica", "Amica"), ("auto-owners", "Auto-Owners"),
    ("erie", "Erie"), ("hartford", "The Hartford"), ("chubb", "Chubb"), ("ace american", "Chubb"), ("ace property", "Chubb"),
    ("texas farm bureau", "Texas Farm Bureau"), ("kemper", "Kemper"), ("mercury", "Mercury"),
    ("national general", "National General"), ("root", "Root Insurance"),
    ("esurance", "Esurance"), ("elephant", "Elephant"), ("republic", "Republic"),
    ("texas fair plan", "Texas FAIR Plan"), ("twia", "Texas FAIR Plan"),
]


def family(name):
    """Match on word boundaries, not bare substrings. A plain `in` test mapped
    "HORACE MANN INSURANCE COMPANY" to Chubb, because the pattern "ace " occurs inside
    "hor-ACE -mann". A wrong family silently corrupts the tool's drift layer, so the
    matcher errs toward returning None (reported as unmapped) over guessing."""
    n = " " + re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip() + " "
    for sub, fam in FAMILY:
        if re.search(r"(?<![a-z])" + re.escape(sub.strip()) + r"(?![a-z])", n):
            return fam
    return None


def pct(r):
    raw = (r.get("percent_change") or "").replace("%", "").strip()
    try:
        return float(raw)
    except ValueError:
        return None


def iso(v):
    return v.split("T")[0] if v else None


def fetch(since, limit=10000):
    where = (f"received_date > '{since}' AND "
             "state_type_of_insurance in('Homeowners','Personal Automobile')")
    url = API + "?" + urllib.parse.urlencode({"$where": where, "$limit": limit,
                                              "$order": "received_date DESC"})
    with urllib.request.urlopen(url, timeout=60) as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-01-01")
    ap.add_argument("--min-pct", type=float, default=3.0,
                    help="material threshold, matching the runbook's +-3%% rule")
    ap.add_argument("--include-pending", action="store_true",
                    help="include filings not yet Closed (default: approved only)")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    try:
        rows = fetch(args.since)
    except Exception as e:
        sys.exit(f"TDI API unreachable: {e}")

    have = set()
    for f in ("serff_filings.json", "serff_home_filings.json"):
        try:
            have |= {r["tracking"] for r in json.load(open(f))["filings"]}
        except Exception:
            pass

    # TDI emits ONE ROW PER COMPANY, so a multi-company filing repeats its serff_id with a
    # different percentage each time (FARM-134961095 appears 4x at 6.2/5.4/2.2/6.2%). Left
    # as-is that double-counts one filing as several. Collapse per tracking below, mirroring
    # how the SERFF pipeline handles multi-entity jackets — except TDI publishes no premium or
    # policy counts, so a premium-weighted average is impossible here. We take the dominant
    # (largest-magnitude) entity and record the entity count and spread, rather than inventing
    # a weighting the data cannot support.
    grouped = collections.defaultdict(list)
    for r in rows:
        if r.get("serff_id"):
            grouped[r["serff_id"]].append(r)

    kept, unmapped, skipped = [], collections.Counter(), collections.Counter()
    for r in rows:
        p = pct(r)
        if p is None:
            skipped["no percent"] += 1
            continue
        if not args.include_pending and r.get("status") != "Closed":
            skipped["not approved"] += 1
            continue
        if abs(p) < args.min_pct:
            skipped["below threshold"] += 1
            continue
        trk = r.get("serff_id")
        if not trk or trk in have:
            skipped["already in ledger"] += 1
            continue
        line, product = LINES[r["state_type_of_insurance"]]
        fam = family(r["company_name"])
        if not fam:
            unmapped[r["company_name"]] += 1
            continue
        siblings = grouped.get(trk, [r])
        # only emit once per tracking, from its largest-magnitude entity
        dom = max(siblings, key=lambda x: abs(pct(x) or 0))
        if dom is not r:
            skipped["sibling of a multi-entity filing"] += 1
            continue
        ent = r["company_name"].title()
        if len(siblings) > 1:
            spread = [pct(x) for x in siblings if pct(x) is not None]
            ent += f" (dominant of {len(siblings)} entities; {min(spread):+.1f}% to {max(spread):+.1f}%)"
        kept.append({
            "state": "TX", "line": line, "carrier": fam,
            "entity": ent, "tracking": trk, "url": PORTAL,
            "product": product, "filing_type": None,
            "disposition_date": iso(r.get("received_date")),
            "effective_new": iso(r.get("effective_date_new_business")),
            "effective_renewal": iso(r.get("effective_date_renewal")),
            "overall_pct": p, "indicated_pct": None, "prior_revision_pct": None,
            "written_premium": None, "written_premium_change": None, "affected": None,
            "count_basis": None, "coverage_changes": None, "premium_as_of": None,
            "recorded_date": datetime.date.today().isoformat(),
            "status": r.get("status"),
            "source_note": "TX TDI open data (data.texas.gov iubg-btfs); no PH/premium; file-and-use.",
            "note": None,
        })

    kept.sort(key=lambda r: -abs(r["overall_pct"]))
    print(f"TDI rows since {args.since}: {len(rows)}")
    for k, v in skipped.most_common():
        print(f"  skipped, {k:<20} {v}")
    print(f"\nNEW material filings not in our ledger: {len(kept)}")
    print(f"{'':2}{'pct':>8}  {'line':<5} {'carrier':<20} {'effective':<11} tracking")
    for r in kept[:40]:
        print(f"  {r['overall_pct']:+7.1f}%  {r['line']:<5} {r['carrier']:<20} "
              f"{str(r['effective_new'] or '—'):<11} {r['tracking']}")
    if len(kept) > 40:
        print(f"  ... and {len(kept) - 40} more")

    if unmapped:
        print(f"\nUNMAPPED companies ({sum(unmapped.values())} filings) — add to FAMILY or ignore "
              f"as non-roster writers:")
        for name, n in unmapped.most_common(12):
            print(f"  {n:>3}  {name}")

    if args.write:
        out = "tx_filings_new.json"
        json.dump({"_meta": {
            "purpose": "Candidate TX rows fetched from the TDI open-data API. REVIEW before "
                       "merging into serff_filings.json / serff_home_filings.json — carrier "
                       "family mapping and editorial notes need a human pass.",
            "fetched": datetime.date.today().isoformat(),
            "since": args.since, "min_pct": args.min_pct, "count": len(kept),
        }, "filings": kept}, open(out, "w"), indent=1)
        print(f"\nwrote {out} — review, then merge deliberately.")
    else:
        print("\n(report only; --write to emit tx_filings_new.json)")


if __name__ == "__main__":
    main()
