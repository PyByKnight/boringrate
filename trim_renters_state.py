#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-off (2026-11-17): trim the shared boilerplate on the 51 static renters state pages.

AdSense content-quality rejection. These pages have no generator; they share ~300 words of
generic prose and a visible FAQ that repeats the body. They also named "Lemonade, State Farm,
and GEICO" as cheapest on every page, contradicting each page's own ranking table (the
tool<->prose consistency rule) - that trio is replaced with the table's top 3.

    python3 trim_renters_state.py            # dry run: counts per edit
    python3 trim_renters_state.py --apply
Idempotent: a second run changes nothing.
"""
import glob, re, sys
from collections import Counter

TRIO = "Lemonade, State Farm, and GEICO"


def trim(h, state):
    hits = Counter()

    def sub(key, pat, rep, s, flags=re.S):
        s2, n = re.subn(pat, rep, s, flags=flags)
        hits[key] += n
        return s2

    tb = re.search(r"<tbody>(.*?)</tbody>", h, flags=re.S)
    top = re.findall(r"<strong>([^<]+)</strong>", tb.group(1))[:3]
    t3 = f"{top[0]}, {top[1]}, and {top[2]}"

    h = sub("generic carrier para", r"\s*<p>Carrier selection still matters significantly\..*?</p>", "", h)
    h = sub("carrier aside", r" Lemonade has been aggressive on pricing[^<]*?agent availability\.", "", h)
    h = sub("cheapest section",
            r"(<h2>Cheapest renters insurance companies in [^<]+</h2>)\s*<p>.*?</p>\s*<p>One thing many renters underestimate.*?</p>",
            lambda m: (m.group(1) + f"\n    <p>{t3} come out lowest-priced for a standard {state} renters "
                       f"policy in our model; the full ranking is in the table above.</p>"), h)
    h = sub("not-required para", r"\s*<p>Even when it(?:&rsquo;|’|')s not required.*?</p>", "", h)
    h = sub("visible FAQ", r"\s*<h2>Frequently asked questions</h2>.*?(?=\s*<!-- nearby-states -->)", "", h)
    h = sub("literal {name}", r"\{name\}", state, h)
    h = sub("carrier trio", re.escape(TRIO), t3, h)
    return h, hits


def main():
    tot, changed = Counter(), 0
    for f in sorted(glob.glob("renters/state/*.html")):
        if f.endswith("index.html"):
            continue
        h = open(f, encoding="utf-8").read()
        state = re.search(r"<h1[^>]*>\s*([A-Z][A-Za-z .]+?) renters insurance", h)
        state = state.group(1).strip() if state else None
        if not state:
            sys.exit(f"{f}: could not read the state name from <h1>")
        new, hits = trim(h, state)
        tot.update(hits)
        if new != h:
            changed += 1
            if "--apply" in sys.argv:
                open(f, "w", encoding="utf-8").write(new)
    print(f"{changed} pages {'changed' if '--apply' in sys.argv else 'would change'}")
    for k, v in tot.items():
        print(f"  {k:22} {v}")


if __name__ == "__main__":
    main()
