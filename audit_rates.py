#!/usr/bin/env python3
"""
Rate verification auditor (auto / renters / home).

Tracks WHEN each rate atom was last verified against a source, so we can
guarantee every rate is re-checked at least once every 30 days (data integrity).

Atoms scanned per product:
  auto    (index.html):         carrier base/CS grade/stability (national,
                                nonstandard, regional), 51 state averages,
                                documented STATE_CARRIER_ADJ offsets
  renters (renters/index.html): carrier base/NAIC/CS grade/stability, 51 state avgs
  home    (home/index.html):    carrier base/NAIC/CS grade/stability, 51 state avgs

Ledgers (one per product): rate_audit.json, rate_audit_renters.json, rate_audit_home.json.
Each atom stores a value snapshot; if the source HTML later differs, the atom is
flagged DRIFTED (forces a fresh source check). Atoms past the SLA are STALE.

Usage (default product=auto; --product renters|home|all):
  python3 audit_rates.py [--product P]                 # check; exit 1 if attention needed
  python3 audit_rates.py --product P --init            # baseline all atoms today
  python3 audit_rates.py --product P --sync             # add/remove atoms; keep dates
  python3 audit_rates.py --product P --mark <id> ...    # record verification(s)
  python3 audit_rates.py --product P --mark-all
  python3 audit_rates.py --product P --due [DAYS]
  python3 audit_rates.py --coverage                     # auto only: carrier x state offset coverage
Options: --source URL  --note "text"  --date YYYY-MM-DD
"""
import argparse, json, re, sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SLA_DAYS = 30

PRODUCTS = {
    "auto":    {"src": "index.html",         "ledger": "rate_audit.json"},
    "renters": {"src": "renters/index.html", "ledger": "rate_audit_renters.json"},
    "home":    {"src": "home/index.html",    "ledger": "rate_audit_home.json"},
}


def src_path(p):    return ROOT / PRODUCTS[p]["src"]
def ledger_path(p): return ROOT / PRODUCTS[p]["ledger"]


def _block(s, start, end):
    i = s.index(start)
    return s[i:s.index(end, i)]


def _carriers(block_text, category, atoms):
    rx = re.compile(
        r'name:\s*"([^"]+)"\s*,\s*base:\s*([0-9.]+)\s*,\s*csGrade:\s*"([^"]+)"\s*,\s*stability:\s*(\d)')
    for m in rx.finditer(block_text):
        atoms["carrier/%s/%s" % (category, m.group(1))] = {
            "category": category, "name": m.group(1),
            "base": float(m.group(2)), "csGrade": m.group(3), "stability": int(m.group(4)),
        }


def scan_auto(s):
    atoms = {}
    _carriers(_block(s, "CARRIERS_STANDARD = [", "\n];"), "national", atoms)
    _carriers(_block(s, "CARRIERS_NONSTANDARD = [", "\n];"), "nonstandard", atoms)
    loc = _block(s, "LOCAL_CARRIER_DEFS = {", "\n};")
    for m in re.finditer(r'"([^"]+)":\s*\{\s*base:\s*([0-9.]+)\s*,\s*csGrade:\s*"([^"]+)"\s*,\s*stability:\s*(\d)', loc):
        atoms["carrier/regional/%s" % m.group(1)] = {
            "category": "regional", "name": m.group(1),
            "base": float(m.group(2)), "csGrade": m.group(3), "stability": int(m.group(4))}
    sd = _block(s, "STATE_DATA = {", "\n};")
    for m in re.finditer(r'"([A-Z]{2})":\s*\{\s*name:\s*"([^"]+)"\s*,\s*avg:\s*(\d+)', sd):
        atoms["state_avg/%s" % m.group(1)] = {"category": "state_avg", "name": m.group(2), "avg": int(m.group(3))}
    sca = _block(s, "STATE_CARRIER_ADJ = {", "\n};")
    for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', sca):
        st = m.group(1)
        for mm in re.finditer(r'"([^"]+)":\s*([0-9.]+)', m.group(2)):
            atoms["offset/%s/%s" % (st, mm.group(1))] = {
                "category": "state_offset", "name": "%s in %s" % (mm.group(1), st),
                "state": st, "carrier": mm.group(1), "mult": float(mm.group(2))}
    return atoms


