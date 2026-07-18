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


def portal_url(row):
    """Stable external link to the primary source.

    SERFF Filing Access deep links (filingSummary.xhtml?filingId=…) are session-bound and
    expire to sessionExpired.xhtml, so we point at the state's Filing Access landing page
    instead — the reader accepts the disclaimer there and searches by the tracking number we
    display. Non-SERFF sources (TX open data, CA CDI, FL FLOIR, press) keep their working URL.
    """
    url = row.get("url") or ""
    st = (row.get("state") or "").upper()
    if "filingaccess.serff.com" in url and st:
        return f"https://filingaccess.serff.com/sfa/home/{st}"
    return url
