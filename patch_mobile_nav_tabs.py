#!/usr/bin/env python3
"""
Fix mobile nav-tabs visibility on state and metro article pages.

Root cause: @media(max-width:900px){.nav-tabs{display:none}} is declared at
line ~89, but .nav-tabs{display:flex} appears unconditionally at line ~91.
Equal specificity (0-1-0), later rule wins → tabs always show on mobile.

Fix: raise media query specificity to nav.primary .nav-tabs{display:none}
(0-2-1 beats 0-1-0), so mobile hides correctly without touching anything else.

Safe to re-run — skips files already patched.
"""
import re
from pathlib import Path

DIRS = [
    Path(__file__).parent / "article" / "state",
    Path(__file__).parent / "article" / "metro",
]

OLD = ".nav-tabs{display:none;}"
NEW = "nav.primary .nav-tabs{display:none;}"

MARKER = "@media(max-width:900px){"

updated = skipped = errors = 0

for d in DIRS:
    for path in sorted(d.glob("*.html")):
        html = path.read_text(encoding="utf-8")

        if NEW in html:
            skipped += 1
            continue

        if MARKER not in html or OLD not in html:
            print(f"  WARN: expected pattern not found in {path.name}")
            errors += 1
            continue

        # Only replace inside the media query block, not globally
        idx = html.find(MARKER)
        end = html.find("}", idx) + 1  # finds the closing } of the media block
        # The media block may have multiple rules; find the real end
        # It's a single-line block so find the first } after the opening {
        block_start = idx + len(MARKER) - 1  # position of the opening {
        depth = 0
        pos = block_start
        while pos < len(html):
            if html[pos] == "{":
                depth += 1
            elif html[pos] == "}":
                depth -= 1
                if depth == 0:
                    block_end = pos
                    break
            pos += 1

        block = html[idx:block_end + 1]
        if OLD not in block:
            print(f"  WARN: .nav-tabs{{display:none}} not inside media query in {path.name}")
            errors += 1
            continue

        new_block = block.replace(OLD, NEW, 1)
        html = html[:idx] + new_block + html[block_end + 1:]
        path.write_text(html, encoding="utf-8")
        updated += 1

print(f"\nDone. {updated} updated, {skipped} already patched, {errors} warnings.")
