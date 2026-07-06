#!/usr/bin/env python3
"""Inject a "who's cutting / raising rates right now" highlight into each auto state page
(article/state/<slug>.html), sourced from the curated rate_changes.json tracker. Serves the
REACTIVE shopper (just got a rate hike -> wants who's cheaper, with proof). Framed as
DIRECTION + primary-source proof; the ZIP tool remains the arbiter of "cheapest for you"
(consistency requirement: tool rankings already verified to agree — see
verify_filing_tool_consistency.py). Idempotent; inserts after the rankings block.

Run after any rate_changes.json edit:  python3 gen_filing_highlights.py
"""
import json, re, os
from collections import defaultdict

GREEN, RED = "#2f6b3a", "#b4321a"
START, END = "<!-- filing-highlights-start -->", "<!-- filing-highlights-end -->"
ANCHOR = "<!-- state-rankings-end -->"  # insert right after the cheapest-carriers table

def slug(name):
    return name.lower().replace(".", "").replace(" ", "-")

def li(c, color, arrow):
    pct = ("%g" % c["pct"]).rstrip("0").rstrip(".")
    eff = c.get("effective", "")
    when = ""
    if eff:
        y, m, _ = (eff.split("-") + ["", "", ""])[:3]
        mon = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        when = " <span style=\"color:var(--ink-mute);\">(eff. %s %s)</span>" % (mon[int(m)], y) if m.isdigit() else ""
    return ('<li style="margin:4px 0;"><strong>%s</strong> '
            '<span style="color:%s;font-weight:700;font-family:var(--mono);">%s%s%%</span>%s</li>'
            % (c["carrier"], color, arrow, pct, when))

def block(name, st_slug, cuts, ups):
    cut_html = "".join(li(c, GREEN, "↓ ") for c in cuts)
    up_html = "".join(li(c, RED, "↑ ") for c in ups)
    cols = []
    if cuts:
        cols.append('<div style="flex:1 1 240px;min-width:0;">'
                    '<div style="font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:%s;margin-bottom:6px;">Cutting rates &mdash; worth a quote</div>'
                    '<ul style="list-style:none;padding:0;margin:0;font-size:16px;">%s</ul></div>' % (GREEN, cut_html))
    if ups:
        cols.append('<div style="flex:1 1 240px;min-width:0;">'
                    '<div style="font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:0.06em;color:%s;margin-bottom:6px;">Raising rates &mdash; time to compare</div>'
                    '<ul style="list-style:none;padding:0;margin:0;font-size:16px;">%s</ul></div>' % (RED, up_html))
    return (START + "\n"
        '<h2>Who\'s cutting and raising rates in %s right now</h2>\n'
        '<p>The actual overall changes carriers filed with state regulators &mdash; primary-source numbers, not estimates. '
        'If your carrier is on the &uarr; list, it\'s a good moment to compare; the &darr; carriers are actively cutting.</p>\n'
        '<div style="display:flex;flex-wrap:wrap;gap:24px;margin:14px 0;max-width:660px;">%s</div>\n'
        '<p style="font-size:14px;margin:10px 0;"><a class="ca-link" href="/article/rate-changes/%s.html">See every %s rate filing, with the source &rarr;</a></p>\n'
        + END) % (name, "".join(cols), st_slug, name)

def main():
    d = json.load(open("rate_changes.json"))
    sr = json.load(open("state_rankings.json"))
    code2name = {k: v["name"] for k, v in sr.items()}
    by = defaultdict(list)
    for c in d["changes"]:
        by[c["state"]].append(c)
    done = 0
    for st, chs in by.items():
        name = code2name.get(st)
        if not name:
            continue
        cuts = sorted([c for c in chs if c.get("dir") == "decrease"], key=lambda x: -x["pct"])
        ups = sorted([c for c in chs if c.get("dir") == "increase"], key=lambda x: -x["pct"])
        if not cuts and not ups:
            continue
        st_slug = slug(name)
        path = "article/state/%s.html" % st_slug
        if not os.path.exists(path):
            print("  ! no state page:", path); continue
        h = open(path).read()
        h = re.sub(r"\s*" + re.escape(START) + r"[\s\S]*?" + re.escape(END), "", h)
        at = h.find(ANCHOR)
        if at == -1:
            print("  ! no rankings anchor:", path); continue
        pos = at + len(ANCHOR)
        blk = "\n" + block(name, st_slug, cuts, ups)
        h = h[:pos] + blk + h[pos:]
        open(path, "w").write(h)
        print("  injected: %s (%d cut / %d up)" % (path, len(cuts), len(ups)))
        done += 1
    print("done: %d state pages" % done)

if __name__ == "__main__":
    main()
