#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Canonical guards for anything that reads the SERFF filing ledgers.

WHY THIS EXISTS. Seven times now a guard has been added to one script and left out
of its twin — and the twin was usually the one that *writes prices*, while the
script with the guard only *reported*. The safest-looking script was the strictest
and the live one was the loosest. See memory boringrate-filter-twin-pattern.

The fix pattern is the one that worked for filing_dupes.py (instance 6): the guard
lives in ONE module that every caller imports, so a new consumer inherits it
instead of re-deriving it. Change a rule here and every script moves together.

Each guard is deliberately small and pure so callers can compose them:

    import filing_guards as fg

    rows = [r for r in ledger
            if fg.has_pct(r) and fg.is_driftable(r)
            and fg.in_window(r, anchor, fg.today())]

Do not re-implement any of these inline. If a caller genuinely needs different
behaviour, add a named parameter here and say why — that keeps the divergence
visible in one file instead of silently forking across six.
"""
from datetime import date

# A sub-brand filing on a token book is not the carrier family's trajectory.
# Origin: GA Allstate +5.5% filed by Allstate Indemnity on 434 policyholders would
# have moved the displayed Allstate GA price $2,488 -> $2,624 for everyone (571ac8c7).
MIN_BOOK = 4000

# Below this the filing is treated as noise rather than a rate action, so a tiny
# book only disqualifies a filing that actually moves the number.
MIN_PCT = 1.0

# Carriers must have filed in at least this many DISTINCT states before filings
# override a static score — one state's many filings is not cross-state signal.
COVERAGE_MIN = 3


def today():
    """Indirection so callers share one notion of 'now' and tests can pin it."""
    return date.today().isoformat()


def eff_date(row):
    """Effective date of a filing: new business first, else renewal."""
    return row.get("effective_new") or row.get("effective_renewal")


def has_pct(row, allow_zero=True):
    """Row carries a usable overall percentage.

    allow_zero=False additionally drops 0% filings — the home drift path treats a
    0% filing as nothing to apply, while stability scoring counts it as 'held flat'.
    """
    p = row.get("overall_pct")
    if p is None:
        return False
    return True if allow_zero else p not in (0, 0.0)


def is_driftable(row):
    """False for segment-only / unrepresentative filings flagged in the ledger.

    `drift_exclude` marks filings (e.g. minimum-limits-only programs) that are real
    but must not move a standard-coverage model. Origin: the GA min-limits fix.
    """
    return not row.get("drift_exclude")


def too_small(row, min_book=MIN_BOOK, min_pct=MIN_PCT):
    """True when the filing's book is too small to represent the carrier family."""
    aff = row.get("affected")
    return (aff is not None and aff < min_book
            and abs(row.get("overall_pct") or 0) >= min_pct)


def in_window(row, anchor, upto=None):
    """Filing took effect after `anchor` and is already in force.

    The upper bound is the guard that is repeatedly missed: without it a filing
    effective next month moves today's price (924bda09 — GA Liberty Mutual +3.4%
    effective 2026-08-31 would have priced in July).
    """
    eff = eff_date(row)
    if not eff:
        return False
    return anchor < eff <= (upto or today())


def drift_rows(ledger, anchor, upto=None, allow_zero=True,
               min_book=MIN_BOOK, min_pct=MIN_PCT):
    """The full guard stack for 'which filings may move a price'.

    This is the composition every mutator should use. Keeping it here means a new
    price-writing script cannot accidentally ship with three of the four guards.
    """
    return [r for r in ledger
            if has_pct(r, allow_zero=allow_zero)
            and is_driftable(r)
            and not too_small(r, min_book=min_book, min_pct=min_pct)
            and in_window(r, anchor, upto)]


def behavior_rows(ledger, allow_zero=True):
    """Filings usable as evidence of a carrier's RATE BEHAVIOUR (stability scoring).

    Deliberately WEAKER than drift_rows, and the difference is the point:

      drift_rows     answers "what should the displayed price be today?"
                     -> a 434-policyholder sub-brand filing must not move a whole
                        family's price, and a filing effective next month is not
                        in force. Both are excluded.

      behavior_rows  answers "does this carrier raise rates, and how often?"
                     -> a small filing is still evidence of behaviour, and a filed
                        increase is evidence the day it is FILED, not the day it
                        takes effect. Both are kept.

    Applying the book-size floor here was measured and rejected (2026-10-15): it
    would drop every filing for Clearcover, Hugo, Mercury, Berkley, PURE, AIG and
    others, pushing them under COVERAGE_MIN so they vanish from scoring entirely —
    less accurate, not more.

    This divergence is intentional. It lives here, named and explained, so it
    cannot be mistaken for the accidental kind that caused instances 1-9.
    """
    return [r for r in ledger if has_pct(r, allow_zero=allow_zero) and is_driftable(r)]


def gated_carriers(by_carrier_states, roster, coverage_min=COVERAGE_MIN):
    """Carriers filed in >= coverage_min DISTINCT states AND present in the roster.

    `by_carrier_states` maps carrier -> a set/collection of state codes. Counting
    distinct states (not filings) is the point: one state filing five times is not
    cross-state signal.
    """
    return {c for c, states in by_carrier_states.items()
            if len(states) >= coverage_min and c in roster}
