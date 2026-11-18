#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Carriers that cut the SAME book more than once - the cumulative-filings angle.

A tracker row shows one filing at a time, so three consecutive Allstate cuts in Ohio
(-5.4%, -3.0%, -3.0%) read as "-3%" while the book is actually ~-11% cheaper. This module
is the single source for that roll-up; gen_rate_tracker.py renders it and anything else
that wants the number should import it rather than re-derive it (memory
boringrate-filter-twin-pattern).

Rules:
  - guards from filing_guards (has_pct, is_driftable, too_small); rate-neutral rows dropped
  - only filings already in effect (effective <= today) - "has cut" must be true today
  - grouped by (carrier, book) using the consistency checker's book_key, so separate legal
    entities are never chained together
  - >= 2 cuts on the book, compounded net (raises on that book included) <= -NET_MIN,
    book size >= filing_guards.MIN_BOOK policyholders
"""
from functools import reduce
from collections import defaultdict
import filing_guards as fg
from verify_filing_tool_consistency import book_key

NET_MIN = 5.0


def repeat_cutters(ledger, state, today=None):
    today = today or fg.today()
    books = defaultdict(list)
    for r in ledger:
        if r.get("state") != state: continue
        if not fg.has_pct(r) or not fg.is_driftable(r) or fg.too_small(r): continue
        if not r.get("affected") and not r["overall_pct"]: continue
        eff = fg.eff_date(r)
        if not eff or eff > today: continue
        books[(r["carrier"], book_key(r))].append(r)
    out = []
    for (carrier, _), rs in books.items():
        rs.sort(key=fg.eff_date)
        cuts = [r for r in rs if r["overall_pct"] < 0]
        if len(cuts) < 2: continue
        net = (reduce(lambda a, r: a * (1 + r["overall_pct"] / 100.0), rs, 1.0) - 1) * 100
        size = max(r.get("affected") or 0 for r in rs)
        if net > -NET_MIN or size < fg.MIN_BOOK: continue
        out.append({"carrier": carrier,
                    "entity": (rs[-1].get("entity") or "").split("(")[0].strip(),
                    "net_pct": round(net, 1), "affected": size, "filings": rs})
    return sorted(out, key=lambda x: x["net_pct"])
