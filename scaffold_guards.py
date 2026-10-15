#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guards for generators that clone a real page as their HTML scaffold.

WHY THIS EXISTS. Several generators build pages by cloning an existing page and
replacing regions of it. gen_metro_base.html IS a copy of the old atlanta.html, and
renters/state/colorado.html is a live Colorado page. Anything stamped site-wide also
lands in the scaffold, so the clone inherits content belonging to a DIFFERENT place.

This has shipped four times ("the Atlanta leak"). The fourth, in bc29639f, put

    <h2>Cheapest car insurance carriers in Atlanta</h2>

on all 16 article/rate-changes/ pages — telling Nevada shoppers the Atlanta average,
on the best-converting section of the site. Each time the fix was to add a strip to
ONE generator; each time the next generator to clone the same scaffold lacked it.

So the strip lives here, and verify_scaffold_leaks.py checks the OUTPUT rather than
trusting every generator to remember. See memory boringrate-filter-twin-pattern.
"""
import re

# Region stamped by move_ctas_up.py; place-specific, must never survive a clone.
RANKINGS = re.compile(r"<!-- state-rankings-start -->.*?<!-- state-rankings-end -->\s*", re.S)


def strip_rankings(html):
    """Remove the scaffold's place-specific rankings block.

    Safe to call unconditionally: a generator that legitimately injects its own
    block should call this FIRST and then insert, so the scaffold's copy can never
    be mistaken for its own.
    """
    return RANKINGS.sub("", html)


def rankings_place(html):
    """The place named by a page's rankings block, or None if it has no block."""
    m = RANKINGS.search(html)
    if not m:
        return None
    h2 = re.search(r"<h2>\s*Cheapest [^<]*? in ([^<]+?)\s*</h2>", m.group(0))
    return h2.group(1).strip() if h2 else None


def page_place(html):
    """The place a page is actually about, taken from its own <h1>."""
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if not m:
        return None
    t = re.sub(r"<[^>]+>", "", m.group(1))
    return re.sub(r"\s+", " ", t).strip()


def _norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _head(place):
    """Leading place token: 'Tampa-St. Pete' -> 'Tampa', 'Charleston, WV' -> 'Charleston'.

    Block labels carry the disambiguated form while the h1 uses the short one, so
    comparing the whole string produces false positives on every compound metro.
    """
    return _norm(re.split(r"[,/\u2013\u2014]", place)[0])


def leaks(html):
    """True when the page's rankings block names a place the page is not about.

    Compares the block's leading place token against the page's own <h1>. Atlanta
    on a Nevada page fails; 'Tampa-St. Pete' on the Tampa page does not.
    """
    rp, pp = rankings_place(html), page_place(html)
    if not rp or not pp:
        return False
    head = _head(rp)
    return bool(head) and head not in _norm(pp)
