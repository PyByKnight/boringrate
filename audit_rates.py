#!/usr/bin/env python3
"""
Auto-rate verification auditor.

Tracks WHEN each auto rate atom was last verified against a source, so we can
guarantee every rate is re-checked at least once every 30 days (data integrity).

Rate atoms scanned from index.html:
  - carrier base rate / CS grade / rate stability  (national, nonstandard, regional)
  - per-state average premium (STATE_DATA.avg)

Ledger: rate_audit.json (top-level, same convention as rate_changes.json).
Each atom stores a snapshot of its value; if the value in index.html later
differs from the snapshot, the atom is flagged DRIFTED and must be re-verified
(this is how an edit to a rate forces a fresh source check).

Usage:
  python3 audit_rates.py                 # check + report; exit 1 if anything needs attention
  python3 audit_rates.py --init          # create ledger, baseline every atom as verified today
  python3 audit_rates.py --sync          # add NEW atoms (today) + drop removed; keep existing dates
  python3 audit_rates.py --mark ID ...   # mark atom(s) verified today (snapshot refreshed)
  python3 audit_rates.py --mark-all      # mark ALL atoms verified today (after a full review pass)
  python3 audit_rates.py --due [DAYS]    # list overdue + due within DAYS (default 7)
Options (with --mark/--mark-all/--init): --source URL  --note "text"  --date YYYY-MM-DD
"""
import argparse, json, re, sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "index.html"
LEDGER = ROOT / "rate_audit.json"
SLA_DAYS = 30


def _block(s, start, end):
    i = s.index(start)
    return s[i:s.index(end, i)]


def scan_atoms():
    """Parse all current auto rate atoms from index.html -> {id: {...snapshot...}}."""
    s = SRC.read_text(encoding="utf-8")
    atoms = {}

    def carriers(block_text, category):
        # match: name: "X", base: 0.82, csGrade: "A+", stability: 4
        rx = re.compile(
            r'name:\s*"([^"]+)"\s*,\s*base:\s*([0-9.]+)\s*,\s*csGrade:\s*"([^"]+)"\s*,\s*stability:\s*(\d)')
        for m in rx.finditer(block_text):
            atoms["carrier/%s/%s" % (category, m.group(1))] = {
                "category": category, "name": m.group(1),
                "base": float(m.group(2)), "csGrade": m.group(3),
                "stability": int(m.group(4)),
            }

    carriers(_block(s, "CARRIERS_STANDARD = [", "\n];"), "national")
    carriers(_block(s, "CARRIERS_NONSTANDARD = [", "\n];"), "nonstandard")

    # LOCAL_CARRIER_DEFS: "Name": { base: 0.77, csGrade: "A+", stability: 5,
    loc = _block(s, "LOCAL_CARRIER_DEFS = {", "\n};")
    rx = re.compile(r'"([^"]+)":\s*\{\s*base:\s*([0-9.]+)\s*,\s*csGrade:\s*"([^"]+)"\s*,\s*stability:\s*(\d)')
    for m in rx.finditer(loc):
        atoms["carrier/regional/%s" % m.group(1)] = {
            "category": "regional", "name": m.group(1),
            "base": float(m.group(2)), "csGrade": m.group(3),
            "stability": int(m.group(4)),
        }

    # STATE_DATA: "AL": { name: "Alabama", avg: 2468, code: "AL" }
    sd = _block(s, "STATE_DATA = {", "\n};")
    rx = re.compile(r'"([A-Z]{2})":\s*\{\s*name:\s*"([^"]+)"\s*,\s*avg:\s*(\d+)')
    for m in rx.finditer(sd):
        atoms["state_avg/%s" % m.group(1)] = {
            "category": "state_avg", "name": m.group(2), "avg": int(m.group(3)),
        }
    return atoms


def snapshot(atom):
    """The value fields tracked for drift, by category."""
    if atom["category"] == "state_avg":
        return {"avg": atom["avg"]}
    return {"base": atom["base"], "csGrade": atom["csGrade"], "stability": atom["stability"]}


def load_ledger():
    if not LEDGER.exists():
        return None
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def save_ledger(led):
    LEDGER.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def new_meta(today):
    return {
        "note": ("Verification ledger for every auto rate atom. Integrity SLA: each atom must be "
                 "re-verified against a real source at least every %d days. A snapshot of each value "
                 "is stored; if index.html later differs, the atom is DRIFTED and must be re-verified. "
                 "Update dates only via `audit_rates.py --mark`/`--mark-all` after an actual source check." % SLA_DAYS),
        "sla_days": SLA_DAYS,
        "baseline": today,
        "last_run": today,
    }


def cmd_init(args, today):
    if LEDGER.exists() and not args.force:
        print("rate_audit.json already exists. Use --sync to add new atoms, or --init --force to rebuild.")
        return 2
    atoms = scan_atoms()
    items = {}
    for aid, atom in sorted(atoms.items()):
        items[aid] = {
            "category": atom["category"], "name": atom["name"],
            "snapshot": snapshot(atom),
            "last_verified": today,
            "source": args.source or "",
            "notes": args.note or "",
        }
    save_ledger({"_meta": new_meta(today), "items": items})
    print("Initialized rate_audit.json with %d atoms, baselined %s." % (len(items), today))
    return 0


