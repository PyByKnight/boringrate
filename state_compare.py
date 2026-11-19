#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'How <state> compares' facts for home + renters state pages, from the tool's own model.

Why (2026-11-19): after the templated-prose strip, home state pages were ~280 words and renters
~230. These are facts only this state's page can carry (memory boringrate-unique-content-rule),
read live from home/index.html / renters/index.html so they can never contradict the tool:
  - rank of the state average among 51
  - bordering states' averages (BORDERS from patch_renters_nearby.py)
  - carriers priced furthest under / over their own national level here (STATE_CARRIER_ADJ)
  - regional carriers on the roster that write here (states list <= REGIONAL_MAX)
Each sentence only renders when the data supports it.

    block(line, code) -> HTML section ("" if nothing to say)
"""
import os, re
from patch_renters_nearby import BORDERS

ROOT = os.path.dirname(os.path.abspath(__file__))
REGIONAL_MAX = 15        # a carrier writing in <= 15 states is regional, not national
ADJ_MIN = 0.05           # only call out carriers >= 5% off their national price
CFG = {"home": ("home/index.html", "HOME_STATE_DATA = {", "HOME_CARRIERS = [", "homeowners", "home"),
       "renters": ("renters/index.html", "RENTERS_STATE_DATA = {", "RENTERS_CARRIERS = [", "renters", "renters")}
START, END = "<!-- state-compare-start -->", "<!-- state-compare-end -->"


def _block(s, start, end="\n};"):
    i = s.index(start); return s[i + len(start):s.index(end, i)]


_CACHE = {}


def model(line):
    if line in _CACHE:
        return _CACHE[line]
    path, sd, cars, _, _ = CFG[line]
    s = open(os.path.join(ROOT, path), encoding="utf-8").read()
    states = {m.group(1): (m.group(2), int(m.group(3)))
              for m in re.finditer(r'"([A-Z]{2})":\s*\{name:\s*"([^"]+)",\s*avg:\s*(\d+)', _block(s, sd))}
    carriers = []
    for chunk in re.split(r"\n  \{", _block(s, cars, "\n];")):
        nm = re.search(r'name:\s*"([^"]+)"', chunk)
        if not nm:
            continue
        st = re.search(r"states:\s*\[([^\]]*)\]", chunk)
        carriers.append((nm.group(1), set(re.findall(r'"([A-Z]{2})"', st.group(1))) if st else None))
    adj = {m.group(1): {c: float(v) for c, v in re.findall(r'"([^"]+)":\s*([0-9.]+)', m.group(2))}
           for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', _block(s, "STATE_CARRIER_ADJ = {"))}
    _CACHE[line] = (states, carriers, adj)
    return _CACHE[line]


def slug(name):
    return name.lower().replace(".", "").replace(" ", "-")


def _ord(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _join(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def block(line, code):
    states, carriers, adj = model(line)
    if code not in states:
        return ""
    name, avg = states[code]
    _, _, _, LN, dirn = CFG[line]
    out = []
    order = sorted(states, key=lambda c: -states[c][1])
    r = order.index(code) + 1
    n = len(order)
    if r <= n // 2:
        out.append(f"{name} is the <strong>{_ord(r)} most expensive</strong> state for {LN} insurance of the {n} we price.")
    else:
        out.append(f"{name} is the <strong>{_ord(n - r + 1)} cheapest</strong> state for {LN} insurance of the {n} we price.")
    by_slug = {slug(v[0]): c for c, v in states.items()}
    nb = [by_slug[s] for s in BORDERS.get(slug(name), []) if s in by_slug]
    if nb:
        nb.sort(key=lambda c: states[c][1])
        parts = [f'<a href="/{dirn}/state/{slug(states[c][0])}.html">{states[c][0]}</a> ${states[c][1]:,}' for c in nb]
        lo, hi = states[nb[0]][1], states[nb[-1]][1]
        where = ("cheaper than every bordering state" if avg < lo else
                 "more expensive than every bordering state" if avg > hi else
                 "in the middle of its neighbors")
        out.append(f"At ${avg:,}/yr it is {where}: {_join(parts)}.")
    roster = {c for c, st in carriers if st is None or code in st}
    tilt = {c: v for c, v in adj.get(code, {}).items() if c in roster}
    if tilt:
        lo = min(tilt.items(), key=lambda x: x[1])
        hi = max(tilt.items(), key=lambda x: x[1])
        bits = []
        if lo[1] <= 1 - ADJ_MIN:
            bits.append(f"{lo[0]} prices {name} about <strong>{round((1 - lo[1]) * 100)}% below</strong> its own national level")
        if hi[1] >= 1 + ADJ_MIN:
            bits.append(f"{hi[0]} prices it about <strong>{round((hi[1] - 1) * 100)}% above</strong>" if bits else
                        f"{hi[0]} prices {name} about <strong>{round((hi[1] - 1) * 100)}% above</strong> its own national level")
        if bits:
            out.append("In our model, " + ", while ".join(bits) + ".")
    regional = sorted(c for c, st in carriers if st and code in st and len(st) <= REGIONAL_MAX)
    if regional:
        out.append(f"Regional carriers in our ranking that write here: {_join(regional)}"
                   " &mdash; often missing from national comparison sites.")
    return (f"{START}\n    <h2>How {name} compares</h2>\n    <p>" + " ".join(out) + f"</p>\n    {END}")


def inject(html, line, code, before):
    """Idempotent: drop any existing block, insert a fresh one before the `before` marker."""
    html = re.sub(r"\s*" + re.escape(START) + r"[\s\S]*?" + re.escape(END), "", html)
    blk = block(line, code)
    if not blk or before not in html:
        return html, False
    i = html.index(before)
    return html[:i] + blk + "\n\n    " + html[i:], True


if __name__ == "__main__":
    import sys
    for code in sys.argv[2:] or ["OK", "OH", "VT"]:
        print(re.sub(r"<[^>]+>", "", block(sys.argv[1] if len(sys.argv) > 1 else "home", code)), "\n")
