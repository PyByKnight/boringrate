#!/usr/bin/env python3
"""Inject the 'How <state> compares' block (state_compare.py) into the static renters state pages,
just above the nearby-states links. Idempotent: re-running replaces the block in place.
Re-run after renters/index.html model changes (averages, STATE_CARRIER_ADJ, carrier states).

    python3 patch_renters_compare.py
"""
import state_compare as sc

BEFORE = "<!-- nearby-states -->"


def main():
    states, _, _ = sc.model("renters")
    done, miss = 0, []
    for code, (name, _) in states.items():
        path = f"renters/state/{sc.slug(name)}.html"
        try:
            h = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            miss.append(path); continue
        new, ok = sc.inject(h, "renters", code, BEFORE)
        if not ok:
            miss.append(path); continue
        if new != h:
            open(path, "w", encoding="utf-8").write(new)
        done += 1
    print(f"renters compare block: {done} pages" + (f"; skipped {miss}" if miss else ""))


if __name__ == "__main__":
    main()
