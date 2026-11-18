#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPORT ONLY: pre-anchor filing catch-up on STATE_CARRIER_ADJ.

WHY. apply_filed_changes.py only drifts filings effective AFTER a state's anchor, on the
theory that earlier filings are baked into the 2026-06-23 third-party snapshot. But that
snapshot (cheapest_by_state.json) only names each state's CHEAPEST carrier - it never
priced, say, Allstate in Ohio. Most STATE_CARRIER_ADJ cells came from the 2026-06-17
cost-percentile formula tilt (1a70e054), so the pre-anchor cuts/raises were never priced
in anywhere. Origin: OH Allstate compounded -11.0% (Jul 2025 - Mar 2026, 158K PH) while
the tool ranked it #18/20.

WHAT. For every (state, tool-roster carrier) with in-ledger filings effective ON OR BEFORE
the state's anchor:
  net   = carrier_net(): compound within a book, weight across books by policyholders
          (same function as verify_filing_tool_consistency.py)
  F     = 1 + net/100
  F_bar = written-premium-weighted mean F across the state's filing carriers
  adj'  = adj * F / F_bar        (renormalized: state average level is untouched; carriers
                                  cutting MORE than peers move up the rankings, less move down)
Guards from filing_guards (has_pct, is_driftable, too_small) + rate-neutral rows dropped.
Excluded states: TX (owner: drift record-only), CA (workbook mutable, rows never drift).
Post-anchor filings are NOT included - apply_filed_changes.py owns those.

  python3 catchup_report.py            # human table + catchup_report.json
