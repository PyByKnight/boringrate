#!/usr/bin/env python3
"""
gen_auto_offset_fill.py — deepen auto's partial carrier offsets.

State Farm (36/51), Progressive (17/51), and Farmers (5/51) were the three
partially-tuned nationals in `STATE_CARRIER_ADJ` (RATE_METHODOLOGY.md §3/§6).
This fills their MISSING states only — existing hand-tuned values are never
touched — with a per-carrier linear model fit to each carrier's own existing
cloud (so the fills extend the established shape rather than impose a generic
tilt):

  State Farm  offset = max(0.84, 0.85 + 0.40*(pct-0.5))   # cheap floor, loads priciest
  Progressive offset = 0.90 - 0.06*pct                    # tight value band
  Farmers     offset = 0.91 + 0.04*(pct-0.5)              # mild agent loading

pct = rank of the state's STATE_DATA.avg, 0 (cheapest) … 1 (priciest).
A fill that rounds to 1.00 is dropped (== national base). Modeled/directional,
same status as the rest of STATE_CARRIER_ADJ. Surgical, idempotent: each missing
carrier is appended to its state row; rerunning is a no-op.
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "index.html"

MODELS = {
    "State Farm":  lambda p: round(max(0.84, 0.85 + 0.40 * (p - 0.5)), 2),
    "Progressive": lambda p: round(0.90 - 0.06 * p, 2),
    "Farmers":     lambda p: round(0.91 + 0.04 * (p - 0.5), 2),
}


def block(s, start, end="\n};"):
    i = s.index(start)
    j = s.index(end, i)
    return i + len(start), j  # span of inner text


def main():
    s = SRC.read_text(encoding="utf-8")

    # state cost percentiles
    a, b = block(s, "STATE_DATA = {")
    avgs = {m.group(1): int(m.group(3)) for m in
            re.finditer(r'"([A-Z]{2})":\s*\{\s*name:\s*"([^"]+)"\s*,\s*avg:\s*(\d+)', s[a:b])}
    codes = sorted(avgs, key=lambda c: avgs[c])
    pct = {c: i / (len(codes) - 1) for i, c in enumerate(codes)}

    # operate only inside the STATE_CARRIER_ADJ block
    a, b = block(s, "STATE_CARRIER_ADJ = {")
    head, body, tail = s[:a], s[a:b], s[b:]

    added = {c: 0 for c in MODELS}
    dropped = {c: [] for c in MODELS}
    lines = body.split("\n")
    for idx, line in enumerate(lines):
        m = re.match(r'(\s*)"([A-Z]{2})":\s*\{(.*)\}(,?)\s*$', line)
        if not m:
            continue
        indent, code, inner, comma = m.groups()
        present = set(re.findall(r'"([^"]+)":', inner))
        adds = []
        for car, fn in MODELS.items():
            if car in present:
                continue
            val = fn(pct[code])
            if val == 1.00:
                dropped[car].append(code)
                continue
            adds.append('"%s": %s' % (car, ("%g" % val)))
            added[car] += 1
        if adds:
            inner = inner.strip()
            joined = ", ".join(adds)
            inner = (inner + ", " + joined) if inner else joined
            lines[idx] = '%s"%s": { %s }%s' % (indent, code, inner, comma)

    SRC.write_text(head + "\n".join(lines) + tail, encoding="utf-8")
    for car in MODELS:
        print("[%s] filled %d states%s" % (
            car, added[car],
            (" (dropped %s → 1.00)" % ",".join(dropped[car])) if dropped[car] else ""))


if __name__ == "__main__":
    main()