def scan_rh(s, arr_marker, sd_marker):
    """Renters/home: one carrier array (with naic) + quoted-key state data."""
    atoms = {}
    block = _block(s, arr_marker, "\n];")
    # split into per-carrier object chunks and pull fields
    for chunk in re.split(r'\n  \{', block):
        nm = re.search(r'name:\s*"([^"]+)"', chunk)
        bs = re.search(r'base:\s*([0-9.]+)', chunk)
        na = re.search(r'naic:\s*([0-9.]+)', chunk)
        cg = re.search(r'csGrade:\s*"([^"]+)"', chunk)
        sb = re.search(r'stability:\s*(\d)', chunk)
        if not (nm and bs and cg and sb):
            continue
        atoms["carrier/%s" % nm.group(1)] = {
            "category": "carrier", "name": nm.group(1),
            "base": float(bs.group(1)), "naic": float(na.group(1)) if na else None,
            "csGrade": cg.group(1), "stability": int(sb.group(1))}
    sd = _block(s, sd_marker, "\n};")
    # inner keys are unquoted in renters/home state data: {name:"Alabama",avg:202,...}
    for m in re.finditer(r'"([A-Z]{2})":\s*\{\s*"?name"?:\s*"([^"]+)"[^}]*?"?avg"?:\s*(\d+)', sd):
        atoms["state_avg/%s" % m.group(1)] = {"category": "state_avg", "name": m.group(2), "avg": int(m.group(3))}
    # Per-state carrier offsets (gen_product_offsets.py) — same atom scheme as auto.
    if "STATE_CARRIER_ADJ = {" in s:
        sca = _block(s, "STATE_CARRIER_ADJ = {", "\n};")
        for m in re.finditer(r'"([A-Z]{2})":\s*\{([^}]*)\}', sca):
            st = m.group(1)
            for mm in re.finditer(r'"([^"]+)":\s*([0-9.]+)', m.group(2)):
                atoms["offset/%s/%s" % (st, mm.group(1))] = {
                    "category": "state_offset", "name": "%s in %s" % (mm.group(1), st),
                    "state": st, "carrier": mm.group(1), "mult": float(mm.group(2))}
    return atoms


def scan(product):
    s = src_path(product).read_text(encoding="utf-8")
    if product == "auto":
        return scan_auto(s)
    if product == "renters":
        return scan_rh(s, "RENTERS_CARRIERS = [", "RENTERS_STATE_DATA = {")
    if product == "home":
        return scan_rh(s, "HOME_CARRIERS = [", "HOME_STATE_DATA = {")
    raise ValueError(product)


def snapshot(atom):
    if atom["category"] == "state_avg":
        return {"avg": atom["avg"]}
    if atom["category"] == "state_offset":
        return {"mult": atom["mult"]}
    snap = {"base": atom["base"], "csGrade": atom["csGrade"], "stability": atom["stability"]}
    if atom.get("naic") is not None:
        snap["naic"] = atom["naic"]
    return snap


def load_ledger(p):
    lp = ledger_path(p)
    return json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else None


def save_ledger(p, led):
    ledger_path(p).write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def new_meta(product, today):
    return {
        "product": product,
        "note": ("Verification ledger for every %s rate atom. Integrity SLA: each atom must be "
                 "re-verified against a real source at least every %d days. A value snapshot is "
                 "stored; if the source HTML later differs, the atom is DRIFTED and must be "
                 "re-verified. Update dates only via `audit_rates.py --mark` after an actual check."
                 % (product, SLA_DAYS)),
        "sla_days": SLA_DAYS, "baseline": today, "last_run": today,
    }


