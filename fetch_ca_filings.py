#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch California rate filings from the CDI Approval/Closed bulk file — no clicking.

WHY: we hold 15 CA rows, hand-read from "the CDI list". The list is actually published as a
stable YTD .xlsx — 3,994 rows covering every P&C line — refreshed about 15 days after each
month end. We were transcribing a spreadsheet by hand.

★ CA IS RICHER THAN OUR SERFF STATES IN ONE IMPORTANT WAY. The file carries BOTH
`% RATE CHNG REQ` and `% RATE CHNG APPVD` — requested versus approved, for every filing, for
free. In SERFF states that comparison is the indicated-vs-taken story we can only get by opening
each jacket and reading the Company Rate Information block. Here it is a column.

Terms checked: insurance.ca.gov/robots.txt disallows /0100-consumers/, the statistical-plan
archives, loader.cfm and login.cfm. The rate-filing path used here is not restricted.

Parsed with zipfile + regex over sheet1.xml rather than openpyxl, which is not installed here —
an .xlsx is a zip of XML, so this needs no third-party dependency.

  python3 fetch_ca_filings.py                 # material personal auto/home filings not in the ledger
  python3 fetch_ca_filings.py --all-lines     # do not restrict to personal auto/home
  python3 fetch_ca_filings.py --write         # -> ca_filings_new.json for review
