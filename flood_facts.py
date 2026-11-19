#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'Flood in <state>' section for home + renters state pages, from flood_by_state.json
(FEMA OpenFEMA, fetched by fetch_openfema_flood.py).

Standard homeowners and renters policies exclude flood; this replaces the generic flood advice
cut in the 2026-11-19 prose strip with each state's own federal numbers (memory
boringrate-unique-content-rule). Sentences render only when the data supports them.

    block(line, code, name) -> HTML ("" when the state has no FEMA data)
    inject(html, line, code, name, before) -> (html, ok)   idempotent
"""
import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
START, END = "<!-- flood-facts-start -->", "<!-- flood-facts-end -->"
GUIDE = {"home": ("/home/does-homeowners-insurance-cover-flood-damage.html", "Does homeowners insurance cover flood damage?"),
         "renters": ("/renters/does-renters-insurance-cover-water-damage.html", "What renters insurance pays for water and flood damage")}
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        p = os.path.join(ROOT, "flood_by_state.json")
        _DATA = json.load(open(p)) if os.path.exists(p) else {"_meta": {}, "states": {}}
    return _DATA


def _money(x):
    if x >= 1e9:
        return f"${x / 1e9:.1f} billion"
    if x >= 1e6:
        return f"${x / 1e6:.1f} million"
    return f"${x:,.0f}"


def block(line, code, name):
    d = data()
    s = d["states"].get(code)
    if not s:
        return ""
    y0, y1 = d["_meta"].get("claims_years", [2016, 2025])
    LN = "homeowners" if line == "home" else "renters"
    out = []   # no shared opener: every sentence carries this state's numbers
    if s.get("penetration_pct") is not None and s.get("res_policies"):
        t = (f"Standard {LN} policies exclude flood, and only <strong>{s['penetration_pct']:.1f}%</strong> of "
             f"{name} homes carry a federal flood policy from FEMA&rsquo;s NFIP ({s['res_policies']:,} policies)")
        if s.get("sfha_penetration_pct") is not None:
            t += f"; inside FEMA&rsquo;s high-risk flood zones the share is {s['sfha_penetration_pct']:.0f}%"
        out.append(t + ".")
    if s.get("claims"):
        if s["claims"] >= 50:
            out.append(f"From {y0} to {y1}, NFIP paid <strong>{s['claims']:,}</strong> {name} flood claims totaling "
                       f"<strong>{_money(s['paid'])}</strong>, about {_money(s['avg_paid'])} per claim.")
            if s.get("worst_year_claims", 0) >= 0.25 * s["claims"] and s["claims"] >= 200:
                out.append(f"{s['worst_year']} alone accounted for {s['worst_year_claims']:,} of them.")
            if (s.get("top_event") and (s.get("top_event_claims") or 0) >= 100
                    and not re.match(r"\d{4}-\d{2}-", s["top_event"])):      # skip FEMA internal event codes
                out.append(f"The event with the most claims was {s['top_event']} ({s['top_event_claims']:,}).")
        else:
            out.append(f"Flood claims are rare here: NFIP paid {s['claims']:,} {name} claims from {y0} to {y1}.")
        if line == "renters" and s.get("contents_paid", 0) >= 1e5:
            out.append(f"Contents claims &mdash; the part a renter&rsquo;s flood policy covers &mdash; came to "
                       f"{_money(s['contents_paid'])} of that.")
    if (line == "home" and s.get("top_county") and (s.get("top_county_policies") or 0) >= 500
            and code != "DC"):
        out.append(f"{s['top_county']} {'Parish' if code == 'LA' else 'County'} holds the most policies in the state ({s['top_county_policies']:,}).")
    href, label = GUIDE[line]
    return (f"{START}\n    <h2>Flood insurance in {name}</h2>\n    <p>" + " ".join(out) + "</p>\n"
            f'    <p style="font-size:13px;color:var(--ink-mute);">Source: FEMA OpenFEMA (NFIP claims and policies in force). '
            f'<a class="ca-link" href="{href}">{label}</a></p>\n    {END}')


def inject(html, line, code, name, before):
    html = re.sub(r"\s*" + re.escape(START) + r"[\s\S]*?" + re.escape(END), "", html)
    blk = block(line, code, name)
    if not blk or before not in html:
        return html, False
    i = html.index(before)
    return html[:i] + blk + "\n\n    " + html[i:], True
