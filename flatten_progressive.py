#!/usr/bin/env python3
"""
flatten_progressive.py — fix Progressive's offset to match real data (2026-06-23).

Earlier this session Progressive's offset was steepened (1.04-0.22*pct) tuned
against the IN-HOUSE editorial rankings page. The real reference
(cheapest_by_state.json) shows Progressive is the actual cheapest in 6 states
(IN, ME, NV, NY, NC, OK) — several low-cost — so the steepening (which made it
EXPENSIVE in low-cost states) fought the data and buried it (ranks 9-12 there).

Fix = treat Progressive like the home-turf regional model:
  - drop ALL its per-state STATE_CARRIER_ADJ entries (the steepening + originals),
  - base 0.95 -> 0.92 (competitive value tier),
  - add a home-turf 0.82 offset in its 6 real-#1 states.

Measured vs the reference: top-5 71% -> 83%, median rank 3 -> 2, Progressive #1 in
all 6 home states. Idempotent (aborts if Progressive base already 0.92).
"""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent / "index.html"
HOME = ["IN", "ME", "NV", "NY", "NC", "OK"]
HOME_OFFSET = 0.82


def span(s, start, end="\n};"):
    i = s.index(start)
    return i, s.index(end, i)


def main():
    s = SRC.read_text(encoding="utf-8")
    if re.search(r'name:\s*"Progressive"[^}]*?base:\s*0\.92\b', s):
        raise SystemExit("Already flattened (Progressive base==0.92). Aborting.")

    # base 0.95 -> 0.92
    i, j = span(s, "CARRIERS_STANDARD = [", "\n];")
    nb = re.sub(r'(name:\s*"Progressive"[^}]*?base:\s*)[0-9.]+',
                lambda m: m.group(1) + "0.92", s[i:j], count=1)
    s = s[:i] + nb + s[j:]

    # rewrite STATE_CARRIER_ADJ: drop all Progressive entries, then add home-turf
    i, j = span(s, "STATE_CARRIER_ADJ = {")
    lines = s[i:j].split("\n")
    for idx, line in enumerate(lines):
        m = re.match(r'(\s*)"([A-Z]{2})":\s*\{(.*)\}(,?)\s*$', line)
        if not m:
            continue
        indent, code, inner, comma = m.groups()
        pairs = re.findall(r'"([^"]+)":\s*([0-9.]+)', inner)
        pairs = [(c, v) for c, v in pairs if c != "Progressive"]
        if code in HOME:
            pairs.append(("Progressive", "%g" % HOME_OFFSET))
        body = ", ".join('"%s": %s' % (c, v) for c, v in pairs)
        lines[idx] = '%s"%s": { %s }%s' % (indent, code, body, comma) if body \
            else '%s"%s": {}%s' % (indent, code, comma)
    s = s[:i] + "\n".join(lines) + s[j:]

    SRC.write_text(s, encoding="utf-8")
    print("Progressive: base->0.92, offsets cleared, home-turf 0.82 in %s" % ",".join(HOME))


if __name__ == "__main__":
    main()