"""
import argparse, json, re, sys, zipfile, io, datetime, collections, urllib.request

INDEX = ("https://www.insurance.ca.gov/0250-insurers/0800-rate-filings/"
         "0100-rate-filing-lists/rate-filing-approvals/index.cfm")
BASE = "https://www.insurance.ca.gov"
PORTAL = INDEX

# CDI LINE CODE -> our line. Personal lines only unless --all-lines.
LINE_CODE = {
    "HOMEOWNERS MULTI-PERIL": ("home", "HO"),
    "AUTO LIAB/PHYS DAMAGE": ("auto", "PPA"),
}

FAMILY = [
    ("state farm", "State Farm"), ("geico", "GEICO"), ("government employees", "GEICO"),
    ("progressive", "Progressive"), ("allstate", "Allstate"), ("usaa", "USAA"),
    ("garrison", "USAA"), ("farmers", "Farmers"), ("fire insurance exchange", "Farmers"),
    ("mid century", "Farmers"), ("mid-century", "Farmers"), ("foremost", "Farmers"),
    ("bristol west", "Farmers"), ("liberty", "Liberty Mutual"), ("safeco", "Safeco"),
    ("nationwide", "Nationwide"), ("travelers", "Travelers"), ("american family", "American Family"),
    ("homesite", "Homesite"), ("amica", "Amica"), ("auto owners", "Auto-Owners"),
    ("auto-owners", "Auto-Owners"), ("erie", "Erie"), ("hartford", "The Hartford"),
    ("chubb", "Chubb"), ("ace american", "Chubb"), ("mercury", "Mercury"),
    ("wawanesa", "Wawanesa"), ("kemper", "Kemper"), ("csaa", "CSAA / AAA"),
    ("interinsurance exchange", "CSAA / AAA"), ("auto club", "CSAA / AAA"),
    ("horace mann", "Horace Mann"), ("national general", "National General"),
    ("root", "Root Insurance"), ("esurance", "Esurance"), ("pacific specialty", "Pacific Specialty"),
]


def family(name):
    """Word-boundary match. A bare substring test previously filed HORACE MANN under Chubb
    (the pattern "ace " sits inside "hor-ACE -mann"); unmapped is reported, never guessed."""
    n = " " + re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip() + " "
    for sub, fam in FAMILY:
        if re.search(r"(?<![a-z])" + re.escape(sub.strip()) + r"(?![a-z])", n):
            return fam
    return None


def latest_workbook():
    """Newest Approval-Closed-List YTD .xlsx linked from the CDI index page."""
    html = urllib.request.urlopen(INDEX, timeout=60).read().decode("utf-8", "replace")
    hrefs = re.findall(r'href="([^"]*Approval-Closed-List-YTD-[^"]*\.xlsx)"', html, re.I)
    if not hrefs:
        sys.exit("no Approval-Closed-List YTD workbook linked on the CDI index page")

    def key(h):
        m = re.search(r"YTD-(\d+)-(\d+)-(\d+)\.xlsx", h)
        if not m:
            return (0, 0, 0)
        mo, dy, yr = (int(x) for x in m.groups())
        return (yr, mo, dy)

    href = max(hrefs, key=key)
    url = href if href.startswith("http") else BASE + href
    return url, urllib.request.urlopen(url, timeout=120).read()


def sheet_rows(blob):
    """(header, rows) from an .xlsx without openpyxl — it is a zip of XML."""
    z = zipfile.ZipFile(io.BytesIO(blob))
    shared = re.findall(r"<t[^>]*>([^<]*)</t>", z.read("xl/sharedStrings.xml").decode("utf-8", "replace"))
    xml = z.read("xl/worksheets/sheet1.xml").decode("utf-8", "replace")
    out = []
    for raw in re.findall(r"<row[^>]*>(.*?)</row>", xml, re.S):
        cells = {}
        for col, attrs, val in re.findall(r'<c r="([A-Z]+)\d+"([^>]*)(?:/>|>(?:<v>([^<]*)</v>)?)', raw):
            if val is None or val == "":
                continue
            cells[col] = shared[int(val)] if 't="s"' in attrs else val
        out.append(cells)
    if not out:
        sys.exit("workbook parsed to zero rows — CDI may have changed the sheet layout")
    header = {v.strip().upper(): k for k, v in out[0].items()}
    return header, out[1:]


def num(v):
    if v is None:
        return None
    try:
        return round(float(str(v).replace("%", "").strip()), 3)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-pct", type=float, default=3.0)
    ap.add_argument("--all-lines", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    try:
        url, blob = latest_workbook()
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"CDI workbook unreachable: {e}")
    header, rows = sheet_rows(blob)
    print(f"workbook: {url.rsplit('/', 1)[-1]}  ({len(rows)} rows)")

    need = ["NAME", "LINE CODE", "% RATE CHNG APPVD", "% RATE CHNG REQ", "STATUS",
            "CLOSED DATE", "SERFF FILING #", "PROGRAM", "FILING TYPE"]
    missing = [c for c in need if c not in header]
    if missing:
        sys.exit(f"CDI changed the columns — missing {missing}. Header seen: {sorted(header)}")
    g = lambda r, c: r.get(header[c])

    have = set()
    for f in ("serff_filings.json", "serff_home_filings.json"):
        try:
            have |= {x["tracking"] for x in json.load(open(f))["filings"]}
        except Exception:
            pass

    # Same shape as the TX feed: one row PER COMPANY, so a multi-company filing repeats its
    # SERFF id (LWCM-134853327 appears 4x). Collapse per tracking to the dominant entity or the
    # ledger double-counts one filing as several. No premium/policy counts here either, so the
    # dominant row is the largest-magnitude approved change, not a premium weighting.
    by_trk = collections.defaultdict(list)
    for r in rows:
        t = (g(r, "SERFF FILING #") or "").strip()
        if t:
            by_trk[t].append(r)

    kept, unmapped, skip = [], collections.Counter(), collections.Counter()
    for r in rows:
        code = (g(r, "LINE CODE") or "").strip().upper()
        if not args.all_lines and code not in LINE_CODE:
            skip["other line"] += 1
            continue
        appvd = num(g(r, "% RATE CHNG APPVD"))
        if appvd is None:
            skip["no approved %"] += 1
            continue
        if abs(appvd) < args.min_pct:
            skip["below threshold"] += 1
            continue
        trk = (g(r, "SERFF FILING #") or "").strip()
        if not trk:
            skip["no SERFF id"] += 1
            continue
        if trk in have:
            skip["already in ledger"] += 1
            continue
        sibs = by_trk.get(trk, [r])
        dom = max(sibs, key=lambda x: abs(num(g(x, "% RATE CHNG APPVD")) or 0))
        if dom is not r:
            skip["sibling of a multi-entity filing"] += 1
            continue
        name = (g(r, "NAME") or "").strip()
        fam = family(name)
        if not fam:
            unmapped[name] += 1
            continue
        line, product = LINE_CODE.get(code, ("auto", "PPA"))
        closed = (g(r, "CLOSED DATE") or "").strip() or None
        kept.append({
            "state": "CA", "line": line, "carrier": fam,
            "entity": name.title() + (f" (dominant of {len(sibs)} entities)" if len(sibs) > 1 else ""),
            "tracking": trk, "url": PORTAL, "product": product,
            "filing_type": (g(r, "FILING TYPE") or "").strip() or None,
            "disposition_date": closed, "effective_new": None, "effective_renewal": None,
            "overall_pct": appvd,
            # the column SERFF states make us read a jacket for
            "indicated_pct": num(g(r, "% RATE CHNG REQ")),
            "prior_revision_pct": None, "written_premium": None,
            "written_premium_change": None, "affected": None, "count_basis": None,
            "coverage_changes": None, "premium_as_of": None,
            "recorded_date": datetime.date.today().isoformat(),
            "status": (g(r, "STATUS") or "").strip() or None,
            "source_note": "CA CDI Approval/Closed List (YTD xlsx); no PH/premium.",
            "note": None,
        })

    kept.sort(key=lambda r: -abs(r["overall_pct"]))
    for k, v in skip.most_common():
        print(f"  skipped, {k:<20} {v}")
    print(f"\nNEW material filings not in our ledger: {len(kept)}")
    print(f"{'':2}{'appvd':>8} {'req':>8}  {'line':<5} {'carrier':<18} tracking")
    for r in kept[:40]:
        req = f"{r['indicated_pct']:+.1f}%" if r["indicated_pct"] is not None else "—"
        print(f"  {r['overall_pct']:+7.1f}% {req:>8}  {r['line']:<5} {r['carrier']:<18} {r['tracking']}")
    if len(kept) > 40:
        print(f"  ... and {len(kept) - 40} more")

    trimmed = [r for r in kept if r["indicated_pct"] is not None
               and r["indicated_pct"] > r["overall_pct"] + 0.05]
    if trimmed:
        print(f"\n{len(trimmed)} were approved BELOW what the carrier requested — "
              f"the indicated-vs-taken angle, free in this feed:")
        for r in trimmed[:8]:
            print(f"  {r['carrier']:<18} requested {r['indicated_pct']:+.1f}%, "
                  f"approved {r['overall_pct']:+.1f}%  ({r['tracking']})")

    if unmapped:
        print(f"\nUNMAPPED companies ({sum(unmapped.values())} filings):")
        for n, c in unmapped.most_common(10):
            print(f"  {c:>3}  {n}")

    if args.write:
        out = "ca_filings_new.json"
        json.dump({"_meta": {
            "purpose": "Candidate CA rows from the CDI Approval/Closed YTD workbook. REVIEW "
                       "before merging — family mapping and editorial notes need a human pass.",
            "source": url, "fetched": datetime.date.today().isoformat(),
            "min_pct": args.min_pct, "count": len(kept),
        }, "filings": kept}, open(out, "w"), indent=1)
        print(f"\nwrote {out} — review, then merge deliberately.")
    else:
        print("\n(report only; --write to emit ca_filings_new.json)")


if __name__ == "__main__":
    main()
