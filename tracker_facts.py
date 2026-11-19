#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""State-specific lead facts for the auto + home rate-change trackers.

Why (2026-11-19 prose audit): the trackers shared 7 identical disclaimer/CTA sentences, 50-62%
of their prose. This replaces that wrapper with facts only this state's filings can produce, so
each tracker's text differs because its data differs (memory boringrate-unique-content-rule).
Sentences are included only when the data supports them - never filler.

    facts(changes, name, line) -> HTML <p> or ""
    changes: dicts with carrier, pct (signed or unsigned + dir), affected, effective
"""
from html import escape as esc

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _d(iso):
    if not iso:
        return ""
    p = iso.split("-")
    return f"{MONTHS[int(p[1])]} {p[0]}" if len(p) >= 2 else p[0]


def _norm(c):
    pct = c.get("overall_pct", c.get("pct"))
    if pct is None:
        return None
    if "overall_pct" not in c and c.get("dir") == "decrease":
        pct = -abs(pct)
    return {"carrier": c["carrier"], "pct": float(pct), "affected": c.get("affected") or 0,
            "eff": c.get("effective_new") or c.get("effective")}


def _pct(p):
    return f"{'+' if p > 0 else '&minus;'}{abs(p):.1f}%"


def facts(changes, name, line="auto"):
    rows = [r for r in (_norm(c) for c in changes) if r]
    if not rows:
        return ""
    out = []
    sized = [r for r in rows if r["affected"]]
    tot = sum(r["affected"] for r in sized)
    if len(sized) >= 3 and tot:
        w = sum(r["pct"] * r["affected"] for r in sized) / tot
        tone = ("Most of the market moved up" if w >= 1 else "Most of the market moved down" if w <= -1
                else "Raises and cuts roughly offset")
        # no policy total: a carrier that filed twice would count its book twice
        out.append(f"{tone}: weighted by the policies each one touches, the {len(sized)} {esc(name)} filings "
                   f"that report a book size average <strong>{_pct(w)}</strong>.")
    big = max(sized, key=lambda r: r["affected"]) if sized else None
    if big:
        out.append(f"The change reaching the most customers is {esc(big['carrier'])}&rsquo;s "
                   f"<strong>{_pct(big['pct'])}</strong> on {big['affected']:,} policies"
                   + (f" ({_d(big['eff'])})." if big["eff"] else "."))
    cuts = [r for r in rows if r["pct"] < 0]
    if cuts:
        c = min(cuts, key=lambda r: r["pct"])
        if not big or c["carrier"] != big["carrier"] or c["pct"] != big["pct"]:
            out.append(f"Deepest cut: {esc(c['carrier'])} at <strong>{_pct(c['pct'])}</strong>"
                       + (f" &mdash; worth a quote if you have not checked it lately." if c["pct"] <= -3 else "."))
    else:
        out.append(f"No carrier we track has cut {esc(name)} {line} rates this year.")
    latest = max((r for r in rows if r["eff"]), key=lambda r: r["eff"], default=None)
    if latest and latest is not big:
        out.append(f"Most recent: {esc(latest['carrier'])} {_pct(latest['pct'])}, effective {_d(latest['eff'])}.")
    return '<p style="max-width:660px;">' + " ".join(out) + "</p>"


# One-line source note, shared on purpose and kept short: the facts above carry the page.
NOTE = ('<p style="font-size:13px;color:var(--ink-mute);">Approved statewide-average filings from the state '
        'insurance department, each linked to its source; your own change depends on your {what}. '
        '<a href="/methodology.html">Methodology</a>.</p>')
