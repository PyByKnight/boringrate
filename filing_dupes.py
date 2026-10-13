#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared near-duplicate detection for the state open-data feeds (TX, CA, IL).

WHY THIS EXISTS. Both feeds collapse repeated rows per SERFF tracking number, which handles a
multi-company filing published as one tracking. It does NOT handle the other shape: a carrier
filing ONE rate action as SEVERAL tracking numbers, one per writing entity.

California's USAA is the worked example. The ledger already holds

    USAA-134678224  "USAA / Casualty / General Indemnity"  +6.9%  CA home  closed 2026-02-06

as a single aggregated row. The CDI workbook also lists

    USAA-134678302  Garrison Property & Casualty           +6.9%  CA home  closed 2026-02-06
    USAA-134678297  USAA General Indemnity                 +6.9%  CA home  closed 2026-02-06

Those are the same rate action under sibling trackings. Per-tracking dedupe cannot see it, so
both read as brand-new filings and merging them would have counted USAA's one CA home increase
three times — inflating the filing count, and (in a state where drift were possible) averaging
a carrier's move over duplicate rows.

DELIBERATELY A WARNING, NOT A SKIP. Two filings on one day at one percentage can legitimately
be distinct (a carrier splitting HO-3 and HO-6 programs). A false skip silently loses a real
filing, which is worse than a flag a human clears in five seconds. So the row is kept and
annotated with `possible_duplicate_of`, and the caller prints it for review.

This lives in its own module because the guards keep getting added to one feed and missed in
its twin (see memory: the filter-twin pattern — four instances so far in the SERFF scripts).
"""
import json

LEDGERS = ("serff_filings.json", "serff_home_filings.json")


def load_ledger_rows(paths=LEDGERS):
    rows = []
    for p in paths:
        try:
            rows += json.load(open(p))["filings"]
        except Exception:
            pass
    return rows


def _key(state, carrier, line, pct, disposition):
    """Same state + family + line + percentage + disposition date."""
    try:
        p = round(float(pct), 2)
    except (TypeError, ValueError):
        p = None
    return (state, carrier, line, p, disposition)


def annotate(candidates, ledger_rows=None):
    """Tag each candidate that matches an existing ledger row on the key above.

    Mutates and returns `candidates`; returns the list of flagged rows as well.
    `line` is compared loosely: ledger auto rows carry no `line` field at all
    (serff_filings.json IS the auto ledger), so a missing value means "auto".
    """
    ledger_rows = load_ledger_rows() if ledger_rows is None else ledger_rows
    seen = {}
    for r in ledger_rows:
        k = _key(r.get("state"), r.get("carrier"), r.get("line") or "auto",
                 r.get("overall_pct"), r.get("disposition_date"))
        if k[3] is not None and k[4]:
            seen.setdefault(k, r["tracking"])

    flagged = []
    for c in candidates:
        k = _key(c.get("state"), c.get("carrier"), c.get("line") or "auto",
                 c.get("overall_pct"), c.get("disposition_date"))
        hit = seen.get(k)
        if hit and hit != c.get("tracking"):
            c["possible_duplicate_of"] = hit
            flagged.append(c)
    return candidates, flagged


def report(flagged):
    if not flagged:
        return
    print(f"\n⚠ {len(flagged)} candidate(s) look like the SAME rate action already in the "
          f"ledger under a sibling tracking number — same state/carrier/line/percent/"
          f"disposition date. Verify before merging; do not merge blind:")
    for c in flagged:
        print(f"  {c['tracking']:20} {c['carrier']:<18} {c['overall_pct']:+.1f}% "
              f"{c.get('disposition_date')}  ~=  {c['possible_duplicate_of']}")