"""
import json, sys
from collections import defaultdict
import filing_guards as fg
from verify_filing_tool_consistency import load_model, full_rank, carrier_net
from apply_filed_changes import roster_name

EXCLUDE_STATES = {"TX", "CA"}
FLAG_MOVE = 0.10   # flag any single-cell change > 10%
# --baseline=premium : WP-weighted mean of the filing carriers (apply_filed_changes' F_bar)
# --baseline=roster  : equal-weight mean over the full tool roster, non-filers flat (default)
CAP = 0.15         # owner 2026-11-18: no single cell moves more than +/-15% in one pass
APPLY = "--apply" in sys.argv
BASELINE = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--baseline=")), "roster")

def main():
    avg, nat, loc, slc, adj = load_model()
    anchors = json.load(open("anchor_dates.json"))
    led = json.load(open("serff_filings.json"))["filings"]
    by = defaultdict(list)
    for r in led:
        st = r["state"]
        if st in EXCLUDE_STATES: continue
        if not fg.has_pct(r) or not fg.is_driftable(r) or fg.too_small(r): continue
        if not r.get("affected") and not r["overall_pct"]: continue      # rate-neutral / 0 PH
        if r.get("catchup_applied"): continue                               # already priced in once
        eff = fg.eff_date(r)
        anc = anchors["states"].get(st, anchors["default"])
        if not eff or eff > anc: continue                                 # post-anchor: drift owns it
        by[(st, roster_name(r["carrier"], r.get("entity")))].append(r)

    out, moved, flags = {}, 0, 0
    for st in sorted({s for s, _ in by}):
        roster = set(nat) | {n for n in slc.get(st, []) if n in loc}
        cars = {c: rs for (s, c), rs in by.items() if s == st and c in roster}
        if not cars: continue
        F, W = {}, {}
        for c, rs in cars.items():
            F[c] = 1 + carrier_net(rs) / 100.0
            W[c] = sum(r.get("written_premium") or 0 for r in rs) or 1.0
        if BASELINE == "roster":
            # Equal-weight over the WHOLE state roster, non-filers counted flat (F=1).
            # Cutters always get cheaper, raisers dearer; one giant book can't push every
            # other cutter's price up (IL: State Farm -14.5% under the premium-weighted mean).
            Fbar = (sum(F.values()) + (len(roster) - len(F))) / len(roster)
        else:
            Fbar = sum(F[c] * W[c] for c in F) / sum(W.values())
        before = full_rank(st, avg, nat, loc, slc, adj)
        A = dict(adj.get(st, {}))
        new = {}
        for c in F:
            old = A.get(c, 1.0)
            ratio = max(1 - CAP, min(1 + CAP, F[c] / Fbar))
            new[c] = round(old * ratio, 4)
        A2 = dict(A); A2.update(new)
        adj2 = dict(adj); adj2[st] = A2
        after = full_rank(st, avg, nat, loc, slc, adj2)
        rows = []
        for c in sorted(F, key=lambda c: F[c]):
            old = A.get(c, 1.0); chg = new[c] / old - 1
            b, a = before.get(c), after.get(c)
            flag = abs(chg) > FLAG_MOVE
            flags += flag; moved += 1
            rows.append({"carrier": c, "net_pct": round((F[c] - 1) * 100, 2), "adj_old": old,
                         "adj_new": new[c], "price_chg_pct": round(chg * 100, 2),
                         "rank_old": b[0] if b else None, "rank_new": a[0] if a else None,
                         "price_old": b[1] if b else None, "price_new": a[1] if a else None,
                         "n": b[2] if b else None, "new_adj_entry": c not in A, "flag_gt10": flag,
                         "capped": abs(F[c] / Fbar - 1) > CAP,
                         "trackings": sorted({r["tracking"] for r in cars[c]})})
        out[st] = {"anchor": anchors["states"].get(st, anchors["default"]),
                   "Fbar_pct": round((Fbar - 1) * 100, 2), "carriers": rows}

    json.dump({"_meta": {"purpose": "PROPOSED pre-anchor catch-up; NOT applied", "excluded": sorted(EXCLUDE_STATES),
                         "baseline": BASELINE},
               "states": out}, open("catchup_report.json", "w"), indent=1)
    for st, s in out.items():
        print(f"== {st} ==  anchor {s['anchor']}  peer mean {s['Fbar_pct']:+.1f}%")
        for r in s["carriers"]:
            mv = (f"#{r['rank_old']}->#{r['rank_new']}/{r['n']}" if r["rank_old"] else "n/a")
            print(f"  {r['carrier']:24} filed {r['net_pct']:+6.1f}%  adj {r['adj_old']:.4f}->{r['adj_new']:.4f}"
                  f" ({r['price_chg_pct']:+5.1f}%)  ${r['price_old']}->${r['price_new']}  {mv}"
                  + ("  NEW-ENTRY" if r["new_adj_entry"] else "") + ("  >10%" if r["flag_gt10"] else ""))
        print()
    if APPLY:
        apply(out, led)
    print(f"cells {'moved' if APPLY else 'that would move'}: {moved}  |  >10% moves: {flags}  |  states: {len(out)}")

def _num(v):
    t = f"{v:.4f}".rstrip("0")
    return t + "0" if t.endswith(".") else t

def apply(out, led):
    """Write adj_new into STATE_CARRIER_ADJ (one line per state, key order kept, new carriers
    appended) and stamp every contributing ledger row catchup_applied so a re-run skips it."""
    import re
    from datetime import date
    html = open("index.html", encoding="utf-8").read()
    blk = re.search(r"const STATE_CARRIER_ADJ\s*=\s*\{(.*?)\n\};", html, re.DOTALL)
    body = blk.group(1)
    for st, s in out.items():
        m = re.search(r'\n(\s*)"%s":\s*(\{[^}]*\})(,?)' % st, body)
        if not m:
            raise SystemExit(f"apply: no STATE_CARRIER_ADJ line for {st}")
        cur = json.loads(m.group(2))
        for r in s["carriers"]:
            cur[r["carrier"]] = r["adj_new"]
        line = "{ " + ", ".join(f'"{k}": {_num(v)}' for k, v in cur.items()) + " }"
        body = body[:m.start()] + f'\n{m.group(1)}"{st}": {line}{m.group(3)}' + body[m.end():]
    html = html[:blk.start(1)] + body + html[blk.end(1):]
    open("index.html", "w", encoding="utf-8").write(html)
    stamp = date.today().isoformat()
    want = {(st, t) for st, s in out.items() for r in s["carriers"] for t in r["trackings"]}
    n = 0
    for r in led:
        if (r["state"], r["tracking"]) in want:
            r["catchup_applied"] = stamp; n += 1
    full = json.load(open("serff_filings.json"))
    full["filings"] = led
    json.dump(full, open("serff_filings.json", "w"), indent=1)
    print(f"APPLIED: {len(out)} states written to STATE_CARRIER_ADJ; {n} ledger rows stamped catchup_applied={stamp}")

if __name__ == "__main__":
    sys.exit(main())
