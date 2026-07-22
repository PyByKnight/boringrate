#!/usr/bin/env python3
"""Per-entity share of a carrier's book within a state ("% of brand").

A rate filing almost always covers 100% of the filing entity's book (median
share-of-book across OH filings is 100.0%), so "% of book" is a column of
100s and tells a reader nothing. The useful question is how big that ENTITY
is inside the carrier's overall state presence: Allstate Northbrook's +2.5%
covers 1,229 of Allstate's 159,529 Ohio customers — 0.8% of the brand — which
is what makes a token sub-brand filing visibly token.

Denominator = sum of the latest-effective book for each DISTINCT entity of
that carrier in that state, excluding rows flagged `entity_aggregate` (those
collapse several companies into one row, so mixing them with entity rows
double-counts: IL State Farm computed 6.4M policies, more than Illinois has
drivers, by adding the same book twice).

Only OH/IL/PA carry entity detail today — the other states were pulled before
the ledger stored per-entity rows and their jackets are no longer on disk.
Those return None, and callers must render an em dash rather than invent a
number.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _entity_key(row):
    """Entity name with annotations stripped — those live in parentheses."""
    return (row.get("entity") or "").split("(")[0].strip().lower()


def build(filings=None):
    """-> (brand_totals, entity_books) keyed for lookup.

    brand_totals[(state, carrier)]      = total policyholders across entities
    entity_books[(state, carrier, ent)] = that entity's latest-effective book
    """
    if filings is None:
        filings = json.load(open(ROOT / "serff_filings.json"))["filings"]
    latest = {}
    for r in filings:
        if r.get("entity_aggregate"):
            continue                      # collapsed multi-company row — not an entity
        if not r.get("affected"):
            continue                      # rate-neutral rows report 0 affected
        k = (r["state"], r["carrier"], _entity_key(r))
        eff = r.get("effective_new") or r.get("effective_renewal") or ""
        if k not in latest or eff > latest[k][0]:
            latest[k] = (eff, r["affected"])
    entity_books = {k: v[1] for k, v in latest.items()}
    brand_totals, counts = {}, {}
    for (st, car, _), aff in entity_books.items():
        brand_totals[(st, car)] = brand_totals.get((st, car), 0) + aff
        counts[(st, car)] = counts.get((st, car), 0) + 1
    # A carrier with one captured entity is trivially 100% — that is an artifact
    # of what we captured, not a fact about the brand. Suppress it.
    brand_totals = {k: v for k, v in brand_totals.items() if counts[k] >= 2}
    return brand_totals, entity_books


def share(row, brand_totals, entity_books):
    """Fraction of the carrier's state book this row's entity represents.

    None when unknowable: an aggregate row, a state without entity detail, or
    a rate-neutral row with no policyholder count.
    """
    if row.get("entity_aggregate") or not row.get("affected"):
        return None
    st, car = row.get("state"), row.get("carrier")
    total = brand_totals.get((st, car))
    if not total:
        return None
    mine = entity_books.get((st, car, _entity_key(row)))
    if not mine:
        return None
    return min(mine / total, 1.0)


def fmt(frac):
    """Render for a table cell. '<0.1%' beats '0.0%' for a real but tiny book."""
    if frac is None:
        return "&mdash;"
    pct = frac * 100
    if pct >= 99.95:
        return "100%"
    if pct < 0.1:
        return "&lt;0.1%"
    return f"{pct:.1f}%"


if __name__ == "__main__":
    bt, eb = build()
    have = sorted({st for st, _ in bt})
    print("states with entity detail:", have)
    for k in sorted(eb, key=lambda k: -eb[k])[:10]:
        st, car, ent = k
        print(f"  {st} {car:<14}{eb[k]:>10,}  {fmt(eb[k]/bt[(st,car)]):>7}  {ent[:34]}")
