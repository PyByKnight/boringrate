#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strip prose the renters state pages share with each other (renters/state/*.html).

Why (2026-11-19 prose audit): renters state pages were 37% repeated prose - a lease paragraph
on all 51, plus "low-cost", "storm", "urban" and "coastal" archetype paragraphs pasted across
groups of states. Rule (memory boringrate-unique-content-rule): keep what only this state's page
says, cut what every page says, and point to the one guide that says it properly.

These pages have no generator (static since 4bf4b6f6), so this patches HTML surgically:
  - any sentence or TLDR bullet whose number-normalized text appears on >= MIN_PAGES renters
    state pages is removed (state names are not normalized, so state-specific text survives)
  - a paragraph/callout left empty is dropped; a callout left with only the average is dropped
    (the dek + TLDR already state it)
  - topic links replace the advice that was cut: lease -> is-renters-insurance-required,
    flood -> does-renters-insurance-cover-water-damage, theft -> does-renters-insurance-cover-theft
Idempotent: a second run finds nothing repeated.

    python3 patch_renters_state_prose.py            # dry run: counts
    python3 patch_renters_state_prose.py --apply
"""
import collections, glob, re, sys

MIN_PAGES = 3
FILES = sorted(f for f in glob.glob("renters/state/*.html") if not f.endswith("index.html"))
BODY = re.compile(r'(?s)(<div class="article-body">)(.*?)(<!-- nearby-states -->|<div class="rz-zip"><span class="rz-zip-label">Ready)')
SENT = re.compile(r"(?<=[.?!])\s+(?=[A-Z<])")
LINKS = {
    "lease": ('landlord', '<a class="ca-link" href="/renters/is-renters-insurance-required.html">When a landlord can require renters insurance</a>'),
    "flood": ('flood', '<a class="ca-link" href="/renters/does-renters-insurance-cover-water-damage.html">What renters insurance pays for water and flood damage</a>'),
    "theft": ('stolen', '<a class="ca-link" href="/renters/does-renters-insurance-cover-theft.html">How renters theft coverage works</a>'),
}


def key(t):
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"[$]?[-+−]?\d[\d,.]*%?", "#", t.lower()).strip()


# Sentences that differ only by the state name (so the >=3-page count misses them) and that
# lean on a sentence the count removed.
DANGLING = re.compile(r"\s*This makes shopping around at every renewal especially important in [^<]*?urban areas[^<]*?\.(?=\s|<)")


def units(body):
    """Text of every sentence in <p> and every <li> in the body prose (our own link line excluded)."""
    for m in re.finditer(r"(?s)<p(?: [^>]*)?>(.*?)</p>", body):
        if m.group(1).lstrip().startswith('<a class="ca-link"'):
            continue
        for s in SENT.split(m.group(1)):
            yield s
    for m in re.finditer(r"(?s)<li>(.*?)</li>", body):
        yield m.group(1)


def main():
    apply = "--apply" in sys.argv
    pages = {f: open(f, encoding="utf-8").read() for f in FILES}
    count = collections.Counter()
    for f, h in pages.items():
        m = BODY.search(h)
        for k in {key(u) for u in units(m.group(2)) if len(key(u).split()) >= 6}:
            count[k] += 1
    rep = {k for k, n in count.items() if n >= MIN_PAGES}
    total, touched = 0, 0
    for f, h in pages.items():
        m = BODY.search(h)
        body, cut = m.group(2), []

        def para(pm):
            inner = pm.group(2)
            keep = []
            for s in SENT.split(inner):
                if key(s) in rep:
                    cut.append(key(s))
                else:
                    keep.append(s)
            if len(keep) == len(SENT.split(inner)):
                return pm.group(0)
            new = " ".join(keep).strip()
            if not re.sub(r"<[^>]+>", "", new).strip():
                return ""
            return pm.group(1) + new + "</p>"
        body = re.sub(r"(?s)(<p(?: [^>]*)?>)(.*?)</p>", para, body)
        body, nd = DANGLING.subn("", body)
        cut += ["dangling"] * nd

        def li(lm):
            if key(lm.group(1)) in rep:
                cut.append(key(lm.group(1)))
                return ""
            return lm.group(0)
        body = re.sub(r"(?s)\s*<li>(.*?)</li>", li, body)
        # callout reduced to the bare average (already in dek + TLDR) -> drop it
        body = re.sub(r'(?s)\s*<div class="callout"><p><strong>[^<]*renters insurance average:</strong>[^<]*</p></div>', "", body)
        body = re.sub(r'(?s)\s*<div class="callout">\s*</div>', "", body)
        if cut:
            blob = " ".join(cut)
            links = [html for topic, (needle, html) in LINKS.items() if needle in blob and html not in body]
            if links:
                body = body.rstrip() + '\n    <p style="font-size:15px;">' + " &middot; ".join(links) + "</p>\n"
            total += len(cut); touched += 1
            pages[f] = h[:m.start(2)] + body + h[m.end(2):]
    print(f"repeated units: {len(rep)} | removed {total} sentences/bullets on {touched} of {len(FILES)} pages")
    if not apply:
        print("dry run - re-run with --apply"); return
    for f, h in pages.items():
        open(f, "w", encoding="utf-8").write(h)


if __name__ == "__main__":
    main()
