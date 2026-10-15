#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail if any page carries a rankings block for a place it is not about.

This is the check that would have caught the Atlanta leak the first time instead
of the fourth. Run it in the rebuild VALIDATE step - it is cheap and it compares
OUTPUT, so it does not care which generator forgot the strip.

  python3 verify_scaffold_leaks.py          # exit 1 on any leak

gen_metro_base.html is exempt: it IS the Atlanta copy that every metro clone is
built from, so its Atlanta block is correct.
"""
import glob, sys
import scaffold_guards as sg

EXEMPT = {"gen_metro_base.html"}

def main():
    bad = []
    for p in sorted(glob.glob("**/*.html", recursive=True)):
        if "node_modules" in p or p in EXEMPT:
            continue
        html = open(p, encoding="utf-8", errors="replace").read()
        if sg.leaks(html):
            bad.append((p, sg.rankings_place(html), sg.page_place(html)))
    for p, rp, pp in bad:
        print(f"LEAK  {p}\n        block says '{rp}'  but page is '{pp}'")
    print(f"\nscaffold leak check: {len(bad)} leaked page(s)")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