def _age(d, today):
    return (datetime.strptime(today, "%Y-%m-%d").date() - datetime.strptime(d, "%Y-%m-%d").date()).days


def cmd_init(p, args, today):
    if ledger_path(p).exists() and not args.force:
        print("%s exists. Use --sync, or --init --force to rebuild." % PRODUCTS[p]["ledger"]); return 2
    atoms = scan(p)
    items = {aid: {"category": a["category"], "name": a["name"], "snapshot": snapshot(a),
                   "last_verified": today, "source": args.source or "", "notes": args.note or ""}
             for aid, a in sorted(atoms.items())}
    save_ledger(p, {"_meta": new_meta(p, today), "items": items})
    print("[%s] initialized %s with %d atoms, baselined %s." % (p, PRODUCTS[p]["ledger"], len(items), today))
    return 0


def cmd_sync(p, args, today):
    led = load_ledger(p)
    if led is None: print("[%s] no ledger; run --init." % p); return 2
    atoms = scan(p); items = led["items"]
    added = [a for a in atoms if a not in items]; removed = [a for a in items if a not in atoms]
    for aid in added:
        items[aid] = {"category": atoms[aid]["category"], "name": atoms[aid]["name"],
                      "snapshot": snapshot(atoms[aid]), "last_verified": today,
                      "source": args.source or "", "notes": args.note or "(added via --sync)"}
    for aid in removed: del items[aid]
    led["_meta"]["last_run"] = today; save_ledger(p, led)
    print("[%s] synced: +%d new, -%d removed." % (p, len(added), len(removed)))
    for a in added: print("   + " + a)
    for a in removed: print("   - " + a)
    return 0


def cmd_mark(p, args, today):
    led = load_ledger(p)
    if led is None: print("[%s] no ledger; run --init." % p); return 2
    atoms = scan(p)
    targets = list(led["items"]) if args.mark_all else args.mark
    n = 0
    for aid in targets:
        if aid not in led["items"]: print("  ! unknown id: " + aid); continue
        if aid in atoms: led["items"][aid]["snapshot"] = snapshot(atoms[aid])
        led["items"][aid]["last_verified"] = today
        if args.source: led["items"][aid]["source"] = args.source
        if args.note: led["items"][aid]["notes"] = args.note
        n += 1
    led["_meta"]["last_run"] = today; save_ledger(p, led)
    print("[%s] marked %d atom(s) verified %s." % (p, n, today)); return 0


def cmd_check(p, args, today):
    led = load_ledger(p)
    if led is None: print("[%s] no ledger; run --init." % p); return 2
    atoms = scan(p); items = led["items"]
    never = sorted(a for a in atoms if a not in items)
    removed = sorted(a for a in items if a not in atoms)
    drifted, stale = [], []
    sla = led["_meta"].get("sla_days", SLA_DAYS)
    for aid, rec in items.items():
        if aid not in atoms: continue
        if rec.get("snapshot") != snapshot(atoms[aid]): drifted.append(aid)
        elif _age(rec["last_verified"], today) > sla: stale.append(aid)
    drifted.sort(); stale.sort()
    cats = {}
    for v in items.values(): cats[v["category"]] = cats.get(v["category"], 0) + 1
    issues = len(never) + len(drifted) + len(stale) + len(removed)
    print("[%s] rate integrity — %s (SLA %d days)" % (p, today, sla))
    print("  tracked atoms : %d  (%s)" % (len(items), ", ".join("%d %s" % (n, c) for c, n in sorted(cats.items()))))
    print("  fresh & in-sync: %d" % (len(items) - len(drifted) - len(stale) - len(removed)))

    def show(label, ids, why):
        if not ids: return
        print("\n  %s (%d) — %s:" % (label, len(ids), why))
        for aid in ids:
            extra = ("  last_verified %s (%dd)" % (items[aid]["last_verified"], _age(items[aid]["last_verified"], today))) if aid in items else ""
            print("     %s%s" % (aid, extra))
    show("NEVER VERIFIED", never, "in source but not ledger — run --sync")
    show("DRIFTED", drifted, "value changed since last verification — re-verify + --mark")
    show("STALE", stale, "older than SLA — re-verify + --mark")
    show("REMOVED", removed, "in ledger but gone from source — run --sync")
    print("\n%s" % ("All %s rates fresh and in sync." % p if not issues else "%d atom(s) need attention." % issues))
    return 0 if not issues else 1


