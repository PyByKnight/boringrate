#!/usr/bin/env python3
"""Shared citation helpers so the /rate-filings/ ledger and every data page agree on
the SAME per-filing anchor. Keyed on the SERFF tracking number (unique + stable, present
on 100% of rows), so no cross-generator dedup drift.

  anchor(row) -> "fl-state-farm-923648"   (state-carrier-<tracking tail>)
  used by: gen_rate_filings_rollup.py (emits id=) and the data-page generators (link to #id)
"""
import re


def _slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def anchor(row):
    """Deterministic per-filing anchor id. row needs keys: state, carrier, tracking."""
    st = (row.get("state") or "").lower()
    car = _slug(row.get("carrier"))
    trk = re.sub(r"[^A-Za-z0-9]", "", row.get("tracking") or "")
    tail = trk[-6:].lower()
    return "-".join(x for x in (st, car, tail) if x) or "filing"