def cmd_sync(args, today):
    led = load_ledger()
    if led is None:
        print("No ledger yet. Run --init first.")
        return 2
    atoms = scan_atoms()
    items = led["items"]
    added = [a for a in atoms if a not in items]
    removed = [a for a in items if a not in atoms]
    for aid in added:
        items[aid] = {
            "category": atoms[aid]["category"], "name": atoms[aid]["name"],
            "snapshot": snapshot(atoms[aid]), "last_verified": today,
            "source": args.source or "", "notes": args.note or "(added via --sync)",
        }
    for aid in removed:
        del items[aid]
    led["_meta"]["last_run"] = today
    save_ledger(led)
    print("Synced: +%d new (baselined %s), -%d removed." % (len(added), today, len(removed)))
    for a in added:
        print("   + " + a)
    for a in removed:
        print("   - " + a)
    return 0


def cmd_mark(args, today):
    led = load_ledger()
    if led is None:
        print("No ledger yet. Run --init first.")
        return 2
    atoms = scan_atoms()
    targets = list(led["items"]) if args.mark_all else args.mark
    n = 0
    for aid in targets:
        if aid not in led["items"]:
            print("  ! unknown id: " + aid); continue
        if aid in atoms:
            led["items"][aid]["snapshot"] = snapshot(atoms[aid])
        led["items"][aid]["last_verified"] = today
        if args.source:
            led["items"][aid]["source"] = args.source
        if args.note:
            led["items"][aid]["notes"] = args.note
        n += 1
    led["_meta"]["last_run"] = today
    save_ledger(led)
    print("Marked %d atom(s) verified %s." % (n, today))
    return 0


def _age_days(d, today):
    return (datetime.strptime(today, "%Y-%m-%d").date()
            - datetime.strptime(d, "%Y-%m-%d").date()).days


def audit(led, atoms, today):
    items = led["items"]
    never = sorted(a for a in atoms if a not in items)        # in code, not tracked
    removed = sorted(a for a in items if a not in atoms)       # tracked, gone from code
    drifted, stale = [], []
    for aid, rec in items.items():
        if aid not in atoms:
            continue
        if rec.get("snapshot") != snapshot(atoms[aid]):
            drifted.append(aid)
        elif _age_days(rec["last_verified"], today) > led["_meta"].get("sla_days", SLA_DAYS):
            stale.append(aid)
    return never, removed, sorted(drifted), sorted(stale)


def cmd_check(args, today):
    led = load_ledger()
    if led is None:
        print("No ledger yet. Run --init first.")
        return 2
    atoms = scan_atoms()
    never, removed, drifted, stale = audit(led, atoms, today)
    sla = led["_meta"].get("sla_days", SLA_DAYS)
    total = len(led["items"])
    ok = total - len(drifted) - len(stale) - len(removed)
    print("Auto rate integrity — %s (SLA %d days)" % (today, sla))
    print("  tracked atoms : %d  (%d carriers + %d state averages)" % (
        total,
        sum(1 for v in led["items"].values() if v["category"] != "state_avg"),
        sum(1 for v in led["items"].values() if v["category"] == "state_avg")))
    print("  fresh & in-sync: %d" % ok)

    def show(label, ids, why):
        if not ids:
            return
        print("\n  %s (%d) — %s:" % (label, len(ids), why))
        for aid in ids:
            extra = ""
            if aid in led["items"]:
                extra = "  last_verified %s (%dd)" % (
                    led["items"][aid]["last_verified"],
                    _age_days(led["items"][aid]["last_verified"], today))
            print("     %s%s" % (aid, extra))

    show("NEVER VERIFIED", never, "present in index.html but not in ledger — run --sync")
    show("DRIFTED", drifted, "value changed in index.html since last verification — re-verify + --mark")
    show("STALE", stale, "older than SLA — re-verify against source + --mark")
    show("REMOVED", removed, "in ledger but gone from index.html — run --sync")

    issues = len(never) + len(drifted) + len(stale) + len(removed)
    print("\n%s" % ("All auto rates fresh and in sync." if not issues
                     else "%d atom(s) need attention." % issues))
    return 0 if not issues else 1


def cmd_due(args, today):
    led = load_ledger()
    if led is None:
        print("No ledger yet. Run --init first.")
        return 2
    horizon = args.due if isinstance(args.due, int) else 7
    sla = led["_meta"].get("sla_days", SLA_DAYS)
    rows = []
    for aid, rec in led["items"].items():
        due_in = sla - _age_days(rec["last_verified"], today)
        if due_in <= horizon:
            rows.append((due_in, aid))
    rows.sort()
    print("Atoms due within %d days (SLA %d):" % (horizon, sla))
    for due_in, aid in rows:
        tag = "OVERDUE %dd" % -due_in if due_in < 0 else "in %dd" % due_in
        print("  [%s] %s" % (tag, aid))
    if not rows:
        print("  none — next checkpoint is further out.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Auto-rate verification auditor")
    p.add_argument("--init", action="store_true", help="create ledger, baseline all atoms today")
    p.add_argument("--force", action="store_true", help="with --init, overwrite existing ledger")
    p.add_argument("--sync", action="store_true", help="add new atoms / drop removed; keep dates")
    p.add_argument("--mark", nargs="+", metavar="ID", help="mark atom id(s) verified today")
    p.add_argument("--mark-all", action="store_true", help="mark all atoms verified today")
    p.add_argument("--due", nargs="?", const=7, type=int, metavar="DAYS", help="list atoms due within DAYS")
    p.add_argument("--source", help="source URL to record")
    p.add_argument("--note", help="note to record")
    p.add_argument("--date", help="override 'today' (YYYY-MM-DD)")
    args = p.parse_args()

    today = args.date or date.today().isoformat()

    if args.init:
        return cmd_init(args, today)
    if args.sync:
        return cmd_sync(args, today)
    if args.mark or args.mark_all:
        return cmd_mark(args, today)
    if args.due is not None:
        return cmd_due(args, today)
    return cmd_check(args, today)


if __name__ == "__main__":
    sys.exit(main())
