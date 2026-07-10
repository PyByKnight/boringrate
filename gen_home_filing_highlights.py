#!/usr/bin/env python3
"""Inject a 'who's cutting & raising HOME rates in [state]' block into home/state/<slug>.html,
sourced from serff_home_filings.json (material moves). The home twin of gen_filing_highlights.py.
Surfaces the primary-source home rate crisis where home shoppers land, links to the home tracker.
Idempotent; inserts after the cheapest-carriers rankings block. Run after home-filing edits."""
import json, os, re
from gen_metro_page import STATE

GREEN, RED = "#2f6b3a", "#b4321a"
START, END = "<!-- home-filing-highlights-start -->", "<!-- home-filing-highlights-end -->"
ANCHOR = "<!-- state-rankings-end -->"
MIN = 0.5
MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def li(c, color, arrow):
    pct = ("%g" % abs(c["overall_pct"])).rstrip("0").rstrip(".")
    eff = c.get("effective_new") or ""
    when = ""
    p = eff.split("-")
    if len(p) >= 2 and p[1].isdigit():
        when = ' <span style="color:var(--ink-mute);">(eff. %s %s)</span>' % (MON[int(p[1])], p[0])
    return ('<li style="margin:4px 0;"><strong>%s</strong> '
            '<span style="color:%s;font-weight:700;font-family:var(--mono);">%s%s%%</span>%s</li>'
            % (c["carrier"], color, arrow, pct, when))


def block(name, st_slug, cuts, ups):
    cols = []
    if cuts:
        cols.append('<div style="flex:1 1 240px;min-width:0;">'
                    '<div style="font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:%s;margin-bottom:6px;">Cutting rates &mdash; worth a quote</div>'
                    '<ul style="list-style:none;padding:0;margin:0;font-size:16px;">%s</ul></div>'
                    % (GREEN, "".join(li(c, GREEN, "↓ ") for c in cuts)))
    if ups:
        cols.append('<div style="flex:1 1 240px;min-width:0;">'
                    '<div style="font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:%s;margin-bottom:6px;">Raising rates &mdash; time to compare</div>'
                    '<ul style="list-style:none;padding:0;margin:0;font-size:16px;">%s</ul></div>'
                    % (RED, "".join(li(c, RED, "↑ ") for c in ups)))
    return (START + "\n"
        '<h2>Who\'s cutting and raising home rates in %s right now</h2>\n'
        '<p>The actual overall changes home insurers filed with state regulators &mdash; primary-source numbers, not estimates. '
        'Home rate hikes hit at your renewal; if your carrier is on the &uarr; list, it\'s a good moment to compare.</p>\n'
        '<div style="display:flex;flex-wrap:wrap;gap:24px;margin:14px 0;max-width:660px;">%s</div>\n'
        '<p style="font-size:14px;margin:10px 0;"><a class="ca-link" href="/home/rate-changes/%s.html">See every %s home rate filing, with the source &rarr;</a></p>\n'
        + END) % (name, "".join(cols), st_slug, name)


def main():
    filings = json.load(open("serff_home_filings.json"))["filings"]
    by = {}
    for r in filings:
        if r.get("line") != "home" or r.get("overall_pct") is None or abs(r["overall_pct"]) < MIN:
            continue
        by.setdefault(r["state"], []).append(r)
    done = 0
    for st, chs in by.items():
        if st not in STATE:
            continue
        name, st_slug, _ = STATE[st]
        cuts = sorted([c for c in chs if c["overall_pct"] < 0], key=lambda x: x["overall_pct"])
        ups = sorted([c for c in chs if c["overall_pct"] > 0], key=lambda x: -x["overall_pct"])
        if not cuts and not ups:
            continue
        path = "home/state/%s.html" % st_slug
        if not os.path.exists(path):
            print("  ! no home state page:", path); continue
        h = open(path).read()
        h = re.sub(r"\s*" + re.escape(START) + r"[\s\S]*?" + re.escape(END), "", h)
        at = h.find(ANCHOR)
        if at == -1:
            print("  ! no rankings anchor:", path); continue
        pos = at + len(ANCHOR)
        h = h[:pos] + "\n" + block(name, st_slug, cuts, ups) + h[pos:]
        open(path, "w").write(h)
        print("  injected: %s (%d cut / %d up)" % (path, len(cuts), len(ups)))
        done += 1
    print("done: %d home state pages" % done)


if __name__ == "__main__":
    main()