def cmd_due(p, args, today):
    led = load_ledger(p)
    if led is None: print("[%s] no ledger; run --init." % p); return 2
    horizon = args.due if isinstance(args.due, int) else 7
    sla = led["_meta"].get("sla_days", SLA_DAYS)
    rows = sorted((sla - _age(r["last_verified"], today), aid) for aid, r in led["items"].items())
    rows = [r for r in rows if r[0] <= horizon]
    print("[%s] atoms due within %d days (SLA %d):" % (p, horizon, sla))
    for due_in, aid in rows:
        print("  [%s] %s" % ("OVERDUE %dd" % -due_in if due_in < 0 else "in %dd" % due_in, aid))
    if not rows: print("  none.")
    return 0


def cmd_coverage(args, today):
    atoms = scan("auto")
    nats = sorted({a["name"] for a in atoms.values() if a["category"] == "national"})
    states = sorted(a.split("/")[1] for a in atoms if a.startswith("state_avg/"))
    documented = {}
    for a in atoms.values():
        if a["category"] == "state_offset":
            documented.setdefault(a["carrier"], set()).add(a["state"])
    cells = len(nats) * len(states); doc = sum(len(documented.get(n, set())) for n in nats)
    print("Carrier x state offset coverage (auto) — %s" % today)
    print("  national cells : %d  (%d nationals x %d states)" % (cells, len(nats), len(states)))
    print("  documented offset : %d (%.1f%%)" % (doc, 100 * doc / cells))
    print("  national base only: %d (%.1f%%)" % (cells - doc, 100 * (cells - doc) / cells))
    for n in sorted(nats, key=lambda x: -len(documented.get(x, set()))):
        d = len(documented.get(n, set()))
        print("     %-18s %2d/%d%s" % (n, d, len(states), "  <-- national base in ALL states" if d == 0 else ""))
    return 0


def main():
    pa = argparse.ArgumentParser(description="Rate verification auditor (auto/renters/home)")
    pa.add_argument("--product", default="auto", choices=["auto", "renters", "home", "all"])
    pa.add_argument("--init", action="store_true"); pa.add_argument("--force", action="store_true")
    pa.add_argument("--sync", action="store_true")
    pa.add_argument("--mark", nargs="+", metavar="ID"); pa.add_argument("--mark-all", action="store_true")
    pa.add_argument("--due", nargs="?", const=7, type=int, metavar="DAYS")
    pa.add_argument("--coverage", action="store_true", help="auto only: carrier x state offset coverage")
    pa.add_argument("--source"); pa.add_argument("--note"); pa.add_argument("--date")
    args = pa.parse_args()
    today = args.date or date.today().isoformat()

    if args.coverage:
        return cmd_coverage(args, today)

    products = ["auto", "renters", "home"] if args.product == "all" else [args.product]
    rc = 0
    for p in products:
        if args.init: rc |= cmd_init(p, args, today)
        elif args.sync: rc |= cmd_sync(p, args, today)
        elif args.mark or args.mark_all: rc |= cmd_mark(p, args, today)
        elif args.due is not None: rc |= cmd_due(p, args, today)
        else: rc |= cmd_check(p, args, today)
        if len(products) > 1: print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
